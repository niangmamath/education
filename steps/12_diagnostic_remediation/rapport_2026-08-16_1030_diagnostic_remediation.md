# Rapport de réalisation

## Métadonnées

- Étape : 12, diagnostic et remédiation
- Sous-étapes : 12.1, 12.2, 12.3 et 12.4
- Date et heure : 16 août 2026, 10h30
- Agent : Claude Code
- ID du planning : DIA-01 à DIA-04
- Branche : `feat/etape-12-diagnostic`
- Commit ou pull request : Pull Request unique vers `main`
- Statut : Terminé

## Objectif

Nommer une difficulté à partir de ce que la plateforme a déjà enregistré, dire
ce que plusieurs difficultés ont de commun, proposer par quoi commencer, et le
faire sans qu'aucune conclusion échappe à son explication.

## Prérequis vérifiés

- Étape 11 clôturée, Pull Requests #22, #23, #24 et #25 fusionnées, CI verte sur
  `main`, migration à `0010_xapi_statements`, 499 tests.
- Progrès de l'étape 11 relus : délibérément descriptifs, sans diagnostic.
- Les douze règles produit non négociables de `PROMPT_GENERAL.md` relues ; six
  d'entre elles contraignent directement cette étape.
- `DECISIONS_FINALES.md` relu : Quick Repairs de 3 à 7 minutes, score de santé
  académique explicable, détection de lacunes via arbre de compétences.

## État initial observé

La plateforme savait dire ce qu'un enfant avait fait et ce que chaque tentative
avait conclu. Elle ne disait nulle part qu'il y avait une difficulté, et ne
proposait rien. La boucle du MVP s'arrêtait juste avant « lacune détectée ».

## Travaux réalisés

### 12.1, règles de diagnostic

Cinq règles nommées, publiées par `GET /api/v1/diagnostic/rules`, toutes de
l'arithmétique sur des comptes. Aucun modèle, opaque ou non.

- `gap-not-mastered` et `gap-partial-persists` produisent une **lacune
  localisée**. **Une seule lecture intermédiaire n'est pas une difficulté** :
  c'est ce à quoi ressemble un apprentissage en chemin. Elle le devient si elle
  survit à une deuxième tentative terminée.
- **Une compétence jamais travaillée n'est pas une lacune.** Elle n'a aucune
  lecture ; la ranger sous « difficulté » ferait d'une absence une accusation.
- `general-gap-same-domain` regroupe au moins deux lacunes d'un même domaine.
  Les compétences qu'il nomme **restent listées une par une** : la règle produit
  dit que le regroupement ne supprime pas ce qu'il regroupe, et les deux listes
  voyagent côte à côte.
- `root-cause-prerequisite` propose une cause possible quand une compétence en
  lacune est prérequis d'une autre compétence en lacune. Seules les arêtes entre
  deux lacunes comptent : un prérequis acquis est une preuve **contre**
  l'hypothèse, un prérequis jamais travaillé n'est aucune preuve. `confirmed`
  est un champ, toujours `false`, plutôt qu'un sous-entendu.
- `health-weighted-outcomes` rend le score de santé académique.

Chaque conclusion porte la règle qui l'a produite, les comptes lus et une phrase
en français construite des mêmes valeurs.

### 12.2, moteur de remédiation

Une activité **publiée**, travaillant la compétence, durant **de 3 à 7 minutes**.
Hors de cette bande elle n'est pas proposée, si bien assortie soit-elle :
proposer vingt minutes comme réparation rapide rendrait la promesse fausse.

Une seule activité par compétence — en proposer trois laisserait croire que la
plateforme sait laquelle est la meilleure —, **causes racines d'abord**, parce
que commencer par ce qui est dessous est tout l'intérêt d'avoir cherché.

Jamais proposée d'abord ; sinon déjà terminée, proposée quand même et
**signalée** par `already_done`, parce que la refaire est une seconde passe et
que le parent doit le savoir ; jamais celle qui l'attend déjà.

Chaque recommandation **nomme sa preuve finale**, la lecture de la tentative par
les règles de l'étape 10. Rien n'est marqué comme réparé ici.

### 12.3, API du diagnostic

Trois routes, et le partage entre les deux premières est la conception de
l'étape plutôt qu'un détail.

- `GET /api/v1/children/{child_id}/diagnostic`, Parent : lacunes, regroupements,
  hypothèses, score et ses termes, recommandations.
- `GET /api/v1/me/next-steps`, Élève : trois activités courtes, et rien d'autre.
- `GET /api/v1/diagnostic/rules`, toute session authentifiée.

Le même moteur produit les deux premières, et la différence est **ce qui
traverse**. Une enfant voit une activité et sa durée ; ni le score, ni les
lacunes, ni la règle qui a nommé une difficulté. Ce n'est pas du secret sur son
propre travail — ses tentatives, ses résultats et ses progrès restent à sa
disposition — mais une liste de réparations remise à une enfant *comme un
diagnostic* est un jugement auquel elle n'a aucun moyen de répondre.

### Le score de santé académique, et la règle qu'il devait ne pas casser

Le produit demande un score ; une règle non négociable dit qu'une note ne
remplace jamais une compétence. Les deux tiennent ensemble par trois propriétés,
et non par un compromis : le score apparaît **une fois pour un enfant**, à côté
de la lecture complète par compétence qu'il résume et jamais à la place de l'une
d'elles ; il est calculé sur ce que cette enfant a travaillé et **sur rien
d'autre**, ni sur le programme ni contre d'autres enfants ; chacun de ses termes
voyage avec lui, donc il se démonte.

**Rien d'observé ne rend aucun score**, et il n'existe pas de zéro pour cela :
zéro dirait que le travail s'est mal passé, alors qu'il n'a pas eu lieu.

### Rien n'est stocké, et c'est ce qui rend une règle vraie

Aucune table, aucune migration : le diagnostic se calcule à chaque lecture, à
partir des progrès de l'étape 11, eux-mêmes sommés des résultats de l'étape 10.
Trois couches, aucune ne rejugeant celle du dessous.

C'est surtout ce qui rend vraie **par construction** la règle « une cause racine
reste une hypothèse jusqu'à la réévaluation » : l'hypothèse est recalculée à
chaque lecture, donc une réévaluation la change à l'instant où elle arrive.
Aucune tâche de fond, rien à invalider. Un test l'éprouve en réparant la
compétence sous-jacente et en constatant que l'hypothèse disparaît sans que rien
n'ait été rafraîchi.

## Fichiers créés

- `apps/api/app/diagnostic/__init__.py`, `rules.py`, `remediation.py`,
  `service.py`
- `apps/api/app/schemas/diagnostic.py`
- `apps/api/app/api/v1/diagnostic.py`
- `apps/api/tests/test_diagnostic_rules.py`, `test_diagnostic_api.py`
- `docs/adr/ADR-015-diagnostic-explicable.md`
- `docs/backend/diagnostic-remediation.md`

## Fichiers modifiés

- `apps/api/app/core/routing.py`
- `docs/architecture/decision-register.md` : ADR-015, statistiques, date
- `docs/backend/progres.md` : le renvoi vers l'étape 12 devenu réel
- `steps/ETAT.md`, `steps/PLANNING.md`, les quatre fiches de l'étape

## Commandes exécutées

Séquence du workflow d'API CI, jouée depuis la machine et dans le conteneur :

```
ruff format --check .
ruff check .
mypy app
alembic upgrade head
alembic check
alembic downgrade base
alembic upgrade head
pytest -q
```

## Tests exécutés

- 45 tests nouveaux : 16 sur les règles hors base, 29 sur l'API avec une édition
  du référentiel réellement en vigueur.
- Les lacunes sont produites par le chemin long — activité donnée, commencée,
  répondue, terminée — pour que ce qui est diagnostiqué soit ce que la
  plateforme a enregistré, et non une ligne insérée pour faire passer un test.

## Résultats des tests

```text
Ruff       : vert, format inclus
Mypy       : vert sur 72 fichiers
Alembic    : 0010_xapi_statements (head), aucune migration ajoutée par l'étape
Pytest     : 544 tests réussis, dont 45 pour l'étape 12
Tests      : une compétence jamais travaillée n'est jamais une lacune
Tests      : une seule lecture intermédiaire n'est pas une lacune, deux le sont
Tests      : les lacunes regroupées restent listées une par une
Tests      : une lacune seule dans un domaine ne fait pas une lacune générale
Tests      : un prérequis acquis n'explique rien
Tests      : une cause racine n'est jamais marquée comme établie
Tests      : une activité de vingt minutes n'est jamais une Quick Repair
Tests      : la cause racine est recommandée avant ce qu'elle explique
Tests      : une activité déjà en attente n'est pas reproposée
Tests      : une activité déjà faite est reproposée et signalée comme telle
Tests      : rien d'observé ne rend aucun score
Tests      : le score porte chacun de ses termes et ne compare à personne
Tests      : l'Élève ne reçoit ni score, ni lacune, ni code de règle
Tests      : deux lectures du diagnostic rendent exactement la même chose
Tests      : réparer le prérequis fait disparaître l'hypothèse sans rafraîchissement
```

## Critères d'acceptation

- [x] Règles de maîtrise et de difficulté explicables, sans modèle opaque, et
      publiées.
- [x] Recommandation d'activité à partir des compétences et des contenus
      disponibles, dans la bande de durée du produit.
- [x] Diagnostics au Parent, prochaines actions à l'Élève, par deux routes
      distinctes.
- [x] Ruff, Mypy et Pytest verts dans l'ordre du workflow d'API CI.
- [x] Contrôles d'autorisation et d'isolation éprouvés par des tests dédiés.
- [x] Aucune migration : l'étape ne change pas le schéma, et c'est une décision
      consignée plutôt qu'un oubli.
- [x] Une seule Pull Request pour toute l'étape.

## Décisions ou ADR

ADR-015, acceptée, qui consigne les décisions prises sans arbitrage : les seuils
publiés, l'absence de stockage, la façon dont le score coexiste avec la règle sur
les notes, la bande de durée des Quick Repairs, et le partage entre ce que voit
le Parent et ce que voit l'Élève.

## Écarts par rapport au prompt

Aucun sur le périmètre. Le web n'a pas été modifié : il reste le prototype de
l'étape 05, et l'afficher est l'étape 13.

## Risques ou dette technique

- **Aucune assignation automatique.** Une recommandation reste une proposition,
  et la donner reste un geste du parent. C'est délibéré — automatiser déciderait
  à la place d'un adulte — mais cela veut dire que la boucle du MVP demande
  encore une action humaine entre la recommandation et l'activité.
- **Le score suppose que les compétences observées se valent.** Une compétence
  travaillée une fois pèse autant qu'une travaillée dix fois. Pondérer par le
  nombre de tentatives donnerait plus de poids à ce qui a été le plus refait,
  ce qui n'est pas la même chose que ce qui compte le plus. Laissé simple et
  écrit ici plutôt qu'arbitré en silence.
- **Le calcul à la lecture** coûte quelques requêtes par appel. Sans effet aux
  volumes d'une famille ; à revoir si les tableaux de bord de l'étape 13
  demandent un cache, comme déjà noté dans ADR-014.
- Le cache de pytest est recréé par `root` dès que la suite tourne dans le
  conteneur, ce qui fait un avertissement lors de l'exécution suivante sur la
  machine. Cosmétique, sans effet sur les résultats ni sur la CI.

## Blocages

Aucun.

## Prochaines actions

Étape 13, tableaux de bord. C'est là que le web appelle l'API pour la première
fois, que le `postMessage` de `play.html` trouve enfin son destinataire côté
client, et que la boucle du MVP devient visible de bout en bout.

## Mise à jour appliquée à ETAT.md

Section « Étape 12, diagnostic et remédiation, clôturée », résultats techniques,
prochaine action.

## Mise à jour appliquée à PLANNING.md

Phase 8 créée, DIA-01 à DIA-04 à « Terminé » avec leurs preuves ; prochaine
tâche pointée sur l'étape 13.
