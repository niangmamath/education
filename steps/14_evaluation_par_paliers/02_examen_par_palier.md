# 14.2, Examen servi par palier

## Objectif

Servir l'examen d'entrée palier par palier au lieu de toutes les compétences
d'une classe en une fois, en réutilisant le contenu déjà écrit (les
`Activity` et `AuthoredQuestion` de `app/demo/examens.py`) sans le modifier —
seule la politique de service change.

## Prérequis

- 14.1 clôturée ;
- branche dédiée issue de `main` ;
- dépôt propre ;
- Docker et services requis opérationnels.

## Livrables

- `app/authored/service.py:questions_of` gagne un filtre optionnel
  `competency_codes`, même schéma de jointure que l'attribution déjà
  utilisée par `attempts/service.py`.
- `app/assessment/service.py` : `give_to(db, child)` perd le paramètre
  `parent_id` (dérivé de `child.parent_id`) ; sa vérification d'idempotence
  s'aligne sur `assign_activity` (`status IN ('assigned','in_progress')`
  plutôt que « déjà une ligne, point ») ; appelle `tiers.next_sitting` et ne
  crée une `Assignment` que si la liste n'est pas vide. `is_done` devient
  « rien à servir maintenant et rien en attente ».
- Les 4 sites d'appel dans `api/v1/children.py` mis à jour (perte de
  `parent_id`).
- Docstrings de `app/demo/examens.py` et `_examens()` corrigées : elles
  décrivaient un envoi de toutes les questions d'un coup, ce qui n'est plus
  la politique de service — le contenu ne change pas.
- Tests étendus : palier 1 servi, 100 % → palier 2 servi à la lecture
  suivante ; un échec ne redonne rien tant que la remédiation n'a pas
  confirmé la compétence.

## Hors périmètre

- toute modification des questions ou des `Activity` d'examen existantes ;
- le diagnostic (étape 14.3) ;
- le déclenchement depuis la route (étape 14.4).

## Contrôles

- état Git et diff propres ;
- formatage, lint, typage et tests ;
- migrations upgrade et downgrade si applicables (aucune attendue) ;
- inspection des réponses et absence de secrets ;
- revue indépendante avant commit.

## Statut

Terminé.
