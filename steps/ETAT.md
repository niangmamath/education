# État du projet

## Référence

- Projet : StudentConnect
- Date : 11 août 2026
- Dépôt : `tidianesarrndiaye-org/StudentConnect`
- Branche attendue : `main`
- Version cible : `V0.1`

## Terminé

- [x] Dépôt reconstruit depuis zéro.
- [x] Fichiers racine et ADR initiaux.
- [x] Monorepo pnpm/Turborepo.
- [x] Frontend Next.js et Tailwind initialisé.
- [x] Backend FastAPI initialisé.
- [x] Environnement Python Linux `.venv` opérationnel à la racine.
- [x] Node.js et pnpm natifs Linux dans WSL.

## Étape 03, infrastructure locale et CI

- [x] 03.1 Docker Compose validé de bout en bout.
- [x] 03.2 SQLAlchemy async et Alembic validés.
- [x] 03.3 Contrôles locaux frontend et backend validés.
- [x] Workflows GitHub Actions présents et syntaxiquement valides.
- [x] Script global `check_step03.sh` terminé avec le code `0`.
- [x] Rapports de l’étape 03 produits.
- [ ] Commit de clôture créé.
- [ ] Push vers `origin/main` réalisé.
- [ ] Exécution distante des workflows GitHub Actions confirmée.

## Résultats techniques de référence

```text
PostgreSQL : healthy, base et rôle studentconnect
Redis      : healthy, PONG
MinIO      : healthy, cinq buckets privés
FastAPI    : healthy, /health/live → live
Celery     : pong, tâche de santé réussie
Alembic    : 0001_infrastructure_baseline (head)
Ruff       : vert
Mypy       : vert sur 11 fichiers
Pytest     : 12 tests réussis
TypeScript : vert
ESLint     : vert
Next.js    : build de production réussi
```

## Corrections d’état

Les anciens rapports du 11 août 2026 annonçant 03.1, 03.2 et 03.3 comme terminés avant la résolution des erreurs ont été retirés et remplacés par les rapports horodatés `2026-08-11_1709`.

## Organisation des étapes

Les dossiers futurs `steps/04_*` à `steps/16_*` sont temporairement retirés du dépôt. Chaque dossier sera régénéré proprement au démarrage de l’étape correspondante.

## Décisions ouvertes

- Hébergeur Next.js.
- Hébergeur FastAPI.
- PostgreSQL managé.
- Redis managé.
- Stockage S3 et CDN de production.
- Domaine et sous-domaines.
- Région des données.
- Budget mensuel.
- Types H5P autorisés dans le MVP.
- Licence des paquets H5P pilotes.
- Modèle économique et licence PhET.
- Programme scolaire et compétences pilotes.

## Prochaine action

1. Vérifier le diff indexé et l’absence de secrets.
2. Créer le commit de clôture de l’étape 03.
3. Pousser vers `origin/main`.
4. Vérifier l’exécution distante de GitHub Actions.
5. Passer `P0-05` à Terminé après validation distante.
6. Préparer l’étape 04 H5P.

## Derniers rapports appliqués

- `rapport_2026-08-11_1709_docker_compose.md`
- `rapport_2026-08-11_1709_base_migrations.md`
- `rapport_2026-08-11_1709_ci.md`
- `rapport_2026-08-11_1709_etape_complete.md`
