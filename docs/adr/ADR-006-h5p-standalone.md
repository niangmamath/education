# ADR-006 : H5P Standalone et Origine Isolée

## Statut

✅ **Accepted** - Décision validée et implémentée

---

## Contexte

StudentConnect doit permettre aux élèves d'interagir avec des **contenus H5P** (HTML5 Package) de manière **native et sécurisée**, sans redirection vers une plateforme externe.

### Problème à résoudre

Choisir une approche pour :
1. Lire/afficher les paquets H5P dans l'application
2. Capturer les événements xAPI émis par les contenus
3. Isoler les contenus pour des raisons de sécurité
4. Gérer le cycle de vie des paquets (upload, validation, stockage)

### Contraintes

- **Pas d'éditeur H5P complet** (décision dans DECISIONS_FINALES.md)
- **Lecture native** sans redirection
- **Origine de contenu isolée** (décision dans DECISIONS_FINALES.md)
- **Capture xAPI** via dispatcher et bridge postMessage
- **Quarantaine et scan** des paquets uploadés

---

## Décision

**Utiliser `h5p-standalone`** pour la lecture des paquets H5P avec une **origine de contenu isolée**.

### Pipeline H5P

```
Upload → Quarantaine → Scan → Validation → Extraction → Versionnage → Stockage → Lecture
         ↓            ↓           ↓            ↓           ↓         ↓
     h5p-uploads  h5p-quarantine  ZIP check  structure   h5p-stored   CDN/S3
                                             check      versionnée
```

### Architecture de lecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js (Frontend)                          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  H5P Player Component:                                   │  │
│  │  - Charge le paquet H5P depuis S3                       │  │
│  │  - Crée une iframe isolée                               │  │
│  │  - Gère la communication postMessage                    │  │
│  │  - Capturer les événements xAPI                         │  │
│  │  - Envoie les données au backend                        │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │ POST /xapi/statements
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI (Backend)                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  xAPI Endpoint: /xapi/statements                           │  │
│  │  - Reçoit les événements xAPI                            │  │
│  │  - Valide et stocke les données                           │  │
│  │  - Met à jour les progrès de l'élève                      │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Options considérées

### 1. h5p-standalone (Sélectionné)

**Pour** :
- ✅ **Lecture native** dans le navigateur
- ✅ **Pas de dépendance serveur H5P**
- ✅ **Léger et rapide**
- ✅ **Open source** (MIT License)
- ✅ **Actif et maintenu**
- ✅ **Support xAPI intégré**
- ✅ **Compatible** avec les paquets H5P standard

**Contre** :
- ❌ Pas d'éditeur (mais nous n'en avons pas besoin)
- ❌ Certaines fonctionnalités avancées manquantes

**Verdict** : ✅ **Sélectionné** - Parfait pour nos besoins de lecture

---

### 2. Moodle H5P Plugin

**Pour** :
- ✅ Fonctionnalités complètes
- ✅ Éditeur inclus

**Contre** :
- ❌ **Trop lourd** pour nos besoins
- ❌ Dépendance PHP (incompatible avec notre stack)
- ❌ Complexe à intégrer
- ❌ Maintenance difficile

**Verdict** : ❌ **Rejeté** - Incompatible et trop lourd

---

### 3. Iframe vers une plateforme H5P externe

**Pour** :
- ✅ Pas de gestion des paquets
- ✅ Fonctionnalités complètes

**Contre** :
- ❌ **Redirection hors StudentConnect** (interdit)
- ❌ Perte de contrôle sur les données
- ❌ Expérience utilisateur fragmentée
- ❌ Dépendance externe

**Verdict** : ❌ **Rejeté** - Violation de la règle "sans redirection"

---

### 4. Implémentation custom de H5P

**Pour** :
- ✅ Contrôle total
- ✅ Optimisé pour nos besoins

**Contre** :
- ❌ **Très complexe** à implémenter
- ❌ Long à développer
- ❌ Risque de bugs de sécurité
- ❌ Maintenance lourde

**Verdict** : ❌ **Rejeté** - Réinventer la roue

---

## Conséquences

### Pipeline de traitement

1. **Upload** : L'utilisateur upload un fichier .h5p
2. **Quarantaine** : Le fichier est stocké dans un dossier temporaire
3. **Scan** : Vérification du fichier (taille, type MIME, signature ZIP)
4. **Validation** : Vérification de la structure interne du H5P
5. **Extraction** : Extraction du contenu dans un dossier versionné
6. **Versionnage** : Création d'une version unique pour ce paquet
7. **Stockage** : Upload vers S3 avec URL présignée
8. **Indexation** : Enregistrement dans la base de données

### Sécurité

- **Origine isolée** : Les paquets H5P sont servis depuis un sous-domaine dédié (ex: `content.studentconnect.test`)
- **CSP strict** : Content Security Policy pour limiter les capacités de l'iframe
- **Sandboxing** : Attributs sandbox sur l'iframe
- **postMessage** : Communication contrôlée entre iframe et parent
- **xAPI Bridge** : Dispatcher qui valide et filtre les événements avant stockage

### Capture xAPI

```javascript
// Dans le frontend (H5P Player Component)
window.addEventListener("message", (event) => {
  // Vérifier l'origine
  if (event.origin !== "https://content.studentconnect.test") return;
  
  // Vérifier le type de message
  if (event.data.type === "xapi") {
    const statement = event.data.statement;
    
    // Valider le statement
    if (isValidXAPIStatement(statement)) {
      // Envoyer au backend
      fetch("/xapi/statements", {
        method: "POST",
        body: JSON.stringify(statement),
        headers: {"Content-Type": "application/json"}
      });
    }
  }
});
```

---

## Implémentation

### Structure des fichiers

```
apps/web/
├── components/
│   └── H5PPlayer/
│       ├── H5PPlayer.tsx         # Composant principal
│       ├── H5PFrame.tsx          # Iframe isolée
│       ├── XAPIBridge.ts        # Gestion xAPI
│       └── types.ts             # Types TypeScript

apps/api/
├── routes/
│   └── h5p/
│       ├── __init__.py
│       ├── upload.py            # Upload et quarantaine
│       ├── process.py           # Traitement et validation
│       └── xapi.py              # Endpoint xAPI
├── services/
│   └── h5p_service.py          # Service H5P
└── models/
    └── h5p.py                   # Modèles DB
```

### Configuration Docker pour l'origine isolée

```yaml
# docker-compose.yml
services:
  web:
    # ...
  
  content-origin:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./h5p-storage:/usr/share/nginx/html
    environment:
      - NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/templates
      - NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d
    command: |
      sh -c "envsubst < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
```

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| Vulnérabilité XSS | Moyenne | Élevé | CSP strict, sandbox iframe |
| Upload malveillant | Moyenne | Élevé | Scan, validation, quarantaine |
| Fuites de données | Faible | Élevé | Origine isolée, postMessage validé |
| Incompatibilité H5P | Moyenne | Moyen | Tests avec différents types H5P |
| Performance | Faible | Moyen | CDN, caching agressif |

---

## Références

- [h5p-standalone GitHub](https://github.com/tunapanda/h5p-standalone)
- [H5P Specification](https://h5p.org/node/1025)
- [xAPI Specification](https://github.com/adlnet/xAPI-Spec)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [postMessage API](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |

---

## Annexes

### Types H5P autorisés dans le MVP

- H5P.Example - Exemple simple
- H5P.Quiz - Quiz basique
- H5P.InteractiveVideo - Vidéo interactive
- H5P.CoursePresentation - Présentation de cours
- H5P.DragText - Glisser-déposer texte
- H5P.SingleChoiceSet - QCM
- H5P.TrueFalse - Vrai/Faux
- H5P.FillIn - Remplir les blancs

### Bonnes pratiques

1. **Toujours valider** les uploads (taille, type, structure)
2. **Ne jamais faire confiance** au contenu des paquets H5P
3. **Isoler l'exécution** dans une iframe avec sandbox
4. **Limiter les capacités** via CSP
5. **Versionner** chaque paquet pour permettre le rollback
6. **Scanner régulièrement** les paquets stockés
7. **Sauvegarder** les paquets originaux
