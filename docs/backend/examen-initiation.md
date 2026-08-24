# Examen d'initiation

La première marche du parcours, qui manquait. La définition du MVP du projet
dit :

> Parent crée un enfant → **enfant réalise un diagnostic** → compétences mises à
> jour → lacune détectée → Quick Repair recommandé

Toutes les flèches après la deuxième existaient. La deuxième, non. Un enfant
inscrit lundi n'avait aucune compétence observée, donc aucun diagnostic, donc
aucune recommandation : le parcours démarrait vide et le restait jusqu'à ce qu'un
adulte pense à assigner quelque chose.

## Pourquoi il n'est pas en H5P

C'est une décision, pas un raccourci.

**Chaque question doit être rattachée à une compétence de notre référentiel**, et
ce rattachement n'existe nulle part ailleurs que chez nous. Aucune banque de
contenus, si fournie soit-elle, ne peut livrer une question qui « travaille
`cp-ma-denombrer` » — ce code est le nôtre.

L'écrire nativement coûte par ailleurs zéro là où H5P coûte cher : aucune
bibliothèque à figer, aucun type à faire entrer dans la liste d'ADR-012, aucun
volume de contenu partagé à organiser. C'est aussi ce qui rend l'examen
déployable là où le runtime de contenu ne l'est pas encore.

## Ce qui est réutilisé, et ce qui est neuf

**Neuf** : une quatrième nature d'activité, `assessment`, et une table
`assessment_questions` qui porte l'énoncé, les choix et la bonne réponse.

**Réutilisé** : tout le reste. Le rattachement question-compétence reste dans
`catalog_activity_questions`, où il était déjà — le moteur qui lit un résultat
doit continuer à lire **une** table, que l'activité ait été importée ou écrite
ici, et ne jamais apprendre la différence. La tentative, les réponses, le calcul
des résultats, le diagnostic : inchangés.

## La bonne réponse ne quitte jamais le serveur

Le modèle public n'a **pas de champ** pour elle : elle est absente par
construction et non par filtrage, comme les empreintes de mot de passe et de PIN
le sont déjà ailleurs. Aucune édition ultérieure ne peut en faire fuiter une par
ce schéma.

Le client envoie une **position dans la liste des choix**. Il n'envoie jamais si
c'était juste, et il ne serait pas cru s'il le faisait — c'est toute la raison
pour laquelle la correction est de ce côté-ci.

## La seule chose que la plateforme assigne

L'examen est donné **à l'activation du profil**, par la plateforme. C'est le seul
endroit où elle assigne quoi que ce soit, et l'exception est argumentée plutôt
que supposée : un diagnostic qui attend qu'un parent y pense est un diagnostic
qui n'a pas lieu, et tout ce qui vient après n'a rien pour travailler tant qu'il
n'a pas eu lieu.

La remédiation, elle, reste ce qu'elle était : proposée, jamais donnée.

## Ce qu'un enfant voit

Une page sans minuteur, sans score, sans mention de niveau, et un titre qui dit à
quoi elle sert — « Pour faire connaissance ». Une enfant de six ans qui rencontre
une page intitulée « évaluation diagnostique » apprend quelque chose sur l'école
avant d'apprendre quoi que ce soit sur elle-même.

Le bouton d'envoi reste inactif tant qu'il manque une réponse, et dit combien il
en manque. Un formulaire qui refuse à l'envoi enseigne à une enfant qu'elle a
mal fait ; un formulaire qui dit ce qui reste, non.

Tout part en **une fois**. Une enfant sur la tablette du salon ne doit pas perdre
sa place à cause d'une connexion capricieuse, et rien n'est enregistré tant
qu'elle n'a pas dit qu'elle avait fini.

## Ce qu'il produit

Vingt-sept questions par classe, trois par compétence de la classe déclarée —
neuf compétences, trois par matière (français, mathématiques, anglais). Trois
questions et non une : `app.attempts.rules.read_counts` peut alors rendre une
compétence « partielle » (deux bonnes réponses sur trois) plutôt que de
trancher sur un seul coup de dé. À la clôture de la tentative, les règles de
l'étape 10 lisent les réponses et écrivent un résultat par compétence ; le
diagnostic de l'étape 12 en tire des lacunes, des reports et des propositions.

Concrètement, sur le jeu de démonstration : Léa passe l'examen et la plateforme
en sort **douze compétences observées, trois lacunes à travailler, quatre
reportées derrière leur prérequis, trois remédiations proposées** — dont aucune
sur les compétences reportées.

## Ce que l'examen ne fait pas

- **Aucun niveau attribué.** Il ne dit pas qu'une enfant « est CP » ou « est
  CE1 » : il dit ce qui est acquis et ce qui ne l'est pas, compétence par
  compétence. Ranger un enfant dans un niveau serait une conclusion d'une autre
  nature, et personne ne l'a demandée.
- **Aucune reprise.** On le passe une fois. Le repasser serait une réévaluation,
  et la réévaluation se fait par les activités, pas en refaisant le test d'entrée.
- **Aucun son, aucune image.** Les questions de phonologie se lisent, ce qui est
  un pis-aller assumé : à l'oral, elles seraient meilleures. C'est la première
  chose à améliorer si l'examen doit servir en vrai.
