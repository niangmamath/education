# Rapport de réalisation

## Métadonnées

- Étape : 07, référentiel de compétences
- Sous-étape : 07.3, API du référentiel
- Date et heure : 15 août 2026, 14h30
- Agent : Claude Code
- ID du planning : REF-03
- Branche : `feat/etape-07-referentiel`
- Commit ou pull request : branche poussée, Pull Request à la clôture de l'étape
- Statut : Terminé

## Objectif

Exposer des lectures filtrées et paginées du référentiel, et donner à une
édition le moyen d'entrer en vigueur, sans quoi aucune lecture n'aurait rien à
servir.

## Prérequis vérifiés

- 07.1 et 07.2 fusionnées dans `main`, Pull Requests #9, #10 et #11.
- Branche `feat/etape-07-referentiel` issue de `main`, portant déjà le
  garde-fou des déclarations `overlaps`.
- Docker Desktop relancé, cinq services sains.
- Migration à `0004_referential_competencies`, inchangée par cette sous-étape.

## État initial observé

Le référentiel s'importait mais restait invisible : aucune route, et aucun moyen
de publier une édition. Le brouillon `fictif-2026-01` existait en base sans
qu'aucun client puisse le lire.

## Travaux réalisés

### Deux décisions soumises au propriétaire

1. **Toute session authentifiée peut lire**, Parent comme Enfant. Le référentiel
   n'est pas une donnée personnelle et les deux espaces en ont besoin. Une seule
   dépendance d'autorisation, donc un seul chemin de lecture, qui ne peut pas
   diverger entre les espaces. Exiger une session ne protège pas un secret : elle
   évite d'offrir une base complète à aspirer à qui trouve l'URL.
2. **Les routes servent l'édition en vigueur et elle seule.** Aucun paramètre ne
   permet d'en désigner une autre. Un brouillon ne sort jamais par HTTP ; il se
   relit par la commande d'import en essai à blanc.

### La publication, décidée au point précédent

`app/referential/publication.py` et le verbe `publish` de la commande. Deux
verbes plutôt qu'un drapeau sur l'import : un import corrige un brouillon et peut
être rejoué vingt fois pendant qu'un programme s'écrit, une publication change ce
que voit chaque lecteur. Une frappe de trop à l'import ne peut donc rien mettre
en vigueur.

L'édition remplacée est archivée **dans la même transaction**, et l'ancienne est
libérée avant que la nouvelle ne prenne sa place : l'index unique partiel ne
tolère aucun recouvrement, si bref soit-il. Il n'existe aucun instant où deux
éditions sont publiées, ni aucun où il n'y en a plus.

Republier une édition archivée est refusé. La ramener changerait le sens de
toutes les traces enregistrées depuis son archivage ; c'est une décision à part
entière, pas le défaut d'une commande.

### Les lectures

`app/api/v1/referential.py`, quatre routes sous `/api/v1/referential`.

**Chaque réponse nomme l'édition qu'elle a lue.** Un client qui garde une liste
peut savoir s'il regarde toujours l'édition en vigueur au lieu de le supposer.
`edition` vaut `null` quand rien n'est publié : ce n'est pas une erreur, et un
client distingue ce cas d'une édition vide.

Les identifiants exposés sont les codes métier et jamais les UUID, qui sont
refrappés à chaque import et donneraient envie de stocker du transitoire.

L'ordre est total — matière, domaine, niveau, rang, puis code — sans quoi deux
compétences de même rang pourraient s'échanger d'une page à l'autre, et la
pagination montrerait l'une deux fois et l'autre jamais.

Les jointures répètent `version_id` à dessein : c'est la moitié de chaque clé
composite du schéma, et l'omettre laisserait une requête traverser les éditions.

L'arbre de prérequis n'est pas exposé. Il est modélisé depuis 07.1, n'a encore
aucun lecteur, et appartient à la remédiation de l'étape 12.

### Une fragilité des tests de 07.1 et 07.2, corrigée

Trois tests d'immuabilité et un test de contrainte publiaient une édition en
supposant qu'aucune ne l'était. Vrai sur une base fraîche, faux dès qu'une
édition est en vigueur — c'est-à-dire l'état normal depuis cette sous-étape. Ils
échouaient en local sans jamais échouer en CI, ce qui est le pire des deux.

`tests/support.py` porte le remède : les tests concernés écartent l'édition en
place pour leur durée et la remettent ensuite. Ils ne dépendent plus de l'état
de la machine et ne le détruisent pas.

## Fichiers créés

- `apps/api/app/referential/publication.py`
- `apps/api/app/api/v1/referential.py`
- `apps/api/app/schemas/referential.py`
- `apps/api/tests/support.py`
- `apps/api/tests/test_referential_publication.py`
- `apps/api/tests/test_referential_api.py`
- `docs/backend/api-referentiel.md`
- `steps/07_referentiel_competences/rapport_2026-08-15_1430_api_referentiel.md`

## Fichiers modifiés

- `apps/api/app/referential/__main__.py`, deux verbes au lieu d'un
- `apps/api/app/core/routing.py`
- `apps/api/tests/test_referential_import.py`, `test_referential_constraints.py`
- `docs/backend/import-referentiel.md`, `apps/api/seeds/referential/README.md`
- `steps/07_referentiel_competences/03_api_competences.md`
- `steps/ETAT.md`, `steps/PLANNING.md`, `steps/MANIFESTE.md`

Aucune migration : le schéma de 07.1 n'a pas bougé.

## Commandes exécutées

```
docker compose up -d
docker compose exec -T api ruff format --check .
docker compose exec -T api ruff check .
docker compose exec -T api mypy app --ignore-missing-imports
docker compose exec -T api pytest -q
docker compose exec -T api python -m app.referential publish fictif-2026-01
curl sur /api/v1/referential/edition, /levels, /competencies
```

## Tests exécutés

37 tests dédiés : 8 sur la publication et 29 sur les routes, tous d'intégration
contre PostgreSQL réel, les seconds passant par l'API et de vraies sessions.
L'autorisation n'est éprouvée qu'en refusant réellement une requête sans cookie.

## Résultats des tests

```text
Ruff       : vert, format inclus
Mypy       : vert sur 32 fichiers
Pytest     : 255 tests réussis, dont 37 nouveaux
Commande   : publish sur un brouillon, mise en vigueur, code de retour 0
Commande   : publish rejoué, « déjà en vigueur », code de retour 0
Commande   : publish sur un code inconnu, code de retour 3
API vivante: sans session, 401 sur les quatre routes
API vivante: /edition rend fictif-2026-01, /levels rend les cinq niveaux en ordre
API vivante: /competencies?level=cm1&subject=math&page_size=2 rend 2 items, total 5
Tests      : l'édition remplacée est archivée, exactement une reste en vigueur
Tests      : une édition archivée n'est pas remise en vigueur
Tests      : un brouillon n'est jamais servi, même en présence d'une édition en vigueur
Tests      : trois pages de deux rendent cinq compétences distinctes
Tests      : page ou taille hors bornes, 422 ; code de filtre inconnu, page vide
Tests      : un Enfant lit les mêmes routes qu'un Parent
Tests      : aucune réponse ne contient de prérequis
```

## Critères d'acceptation

- [x] Lectures des niveaux, matières et compétences.
- [x] Filtres par niveau, matière et domaine, combinables.
- [x] Pagination plafonnée, ordre total, bornes refusées.
- [x] Autorisation validée : `401` sans session, Parent et Enfant admis.
- [x] Édition en vigueur seule servie, brouillon jamais exposé.
- [x] Publication d'une édition, avec archivage de la précédente.
- [x] Arbre de prérequis non exposé.
- [x] Formatage, lint, typage et tests verts.
- [x] Aucune donnée réelle, aucun secret.

## Décisions ou ADR

Les deux décisions ci-dessus ont été prises par le propriétaire, ainsi que celle
du verbe `publish` dédié, arbitrée à la fin de 07.2. Aucune ADR nouvelle :
ADR-004 décrit le schéma, et rien ici ne le contredit.

## Écarts par rapport au prompt

La commande d'import s'invoque désormais `python -m app.referential import
<fichier>` au lieu de `python -m app.referential <fichier>`, l'ajout du verbe
`publish` demandant de nommer les deux. Documentation et README mis à jour.

## Risques ou dette technique

- **Aucune lecture d'une édition archivée.** Les traces des étapes 10 à 12
  devront être relues dans le référentiel où elles ont été écrites ; il faudra
  alors décider qui peut lire une édition retirée.
- Aucun plafond de débit sur ces routes, comme sur le reste de l'API. Le
  référentiel complet tient en quelques requêtes pour un compte authentifié.
- Le comptage et la page sont deux requêtes ; à cette échelle, c'est sans objet.
- La publication n'est pas journalisée autrement que par la sortie de la
  commande. Savoir qui a publié quoi et quand relèvera de l'étape 15.

## Blocages

Aucun.

## Prochaines actions

1. Sous-étape 07.4, clôture de l'étape 07 : Pull Request unique portant 07.3 et
   la dette résorbée, contrôles distants, fusion vers `main`.

## Mise à jour appliquée à ETAT.md

Sous-étape 07.3 ajoutée, points ouverts et prochaine action mis à jour.

## Mise à jour appliquée à PLANNING.md

REF-03 passée à En revue.
