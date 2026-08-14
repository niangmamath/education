# Rapport de réalisation

## Métadonnées

- Étape : 07, référentiel de compétences
- Sous-étape : 07.2, import contrôlé
- Date et heure : 14 août 2026, 21h00
- Agent : Claude Code
- ID du planning : REF-02
- Branche : `feat/import-referentiel`
- Commit ou pull request : Pull Request vers `main`
- Statut : Terminé

## Objectif

Faire entrer une édition du référentiel dans la base par un import validé,
rejouable sans effet de bord, avec un rapport d'erreurs qui nomme la ligne
fautive du fichier.

## Prérequis vérifiés

- 07.1 fusionnée dans `main` par la Pull Request #9, ADR-004 amendée par la #10.
- Branche `feat/import-referentiel` issue de `main` à jour, commit `71776c7`.
- Docker Desktop n'était pas démarré au début de la session ; il a été lancé et
  les cinq services sont remontés sains avant le premier contrôle.
- Migration à `0004_referential_competencies` avant de commencer.
- `PROMPT_GENERAL.md`, `DECISIONS_FINALES.md`, `ETAT.md` et le rapport de 07.1
  relus.

## État initial observé

Le schéma du référentiel existait, entièrement vide : aucune ligne, aucun moyen
d'en écrire. La détection des cycles de prérequis avait été explicitement
renvoyée à cette sous-étape par le rapport de 07.1.

## Travaux réalisés

### Deux décisions soumises au propriétaire

1. **L'idempotence est une réconciliation de brouillon.** Le fichier décrit
   l'état voulu d'une édition. L'import crée la version en `draft` si elle
   n'existe pas, puis fait correspondre la base au fichier : créations, mises à
   jour, et suppression des lignes que le fichier ne mentionne plus. Rejouer le
   même fichier ne rapporte rien à faire. Une version `published` ou `archived`
   est immuable et l'import la refuse.
2. **L'import est une commande en ligne et non une route.** Une route
   d'administration demanderait un rôle Administrateur que le projet n'a pas et
   que l'étape 15 prévoit ; elle exposerait de surcroît un import de masse sur
   le réseau.

Les deux options recommandées ont été retenues.

### Le fichier et sa lecture

`app/referential/document.py` décrit la forme du fichier avec Pydantic. Le
fichier ne parle qu'en codes métier, jamais en identifiants de base, ce qui le
rend relisible et rejouable contre une base vide. **Une clé inconnue est refusée
et non ignorée** : un référentiel s'écrit à la main, et une clé mal orthographiée
silencieusement écartée est exactement la perte qu'un import ne doit pas couvrir.

### La validation

`app/referential/validation.py` vérifie tout avant la moindre écriture et rend
**toutes les erreurs en une seule passe**. Elle reprend délibérément des règles
que la base porte déjà : une `IntegrityError` ne dit pas quelle ligne du fichier
est fautive, et un fichier doit être refusé en entier plutôt qu'appliqué à
moitié.

Une vérification n'a aucun équivalent en base : **le cycle de prérequis**. `A`
requiert `B` qui requiert `A` forme deux lignes parfaitement légales prises
séparément. Le parcours est en profondeur, itératif pour ne pas dépendre de la
limite de récursion de Python, et une même boucle trouvée depuis plusieurs
départs n'est signalée qu'une fois. C'est la dette que le rapport de 07.1 avait
consignée ; elle est résorbée.

### La réconciliation

`app/referential/importer.py` ne valide rien et n'ouvre aucune transaction : il
réconcilie, le propriétaire de la transaction étant l'appelant. C'est ce qui
permet à l'essai à blanc de faire le travail entier, `flush` compris, donc
d'éprouver toutes les contraintes de la base, avant d'annuler. Un essai à blanc
qui annoncerait des changements que l'écriture ne saurait pas produire serait
pire que pas d'essai du tout.

L'identité d'une ligne entre le fichier et la base est son code métier. Déplacer
une compétence d'un domaine à un autre met à jour la ligne existante et lui
conserve son `id`, ce qui comptera pour les traces des étapes 10 à 12.

Les suppressions sont exécutées des feuilles vers la racine, alors que la base
cascaderait de toute façon : c'est ce qui rend les nombres du rapport honnêtes.

### La commande

`app/referential/__main__.py`. **L'essai à blanc est le comportement par
défaut**, parce qu'un import réécrit une édition entière, suppressions comprises.
Codes de retour : `0` réussite, `1` fichier illisible, `2` fichier refusé, `3`
version immuable, `4` refus de la base.

### Le référentiel fictif

`apps/api/seeds/referential/fictif-2026-01.json` : cinq niveaux, deux matières,
huit domaines, trente-neuf compétences et trente-six liens de prérequis
traversant les niveaux, pour que l'arbre de l'étape 12 ait de quoi se déployer.
Fichier **entièrement fictif**, plausible mais ne reproduisant aucun programme
officiel, ce que rappellent le README du dossier et la documentation.

## Fichiers créés

- `apps/api/app/referential/__init__.py`
- `apps/api/app/referential/document.py`
- `apps/api/app/referential/validation.py`
- `apps/api/app/referential/importer.py`
- `apps/api/app/referential/__main__.py`
- `apps/api/seeds/referential/fictif-2026-01.json`
- `apps/api/seeds/referential/README.md`
- `apps/api/tests/test_referential_document.py`
- `apps/api/tests/test_referential_validation.py`
- `apps/api/tests/test_referential_import.py`
- `docs/backend/import-referentiel.md`
- `steps/07_referentiel_competences/rapport_2026-08-14_2100_import_referentiel.md`

## Fichiers modifiés

- `apps/api/app/core/db.py`, ajout de `sync_database_url`
- `steps/07_referentiel_competences/02_import_referentiel.md`
- `steps/ETAT.md`, `steps/PLANNING.md`, `steps/MANIFESTE.md`

Aucune migration : 07.2 ne touche pas au schéma.

## Commandes exécutées

```
docker compose up -d
docker compose exec -T api ruff format --check .
docker compose exec -T api ruff check .
docker compose exec -T api mypy app --ignore-missing-imports
docker compose exec -T api alembic upgrade head
docker compose exec -T api alembic check
docker compose exec -T api alembic downgrade base
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
docker compose exec -T api python -m app.referential seeds/referential/fictif-2026-01.json
docker compose exec -T api python -m app.referential seeds/referential/fictif-2026-01.json --apply
```

## Tests exécutés

54 tests dédiés à l'import : 32 sur la lecture et la validation du fichier, qui
ne touchent aucune base, et 22 d'intégration contre PostgreSQL réel.
L'idempotence est vérifiée en rejouant réellement l'import, et non en inspectant
un plan : la comparaison porte sur les identifiants des lignes avant et après.

Les chemins d'échec ont aussi été éprouvés à la main sur l'API vivante :
fichier absent, JSON malformé, fichier fautif, version publiée puis archivée.

## Résultats des tests

```text
Ruff       : vert, format inclus, 62 fichiers
Mypy       : vert sur 29 fichiers
Alembic    : 0004_referential_competencies (head), check vert, aucune dérive
Alembic    : downgrade base puis retour au head validés, 07.2 n'ajoutant aucune migration
Pytest     : 218 tests réussis, dont 54 nouveaux
Commande   : essai à blanc, 5 niveaux, 2 matières, 8 domaines, 39 compétences, 36 prérequis
Commande   : essai à blanc annulé, aucune ligne écrite, version absente de la base
Commande   : --apply, mêmes nombres, version créée en brouillon
Commande   : rejoué, 0 création, 0 modification, 0 suppression, code de retour 0
Commande   : base comptée après import, 5 / 2 / 8 / 39 / 36
Commande   : fichier fautif refusé, 3 erreurs nommant leur ligne, code de retour 2
Commande   : version publiée refusée, code de retour 3, édition laissée intacte
Commande   : version archivée refusée, code de retour 3
Commande   : fichier absent, code de retour 1 ; JSON malformé, code de retour 2
Tests      : cycle à deux et à trois compétences détecté, losange non confondu avec un cycle
Tests      : compétence déplacée de domaine, même identifiant conservé
Tests      : domaine retiré emportant sa compétence, prérequis retiré avec elle
```

## Critères d'acceptation

- [x] Import d'un référentiel fictif versionné.
- [x] Idempotent : rejouer le même fichier ne change rien.
- [x] Validation complète avant écriture, toutes les erreurs en une passe.
- [x] Rapport d'erreurs nommant la ligne fautive du fichier.
- [x] Détection des cycles de prérequis, dette de 07.1 résorbée.
- [x] Version publiée ou archivée immuable.
- [x] Essai à blanc par défaut, éprouvant réellement les contraintes.
- [x] Formatage, lint, typage et tests verts.
- [x] Aucune donnée réelle, aucun secret.

## Décisions ou ADR

Les deux décisions ci-dessus ont été prises par le propriétaire. Aucune ADR
nouvelle : ADR-004, amendée le 14 août, décrit le schéma et non l'outillage
d'import, et la réconciliation de brouillon ne contredit rien de ce qu'elle dit.

## Écarts par rapport au prompt

La commande s'invoque `python -m app.referential fichier.json` et non
`python -m app.referential.import fichier.json` comme l'illustrait la question
posée au propriétaire : `import` est un mot réservé de Python, et un module
portant ce nom ne s'importe pas normalement. Le comportement décrit est inchangé.

## Risques ou dette technique

- **Aucun moyen de publier une édition.** L'import s'arrête au brouillon, et
  mettre une version en vigueur est un acte distinct dont la décision revient au
  propriétaire. Tant qu'il n'existe pas, les lectures de 07.3 n'auront aucune
  édition publiée à servir. C'est le premier point à trancher en ouvrant 07.3.
- Aucune comparaison entre deux éditions. Le code métier stable la rendra
  possible ; rien ne la demande encore.
- Le fichier fictif est cohérent mais mince : trente-neuf compétences suffisent
  à éprouver l'import, pas à alimenter un diagnostic réaliste en étape 12.
- Un import très volumineux tiendrait entièrement en mémoire et en une seule
  transaction. À l'échelle d'un référentiel de primaire, c'est sans objet.

## Blocages

Aucun.

## Prochaines actions

1. Sous-étape 07.3, lectures filtrées et paginées du référentiel.
2. Trancher la publication d'une édition, préalable aux lectures de 07.3.

## Mise à jour appliquée à ETAT.md

Sous-étape 07.2 ajoutée à la section « Étape 07 », clôture distante de 07.1
consignée, points ouverts et prochaine action mis à jour.

## Mise à jour appliquée à PLANNING.md

REF-02 passée à Terminé avec sa preuve.
