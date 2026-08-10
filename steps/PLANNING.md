# Planning simple de développement

## Principes

- Le planning est la source de pilotage principale.
- Chaque ligne passe par : À faire, En cours, Bloqué, En revue, Terminé.
- Une tâche bloquée doit référencer un rapport.
- Les dates sont ajustables, mais les dépendances ne doivent pas être ignorées.

## Phase 0, préparation et spike critique

| ID | Travail | Dépendance | Statut | Livrable |
|---|---|---|---|---|
| P0-01 | Vérifier le dépôt vidé | Aucune | Terminé | Rapport d’audit |
| P0-02 | Recréer les fichiers racine | P0-01 | Terminé | README, gitignore, env example |
| P0-03 | Créer les ADR initiaux | P0-02 | Terminé | ADR 000-010, registre |
| P0-04 | Initialiser le monorepo | P0-03 | À faire | Apps et packages |
| P0-05 | Configurer Docker local | P0-04 | À faire | PostgreSQL, Redis, stockage |
| P0-06 | Réaliser le spike H5P | P0-05 | À faire | Preuve lecture + xAPI |
| P0-07 | Geler les types H5P autorisés | P0-06 | À faire | ADR H5P |

## Sprint 1, fondations et identité familiale

| ID | Travail | Dépendance | Statut | Livrable |
|---|---|---|---|---|
| S1-01 | Initialiser Next.js et Tailwind | P0-03 | À faire | Frontend |
| S1-02 | Initialiser FastAPI | P0-03 | À faire | Backend |
| S1-03 | Configurer SQLAlchemy et Alembic | S1-02 | À faire | Base |
| S1-04 | Créer auth Parent | S1-03 | À faire | Session parent |
| S1-05 | Créer profils Élève et PIN | S1-04 | À faire | Accès enfant |
| S1-06 | Créer layouts Parent et Élève | S1-01 | À faire | Dashboards vides |
| S1-07 | Configurer CI | S1-01,S1-02 | À faire | Workflows |

## Sprint 2, compétences, évaluations et lacunes

| ID | Travail | Dépendance | Statut | Livrable |
|---|---|---|---|---|
| S2-01 | Définir référentiel pilote | S1 | À faire | Compétences |
| S2-02 | Implémenter arbre de compétences | S2-01 | À faire | Relations |
| S2-03 | Implémenter diagnostic interne | S2-02 | À faire | Évaluation |
| S2-04 | Calculer résultats par compétence | S2-03 | À faire | Résultats |
| S2-05 | Détecter les lacunes | S2-04 | À faire | Gaps |
| S2-06 | Calculer score de santé initial | S2-05 | À faire | Score |
| S2-07 | Afficher alerte Parent | S2-06 | À faire | UI Parent |

## Sprint 3, contenus et Quick Repairs

| ID | Travail | Dépendance | Statut | Livrable |
|---|---|---|---|---|
| S3-01 | Content Studio minimal | P0-05 | À faire | Import H5P |
| S3-02 | Pipeline de quarantaine | S3-01 | À faire | Worker sécurisé |
| S3-03 | Publication H5P versionnée | S3-02 | À faire | Runtime |
| S3-04 | Lecteur et bridge xAPI | S3-03 | À faire | Lecture native |
| S3-05 | Intégration PhET | S2-02 | À faire | Module PhET |
| S3-06 | Association gap-contenu | S2-05,S3-03 | À faire | Mapping |
| S3-07 | Générer Quick Repair | S3-06 | À faire | Parcours court |
| S3-08 | Réévaluer et mettre à jour | S3-07 | À faire | Progression |

## Sprint 4, dashboards et release

| ID | Travail | Dépendance | Statut | Livrable |
|---|---|---|---|---|
| S4-01 | Finaliser dashboard Élève | S3 | À faire | UI Élève |
| S4-02 | Finaliser dashboard Parent | S3 | À faire | UI Parent |
| S4-03 | Notifications | S4-02 | À faire | Alertes |
| S4-04 | Sécurité et upload hostile | S3-02 | À faire | Rapport sécurité |
| S4-05 | Performance et Lighthouse | S4-01,S4-02 | À faire | Rapport performance |
| S4-06 | Tests E2E et acceptation | S4 | À faire | Matrice CA |
| S4-07 | Déploiement | S4-06 | À faire | Environnement démo |
| S4-08 | Documentation et release | S4-07 | À faire | V0.1 |
