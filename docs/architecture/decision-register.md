# Registre des décisions — StudentConnect V0.1

**Dernière mise à jour :** 2026-08-07  
**Source :** audit initial + consolidation ADR étape `01_gouvernance_et_audit`

---

## Décisions architecturales (ADR)

| ID | Titre | Statut | Fichier |
|---|---|---|---|
| ADR-001 | Monolithe modulaire Django | Accepted | [ADR-001](../adr/ADR-001-monolithe-modulaire-django.md) |
| ADR-002 | Bootstrap 5 et HTMX, pas Tailwind | Accepted | [ADR-002](../adr/ADR-002-bootstrap-5-htmx.md) |
| ADR-003 | PostgreSQL pour compétences et relations | Accepted | [ADR-003](../adr/ADR-003-postgresql-competences.md) |
| ADR-004 | Stratégie H5P | Accepted (piste) / **Proposed** (hébergement) | [ADR-004](../adr/ADR-004-strategie-h5p.md) |
| ADR-005 | CK-12, Khan Academy et PhET | Accepted | [ADR-005](../adr/ADR-005-integrateurs-ck12-khan-phet.md) |
| ADR-006 | Données fictives et protection enfant | Accepted | [ADR-006](../adr/ADR-006-donnees-fictives-protection-enfant.md) |
| ADR-007 | Kolibri spike non bloquant | Accepted | [ADR-007](../adr/ADR-007-kolibri-spike-non-bloquant.md) |

---

## Décisions produit validées (hors ADR détaillé)

| Sujet | Décision | Référence |
|---|---|---|
| Utilisateurs centraux | Élève + parent/tuteur | `steps/etat.md` |
| Enseignant / valideur | Facultatif V0.1 | `steps/etat.md` |
| Note vs compétence | Une note ne remplace jamais une compétence | `steps/PROMPT_GENERAL.md` §3 |
| Historique | Aucune observation antérieure écrasée | `steps/PROMPT_GENERAL.md` §3 |
| APIs non officielles | Jamais dépendance critique | ADR-005, `steps/PROMPT_GENERAL.md` §3 |

---

## Décisions ouvertes (non inventées)

| Sujet | Statut | Bloquant pour | Action |
|---|---|---|---|
| Programme scolaire et pays | Ouvert | Étape 03 | Atelier cadrage |
| Classe / tranche d’âge pilote | Ouvert | Étape 03 | Atelier cadrage |
| Trois matières prioritaires | Ouvert | Étape 03 | Atelier cadrage |
| 10–20 compétences pilotes | Ouvert | Étape 03 | Atelier cadrage |
| Hébergement H5P | **Proposed** (ADR-004) | Étape 04 spike | Issue à créer |
| Hébergeur démonstration | Ouvert | Étape 12 | ADR futur |
| Niveau exact spike Kolibri | **Proposed** (ADR-007) | Étape 12 | Timebox spike |
| Politique conservation données post-stage | Ouvert | Post-V0.1 | Hors périmètre stage |

---

## Issues GitHub

Aucune issue n’était ouverte au moment de l’audit (2026-08-07). Issues recommandées :

| Sujet suggéré | Priorité | Epic |
|---|---|---|
| Décision hébergement H5P | P1 | M04 / M06 |
| Validation référentiel pilote | P1 | M03 |
| Initialisation socle Django | P0 | M11 |

---

## Historique

| Date | Action |
|---|---|
| 2026-08-07 | Création registre et ADR-001 à ADR-007 (étape 01.2) |
