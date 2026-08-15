# Rapport de réalisation

## Métadonnées

- Étape : 10, tentatives et résultats
- Sous-étapes : 10.1, 10.2, 10.3 et 10.4
- Date et heure : 15 août 2026, 18h20
- Agent : Claude Code
- ID du planning : TEN-01 à TEN-04
- Branche : `feat/etape-10-tentatives`
- Commit ou pull request : Pull Request unique vers `main`
- Statut : Terminé

## Objectif

Enregistrer ce qu'un enfant a fait, et en lire une conclusion par des règles
explicites rattachées aux compétences, sans fabriquer de score.

## Prérequis vérifiés

- Runtime de contenu fusionné, Pull Request #18, commit `3a0d46c` : une
  tentative a désormais un contenu réel derrière elle.
- Ordre des étapes rétabli, l'étape 10 précédant la 11.
- Cinq services Docker sains, migration à `0007`.
- `DECISIONS_FINALES.md` relu, en particulier les trois règles produit qui
  gouvernent cette étape.

## État initial observé

Une activité pouvait être donnée, commencée, jouée et marquée terminée, sans que
rien n'enregistre ce qui s'y était passé. « Terminée » ne voulait rien dire de
plus que « la case a été cochée ».

## Travaux réalisés

### La ligne qui structure l'étape

Les **faits** d'un côté, la **lecture** de l'autre, et deux tables distinctes
plutôt qu'une convention. Une tentative et une réponse sont des faits ; un
résultat est une interprétation, rangé à part parce qu'il en est une.

C'est ce qui rend applicables, plutôt que simplement énoncées, deux règles du
projet : une note ne remplace jamais une compétence, et une lacune automatique
est une candidate explicable. On peut relire, recalculer ou contester une
interprétation sans toucher à ce qui a été observé.

### 10.1, le modèle

`attempts`, `attempt_responses`, `attempt_results` ; migration `0008_attempts`
réversible.

Aucune colonne de score, nulle part. Un résultat porte trois mots — acquise, en
cours, non acquise — et les comptes dont ils viennent.

Les réponses ne portent **aucune clé unique sur la question** : répondre deux
fois est deux faits, et le second n'efface pas le premier.

### 10.2, les routes, et l'idempotence

Commencer deux fois rend la même tentative. **C'est la base qui le garantit** :
un index unique partiel n'admet qu'une tentative en cours par affectation, donc
deux requêtes simultanées ne peuvent pas gagner toutes les deux, et le perdant
est renseigné sur le gagnant au lieu d'échouer. La route répond `201` quand elle
a créé et `200` quand elle a rendu l'existante, sans qu'aucune ne soit une
erreur.

Terminer la tentative termine l'affectation : les deux ne doivent pas pouvoir se
contredire sur le fait que le travail a été fait. Annuler une affectation
abandonne la tentative en cours **sans l'effacer** : l'enfant avait bien
commencé, et cela reste vrai.

### 10.3, les règles

Trois règles nommées, de l'arithmétique sur des comptes. La maîtrise exige tout,
parce que ce sont des activités courtes sur un point précis ; la bande
intermédiaire existe pour que « presque » ne soit pas rangé avec « pas du tout »,
ce qui dirait à un parent quelque chose de faux.

L'API rend la phrase explicative, construite à partir des mêmes valeurs que
celles qui ont été stockées : elle ne peut donc pas diverger de ce qu'elle
explique.

**Aucune preuve ne conclut rien.** Un contenu qui ne dit pas si une réponse était
juste n'y est pas contraint, ces réponses ne sont pas comptées, et si aucune n'a
été évaluée, aucun résultat n'est écrit. Il n'existe volontairement pas de statut
pour cela : ranger un silence sous « non acquise » en ferait une accusation, sous
« en cours » une affirmation que quelque chose a été à moitié fait.

### Deux défauts trouvés en chemin

- **Les résultats n'apparaissaient pas dans la réponse.** Ils étaient bien
  écrits, mais la collection de la tentative avait été chargée vide avant leur
  création ; ils sont désormais rattachés par la relation et non par une clé
  étrangère posée derrière son dos.
- **Deux tests supposaient qu'aucune autre activité ne citait la même
  compétence.** Ils tiraient un code fixe. Les codes de compétence des tests sont
  maintenant tirés par exécution, ce qui les rend indépendants de ce que la base
  contient par ailleurs. C'est la troisième fois que cette famille de fragilité
  apparaît, et elle est traitée à la racine cette fois.

## Fichiers créés

- `apps/api/app/models/attempt.py`
- `apps/api/alembic/versions/0008_attempts.py`
- `apps/api/app/attempts/{__init__,rules,service}.py`
- `apps/api/app/api/v1/attempts.py`, `apps/api/app/schemas/attempt.py`
- `apps/api/tests/test_attempt_rules.py`, `apps/api/tests/test_attempts_api.py`
- `docs/backend/tentatives-resultats.md`

## Fichiers modifiés

- `apps/api/app/models/__init__.py`, `apps/api/app/core/routing.py`
- `apps/api/app/assignments/service.py`, abandon à l'annulation
- `apps/api/tests/test_catalog_api.py`, codes de compétence tirés par exécution
- `steps/ETAT.md`, `steps/PLANNING.md`, `steps/MANIFESTE.md`, fiches 10.1 à 10.4

## Commandes exécutées

```
docker compose exec -T api alembic revision --autogenerate -m "Create attempts..."
docker compose exec -T api alembic upgrade head ; alembic check
docker compose exec -T api alembic downgrade base ; alembic upgrade head
docker compose exec -T api ruff format --check . ; ruff check .
docker compose exec -T api mypy app --ignore-missing-imports
docker compose exec -T api pytest -q
```

## Tests exécutés

36 tests dédiés : 15 sur les règles seules, sans base ni API, parce que c'est la
partie qu'un parent pourra un jour contester et qu'elle doit être lisible isolée ;
21 d'intégration à travers l'API, dont l'isolation éprouvée en construisant une
seconde famille et en frappant à chaque porte.

## Résultats des tests

```text
Ruff       : vert, format inclus
Mypy       : vert sur 56 fichiers
Alembic    : 0008_attempts (head), check vert, aucune dérive
Alembic    : downgrade base puis retour au head validés
Pytest     : 434 tests réussis, dont 36 nouveaux
Tests      : dix demandes de démarrage laissent une seule tentative
Tests      : reprendre rend 200 et la même tentative, créer rend 201
Tests      : activité non commencée n'accepte aucune tentative, 409
Tests      : deux réponses à la même question, les deux conservées
Tests      : la lecture prend la dernière réponse par question
Tests      : réponse non évaluée par le contenu non comptée
Tests      : aucune réponse évaluée, aucun résultat écrit
Tests      : chaque résultat nomme sa règle et porte ses comptes
Tests      : aucun résultat ne porte de score ni de pourcentage
Tests      : terminer deux fois ne recalcule rien
Tests      : terminer la tentative termine l'affectation
Tests      : annuler l'affectation abandonne la tentative sans l'effacer
Tests      : tentative d'une autre famille en 404, parent en 403
```

## Critères d'acceptation

- [x] Tentatives, réponses et statut de complétion modélisés, sans score.
- [x] Démarrage, reprise et achèvement idempotents.
- [x] Concurrence tranchée par la base et non par une lecture préalable.
- [x] Résultats calculés par des règles explicites, nommées et testées.
- [x] Résultats rattachés aux compétences, par leur code métier.
- [x] Autorisation et isolation validées en essayant de les franchir.
- [x] Migration réversible, `alembic check` sans dérive.
- [x] Formatage, lint, typage et tests verts.

## Décisions ou ADR

Aucune ADR : ces décisions portent sur le comportement de trois tables et de
trois règles, et le rapport avec la documentation suffit à les tenir. Les seuils
retenus — tout pour la maîtrise, la moitié pour la bande intermédiaire — sont
consignés dans `docs/backend/tentatives-resultats.md` et pinnés par des tests.

## Écarts par rapport au prompt

Un seul rapport couvre les quatre sous-étapes, comme aux étapes 08 et 09.

## Risques ou dette technique

- **Les règles s'appliquent à toutes les compétences d'une activité**, parce que
  H5P ne dit pas quelle question relève de quelle compétence. Une activité
  rattachée à deux compétences produit la même lecture pour les deux. La limite
  se lèvera quand les événements xAPI de l'étape 11 porteront de quoi distinguer
  les questions.
- Les réponses sont **déclarées par le client**. L'étape 11 les recevra du
  runtime lui-même, ce qui est autre chose, et il faudra décider ce qui prime.
- Aucun agrégat dans le temps : un résultat porte sur une tentative.
- Aucune lecture des résultats côté Parent au-delà de l'affectation ; les
  tableaux de bord sont l'étape 13.
- Les seuils sont figés dans le code. Les rendre configurables demanderait de
  décider qui peut les changer, ce qui n'est pas une question de cette étape.

## Blocages

Aucun.

## Prochaines actions

1. Étape 11, ingestion des événements xAPI, liaison de l'acteur pseudonyme,
   agrégation des progrès.
2. Consigner la clôture distante de l'étape 10 au premier commit de l'étape 11.

## Mise à jour appliquée à ETAT.md

Étape 10 consignée et marquée clôturée, résultats techniques et points ouverts
ajoutés.

## Mise à jour appliquée à PLANNING.md

TEN-01 à TEN-04 terminées.
