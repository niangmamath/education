# ADR-022, Le cours est donné automatiquement, jamais une porte

- Statut : Accepté
- Date : 26 août 2026

## Contexte

L'étape 14 (ADR-021) a remplacé un examen d'entrée testant toute une classe
d'un coup par une évaluation par paliers, gagnés un à un. Ce que cette étape
ne changeait pas restait entier : **rien sur la plateforme n'enseigne**.
L'examen teste un palier à froid dès que le précédent est maîtrisé ; les
fiches de remédiation (ADR-017) réparent une lacune déjà constatée, sur
l'hypothèse qu'un enfant a appris ailleurs, hors plateforme. Le propriétaire a
annoncé le 25 août 2026, aussitôt après la correction du modèle
d'évaluation, que l'étape suivante était de construire le cours proprement
dit — la brique qui enseigne avant de tester, et non après avoir échoué.

Deux décisions structurantes ont été soumises et tranchées par le
propriétaire le 26 août 2026, avant toute construction, même démarche qu'à
l'ouverture des étapes 07, 08 et 14.

## Décision

### Un cours est donné automatiquement, et n'est jamais une porte

Comme l'examen (ADR-014, étendue par ADR-021), le cours est donné par la
plateforme elle-même — extension d'un cran de la même exception plutôt
qu'une nouvelle créée — dès que `app.assessment.tiers.next_sitting` déclare
une compétence due. Mais ce n'est **pas** un préalable obligatoire : l'examen
du palier reste accessible sans être passé par le cours qui le précède. Un
enfant confiante dans la matière peut aller directement à l'examen.

`app.assessment.service.give_to` calcule `due` une seule fois et le partage
avec `app.course.service.give_to`, plutôt que de recalculer le graphe de
prérequis une seconde fois. Un code de `due` déjà testé — réussi ou échoué —
sort de `next_sitting` par construction : le cours ne réapparaît donc jamais
après le premier examen de cette compétence, sans logique supplémentaire à
écrire. La remédiation réactive (`quick_repairs`, inchangée) reste la seule
réponse à un échec.

### Une leçon native avec vérification à la volée, sans conséquence sur la maîtrise

Un cours est une activité authorée ici, comme une fiche (ADR-017, pour les
mêmes raisons : rattachement par code de compétence, indépendance vis-à-vis
du déploiement de l'origine de contenu isolée, et une leçon qui explique
avant d'interroger). `ACTIVITY_KIND_COURSE` rejoint `assessment` et
`remediation` dans `AUTHORED_KINDS`, partageant `Activity.guidance` pour la
leçon et `authored_questions` pour ses questions de vérification.

La différence décisive est que **répondre à une question d'un cours ne
produit aucune lecture de compétence**. Une fiche complétée produit une
lecture par les règles de l'étape 10 (ADR-021) ; un cours, non. La route de
vérification (`app/api/v1/cours.py`) n'écrit jamais dans `attempts` ni
`attempt_responses` — elle appelle `app.authored.service.grade` directement
contre l'affectation, sans qu'aucune tentative n'existe. La maîtrise reste
décidée uniquement par l'examen du palier, inchangé. L'achèvement du cours
lui-même passe par la route générique d'affectation déjà construite en 09.3
(« terminer n'est pas réussir »), qui ne touche pas davantage à une
compétence.

### Ce qui a été corrigé en chemin

`app.diagnostic.remediation.quick_repairs` sélectionnait une réparation par
sa seule durée (3 à 7 minutes), sans filtrer sur le type d'activité — ce qui
suffisait tant qu'aucun autre type authoré court n'existait. Une première
correction, trop large, restreignait la sélection au seul type
`remediation` : elle cassait la sélection de réparations réelles en H5P ou
PhET, que la suite de tests éprouve explicitement et que
`quick_repairs` a toujours eu vocation à proposer, quel que soit leur média.
La sélection exclut désormais seulement `assessment` (jamais une réparation
par nature) et `course` (déjà donné automatiquement, ne doit pas se
reproposer comme réparation) — `Activity.kind.not_in(_NOT_A_REPAIR)` —
laissant tout le reste, y compris les fiches, passer comme avant.

`app.authored.service.grade` prenait une `Attempt` en paramètre alors qu'elle
n'utilisait jamais que `attempt.assignment_id`. Elle prend maintenant un
`assignment_id` directement — un cours n'a pas de tentative à lui passer, et
les trois appelants existants (fiches, examen, script de démonstration) ne
changent pas de comportement. `open_sheet_for` est renommée
`open_authored_activity_for`, puisqu'elle sert désormais deux natures et non
une seule.

## Conséquences

Un enfant qui vient de franchir un palier reçoit, à la même lecture, le
cours et l'examen du palier suivant. Elle peut faire l'un, l'autre, les
deux, ou passer l'examen directement. Rien n'oblige à ouvrir le cours pour
progresser ; rien n'empêche de le faire.

Deux cours pilotes seulement sont écrits pour l'instant
(`ci-fr-lettres`, `ci-ma-denombrer`, `app/demo/cours.py`), sur des
compétences déjà couvertes par une fiche — la boucle complète (cours, examen,
en cas d'échec la fiche déjà existante, retest) est donc démontrable de bout
en bout sans attendre la couverture des cinquante-quatre compétences.
Couvrir le reste du référentiel est une dette assumée, à traiter hors étape
comme HORS-04 puis HORS-09 l'ont fait pour les fiches.

## Alternatives écartées

**Le cours comme porte obligatoire avant l'examen.** Aurait garanti que
l'enseignement a bien eu lieu avant chaque mesure, au prix de forcer un
enfant qui maîtrise déjà la matière à traverser une leçon inutile avant de
pouvoir être testée. Écartée par le propriétaire : l'examen reste accessible
directement.

**Faire transiter la vérification du cours par une tentative**, en
réutilisant telle quelle la mécanique des fiches. Aurait évité d'étendre
`grade`, mais aurait produit une lecture de compétence pour chaque question
de vérification — exactement ce que la décision « sans conséquence sur la
maîtrise » interdit, la table `attempt_results` n'ayant aucun moyen
d'exprimer « cette lecture ne compte pas ».
