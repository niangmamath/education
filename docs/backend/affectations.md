# Affectations

## Périmètre

Cette page décrit l'étape 09 : comment une activité du catalogue est donnée à un
enfant, ce qu'il en fait, et ce qu'un parent peut reprendre. Le catalogue est
décrit dans `catalogue-activites.md`. Les tentatives et leurs preuves relèvent de
l'étape 10.

## Une affectation est un fait, pas un réglage

L'affectation est la première table du projet qui relie le catalogue à une
personne. Elle porte donc deux garanties sur lesquelles la suite s'appuiera.

**Rien n'est réécrit ni supprimé.** Une affectation est donnée, prise, terminée —
ou annulée. Annuler ne l'efface pas : la ligne reste, datée, parce qu'un enfant à
qui l'on a donné puis retiré quelque chose n'a pas la même histoire qu'un enfant
à qui l'on n'a rien donné. Redonner la même activité crée une **seconde ligne**,
de sorte que « elle l'a faite deux fois » et « elle l'a faite une fois » restent
deux faits distincts.

**Une activité affectée ne peut plus être supprimée.** La clé étrangère
*restreint* au lieu de cascader : perdre une activité laisserait chaque tentative
de l'étape 10 pointer vers rien. Une activité se retire du service en passant à
`archived`, jamais en disparaissant.

## Les états, et le fait que rien ne revienne en arrière

```text
                 ┌──────────────┐
   parent ──────▶│  assigned    │──────▶ cancelled   (parent)
                 └──────┬───────┘
                        │ enfant
                        ▼
                 ┌──────────────┐
                 │ in_progress  │──────▶ cancelled   (parent)
                 └──────┬───────┘
                        │ enfant
                        ▼
                 ┌──────────────┐
                 │  completed   │        terminal
                 └──────────────┘
```

Une affectation terminée ne se rouvre pas, une affectation annulée ne reprend
pas. Toute tentative répond `409`.

Chaque état porte sa date, et une contrainte l'exige : un statut sans son moment
serait une affirmation sans date derrière elle.

**Terminer n'est pas réussir.** Rien ici ne touche à une compétence. Une règle du
projet dit qu'ouvrir un contenu ne valide jamais une compétence à lui seul ; la
preuve appartient aux tentatives de l'étape 10, et cette étape-ci ne fait que
constater qu'une activité a été menée à son terme.

## Qui fait quoi

| Action | Qui | Route |
|---|---|---|
| donner une activité | Parent | `POST /api/v1/assignments` |
| lister ce qui a été donné | Parent | `GET /api/v1/assignments` |
| annuler | Parent | `POST /api/v1/assignments/{id}/cancel` |
| voir ce qu'on lui a donné | Élève | `GET /api/v1/me/activities` |
| commencer | Élève | `POST /api/v1/me/activities/{id}/start` |
| terminer | Élève | `POST /api/v1/me/activities/{id}/complete` |

**Les deux espaces ne se mélangent pas.** Une route Parent exige `CurrentParent`,
une route Élève exige `CurrentChild`, et aucune n'accepte l'autre : un enfant ne
peut pas se donner du travail, un parent ne peut pas terminer l'activité à sa
place. Une route qui accepterait les deux serait à un oubli de contrôle près de
permettre l'un ou l'autre.

## L'isolation est portée par la requête

Un parent demande un de **ses** enfants ; une affectation d'une autre famille
répond exactement comme une affectation qui n'existe pas. Rien ne permet de
savoir si une ligne appartient à quelqu'un d'autre.

C'est le même principe qu'à l'étape 06 : le rattachement familial est dans la
clause `WHERE`, pas dans un contrôle ajouté après coup.

Un enfant ne voit que ses propres lignes, et sa vue ne lui répète pas de quel
enfant il s'agit : tout ce qu'il voit est à lui, le dire sur chaque ligne serait
du bruit.

## Ce que la base refuse d'elle-même

| Règle | Comment |
|---|---|
| statut hors des quatre valeurs | contrainte `CHECK` |
| statut sans sa date | trois contraintes `CHECK` |
| même activité due deux fois à la fois | index unique partiel sur les états ouverts |
| supprimer une activité affectée | clé étrangère `RESTRICT` |

L'index est **partiel**, sur `assigned` et `in_progress` seulement : c'est ce qui
interdit le doublon tout en laissant l'activité être redonnée une fois la
première affectation close.

Le refus du doublon est aussi vérifié avant l'écriture, non par méfiance envers
la base mais pour rendre au parent une réponse sur laquelle agir plutôt qu'une
erreur d'intégrité.

## Ce que l'étape 09 ne fait pas

- Aucune tentative, aucun score, aucune preuve : c'est l'étape 10.
- Aucune recommandation automatique : le moteur déterministe est l'étape 12. Ici,
  c'est le parent qui choisit.
- Aucune échéance ni ordre de parcours : une affectation est donnée, pas
  planifiée.
- Aucune remise du contenu au navigateur : le lecteur H5P et l'origine de contenu
  isolée restent à construire.
- Aucun affichage : les pages web restent les maquettes de l'étape 05.
