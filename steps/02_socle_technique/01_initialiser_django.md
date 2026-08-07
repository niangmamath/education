# Prompt 02.1, initialiser le socle Django

Analyse d’abord l’état du dépôt. Si Django existe déjà, améliore l’existant au lieu de recréer le projet.

## Stack

- Python 3.12
- Django 5.x
- Django REST Framework
- Bootstrap 5
- HTMX
- PostgreSQL

## Travaux

1. Créer ou vérifier l’environnement Python et `pyproject.toml`.
2. Créer `config/` et `apps/` selon l’architecture décidée.
3. Configurer les settings par environnement si nécessaire.
4. Ajouter `.env.example` sans secret.
5. Configurer templates, static, Bootstrap et HTMX.
6. Créer une page d’accueil minimale et un health check.
7. Ajouter `README.md` avec démarrage local.

## Critères

- serveur Django démarre ;
- page d’accueil responsive Bootstrap ;
- health check répond ;
- aucune dépendance Tailwind ;
- aucune donnée sensible.

Créer le rapport de réalisation.
