# Etat du projet

## Reference

- Projet : StudentConnect
- Date : 11 aout 2026
- Branche attendue : main
- Version cible : V0.1

## Termine

- [x] Depot reconstruit depuis zero.
- [x] Fichiers racine et ADR initiaux.
- [x] Monorepo pnpm/Turborepo.
- [x] Frontend Next.js/Tailwind initialise.
- [x] Backend FastAPI initialise.
- [x] Environnement Python local `.venv` cree.

## Etape active

- [ ] 03.1 Docker Compose valide de bout en bout.
- [ ] 03.2 SQLAlchemy async et Alembic valides.
- [ ] 03.3 CI frontend/backend/secrets validee.
- [ ] 03.4 Rapport de cloture, commit et push.

## Correction d'etat

Les anciens rapports du 11 aout annoncant 03.1, 03.2 et 03.3 comme termines sont invalides, car les executions ont revele un conflit de port PostgreSQL puis un volume initialise avec un role incorrect. Ils sont retires avant la reprise.

## Dette connue issue de l'etape 02

- Lint Next.js a verifier et corriger.
- Test CORS FastAPI a verifier et corriger.
- Les paquets Python doivent etre assures dans l'image Docker, independamment du `.venv` Windows.

## Prochaine action

Extraire le correctif, executer les deux scripts de preparation, puis suivre `steps/03_infrastructure_locale_ci/01_docker_compose.md`.
