# ADR-004 : Stratégie H5P

| Attribut | Valeur |
|---|---|
| **Statut** | Accepted (piste principale) / **Proposed** (mode d’hébergement) |
| **Date** | 2026-08-07 |
| **Décideurs** | Équipe stage StudentConnect |
| **Issue GitHub** | — (à créer : décision hébergement H5P) |

## Contexte

H5P permet des activités interactives, diagnostics et réévaluations sous contrôle éditorial. StudentConnect en fait la **piste principale** pour les évaluations contrôlées en V0.1. La collecte xAPI et le suivi fine-grained dépendent du mode d’hébergement, qui **n’est pas encore tranché** (`steps/etat.md` — décision ouverte).

## Décision

1. **Retenu :** H5P est le moteur privilégié pour activités, diagnostics et réévaluations pilotes (POC obligatoire en V0.1).
2. **En attente de validation :** le mode d’hébergement exact parmi :
   - instance H5P native / standalone ;
   - Moodle pilote comme back-office H5P ;
   - autre moteur compatible (LTI, xAPI).

3. En V0.1, le suivi minimal accepté est `launch-only` ou `manual-verified` si xAPI n’est pas disponible à temps.

## Options étudiées

| Option | Avantages | Inconvénients |
|---|---|---|
| H5P standalone / hébergement dédié | Contrôle total, xAPI possible | Ops supplémentaires, POC complexe |
| Moodle pilote (back-office) | Écosystème H5P mature | Moodle n’est pas l’UI familiale ; couplage |
| Intégration légère embed seule | Rapide | Suivi limité sans xAPI |
| Abandon H5P pour quiz Django internes | Simplicité | Perte différenciation évaluations riches |

## Conséquences

- Le spike H5P est planifié à l’étape `04_catalogue_et_integrations/04_spike_h5p.md`.
- Le catalogue de ressources enregistre mode d’accès et mode de suivi par ressource H5P.
- Aucune dépendance critique à une API H5P non documentée.

## Risques

| Risque | Niveau | Atténuation |
|---|---|---|
| POC H5P plus long que prévu | P1 | Plan B : quiz Django interne pour la démo |
| Hébergement non décidé bloque le spike | P1 | Timebox décision avant étape 04 |
| xAPI indisponible | P2 | Modes `launch-only` / `manual-verified` |

## Références

- `steps/PROMPT_GENERAL.md` §7
- `steps/etat.md` — Décisions ouvertes (hébergement H5P)
- `steps/04_catalogue_et_integrations/04_spike_h5p.md`
