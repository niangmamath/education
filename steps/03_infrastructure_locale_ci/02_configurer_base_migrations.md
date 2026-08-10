# Étape 03.2, configurer SQLAlchemy et Alembic

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Connecter FastAPI à PostgreSQL et établir la politique de migrations.

## Travaux obligatoires


1. Configurer engine, sessions et transactions.
2. Choisir sync ou async et consigner la décision.
3. Initialiser Alembic.
4. Créer une migration technique minimale si nécessaire.
5. Ajouter un check empêchant les migrations divergentes.
6. Documenter création, upgrade, downgrade et vérification.
7. Ajouter tests de transaction et connexion.


## Critères d’acceptation


- [ ] Alembic applique les migrations sur une base vide.
- [ ] Le downgrade de la migration initiale est testé.
- [ ] La session est fermée correctement.
- [ ] La décision sync/async est documentée.


## Livrables

Configuration DB, ADR si nécessaire et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
