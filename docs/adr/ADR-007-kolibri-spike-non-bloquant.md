# ADR-007 : Kolibri comme spike offline non bloquant

| Attribut | Valeur |
|---|---|
| **Statut** | Accepted |
| **Date** | 2026-08-07 |
| **Décideurs** | Équipe stage StudentConnect |
| **Issue GitHub** | — |

## Contexte

Kolibri offre un accès offline à des contenus éducatifs, pertinent pour des contextes à connectivité limitée. Le stage dispose d’un délai contraint et le flux vertical V0.1 est déjà ambitieux. `steps/etat.md` classe Kolibri comme spike non bloquant avec un niveau exact encore ouvert.

## Décision

1. Kolibri est un **spike exploratoire**, pas une dépendance du MVP V0.1.
2. Le spike utilise **uniquement des interfaces documentées** (pas d’API non officielle).
3. L’échec ou le report du spike Kolibri **ne bloque pas** la livraison V0.1.
4. Le niveau exact du spike (POC embed, export channel, etc.) reste **Proposed** jusqu’à validation en étape 12.

## Options étudiées

| Option | Avantages | Inconvénients |
|---|---|---|
| **Spike non bloquant** (retenue) | Protège le délai MVP | Offline non démontré si spike échoue |
| Kolibri intégré au cœur MVP | Démo offline forte | Hors délai, double stack |
| Exclusion totale Kolibri | Focus | Perte exploration différenciante |
| Synchronisation bidirectionnelle | Dossier unifié offline | Complexité excessive pour V0.1 |

## Conséquences

- Spike planifié : `steps/12_deploiement_et_offline/03_spike_kolibri.md`.
- Aucun module métier ne dépend de Kolibri pour fonctionner.
- Résultat attendu : note de faisabilité + démo optionnelle, pas feature production.

## Risques

| Risque | Niveau | Atténuation |
|---|---|---|
| Temps spike grignoté sur MVP | P1 | Timebox strict, priorités GitHub Project |
| Attentes stakeholders sur offline | P2 | Communication : spike ≠ livrable garanti |
| Interfaces Kolibri insuffisantes | P3 | Documenter limites dans le rapport spike |

## Références

- `steps/PROMPT_GENERAL.md` §6, §7
- `steps/etat.md` — Kolibri spike, décision ouverte (niveau exact)
- `steps/12_deploiement_et_offline/03_spike_kolibri.md`
