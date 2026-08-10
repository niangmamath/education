# ADR-000 : Choix de la licence du projet StudentConnect

## Statut

⚠️ **Proposed** - En discussion, décision non finale

---

## Contexte

Le projet StudentConnect est un projet EdTech B2C développé dans le cadre d'un stage présentiel à Casablanca. Il est crucial de choisir une licence qui :

1. **Protège les droits intellectuels** du travail réalisé
2. **Permet l'utilisation libre** pour les établissements éducatifs
3. **Respecte les licences** des dépendances utilisées (Next.js, FastAPI, H5P, PhET, etc.)
4. **S'aligne avec les valeurs** du projet (éducation, accessibilité)
5. **Est compatible** avec une éventuelle commercialisation future

### Contraintes identifiées

- Le projet utilise des **bibliothèques open source** avec différentes licences (MIT, Apache 2.0, BSD, LGPL)
- Le projet intègre des **contenus tiers** (H5P, PhET) avec leurs propres licences
- Le projet pourrait être **commercialisé** à l'avenir (modèle freemium ou SaaS)
- Le projet est développé dans un **cadre académique** (stage)
- Les données du stage sont **exclusivement fictives**

---

## Décision

**Décision proposée** : Utiliser la licence **AGPL-3.0** (Affero General Public License version 3) avec les exceptions suivantes :

### Licence principale : AGPL-3.0

La licence AGPL-3.0 a été choisie car elle :

- ✅ **Oblige à partager le code source** pour toute utilisation en réseau (SaaS)
- ✅ **Protège contre l'appropriation privée** sans contribution en retour
- ✅ **Est compatible** avec la plupart des licences open source utilisées
- ✅ **Permet une utilisation libre** pour les établissements éducatifs
- ✅ **Est largement reconnue** et testée juridiquement

### Exceptions et clarifications

1. **Contenus H5P** : Les paquets H5P importés conservent leur licence d'origine (généralement GPL ou CC-BY)
2. **Simulations PhET** : Les simulations PhET restent sous licence CC-BY (attribution requise)
3. **Dépendances** : Les bibliothèques tierces restent sous leur licence respective
4. **Données** : Les données fictives créées pour le projet sont libres de droits

### Alternative proposée : Double licence

Une alternative serait d'utiliser une **double licence** :
- **AGPL-3.0** pour la version open source (communauté)
- **Licence propriétaire** pour la version commerciale (entreprises)

---

## Options considérées

### 1. MIT License

**Pour** :
- Très permissive
- Facile à comprendre et à adopter
- Compatible avec presque toutes les dépendances

**Contre** :
- ❌ Ne protège pas contre l'appropriation privée
- ❌ Permet une utilisation commerciale sans contribution
- ❌ Pas de garantie que les améliorations soient partagées

**Verdict** : ❌ Rejetée - Trop permissive, ne protège pas le projet

---

### 2. Apache License 2.0

**Pour** :
- Permet l'utilisation commerciale
- Obligation d'attribution
- Compatible avec la plupart des licences
- protections juridiques (patents)

**Contre** :
- ❌ Ne protège pas contre le SaaS fermé
- ❌ Permet une utilisation sans partager les modifications

**Verdict** : ❌ Rejetée - Ne convient pas pour un projet SaaS

---

### 3. GPL-3.0

**Pour** :
- Obligation de partager le code source
- Protège contre l'appropriation
- Copyleft fort

**Contre** :
- ❌ Moins adaptée pour les applications web/SaaS
- ❌ Certains pays ont des restrictions sur la GPL

**Verdict** : ❌ Rejetée - AGPL est plus adaptée pour les applications web

---

### 4. AGPL-3.0

**Pour** :
- ✅ Spécialement conçue pour les applications web/SaaS
- ✅ Obligation de partager le code source même pour les services en ligne
- ✅ Protège contre l'appropriation privée
- ✅ Compatible avec la plupart des dépendances open source
- ✅ Permet une utilisation libre pour les établissements éducatifs

**Contre** :
- Peut décourager certaines entreprises de l'utiliser
- Complexité juridique légèrement plus élevée

**Verdict** : ✅ **Sélectionnée** - Meilleure adaptation aux besoins du projet

---

### 5. Licence propriétaire

**Pour** :
- Contrôle total sur le code
- Possibilité de commercialisation exclusive

**Contre** :
- ❌ Contradictoire avec les valeurs open source
- ❌ Empêche la collaboration communautaire
- ❌ Doit respecter les licences des dépendances

**Verdict** : ❌ Rejetée - Incompatible avec la philosophie du projet

---

### 6. Double licence (AGPL-3.0 + Propriétaire)

**Pour** :
- Permet une version open source pour la communauté
- Permet une version commerciale pour les entreprises
- Modèle économique éprouvé (ex: GitLab, Elastic)

**Contre** :
- Complexité de gestion
- Nécessite une infrastructure pour gérer les deux versions

**Verdict** : ⚠️ **Alternative viable** - À considérer pour la phase de commercialisation

---

## Conséquences

### Conséquences positives

- Protection juridique du projet
- Encouragement de la contribution communautaire
- Alignement avec les valeurs éducatives
- Possibilité de commercialisation future

### Conséquences négatives

- Certaines entreprises pourraient éviter d'utiliser le projet
- Complexité de gestion des licences des dépendances
- Besoin de vérification juridique

### Risques

- **Risque juridique** : Mauvaise compréhension des obligations de l'AGPL
- **Risque d'adoption** : Certaines organisations évitent l'AGPL
- **Risque de compatibilité** : Vérification nécessaire avec toutes les dépendances

---

## Validation

### Compatibilité avec les dépendances

| Dépendance | Licence | Compatible AGPL-3.0? |
|------------|---------|----------------------|
| Next.js | MIT | ✅ Oui |
| React | MIT | ✅ Oui |
| TypeScript | Apache 2.0 | ✅ Oui |
| Tailwind CSS | MIT | ✅ Oui |
| FastAPI | MIT | ✅ Oui |
| SQLAlchemy | MIT | ✅ Oui |
| PostgreSQL | PostgreSQL License | ✅ Oui |
| Redis | BSD | ✅ Oui |
| Celery | BSD | ✅ Oui |
| h5p-standalone | MIT | ✅ Oui |
| PhET | CC-BY | ⚠️ À vérifier (attribution requise) |

---

## Décisions ouvertes

1. **Modèle de double licence** : Faut-il implémenter une double licence dès maintenant ?
2. **Licence des contenus** : Quelle licence appliquer aux contenus créés pour StudentConnect ?
3. **Attribution PhET** : Comment gérer l'attribution pour les simulations PhET ?
4. **Vérification juridique** : Faut-il consulter un avocat pour valider le choix ?

---

## Prochaines étapes

1. ✅ **Créer cet ADR** en status Proposed
2. ⏳ **Discuter avec l'équipe** et les parties prenantes
3. ⏳ **Consulter un expert juridique** si nécessaire
4. ⏳ **Décider** de la licence finale
5. ⏳ **Créer le fichier LICENSE** avec la licence choisie
6. ⏳ **Mettre à jour** ce document avec la décision finale

---

## Références

- [Texte complet de l'AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html)
- [Choose a License](https://choosealicense.com/)
- [Open Source Initiative - AGPL-3.0](https://opensource.org/license/agpl-v3/)
- [Comparaison des licences](https://tldrlegal.com/)
- [GitHub - Understanding license compatibility](https://docs.github.com/en/repositories/managing-your-repositorys- settings-and-features/customizing-your-repository/licensing-a-repository)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Proposed) |

---

## Annexes

### Comparaison rapide des licences

| Critère | MIT | Apache 2.0 | GPL-3.0 | AGPL-3.0 |
|---------|-----|------------|---------|----------|
| Permissive | ✅ | ✅ | ❌ | ❌ |
| Copyleft | ❌ | ❌ | ✅ | ✅ |
| SaaS-friendly | ✅ | ✅ | ❌ | ✅ |
| Modifications partagées | ❌ | ❌ | ✅ | ✅ |
| Utilisation commerciale | ✅ | ✅ | ⚠️ | ⚠️ |
| Patents | ❌ | ✅ | ❌ | ❌ |

### Recommandation finale

**Recommandation** : Adopter l'**AGPL-3.0** comme licence principale pour StudentConnect, avec une clause d'exception pour les contenus tiers (H5P, PhET) qui conservent leurs licences respectives.

Cette licence offre le meilleur équilibre entre protection du travail et encouragement de la collaboration communautaire, tout en restant compatible avec une éventuelle commercialisation future via un modèle de double licence.
