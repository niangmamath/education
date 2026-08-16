# ADR-015, Diagnostic explicable, hypothèses non stockées, et ce que chaque côté voit

- Statut : Accepté
- Date : 16 août 2026, amendée le 16 août 2026 par le propriétaire

## Contexte

L'étape 11 a livré des progrès **descriptifs** : le dernier mot par compétence,
les comptes derrière lui, et rien de plus. Nommer une difficulté et proposer une
suite en avaient été délibérément écartés, pour que deux endroits ne décident pas
de ce qu'est une difficulté.

L'étape 12 doit donc trancher quatre questions, et les règles produit non
négociables du projet en contraignent chacune :

1. **À partir de quand la plateforme dit-elle qu'il y a une difficulté ?**
   « Une lacune automatique est une candidate explicable. »
2. **Que fait-on de plusieurs lacunes à la fois ?** « Une lacune générale
   regroupe des lacunes localisées sans les supprimer », et « une cause racine
   reste une hypothèse jusqu'à la réévaluation. »
3. **Comment un score peut-il coexister avec « une note ne remplace jamais une
   compétence » ?** Le produit demande pourtant un « score de santé académique
   explicable », et la règle ajoute « et non comparatif ».
4. **Qu'est-ce qu'on montre à l'enfant ?** La fiche 12.3 demande « les
   diagnostics autorisés au Parent et les prochaines actions à l'Élève ».

## Décision

### Les seuils sont publiés, et le silence ne conclut rien

Deux règles nommées produisent une lacune localisée : `gap-not-mastered` quand
la dernière lecture terminée conclut « non acquise », et
`gap-partial-persists` quand « en cours d'acquisition » survit à une deuxième
tentative terminée.

**Une seule lecture intermédiaire n'est pas une difficulté** : c'est ce à quoi
ressemble un apprentissage en chemin. Le seuil de deux tentatives est le point où
l'enfant est revenue sur la compétence sans que cela bouge.

**Une compétence jamais travaillée n'est pas une lacune.** Elle n'a aucune
lecture ; la ranger sous « difficulté » ferait d'une absence une accusation.
C'est la même règle qu'à l'étape 10, où l'absence de preuve n'écrit aucun
résultat.

Les cinq règles sont **publiées** par `GET /api/v1/diagnostic/rules` plutôt que
rendues configurables, exactement comme les règles de lecture de l'étape 10 :
choisir le seuil à partir duquel la plateforme appelle quelque chose une
difficulté est une décision sur ce qui est dit d'un enfant, pas un réglage, et il
n'existe personne pour la prendre avant le rôle Administrateur de l'étape 15.

### Le regroupement ajoute une lecture, il n'en retire aucune

`general-gap-same-domain` regroupe au moins deux lacunes localisées d'un même
domaine du référentiel. Les compétences qu'il nomme **restent listées une par
une** dans les lacunes localisées, et les deux listes voyagent côte à côte.

Une lacune seule dans un domaine n'est pas un motif : l'appeler ainsi en
inventerait un.

### Une cause racine est une arête entre deux lacunes, et rien de plus

`root-cause-prerequisite` : quand une compétence en lacune est prérequis d'une
autre compétence en lacune, dans l'édition en vigueur, elle est proposée comme
cause possible. Seules les arêtes entre deux lacunes comptent — un prérequis
acquis est une preuve *contre* l'hypothèse, un prérequis jamais travaillé n'est
aucune preuve.

`confirmed` est un **champ**, toujours `false`, plutôt qu'un sous-entendu : un
client ne doit pas pouvoir présenter l'hypothèse comme une cause établie par
simple omission.

### Rien n'est stocké, et c'est ce qui rend la règle vraie

Aucune table. Le diagnostic se calcule à chaque lecture, à partir des progrès de
l'étape 11, eux-mêmes sommés des résultats de l'étape 10.

Un diagnostic stocké serait une quatrième chose capable de contredire les trois
dont il vient, et une lacune périmée est pire qu'une lacune absente. Surtout,
c'est ce qui rend vraie **par construction** la règle « une cause racine reste
une hypothèse jusqu'à la réévaluation » : l'hypothèse est recalculée à chaque
lecture, donc une réévaluation la change à l'instant où elle arrive. Aucune tâche
de fond, rien à invalider.

Aucune couche ne rejuge celle du dessous : le diagnostic somme des lectures, il
ne recalcule aucune. Recalculer laisserait les mêmes preuves dire deux choses
différentes selon le chemin emprunté.

### Le score de santé résume, il ne remplace pas

`health-weighted-outcomes` : moyenne pondérée des compétences **observées**, une
acquise comptant 1, une en cours 0,5, une non acquise 0, rendue sur 100, avec
chacun de ses termes à côté.

La tension avec « une note ne remplace jamais une compétence » se résout par
trois propriétés, et non par un compromis :

- il apparaît **une fois, pour un enfant**, à côté de la lecture complète par
  compétence qu'il résume — jamais à la place de l'une d'elles ;
- il est calculé sur ce que cette enfant a travaillé, **et sur rien d'autre** :
  ni sur le programme, ce qui se lirait « quel retard », ni contre d'autres
  enfants, ce que la plateforme ne calcule nulle part ;
- chacun de ses termes voyage avec lui, donc il se démonte.

**Rien d'observé ne rend aucun score**, et il n'y a délibérément pas de zéro pour
cela : zéro dirait que le travail s'est mal passé, alors qu'il n'a pas eu lieu.

### Une compétence dont le prérequis est en lacune n'est pas proposée du tout

*Amendement du 16 août 2026.* La première version proposait la compétence
dépendante **après** sa cause racine. Le propriétaire a corrigé : elle ne doit
pas être proposée du tout tant que le prérequis est en lacune.

> « L'idée est de ne pas lui demander d'assurer une compétence alors que le vrai
> problème c'est une autre compétence prérequis : lui demander d'assurer des
> opérations mathématiques alors que le vrai problème c'est le comptage, lui
> demander de conjuguer alors qu'il peine à reconnaître les groupes de verbes ou
> à discerner les temps qui existent. »

`defer-behind-prerequisite` est donc une sixième règle publiée. La lacune
dépendante **reste affichée** au parent, avec `blocked_by` et la phrase qui dit
sur quoi elle attend : reporter ce qu'on fait travailler n'est pas cacher ce
qu'on a trouvé, et un parent qui voit une difficulté sans remédiation à côté doit
savoir que le silence est délibéré.

Les chaînes se règlent d'elles-mêmes : dans A ⟵ B ⟵ C toutes en lacune, B attend
A et C attend B, donc seule A est travaillée.

### Le score est pondéré par le nombre de tentatives

*Amendement du 16 août 2026.* La première version faisait peser toutes les
compétences observées pareil, et l'agent avait signalé la limite sans la lever.
Le propriétaire a tranché : **pondérer par le nombre de tentatives terminées**.

Une compétence reprise dix fois pèse dix fois une compétence vue une seule.
Le coût est écrit plutôt que caché : ce qui a été le plus refait porte désormais
le plus de poids, et ce n'est pas toujours ce qui compte le plus. Le total des
tentatives voyage avec le score, parce qu'une moyenne pondérée dont le
dénominateur est caché ne peut pas être vérifiée par qui on la montre.

### La plateforme n'assigne rien d'elle-même, et une route évite la ressaisie

*Amendement du 16 août 2026, en deux temps, et il vaut la peine de garder les
deux.*

La première version excluait toute assignation automatique, au motif
qu'automatiser déciderait à la place d'un adulte. Le propriétaire a **infirmé** :

> « Le système doit pouvoir faciliter la tâche au parent. Après avoir fait un
> diagnostic, il doit pouvoir lui proposer puis aviser le parent, mais tout ça
> doit être réglable par le parent : il peut décider de faire entièrement
> confiance et d'approuver que le système assigne directement. »

Un mode `automatic`, réglable par enfant, a donc été construit. Le propriétaire a
ensuite tranché : **« on abandonne le mode automatique pour le moment, on reste
comme avant »**. Il a été retiré, colonnes comprises, par la migration `0012`.

Ce qui subsiste de l'aller-retour, et qui répond au « faciliter la tâche » sans
rien décider à la place de personne :

- `POST /api/v1/children/{id}/remediation` donne les propositions **sur la parole
  du parent**. Ce que la route retire est la ressaisie, pas la décision : être
  d'accord avec les propositions ne doit pas obliger à les recopier une à une
  dans le formulaire d'affectation.
- Ce qui est déjà en attente, ou ce qui passerait le plafond d'activités en
  cours, est **écarté et nommé** plutôt que forcé.
- Aucune lecture n'affecte quoi que ce soit : un `GET` ne crée rien, et la
  clôture d'une tentative ne donne rien non plus.

**La leçon de conception retenue** : quand une fonctionnalité pourrait agir à la
place du parent, la question n'est pas « automatiser ou refuser » mais « qu'est-ce
qui est de l'ergonomie et qu'est-ce qui est de la décision ». Retirer une
ressaisie est de l'ergonomie ; choisir ce qu'un enfant fera est une décision.

**Où vivra le réglage s'il revient.** Le propriétaire a corrigé l'agent sur ce
point avant d'abandonner la fonctionnalité, et l'arbitrage reste valable : « le
réglage doit être porté par le parent pour cette version, mais si le ou les
parents ont plusieurs enfants ils peuvent faire différents réglages selon
l'enfant ». Donc un réglage **appartenant au parent**, avec une valeur par
enfant — et non une colonne du profil de l'enfant, ce que l'agent avait choisi.

Les colonnes de `0011` ont été supprimées plutôt que laissées en place « pour
plus tard ». Une colonne à valeur unique se lit comme une distinction que le code
ferait, et il ne la fait pas ; la garder coûterait un malentendu à chaque
rencontre, et la ramener coûte une migration.

### Une Quick Repair dure de 3 à 7 minutes, et mène à une preuve

Une activité publiée travaillant la compétence, dans cette bande de durée. Hors
de la bande, elle n'est pas proposée, si bien assortie soit-elle : proposer vingt
minutes comme réparation rapide rendrait la promesse fausse.

Une seule activité par compétence, les causes racines d'abord. En proposer trois
laisserait croire que la plateforme sait laquelle est la meilleure.

Chaque recommandation **nomme sa preuve finale** — la lecture de la tentative,
par les règles de l'étape 10 — parce que « toute remédiation possède une preuve
finale » et que recommander quelque chose qui ne conclut rien laisserait la
lacune où elle était. Rien n'est marqué comme réparé ici : « une ouverture de
contenu ne valide jamais seule une compétence ».

### L'enfant voit des actions, le parent voit le diagnostic

Le même moteur produit les deux, et la différence est **ce qui traverse**. Une
enfant voit une activité et sa durée ; ni le score, ni les lacunes, ni la règle
qui a nommé une difficulté.

Ce n'est pas du secret sur son propre travail : ses tentatives, ses résultats et
ses progrès restent à sa disposition, et chacun s'explique tout seul. C'est
qu'une liste de réparations remise à une enfant **comme un diagnostic** est un
jugement auquel elle n'a aucun moyen de répondre, et que le produit place un
adulte dans la boucle précisément pour qu'elle n'ait pas à le faire.

Deux routes distinctes plutôt qu'une route qui servirait l'un ou l'autre : une
route unique serait à un contrôle oublié près de montrer à une enfant ce qui
n'est pas pour elle.

## Conséquences

- Le MVP tient enfin sa boucle : lacune détectée, Quick Repair recommandé,
  contenu joué, résultat capturé, lacune et score recalculés. Il manque
  l'affichage, qui est l'étape 13.
- **La plateforme n'assigne rien d'elle-même dans cette version.** Elle propose,
  et le parent donne — en un appel plutôt qu'en ressaisissant. Un mode
  automatique ne sera pas reconstruit sans une demande nouvelle et explicite ; s'il
  revient, son réglage appartiendra au parent, avec une valeur par enfant.
- Le calcul à la lecture coûte quelques requêtes par appel, sur des volumes
  d'une famille. Si les tableaux de bord de l'étape 13 demandent un cache, ce
  sera une décision de cache prise au grand jour, comme déjà écrit dans ADR-014.
- Sans édition du référentiel en vigueur, les lacunes sont rendues mais ni
  regroupées ni expliquées par un prérequis. `tree_available` le dit, pour qu'une
  réponse courte ne se lise pas « aucune difficulté ».
