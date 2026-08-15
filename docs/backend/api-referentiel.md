# API du référentiel

## Périmètre

Cette page décrit la sous-étape 07.3 : les lectures filtrées et paginées du
référentiel. La modélisation est décrite dans `referentiel-competences.md`,
l'import et la publication dans `import-referentiel.md`.

## Les routes servent l'édition en vigueur, et elle seule

```text
GET /api/v1/referential/edition
GET /api/v1/referential/levels
GET /api/v1/referential/subjects
GET /api/v1/referential/competencies
```

Toutes lisent la version `published`, sans qu'aucun paramètre ne permette d'en
désigner une autre.

Un **brouillon** ne sort jamais par HTTP. C'est un programme en cours
d'écriture ; il se relit avec la commande d'import en essai à blanc, par qui a
accès au serveur. Aucun client ne peut donc bâtir sur un référentiel qui n'est
pas arrêté.

Une **édition archivée** n'est pas servie non plus. Les traces des étapes 10 à
12 en auront besoin un jour, pour être relues dans le référentiel où elles ont
été écrites ; ce jour-là viendra avec sa propre route, et la décision de savoir
qui peut lire une édition retirée.

## Qui peut lire

**Toute session authentifiée**, Parent comme Enfant. Le référentiel n'est pas
une donnée personnelle et les deux espaces en ont besoin : l'Élève pour son
arbre de compétences, le Parent pour son tableau de bord. Une seule dépendance
d'autorisation, donc un seul chemin de lecture, qui ne peut pas diverger entre
les deux espaces.

Exiger une session ne protège pas un secret : elle évite d'offrir à qui trouve
l'URL une base complète à aspirer, alors que le premier plafond de débit du
projet reste à construire.

Sans cookie de session, les quatre routes répondent `401`.

## L'enveloppe

```json
{
  "edition": { "code": "fictif-2026-01", "label": "Référentiel fictif 2026-01" },
  "items": [ ... ],
  "page": 1,
  "page_size": 50,
  "total": 39
}
```

**Chaque réponse nomme l'édition qu'elle a lue.** Un client qui garde une liste
de compétences peut ainsi savoir s'il regarde toujours l'édition en vigueur, au
lieu de le supposer. Le jour où une nouvelle édition est publiée, la même URL
répond avec un autre `edition.code` : c'est le signal, et il est dans la réponse.

`edition` vaut `null` quand aucune édition n'est en vigueur. Ce n'est pas une
erreur : le référentiel n'a simplement rien de publié, et `items` est vide. Un
client distingue ce cas d'une édition qui ne contiendrait rien. La route
`/edition`, elle, répond `404` : c'est une ressource unique, et elle n'existe
pas.

Les identifiants exposés sont les **codes métier**, jamais les UUID. `cm1-math-num-01`
désigne la même compétence d'une édition à l'autre ; un UUID est refrappé à
chaque import et donnerait à un client l'envie de stocker quelque chose de
transitoire.

## Filtres et pagination

| Paramètre | Route | Effet |
|---|---|---|
| `level` | compétences | code de niveau |
| `subject` | compétences | code de matière |
| `domain` | compétences | code de domaine |
| `page` | toutes | numéro de page, à partir de 1 |
| `page_size` | toutes | taille de page, 100 au plus |

Les filtres se combinent. Un filtre nommant un code que l'édition ne contient
pas rend une page vide plutôt qu'une erreur : c'est un filtre, et ne rien
laisser passer est une réponse ordinaire.

Un `page` ou un `page_size` hors bornes est refusé en `422` ; le plafond de 100
existe pour qu'une seule requête ne puisse pas demander tout le référentiel.

L'ordre est **total** : matière, domaine, niveau, rang, puis code. Sans ce
dernier critère, deux compétences de même rang pourraient s'échanger d'une page
à l'autre, et la pagination montrerait l'une deux fois et l'autre jamais.

Les compétences nomment leur niveau, leur domaine **et** leur matière, ce qui
évite au client une seconde requête pour savoir de quelle matière relève un
domaine.

## L'arbre de prérequis n'est pas exposé

Il est modélisé depuis 07.1 et n'a encore aucun lecteur. Il appartient à la
remédiation de l'étape 12, qui dira quelle forme lui donner ; l'exposer avant
figerait une forme dont personne n'a eu besoin.

## Ce que 07.3 ne fait pas

- Aucune lecture d'un brouillon ni d'une édition archivée.
- Aucune écriture : l'import et la publication restent des commandes.
- Aucun accès sans session, et aucun plafond de débit, qui reste à construire.
- Aucun lien vers les activités H5P, qui relève de l'étape 08.
