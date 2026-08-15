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

### À quoi une réponse est attribuée

Cela dépend de ce que l'activité déclare.

**Si elle associe ses questions à des compétences**, chaque question ne compte
que pour ce qu'elle travaille, et une compétence sans question à elle ne reçoit
aucun résultat plutôt qu'un résultat emprunté. C'est la table
`catalog_activity_questions`, remplie par qui enregistre l'activité — personne
d'autre ne le sait, puisqu'un paquet H5P ne le dit pas.

**Si elle ne déclare rien**, ce qui est le cas ordinaire, toutes les compétences
de l'activité reçoivent la même lecture. C'est grossier, et c'est écrit ici
plutôt que caché : la plateforme ne peut pas en dire plus que l'activité.

### D'où vient une réponse

Chaque réponse porte sa provenance. `declared` signifie que le navigateur l'a
dite ; `xapi` signifiera que l'événement du runtime lui-même est parvenu au
serveur.

**Le champ n'est pas dans la charge utile** : un client qui pourrait déclarer
« ceci vient du runtime » annulerait la distinction. Il est posé par le serveur,
et une charge utile qui le mentionne est refusée.

La distinction est la frontière de confiance rendue visible. Rien ne prouve
encore que ce qu'un navigateur rapporte est ce qui s'est passé dans le contenu ;
l'étape 11 apportera les événements du runtime à côté de ces déclarations, et il
faudra alors décider ce qui prime. Enregistrer laquelle est laquelle dès
maintenant est ce qui permettra de trancher sans avoir à deviner pour les lignes
déjà écrites.

`recorded_at` est l'horloge du serveur, jamais celle du client — ADR-012 demande
qu'une date de réception serveur reste distincte de ce qu'une source prétend.

### Pourquoi les seuils ne sont pas configurables

Ils sont **publiés** plutôt que réglables : `GET /api/v1/attempts/rules` rend les
trois règles, leur condition et la raison de chacune.

Les rendre configurables reviendrait à décider qui peut changer ce que « acquise »
veut dire. C'est une décision, pas un réglage, et il n'existe personne pour la
prendre — le rôle Administrateur est l'étape 15. Publier donne la même
transparence sans inventer une autorité.

## Les routes

```text
POST /api/v1/me/activities/{assignment_id}/attempts   commencer ou reprendre
POST /api/v1/me/attempts/{id}/responses               ajouter une réponse
POST /api/v1/me/attempts/{id}/complete                terminer et lire
GET  /api/v1/me/attempts                              ses tentatives
GET  /api/v1/attempts/rules                           les règles, telles qu'appliquées
```

Toutes appartiennent à l'espace Élève et exigent `CurrentChild`. Un parent n'a
rien à y faire — non par secret, mais parce qu'une tentative est ce qu'un enfant
fait, et une route qui accepterait les deux serait à un oubli près de laisser un
parent répondre à sa place.

## Ce que l'étape 10 ne fait pas

- Aucune ingestion xAPI : les réponses restent déclarées par le client, ce que
  leur provenance dit désormais explicitement. L'étape 11 recevra celles du
  runtime.
- Aucun agrégat dans le temps : un résultat porte sur une tentative. L'agrégation
  est 11.3.
- Aucun diagnostic ni recommandation : c'est l'étape 12, et une lecture par
  tentative n'est qu'un des éléments qu'elle prendra.
- Aucune lecture côté Parent au-delà de l'affectation : les tableaux de bord sont
  l'étape 13.
