# Validation des états et de l’accessibilité

## Portée

Cette validation concerne le prototype UX de l’étape 05. Elle ne constitue pas encore un audit de conformité complet.

## Résultats de l’audit statique

- Chaque page possède un titre principal `h1` unique.
- Les espaces Parent et Élève possèdent un landmark `main` dans leur layout.
- Les navigations utilisent un nom accessible et `aria-current="page"`.
- Le sélecteur d’enfant possède un label associé.
- Les icônes décoratives sont masquées aux technologies d’assistance directement ou par un parent `aria-hidden`.
- Le focus global est visible.
- `prefers-reduced-motion` désactive le défilement doux et réduit les transitions.
- Les données de prototype sont signalées comme fictives.
- Les états de santé associent couleur, texte et icône.

## Corrections intégrées

- hauteur tactile minimale de 44 pixels pour les navigations Parent et Élève ;
- correction des textes `Indisponible dans le prototype` et `difficulté fictive` ;
- page interne présentant chargement, vide, erreur, succès, accès refusé, connexion requise, contenu indisponible et réseau dégradé ;
- page introuvable personnalisée avec une destination sûre.

## Contrôles manuels à renseigner

- [x] Navigation complète au clavier.
- [x] Focus visible sur chaque élément interactif.
- [x] Zoom navigateur à 200 % sans perte de contenu.
- [x] Affichage mobile sans défilement horizontal bloquant.
- [x] Affichage tablette et bureau.
- [x] Messages compréhensibles sans dépendre de la couleur.
- [x] Cibles tactiles principales suffisamment grandes.
- [x] Aucun message d’erreur ou d’hydratation dans la console.

## Limites

- aucune technologie d’assistance réelle n’a encore été utilisée ;
- aucun audit automatisé WCAG complet n’est revendiqué ;
- les routes protégées ne disposent pas encore d’une authentification réelle ;
- les données métier et les interactions réseau restent hors périmètre.
