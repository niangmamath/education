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
| ouvrir le contenu | Élève | `GET /api/v1/me/activities/{id}/content` |
| connaître les statuts existants | Parent | `GET /api/v1/assignments/statuses` |

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

## Échéance et ordre du parcours

Une affectation peut porter une **échéance**, une date et non un moment : la
semaine d'un enfant se compte en jours, et une heure de la journée serait une
précision que personne ne veut dire. Elle est facultative — la plupart des
activités sont simplement données, sans être attendues un jour précis. Une date
déjà passée est refusée : personne ne veut donner à un enfant quelque chose qui
était dû hier.

L'ordre du parcours en découle : **ce qui est attendu le plus tôt vient en
premier, ce qui n'est attendu aucun jour vient après tout le reste**, du plus
ancien au plus récent. C'est tout le « parcours ».

Réordonner à la main n'a pas été retenu : cela demanderait de maintenir un rang,
et un rang que personne ne met à jour est pire que pas de rang du tout. Le parent
dispose des dates, qui disent la même chose et se justifient d'elles-mêmes.

## Un plafond sur ce qui est dû

Un enfant ne peut pas se voir donner plus de **vingt activités à la fois**. Le
plafond compte ce qui est encore dû, jamais ce qui a été donné : terminer ou
annuler libère une place.

Il n'est pas là contre un abus mais contre un geste — une frappe de trop, un
parent qui déroule une liste — dont la conséquence serait d'ensevelir un enfant
de six ans.

## Ouvrir le contenu d'une activité

```text
GET /api/v1/me/activities/{id}/content
```

Rend un lien **signé et de courte durée**, cinq minutes, vers le paquet H5P.

**L'accès à un contenu n'est pas une propriété du contenu : c'est une propriété
de l'affectation.** Le paquet n'est remis qu'à l'enfant à qui il a été donné, et
seulement pendant qu'il y travaille. Un lien demandé avant d'avoir commencé, ou
gardé après avoir terminé, n'ouvre rien.

| Cas | Réponse |
|---|---|
| affectation en cours, activité H5P | lien signé, 200 |
| affectation pas encore commencée, terminée ou annulée | 409 |
| affectation d'un autre enfant | 404, comme une inexistante |
| Parent qui demande | 403, l'espace n'est pas le sien |
| activité PhET ou vidéo | 409, il n'y a pas de paquet à remettre |

Le bucket reste privé, conformément à ADR-008 : sans signature, le stockage
répond `403`.

### Ce qui manque encore pour jouer réellement le contenu

Le lien remet le fichier vérifié ; il ne le **joue** pas. Trois pièces manquent,
et aucune n'est une ligne de code de plus dans l'API :

1. **L'origine de contenu isolée**, sa CSP et son iframe, qu'ADR-012 exige à sa
   condition 5. Servir le contenu depuis l'origine de l'API serait précisément ce
   que cette isolation interdit ; c'est un travail d'infrastructure, un second
   domaine servi par le reverse proxy.
2. **Le lecteur `h5p-standalone` dans le web**, qui suppose le paquet déployé et
   les bibliothèques préparées hors ligne, figées comme artefacts internes selon
   la condition 3.
3. **L'endpoint xAPI authentifié**, condition 6, qui relève de l'étape 11 par
   construction.

La dette est donc réduite à ce qu'elle est vraiment : de l'infrastructure et une
étape à venir, plus une décision de déploiement. La part qui appartenait à l'API
— qui peut ouvrir quoi, quand, et sous quelle preuve — est faite.

## Ce que l'étape 09 ne fait pas

- Aucune tentative, aucun score, aucune preuve : c'est l'étape 10.
- Aucune recommandation automatique : le moteur déterministe est l'étape 12. Ici,
  c'est le parent qui choisit.
- Aucun réordonnancement manuel du parcours : l'ordre découle des échéances.
- Aucune lecture du contenu dans le navigateur : le lien est remis, l'origine
  isolée et le lecteur restent à construire.
- Aucun affichage : les pages web restent les maquettes de l'étape 05.
