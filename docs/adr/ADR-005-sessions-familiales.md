# ADR-005 : Gestion des Sessions Familiales

## Statut

✅ **Accepted** - Décision validée, amendée le 14 août 2026 après l'implémentation
de l'étape 06.

---

## Amendement du 14 août 2026

L'implémentation de l'étape 06 a mis au jour trois points sur lesquels cette ADR
ne pouvait pas tenir telle quelle. **Les règles ci-dessous prévalent sur tout
extrait plus ancien de ce document.**

### 1. L'unicité du pseudonyme est familiale, et la connexion Enfant passe par le code famille

Le flux d'origine, `POST /auth/child/login (pseudonyme, pin)`, supposait qu'un
pseudonyme désigne un enfant sur toute la plateforme. C'est intenable : le premier
inscrit réserverait `lea` pour tout le monde. Le pseudonyme est donc unique **dans
sa famille**, la contrainte porte sur le couple `(parent_id, pseudonym)`, et deux
familles peuvent chacune avoir une `lea`.

Le pseudonyme ne désignant plus personne à lui seul, chaque Parent porte un **code
famille** de six caractères, tiré au hasard à l'inscription, rendu dans son profil,
et régénérable en cas de fuite. La connexion Enfant devient
`POST /auth/child/login (family_code, pseudonyme, pin)`.

Un Enfant peut aussi ouvrir son propre profil avec ce code, via
`POST /auth/child/register`, mais ce profil reste **en attente** jusqu'à activation
par le Parent : connaître un code permet de demander à rejoindre une famille,
jamais d'y entrer.

### 2. Argon2id remplace bcrypt

Les extraits de code de cette ADR mentionnaient bcrypt ; sa section Décision ne
fixait aucun algorithme. Mots de passe Parent et PIN Enfant sont hachés en
**Argon2id**, avec les paramètres par défaut d'`argon2-cffi`, qui suivent le profil
recommandé par la RFC 9106. Argon2id est en tête des recommandations OWASP devant
bcrypt : son coût mémoire rend l'attaque par matériel dédié bien plus chère. Une
connexion réussie réhache une empreinte produite sous d'anciens paramètres.

### 3. Un PIN à six chiffres ne tient que si les tentatives sont plafonnées

La table des risques ne comptait que sur le million de combinaisons, ce qu'un
script épuise. Un compteur d'échecs par enfant est tenu dans Redis, en fenêtre
glissante ; au-delà du plafond la connexion répond `429`, y compris avec le bon
PIN. Sont également refusés à la création le chiffre répété et la suite continue.

### Précisions apportées par l'implémentation

- **Aucune table SQL de session.** Le modèle ci-dessous montre une entité
  `Session` ; elle n'existe pas. Une session est une entrée Redis, indexée par
  l'empreinte SHA-256 du jeton et non par le jeton, afin qu'une copie de Redis ne
  livre aucun cookie rejouable.
- **Un index des sessions par compte** permet de toutes les révoquer d'un coup,
  ce qu'exigent le changement de PIN et la désactivation d'un profil.
- **Trois états de profil Enfant**, `pending`, `active` et `disabled`, à la place
  d'un booléen : la question « ce profil peut-il ouvrir une session » a trois
  réponses.
- **Session Enfant d'une journée** contre sept jours pour le Parent.
- **La vérification d'adresse email reste non implémentée**, faute de service
  d'envoi. `is_verified` demeure à `false` et la connexion ne l'exige pas.

La mise en œuvre est décrite dans `docs/backend/authentification-parent-sessions.md`
et `docs/backend/acces-enfant.md`.

---

## Contexte

StudentConnect doit gérer **deux types d'utilisateurs distincts** :
- **Parents** : Accès complet, gestion des enfants, visualisation des dashboards
- **Enfants** : Accès restreint, réalisent des activités, pas d'email requis

### Problème à résoudre

Concevoir un système d'**authentification et de gestion des sessions** qui :
1. Permet aux parents de créer et gérer leurs enfants
2. Authentifie les enfants via un PIN simple
3. Maintient des sessions sécurisées
4. Respecte les contraintes de sécurité et de confidentialité

### Contraintes

- **Parents** : email + mot de passe + vérification email
- **Enfants** : pas d'email, pas de téléphone (règle non négociable)
- **Sessions** : cookies opaques, HttpOnly, Secure, SameSite
- **Stockage** : Redis pour les sessions
- **Données fictives** : toutes les données du stage sont fictives

---

## Décision

**Implémenter un système d'authentification basé sur les sessions** avec :

### Modèle de données

```
Authentification:
├── Parent (email, family_code, password_hash, is_verified)
├── Child (parent_id, pseudonyme, pin_hash, status)
├── Session (Redis uniquement : user_id, user_type, expires_at)
└── Family (parent_id, children[])

Unicité : email et family_code sur toute la plateforme,
          pseudonyme dans sa famille seulement.
```

### Flux d'authentification

```
Parent Flow:
1. Register: POST /auth/parent/register (email, password)
2. Verify: GET /auth/parent/verify?token=...
3. Login: POST /auth/parent/login (email, password)
4. Session: Cookie HttpOnly avec session_id
5. Logout: DELETE /auth/logout

Child Flow:
1. Parent crée enfant: POST /auth/children (pseudonyme, pin)
   ou l'enfant le demande: POST /auth/child/register (family_code, pseudonyme, pin),
   profil en attente jusqu'à POST /auth/children/{id}/activate
2. Child login: POST /auth/child/login (family_code, pseudonyme, pin)
3. Session: Cookie HttpOnly avec session_id (marqué comme child), un jour
4. Logout: DELETE /auth/logout
```

---

## Options considérées

### 1. Sessions basées sur cookies (Sélectionné)

**Pour** :
- ✅ Simple à implémenter
- ✅ Pas de token à stocker côté client
- ✅ Facile à invalider (suppression côté serveur)
- ✅ Sécurisé avec HttpOnly, Secure, SameSite
- ✅ Compatible avec tous les navigateurs

**Contre** :
- ❌ Moins flexible pour les apps mobiles (futur)
- ❌ Nécessite un stockage serveur (Redis)

**Verdict** : ✅ **Sélectionné**

---

### 2. JWT (JSON Web Tokens)

**Pour** :
- ✅ Stateless (pas de stockage serveur)
- ✅ Flexible pour apps mobiles
- ✅ Standard industriel

**Contre** :
- ❌ Moins sécurisé (stockage local)
- ❌ Difficile à invalider avant expiration
- ❌ Token peut être volé (XSS)
- ❌ Plus complexe pour le refresh

**Verdict** : ❌ **Rejeté** - Moins sécurisé pour notre use case

---

### 3. OAuth2 / OpenID Connect

**Pour** :
- ✅ Standard industriel
- ✅ Support SSO

**Contre** :
- ❌ Trop complexe pour un MVP
- ❌ Nécessite un provider externe
- ❌ Surkill pour nos besoins

**Verdict** : ❌ **Rejeté** - Trop complexe

---

## Conséquences

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client (Browser)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │ Cookie (HttpOnly, Secure, SameSite)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer / Proxy                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      Next.js (Frontend)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ Session Cookie
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI (Backend)                          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Session Middleware:                                      │  │
│  │  - Lit le cookie                                         │  │
│  │  - Vérifie la session dans Redis                       │  │
│  │  - Attache user_info à la request                       │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      Redis (Session Store)                     │
│  session_id: {user_id, user_type, expires_at, ...}            │
└─────────────────────────────────────────────────────────────┘
```

### Modèle de données SQLAlchemy

> Extrait d'origine, conservé pour mémoire. L'amendement du 14 août 2026 prévaut :
> il n'existe aucune table `Session`, le PIN est haché en Argon2id et non en
> bcrypt, `Parent` porte un `family_code`, `Child` porte un `status`, et l'unicité
> du pseudonyme est familiale. Le modèle réel est `apps/api/app/models/identity.py`.

```python
# models/user.py
from sqlalchemy import Column, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Parent(Base):
    __tablename__ = "auth_parents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    
    children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user")

class Child(Base):
    __tablename__ = "auth_children"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("auth_parents.id"), nullable=False)
    pseudonyme = Column(String(50), nullable=False)
    hashed_pin = Column(String(255), nullable=False)  # bcrypt hash
    date_of_birth = Column(Date)
    
    parent = relationship("Parent", back_populates="children")
    sessions = relationship("Session", back_populates="user")

class Session(Base):
    __tablename__ = "auth_sessions"
    
    id = Column(String(64), primary_key=True)  # UUID string
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_type = Column(String(10), nullable=False)  # "parent" or "child"
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("Parent", back_populates="sessions", foreign_keys=[user_id])
```

---

## Implémentation

> Extraits d'origine, conservés pour mémoire. Ils précèdent l'amendement du
> 14 août 2026 : la connexion Enfant y prend un pseudonyme seul et les sessions y
> sont écrites sans empreinte. Le code livré est dans `apps/api/app/api/v1/`.

### FastAPI Middleware

```python
# middleware/session.py
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
import redis.asyncio as redis
from uuid import UUID

redis_client = redis.from_url("redis://localhost:6379")

async def get_session(request: Request):
    session_id = request.cookies.get("studentconnect_session")
    if not session_id:
        return None
    
    session_data = await redis_client.hgetall(f"session:{session_id}")
    if not session_data:
        return None
    
    return {
        "session_id": session_id,
        "user_id": UUID(session_data[b"user_id"]),
        "user_type": session_data[b"user_type"].decode(),
        "expires_at": session_data[b"expires_at"]
    }

async def require_auth(request: Request):
    session = await get_session(request)
    if not session:
        raise HTTPException(status_code=401, detail="Non autorisé")
    return session
```

### Routes d'authentification

```python
# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import bcrypt

router = APIRouter(prefix="/auth", tags=["authentication"])

class ParentRegister(BaseModel):
    email: str
    password: str

class ParentLogin(BaseModel):
    email: str
    password: str

class ChildLogin(BaseModel):
    pseudonyme: str
    pin: str

@router.post("/parent/register")
async def register_parent(data: ParentRegister, db: AsyncSession = Depends(get_db)):
    # Vérifier email unique
    # Hash password
    # Créer parent
    # Envoyer email de vérification
    pass

@router.post("/parent/login")
async def login_parent(data: ParentLogin, response: Response, db: AsyncSession = Depends(get_db)):
    parent = await authenticate_parent(db, data.email, data.password)
    if not parent:
        raise HTTPException(status_code=401)
    
    session_id = secrets.token_urlsafe(32)
    await redis_client.hset(
        f"session:{session_id}",
        mapping={
            "user_id": str(parent.id),
            "user_type": "parent",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    await redis_client.expire(f"session:{session_id}", 7 * 24 * 60 * 60)
    
    response.set_cookie(
        key="studentconnect_session",
        value=session_id,
        httponly=True,
        secure=True,  # HTTPS seulement
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    return {"status": "logged_in"}

@router.post("/child/login")
async def login_child(data: ChildLogin, response: Response, db: AsyncSession = Depends(get_db)):
    child = await authenticate_child(db, data.pseudonyme, data.pin)
    if not child:
        raise HTTPException(status_code=401)
    
    session_id = secrets.token_urlsafe(32)
    await redis_client.hset(
        f"session:{session_id}",
        mapping={
            "user_id": str(child.id),
            "user_type": "child",
            "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }
    )
    await redis_client.expire(f"session:{session_id}", 24 * 60 * 60)
    
    response.set_cookie(
        key="studentconnect_session",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=24 * 60 * 60
    )
    return {"status": "logged_in"}

@router.post("/logout")
async def logout(response: Response, session: dict = Depends(require_auth)):
    await redis_client.delete(f"session:{session['session_id']}")
    response.delete_cookie("studentconnect_session")
    return {"status": "logged_out"}
```

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| Session hijacking | Faible | Élevé | HttpOnly, Secure, SameSite cookies |
| Session fixation | Faible | Élevé | Régénérer session_id au login |
| Session expiration | Moyenne | Moyen | Auto-refresh avec CSRF token |
| Redis downtime | Faible | Élevé | Fallback en mémoire (limité) |
| PIN deviné | Moyenne | Élevé | PIN à 6 chiffres hachés en Argon2id, PIN triviaux refusés, et surtout compteur d'échecs par enfant : sans plafond, un million de combinaisons s'épuise |
| Code famille divulgué | Moyenne | Moyen | Il ne donne aucun accès, seulement le droit de demander un profil, que le Parent doit activer. Régénérable, et les demandes reçues sont écartables |
| Profil Enfant compromis | Faible | Élevé | PIN réinitialisable par le Parent, profil désactivable, et toutes les sessions du profil révocables d'un coup |

---

## Références

- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Redis Sessions](https://redis.io/topics/sessions)
- [RFC 9106, Argon2](https://www.rfc-editor.org/rfc/rfc9106.html)
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [argon2-cffi](https://argon2-cffi.readthedocs.io/)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |
| 2026-08-14 | Claude Code | Amendement après l'étape 06 : unicité familiale du pseudonyme et code famille, Argon2id au lieu de bcrypt, plafond sur les tentatives de PIN, précisions sur les sessions Redis |
