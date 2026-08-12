# Registre des paquets H5P pilotes

Aucun paquet `.h5p` n’est encore accepté ou téléchargé.

## Informations obligatoires par paquet

- Identifiant interne
- Nom du fichier
- Type H5P principal
- Version principale déclarée dans le paquet
- URL exacte de téléchargement
- Page de provenance
- Auteur ou fournisseur déclaré
- Licence du contenu du paquet
- Licence des bibliothèques incluses
- Droit de redistribution du paquet complet
- Attribution requise
- Date de téléchargement
- Taille en octets
- SHA-256
- Résultat de `file`
- Résultat de `unzip -t`
- Liste des bibliothèques incluses
- Décision provisoire
- Incertitudes

## Candidats de type

| Priorité | Type | Version de bibliothèque observée | État |
|---|---|---:|---|
| 1 | True/False Question (`H5P.TrueFalse`) | 1.8.24 | Type présélectionné, paquet exact à trouver et licencier |
| 2 | Multiple Choice (`H5P.MultiChoice`) | 1.16.27 | Type de comparaison, paquet exact à trouver et licencier |
| 3 | Fill in the Blanks (`H5P.Blanks`) | 1.14.37 | Reporté après les deux types plus simples |

## Premier paquet pilote

- Identifiant interne : `truefalse-oslo-001`
- Nom du fichier : `true-false-question-34806.h5p`
- Type : `H5P.TrueFalse`
- Version : `1.8`
- Page de provenance : `https://h5p.org/true-false`
- Auteur de l’image : Rafał Konieczny
- Licence de l’image : Public Domain
- Source de l’image : `https://en.wikipedia.org/wiki/Oslo_Opera_House#/media/File:Full_Opera_by_night.jpg`
- Taille : `1056130` octets
- SHA-256 : `9914c27552f00aa91d4a29e85f6a299b11f984030c3451658fb0246f84b07f3c`
- Résultat ZIP : valide
- Licence globale du manifest : `U` (non divulguée)
- Décision : accepté uniquement pour le spike local, paquet hors Git
- Incertitude : redistribution du paquet complet non validée