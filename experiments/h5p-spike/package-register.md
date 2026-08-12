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

Non sélectionné. Ne renseigner cette section qu’après vérification de l’URL exacte du fichier `.h5p` et de sa licence de contenu.
