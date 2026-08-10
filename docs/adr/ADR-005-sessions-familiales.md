# ADR-005 : Gestion des Sessions Familiales

## Statut

✅ **Accepted** - Décision validée et implémentée

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
├── Parent (email, password_hash, is_verified)
├── Child (parent_id, pseudonyme, pin_hash)
├── Session (session_id, user_id, user_type, expires_at)
└── Family (parent_id, children[])
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
2. Child login: POST /auth/child/login (pseudonyme, pin)
3. Session: Cookie HttpOnly avec session_id (marqué comme child)
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
| PIN deviné | Faible | Moyen | PIN à 6 chiffres (1M combinaisons) |

---

## Références

- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Redis Sessions](https://redis.io/topics/sessions)
- [bcrypt Documentation](https://bcrypt.readthedocs.io/)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |
