# Rapport de réalisation

## Métadonnées

- Étape : 12, diagnostic et remédiation, travaux après clôture
- Sous-étape : DIA-05
- Date et heure : 16 août 2026, 16h00
- Agent : Claude Code
- ID du planning : DIA-05
- Branche : `feat/remediation-reglable`
- Commit ou pull request : Pull Request unique vers `main`
- Statut : Terminé

## Objectif

Corriger deux décisions de l'étape 12 que le propriétaire a infirmées à sa
clôture : l'absence d'assignation automatique, et le fait qu'une compétence dont
le prérequis est en lacune restait proposée.

## Ce que le propriétaire a corrigé

**Sur l'automatisation.** L'agent avait tranché qu'il n'y aurait aucune
assignation automatique, au motif qu'automatiser déciderait à la place d'un
adulte. Le propriétaire a infirmé :

> « Le système doit pouvoir faciliter la tâche au parent. Après avoir fait un
> diagnostic, il doit pouvoir lui proposer puis aviser le parent, mais tout ça
> doit être réglable par le parent : il peut décider de faire entièrement
> confiance et d'approuver que le système assigne directement. »

Ni « le système n'assigne jamais » ni « le système assigne toujours » : le parent
choisit, et le défaut reste prudent.

**Sur les prérequis.** L'agent recommandait la cause racine *puis* la compétence
qui en dépend. Le propriétaire a rappelé l'intention du produit :

> « Ne pas lui demander d'assurer une compétence alors que le vrai problème c'est
> une autre compétence prérequis : lui demander d'assurer des opérations
> mathématiques alors que le vrai problème c'est le comptage, lui demander de
> conjuguer alors qu'il peine à reconnaître les groupes de verbes. »

Il a également demandé de **pondérer le score par le nombre de tentatives**,
point ouvert que l'agent avait signalé sans le lever.

## Travaux réalisés

### Le réglage, porté par l'enfant

`auth_children.remediation_mode`, `proposed` ou `automatic`, migration
`0011_remediation_settings` réversible. Porté par l'**enfant et non par le
parent** : la confiance accordée à une automatisation dépend de la situation
d'un enfant, et une famille avec une enfant de six ans et une de onze répond
plausiblement différemment pour chacune. `proposed` est le défaut, donc un parent
qui n'ouvre jamais le réglage n'est jamais agi pour.

`PUT /api/v1/children/{id}/remediation-mode` pour le régler.

### Les deux chemins

`POST /api/v1/children/{id}/remediation` donne les propositions **sur la parole
du parent**, dans les deux modes : être d'accord avec elles ne doit pas obliger à
les ressaisir dans le formulaire d'affectation. C'est la moitié « faciliter la
tâche ».

En mode `automatic`, **une** activité est donnée à la clôture d'une tentative,
parce que c'est le moment où la lecture change. Une seule, jamais une liste :
remettre cinq réparations parce que cinq compétences ont glissé transformerait un
coup de main en punition. Et c'est celle que rien n'attend, donc le chemin
automatique travaille sur ce qui bloque exactement comme le manuel.

Le déclenchement est dans la **route** de clôture d'une tentative et non dans le
service : un service qui affecterait du travail comme effet de bord d'un « j'ai
fini » ferait deux choses à la fois, et une seule serait dans son nom. Pour la
même raison, aucune lecture n'affecte quoi que ce soit — un `GET` ne crée rien,
et c'est toute la raison d'être de la route d'application.

### Qui a décidé reste lisible

`assignments.origin`, `parent` ou `system`, posé par le serveur. Sans cette
colonne, un parent ne pourrait plus dire le lendemain ce qu'il a choisi de ce qui
a été fait en son nom. C'est aussi la trace sur laquelle s'appuiera le « puis
aviser le parent » demandé, dont la remise appartient à l'étape 14.

Le plafond d'activités en cours et l'interdiction du doublon s'appliquent aux
deux chemins sans exception : ces règles protègent l'enfant de la plateforme
exactement comme elles la protègent d'un geste malheureux d'un parent. Une
proposition écartée pour l'une de ces raisons est **nommée** dans la réponse
plutôt que forcée ou tue.

### Le report derrière le prérequis

Sixième règle publiée, `defer-behind-prerequisite` : tant qu'un prérequis est
lui-même en lacune, la compétence qui en dépend n'est **pas proposée du tout**.

La lacune reportée **reste affichée**, avec `blocked_by` et la phrase qui dit sur
quoi elle attend. Reporter ce qu'on fait travailler n'est pas cacher ce qu'on a
trouvé, et un parent qui voit une difficulté sans remédiation à côté doit savoir
que le silence est délibéré.

Les chaînes se règlent d'elles-mêmes : dans A ⟵ B ⟵ C toutes en lacune, seule A
est travaillée.

### Le score pondéré

Chaque compétence pèse son nombre de tentatives terminées. Une compétence
reprise dix fois pèse dix fois une compétence vue une seule. Le coût est écrit
plutôt que caché : ce qui a été le plus refait porte le plus de poids, et ce
n'est pas toujours ce qui compte le plus. Le total des tentatives voyage avec le
score, parce qu'une moyenne pondérée dont le dénominateur est caché ne peut pas
être vérifiée par qui on la montre.

## Fichiers créés

- `apps/api/alembic/versions/0011_remediation_settings.py`

## Fichiers modifiés

- `apps/api/app/models/identity.py`, `apps/api/app/models/assignment.py`
- `apps/api/app/assignments/service.py` : `origin` en paramètre du service
- `apps/api/app/diagnostic/rules.py`, `service.py`
- `apps/api/app/schemas/diagnostic.py`, `apps/api/app/schemas/assignment.py`
- `apps/api/app/api/v1/diagnostic.py`, `attempts.py`, `assignments.py`
- `apps/api/tests/test_diagnostic_rules.py`, `test_diagnostic_api.py`
- `docs/adr/ADR-015-diagnostic-explicable.md` : trois amendements datés
- `docs/backend/diagnostic-remediation.md`
- `steps/ETAT.md`, `steps/PLANNING.md`

## Commandes exécutées

Séquence complète du workflow d'API CI, depuis la machine.

## Résultats des tests

```text
Ruff       : vert, format inclus
Mypy       : vert sur 72 fichiers
Alembic    : 0011_remediation_settings (head), check vert, downgrade base et retour au head
Pytest     : 568 tests réussis, dont 24 ajoutés par cette correction
Tests      : une compétence dont le prérequis est en lacune n'est pas proposée
Tests      : la lacune reportée reste affichée, avec ce qu'elle attend
Tests      : réparer le prérequis libère la compétence qui en dépend
Tests      : une compétence reprise dix fois pèse dix fois celle vue une seule
Tests      : lire le diagnostic n'affecte rien
Tests      : le mode par défaut ne donne rien de lui-même
Tests      : le mode automatique donne une activité, et une seule
Tests      : le mode automatique donne le prérequis, pas ce qui en dépend
Tests      : ce que la plateforme donne se distingue de ce que le parent donne
Tests      : appliquer deux fois n'ajoute rien et le dit
Tests      : un enfant ne règle pas le mode et n'applique rien
Tests      : l'enfant d'une autre famille n'existe pas
```

## Critères d'acceptation

- [x] L'automatisation est un réglage du parent, avec un défaut prudent.
- [x] Ce que la plateforme fait au nom du parent reste distinguable.
- [x] Une compétence dont le prérequis est en lacune n'est pas proposée.
- [x] Le score est pondéré par le nombre de tentatives.
- [x] Migration réversible, séquence d'API CI verte, suite rejouée sur un schéma
      reconstruit depuis `base`.

## Décisions ou ADR

ADR-015 amendée par trois sections datées, chacune citant la correction du
propriétaire qui l'a motivée.

Une décision de conception a été prise sans arbitrage : le réglage est porté par
**l'enfant** et non par le parent. Signalée à la fin, comme les autres.

## Écarts par rapport au prompt

Aucun. Travaux menés après la clôture de l'étape, ce que les décisions finales
autorisent explicitement pour résorber ce qu'un rapport de clôture a consigné.

## Risques ou dette technique

- **Aucune notification.** Le « puis aviser le parent » demandé n'est pas livré :
  le mode automatique laisse une trace lisible, mais rien ne va encore chercher
  le parent. C'est l'étape 14, et la colonne `origin` est ce sur quoi elle
  s'appuiera.
- Le mode automatique donne au plus une activité par tentative terminée. Sur une
  série de tentatives, cela peut faire plusieurs activités en peu de temps ; le
  plafond d'activités en cours et l'interdiction du doublon restent les seules
  bornes. Un délai minimal entre deux assignations automatiques serait un réglage
  de plus, et il n'a pas été inventé sans demande.

## Blocages

Aucun.

## Prochaines actions

Étape 13, tableaux de bord.
