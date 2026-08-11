 # Infrastructure Docker - commandes locales

 Démarrage des services en arrière-plan :

 ```
 docker compose up -d
 ```

 Arrêt sans supprimer les volumes :

 ```
 docker compose down
 ```

 Reset complet (supprime volumes et recrée) :

 ```
 docker compose down -v
 docker compose up -d
 ```

 Voir les logs :

 ```
 docker compose logs -f
 ```

 Créer les buckets MinIO (après `docker compose up -d`) :

 ```
 ./infrastructure/scripts/create_minio_buckets.sh
 ```

 Remarques :
 - Les services sont liés sur `127.0.0.1`, ils ne seront pas exposés publiquement.
 - Éviter de commiter un fichier `.env` avec des secrets réels. Utiliser `.env.example`.
