# ADR-019, Une troisième matière et trois questions par compétence à l'examen d'entrée

- Statut : Accepté
- Date : 24 août 2026

## Contexte

Le propriétaire a demandé deux choses en même temps, et elles se répondent :
ajouter l'anglais comme troisième matière, et cesser de mesurer une compétence
avec une seule question à l'examen d'entrée — trois sont nécessaires.

**Une seule question ne peut rendre qu'un verdict binaire.** Avec un item par
compétence, `app.attempts.rules.read_counts` calcule un ratio qui ne peut valoir
que 0 ou 1 : la bande `partial` (entre le seuil de maîtrise et zéro) était
inatteignable en pratique, alors que le code la prévoyait déjà. Un enfant qui
connaît une notion à moitié recevait donc le même verdict qu'un enfant qui ne la
connaît pas du tout.

**L'anglais n'était pas prévu, mais rien ne l'empêchait.** Le référentiel
modélise déjà la matière comme une vraie table (`Subject`), pas comme un enum ou
un préfixe codé en dur : `fr` et `ma` sont des lignes de données, pas des cas
particuliers du schéma. Ajouter `an` ne demande donc aucune migration, seulement
du contenu.

## Décision

### Anglais, troisième matière, arbre de prérequis indépendant

Sujet `an`, deux domaines — `an-oral` (écouter et parler) et `an-ecrit` (lire et
écrire) — et dix-huit compétences, trois par classe du CI au CM2, cumulatives
comme le reste du référentiel. Le CI reste oral seulement, comme pour le
français : saluer, nommer des couleurs, compter jusqu'à cinq. Le CM2 attend la
compréhension d'un texte court et la rédaction de phrases simples sur soi-même.

Les prérequis de l'anglais ne traversent **pas** les matières. Rien n'oblige un
enfant à lire en français avant de saluer en anglais : les deux apprentissages
sont concurrents, pas l'un préalable à l'autre. C'est le même principe que pour
le français et les mathématiques, qui n'ont jamais eu de prérequis croisés entre
eux non plus.

Le référentiel compte désormais neuf compétences par classe et cinquante-quatre
au total, trois par matière.

### Trois questions par compétence, et non une

L'examen d'entrée passe de six questions par classe à vingt-sept : neuf
compétences, trois questions chacune. Ni le modèle de données, ni le moteur de
résultats n'ont dû changer : `authored_questions` et
`catalog_activity_questions` acceptaient déjà plusieurs lignes par compétence,
et `_compute_results()` (`app/attempts/service.py`) regroupait déjà toutes les
réponses jugées sur un même code avant d'appeler `read_counts`. La seule
addition a été le contenu — cent soixante-deux questions au total sur les six
classes — et une référence dérivée du code de compétence (`{compétence}-q{n}`),
qui ne peut pas entrer en collision puisque le code l'est déjà.

## Conséquences

**Quarante-deux compétences sur cinquante-quatre n'ont pas de fiche de
remédiation**, dix-huit de plus qu'avant : les dix-huit d'anglais s'ajoutent aux
vingt-quatre de français et de mathématiques déjà en dette. Le test qui épingle
cette couverture dans les deux sens (`tests/test_fiche_items.py`) a été relevé
en conséquence — il continuera d'échouer tant que la dette ne baisse pas
visiblement.

**Un enfant qui échoue une compétence d'anglais n'a aucun prérequis vers lequel
descendre en dehors de sa propre matière.** `unobserved-prerequisite`
(ADR-018) fonctionne identiquement sur l'arbre anglais, mais cet arbre est plus
court : trois classes au maximum séparent une compétence de CM2 de son
antécédent le plus ancien, contre cinq en français ou en mathématiques.

**Le temps de passation de l'examen a plus que doublé.** Neuf minutes de plus en
moyenne par classe, dans une fourchette de 20 (CI) à 32 (CM2) minutes. Rien
n'indique qu'un enfant de six ans tienne vingt minutes d'affilée sans
interruption ; c'est une hypothèse non vérifiée, la même que celle déjà admise
pour l'examen initial.

## Alternatives écartées

**Garder une seule question par compétence et vivre sans bande « partielle ».**
C'était l'état antérieur. Le propriétaire l'a explicitement jugé insuffisant :
une compétence à moitié maîtrisée ne doit pas recevoir le même verdict qu'une
compétence ignorée.

**Faire dépendre l'anglais du français ou des mathématiques.** Le sens commun
pédagogique ne l'impose pas — les trois matières s'apprennent en parallèle dans
le programme réel — et cela aurait ajouté une dépendance croisée que rien ne
justifie, contrairement aux prérequis qui traversent déjà les classes à
l'intérieur d'une même matière.
