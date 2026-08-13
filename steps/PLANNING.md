# Planning simple de développement

## Principes

- Statuts : À faire, En cours, Bloqué, En revue, Terminé.
- Une tâche terminée doit disposer d’une preuve reproductible.
- Une tâche bloquée doit référencer un rapport.
- Le commit, le push et la CI distante font partie de la clôture d’une étape d’infrastructure.

## Phase 0, préparation et infrastructure

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| P0-01 | Vérifier le dépôt vidé | Aucune | Terminé | Rapport étape 01 |
| P0-02 | Recréer les fichiers racine | P0-01 | Terminé | README, gitignore, env example |
| P0-03 | Créer les ADR initiaux | P0-02 | Terminé | ADR et registre |
| P0-04 | Initialiser le monorepo | P0-03 | Terminé | Rapports étape 02 |
| S1-01 | Initialiser Next.js et Tailwind | P0-03 | Terminé | TypeScript, ESLint et build verts |
| S1-02 | Initialiser FastAPI | P0-03 | Terminé | API, CORS et tests verts |
| P0-05A | Configurer Docker Compose | P0-04, S1-02 | Terminé | Services healthy, Celery et buckets |
| S1-03 | Configurer SQLAlchemy et Alembic | S1-02, P0-05A | Terminé | Upgrade, downgrade et head |
| S1-07 | Configurer la CI | S1-01, S1-02, S1-03 | Terminé | API CI, Web CI et Secret Scan réussis |
| P0-05 | Clôturer l’infrastructure locale | P0-05A, S1-03, S1-07 | Terminé | Rapports, commits, push et CI distante |
| P0-06 | Réaliser le spike H5P | P0-05 | Terminé | Rendu True/False et événement xAPI validés |
| P0-07 | Geler les types H5P autorisés | P0-06 | Terminé | ADR-011, True/False pilote uniquement |

## Preuves de clôture de P0-05

- [x] Script global local terminé avec code `0`.
- [x] Rapports de l’étape 03 produits.
- [x] Commit principal `d7a7262` poussé sur `main`.
- [x] Correctif Secret Scan `6bcf765` poussé sur `main`.
- [x] API CI distante réussie.
- [x] Web CI distante réussie.
- [x] Secret Scan distant réussi.

## Prochaine tâche

`P0-06`, réaliser le spike H5P critique.

Le dossier `steps/04_spike_h5p_critique` doit être régénéré proprement au démarrage de cette tâche.
