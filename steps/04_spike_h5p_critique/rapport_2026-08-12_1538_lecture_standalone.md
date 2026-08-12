# Rapport de validation du lecteur H5P Standalone

## Métadonnées

- Étape : `04_spike_h5p_critique`
- Sous-étape : `02_preparer_lecteur_standalone`
- Date : 12 août 2026
- Branche : `spike/h5p-critical`
- Statut : **Terminé pour le paquet pilote True/False**

## Paquet pilote

- Fichier local : `true-false-question-34806.h5p`
- Bibliothèque principale : `H5P.TrueFalse 1.8`
- SHA-256 : `9914c27552f00aa91d4a29e85f6a299b11f984030c3451658fb0246f84b07f3c`
- Usage : local uniquement pour le spike
- Redistribution Git : interdite à ce stade

## Runtime

- `h5p-standalone` : `3.8.2`
- `h5p-cli` : `1.1.4`
- Node.js : `22.23.2`
- pnpm : `11.21.0`
- Serveur local : `http://127.0.0.1:4174/`

## Problèmes rencontrés et corrigés

1. Installation pnpm exécutée dans le workspace racine au lieu du projet expérimental isolé.
2. Script `preinstall` de `h5p-standalone` bloqué par pnpm alors que les assets `dist` étaient déjà publiés.
3. Commande obsolète du CLI H5P remplacée par `h5p-cli setup`.
4. Copie en double des bibliothèques depuis `libraries/` et `temp/`.
5. La copie source non compilée de `H5P.Components` écrasait la copie compilée.
6. Les requêtes `h5p-components.css` et `h5p-components.js` retournaient initialement `404`.

## Validation finale

- 13 bibliothèques H5P uniques normalisées.
- 53 assets JavaScript et CSS déclarés vérifiés.
- `H5P.Components-1.0/dist/h5p-components.css` répond `200`.
- `H5P.Components-1.0/dist/h5p-components.js` répond `200`.
- Le paquet est extrait de manière sûre.
- Le contenu True/False est visible dans le navigateur.
- L’image de l’Opéra d’Oslo est visible.
- Les choix `Yes` et `No` sont visibles.
- Le bouton de vérification fonctionne.
- Une réponse correcte produit un score de `1/1`.
- Le message `You got 1 out of 1 points` est affiché.
- `Rights of use` est accessible.
- Le seul `404` observé après correction concerne `favicon.ico`, sans effet fonctionnel.
- Aucun paquet `.h5p` n’est suivi par Git.

## Décision

La lecture locale de `H5P.TrueFalse 1.8` avec `h5p-standalone 3.8.2` est validée pour le spike StudentConnect. Cette validation ne couvre pas encore la production, les autres types H5P ou le stockage définitif.

## Prochaine sous-étape

Capturer un événement xAPI réel produit par une interaction True/False.
