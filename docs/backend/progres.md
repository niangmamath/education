# Progrès

Ce que plusieurs tentatives, mises bout à bout, disent d'un enfant. Les
tentatives et leur lecture sont dans `tentatives-resultats.md`, les événements
dans `evenements-xapi.md`, la décision dans ADR-014.

## Rien n'est stocké

Il n'y a **pas de table d'agrégats**. Les progrès sont calculés à chaque
lecture, à partir des résultats déjà écrits et des événements déjà reçus.

C'est ce qui les rend *reproductibles* au sens que l'étape demande : les mêmes
faits donnent la même réponse, et il n'existe pas une quatrième chose capable de
contredire les trois dont elle est tirée. Le prix est quelques requêtes par
lecture, sur les volumes d'une famille. Si les tableaux de bord de l'étape 13
demandent un cache, ce sera une décision de cache prise au grand jour, et non une
duplication silencieuse de la vérité.

## Les résultats sont sommés, jamais recalculés

La lecture d'une tentative a été faite à sa clôture, avec l'attribution
question-compétence telle qu'elle était alors — `catalog_activity_questions`,
facultative, décrite dans `catalogue-activites.md`.

Recalculer ici appliquerait l'attribution d'aujourd'hui aux réponses d'hier, et
changerait sans le dire une conclusion qu'un parent a peut-être déjà vue. Donc
ce fichier somme des résultats ; il ne touche jamais aux règles.

C'est aussi pourquoi la répartition des preuves par provenance est donnée **au
niveau de l'enfant et non par compétence** : la ventiler par compétence
supposerait de réattribuer les réponses d'hier, exactement ce qu'on refuse.

## Seules les tentatives terminées comptent

Une tentative en cours n'a rien conclu — par construction, puisque les résultats
sont écrits à sa clôture. Une tentative abandonnée a été interrompue. Compter
l'une ou l'autre rapporterait comme progrès quelque chose qui n'a pas eu lieu.

Les **preuves**, en revanche, sont comptées sur toutes les tentatives : elles
décrivent ce que la plateforme a reçu, ce qui est vrai qu'une tentative ait été
terminée ou non.

## Ce qui est rendu

Par compétence :

- le **dernier mot**, `latest_outcome`, et sa date ; pas une moyenne. Une
  compétence retravaillée se lit à son état le plus récent ;
- combien de tentatives terminées ont conclu, et combien de fois chacun des
  trois mots a été atteint ;
- les comptes cumulés, `answered_total` et `correct_total` ;
- une phrase en français, construite à partir des mêmes valeurs, pour qu'un
  parent puisse se voir montrer autre chose qu'un tableau.

Pour l'enfant, un bloc `evidence` : combien d'événements reçus, combien de
réponses déclarées, combien venues du runtime. C'est ce qui dit sur quoi la
lecture repose.

**Aucun ratio, aucun pourcentage, aucun score, nulle part.** Les comptes
voyagent, et qui les affiche peut les diviser ; la plateforme ne le fait pas,
parce qu'un nombre présenté comme un niveau de maîtrise est précisément ce qu'une
règle du projet interdit. Un test le vérifie sur la charge utile.

## Routes

| Route | Qui | Ce qu'elle rend |
|---|---|---|
| `GET /api/v1/me/progress` | Élève | Ses propres progrès |
| `GET /api/v1/children/{child_id}/progress` | Parent | Les progrès d'un enfant de sa famille |

Deux routes pour une même lecture, plutôt qu'une route qui servirait l'un ou
l'autre. L'enfant demande les siens et ne peut nommer personne ; le parent nomme
un enfant et doit en être le parent. Une route unique avec un identifiant
facultatif serait à un contrôle oublié près de montrer à une famille le travail
d'une autre.

Un enfant d'une autre famille est refusé comme un enfant qui n'existe pas.

Les deux routes rendent la même forme. Il n'y a rien ici qu'un enfant ne puisse
voir sur elle-même : une lecture qui nomme sa règle et porte ses comptes est
faite pour être montrée à la personne dont elle parle.

## Ce que les progrès ne font pas

- **Aucun diagnostic, aucune recommandation, aucune tendance nommée.** C'est
  l'étape 12, et en poser une première version ici ferait décider à deux endroits
  ce qu'est une difficulté. Ce qui est rendu est descriptif.
- **Aucune vue famille**, aucune comparaison entre enfants, aucun classement.
- **Aucun libellé de compétence** : le lien avec le référentiel se fait par
  code, ADR-013, et résoudre les libellés appartient à qui affiche.
