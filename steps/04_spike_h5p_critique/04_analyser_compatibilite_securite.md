# 04.4, analyser la compatibilité et la sécurité

## Objectif

Décider si le lecteur et les paquets pilotes peuvent entrer dans le périmètre du MVP.

## Axes d’analyse

### Compatibilité

- rendu dans Chromium sous WSL/Windows ;
- comportement responsive ;
- support clavier observé ;
- chargement des médias ;
- xAPI réellement émis ;
- fonctionnement sans CDN ;
- dépendances incluses dans le paquet.

### Sécurité

- chemins d’archive et tentative de Zip Slip ;
- taille compressée et décompressée ;
- nombre de fichiers ;
- extensions inattendues ;
- JavaScript embarqué ;
- accès réseau externe ;
- nécessité future d’une quarantaine ;
- politique CSP à prévoir ;
- isolation iframe.

### Licence

- licence du contenu ;
- licence du type H5P et de ses bibliothèques ;
- droit de redistribution ;
- attribution nécessaire ;
- incompatibilité éventuelle avec un usage commercial.

## Classification finale

Chaque type testé reçoit une décision :

- autorisé pour le pilote ;
- autorisé sous conditions ;
- reporté ;
- refusé.

## Acceptation

- [ ] Tableau d’analyse rempli.
- [ ] Risques de sécurité documentés.
- [ ] Provenance et licence confirmées ou marquées incertaines.
- [ ] Décision explicite par type.
- [ ] Aucun type non testé présenté comme compatible.
