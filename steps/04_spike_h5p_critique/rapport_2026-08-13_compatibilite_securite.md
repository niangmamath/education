# Rapport de compatibilité et de sécurité H5P

## Métadonnées

- Étape : `04_spike_h5p_critique`
- Sous-étape : `04_analyser_compatibilite_securite`
- Date : 13 août 2026
- Branche : `spike/h5p-critical`
- Portée : paquet pilote `H5P.TrueFalse 1.8`
- Statut : **Analyse terminée pour le type pilote uniquement**

## Résumé exécutif

Le spike démontre qu’un paquet `H5P.TrueFalse 1.8` peut être contrôlé, extrait, rendu localement avec `h5p-standalone 3.8.2` et produire un statement xAPI réel. La solution est viable pour poursuivre l’expérimentation, mais elle n’est pas encore prête pour une intégration de production.

## Compatibilité validée

- [x] Archive `.h5p` reconnue comme ZIP valide.
- [x] Contrôle CRC réussi.
- [x] `h5p.json` et `content/content.json` présents.
- [x] Bibliothèque principale `H5P.TrueFalse 1.8` reconnue.
- [x] Extraction locale avec refus des chemins absolus, `..` et liens symboliques.
- [x] `h5p-standalone 3.8.2` fonctionne sous Node.js 22 et pnpm 11.
- [x] Treize bibliothèques H5P uniques normalisées.
- [x] Cinquante-trois assets JavaScript et CSS déclarés vérifiés.
- [x] Rendu dans Microsoft Edge via serveur local WSL.
- [x] Image, question, réponses et résultat visibles.
- [x] Interaction `Yes`, contrôle et score `1/1` fonctionnels.
- [x] Événements `attempted` et `answered` observés.
- [x] Statement xAPI `answered` validé avec score, succès, complétion et réponse.
- [x] Aucun CDN externe requis pendant le rendu observé.

## Types H5P

| Type | Décision actuelle | Justification |
|---|---|---|
| `H5P.TrueFalse 1.8` | Autorisé pour le pilote local | Rendu et xAPI validés avec le paquet identifié par son SHA-256 |
| `H5P.MultiChoice 1.16` | Reporté | Présélectionné, mais aucun paquet, rendu ou statement testé |
| `H5P.Blanks 1.14` | Reporté | Présélectionné, mais saisie textuelle et variantes non testées |
| Tout autre type | Refusé par défaut | Aucun test réel ni décision explicite |

## Sécurité de l’archive

Les contrôles du spike couvrent :

- le nombre maximal de fichiers ;
- la taille maximale d’un fichier décompressé ;
- la taille décompressée totale ;
- les chemins absolus ;
- les segments `..` ;
- les liens symboliques ;
- la présence des manifests ;
- la bibliothèque principale attendue ;
- les taux de compression suspects.

### Limites

- Les seuils sont expérimentaux et doivent devenir une politique backend configurable.
- Le contrôle antivirus n’est pas encore implémenté.
- Aucune quarantaine objet n’est encore connectée à MinIO.
- L’archive n’est pas encore traitée par un worker isolé.
- Les extensions et types MIME ne sont pas encore contrôlés par une liste d’autorisation complète.

## Sécurité d’exécution

Le contenu H5P exécute du JavaScript fourni par les bibliothèques autorisées. Une intégration de production devra donc prévoir :

1. une liste d’autorisation par `machineName`, version majeure et version mineure ;
2. un inventaire et une empreinte des bibliothèques déployées ;
3. une isolation dans une iframe dédiée ;
4. une origine distincte ou un sous-domaine dédié au runtime H5P ;
5. une politique CSP restrictive et testée ;
6. l’interdiction des ressources réseau externes non autorisées ;
7. la désactivation de l’export et de l’embed par défaut ;
8. la validation des médias et de leurs licences ;
9. un stockage privé avant publication ;
10. une journalisation sans données personnelles sensibles.

## Dépendances et reproductibilité

- `h5p-standalone` est verrouillé à `3.8.2`.
- `h5p-cli` est verrouillé à `1.1.4` pour la préparation expérimentale.
- Le paquet exporté depuis H5P.org ne contenait pas toutes les bibliothèques d’exécution.
- Les bibliothèques ont été récupérées séparément, puis normalisées.
- Le dossier `temp/` du CLI ne doit jamais écraser le dossier compilé `libraries/`.
- Les fichiers générés, `node_modules`, le runtime et le paquet `.h5p` restent hors de Git.

### Risque de chaîne d’approvisionnement

Le CLI H5P a installé et construit des dépendances anciennes, avec des avertissements et des vulnérabilités signalées dans l’environnement expérimental. Le CLI ne doit donc pas être exécuté à la demande dans le chemin de production. Les bibliothèques autorisées devront être préparées hors ligne, contrôlées, figées et publiées comme artefacts internes.

## Licence et provenance

- La bibliothèque `H5P.TrueFalse` est sous licence MIT.
- Le manifest global du paquet déclare `U`, licence non divulguée.
- Le média intégré est déclaré Public Domain dans `Rights of use`.
- L’auteur et la source du média sont enregistrés dans les preuves.
- Le paquet complet reste hors de Git.
- L’autorisation actuelle couvre uniquement l’usage local pour le spike.

## xAPI et protection des données

- L’acteur capturé utilise un UUID pseudonyme.
- Aucun nom ou email réel n’est présent dans la preuve.
- Le statement H5P ne contient pas de timestamp source.
- La date `validatedAtUtc` date uniquement la validation technique.
- En production, le serveur de collecte devra ajouter une date de réception sans modifier silencieusement la signification du statement source.
- La liaison entre l’acteur pseudonyme et l’utilisateur StudentConnect devra rester côté serveur et être protégée par les règles d’accès.

## Décision

**Poursuivre sous conditions.**

`H5P.TrueFalse 1.8` est autorisé pour le pilote local et peut servir de base au futur lecteur. Aucune autorisation de production ou d’ouverture à d’autres types H5P n’est accordée à ce stade.

## Conditions avant production

- [ ] Pipeline backend d’import et de quarantaine.
- [ ] Analyse antivirus et contrôle MIME.
- [ ] Liste d’autorisation versionnée des bibliothèques.
- [ ] Artefacts runtime préparés et signés, sans exécution du CLI en production.
- [ ] Isolation iframe et CSP testées.
- [ ] Stockage privé et publication contrôlée.
- [ ] Endpoint xAPI authentifié, autorisé et validé.
- [ ] Politique de timestamp et d’idempotence.
- [ ] Tests d’accessibilité, de performance et multi-navigateurs.
- [ ] Validation juridique de chaque contenu publié.

## Prochaine action

Clôturer le spike avec une décision d’architecture, mettre à jour le suivi et préparer la fusion de la branche après les contrôles finaux.
