# ADR-008 : Stockage S3 Compatible et URLs Présignées

## Statut

✅ **Accepted** - Décision validée et implémentée

---

## Contexte

StudentConnect doit stocker et servir des **fichiers binaires** :
- Paquets H5P versionnés
- Contenu statique généré
- Uploads utilisateurs (en quarantaine)
- Assets divers (images, vidéos)

### Problème à résoudre

Choisir une solution de **stockage objet** qui offre :
- **Scalabilité** pour un grand nombre de fichiers
- **Durabilité** et disponibilité
- **Sécurité** des accès
- **Performance** pour le chargement
- **Coût raisonnable**
- **Compatibilité** avec l'infrastructure locale (Docker)

### Contraintes

- **Stockage compatible S3** (décision dans DECISIONS_FINALES.md)
- **URLs présignées** pour les accès temporaires
- **Origine de contenu dédiée** pour l'isolation
- **Versionnage** des fichiers H5P

---

## Décision

**Utiliser un stockage compatible S3** avec **URLs présignées** pour les accès temporaires.

### Architecture de stockage

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Browser)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ URL présignée (expire après 1h)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    CDN / Reverse Proxy                         │
│  - Cache les fichiers fréquemment accédés                    │
│  - Termine le TLS                                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    S3 Compatible (MinIO/AWS)                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Buckets:                                               │  │
│  │  - h5p-packages/ (paquets validés, versionnés)            │  │
│  │  - h5p-quarantine/ (fichiers en quarantaine)              │  │
│  │  - h5p-temp/ (uploads temporaires)                        │  │
│  │  - phet-cache/ (cache PhET si hébergement local)          │  │
│  │  - assets/ (images, vidéos, etc.)                         │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Pour le développement local

**MinIO** sera utilisé comme alternative open-source à AWS S3 :
- Conteneur Docker léger
- API 100% compatible S3
- Idéal pour le développement et les tests

### Pour la production

Différentes options possibles :
- **AWS S3** : Service managé, haute disponibilité
- **DigitalOcean Spaces** : Plus simple et moins cher
- **Backblaze B2** : Moins cher, bonne performance
- **MinIO hébergé** : Auto-hébergé pour contrôle total

---

## Options considérées

### 1. MinIO (Développement) + AWS S3 (Production)

**Pour** :
- ✅ **Compatibilité S3** totale
- ✅ **MinIO gratuit** pour le développement
- ✅ **AWS S3** : service mature et fiable
- ✅ **Migration facile** entre les deux
- ✅ **Outils communs** (sdk, cli)

**Contre** :
- ❌ Configuration différente dev/prod

**Verdict** : ✅ **Sélectionné**

---

### 2. Filesystem local

**Pour** :
- ✅ Simple à configurer
- ✅ Pas de dépendance externe

**Contre** :
- ❌ Pas scalable
- ❌ Pas durable (un seul disque)
- ❌ Pas adapté pour production
- ❌ Pas de versionnage natif

**Verdict** : ❌ **Rejeté** - Pas adapté pour production

---

### 3. NFS / GlusterFS

**Pour** :
- ✅ Partage de fichiers entre serveurs

**Contre** :
- ❌ Complexe à configurer
- ❌ Pas d'API standardisée
- ❌ Performances limitées
- ❌ Pas de versionnage natif

**Verdict** : ❌ **Rejeté** - Pas adapté pour nos besoins

---

### 4. MongoDB GridFS

**Pour** :
- ✅ Intégration avec MongoDB
- ✅ Bon pour les gros fichiers

**Contre** :
- ❌ **Interdit** par inférence (Neo4j interdit, autres bases non-SQL aussi)
- ❌ Pas compatible S3
- ❌ Complexe pour nos besoins simples

**Verdict** : ❌ **Rejeté** - Incompatible avec la décision S3

---

## Conséquences

### Avantages

- **Scalabilité illimitée** : S3 scale horizontalement
- **Durabilité** : 11 9's de durabilité pour AWS S3
- **Disponibilité** : 99.99% de disponibilité
- **Sécurité** : Chiffrement au repos et en transit
- **Performance** : CDN intégré ou compatible
- **Coût optimisé** : Paiement à l'usage

### Inconvénients

- **Coût** : Peut devenir cher avec beaucoup de données
- **Complexité** : Configuration initiale plus complexe
- **Latence** : Accès réseau nécessaire

### Mitigations

- **Lifecycle policies** : Archiver les vieux fichiers vers storage froid
- **Caching agressif** : CDN pour les fichiers fréquemment accédés
- **Compression** : Compresser les fichiers quand possible
- **Optimisation** : Taille des paquets H5P avant upload

---

## Implémentation

### Configuration MinIO (Docker Compose)

```yaml
# docker-compose.yml
services:
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"  # Console
    volumes:
      - minio_data:/data
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  minio_data:
```

### Configuration Python (boto3)

```python
# config.py
import os
from typing import Optional

class S3Config:
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_ACCESS_KEY: str = os.environ["S3_ACCESS_KEY"]
    S3_SECRET_KEY: str = os.environ["S3_SECRET_KEY"]
    S3_BUCKET: str = os.getenv("S3_BUCKET", "studentconnect")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_PUBLIC_URL: str = os.getenv("S3_PUBLIC_URL", "http://localhost:9000")
    S3_PRESIGNED_EXPIRE: int = int(os.getenv("S3_PRESIGNED_EXPIRE", "3600"))  # 1h

    @property
    def is_aws(self) -> bool:
        return "amazonaws.com" in self.S3_ENDPOINT
```

### Service S3

```python
# services/s3_service.py
import boto3
from botocore.client import Config
from config import S3Config
from typing import Optional
import datetime

class S3Service:
    def __init__(self):
        config = Config(
            signature_version='s3v4',
            region_name=S3Config.S3_REGION,
            s3={'addressing_style': 'path'}  # Pour MinIO
        )
        
        self.client = boto3.client(
            's3',
            endpoint_url=S3Config.S3_ENDPOINT,
            aws_access_key_id=S3Config.S3_ACCESS_KEY,
            aws_secret_access_key=S3Config.S3_SECRET_KEY,
            config=config
        )
    
    def generate_presigned_url(
        self,
        object_name: str,
        expiration: int = S3Config.S3_PRESIGNED_EXPIRE
    ) -> str:
        """Génère une URL présignée pour un fichier"""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3Config.S3_BUCKET, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            print(f"Erreur générant URL présignée: {e}")
            raise
    
    def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        content_type: str = 'application/octet-stream'
    ) -> str:
        """Upload un fichier vers S3"""
        self.client.put_object(
            Bucket=S3Config.S3_BUCKET,
            Key=object_name,
            Body=file_data,
            ContentType=content_type
        )
        return f"s3://{S3Config.S3_BUCKET}/{object_name}"
    
    def download_file(self, object_name: str) -> bytes:
        """Télécharge un fichier depuis S3"""
        response = self.client.get_object(
            Bucket=S3Config.S3_BUCKET,
            Key=object_name
        )
        return response['Body'].read()
    
    def delete_file(self, object_name: str) -> None:
        """Supprime un fichier de S3"""
        self.client.delete_object(
            Bucket=S3Config.S3_BUCKET,
            Key=object_name
        )
```

### Versionnage des paquets H5P

Les paquets H5P seront stockés avec la structure :
```
h5p-packages/
├── {package_id}/
│   ├── {version}/
│   │   ├── content/          # Contenu extrait
│   │   │   ├── index.html
│   │   │   ├── h5p.json
│   │   │   └── ...
│   │   ├── h5p-original.h5p  # Fichier original
│   │   └── metadata.json    # Métadonnées
│   └── latest -> {version}  # Symlink vers la dernière version
└── index.json              # Index de tous les paquets
```

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| Perte de données | Très faible | Élevé | Backups automatiques, versionnage |
| Coût excessif | Moyenne | Moyen | Monitoring, lifecycle policies |
| Latence | Faible | Moyen | CDN, caching |
| Incompatibilité | Faible | Moyen | Tests avec MinIO et AWS S3 |

---

## Références

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Presigned URLs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |
