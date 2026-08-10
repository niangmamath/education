# Étape 08.2, implémenter les lacunes

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Détecter lacunes localisées et causes racines candidates.

## Travaux obligatoires


1. Créer Gaps et GapMemberships.
2. Implémenter règles : score < 60 % sur deux tentatives, niveau attendu/observé, prérequis manquant.
3. Calculer sévérité et confiance.
4. Regrouper des gaps locaux partageant un prérequis.
5. Produire une explication lisible.
6. Ne jamais présenter une hypothèse comme certitude.
7. Ajouter tests.


## Critères d’acceptation


- [ ] Deux tentatives peuvent créer un gap.
- [ ] Le même événement ne crée pas deux gaps identiques.
- [ ] GeneralGap conserve les gaps locaux.
- [ ] Explication et confiance disponibles.


## Livrables

Moteur de gaps et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
