# Prompt 02.3, ajouter tests, qualité et CI

## Outils

pytest, pytest-django, coverage, Ruff, Black, djLint et GitHub Actions.

## Travaux

- configurer les outils dans `pyproject.toml` ;
- créer un test du health check ;
- ajouter une CI exécutant lint, format check, migrations check et tests ;
- documenter les commandes locales ;
- ne pas imposer une couverture irréaliste au premier commit.

## Critères

- les commandes passent localement ;
- le workflow CI est valide ;
- la CI n’expose aucun secret ;
- le rapport indique les résultats exacts.
