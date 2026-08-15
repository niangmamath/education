# Tentatives et résultats

## Périmètre

Cette page décrit l'étape 10 : ce qu'un enfant a fait, et ce qu'on en lit.
L'affectation est décrite dans `affectations.md`, le contenu jouable dans
`runtime-contenu.md`. L'ingestion des événements xAPI relève de l'étape 11.

## Les faits d'un côté, la lecture de l'autre

C'est la ligne qui structure toute l'étape, et elle est portée par trois tables
plutôt que par une convention.

| Table | Nature |
|---|---|
| `attempts` | un **fait** : cet enfant a ouvert cette activité, puis s'est arrêté |
| `attempt_responses` | un **fait** : cette réponse a été donnée à cette question |
| `attempt_results` | une **interprétation**, et elle est rangée à part parce qu'elle en est une |

Une règle du projet dit qu'une note ne remplace jamais une compétence, une autre
qu'une lacune automatique est une candidate explicable. Garder les faits et leur
lecture dans des tables distinctes est ce qui rend ces règles applicables plutôt
que simplement énoncées : on peut relire, recalculer, ou contester une
interprétation sans toucher à ce qui a été observé.

## Rien n'écrase rien

Les réponses sont **ajoutées, jamais remplacées**. Un enfant qui répond, change
d'avis et répond à nouveau a fait deux choses, et la seconde n'efface pas la
première — une règle du projet dit qu'une observation nouvelle ne doit jamais
écraser l'historique.

La lecture prend **la dernière réponse par question** ; l'historique les garde
toutes. Les deux affirmations tiennent ensemble parce qu'elles vivent à des
endroits différents.

## Commencer est idempotent

Un enfant qui recharge la page, ou dont le réseau hoquette, ne doit pas se
retrouver avec deux tentatives. Demander à commencer alors qu'une tentative est
en cours rend celle-là.

**C'est la base qui le garantit, pas le code** : un index unique partiel n'admet
qu'une tentative `in_progress` par affectation, donc deux requêtes arrivant
ensemble ne peuvent pas gagner toutes les deux. Le perdant est renseigné sur le
gagnant au lieu d'échouer : des deux côtés on a demandé la même chose, on reçoit
la même réponse.

La route répond `201` quand elle a créé, `200` quand elle a rendu l'existante,
si bien qu'un client peut distinguer les deux sans qu'aucune soit une erreur.

## Les règles de lecture

Trois règles nommées, de l'arithmétique sur des comptes, et rien d'autre.

| Règle | Condition | Conclusion |
|---|---|---|
| `all-correct` | tout est juste | acquise |
| `majority-correct` | au moins la moitié | en cours d'acquisition |
| `too-few-correct` | moins de la moitié | non acquise |

La maîtrise exige **tout**, parce que ce sont des activités courtes sur un point
précis : réussir la plupart d'un exercice de trois questions n'est pas le
maîtriser. La bande intermédiaire existe pour que « presque » ne soit pas rangé
avec « pas du tout », ce qui dirait à un parent quelque chose de faux.

Aucun modèle, opaque ou non. Un parent doit pouvoir s'entendre dire : « elle a
répondu à quatre questions, trois étaient justes, et la règle qui exige tout a
conclu que ce n'est pas encore acquis ». Cette phrase est toute la conception, et
l'API la rend telle quelle dans le champ `explanation`, construite à partir des
mêmes valeurs que celles qui ont été stockées — elle ne peut donc pas diverger de
ce qu'elle explique.

### Aucune preuve ne conclut rien

Un contenu qui ne dit pas si une réponse était juste **n'est pas obligé de le
dire**. Ces réponses ne sont pas comptées, et si aucune n'a été évaluée, **aucun
résultat n'est écrit du tout**.

C'est délibéré et il n'existe pas de statut pour cela : ranger un silence sous
« non acquise » en ferait une accusation, sous « en cours » une affirmation que
quelque chose a été à moitié fait. Rien n'a été observé, donc rien n'est
enregistré, et l'absence de résultat est elle-même la réponse honnête.

### Une limite écrite, non cachée

Les règles s'appliquent à **toutes les compétences de l'activité**, parce que H5P
ne dit pas quelle question relève de quelle compétence. Une activité rattachée à
deux compétences produit donc la même lecture pour les deux. C'est une limite
réelle du pilote ; elle se lèvera le jour où les événements xAPI de l'étape 11
porteront de quoi distinguer les questions.

## Les routes

```text
POST /api/v1/me/activities/{assignment_id}/attempts   commencer ou reprendre
POST /api/v1/me/attempts/{id}/responses               ajouter une réponse
POST /api/v1/me/attempts/{id}/complete                terminer et lire
GET  /api/v1/me/attempts                              ses tentatives
```

Toutes appartiennent à l'espace Élève et exigent `CurrentChild`. Un parent n'a
rien à y faire — non par secret, mais parce qu'une tentative est ce qu'un enfant
fait, et une route qui accepterait les deux serait à un oubli près de laisser un
parent répondre à sa place.

## Ce que l'étape 10 ne fait pas

- Aucune ingestion xAPI : les réponses sont déclarées par le client. L'étape 11
  les recevra du runtime lui-même, ce qui est autre chose.
- Aucun agrégat dans le temps : un résultat porte sur une tentative. L'agrégation
  est 11.3.
- Aucun diagnostic ni recommandation : c'est l'étape 12, et une lecture par
  tentative n'est qu'un des éléments qu'elle prendra.
- Aucune lecture côté Parent au-delà de l'affectation : les tableaux de bord sont
  l'étape 13.
