# Prompt général de contexte pour tous les agents

## 1. Identité du projet

Tu travailles sur **StudentConnect**, une plateforme familiale de suivi, d’apprentissage et de remédiation de l’élève, réalisée dans le cadre d’un **stage présentiel à Casablanca**.

Ce projet est totalement distinct d’AgriConnect et de tout travail avec M. Boinzemwendé SANKARA. Ne mélange jamais les documents, personnes, décisions, chemins, dépôts ou livrables de ces projets.

- Organisation GitHub : `tidianesarrndiaye-org`
- Dépôt : `StudentConnect`
- GitHub Project : `Plateforme familiale élève - Stage Casablanca 2026`
- Période de référence : du 5 août au 4 septembre 2026
- Livraison : prototype démontrable `V0.1`
- Données : exclusivement fictives pendant le stage
- Utilisateurs centraux : élève du primaire et son ou ses parents/tuteurs
- Enseignant ou valideur : rôle facultatif et non bloquant pour l’usage familial

## 2. Vision produit

StudentConnect ne cherche pas à refaire Khan Academy, CK-12, H5P, PhET ou Kolibri. StudentConnect constitue une couche longitudinale et transversale qui :

1. centralise le dossier de l’élève ;
2. conserve les évaluations, preuves et observations dans le temps ;
3. distingue la note de la compétence ;
4. détecte des lacunes localisées dans une matière ;
5. relie plusieurs lacunes localisées pour proposer une hypothèse de lacune générale ou transversale ;
6. construit un plan de correction mesurable ;
7. utilise des ressources externes sans perdre le contrôle du dossier ;
8. mesure la progression avant et après correction ;
9. fournit à l’enfant et aux parents une vue simple, positive et actionnable.

## 3. Règles produit non négociables

- Une note ne remplace jamais une compétence.
- Toute nouvelle observation crée un historique. Aucune valeur antérieure ne doit être écrasée.
- Une lacune automatique est une **candidate explicable**, jamais une vérité définitive.
- Une cause probable est une hypothèse, jamais un diagnostic médical, psychologique ou comportemental.
- Une lacune localisée est liée à une compétence précise, un contexte, des preuves et une date.
- Une lacune générale regroupe plusieurs lacunes localisées sans les supprimer.
- Toute lacune traitée doit conduire à un objectif, une activité, un responsable, une échéance, un indicateur et une réévaluation.
- Les formulations doivent être factuelles, positives et non stigmatisantes.
- Chaque ressource externe doit conserver : fournisseur, URL, licence ou conditions, langue, niveau, matière, compétence, mode d’accès, mode de suivi, date de vérification et statut éditorial.
- Gratuit ne signifie pas librement copiable, modifiable ou réhébergeable.
- Aucune API non officielle ne doit devenir une dépendance critique.
- Aucune donnée réelle d’enfant ne doit être utilisée dans le dépôt, les tests, les captures ou la démonstration.
- Aucun secret, cookie, jeton, mot de passe ou fichier `.env` ne doit être commité.

## 4. Stack technique retenue

Utilise cette stack sauf décision d’architecture enregistrée dans un ADR :

- Python 3.12
- Django 5.x
- Django REST Framework
- Django Templates
- **Bootstrap 5** pour l’interface, et non Tailwind CSS
- HTMX et JavaScript natif pour les interactions légères
- PostgreSQL
- pytest, pytest-django et coverage
- Ruff, Black et djLint
- drf-spectacular pour OpenAPI
- Docker Compose
- Git et GitHub
- GitHub Actions
- Gunicorn, Nginx et HTTPS pour la démonstration si l’hébergement le permet

Architecture attendue : **monolithe modulaire Django**, sans microservices pour la V0.1.

## 5. Modules du projet

- M01 : comptes, famille et consentements
- M02 : profil et dossier longitudinal
- M03 : référentiel et carte de compétences
- M04 : catalogue de contenus et ressources
- M05 : parcours de cours et apprentissage
- M06 : évaluations et collecte des preuves
- M07 : détection et gestion des lacunes
- M08 : plan de correction et remédiation
- M09 : espace parent et accompagnement familial
- M10 : tableaux de bord, notifications et progression
- M11 : administration, intégrations, sécurité et offline

Les onze modules sont des domaines ou Epics. Ils ne doivent pas être développés comme onze produits complets pendant le stage.

## 6. Périmètre MVP V0.1

Le prototype doit démontrer ce flux vertical :

`parent/enfant → profil → diagnostic → résultats par compétence → lacune localisée → hypothèse transversale → ressource → activité → plan de correction → réévaluation → progression avant/après`

Limites obligatoires :

- référentiel pilote de 10 à 20 compétences ;
- trois matières maximum ;
- catalogue pilote d’au moins 20 ressources ;
- trois profils d’élèves fictifs ;
- règles simples et explicables ;
- H5P sous forme de preuve de concept ;
- Kolibri sous forme de spike non bloquant ;
- pas d’IA de diagnostic ;
- pas de marketplace, paiement, visioconférence ou gestion complète d’établissement.

## 7. Stratégie EdTech

- H5P : moteur d’activités, diagnostics et réévaluations sous notre contrôle. La collecte xAPI nécessite un hébergement compatible.
- CK-12 : lien ou embed officiel. Les redirections sont acceptées. V0.1 utilise `launch-only` ou `internal-wrapper`, puis un quiz interne.
- Khan Academy et Khan Academy Kids : liens contrôlés. Ne jamais supposer une synchronisation complète de la progression.
- PhET : simulation externe suivie d’un quiz interne.
- Kolibri : spike offline non bloquant utilisant uniquement des interfaces documentées.
- Moodle : éventuel back-office H5P, jamais interface principale des familles.

Modes de suivi autorisés : `none`, `launch-only`, `internal-wrapper`, `xAPI`, `LTI`, `import`, `manual-verified`.

## 8. Organisation du dépôt

Structure cible :

```text
StudentConnect/
├── config/
├── apps/
│   ├── accounts/
│   ├── students/
│   ├── competencies/
│   ├── resources/
│   ├── learning/
│   ├── assessments/
│   ├── gaps/
│   ├── remediation/
│   ├── dashboards/
│   └── audit/
├── templates/
├── static/
├── fixtures/
├── docs/
│   ├── architecture/
│   ├── adr/
│   ├── api/
│   └── user-guide/
├── tests/
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

Ne déplace pas ou ne renomme pas un dossier existant sans analyser les conséquences et consigner la décision.

## 9. GitHub Project et workflow

Statuts : `Backlog`, `Ready`, `In progress`, `In review`, `Blocked`, `Done`.

Priorités : `P0 Critical`, `P1 High`, `P2 Medium`, `P3 Low`.

Itérations :

- I0 : cadrage consolidé, 5 au 11 août
- I1 : conception prête, 12 au 18 août
- I2 : prototype vertical, 19 au 25 août
- I3 : validation finale, 26 août au 4 septembre

Conventions :

- branche courte : `feat/M03-carte-competences`, `fix/M06-score`, `docs/api` ;
- commit : `feat(M03): add competency history` ;
- une fonctionnalité significative doit être liée à une issue et une pull request ;
- aucune tâche ne passe à `Done` sans preuve vérifiable.

## 10. Protocole obligatoire avant toute action

1. Lire `etat.md` à la racine du dossier `steps`.
2. Lire le rapport de l’étape précédente, s’il existe.
3. Lire tous les prompts du dossier de l’étape courante.
4. Inspecter le dépôt réel avant de proposer ou modifier des fichiers.
5. Vérifier les dépendances et les décisions ADR existantes.
6. Ne travailler que sur l’étape assignée.
7. Ne pas élargir silencieusement le périmètre.
8. Si une décision bloque réellement le travail, créer un rapport de blocage au lieu d’inventer une règle métier.

## 11. Protocole obligatoire après réalisation

À la fin de chaque sous-étape, créer dans le dossier de l’étape courante un rapport Markdown nommé :

`rapport_YYYY-MM-DD_HHMM_<slug-de-la-sous-etape>.md`

Le rapport doit contenir :

```markdown
# Rapport de réalisation

## Métadonnées
- Étape :
- Sous-étape :
- Date et heure :
- Agent :
- Issue GitHub :
- Branche :
- Commit ou PR :
- Statut : Terminé | Partiel | Bloqué

## Objectif

## État initial observé

## Travaux réalisés

## Fichiers créés

## Fichiers modifiés

## Commandes exécutées

## Tests exécutés et résultats

## Critères d’acceptation
- [ ] Critère 1
- [ ] Critère 2

## Décisions prises

## Écarts par rapport au prompt

## Risques ou dette technique

## Blocages

## Prochaines actions recommandées

## Mise à jour proposée pour etat.md
```

Ne jamais modifier ou supprimer le rapport d’un autre agent. Créer un nouveau rapport si une correction est nécessaire.

## 12. Règles de non-conflit entre agents

- Une seule étape principale active à la fois, sauf tâches explicitement indépendantes.
- Un agent ne modifie pas les fichiers appartenant à une autre étape sans justification dans le rapport.
- Avant modification, vérifier `git status`, la branche active et les changements non commités.
- Ne jamais écraser une migration Django existante.
- Ne jamais réécrire l’historique Git partagé.
- Ne jamais forcer un push.
- Ne jamais supprimer un fichier inconnu sans recherche dans le dépôt.
- En cas de conflit, arrêter, documenter et placer l’item en `Blocked`.
- Toute décision structurante est inscrite dans `docs/adr/` et référencée dans le rapport.

## 13. Definition of Ready

Une tâche est prête si :

- l’objectif et la valeur utilisateur sont compris ;
- l’Epic, la priorité, l’itération et les dépendances sont renseignés ;
- les critères d’acceptation sont vérifiables ;
- les données de test fictives sont précisées ;
- aucun choix bloquant non identifié ne subsiste.

## 14. Definition of Done

Une tâche est terminée si :

- les critères d’acceptation sont passés ;
- les tests essentiels ont été exécutés ;
- l’interface mobile a été vérifiée si nécessaire ;
- les permissions ont été vérifiées si la tâche touche les données ;
- la documentation est à jour ;
- la CI est réussie si une PR existe ;
- aucun secret ou donnée réelle n’est présent ;
- le rapport de réalisation a été créé ;
- `etat.md` a été mis à jour ou une proposition de mise à jour a été fournie.
