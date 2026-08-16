# ADR-015, Diagnostic explicable, hypothèses non stockées, et ce que chaque côté voit

- Statut : Accepté
- Date : 16 août 2026

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
- **Aucune assignation automatique.** Une recommandation est une proposition ;
  la donner reste un geste du parent, par la route d'affectation de l'étape 09.
  Automatiser cela déciderait à la place d'un adulte, ce que le produit refuse.
- Le calcul à la lecture coûte quelques requêtes par appel, sur des volumes
  d'une famille. Si les tableaux de bord de l'étape 13 demandent un cache, ce
  sera une décision de cache prise au grand jour, comme déjà écrit dans ADR-014.
- Sans édition du référentiel en vigueur, les lacunes sont rendues mais ni
  regroupées ni expliquées par un prérequis. `tree_available` le dit, pour qu'une
  réponse courte ne se lise pas « aucune difficulté ».
