# bin/ — code retiré du produit

Code qui n'est plus utilisé par medical_report (aucun import, hors du rapport livré),
conservé ici plutôt que supprimé, au cas où il servirait de référence.
Rien dans `bin/` n'est installé avec le paquet (`src/` seulement) ni testé.

| Élément | Ce que c'était | Retiré le |
|---|---|---|
| `check_match.py` | Ancien utilitaire de l'interface, plus appelé | 22/10/2026 |
| `ff_diagram_bands/` | Prototype du schéma FF par « bandes » ; le rapport utilise la version B-splines (`FF_diagram/main_bsplines.py`) | 22/10/2026 |
| `evolution_prototype/` | Prototype du calcul d'évolution T2 (scripts lisant `data/data01.json`, palettes Crameri) ; remplacé par `synthesis_builder.py` | 22/10/2026 |

Pour réutiliser un fichier, le remettre dans `src/` et lui écrire des tests.
