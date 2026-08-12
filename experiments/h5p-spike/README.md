# Spike H5P critique

## Objectif

Vérifier qu’un paquet H5P autorisé peut être extrait de manière sûre, lu avec H5P Standalone et produire un événement xAPI exploitable dans StudentConnect.

## Statut

Préparation en cours. Aucun type H5P ni paquet de contenu n’est encore validé pour le MVP.

## Règles

- Les paquets `.h5p` restent hors de Git.
- Aucun paquet n’est utilisé sans provenance et licence documentées.
- Chaque paquet reçoit une empreinte SHA-256.
- Les dossiers extraits et les preuves runtime restent hors de Git.
- Les statements xAPI anonymisés peuvent être conservés comme preuves.
- Aucun résultat simulé ne peut valider le spike.
- La licence d’une bibliothèque H5P ne prouve pas la licence du contenu d’un paquet `.h5p`.

## Structure

```text
experiments/h5p-spike/
├── README.md
├── package-register.md
├── candidate-review.md
├── packages/
├── extracted/
├── evidence/
│   ├── runtime/
│   └── xapi/
└── scripts/
```

## Étape courante

Sélectionner un paquet pilote légalement réutilisable, puis consigner son URL exacte, sa licence, sa taille, son SHA-256 et le résultat de la validation ZIP.
