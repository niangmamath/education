# Rapport de réalisation

## Métadonnées

- Étape : 08, catalogue de contenus et activités
- Sous-étapes : 08.1, 08.2 et 08.3
- Date et heure : 15 août 2026, 15h30
- Agent : Claude Code
- ID du planning : CAT-01, CAT-02, CAT-03
- Branche : `feat/etape-08-catalogue`
- Commit ou pull request : `ac3df20`, `d01af0f` et le commit de 08.3
- Statut : Terminé

## Objectif

Modéliser le catalogue d'activités et ses liens vers les compétences, n'y
admettre que les types H5P validés par ADR-012, et exposer les lectures.

## Prérequis vérifiés

- Étape 07 clôturée et fusionnée, Pull Request #14.
- Branche `feat/etape-08-catalogue` issue de `main` à jour.
- Cinq services Docker sains, migration à `0004` avant de commencer.
- ADR-006, ADR-008 et ADR-012 relus, ainsi que `DECISIONS_FINALES.md`.

## État initial observé

Le référentiel était complet et lisible, mais rien ne s'y rattachait : aucune
activité, aucun contenu. Le paquet H5P pilote validé par le spike de l'étape 04
dormait dans `experiments/`, sans aucun moyen d'entrer dans la plateforme.

## Travaux réalisés

### Une décision de conception, prise sans arbitrage préalable

Le propriétaire a demandé, le 15 août 2026, que les sous-étapes s'enchaînent sans
arrêt entre elles. La décision structurante de l'étape a donc été prise par
l'agent, consignée en **ADR-013**, et reste à confirmer :

**Le catalogue pointe vers les compétences par leur code métier, sans clé
étrangère.** Le référentiel est versionné parce que des traces le désignent ; le
catalogue est un travail éditorial qui doit suivre le programme en vigueur. Une
clé étrangère vers une ligne de compétence serait caduque à chaque publication
d'édition et imposerait de remapper tout le catalogue avant qu'une nouvelle
édition ne serve — une propriété souhaitable transformée en corvée, donc en
oubli.

La contrepartie est explicite et livrée avec la décision : un code qui ne
désigne rien est accepté par la base, et `python -m app.catalog check` est ce qui
le trouve.

### 08.1, le modèle

`catalog_activities`, `catalog_activity_competencies` et
`catalog_h5p_packages`, migration `0005_catalog_activities` réversible.

Deux contraintes portent des décisions plutôt que des formes. Le lien de
compétence n'a **pas** de clé étrangère, par ADR-013. La bibliothèque H5P est
bornée par un `CHECK` à ce qu'ADR-012 autorise : admettre un second type demande
alors une migration et un amendement d'ADR, ce qui est la friction que la
décision réclamait.

La durée est bornée entre une et soixante minutes. Un Quick Repair dure trois à
sept minutes, ce qui est une règle produit ; rien ne doit prétendre ne prendre
aucun temps, ni durer une heure et demie.

### 08.2, les paquets H5P

Ni éditeur ni route de téléversement, par ADR-006 et ADR-012 : un paquet est
vérifié, stocké et enregistré par quelqu'un qui a accès au serveur.

Un `.h5p` est une archive zip, donc une entrée non fiable. **L'archive est lue
sans jamais être extraite** : rien n'est écrit sur le disque, donc un nom d'entrée
forgé n'a nulle part où s'échapper. Sont refusés les chemins remontants et
absolus, les archives de plus de cinq cents entrées, celles qui se déploient au
delà de cent fois leur poids, les fichiers au-delà de vingt mégaoctets, et tout
ce qui ne dit pas quelle bibliothèque il joue.

Le type est refusé **avant que le moindre octet n'atteigne le bucket**. L'ordre
des opérations est vérification, stockage, écriture ; si l'écriture échoue,
l'objet est retiré, car un objet sans ligne est un orphelin que personne ne
revérifiera.

L'empreinte est calculée sur les octets lus, et nomme l'objet dans le bucket : les
mêmes octets ne s'y trouvent jamais deux fois.

### 08.3, les lectures

`GET /api/v1/catalog/activities`, `.../{code}` et `/kinds`. Seules les activités
publiées sont servies ; un brouillon répond exactement comme une activité
inexistante. Toute session authentifiée peut lire, Parent comme Enfant, sur le
même raisonnement qu'en 07.3.

Filtres `competency`, `kind` et `max_duration`, combinables. Le dernier existe
parce que trois à sept minutes est une règle produit, et demander un Quick Repair
ne doit pas obliger à lire tout le catalogue.

**Aucune réponse ne dit où vit un paquet.** Clé d'objet, empreinte, licence et
provenance restent côté serveur : l'origine de contenu isolée d'ADR-012 est ce
qui remettra le fichier.

### Dettes corrigées en chemin

- **Le registre des décisions** annonçait dix ADR dont neuf « à créer », alors
  que treize existaient et onze étaient acceptées. Il a été reconstruit depuis
  les fichiers d'ADR eux-mêmes, ADR-013 comprise.
- **Un test portait un nom plus fort que ce qu'il prouvait** : la compensation du
  stockage n'était jamais exercée, le doublon étant refusé avant l'écriture. Il
  fait désormais échouer l'écriture après le dépôt de l'objet.
- **Deux tests supposaient une base vide** et une empreinte libre, ce qui a cessé
  d'être vrai dès que l'activité de démonstration a existé. Ils portent maintenant
  sur leurs propres lignes.

## Fichiers créés

- `apps/api/app/models/catalog.py`
- `apps/api/alembic/versions/0005_catalog_activities.py`
- `apps/api/app/catalog/{__init__,h5p,registration,storage,checks,__main__}.py`
- `apps/api/app/api/v1/catalog.py`, `apps/api/app/schemas/catalog.py`
- `apps/api/tests/test_catalog_{models,h5p,registration,api}.py`
- `docs/adr/ADR-013-catalogue-lie-par-code.md`
- `docs/backend/catalogue-activites.md`

## Fichiers modifiés

- `apps/api/app/models/__init__.py`, `apps/api/app/core/routing.py`
- `docs/architecture/decision-register.md`
- `steps/ETAT.md`, `steps/PLANNING.md`, `steps/MANIFESTE.md`, fiches 08.1 à 08.3

## Commandes exécutées

```
docker compose exec -T api alembic revision --autogenerate -m "..."
docker compose exec -T api alembic upgrade head ; alembic check
docker compose exec -T api alembic downgrade base ; alembic upgrade head
docker compose exec -T api ruff format --check . ; ruff check .
docker compose exec -T api mypy app --ignore-missing-imports
docker compose exec -T api pytest -q
docker compose cp experiments/h5p-spike/packages/true-false-question-34806.h5p api:/tmp/pilote.h5p
docker compose exec -T api python -m app.catalog register demo-vrai-faux-01 /tmp/pilote.h5p --licence ... --source ...
docker compose exec -T api python -m app.catalog check
```

## Tests exécutés

81 tests dédiés au catalogue : 27 sur les contraintes du schéma, 19 sur la
vérification des paquets, 12 sur l'enregistrement et le contrôle des liens, 23
sur les routes.

Les archives hostiles sont construites dans les tests eux-mêmes. Le paquet pilote
vit dans `experiments/`, hors de l'arborescence que monte le conteneur de l'API :
il a donc été éprouvé à la main plutôt que par un test qui n'aurait pu tourner
qu'en intégration continue, ce qui aurait été pire que rien.

## Résultats des tests

```text
Ruff       : vert, format inclus
Mypy       : vert sur 41 fichiers
Alembic    : 0005_catalog_activities (head), check vert, aucune dérive
Alembic    : downgrade base puis retour au head validés
Pytest     : 336 tests réussis, dont 81 nouveaux
Commande   : paquet pilote enregistré, H5P.TrueFalse 1.8 accepté
Commande   : empreinte calculée 9914c275…b07f3c, identique à celle publiée par ADR-012
Commande   : check, édition fictif-2026-01, 1 lien, catalogue cohérent, code 0
Tests      : quatre autres types H5P refusés, message citant ADR-012
Tests      : zip slip, chemin absolu, 501 entrées et bombe de décompression refusés
Tests      : type refusé n'atteignant jamais le stockage
Tests      : écriture en échec après dépôt, objet retiré du stockage
Tests      : brouillon et archive répondant 404 comme une activité inexistante
Tests      : aucune réponse ne contient de clé d'objet, d'empreinte ni de licence
Tests      : lien valide dans une édition, mort dans la suivante, détecté
```

## Critères d'acceptation

- [x] Activités, types, métadonnées, statuts et liens vers compétences modélisés.
- [x] Migration réversible, `alembic check` sans dérive.
- [x] Seuls les types validés par ADR-012 sont admis, en code et en base.
- [x] Aucun éditeur, aucune route de téléversement, aucun import non sécurisé.
- [x] Lectures filtrées et paginées, sans affectation ni résultat.
- [x] Autorisation validée : `401` sans session, Parent et Enfant admis.
- [x] Formatage, lint, typage et tests verts.
- [x] Aucune donnée réelle, aucun secret.

## Décisions ou ADR

**ADR-013 créée**, sur le lien du catalogue au référentiel par code métier. Elle
a été décidée par l'agent en l'absence d'arbitrage, la consigne étant d'enchaîner
les sous-étapes ; elle reste à confirmer par le propriétaire, et son option 3
laisse la porte ouverte si un catalogue figé avec une édition devenait
nécessaire.

Registre des décisions reconstruit.

## Écarts par rapport au prompt

Un seul rapport couvre 08.1 à 08.3, au lieu d'un par sous-étape. La consigne du
15 août était d'enchaîner sans s'arrêter, et le propriétaire a demandé un travail
plus économe ; le détail par sous-étape est dans les messages de commit, qui sont
horodatés et attachés au code.

## Risques ou dette technique

- **ADR-013 n'a pas été arbitrée par le propriétaire.** C'est la décision la plus
  structurante de l'étape et elle mérite une confirmation.
- Aucun antivirus dans le contrôle des paquets, alors qu'ADR-012 l'exige pour la
  production. Aucun scanner n'est disponible dans l'environnement de stage.
- Aucune remise de paquet au navigateur : l'origine de contenu isolée, sa CSP et
  l'endpoint xAPI authentifié restent à construire.
- Aucun import de masse du catalogue, contrairement au référentiel. Les activités
  se créent une à une, ce qui suffit à une démonstration mais pas à un contenu
  réel.
- Le catalogue de démonstration se réduit à une activité, celle qui joue le
  paquet pilote.

## Blocages

Aucun.

## Prochaines actions

1. Sous-étape 08.4, clôture de l'étape 08.
2. Faire confirmer ADR-013 par le propriétaire.

## Mise à jour appliquée à ETAT.md

Sous-étapes 08.1 à 08.3 consignées, points ouverts et prochaine action mis à jour.

## Mise à jour appliquée à PLANNING.md

Phase 4 ajoutée, CAT-01 à CAT-03 terminées.
