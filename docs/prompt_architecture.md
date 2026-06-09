# Prompt — Session d'architecture pipeline IRM musculaire

---

Je travaille seule sur la conception d'un pipeline IRM musculaire complet,
de la récupération des DICOMs jusqu'à la génération de comptes-rendus PDF pour des médecins.

Mon responsable m'a demandé de :
- Designer le pipeline de façon rigoureuse, du début à la fin
- Construire une bibliothèque Python propre avec des unit tests
- Intégrer les algorithmes de mutools (son outil) dans mon pipeline
- Identifier ce qui existe et peut être repris, ce qui est à construire

---

## LES BRIQUES EXISTANTES

### 1. part1_Dicom — MON CODE
Récupère les fichiers DICOM depuis un serveur PACS, les anonymise et les pseudonymise.
Structure actuelle : controllers/ (find, get, move, anonym) + services/ + CLI.
Fonctionne mais pas propre. Pas de tests.
Output attendu : fichiers DICOM locaux, organisés par patient/examen.

### 2. mutools — OUTIL INTERNE DU LABO (code source accessible)
Outil développé par mon responsable. CLI Python complet pour le traitement IRM musculaire.
Contient les algorithmes de T2-mapping, Dixon/FF, segmentation, et agrégation des résultats.

Mon responsable m'a explicitement demandé d'utiliser ces algorithmes dans mon pipeline.
Je vais donc extraire et intégrer directement dans mon code les parties pertinentes
— ce n'est pas un appel subprocess, c'est une intégration de code source adapté.

Je connais les commandes mutools à haut niveau (t2map-3exp, dixon3pt, get-results...),
mais identifier exactement quelles parties du code extraire, comment les adapter
et comment les interfacer fait partie du travail de design.

### 3. Segmentation automatique — STATUT INCERTAIN
Il existe un outil de segmentation automatique des muscles.
Je ne sais pas encore si je vais l'intégrer, l'appeler en subprocess,
ou m'appuyer sur les ROI existants. C'est une décision à prendre pendant le design.

### 4. Medical-report-modules — MON CODE
Dernière brique : lit des fichiers JSON et génère des comptes-rendus PDF médicaux.
Stack : Pydantic + Jinja2 + WeasyPrint + cmcrameri.
Pas de tests. Fonctionne en production sur plusieurs patients.
Son seul contrat avec le reste du pipeline : recevoir des JSON bien formés.
Description complète dans le fichier joint (module_description.md).

---

## CE QUI N'EXISTE PAS ENCORE

- L'orchestrateur central qui enchaîne toutes les étapes
- La formalisation des interfaces entre chaque brique
  (formats de fichiers, contrats d'entrée/sortie, conventions de nommage)
- L'intégration propre des algos mutools dans mon code
- La décision sur la segmentation automatique
- La gestion des erreurs et du logging à l'échelle du pipeline
- Les unit tests sur toutes les briques

---

## CONTRAINTES

- Je travaille seule
- CLI d'abord, éventuellement une interface graphique plus tard
- Python uniquement
- Design first : on ne code rien avant d'avoir validé les décisions d'architecture
- Le code doit être rigoureux : testé, documenté, maintenable

---

## CE QUE J'ATTENDS DE CETTE SESSION

Je veux construire l'architecture avec toi, décision par décision.

1. Aide-moi à clarifier les interfaces entre chaque brique :
   qu'est-ce qui entre, qu'est-ce qui sort, sous quel format exactement

2. Aide-moi à décider ce qu'il faut construire, ce qui peut être repris tel quel,
   et ce qui doit être refactorisé

3. Aide-moi à concevoir l'orchestrateur central

4. Aide-moi à décider comment intégrer les algos mutools :
   quoi extraire, comment l'isoler, comment le tester

5. Aide-moi à trancher la question de la segmentation automatique

6. Propose une stratégie de tests adaptée à ce type de pipeline
   (dépendances externes, fichiers intermédiaires, algos scientifiques)

---

Commence par me poser toutes les questions nécessaires
pour bien comprendre les contraintes avant de proposer quoi que ce soit.
Ne fais aucune hypothèse sans me demander.
