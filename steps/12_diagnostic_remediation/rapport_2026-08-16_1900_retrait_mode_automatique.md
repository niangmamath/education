# Rapport de réalisation

## Métadonnées

- Étape : 12, diagnostic et remédiation, travaux après clôture
- Sous-étape : DIA-05, second temps
- Date et heure : 16 août 2026, 19h00
- Agent : Claude Code
- ID du planning : DIA-05
- Branche : `chore/retirer-mode-automatique`
- Commit ou pull request : Pull Request unique vers `main`
- Statut : Terminé

## Objectif

Retirer le mode d'assignation automatique, que le propriétaire a abandonné après
l'avoir demandé, et consigner l'arbitrage qu'il a rendu au passage sur la place
du réglage.

## Ce que le propriétaire a dit

> « Non, le réglage doit être porté par le parent pour cette version, mais si le
> ou les parents ont plusieurs enfants ils peuvent faire différents réglages
> selon l'enfant. D'accord, on abandonne le mode automatique pour le moment, on
> reste comme avant. »

Deux choses, et la seconde emporte la première pour cette version : le réglage
aurait dû appartenir au parent et non au profil de l'enfant, et le mode
automatique est abandonné.

## Ce qui est retiré

Migration `0012_drop_automatic_remediation`, réversible.

- `auth_children.remediation_mode` et sa contrainte.
- `assignments.origin` et sa contrainte.
- `PUT /children/{id}/remediation-mode`.
- L'assignation à la clôture d'une tentative.

**Les colonnes sont supprimées plutôt que laissées « pour plus tard ».** Une
colonne à valeur unique se lit comme une distinction que le code ferait, et il ne
la fait pas ; la garder coûterait un malentendu à chaque rencontre, et la ramener
coûte une migration. Le `downgrade` les remet, donc rien n'est perdu.

## Ce qui reste, et pourquoi

Le propriétaire n'a retiré ni le « faciliter la tâche au parent », ni les deux
autres corrections du même jour.

- `POST /api/v1/children/{id}/remediation` **donne les propositions sur la parole
  du parent**. Ce que la route retire est la ressaisie, pas la décision : être
  d'accord avec les propositions ne doit pas obliger à les recopier une à une
  dans le formulaire d'affectation.
- Le report derrière le prérequis, sixième règle publiée.
- Le score pondéré par le nombre de tentatives.

**La plateforme n'assigne plus rien d'elle-même** : ni à la lecture d'un
diagnostic, ni à la clôture d'une tentative.

## La leçon de conception, consignée

Le sujet a fait un aller-retour complet — refus, puis réglage, puis abandon — et
ce qu'il laisse mérite d'être écrit : la question n'était pas « automatiser ou
refuser », mais **qu'est-ce qui relève de l'ergonomie et qu'est-ce qui relève de
la décision**. Retirer une ressaisie est de l'ergonomie ; choisir ce qu'un enfant
fera est une décision. La plateforme fait la première et laisse la seconde.

L'arbitrage sur la place du réglage est consigné dans ADR-015 pour le jour où
l'automatisation reviendrait : il appartiendra au **parent**, avec une valeur par
enfant.

## Fichiers créés

- `apps/api/alembic/versions/0012_drop_automatic_remediation.py`
- Ce rapport.

## Fichiers modifiés

- `apps/api/app/models/identity.py`, `apps/api/app/models/assignment.py`
- `apps/api/app/assignments/service.py`, `apps/api/app/schemas/assignment.py`
- `apps/api/app/diagnostic/service.py`, `apps/api/app/schemas/diagnostic.py`
- `apps/api/app/api/v1/diagnostic.py`, `attempts.py`, `assignments.py`
- `apps/api/tests/test_diagnostic_api.py`
- `docs/adr/ADR-015-diagnostic-explicable.md`, section réécrite
- `docs/backend/diagnostic-remediation.md`
- `steps/ETAT.md`, `steps/PLANNING.md`

## Résultats des tests

```text
Ruff       : vert, format inclus
Mypy       : vert sur 72 fichiers
Alembic    : 0012_drop_automatic_remediation (head), check vert, downgrade base et retour au head
Pytest     : 559 tests réussis
Tests      : terminer une tentative n'affecte rien
Tests      : lire le diagnostic n'affecte rien
Tests      : le parent donne les propositions en un appel
Tests      : appliquer deux fois n'ajoute rien et le dit
Tests      : un enfant n'applique rien
Tests      : une compétence dont le prérequis est en lacune n'est pas proposée
Tests      : la lacune reportée reste affichée, avec ce qu'elle attend
Tests      : une compétence reprise dix fois pèse dix fois celle vue une seule
```

## Critères d'acceptation

- [x] Le mode automatique n'existe plus, colonnes comprises.
- [x] La plateforme n'assigne rien d'elle-même.
- [x] Ce qui avait été demandé et non retiré est conservé.
- [x] Migration réversible, séquence d'API CI verte, suite rejouée sur un schéma
      reconstruit depuis `base`.

## Décisions ou ADR

ADR-015, section sur l'automatisation entièrement réécrite : elle raconte
l'aller-retour plutôt que de le masquer, dit l'état applicable, et consigne où
vivra le réglage s'il revient.

Une décision prise sans arbitrage : **la route d'application est conservée**. Le
propriétaire a dit « on reste comme avant », ce qui pouvait aussi se lire comme
un retour complet à l'état antérieur à la Pull Request #28. La route a été gardée
parce qu'elle ne décide rien à la place de personne et qu'elle répond au
« faciliter la tâche au parent » demandé le même jour et non retiré. À confirmer.

## Écarts par rapport au prompt

Aucun.

## Risques ou dette technique

Aucune nouvelle. Le retrait laisse le code dans l'état que le propriétaire a
demandé, sans reliquat.

## Blocages

Aucun.

## Prochaines actions

Étape 13, tableaux de bord.
