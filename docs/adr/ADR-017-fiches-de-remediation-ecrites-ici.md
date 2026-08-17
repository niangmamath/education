# ADR-017, Les fiches de remédiation sont écrites ici, pas importées

- Statut : Accepté
- Date : 17 août 2026

## Contexte

Le diagnostic sait nommer une lacune, remonter au prérequis qui la cause et
proposer une réparation courte. Cette chaîne était complète sauf à son dernier
maillon : **les douze remédiations étaient des lignes de catalogue sans rien
derrière**. Un parent pouvait donner une activité qui s'ouvrait sur une page
vide. Une seule des douze avait un contenu jouable, et par accident — c'était
celle sur laquelle le paquet H5P du pilote avait été posé.

La question posée était : produire ou télécharger ?

## Décision

**Les douze fiches sont écrites dans la plateforme**, comme l'examen
d'initiation, et pour une raison de plus que lui.

Une fiche est une activité de nature `remediation` : trois à sept minutes, une
compétence, une leçon puis quatre questions, et une explication après chacune.

## Pourquoi pas du contenu importé

Quatre raisons, dont trois sont des murs.

**Le rattachement n'existe nulle part ailleurs.** Une remédiation doit une
preuve, et une preuve qu'on ne peut pas rattacher à la compétence qu'elle répare
ne prouve rien. Aucune banque de contenus, si fournie soit-elle, ne peut livrer
une question qui travaille `cp-ma-denombrer` : ce code est le nôtre. Sans le
rattachement, une lecture s'étale sur toutes les compétences de l'activité —
exactement l'attribution grossière que le projet refuse.

**ADR-012 n'autorise qu'une bibliothèque.** `H5P.TrueFalse` 1.8, tenue par une
contrainte de vérification sur la table des paquets. Importer autre chose exige
d'élargir la liste, une migration, un amendement d'ADR, l'antivirus et la
vérification de licence — la friction délibérée que cette décision réclamait, et
qui n'a pas à être dépensée pour une démonstration.

**L'origine de contenu n'est pas déployée.** Sur Render, un disque appartient à
un seul service : l'origine isolée que nginx sert n'a nulle part où vivre. Une
fiche importée n'y jouerait pas. Une fiche écrite ici fonctionne partout où
l'examen fonctionne.

**Une réparation doit enseigner.** Une question vrai-ou-faux téléchargée
interroge ; elle n'explique pas. Chaque fiche s'ouvre sur ce qu'il faut retenir
et répond après chaque question — c'est toute la différence entre une réparation
et un second contrôle, servi à une enfant à qui l'on vient d'annoncer une
difficulté.

## Conséquences

### Ce qui est mutualisé, et ce qui ne l'est pas

L'examen et les fiches sont **notés par le même code** : `app.authored.service`
lit les questions et corrige les réponses sans jamais savoir laquelle des deux
natures l'a appelé. La table `assessment_questions` a été renommée
`authored_questions` pour la même raison — deux tables aux quatre mêmes colonnes
auraient divergé, et le moteur de lecture aurait dû apprendre où chercher.

Ce qui **n'est pas** mutualisé, c'est ce que chacun répond. Une fiche renvoie
l'explication ; l'examen ne renvoie rien. Un examen qui répond cesse de mesurer :
il se parcourrait une question à la fois.

Cette asymétrie a ouvert une porte, et il a fallu la fermer. La route des fiches
**refuse une tentative qui n'est pas celle d'une fiche** : sans ce contrôle, une
enfant pouvait poster ses réponses d'examen à la route des fiches et se faire
dire, une par une, si elles étaient justes. L'examen aurait été franchissable par
la porte ouverte pour l'aider.

### Le contenu importé ne disparaît pas

Le paquet H5P vérifié garde une activité à lui, `demo-h5p-vrai-faux`, en dehors
des douze réparations. Le runtime de contenu est un vrai travail et doit rester
démontrable — mais plus rien dans le parcours ne dépend de son déploiement.

### Ce que les fiches ne savent toujours pas faire

**Entendre.** Les questions de phonologie parlent de mots écrits, comme celles de
l'examen. C'est un pis-aller assumé, pas une conception, et l'audio reste la
première chose à ajouter si tout ceci sert en vrai.

**Dessiner.** Le dénombrement se fait sur des rangées de symboles typographiques,
ce qui fonctionne jusqu'à une dizaine et pas au-delà.

## Alternatives écartées

**Élargir la liste d'ADR-012 à MultiChoice, Blanks et QuestionSet.** C'est le
chemin qu'il faudra prendre si la plateforme accueille un jour du contenu produit
par d'autres. Il ne résout ni le rattachement, ni le déploiement, ni le fait
qu'une question importée n'explique rien — et il coûte cher.

**Laisser les douze coquilles et n'en remplir qu'une.** C'est l'état d'avant. Le
diagnostic proposait alors des réparations qui ne réparaient rien, ce qui est
pire qu'un diagnostic sans proposition : le parent agit, et il ne se passe rien.
