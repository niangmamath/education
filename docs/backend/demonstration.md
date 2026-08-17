# Jeu de données de démonstration

Une commande qui remplit la plateforme de quoi la montrer en cinq minutes.
Tout y est fictif, comme les décisions du projet l'exigent, et chaque adresse
appartient à `example.com`, réservé par la RFC 2606.

```bash
docker compose exec api python -m app.demo            # créer ou compléter
docker compose exec api python -m app.demo --reset    # tout refaire à neuf
docker compose exec api python -m app.demo --clean    # tout retirer
```

La commande affiche à la fin les identifiants qu'elle vient de créer. Le code
famille est tiré au hasard à chaque création : c'est le comportement de la
plateforme, pas une négligence du script.

## Tout passe par les services réels

Les tentatives sont **données, commencées, répondues et terminées** par le code
même qu'atteint le navigateur d'un enfant. Les lectures affichées sur les
tableaux de bord sont donc produites par les règles, et non écrites à côté
d'elles.

Un jeu de démonstration inséré directement en base serait une démonstration des
tables. Il divergerait du produit dès la première règle modifiée, et il
mentirait le jour où on s'en servirait pour montrer quelque chose.

**Chaque acte a sa propre session**, parce que c'est aussi ce que fait un
navigateur. Ce n'est pas un détail : une tentative chargée avant que ses
réponses existent garde une collection vide, et la lecture à la clôture ne
trouverait rien à lire. Une seule session pour tout le passé produit des
tentatives et des réponses sans aucune conclusion — c'est exactement ce que le
script a fait avant que ce soit corrigé.

## Ce que la démonstration met en scène

Le jeu de données n'est pas un remplissage. Il est arrangé pour qu'une
démonstration traverse les trois comportements les moins évidents de la
plateforme sans que personne ait à les préparer à la main.

### 1. Le prérequis avant ce qui en dépend

Léa a échoué au comptage **et** aux additions, et additionner requiert de
compter. La plateforme ne propose donc **que** le comptage, et montre les
additions comme reportées, avec la raison :

> Rien n'est proposé pour « Additionner deux nombres jusqu'à 10 » tant que
> « Compter jusqu'à 20 », qui en est un prérequis, reste en lacune.

C'est le point le plus contre-intuitif du produit, et le plus facile à rater
dans une démonstration improvisée : la réponse ordinaire serait « elle est en
retard sur les additions », et ce serait la mauvaise.

### 2. Une lacune est une candidate, pas un verdict

Chaque conclusion à l'écran porte la règle qui l'a produite et les comptes dont
elle vient. Le score de santé se démonte de la même façon : il dit combien de
compétences ont été observées, dans quel état, et sur combien de tentatives.

### 3. Une famille ne voit pas l'autre

Une seconde famille existe pour ça. Se connecter avec l'autre compte Parent ne
montre rien de la première — l'isolation reste une affirmation tant que personne
n'a essayé.

Tom est là pour le contraste : tout ce qu'il a fait s'est bien passé. Une
démonstration où chaque enfant est en difficulté enseigne quelque chose de faux
sur le produit.

## Une seule activité se joue réellement

Le pilote ne dispose que d'un paquet H5P vérifié, et la plateforme refuse
d'attacher le même fichier à deux activités. Une seule activité est donc
réellement jouable, et la commande dit laquelle plutôt que de laisser
quelqu'un le découvrir en cliquant.

C'est **la réparation que la plateforme propose pour Léa** — celle sur laquelle
la démonstration se termine : le parent la donne, l'enfant la joue, l'événement
du contenu remonte, la tentative est lue, et le tableau de bord change.

Les autres activités garnissent les listes. Contourner la règle du catalogue
pour une démonstration reviendrait à démontrer autre chose que le produit.

## Parcours suggéré, cinq minutes

1. **Parent** — se connecter, voir les deux enfants et ce qui a changé.
2. **Page de Léa** — le score et sa phrase, le point d'attention, la section
   « mises de côté pour l'instant » et l'hypothèse de cause racine.
3. **Donner l'activité proposée** — un bouton, et rien n'était donné avant.
4. **Élève** — se déconnecter, entrer avec le code famille, le pseudo et le code
   secret de Léa ; l'activité attend.
5. **Jouer, terminer** — la lecture s'affiche avec sa phrase.
6. **Revenir côté Parent** — le tableau de bord a changé.
7. **Autre famille** — se connecter avec le second compte : rien de la première.

## Ce que la commande ne fait pas

- **Elle ne touche à rien qui ne porte pas son préfixe.** `--clean` retire ce qui
  commence par `demo-` et laisse le reste de la base intacte.
- **Elle ne remet pas en vigueur l'édition du référentiel qu'elle a archivée.**
  Publier archive l'édition précédente, c'est la règle de la plateforme ; la
  remettre en vigueur est une décision, pas un effet de bord d'un script de
  démonstration.
- **Elle n'invente aucune conclusion.** Le jeu de données dit comment les
  questions se sont passées ; ce que cela veut dire est décidé par les règles.
