# ADR-013, le catalogue est lié au référentiel par code métier

## Statut

✅ **Accepted** — Décision validée et implémentée le 15 août 2026, étape 08.1.

## Contexte

Le référentiel scolaire est versionné dans son ensemble depuis ADR-004 amendée :
une **édition** porte ses propres niveaux, matières, domaines et compétences, et
publier une nouvelle édition crée de nouvelles lignes plutôt que d'éditer celles
que des traces désignent déjà. Chaque compétence porte donc deux identifiants,
un `id` UUID refrappé à chaque import, et un `code` métier stable d'une édition
à l'autre.

Le catalogue d'activités de l'étape 08 doit dire quelles compétences chaque
activité travaille. La question est de savoir **à quoi** ce lien pointe.

## Options évaluées

1. **Clé étrangère composite vers `ref_competencies (id, version_id)`.**
   Intégrité référentielle complète : la base refuse un lien vers une compétence
   inexistante, et le lien ne peut pas traverser une édition. Mais chaque
   publication d'une nouvelle édition rend caduc l'intégralité du catalogue, qui
   doit être remappé ligne à ligne avant que la nouvelle édition ne serve.

2. **Lien par code métier**, stocké comme chaîne, résolu à la lecture contre
   l'édition en vigueur. Le catalogue suit le programme sans être reconstruit.
   En contrepartie, aucune clé étrangère ne protège d'un code qui ne désigne
   rien.

3. **Les deux** : clé étrangère vers une édition de référence, plus le code pour
   permettre le remappage. Cumule l'intégrité et la survie, au prix de deux
   sources de vérité qui peuvent se contredire, et d'un doute permanent sur
   laquelle fait foi.

## Décision

**Option 2, le lien par code métier.**

Un catalogue n'est pas une trace. Une tentative de l'étape 10, un événement xAPI
de la 11 et un diagnostic de la 12 sont des faits enregistrés à une date, et
doivent rester lisibles dans le référentiel où ils ont été écrits : pour eux, la
clé étrangère vers une édition précise est la bonne réponse. Un catalogue est un
travail éditorial : l'exercice qui entraîne l'addition posée entraîne encore
l'addition posée après une révision du programme, et exiger qu'un humain
reconstruise le lien à chaque édition transformerait une propriété souhaitable
en corvée, donc en source d'oubli.

Le code métier est précisément l'identifiant que 07.1 a créé pour survivre aux
éditions. S'en servir ici, c'est l'utiliser pour ce à quoi il sert.

## Conséquences

**Ce que la décision donne.** Le catalogue survit à la publication d'une
nouvelle édition sans intervention. Une activité créée sous l'édition de 2026
travaille toujours `cm1-math-num-01` sous celle de 2027, tant que ce code y
existe.

**Ce qu'elle coûte.** Un code qui ne désigne rien est un lien mort, que la base
ne peut pas refuser. Deux contreparties sont donc dues, et livrées avec 08.1 :

- `python -m app.catalog check` liste les liens qui ne se résolvent pas dans
  l'édition en vigueur, et rend un code de retour non nul s'il en trouve ;
- la vérification est rejouée à l'import du catalogue, avant écriture, sur le
  même modèle que la validation d'import du référentiel.

Un lien mort ne casse pas une lecture : l'activité est simplement absente des
résultats filtrés sur ce code. C'est un silence, ce qui est plus dangereux qu'une
erreur, et c'est pourquoi la commande de vérification existe et doit être passée
après chaque publication d'édition.

**Ce qu'elle n'interdit pas.** Si un besoin apparaît de figer un catalogue avec
une édition — par exemple pour rejouer un parcours ancien à l'identique —
l'option 3 reste ouverte : le code est déjà là, il ne manquerait que la clé.

## Références

- ADR-004, amendée, sur le référentiel versionné.
- `docs/backend/referentiel-competences.md`, sur les deux identifiants.
- `docs/backend/catalogue-activites.md`, sur le catalogue lui-même.
