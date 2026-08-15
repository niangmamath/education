# Rapport de réalisation

## Métadonnées

- Étape : 09, affectations et parcours
- Sous-étapes : 09.1, 09.2, 09.3 et 09.4
- Date et heure : 15 août 2026, 16h15
- Agent : Claude Code
- ID du planning : AFF-01 à AFF-04
- Branche : `feat/etape-09-affectations`
- Commit ou pull request : Pull Request unique vers `main`
- Statut : Terminé

## Objectif

Permettre à un Parent d'affecter une activité du catalogue à son Élève, et à
l'Élève de la commencer puis de la terminer, sans qu'aucune famille ne puisse
voir ni toucher celle d'une autre.

## Prérequis vérifiés

- Étape 08 clôturée et fusionnée, Pull Request #15, commit `b41284b`.
- ADR-013 confirmée par le propriétaire.
- Branche issue de `main` à jour, cinq services Docker sains.
- `DECISIONS_FINALES.md` relu, en particulier la règle selon laquelle une
  observation nouvelle n'écrase jamais l'historique.

## État initial observé

Le catalogue existait et se lisait, mais rien ne reliait une activité à une
personne. Les profils Enfant de l'étape 06 et les activités de l'étape 08
vivaient côte à côte sans se rencontrer.

## Travaux réalisés

### Décisions prises par l'agent

L'enchaînement des sous-étapes sans arrêt étant la consigne, trois décisions ont
été tranchées et sont consignées ici plutôt que soumises :

1. **Redonner une activité crée une seconde ligne**, plutôt que de rouvrir la
   première. « Elle l'a faite deux fois » et « elle l'a faite une fois » sont
   deux faits différents, et la règle du projet interdit qu'une observation
   nouvelle écrase l'historique. Un index unique **partiel**, sur les seuls états
   ouverts, interdit le doublon simultané sans interdire la répétition.
2. **Annuler n'efface pas.** La ligne reste, datée : un enfant à qui l'on a donné
   puis retiré quelque chose n'a pas la même histoire qu'un enfant à qui l'on n'a
   rien donné.
3. **L'Élève peut marquer une activité terminée.** Terminer n'est pas réussir :
   rien ici ne touche à une compétence, conformément à la règle selon laquelle
   ouvrir un contenu ne valide jamais une compétence à lui seul. La preuve
   appartient aux tentatives de l'étape 10.

Aucune ADR : ces décisions relèvent du comportement d'une table, non de
l'architecture, et le rapport suffit à les porter.

### 09.1, le modèle

Table `assignments`, migration `0006_assignments` réversible.

La clé étrangère vers l'activité **restreint** au lieu de cascader : une activité
donnée à quelqu'un fait partie de son histoire et ne peut plus être supprimée.
Trois contraintes exigent qu'un statut porte sa date — un statut sans son moment
serait une affirmation sans date derrière elle.

### 09.2 et 09.3, les deux espaces

Toute la logique vit dans `app/assignments/service.py`, parce que l'espace Parent
et l'espace Élève agissent sur les mêmes lignes par les deux bouts et ne doivent
pas diverger.

**Les deux espaces ne se mélangent pas** : une route Parent exige
`CurrentParent`, une route Élève exige `CurrentChild`, et aucune n'accepte
l'autre. Une route qui prendrait les deux serait à un oubli de contrôle près de
laisser un enfant se donner du travail, ou un parent terminer à sa place.

**L'isolation est dans la clause `WHERE`**, comme à l'étape 06. Une affectation
d'une autre famille répond exactement comme une affectation inexistante.

## Fichiers créés

- `apps/api/app/models/assignment.py`
- `apps/api/alembic/versions/0006_assignments.py`
- `apps/api/app/assignments/{__init__,service}.py`
- `apps/api/app/api/v1/assignments.py`, `apps/api/app/schemas/assignment.py`
- `apps/api/tests/test_assignments_api.py`
- `docs/backend/affectations.md`

## Fichiers modifiés

- `apps/api/app/models/__init__.py`, `apps/api/app/core/routing.py`
- `docs/adr/ADR-013-catalogue-lie-par-code.md`, confirmation du propriétaire
- `steps/ETAT.md`, `steps/PLANNING.md`, `steps/MANIFESTE.md`, fiches 09.1 à 09.4

## Commandes exécutées

```
docker compose exec -T api alembic revision --autogenerate -m "Create assignments"
docker compose exec -T api alembic upgrade head ; alembic check
docker compose exec -T api alembic downgrade base ; alembic upgrade head
docker compose exec -T api ruff format --check . ; ruff check .
docker compose exec -T api mypy app --ignore-missing-imports
docker compose exec -T api pytest -q
```

## Tests exécutés

25 tests dédiés, tous d'intégration à travers l'API avec de vraies sessions. Une
seconde famille complète est construite et sert à frapper à chaque porte :
l'isolation n'est éprouvée qu'en essayant réellement de la franchir.

## Résultats des tests

```text
Ruff       : vert, format inclus
Mypy       : vert sur 46 fichiers
Alembic    : 0006_assignments (head), check vert, aucune dérive
Alembic    : downgrade base puis retour au head validés
Pytest     : 361 tests réussis, dont 25 nouveaux
Tests      : affectation d'une autre famille refusée en 404, comme une inexistante
Tests      : parent d'une autre famille ne peut ni voir, ni annuler
Tests      : enfant d'une autre famille ne peut pas commencer
Tests      : enfant tentant de s'affecter une activité, 403
Tests      : parent tentant de terminer à la place de l'enfant, 403
Tests      : activité en brouillon refusée comme une activité inexistante
Tests      : même activité due deux fois à la fois refusée en 409
Tests      : redonnée après achèvement, seconde ligne créée
Tests      : terminer avant de commencer, rouvrir une terminée, reprendre une
             annulée, annuler une terminée : 409 dans les quatre cas
Tests      : annulation conservant la ligne et sa date
Tests      : vue Élève ne contenant ni identifiant ni pseudonyme d'enfant
```

## Critères d'acceptation

- [x] Affectation d'une activité à un Élève par un Parent autorisé.
- [x] Création, liste et annulation avec contrôle d'appartenance familiale.
- [x] Liste des activités disponibles, commencées et terminées du seul Élève
      connecté.
- [x] Transitions d'état validées, aucun retour en arrière possible.
- [x] Isolation validée en essayant réellement de la franchir.
- [x] Migration réversible, `alembic check` sans dérive.
- [x] Formatage, lint, typage et tests verts.
- [x] Aucune donnée réelle, aucun secret.

## Décisions ou ADR

Les trois décisions ci-dessus, prises par l'agent et consignées ici. ADR-013 a
par ailleurs été marquée confirmée par le propriétaire.

## Écarts par rapport au prompt

Un seul rapport couvre les quatre sous-étapes, comme à l'étape 08 et pour les
mêmes raisons : enchaînement demandé et travail plus économe. Le détail est dans
les messages de commit.

## Risques ou dette technique

- **Aucune échéance ni ordre de parcours**, alors que l'étape s'intitule
  « affectations et parcours ». Une affectation est donnée, pas planifiée ;
  ordonner un parcours demandera de décider ce qu'il advient d'une activité
  sautée.
- Aucune recommandation automatique : le moteur déterministe est l'étape 12, et
  ici c'est le parent qui choisit.
- Rien ne plafonne le nombre d'affectations ouvertes pour un enfant.
- Le lecteur H5P manque toujours : une activité peut être donnée et commencée
  sans que le contenu puisse être joué. Cette dette, ouverte en 08, devient
  visible ici.
- Les pages web restent les maquettes de l'étape 05 ; rien n'affiche encore une
  affectation.

## Blocages

Aucun.

## Prochaines actions

1. Ouvrir l'étape 10, tentatives et résultats, qui donnera enfin une preuve à ce
   qu'une activité terminée signifie.
2. Consigner la clôture distante de l'étape 09 au premier commit de l'étape 10.

## Mise à jour appliquée à ETAT.md

Étape 09 consignée et marquée clôturée, résultats techniques et points ouverts
ajoutés, prochaine action mise à jour.

## Mise à jour appliquée à PLANNING.md

Phase 5 ajoutée, AFF-01 à AFF-04 terminées.
