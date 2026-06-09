# Medical-report-modules — Description du module

## Rôle dans le pipeline

Dernière brique du pipeline IRM musculaire.
**Input :** fichiers JSON produits par `mutools get-results`
**Output :** comptes-rendus médicaux en PDF (un ou plusieurs par patient)

Ce module ne sait pas d'où viennent les JSON. Il ne connaît pas mutools,
ni la segmentation, ni les DICOMs. Son seul contrat : recevoir des JSON
bien formés et produire des PDFs.

---

## Entrée : format JSON mutools

Chaque fichier JSON correspond à un examen (patient × date × segment × biomarqueur × méthode).
Nom de fichier : `{patient_id}_{date}_{segment}_{method}_{version1}_{version2}.json`

Contenu : métadonnées patient + liste de muscles, chaque muscle ayant :
- stats volumétriques (T2 ou FF moyen sur tout le volume)
- stats par coupe (slice) avec contour (outline) en coordonnées 2D

---

## Architecture interne

```
interface/
    orchestrator.py       → sélectionne et charge les examens selon un preset
    batch_presets.py      → génère tous les PDFs (preset × colormap × synth_version)

data_reader/              → parse les JSON mutools → objets Exam (Pydantic)
data_writer/              → transforme les Exam en structures pour les templates

section_generator/
    generate_pdf.py       → orchestrateur principal : données → HTML → PDF
    templates/            → Jinja2 (T2, FF, synthesis, shared_macros)
    styles/               → CSS WeasyPrint
    FF_diagram/           → génération des vues anatomiques SVG (B-spline)
    src/
        domain/services/  → synthesis_builder.py (calcul évolution)
        infrastructure/   → color_mappers.py (COLORMAP_REGISTRY)

comment_generator/        → sélection automatique du commentaire T2 (YAML config)

config/
    presets/              → 4 presets JSON (1slice, 1slice_v2, compact, complet)
    staff.json            → noms techniciens et médecins
```

---

## Points d'entrée publics

```python
# Génération d'un PDF
from section_generator import generate_pdf
generate_pdf.create_pdf(exams, output_name, output_dir, synthesis_version, colormap_name)

# Batch complet pour un patient
python -m interface.batch_presets <patient_id> <data_path> [--colormap default] [--quick]
```

---

## Ce qui est propre / réutilisable

- `COLORMAP_REGISTRY` : extensible, bien isolé
- `comment_generator` : logique YAML, découplée
- `synthesis_builder.py` : calcul d'évolution propre
- Les templates Jinja2 : modulaires (macros partagées)

## Ce qui est fragile / à refactoriser

- Pas de unit tests
- `generate_pdf.py` trop long (logique métier mélangée avec rendu)
- L'orchestrator fait trop de choses
- Pas de gestion d'erreur fine par exam
- Le format JSON d'entrée n'est pas formellement spécifié/contractualisé

---

## Interface attendue depuis le pipeline

Ce module attend des JSON dans un dossier (`data_path`).
Il ne sait pas comment ils ont été produits.
**Le seul couplage avec le reste du pipeline : le format JSON.**
C'est ce contrat qu'il faudra formaliser dans le design global.
