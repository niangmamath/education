# 03_infrastructure_locale_ci

Lire les cinq fichiers racine avant toute action. Exécuter les prompts dans l’ordre. Après chaque prompt, créer un rapport dans ce dossier, puis mettre à jour `ETAT.md` et `PLANNING.md`.

Commandes utiles pour l'infrastructure locale
--------------------------------------------

Les scripts suivants ont été ajoutés dans `infrastructure/scripts/` pour automatiser les tâches courantes :

- `start_local_infra.sh` : démarre `docker compose up -d` et tente de créer les buckets MinIO.
- `stop_local_infra.sh` : arrête les services (`docker compose down`).
- `reset_local_infra.sh` : arrête les services et supprime les volumes nommés (demande confirmation explicite).

Exemples d'utilisation (depuis la racine du dépôt) :

```bash
# Démarrer l'infrastructure
infrastructure/scripts/start_local_infra.sh

# Arrêter l'infrastructure
infrastructure/scripts/stop_local_infra.sh

# Réinitialiser (arrêt + suppression des volumes)
infrastructure/scripts/reset_local_infra.sh
```

Tâches manuelles restantes (à exécuter localement)
-------------------------------------------------

1. Lancer `infrastructure/scripts/start_local_infra.sh` pour démarrer les services.
2. Vérifier les healthchecks :
	- PostgreSQL : `docker ps` puis `docker inspect --format='{{json .State.Health}}' <postgres_container>`
	- Redis : `redis-cli -h 127.0.0.1 -p 6379 ping`
	- MinIO : ouvrir `http://localhost:9000` ou `curl http://localhost:9000/minio/health/ready`
3. Exécuter le script de création de buckets si le démarrage a réussi :
	`infrastructure/scripts/create_minio_buckets.sh`
4. Adapter `.env` pour que `DATABASE_URL` utilise le dialecte async (`postgresql+asyncpg://user:pass@127.0.0.1:5433/studentconnect_dev`).
5. Appliquer les migrations Alembic :
	```bash
	cd apps/api
	alembic -c alembic.ini upgrade head
	alembic -c alembic.ini downgrade -1
	```
6. Exécuter les tests backend :
	```bash
	cd apps/api
	pip install -r requirements.txt
	pip install pytest pytest-asyncio
	pytest -q
	```

Notes
-----

- Ne pas committer de mots de passe en clair ; utiliser `.env` et variables d'environnement.
- Les scripts ajoutés ne modifient pas de données de production et sont destinés à l'environnement de développement.

