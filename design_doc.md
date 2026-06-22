# Design doc — Pipeline de traitement IRM (cartographies → rapport médical)

| | |
|---|---|
| **Statut** | Draft (v1) |
| **Auteur** | Inès Benziane |
| **Relecteur** | Pierre-Yves Baudin |
| **Créé le** | 2026-06-16 |
| **Dernière maj** | 2026-06-22 |

---

## 1. Context & background

L'outil dispose aujourd'hui de quatre briques logicielles disjointes, sans
chaînage commun :

- `dicom_client` — recherche, récupération et anonymisation de fichiers DICOM.
- `mutools` — algorithmes (et leur plomberie) produisant les **cartographies**
  (un type par biomarqueur : T2, fraction graisseuse, etc.) à partir des DICOM.
- Segmentation automatique — exécutée sur une station de calcul distante ; code
  externe, maintenu par Louis.
- `section_generator` — construit des tables de résultats (les fichiers JSON, via
  `get_result`) à partir de la segmentation, puis génère un rapport médical.

Chaque brique fonctionne isolément, avec une plomberie manuelle, peu de contrôle
qualité intégré et une traçabilité limitée. L'objectif de ce document est de
définir l'architecture d'un système unifié, fiable, reproductible et débogable,
qui chaîne ces briques tout en permettant de n'en exécuter qu'une partie.

**Politique de dépendances :** tout est écrit en interne (pas de framework de
workflow externe = pas de mises à jour subies).

## 2. Goals

- Chaîner les quatre briques en un pipeline cohérent, exécutable de bout en bout.
- Permettre l'**exécution partielle** : une seule brique, ou une entrée à n'importe
  quelle étape avec des données déjà traitées.
- Garantir la **reproductibilité** : tout résultat est rattachable à une méthode,
  une version et des paramètres connus.
- Rendre les runs **débogables** : logs structurés et données intermédiaires
  inspectables à chaque étape.
- Intégrer un **contrôle qualité** adapté au mode d'usage (lot vs quelques patients).
- Permettre de **réintégrer les informations du patient de manière cadrée** lors de
  la génération du compte-rendu.
- Offrir une interface en ligne de commande claire et prédéfinie.

## 3. Non-goals

- **Flexibilité maximale de paramétrage** : on privilégie un jeu de méthodes
  prédéfinies à paramètres figés plutôt qu'un paramétrage libre.

## 4. User stories

L'utilisateur **choisit au lancement** le mode d'usage et la cible voulue ; le
runner en déduit le reste. Trois modes d'usage, qui déterminent notamment le
traitement des identifiants :

| Cas d'usage | Traitement des données |
|---|---|
| **RESEARCH** | Anonymisation. L'ID n'importe pas, seule la distinction compte. Un pseudonyme à usage unique suffit. |
| **CLINICS** | Pseudonymisation. ID unique par patient + table de correspondance pseudo↔patient. Sert à générer le rapport médical. Centré patient. |
| **STUDY** | Pseudonymisation. ID spécifique défini par l'étude. Centré cohorte. |

**Deux rôles** (voir §9 pour les droits associés) :

- **utilisateur** : ingénieurs, chercheurs, étudiants...
- **médical** : manipulateurs radio, médecins.

Le rôle conditionne l'accès aux informations identifiantes du patient, pas la
capacité à lancer le pipeline ni à générer un rapport.

**Must (v1)**

- En tant qu'ingénieur ou chercheur, je peux exécuter `dicom_client` seul pour
  récupérer et anonymiser des DICOM, afin d'y appliquer ensuite mes propres calculs.
- En tant qu'utilisateur (tout rôle), je peux générer un rapport médical à partir de
  données déjà traitées, sans rejouer les étapes amont. Le rapport contient les
  informations identifiantes du patient uniquement pour le rôle médical ; les autres
  rôles n'obtiennent que le pseudonyme du patient.
- En tant que chercheur, je peux choisir une méthode de calcul dans une liste
  prédéfinie (paramètres figés) et produire les cartographies.
- En tant qu'ingénieure, je peux déboguer un run échoué en inspectant les données
  intermédiaires et les logs de chaque étape.
- En tant qu'utilisateur, je peux exécuter le pipeline complet sur une étude.
- En tant qu'utilisateur, je peux exécuter le pipeline à partir de DICOM déjà
  anonymisés que je possède.
- En tant qu'utilisateur, je peux exécuter le pipeline à partir de résultats de
  `mutools` déjà en ma possession.
- En tant qu'utilisateur, je peux exécuter le pipeline complet à partir de la
  segmentation automatique.
- En tant que chercheur, je peux changer la méthode de segmentation pour comparer
  deux résultats.
- En tant qu'utilisateur, je bénéficie d'un QC automatique en mode lot et d'un QC
  humain pour un petit nombre de patients.
- En tant qu'utilisateur, je peux lancer le traitement sur un lot d'études.

**Could**

- En tant qu'utilisateur, je dispose d'une interface graphique au-dessus de la CLI.

**Won't**

- Aucune fonctionnalité explicitement exclue à ce stade.

## 5. Design principles & politique de dépendances

- **Stages composables** : chaque brique est une unité indépendante, exécutable
  seule, avec un contrat d'entrée/sortie explicite.
- **Exécution par cible** : l'utilisateur demande un output (une *cible*) ; le
  runner ne (re)lance que les étapes nécessaires pour le produire, en sautant ce
  qui est déjà fait et à jour.
- **Hexagonal par stage** : logique métier au cœur, isolée de l'I/O par des ports
  et adapters.
- **Fail fast** : chaque stage valide son entrée contre un schéma et refuse
  bruyamment toute donnée invalide.
- **Reproductibilité d'abord** : méthodes à paramètres figés, provenance tracée.
- **Différer les décisions d'infra** : les coutures permettent d'ajouter un serveur
  plus tard sans toucher au cœur.

## 6. Proposed design — vue d'ensemble

Pipeline modulaire orchestré (DAG), **orienté batch**, file-based, coordonné par un
runner interne. Le choix du batch (traiter une unité — étude ou lot — du début à la
fin, par opposition au traitement continu en temps réel) se justifie ici : le
travail arrive en unités discrètes, sans contrainte de temps réel, avec des calculs
lourds, et on veut pouvoir rejouer une étude entière de façon déterministe.

L'outil est installé localement par chaque utilisateur et utilisé de façon
**concurrente** ; les runners ne se bloquent pas entre eux, la coordination se fait
uniquement aux ressources partagées (voir §11).

L'utilisateur choisit au lancement le mode et la cible. Le runner **coordonne les
dépendances** (il lit le graphe des étapes et les exécute dans un ordre qui respecte
les dépendances, sans jamais lancer une étape dont les entrées manquent) et permet
l'**exécution partielle**. Les artefacts intermédiaires (DICOM anonymisés,
cartographies, masques, tables) sont **matérialisés sur disque** : chaque sortie est
écrite dans un fichier concret, ce qui la rend inspectable pour le debug,
réutilisable par l'étape suivante, et vérifiable par le runner pour décider de
sauter ou non un calcul.

Un **manifest** par étude (un petit fichier JSON) porte l'état (quelles étapes sont
faites, où sont leurs sorties) et la provenance (quelle méthode + version +
paramètres ont produit chaque artefact). À affiner

Flux nominal :

```
PACS → dicom_client (retrieve + anonymise) → mutools (cartographies)
     → segmentation (job async, station distante) → section_generator (tables → rapport)
```

## 7. Detailed design

### 7.1 Runner interne (coordination)

Le runner est le module qui **décide quelles étapes lancer, dans quel ordre, et les
lance** — sans faire lui-même aucun calcul scientifique. C'est le chef d'orchestre
du pipeline ; le modèle mental est celui d'un petit `make` spécialisé. Il est gardé
derrière une couture (driving adapter) pour rester remplaçable, et se situe dans le
repo entre la CLI et les stages (la logique métier). Il fournit :

- **DAG déclaré.** Le DAG (*Directed Acyclic Graph*, graphe orienté acyclique) est
  le graphe des étapes : les nœuds sont les étapes et leurs sorties, les arêtes
  orientées sont les dépendances (`A → B` = B dépend de A). Acyclique = aucune
  dépendance ne boucle. Chaque stage déclare ses inputs, ses outputs et ses
  dépendances amont.
- **Résolution par cible.** Pour un output demandé, le runner calcule le
  sous-ensemble minimal d'étapes à exécuter (tri topologique sur le sous-DAG) et
  saute ce qui est déjà produit et à jour.
- **Détection de péremption (staleness).** Une étape doit être rejouée si son
  résultat ne reflète plus ce qui le produit. Deux niveaux possibles, à choisir :
  - *Niveau minimal — encodage dans le nom de fichier.* La méthode et les paramètres
    sont encodés dans le chemin de sortie, p. ex.
    `results/{study}/carte_T2__dixon3pt__echoes-10-20-30.nii`. Comme l'utilisateur
    choisit méthode et paramètres au lancement, deux calculs différents portent des
    noms différents : « le fichier existe-t-il ? » redevient une vérification
    correcte, et deux méthodes coexistent pour comparaison. Couvre les changements
    de méthode/paramètres ; ne couvre pas les changements de code ni de contenu de
    l'entrée.
  - *Niveau complet — fingerprint.* Un hash de (contenu des entrées + version du
    code + paramètres), stocké dans le manifest ; l'étape est rejouée si le hash
    diffère. Couvre en plus les changements de code (ex. correction d'un bug d'algo)
    et de contenu d'entrée. À adopter si l'on itère beaucoup sur les algorithmes.
- **Complétude atomique.** Écriture dans un emplacement temporaire puis *rename*
  atomique en cas de succès ; suppression des outputs incomplets en cas d'échec.
  Aucun output partiel n'est jamais visible comme complet.
- **Idempotence.** ejouer une étape déjà à jour.
- **Verrouillage par étude (locking).** Empêche que deux runners (utilisateurs
  différents) traitent la même étude en même temps : le second attend ou saute. Voir
  §11 pour la coordination concurrente.
- **Logs structurés.** `run_id` propagé sur tout le run, `stage` et `study_id`
  pseudonymisé à chaque ligne.
- **Gestion d'échec.** Arrêt sur erreur, retries avec backoff pour l'étape async de
  segmentation, surfaçage clair des erreurs.
- **Dry-run.** Afficher le plan d'exécution sans l'exécuter.

Évolutions ultérieures possibles : exécution parallèle des stages indépendants,
soumission à un ordonnanceur de cluster (SLURM) pour la station de calcul.

#### Coûts et risques de l'approche interne (à assumer)

- Risque de correction sur le *long tail* (complétude atomique, détection de
  péremption, idempotence) — critique en contexte médical, car un bug y produit un
  résultat silencieusement faux. Atténuation : tests dédiés sur ces trois mécanismes.
- Bus factor au niveau du projet : le runner doit rester petit, testé et documenté
  pour survivre au départ de son auteur.

### 7.2 Anatomie d'un stage (hexagonal)

Chaque stage suit le même squelette :

1. Valider l'entrée contre un schéma (fail fast).
2. Exécuter la logique métier (cœur sans I/O).
3. Passer la QC gate (§7.5).
4. Valider et écrire la sortie ; mettre à jour le manifest.

Le cœur dépend de ports (interfaces) ; les adapters (PACS, station de seg,
stockage, QC) les implémentent. Les ports « driving » (CLI, runner, test) pilotent
le même cœur, ce qui rend chaque stage exécutable seul et testable avec des *fakes*.

### 7.3 Brique de calcul (migration `mutools`)

Stratégie : Strangler Fig. On reprend les algorithmes de `mutools` et on réécrit la
plomberie. La brique est décomposée en sous-étapes inspectables.

**Registre de méthodes.** Catalogue `nom → (algorithme, paramètres figés, version)`.
L'utilisateur choisit une méthode par son nom ; pas de paramètres libres. Une
variation d'algorithme = une nouvelle méthode nommée. Chaque méthode est validée
une fois (suite de validation sur données de référence) puis épinglée ; la méthode
utilisée est inscrite dans le manifest et le rapport.

### 7.4 Intégration de la segmentation (frontière asynchrone)

La station de segmentation est distante et n'est pas notre code : elle est traitée
comme un service externe via un adapter dédié.

- Pattern : submit → poll → fetch.
- Anti-race-condition : la station signale la complétude par écriture atomique
  (rename) ou fichier sentinelle ; on ne lit jamais un résultat en cours d'écriture.
- Robustesse : retries avec backoff, timeout, jobs idempotents.
- Contrat à formaliser : format/emplacement d'entrée, format/emplacement de sortie,
  signal de fin, comportement en cas d'échec.

Comparaison de méthodes de segmentation : swap d'adapter derrière le port
Segmentation.

### 7.5 Contrôle qualité (QC gate)

QC enfichable, politique sélectionnée par le mode d'exécution, injectée une seule
fois à la configuration du run (pas de conditions `if` disséminées dans les stages) :

- Mode lot → QC automatique (validateurs programmatiques).
- Petit nombre de patients → QC humain : le run se met en pause et attend une
  approbation avant de poursuivre (modélisé via un artefact d'approbation que le
  runner attend).

La définition de « QC raté » par étape : à préciser (Q4).

### 7.6 Génération du rapport

`section_generator` lit les résultats de segmentation, construit les tables, puis
génère le rapport de façon déterministe. Ses dépendances externes (source des
résultats, sink du rapport) sont derrière des ports, ce qui permet de l'exécuter
seul sur des données déjà traitées. Les informations identifiantes du patient ne
sont insérées que pour le rôle médical (voir §9) ; sinon le rapport ne porte que le
pseudonyme.

### 7.7 Contrats de données et provenance

- Schéma d'entrée et de sortie explicite à chaque couture, validé à l'entrée du
  stage.
- Manifest par étude : état d'avancement, chemins des artefacts, méthode + version
  + paramètres, identifiant d'étude pseudonymisé, et l'empreinte par étape selon le
  niveau de détection de péremption retenu (§7.1 : encodage dans le nom ou
  fingerprint). On vise la version minimale (provenance + ce qui est nécessaire à
  l'exécution partielle) ; à affiner avec les relecteurs.

### 7.8 Observabilité et debug

- Logs structurés (format clé-valeur, filtrables) à chaque étape, portant le
  `run_id` (identifiant unique du run, pour corréler toutes les lignes d'un même
  run), le `stage`, et le `study_id` pseudonymisé (l'identifiant d'étude sous forme
  de pseudonyme, jamais l'identité réelle du patient).
- Intermédiaires matérialisés + mode debug qui dump les données intermédiaires.
- Le `run_id` est propagé sur tout le run pour corréler les logs.

## 8. Alternatives considered

**Framework de workflow externe (Snakemake / Dagster).** Considéré : il fournit
nativement la résolution de DAG, l'exécution incrémentale, le nettoyage des outputs
incomplets, la parallélisation et la soumission cluster — c'est-à-dire le runner que
nous écrivons en interne. Écarté : politique du labo (tout maison), volonté de
contrôle total, absence de DSL externe à transmettre au successeur, et suppression
du coût de migration entre versions majeures. Coût accepté en contrepartie : effort
d'ingénierie du runner et bus factor interne. La couture autour du runner préserve
la réversibilité de ce choix.

**Microservices / event-driven (services + message broker).** Complexité de système
distribué injustifiée au vu du débit et de la taille de l'équipe.

**Serveur central de calcul (client-serveur synchrone, thread par requête).** Un
serveur qui exécute le calcul sur le request path se bloque, et le calcul est
CPU-bound (le GIL Python empêche les threads de paralléliser le CPU). Approche
retenue à la place : des runners locaux concurrents + coordination aux ressources
partagées (§11), sans serveur de calcul central. Un serveur ne s'imposerait que pour
un besoin futur d'accès distant ; il prendrait alors la forme d'une job-queue
asynchrone (API fine qui enqueue, pool de workers basés sur des processus, polling,
monitoring), jamais du calcul sur le request path.

## 9. Security & privacy

- **Rôles (RBAC).** Deux rôles : `utilisateur` (ingé/chercheur/étudiant) et
  `médical` (manip/médecin). Les deux peuvent lancer le pipeline et générer un
  rapport.
- **Ré-identification.** Seul le rôle `médical` accède aux informations
  identifiantes du patient et à la table de correspondance pseudonyme ↔ patient ;
  les autres rôles ne voient que le pseudonyme dans le rapport. La ré-identification
  n'est possible que pour des données pseudonymisées (CLINICS / STUDY) ;
  l'anonymisation RESEARCH est irréversible.
- **Authentification + audit trail.** Les utilisateurs sont identifiés ; les actions
  (qui, quel rôle, quelle étude pseudonymisée, quand) sont tracées dans un audit
  trail. Requis pour le RGPD (croisement identité ↔ données patient).
- **Store partagé concurrency-safe** (petite base, pas des fichiers plats édités par
  ~20 personnes) pour l'identité/les rôles, la table de pseudonymes et l'audit.
- Anonymisation / pseudonymisation dès `dicom_client`, en gate d'entrée, avant que
  toute donnée descende dans le pipeline.
- Prise en compte des private tags DICOM et des annotations burned-in dans les
  pixels.

## 10. Testing strategy

Par stage :

- Tests unitaires (logique isolée).
- Tests de contrat aux coutures (la sortie respecte le schéma attendu en aval).
- Tests golden / régression (sortie comparée à une référence), base de la validation
  de méthode.
- Dépendances externes (station de seg, PACS) remplacées par des *fakes* en mémoire,
  pas des mocks ; tests hermétiques (sans GPU ni réseau).

Tests spécifiques au runner interne (critiques) :

- Complétude atomique : simuler un crash en cours d'écriture et vérifier qu'aucun
  output partiel n'est jamais considéré comme valide.
- Détection de péremption : vérifier qu'un changement d'input, de version de code ou
  de paramètre déclenche bien la ré-exécution, et qu'une empreinte identique ne la
  déclenche pas.
- Idempotence : rejouer un run complet ne refait rien et ne corrompt rien.
- Verrouillage : deux runners sur la même étude ne la corrompent pas (l'un attend ou
  saute).

## 11. Deployment & operations

- **Clients locaux concurrents.** Chaque utilisateur exécute son propre runner
  local (CLI) sur sa machine. Les runners ne se bloquent pas entre eux ; pas de
  serveur central de calcul. La concurrence ne se joue qu'aux ressources partagées.
- **Coordination aux ressources partagées :**
  - *PACS* : à voir leur capacité
  - *Station de segmentation* : Q2
  - *Stockage partagé* : isolation par utilisateur/étude, verrou par étude (locking),
    écriture atomique — pour que deux runners ne corrompent pas la même étude.
  - *Store partagé* : identité/rôles + table de pseudonymes + audit, concurrency-safe.
- Les coutures (driving adapters) permettent d'ajouter plus tard une API/serveur (ex.
  accès distant) sans toucher au cœur.

## 12. Rollout / milestones

1. **M1 — Socle + runner.** Contrats de données + manifest + squelette de stage
   hexagonal + logging structuré + runner interne (DAG, résolution par cible,
   staleness [encodage dans le nom ou fingerprint, §7.1], complétude atomique,
   idempotence, verrouillage par étude, dry-run) avec ses tests critiques.
2. **M2 — `dicom_client`.** Récupération + anonymisation en gate, exécutable seul +
   table de pseudonymes (store partagé).
3. **M3 — Brique de calcul.** Registre de méthodes (1 ou 2 méthodes), sous-étapes
   inspectables, golden tests.
4. **M4 — Segmentation.** Adapter async + contrat avec la station, fake pour tests.
5. **M5 — `section_generator`.** Génération de rapport, exécutable seul.
6. **M6 — QC + RBAC + pipeline complet.** QC gate (auto + humain), RBAC (2 rôles) +
   ré-identification réservée au rôle médical + audit trail, exécution de bout en
   bout, exécution partielle validée sur les trois cas d'usage.

## 13. Open questions

- **Q1 — Forme du store partagé** (identité/rôles + table de pseudonymes + audit) :
  technologie et schéma. (La concurrence multi-utilisateur et les deux rôles sont
  actés ; reste la mise en œuvre du store.)
- **Q2 — Contrat avec la station de segmentation** : mécanisme de soumission et de
  récupération (drop-folder, SLURM, API) **et** mécanisme de priorité (clinique >
  batch), à négocier avec Louis.
- **Q3 — Langage de `mutools`** (MATLAB / Python) : impacte les frontières de
  processus.
- **Q4 — Définition de « QC raté » par étape** : dimensionne les validateurs
  automatiques et le human-in-the-loop.
- **Q5 — Anonymisation irréversible vs pseudonymisation** : suivi longitudinal des
  patients nécessaire ou non ?
- Q6 — Base de résultats : moteur (SQLite / PostgreSQL…), schéma, partagée ou
  séparée du store partagé, patterns de requête. (Post-v1.)