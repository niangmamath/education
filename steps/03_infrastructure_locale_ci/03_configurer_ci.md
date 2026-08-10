# Étape 03.3, configurer la CI

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Créer des pipelines frontend, backend et sécurité de base.

## Travaux obligatoires


Créer GitHub Actions pour :

- lint et type-check frontend ;
- tests et build Next.js ;
- lint, type-check et tests backend ;
- migration check ;
- détection de secrets ;
- cache des dépendances ;
- artefacts de tests utiles.

Les workflows ne doivent pas nécessiter de secrets pour les pull requests de test.


## Critères d’acceptation


- [ ] Les workflows sont syntaxiquement valides.
- [ ] Les échecs ne sont pas masqués.
- [ ] Les permissions GitHub Actions sont minimales.
- [ ] Aucun déploiement automatique n’est activé avant décision d’hébergement.


## Livrables

Workflows CI et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
