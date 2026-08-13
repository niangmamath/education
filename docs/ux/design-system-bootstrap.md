# Design system Bootstrap de StudentConnect

## Décision

StudentConnect utilisera Bootstrap 5.3.8 comme socle visuel du frontend. La version sera verrouillée exactement lors de la phase d'implémentation. `react-bootstrap` n'est pas retenu à ce stade : les composants simples seront produits avec React, HTML sémantique et les classes Bootstrap. Les plugins JavaScript Bootstrap ne seront ajoutés que lorsqu'un composant interactif en aura réellement besoin.

## Principes

- interfaces distinctes pour Parent et Élève ;
- une hiérarchie visuelle simple ;
- données fictives toujours signalées ;
- aucune information transmise uniquement par couleur ;
- focus clavier visible ;
- cibles tactiles d'au moins 44 pixels lorsque possible ;
- animations limitées et respect de `prefers-reduced-motion` ;
- composants réutilisables avant multiplication des pages.

## Tokens StudentConnect

Les valeurs définitives seront vérifiées visuellement avant clôture.

### Couleurs fonctionnelles

- primaire : bleu StudentConnect, actions principales et liens ;
- secondaire : turquoise, contexte éducatif et accents ;
- succès : vert accompagné d'un texte explicite ;
- avertissement : jaune ou orange accompagné d'un texte ;
- danger : rouge accompagné d'un texte ;
- surfaces : blanc et gris très clair ;
- texte : gris très foncé sur surface claire.

Les variables personnalisées utiliseront le préfixe `--sc-` et pourront alimenter les variables CSS Bootstrap sans modifier directement les fichiers du paquet.

### Typographie

- police système pour éviter une dépendance réseau ;
- taille de base lisible ;
- titres courts ;
- paragraphes avec largeur raisonnable ;
- textes Élève plus directs, sans infantilisation excessive.

### Espacement et formes

- grille Bootstrap et conteneurs responsives ;
- espacements issus de l'échelle Bootstrap ;
- rayons cohérents pour cartes et boutons ;
- ombres discrètes et non indispensables à la compréhension.

## Composants de base

### Boutons

- primaire : une action principale par zone ;
- secondaire : alternative non destructive ;
- lien : navigation contextuelle ;
- danger : uniquement pour une action réellement destructive ;
- état désactivé accompagné d'une raison lorsque nécessaire.

### Cartes

- titre sémantique ;
- contenu compréhensible sans décoration ;
- action située à la fin ;
- pas de carte cliquable sans indication accessible.

### Alertes

- rôle adapté au message ;
- titre court ;
- explication et prochaine action ;
- icône décorative masquée aux technologies d'assistance.

### Formulaires

- label toujours visible ;
- aide avant l'erreur ;
- erreur associée au champ ;
- état invalide exprimé par texte et style ;
- aucune donnée sensible dans les exemples versionnés.

### Progression

- valeur lisible en texte ;
- `aria-valuenow`, minimum et maximum lorsque le composant est réel ;
- aucune progression fictive présentée comme calculée.

### Navigation

- destination active avec `aria-current="page"` ;
- icône accompagnée d'un libellé ;
- menu mobile utilisable au clavier ;
- focus restauré après fermeture d'un panneau.

## Structure applicative cible

```text
apps/web/
├── app/
│   ├── globals.css
│   └── design-system/
└── components/
    └── ui/
```

La page `design-system` sera une démonstration interne, sans donnée personnelle et sans être présentée comme une fonctionnalité métier terminée.

## Contrôles d'acceptation futurs

- TypeScript ;
- ESLint ;
- build Next.js ;
- navigation clavier ;
- zoom à 200 % ;
- mobile, tablette et bureau ;
- contraste ;
- absence de requête CDN ;
- absence de classes Tailwind après migration complète.
