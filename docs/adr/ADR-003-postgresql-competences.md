# ADR-003 : PostgreSQL pour les compétences et relations

| Attribut | Valeur |
|---|---|
| **Statut** | Accepted |
| **Date** | 2026-08-07 |
| **Décideurs** | Équipe stage StudentConnect |
| **Issue GitHub** | — |

## Contexte

StudentConnect modélise un dossier longitudinal, un référentiel de compétences, des relations entre lacunes localisées et générales, et un historique d’observations jamais écrasé. Ces structures impliquent des relations many-to-many, des contraintes d’intégrité et des requêtes analytiques simples.

## Décision

Utiliser **PostgreSQL** comme SGBD unique pour la V0.1, hébergé via **Docker Compose** en développement et compatible avec un hébergeur de démonstration en production.

## Options étudiées

| Option | Avantages | Inconvénients |
|---|---|---|
| **PostgreSQL** (retenue) | Relations riches, JSONB si besoin, écosystème Django mature, production-ready | Nécessite Docker ou service managé |
| SQLite | Zéro configuration | Insuffisant pour relations complexes et démo multi-utilisateurs |
| MySQL / MariaDB | Répandu | Moins aligné avec conventions Django modernes |
| MongoDB | Flexibilité schéma | Incohérent avec ORM Django relationnel, historique difficile |

## Conséquences

- Django ORM cible PostgreSQL exclusivement en V0.1.
- `docker-compose.yml` fournit PostgreSQL + service web.
- Les migrations Django portent le référentiel de compétences et les relations inter-matières.
- Pas de double base (analytics séparée) en V0.1.

## Risques

| Risque | Niveau | Atténuation |
|---|---|---|
| Complexité modèle compétences / lacunes | P1 | Modélisation progressive étape 03 |
| Hébergeur démo sans PostgreSQL | P2 | Choisir hébergeur compatible (étape 12) |
| Données fictives insuffisantes pour tester relations | P2 | Fixtures étape 11 |

## Références

- `steps/PROMPT_GENERAL.md` §4
- `steps/02_socle_technique/02_postgresql_docker.md`
