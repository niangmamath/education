# Étape 04.2, valider la lecture H5P Standalone

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Afficher un paquet H5P extrait sans Moodle ni redirection.

## Travaux obligatoires


1. Créer un prototype isolé de lecture avec `h5p-standalone`.
2. Extraire le paquet dans un répertoire de test versionné.
3. Charger l’activité dans une iframe ou origine dédiée simulée.
4. Vérifier styles, scripts, resize, clavier et mobile.
5. Documenter toutes les dépendances H5P nécessaires.
6. Ne pas intégrer encore l’upload complet.


## Critères d’acceptation


- [ ] L’activité s’affiche sans redirection.
- [ ] Les assets sont chargés localement.
- [ ] Aucun appel inattendu vers un fournisseur n’est nécessaire.
- [ ] Le comportement mobile est documenté.


## Livrables

Prototype de lecture, matrice de compatibilité et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
