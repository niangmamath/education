# Rapport de réalisation

## Métadonnées

- Étape : 07, référentiel de compétences
- Sous-étape : 07.1, référentiel scolaire
- Date et heure : 14 août 2026, 17h30
- Agent : Claude Code
- ID du planning : REF-01
- Branche : `feat/referentiel-competences`
- Commit ou pull request : Pull Request vers `main`
- Statut : Terminé

## Objectif

Modéliser niveaux, matières, domaines et compétences avec des identifiants stables
et les contraintes qui rendent le référentiel cohérent.

## Prérequis vérifiés

- Étape 06 clôturée et fusionnée dans `main`, dette résorbée.
- Branche dédiée issue de `main` à jour, dépôt propre après le nettoyage.
- Services Docker sains, migration à `0003` avant de commencer.
- ADR-003, ADR-004 et `DECISIONS_FINALES.md` relus.

## État initial observé

Le backend ne portait que l'identité. Aucune table scolaire, aucun modèle de
compétence. ADR-004 esquissait une table `skills` unique auto-référencée, jamais
implémentée.

## Travaux réalisés

### Trois décisions soumises au propriétaire

1. **Quatre tables explicites** plutôt qu'un arbre générique auto-référencé. La
   fiche 07.1 nomme quatre concepts, et les lectures filtrées de 07.3 deviennent
   des jointures directes. Écart assumé avec l'esquisse d'ADR-004.
2. **Le versionnement porte sur une entité version**, avec les statuts `draft`,
   `published` et `archived`. Une seule version publiée à la fois.
3. **L'arbre de prérequis est modélisé maintenant**, l'étape 12 en dépendant,
   sans qu'aucune route ne l'expose avant l'heure.

### Modèle

`apps/api/app/models/referential.py` : `ReferentialVersion`, `Level`, `Subject`,
`Domain`, `Competency` et `CompetencyPrerequisite`.

L'étanchéité des versions est portée par le schéma et non par le code d'import :
chaque ligne fille répète le `version_id` de son parent et le référence par une
clé étrangère composite, les contraintes `UNIQUE (id, version_id)` servant de
cible. Une compétence ne peut donc pas emprunter un domaine ou un niveau d'une
autre édition, et un prérequis ne peut pas franchir une frontière de version.

L'unicité du statut publié est un index unique partiel, `WHERE status =
'published'`, plutôt qu'une règle applicative.

## Fichiers créés

- `apps/api/app/models/referential.py`
- `apps/api/alembic/versions/0004_referential_competencies.py`
- `apps/api/tests/test_referential_models.py`
- `apps/api/tests/test_referential_constraints.py`
- `docs/backend/referentiel-competences.md`
- `steps/07_referentiel_competences/rapport_2026-08-14_1730_modeles_referentiel.md`

## Fichiers modifiés

- `apps/api/app/models/__init__.py`
- `steps/07_referentiel_competences/01_modeles_referentiel.md`
- `steps/ETAT.md`, `steps/PLANNING.md`, `steps/MANIFESTE.md`

Le dossier `steps/07_referentiel_competences/` rejoint le dépôt à l'ouverture de
son étape, comme le prescrit `ETAT.md`.

## Commandes exécutées

```
docker compose exec -T api alembic revision --autogenerate -m "..."
docker compose exec -T api ruff format --check .
docker compose exec -T api ruff check .
docker compose exec -T api mypy app --ignore-missing-imports
docker compose exec -T api alembic upgrade head
docker compose exec -T api alembic check
docker compose exec -T api alembic downgrade -1
docker compose exec -T api alembic upgrade head
docker compose exec -T api alembic downgrade base
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

## Tests exécutés

23 tests dédiés au référentiel, dont 16 d'intégration contre PostgreSQL réel,
écrits pour vérifier que les contraintes refusent effectivement, et non que le
code les déclare.

## Résultats des tests

```text
Alembic    : 0004_referential_competencies (head)
Alembic    : check vert, aucune dérive entre modèles et base
Alembic    : downgrade -1, downgrade base et retour au head validés
Ruff       : vert, format inclus
Mypy       : vert sur 24 fichiers
Pytest     : 164 tests réussis, dont 23 nouveaux
Contraintes: code identique accepté dans deux versions, refusé deux fois dans une
Contraintes: domaine ou niveau d'une autre version refusé par la clé composite
Contraintes: prérequis inter-versions refusé, auto-prérequis refusé, doublon refusé
Contraintes: deuxième version publiée refusée, brouillons et archives illimités
Contraintes: suppression d'une version emportant niveaux, domaines et compétences
```

## Critères d'acceptation

- [x] Niveaux, matières, domaines et compétences modélisés.
- [x] Identifiants métier stables, uniques dans leur version.
- [x] Référentiel versionné, une seule version publiée à la fois.
- [x] Arbre de prérequis modélisé, sans exposition.
- [x] Migration réversible, `alembic check` sans dérive.
- [x] Formatage, lint, typage et tests verts.
- [x] Aucune donnée réelle, aucune donnée du tout à ce stade.

## Décisions ou ADR

Les trois décisions ci-dessus ont été prises par le propriétaire. ADR-004 garde
son esquisse `skills`, devenue caduque sur ce point ; l'écart est consigné ici et
dans `docs/backend/referentiel-competences.md`. Un amendement d'ADR-004 sera à
faire si l'esquisse doit cesser d'induire en erreur.

## Écarts par rapport au prompt

Aucun. Les commits, la Pull Request et la fusion relèvent de l'autorisation
permanente inscrite dans `AGENTS.md` et `steps/PROMPT_GENERAL.md`.

## Risques ou dette technique

- ADR-004 décrit encore une table `skills` unique, qui n'existe pas.
- La détection des cycles dans l'arbre de prérequis dépasse ce qu'une contrainte
  SQL exprime ; elle appartient à la validation d'import de 07.2.
- Les quatre relations qui partagent la colonne `version_id` portent une
  déclaration `overlaps` explicite ; c'est le remède documenté par SQLAlchemy,
  mais il demande de la vigilance si ces relations changent.

## Blocages

Aucun.

## Prochaines actions

1. Sous-étape 07.2, import contrôlé et idempotent du référentiel fictif.
2. Amendement éventuel d'ADR-004 sur la table `skills`.

## Mise à jour appliquée à ETAT.md

Section « Étape 07 » ajoutée avec 07.1 en revue, organisation des étapes corrigée,
prochaine action mise à jour.

## Mise à jour appliquée à PLANNING.md

Phase 3 ajoutée avec les tâches REF-01 à REF-04, REF-01 terminée.
