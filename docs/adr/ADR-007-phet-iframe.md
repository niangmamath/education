# ADR-007 : Intégration PhET via Iframe

## Statut

✅ **Accepted** - Décision validée et implémentée

---

## Contexte

StudentConnect doit intégrer des **simulations PhET** (Physics Education Technology) pour enrichir l'expérience d'apprentissage des élèves avec des simulations scientifiques interactives.

### Problème à résoudre

Choisir une méthode pour intégrer les simulations PhET qui :
1. Permet une **intégration native** dans StudentConnect
2. Respecte les **licences PhET** (CC-BY)
3. Offre une **expérience utilisateur fluide**
4. **Sécurise** l'intégration
5. Permet de **capturer les interactions** (si nécessaire)

### Contraintes

- **Simulations HTML5 françaises uniquement** (décision dans DECISIONS_FINALES.md)
- **Attribution et licence vérifiées**
- **Origine isolée** (iframe sécurisée)
- **Preuve finale** vient d'un mini-test StudentConnect (pas de dépendance externe)

---

## Décision

**Intégrer les simulations PhET via des iframes sécurisées** depuis le site officiel PhET, avec vérification de l'attribution et de la licence.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js (Frontend)                          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  PhET Component:                                          │  │
│  │  - Liste des simulations autorisées                     │  │
│  │  - Iframe vers phet.colorado.edu/fr                      │  │
│  │  - Sandbox et CSP pour sécurité                          │  │
│  │  - Communication postMessage (optionnelle)              │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              PhET Official Server (phet.colorado.edu)          │
│  - Simulations HTML5 françaises                                  │
│  - Attribution CC-BY respectée                                  │
│  - Pas de tracking externe (à vérifier)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Options considérées

### 1. Iframe vers PhET officiel (Sélectionné)

**Pour** :
- ✅ **Pas de téléchargement** des simulations (gain de place)
- ✅ **Toujours à jour** avec les dernières versions
- ✅ **Pas de maintenance** côté StudentConnect
- ✅ **Respect des licences** (lien vers la source)
- ✅ **Attribution claire** via le footer PhET
- ✅ **Sécurité** : PhET gère la sécurité de leurs simulations

**Contre** :
- ❌ **Dépendance externe** (si PhET est down, les sims ne marchent pas)
- ❌ **Moins de contrôle** sur l'UX
- ❌ **Difficile de capturer** les interactions (xAPI)

**Verdict** : ✅ **Sélectionné** - Meilleur compromis

---

### 2. Téléchargement et hébergement local

**Pour** :
- ✅ **Indépendance** (pas de dépendance externe)
- ✅ **Contrôle total** sur l'UX
- ✅ **Capture xAPI possible**

**Contre** :
- ❌ **Taille de stockage** (les sims PhET sont lourdes)
- ❌ **Maintenance** des mises à jour
- ❌ **Respect des licences** à gérer
- ❌ **Bande passante** pour servir les sims
- ❌ **Vérification légales** nécessaire

**Verdict** : ❌ **Rejeté** - Complexité et risques juridiques

---

### 3. Réimplémentation des simulations

**Pour** :
- ✅ Contrôle total
- ✅ Intégration parfaite

**Contre** :
- ❌ **Extremement complexe**
- ❌ **Violation des licences** PhET
- ❌ **Qualité inférieure** aux simulations officielles
- ❌ **Temps de développement prohibitif**

**Verdict** : ❌ **Rejeté** - Impossible et illégal

---

## Conséquences

### Avantages

- **Intégration rapide** : Pas besoin de télécharger ou configurer quoi que ce soit
- **Contenu toujours à jour** : Les élèves bénéficient des dernières améliorations
- **Respect des licences** : Lien clair vers PhET avec attribution
- **Sécurité** : Les simulations tournent dans une iframe sandboxée
- **Performance** : Les sims sont servies par le CDN de PhET

### Inconvénients

- **Dépendance externe** : Si PhET est indisponible, les sims ne fonctionnent pas
- **Pas de capture d'interaction** : Difficile de savoir ce que fait l'élève
- **UX moins intégrée** : Les sims ont l'air "externes"

### Mitigations

- **Liste blanche** : Maintenir une liste de simulations autorisées
- **Fallback** : Message d'erreur clair si PhET est down
- **Cache local** : Optionnel : cache des sims les plus utilisées
- **Proxy** : Optionnel : proxy les requêtes via StudentConnect

---

## Implémentation

### Sélection des simulations

Les simulations doivent être :
1. **En HTML5** (pas de Flash)
2. **En français** (ou avec support français)
3. **Pertinentes** pour le programme scolaire marocain (6-11 ans)
4. **Compatibles mobile**

### Liste initiale suggérée

| Simulation | URL | Sujet | Niveau |
|------------|-----|-------|--------|
| fraction-matcher | /fr/simulation/fraction-matcher | Maths | CM1-CM2 |
| area-builder | /fr/simulation/area-builder | Maths | CE2-CM1 |
| balancing-act | /fr/simulation/balancing-act | Physique | CM1-CM2 |
| circuit-construction-kit-dc | /fr/simulation/circuit-construction-kit-dc | Physique | CM1-CM2 |
| density | /fr/simulation/density | Physique | CM2 |
| energy-skate-park | /fr/simulation/energy-skate-park | Physique | CM1-CM2 |
| gravity-and-orbits | /fr/simulation/gravity-and-orbits | Physique | CM2 |
| molecule-polarity | /fr/simulation/molecule-polarity | Chimie | CM2 |

### Composant React/Next.js

```tsx
// components/PhET/PhETSimulation.tsx
import React, { useState } from 'react';

interface PhETSimulationProps {
  simulationId: string;
  title: string;
  description?: string;
}

const ALLOWED_SIMS = [
  'fraction-matcher',
  'area-builder',
  'balancing-act',
  // ...
];

export const PhETSimulation: React.FC<PhETSimulationProps> = ({
  simulationId,
  title,
  description
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  
  if (!ALLOWED_SIMS.includes(simulationId)) {
    return <div>Simulation non autorisée</div>;
  }
  
  const phetUrl = `https://phet.colorado.edu/fr/simulation/${simulationId}`;
  
  return (
    <div className="phet-simulation">
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      
      <div className="simulation-container">
        <iframe
          src={phetUrl}
          title={`PhET: ${title}`}
          allowFullScreen
          sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
          referrerPolicy="no-referrer"
          onLoad={() => setIsLoaded(true)}
          className={isLoaded ? 'loaded' : 'loading'}
        />
        {!isLoaded && <div className="loading-placeholder">Chargement...</div>}
      </div>
      
      <div className="phet-attribution">
        Simulation PhET - <a href={phetUrl} target="_blank" rel="noopener">Ouvrir dans un nouvel onglet</a>
      </div>
    </div>
  );
};
```

### Sécurité

- **Sandbox** : Limite les capacités de l'iframe
- **CSP** : Content Security Policy pour empêcher le chargement de ressources externes non autorisées
- **Referrer Policy** : no-referrer pour éviter de fuiter des informations
- **Liste blanche** : Seules les simulations autorisées peuvent être chargées

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| PhET indisponible | Faible | Élevé | Message d'erreur, retry automatique |
| Changement de licence PhET | Très faible | Élevé | Surveillance des annonces PhET |
| Simulation supprimée | Faible | Moyen | Vérification périodique des URLs |
| Problème de compatibilité | Faible | Moyen | Tests sur différents navigateurs |

---

## Références

- [PhET Simulations](https://phet.colorado.edu/fr/)
- [PhET License](https://phet.colorado.edu/fr/about/licensing)
- [CC-BY License](https://creativecommons.org/licenses/by/4.0/)
- [Iframe Security](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#attr-sandbox)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |
