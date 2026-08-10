# Décisions finales actives

## Produit

- B2C pour élèves de 6 à 11 ans et parents.
- Deux dashboards distincts.
- Quick Repairs de 3 à 7 minutes.
- Score de santé académique explicable.
- Détection de lacunes via arbre de compétences.
- H5P et PhET consommés sans redirection hors StudentConnect.

## Architecture

- Frontend Next.js 16 et Tailwind CSS 4.
- Backend FastAPI.
- REST, pas GraphQL.
- PostgreSQL, pas Neo4j pour le MVP.
- SQLAlchemy 2 et Alembic.
- Redis et Celery.
- Stockage compatible S3.
- Monolithe modulaire backend.
- Monorepo pour frontend, backend, packages et infrastructure.

## Authentification

- Parent : email, mot de passe et email vérifié.
- Enfant : profil rattaché, pseudonyme et PIN haché.
- Sessions opaques en cookie HttpOnly, Secure et SameSite.
- Sessions stockées dans Redis.

## H5P

- Lecture par `h5p-standalone`.
- Import de paquets déjà produits.
- Pas d’éditeur H5P complet.
- Quarantaine, scan, contrôle ZIP et extraction versionnée.
- Origine de contenu isolée.
- Capture xAPI par dispatcher et bridge `postMessage`.

## PhET

- Simulations HTML5 françaises en iframe.
- Attribution et licence vérifiées.
- La preuve finale vient d’un mini-test StudentConnect.

## Performance

- LCP inférieur à 2 secondes pour le rendu initial défini.
- H5P et PhET chargés après le premier rendu.
- Budgets de bundle et Lighthouse CI.

## Pilotage

- Pas de GitHub Project.
- Planning dans `PLANNING.md`.
- Rapports Markdown par sous-étape.
- `ETAT.md` comme source de vérité opérationnelle.
