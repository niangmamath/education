# ADR-006 : Données fictives et protection de l’enfant

| Attribut | Valeur |
|---|---|
| **Statut** | Accepted |
| **Date** | 2026-08-07 |
| **Décideurs** | Équipe stage StudentConnect |
| **Issue GitHub** | — |

## Contexte

StudentConnect cible des élèves du primaire et leurs parents. Le stage produit un prototype avec des données de démonstration. Les règles produit interdisent tout diagnostic médical ou psychologique, toute formulation stigmatisante, et toute donnée réelle d’enfant dans le dépôt, les tests ou les captures.

## Décision

1. **Exclusivement des données fictives** pendant tout le stage : profils élèves, évaluations, observations, captures d’écran.
2. **Aucun secret** (`.env`, tokens, mots de passe) commité ; `.env.example` sans valeurs sensibles.
3. Les lacunes automatiques restent des **candidates explicables**, jamais des vérités définitives.
4. Les causes probables sont des **hypothèses pédagogiques**, jamais des diagnostics cliniques.
5. Formulations factuelles, positives et non stigmatisantes dans toute l’UI.

## Options étudiées

| Option | Avantages | Inconvénients |
|---|---|---|
| **Données fictives strictes** (retenue) | Conformité éthique, pas de RGPD réel en démo | Moins réaliste |
| Données réelles anonymisées | Réalisme | Interdit par règles projet, risque enfant |
| Données synthétiques générées | Volume test | À combiner avec fictifs nommés (3 profils pilotes) |

## Conséquences

- Fixtures et jeux de démo : 3 profils d’élèves fictifs (`steps/PROMPT_GENERAL.md` §6).
- Revue PR systématique : pas de nom réel, photo réelle, ni identifiant scolaire.
- Politique de conservation/suppression en production : **Proposed** pour phase post-stage (décision ouverte dans `etat.md`).

## Risques

| Risque | Niveau | Atténuation |
|---|---|---|
| Commit accidentel de `.env` | P0 | `.gitignore` dès étape 02 |
| Formulation UI stigmatisante | P1 | Revue UX étape 05, tests acceptation |
| Extension scope consentements enfants | P2 | M01 minimal en V0.1 |

## Références

- `steps/PROMPT_GENERAL.md` §3, §6
- `steps/etat.md` — Décisions validées
- `docs/architecture/audit-initial.md` §6
