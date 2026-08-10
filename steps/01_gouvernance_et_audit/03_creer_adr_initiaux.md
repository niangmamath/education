# Étape 01.3, créer les ADR initiaux

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Consigner les décisions structurantes avant le code.

## Travaux obligatoires


Créer dans `docs/adr/` :

- ADR-001 monorepo ;
- ADR-002 Next.js et Tailwind ;
- ADR-003 FastAPI REST ;
- ADR-004 PostgreSQL et SQLAlchemy ;
- ADR-005 sessions familiales ;
- ADR-006 H5P Standalone et origine isolée ;
- ADR-007 PhET iframe ;
- ADR-008 S3 et URLs présignées ;
- ADR-009 Redis et Celery ;
- ADR-010 planning Markdown sans GitHub Project.

Chaque ADR doit contenir contexte, décision, options, conséquences, risques et statut.


## Critères d’acceptation


- [ ] Les décisions finales sont toutes représentées.
- [ ] Les anciennes stacks ne sont pas réintroduites.
- [ ] Les décisions encore ouvertes sont marquées Proposed.


## Livrables

ADR et registre `docs/architecture/decision-register.md`, plus rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
