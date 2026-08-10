# Security Policy

## Supported Versions

Les versions actuellement supportées reçoivent des correctifs de sécurité :

| Version | Supported | EOL Date |
|---------|----------|----------|
| V0.1 (en développement) | ✅ Oui | À déterminer |

## Reporting a Vulnerability

### Processus de reporting

1. **Ne pas ouvrir d'Issue publique** - Ne pas exposer la vulnérabilité publiquement
2. **Envoyer un email** à : `security@tidianesarrndiaye-org.com` (à configurer)
3. **Ou utiliser GitHub Security Advisories** (quand disponible)
4. **Inclure les informations suivantes** :
   - Description détaillée de la vulnérabilité
   - Étapes pour reproduire
   - Impact potentiel
   - Version affectée
   - Preuve de concept (si applicable)

### Temps de réponse

| Severity | First Response | Resolution Target |
|----------|---------------|-------------------|
| Critical | 24 heures | 7 jours |
| High | 48 heures | 14 jours |
| Medium | 72 heures | 30 jours |
| Low | 7 jours | 60 jours |

## Security Commitments

### Protection des données

- ✅ **Zéro donnée réelle** : Toutes les données du stage sont fictives
- ✅ **Protection des enfants** : Aucun email ou téléphone requis pour les comptes enfants
- ✅ **Minimisation des données** : Seules les données nécessaires sont collectées
- ✅ **Chiffrement** : Données sensibles chiffrées au repos et en transit

### Authentification et Autorisation

- ✅ **Sessions sécurisées** : Cookies HttpOnly, Secure, SameSite
- ✅ **Mots de passe** : Hachage avec bcrypt ou Argon2
- ✅ **Principe du moindre privilège** : Accès minimal requis
- ✅ **Vérification d'email** : Pour les comptes parents

### Protection des API

- ✅ **Rate Limiting** : Limitation des requêtes par client
- ✅ **CORS** : Configuration stricte des origines autorisées
- ✅ **Validation des entrées** : Toutes les entrées sont validées
- ✅ **Sanitization des sorties** : Prévention des XSS

### Infrastructure

- ✅ **HTTPS** : Tout le trafic est chiffré
- ✅ **Reverse Proxy** : Nginx ou équivalent pour le routage
- ✅ **Headers de sécurité** : CSP, X-Frame-Options, etc.
- ✅ **Logs structurés** : Pour l'audit et le debugging

## Security Headers

Les headers de sécurité suivants sont configurés :

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-src 'self' https://phet.colorado.edu; object-src 'none'; base-uri 'self'; form-action 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
```

## Security Best Practices

### Pour les développeurs

1. **Ne jamais commiter de secrets**
   - `.env` et fichiers similaires sont dans `.gitignore`
   - Utiliser des variables d'environnement
   - Vérifier avec `git-secrets` avant de push

2. **Validation des entrées**
   ```python
   # FastAPI avec Pydantic
   from pydantic import BaseModel, constr
   
   class UserCreate(BaseModel):
       username: constr(strip_whitespace=True, min_length=3, max_length=50)
       email: EmailStr
   ```

3. **Sanitization des sorties**
   ```typescript
   // Next.js avec escape HTML
   import { escape } from 'html-escaper';
   const safeOutput = escape(userInput);
   ```

4. **SQL Injection**
   ```python
   # SQLAlchemy ORM (sécurisé)
   from sqlalchemy import text
   result = db.session.execute(
       text("SELECT * FROM users WHERE email = :email"),
       {"email": user_email}
   )
   
   # NE PAS FAIRE :
   # cursor.execute(f"SELECT * FROM users WHERE email = '{user_email}'")
   ```

5. **XSS Prevention**
   - Toujours échapper le HTML avant rendu
   - Utiliser des frameworks qui échappent automatiquement (React, Next.js)
   - Pour les contenus riches (H5P), utiliser des iframes isolées

### Pour les utilisateurs

1. **Mot de passe fort** : Minimum 12 caractères, mélange de types
2. **2FA** : À implémenter pour les comptes parents
3. **Sessions** : Déconnexion automatique après inactivité
4. **Appareils** : Vérification des nouveaux appareils

## Security Testing

### Outils utilisés

- **SAST** : Bandit (Python), ESLint (JavaScript/TypeScript)
- **DAST** : OWASP ZAP (à intégrer dans CI)
- **Dependency Scanning** : Dependabot, Snyk
- **Secret Scanning** : GitHub Secret Scanning, TruffleHog
- **Container Scanning** : Trivy, Docker Scout

### Commandes de vérification

```bash
# Scanner les secrets dans le code
trufflehog git file://. --since-commit HEAD

# Scanner les vulnérabilités Python
bandit -r apps/api/

# Scanner les vulnérabilités JavaScript
npm audit

# Scanner les dépendances vulnérables (Python)
safety check

# Scanner les conteneurs
trivy image studentconnect-web:latest
```

## Incident Response

### Classification des incidents

| Level | Description | Response Team |
|-------|-------------|---------------|
| Level 1 | Vulnérabilité théorique | Équipe Dev |
| Level 2 | Accès non autorisé tenté | Équipe Dev + Lead |
| Level 3 | Accès non autorisé réussi | Équipe Dev + Lead + Security |
| Level 4 | Compromission des données | Tous + External Security |

### Procédure de réponse

1. **Détection** : Identification de l'incident
2. **Containment** : Limiter l'impact (2 heures max)
3. **Éradication** : Supprimer la menace (24 heures max)
4. **Récupération** : Restaurer les services (48 heures max)
5. **Review** : Analyse post-incident (1 semaine max)
6. **Documentation** : Rapport complet

## Security Contacts

| Role | Email | Responsabilité |
|------|-------|----------------|
| Security Lead | security@tidianesarrndiaye-org.com | Coordination |
| Dev Team | dev@tidianesarrndiaye-org.com | Implémentation |
| Incident Response | incident@tidianesarrndiaye-org.com | Urgences |

## Acknowledgements

Merci aux chercheurs de sécurité qui contribuent à la sécurité de StudentConnect.

---

*Dernière mise à jour : 10 août 2026*
