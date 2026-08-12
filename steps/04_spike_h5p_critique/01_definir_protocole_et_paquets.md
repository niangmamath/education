# 04.1, définir le protocole et les paquets pilotes

## Objectif

Définir les preuves attendues avant d’intégrer une bibliothèque ou un paquet H5P.

## Travail

1. Créer une branche :

```bash
git switch -c spike/h5p-critical
```

2. Créer un espace expérimental isolé :

```text
experiments/h5p-spike/
├── README.md
├── packages/
├── extracted/
├── evidence/
└── scripts/
```

3. Ajouter dans `.gitignore` :

```gitignore
experiments/h5p-spike/packages/*.h5p
experiments/h5p-spike/extracted/
experiments/h5p-spike/evidence/runtime/
```

4. Pour chaque paquet candidat, documenter :

- nom du type H5P ;
- version de la bibliothèque principale ;
- URL de provenance ;
- auteur ou fournisseur déclaré ;
- licence du contenu ;
- licence des bibliothèques ;
- date de téléchargement ;
- empreinte SHA-256 ;
- taille ;
- raison du choix.

5. Limiter le premier essai à un paquet simple et interactif. Aucun paquet n’est accepté seulement parce qu’il est techniquement lisible.

## Vérifications

```bash
sha256sum experiments/h5p-spike/packages/*.h5p
file experiments/h5p-spike/packages/*.h5p
unzip -t experiments/h5p-spike/packages/PAQUET.h5p
```

## Intervention possible d’un agent

Un agent peut rechercher des paquets candidats et leurs licences, mais ne doit télécharger, modifier ou commiter aucun paquet. Toute conclusion doit inclure les URLs et les incertitudes.

## Acceptation

- [ ] Protocole écrit.
- [ ] Au moins un paquet candidat identifié.
- [ ] Provenance vérifiable.
- [ ] Licence documentée.
- [ ] SHA-256 enregistré.
- [ ] Archive ZIP valide.
