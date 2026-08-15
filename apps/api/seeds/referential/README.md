# Référentiels d’import

Les fichiers de ce dossier décrivent une **édition** du référentiel scolaire :
sa version, ses niveaux, ses matières et leurs domaines, et les compétences
rattachées à un domaine et à un niveau.

## Données fictives

`fictif-2026-01.json` est **entièrement fictif**. Ses libellés s’inspirent de
l’école primaire française pour rester plausibles, mais ce fichier ne reproduit
aucun programme officiel et n’en tient pas lieu. Le stage travaille sur données
fictives, et un référentiel réel demanderait une vérification de licence qui
n’a pas été faite.

## Importer

```bash
# essai à blanc, rien n’est écrit
docker compose exec -T api python -m app.referential import seeds/referential/fictif-2026-01.json

# écriture
docker compose exec -T api python -m app.referential import seeds/referential/fictif-2026-01.json --apply
```

L’import crée la version en `draft` si elle n’existe pas, puis réconcilie ce
brouillon avec le fichier. Rejouer le même fichier ne change rien. Une version
`published` ou `archived` est refusée : elle est immuable, et un programme
corrigé s’importe sous un nouveau code de version.

Le détail est dans `docs/backend/import-referentiel.md`.
