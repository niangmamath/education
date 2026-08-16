# Diagnostic et remédiation

Nommer une difficulté, dire ce qu'elle peut avoir de commun avec une autre,
proposer par quoi commencer. Les progrès de l'étape 11 sont dans `progres.md`,
les tentatives et leur lecture dans `tentatives-resultats.md`, la décision dans
ADR-015.

## Trois couches, et aucune ne rejuge celle du dessous

```
tentatives et résultats (étape 10)   les faits, et une lecture par tentative
        ▼
progrès (étape 11)                   les lectures sommées, sans rien conclure
        ▼
diagnostic (étape 12)                une lacune proposée, une hypothèse, un score
```

Chaque couche lit la précédente et ne la recalcule pas. Une lacune proposée ici
se remonte toujours jusqu'à une tentative, une règle et des comptes. Recalculer
à ce niveau laisserait les mêmes preuves dire deux choses différentes selon le
chemin emprunté pour y arriver.

## Rien n'est stocké

Comme les progrès, le diagnostic se calcule à chaque lecture. Un diagnostic
stocké serait une quatrième chose capable de contredire les trois dont il vient,
et une lacune périmée est pire qu'une lacune absente.

C'est aussi ce qui rend vraie **par construction** la règle « une cause racine
reste une hypothèse jusqu'à la réévaluation » : l'hypothèse est recalculée à
chaque lecture, donc une réévaluation la change à l'instant où elle arrive.
Aucune tâche de fond, aucun rafraîchissement à déclencher, rien à invalider.

## Ce qu'est une lacune, et ce qui n'en est pas une

| Règle | Condition | Produit |
|---|---|---|
| `gap-not-mastered` | la dernière lecture terminée conclut « non acquise » | lacune localisée |
| `gap-partial-persists` | « en cours d'acquisition » après au moins 2 tentatives terminées | lacune localisée |

**Une seule lecture intermédiaire n'est pas une difficulté.** C'est ce à quoi
ressemble un apprentissage en chemin. Elle le devient si elle ne se règle pas
d'une tentative à l'autre : l'enfant est revenue sur la compétence et cela n'a
pas bougé.

**Une compétence que personne n'a travaillée n'est pas une lacune.** Elle n'a
aucune lecture, donc rien à lire ; la ranger sous « difficulté » ferait d'une
absence une accusation. C'est la même règle qu'à l'étape 10, où l'absence de
preuve n'écrit aucun résultat.

Une lacune est une **candidate**. Elle porte la règle qui l'a proposée, les
comptes lus et une phrase en français. Une conclusion que personne ne peut
remonter est un verdict, pas une candidate.

## Une lacune générale regroupe sans supprimer

`general-gap-same-domain` : au moins deux lacunes localisées portant sur le même
domaine du référentiel sont **aussi** lues ensemble.

Les compétences nommées dans une lacune générale restent listées une par une
dans les lacunes localisées. Les deux listes voyagent côte à côte, parce que la
règle produit dit que le regroupement ne supprime pas ce qu'il regroupe. Une
lacune seule dans un domaine n'est pas un motif : l'appeler ainsi en inventerait
un.

## Une cause racine reste une hypothèse

`root-cause-prerequisite` : quand une compétence en lacune est **prérequis**
d'une autre compétence en lacune, dans l'édition en vigueur, elle est proposée
comme cause racine possible.

Seules les arêtes entre deux lacunes comptent. Un prérequis acquis n'explique
rien — c'est une preuve *contre* l'hypothèse — et un prérequis jamais travaillé
n'est aucune preuve du tout.

Le champ `confirmed` vaut toujours `false`, et c'est un champ plutôt qu'un
sous-entendu : un client ne doit pas pouvoir afficher l'hypothèse comme une cause
établie par simple omission.

## L'arbre sert au regroupement, pas aux lacunes

Une lacune localisée n'a besoin que d'un code de compétence, que les résultats
portent. Le regroupement et les causes racines ont besoin de l'édition en
vigueur.

Sans édition publiée, les lacunes sont quand même rendues, et `tree_available`
vaut `false`. Une réponse courte ne doit pas se lire comme « aucune difficulté ».

## Le score de santé académique

`health-weighted-outcomes` : moyenne pondérée des compétences **observées**, une
acquise comptant 1, une en cours 0,5, une non acquise 0, **chacune pesant son
nombre de tentatives terminées**, rendue sur 100.

Une compétence reprise dix fois pèse dix fois une compétence vue une seule. Le
coût est écrit plutôt que caché : ce qui a été le plus refait porte le plus de
poids, et ce n'est pas toujours ce qui compte le plus.

- **Explicable** : chaque terme voyage à côté du score, y compris le total des
  tentatives — une moyenne pondérée dont le dénominateur est caché ne peut pas
  être vérifiée par qui on la montre.
- **Non comparatif** : calculé sur ce que cette enfant a travaillé, et sur rien
  d'autre. Ni sur le programme, ce qui se lirait « quel retard », ni contre
  d'autres enfants, ce que la plateforme ne calcule jamais.
- **Ce n'est pas une note sur une compétence.** Il apparaît une fois, pour un
  enfant, à côté de la lecture complète par compétence qu'il résume — jamais à la
  place de l'une d'elles. C'est ce qui permet de tenir ensemble « une note ne
  remplace jamais une compétence » et la vue unique que le produit demande.

**Rien d'observé ne rend aucun score.** Il n'y a délibérément pas de zéro pour
cela : zéro dirait que le travail s'est mal passé, alors qu'il n'a pas eu lieu.

## Quick Repairs

Une activité **publiée**, travaillant la compétence, et durant **de 3 à 7
minutes**. Hors de cette bande, elle n'est pas proposée, si bien assortie
soit-elle : proposer vingt minutes comme réparation rapide rendrait la promesse
fausse.

Une seule activité par compétence. Un enfant qui regarde ce qu'elle peut faire a
besoin de quelque chose à faire, pas d'un catalogue ; et en proposer trois
laisserait croire que la plateforme sait laquelle est la meilleure, ce qui est
faux.

**Une compétence dont le prérequis est en lacune n'est pas proposée du tout.**
`defer-behind-prerequisite`. Demander d'assurer les opérations quand le vrai
problème est le comptage, ou de conjuguer quand les groupes de verbes ne sont pas
reconnus, c'est faire travailler l'enfant sur ce qui bute plutôt que sur ce qui
bloque, et cela ne règle ni l'un ni l'autre.

La lacune dépendante **reste affichée**, avec `blocked_by` et la phrase qui dit
sur quoi elle attend. Reporter ce qu'on fait travailler n'est pas cacher ce qu'on
a trouvé, et un parent qui voit une difficulté sans remédiation à côté doit
savoir que le silence est délibéré.

Les chaînes se règlent d'elles-mêmes : dans A ⟵ B ⟵ C toutes en lacune, seule A
est travaillée.

Choix de l'activité :

1. jamais proposée à cet enfant ;
2. sinon, déjà terminée — proposée quand même, et **signalée** par
   `already_done` : la refaire est une seconde passe, et le parent doit le
   savoir ;
3. jamais celle qui l'attend déjà, assignée ou en cours.

**Toute remédiation possède une preuve finale**, et chaque recommandation la
nomme : la lecture de la tentative, par les règles de l'étape 10. Recommander
quelque chose qui ne conclut rien laisserait la lacune exactement où elle était.

Rien ici ne marque quoi que ce soit comme réparé. **Une ouverture de contenu ne
valide jamais seule une compétence.**

## Ce que chaque côté voit

| Route | Qui | Ce qu'elle rend |
|---|---|---|
| `GET /api/v1/children/{child_id}/diagnostic` | Parent | Lacunes, regroupements, hypothèses, score, recommandations |
| `POST /api/v1/children/{child_id}/remediation` | Parent | Donne les activités proposées |
| `GET /api/v1/me/next-steps` | Élève | Trois activités courtes, et rien d'autre |
| `GET /api/v1/diagnostic/rules` | Toute session | Les six règles, condition et raison |

Le même moteur produit les deux, et la différence est **ce qui traverse**. Une
enfant voit une activité et sa durée. Elle ne voit ni le score, ni les lacunes,
ni la règle qui a nommé une difficulté.

Ce n'est pas du secret sur son propre travail : ses tentatives, ses résultats et
ses progrès restent à sa disposition, et chacun s'explique. C'est qu'une liste de
réparations remise à une enfant **comme un diagnostic** est un jugement auquel
elle n'a aucun moyen de répondre, et que le produit place un adulte dans la
boucle précisément pour qu'elle n'ait pas à le faire.

Les règles sont lisibles par toute session authentifiée, comme celles de
l'étape 10 : les publier derrière une porte qu'un seul côté ouvre reviendrait à
ne les publier à personne.

## La plateforme propose, le parent donne

**Rien n'est jamais affecté par la plateforme elle-même.** Ni à la lecture d'un
diagnostic — un `GET` ne crée rien —, ni à la clôture d'une tentative, qui serait
pourtant le moment naturel puisque c'est là que la lecture change.

Ce qui existe est une route qui **retire la ressaisie, pas la décision** :

`POST /api/v1/children/{id}/remediation` donne les activités proposées, sur la
parole du parent. Être d'accord avec les propositions ne doit pas obliger à les
recopier une à une dans le formulaire d'affectation. Ce qui est déjà en attente,
ou ce qui passerait le plafond d'activités en cours, est **écarté et nommé**
plutôt que forcé.

La distinction vaut d'être gardée : retirer une ressaisie est de l'ergonomie,
choisir ce qu'un enfant fera est une décision. La plateforme fait la première et
laisse la seconde.

Un mode automatique a existé brièvement, réglable par enfant ; il a été retiré à
la demande du propriétaire, colonnes comprises, par la migration `0012`. S'il
revient, son réglage appartiendra au **parent**, avec une valeur par enfant.
Voir ADR-015.

## Ce que l'étape 12 ne fait pas

- **Aucun diagnostic médical, psychologique ou comportemental.** Ce qui est
  nommé est une compétence lue à partir de réponses, rien d'autre.
- **Aucune assignation par la plateforme.** Elle propose, le parent donne.
- **Aucune notification** : c'est l'étape 14.
- **Aucun classement, aucune cohorte, aucun percentile.** Le score ne compare à
  personne, et il n'existe aucune route qui compare deux enfants.
- **Aucune IA générative de diagnostic**, hors périmètre du projet par décision.
- **Aucun tableau de bord** : l'affichage est l'étape 13.
