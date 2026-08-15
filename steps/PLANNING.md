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
| P0-07 | Geler les types H5P autorisés | P0-06 | Terminé | ADR-012, True/False pilote uniquement |

## Preuves de clôture de P0-05

- [x] Script global local terminé avec code `0`.
- [x] Rapports de l’étape 03 produits.
- [x] Commit principal `d7a7262` poussé sur `main`.
- [x] Correctif Secret Scan `6bcf765` poussé sur `main`.
- [x] API CI distante réussie.
- [x] Web CI distante réussie.
- [x] Secret Scan distant réussi.

### Phase 1, UX design et navigation

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| UX-01 | Définir les parcours utilisateurs | P0-07 | Terminé | Personas, parcours et matrice besoins-écrans |
| UX-02 | Définir les routes et la navigation | UX-01 | Terminé | Routes MVP et règles d’accès |
| UX-03 | Migrer le design system vers Bootstrap | UX-02 | Terminé | Bootstrap 5.3.8, Tailwind retiré, build vert |
| UX-04 | Concevoir l’espace Parent | UX-03 | Terminé | Layout et routes Parent validés |
| UX-05 | Concevoir l’espace Élève | UX-03 | Terminé | Layout et routes Élève validés |
| UX-06 | Valider les états et l’accessibilité | UX-04, UX-05 | Terminé | Validation manuelle et page accessibilité |
| UX-07 | Clôturer l’étape 05 | UX-06 | Terminé | Rapport, fusion et contrôles distants verts |

### Phase 2, backend identité et famille

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| BE-01 | Modéliser Parent et Enfant | UX-07 | Terminé | Migration `0002`, `alembic check` vert |
| BE-02 | Authentifier le Parent et ouvrir des sessions | BE-01 | Terminé | Sessions Redis, cookie durci, réponses indistinctes |
| BE-03 | Créer et connecter l’Enfant | BE-02 | Terminé | Code famille, unicité familiale, verrou PIN, 123 tests |
| BE-04 | Clôturer l’étape 06 | BE-03 | Terminé | Rapport du 14 août 2026, PR #4 fusionnée, CI verte sur `main` |
| BE-05 | Résorber la dette de l’étape 06 | BE-04 | Terminé | Cycle de vie du profil, retour arrière de `0003`, ADR-005 amendée |

### Preuves de clôture de BE-04

- [x] Rapport de validation produit et appliqué à `ETAT.md`.
- [x] Pull Request #4 fusionnée dans `main`, commit `a49ec43`.
- [x] API CI distante réussie sur la Pull Request puis sur `main`.
- [x] Secret Scan distant réussi sur la Pull Request puis sur `main`.

### Phase 3, référentiel de compétences

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| REF-01 | Modéliser le référentiel scolaire | BE-05 | Terminé | Migration `0004`, 23 tests de contraintes, rapport du 14 août 2026 |
| REF-02 | Importer un référentiel fictif de façon idempotente | REF-01 | Terminé | PR #11 fusionnée, CI verte sur `main`, rapport du 14 août 2026 |
| REF-03 | Exposer les lectures filtrées et paginées | REF-02 | Terminé | Commande `publish`, quatre routes, 37 tests, rapport du 15 août 2026 |
| REF-04 | Clôturer l’étape 07 | REF-03 | Terminé | Séquence de l’API CI rejouée, 255 tests, Pull Request unique |

### Prochaine tâche

Ouvrir l’étape 08, catalogue de contenus et activités.
