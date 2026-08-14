# Étape 06, backend identité et famille

## Objectif

Implémenter l’identité Parent et Élève, les relations familiales et les sessions serveur conformément à ADR-005.

## Ordre obligatoire

1. `01_modeles_users.md`
2. `02_auth_parent_sessions.md`
3. `03_acces_enfant.md`
4. clôture et validation distante

## Hors périmètre

- activités et exercices ;
- résultats et progression ;
- dashboards alimentés ;
- H5P de production ;
- notifications métier.

## Règles

- le parent utilise email et mot de passe ;
- l’enfant n’a ni email ni téléphone ;
- l’enfant utilise un pseudonyme et un PIN haché ;
- le pseudonyme est unique dans la famille, jamais sur la plateforme ;
- l’enfant atteint sa famille par le code famille de son parent ;
- les sessions opaques seront stockées dans Redis ;
- un parent ne peut accéder qu’aux enfants associés ;
- toutes les données de stage restent fictives.
