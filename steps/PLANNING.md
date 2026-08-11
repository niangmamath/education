# Planning simple de développement

## Principes

- Statuts : À faire, En cours, Bloqué, En revue, Terminé.
- Une tâche terminée doit disposer d’une preuve reproductible.
- Une tâche bloquée doit référencer un rapport.
- Le commit et le push font partie de la clôture d’une étape.

## Phase 0, préparation et infrastructure

| ID | Travail | Dépendances | Statut | Preuve attendue |
|---|---|---|---|---|
| P0-01 | Vérifier le dépôt vidé | Aucune | Terminé | Rapport étape 01 |
| P0-02 | Recréer les fichiers racine | P0-01 | Terminé | README, gitignore, env example |
| P0-03 | Créer les ADR initiaux | P0-02 | Terminé | ADR et registre |
| P0-04 | Initialiser le monorepo | P0-03 | Terminé | Rapports étape 02 |
| S1-01 | Initialiser Next.js et Tailwind | P0-03 | Terminé | TypeScript, ESLint et build verts |
| S1-02 | Initialiser FastAPI | P0-03 | Terminé | API, CORS et tests verts |
| P0-05A | Configurer Docker Compose | P0-04, S1-02 | Terminé | Services healthy, Celery et buckets |
| S1-03 | Configurer SQLAlchemy et Alembic | S1-02, P0-05A | Terminé | Upgrade, downgrade et head |
| S1-07 | Configurer la CI | S1-01, S1-02, S1-03 | Terminé localement | Contrôles locaux et YAML valides |
| P0-05 | Clôturer l’infrastructure locale | P0-05A, S1-03, S1-07 | En revue | Rapports, commit, push et CI distante |
| P0-06 | Réaliser le spike H5P | P0-05 | À faire | Lecture Standalone et événement xAPI |
| P0-07 | Geler les types H5P autorisés | P0-06 | À faire | ADR H5P mis à jour |

## Conditions pour passer P0-05 à Terminé

- [x] Script global local terminé avec code `0`.
- [x] Quatre rapports de l’étape 03 produits.
- [x] `ETAT.md` et `PLANNING.md` mis à jour.
- [ ] Commit créé.
- [ ] Push vers `origin/main` réalisé.
- [ ] GitHub Actions distantes contrôlées.

## Étapes futures

Les dossiers détaillés des étapes 04 à 16 seront régénérés au démarrage de chaque étape. Le prochain dossier à créer sera `steps/04_spike_h5p_critique` après la clôture effective de P0-05.
