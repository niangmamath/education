# Fiches de remédiation

Le dernier maillon de la chaîne, qui manquait.

Le diagnostic savait nommer une lacune, remonter au prérequis qui la cause et
proposer une réparation courte. Mais **les douze premières remédiations étaient
des lignes de catalogue sans rien derrière** : un parent pouvait donner une
activité qui s'ouvrait sur une page vide. Le parcours avait l'air complet et ne
l'était pas.

## Ce qu'est une fiche

Trois à sept minutes, une compétence, et deux temps :

1. **Ce qu'il faut retenir** — la leçon, adressée à l'enfant. Elle est visible
   avant les questions et le reste pendant qu'on y répond.
2. **Quatre questions**, chacune suivie d'une explication, tirées d'une réserve
   de huit (HORS-10, ADR-020) — voir plus bas.

Quinze fiches aujourd'hui : les douze premières (français et mathématiques, du
CI au CE1), et trois de plus pour l'anglais du CI (ADR-019). Trente-neuf
compétences sur cinquante-quatre restent sans réparation ; un test épingle
cette couverture dans les deux sens.

## Pourquoi elles ne sont pas en H5P

C'est ADR-017, et c'est une décision plutôt qu'un raccourci. Quatre raisons, dont
trois sont des murs :

- **le rattachement question-compétence n'existe nulle part ailleurs.** Une
  réparation doit une preuve, et une preuve qu'on ne peut pas rattacher à la
  compétence qu'elle répare ne prouve rien ;
- **ADR-012 n'autorise qu'une bibliothèque**, tenue par une contrainte de
  vérification en base ;
- **l'origine de contenu n'est pas déployable sur Render**, où un disque
  appartient à un seul service ;
- **une réparation doit enseigner**, et une question importée ne fait
  qu'interroger.

## La leçon vient avant, l'explication vient après

C'est ce qui sépare une réparation d'un second contrôle. Une enfant à qui l'on
vient d'annoncer une difficulté n'a aucune raison de repasser un test ; elle a
besoin qu'on lui explique.

**L'explication ne change pas avec la réponse donnée.** La même phrase est
affichée qu'on ait vu juste ou non, parce qu'une fiche explique ce qui est vrai —
elle ne commente pas l'enfant. Un test le vérifie, et refuse « bravo », «
dommage », « raté ».

**Rien n'est rouge.** Une réponse fausse ici n'est ni une panne ni une faute :
c'est l'endroit exact où la fiche sert à quelque chose, et elle est marquée en
ocre comme tout ce qui se travaille.

## Ce qui est partagé avec l'examen, et ce qui ne l'est pas

**Partagé** : la correction. `app.authored.service` lit les questions et corrige
les réponses sans jamais savoir laquelle des deux natures l'a appelé. La table
s'appelle `authored_questions` — et non plus `assessment_questions` — parce
qu'elle sert les deux : deux tables aux quatre mêmes colonnes auraient divergé.

Le rattachement, lui, reste dans `catalog_activity_questions`, où il était déjà.
Le moteur qui lit un résultat continue de lire **une** table, que l'activité ait
été importée ou écrite ici, et n'apprend jamais la différence.

**Pas partagé** : ce que chacun répond. Une fiche renvoie l'explication ; l'examen
ne renvoie rien. Un examen qui répond cesse de mesurer.

## La porte qu'il a fallu fermer

Cette asymétrie a créé une faille, et elle mérite d'être écrite.

Si la route des fiches acceptait n'importe quelle tentative, une enfant pouvait y
poster ses réponses d'**examen** et se faire dire, une question à la fois, si
chacune était juste. L'examen d'initiation — celui qui décide de tout ce qui
suit — serait devenu franchissable par la porte ouverte pour l'aider.

La route vérifie donc la nature de l'activité derrière la tentative, plutôt que
de faire confiance aux clients pour appeler la bonne adresse.
`test_an_assessment_attempt_is_refused_here` est le verrou.

## Une réserve de huit, quatre servies

Une fiche reprise montrait les quatre mêmes questions dans le même ordre à
chaque tentative — une invitation à mémoriser la réponse plutôt qu'à retravailler
la compétence. Chaque fiche porte désormais une réserve de huit questions ;
`app.authored.service.questions_of` en tire quatre à chaque lecture, avec
`random.Random(seed)` où `seed` est l'identifiant de la tentative en cours.

Tant que la tentative reste ouverte, le tirage ne change pas : recharger la
page ne doit pas faire bouger les questions sous les yeux d'une enfant qui y
répond déjà. Une nouvelle tentative — la fiche reprise depuis le début — porte
un nouvel identifiant et tire donc à nouveau. Aucune migration : l'identifiant
de tentative existe déjà et suffit de graine.

**L'examen n'est pas concerné.** `questions_of` accepte le tirage en paramètre
optionnel plutôt que de le décider elle-même — la politique reste à
l'appelant, comme tout ce qui distingue déjà une fiche de l'examen. La route
de l'examen ne passe jamais ce paramètre et continue de recevoir sa réserve
entière. ADR-020 consigne la décision.

## Les routes

| Route | Ce qu'elle fait |
|---|---|
| `GET /me/activities/{assignment_id}/fiche` | La leçon et quatre questions tirées de la réserve, sans réponse ni explication |
| `POST /me/fiches/attempts/{attempt_id}/answers` | Une réponse, et ce que la fiche dit en retour |

Ouvrir la tentative et la terminer passent par les routes de tentative qui
existaient déjà : une fiche est une activité, et la plateforme n'a pas à
apprendre une seconde façon de faire une activité parce que celle-ci a été écrite
ici.

## Ce que les fiches ne savent pas faire

- **Entendre.** Les questions de phonologie parlent de mots écrits, comme celles
  de l'examen. C'est un pis-aller assumé, et l'audio reste la première chose à
  ajouter si tout ceci sert en vrai.
- **Dessiner.** Le dénombrement se fait sur des rangées de symboles
  typographiques : cela fonctionne jusqu'à une dizaine et pas au-delà.
- **Se réévaluer toutes seules.** Une fiche produit des lectures comme n'importe
  quelle activité ; c'est le diagnostic qui décide ensuite si la lacune est
  résorbée, et rien ici ne l'anticipe.
