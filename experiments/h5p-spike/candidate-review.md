# Revue de la recherche des candidats H5P

## Conclusion

La recherche constitue une bonne présélection de **types de bibliothèques**, mais ne suffit pas encore à sélectionner un **paquet de contenu `.h5p`**. La licence MIT des dépôts couvre le logiciel de la bibliothèque. La licence du contenu, des médias et du paquet téléchargeable doit être vérifiée séparément sur la source exacte.

## 1. True/False Question

- Machine name : `H5P.TrueFalse`
- Version observée dans le dépôt officiel : `1.8.24`
- Bibliothèque : MIT
- Dépôt : `https://github.com/h5p/h5p-true-false`
- Page du type : `https://h5p.org/true-false`
- Priorité du spike : 1
- Raisons : interaction minimale, score simple, surface de débogage limitée.
- Point non vérifié : licence et URL du paquet de contenu exact à utiliser.

## 2. Multiple Choice

- Machine name : `H5P.MultiChoice`
- Version observée dans le dépôt officiel : `1.16.27`
- Bibliothèque : MIT
- Dépôt : `https://github.com/h5p/h5p-multi-choice`
- Page du type : `https://h5p.org/multichoice`
- Priorité du spike : 2
- Raisons : interaction plus riche et utile pour comparer les statements xAPI.
- Risques : plusieurs bonnes réponses et scoring plus complexes.
- Point non vérifié : licence et URL du paquet de contenu exact à utiliser.

## 3. Fill in the Blanks

- Machine name : `H5P.Blanks`
- Version observée dans le dépôt officiel : `1.14.37`
- Bibliothèque : MIT
- Dépôt : `https://github.com/h5p/h5p-blanks`
- Page du type : `https://h5p.org/fill-in-the-blanks`
- Priorité du spike : 3
- Raisons du report : saisie textuelle, variantes de réponses, casse, ponctuation et apostrophes augmentent la surface de test.
- Point non vérifié : licence et URL du paquet de contenu exact à utiliser.

## Décision provisoire

Commencer par **True/False Question**. Utiliser Multiple Choice comme deuxième preuve seulement après réussite du premier rendu et de la première capture xAPI. Ne pas télécharger un paquet tant que la page exacte ne confirme pas le droit de réutilisation et de redistribution du contenu.
