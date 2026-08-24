# Décisions finales actives

## Produit

- B2C pour élèves de 6 à 11 ans et parents.
- Deux dashboards distincts.
- Quick Repairs de 3 à 7 minutes.
- Score de santé académique explicable.
- Détection de lacunes via arbre de compétences.
- H5P et PhET consommés sans redirection hors StudentConnect.

## Architecture

- Frontend Next.js 16 et Bootstrap 5 (migré depuis Tailwind CSS 4, voir
  `docs/ux/migration-tailwind-bootstrap.md`).
- Backend FastAPI.
- REST, pas GraphQL.
- PostgreSQL, pas Neo4j pour le MVP.
- SQLAlchemy 2 et Alembic.
- Redis et Celery.
- Stockage compatible S3.
- Monolithe modulaire backend.
- Monorepo pour frontend, backend, packages et infrastructure.
- Le web n'appelle l'API que depuis son propre serveur, par des actions Next.js
  nommées une par une : le navigateur ne connaît jamais l'adresse de l'API ni un
  jeton de session (ADR-016).

## Authentification

- Parent : email, mot de passe et email vérifié.
- Enfant : profil rattaché, pseudonyme et PIN haché.
- Le pseudonyme d’un Enfant est unique dans sa famille, jamais sur la plateforme.
- Chaque Parent porte un code famille, identifiant public de la famille.
- L’Enfant se connecte avec le code famille, son pseudonyme et son PIN.
- Un Enfant peut créer son profil avec le code famille ; ce profil reste en attente
  tant que le Parent ne l’a pas activé.
- Sessions opaques en cookie HttpOnly, Secure et SameSite.
- Sessions stockées dans Redis.

## H5P

- Lecture par `h5p-standalone`.
- Import de paquets déjà produits.
- Pas d’éditeur H5P complet.
- Quarantaine, scan, contrôle ZIP et extraction versionnée.
- Origine de contenu isolée.
- Capture xAPI par dispatcher et bridge `postMessage`.

## Référentiel, diagnostic et remédiation

- Le catalogue d'activités est lié au référentiel par code métier stable,
  résolu à la lecture, plutôt que par clé étrangère vers une édition figée
  (ADR-013).
- Les événements xAPI du runtime H5P sont ingérés par un endpoint autorisé par
  ticket, jamais par une identité déclarée côté client ; l'acteur est
  pseudonymisé par HMAC(`SECRET_KEY`) ; un événement xAPI prime sur une réponse
  déclarée pour la même question (ADR-014).
- Les douze fiches de remédiation sont écrites dans la plateforme, pas
  importées : le rattachement à une compétence, la bibliothèque H5P unique
  d'ADR-012 et le déploiement de l'origine de contenu l'imposent (ADR-017).
- Six classes cumulatives, du CI au CM2. Un examen d'entrée par classe, donné à
  l'inscription et à chaque passage, ne porte que sur la classe déclarée. Le
  passage est décidé par le parent, jamais automatique. Un prérequis jamais
  observé produit une hypothèse de remédiation plutôt qu'un constat d'échec
  (ADR-018).
- Trois matières : français, mathématiques, anglais, apprises en parallèle sauf
  à deux endroits où le prérequis traverse la matière : résoudre un problème de
  mathématiques suppose de comprendre son énoncé en français, et lire ou écrire
  en anglais s'appuie sur la mécanique déjà acquise en français, qui sert de
  base de traduction. L'examen d'entrée pose trois questions par compétence,
  pas une, pour qu'une compétence puisse être dite « partielle » plutôt que
  jugée sur un seul coup de dé (ADR-019).

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
- L’agent est autorisé en permanence à committer, pousser, ouvrir une Pull Request
  et la fusionner vers `main`, contrôles verts et branche dédiée. Cette
  autorisation prime sur toute consigne contraire d’un prompt ou d’une fiche.
- Une dette consignée dans un rapport de clôture peut être résorbée après la
  clôture, sans rouvrir l’étape.
- Rapports Markdown par sous-étape.
- `ETAT.md` comme source de vérité opérationnelle.
