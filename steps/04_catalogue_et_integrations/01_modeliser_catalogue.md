# Prompt 04.1, modéliser le catalogue de ressources

## Champs obligatoires

provider, external_id, title, description, source_url, embed_url, embed_mode, subject, grade, age, competency links, language, duration, license, attribution, offline_available, tracking_mode, review_status et last_verified_at.

## Travaux

- modèles et migrations ;
- admin ;
- validations ;
- filtres essentiels ;
- tests ;
- documentation du schéma.

## Critères

- une ressource incomplète est rejetée ou marquée à vérifier ;
- `tracking_mode` utilise uniquement les valeurs autorisées ;
- aucune ressource gratuite n’est supposée réhébergeable.
