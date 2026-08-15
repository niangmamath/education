# Points ouverts de l'authentification, stratégies de résolution

Trois écarts subsistaient après la sous-étape 06.2. Cette page décrit pour chacun
l'état constaté, les options et la voie recommandée.

**Point 1 réglé le 14 août 2026** : ADR-005 a été amendée, l'option A ci-dessous
ayant été retenue. Le constat et les options sont conservés pour mémoire du
raisonnement. Les points 2 et 3 restent ouverts.

---

## 1. Argon2id face à la mention bcrypt d'ADR-005, réglé

### Résolution

ADR-005 porte depuis le 14 août 2026 une section « Amendement » qui nomme
Argon2id, la bibliothèque `argon2-cffi`, ses paramètres par défaut alignés sur la
RFC 9106 et le réhachage à la connexion. L'extrait de modèle mentionnant bcrypt
est signalé comme antérieur à l'amendement, la référence bcrypt a été remplacée et
l'historique de l'ADR porte la ligne correspondante.

### Constat d'origine

`app/core/security.py` hache les mots de passe en **Argon2id**. ADR-005 écrit
`hashed_pin = Column(String(255))  # bcrypt hash` dans son extrait de modèle et
cite la documentation bcrypt en référence. Sa section **Décision** ne nomme
pourtant aucun algorithme : elle fixe le principe des sessions par cookie et le
stockage Redis, rien de plus. L'écart porte donc sur du texte illustratif, pas
sur une décision formelle. Il doit malgré tout être levé, sans quoi la prochaine
personne qui lira l'ADR implémentera bcrypt.

### Options

| Option | Contenu | Coût | Effet |
|---|---|---|---|
| A. Amender ADR-005 | Ajouter une sous-section « Algorithme de hachage » à la Décision, corriger l'extrait illustratif, ajouter une ligne d'historique | Faible | L'ADR dit ce que fait le code |
| B. Nouvel ADR dédié | Un ADR « Hachage des secrets d'authentification » au prochain numéro libre, ADR-005 le référence | Moyen | Traçabilité plus nette si le projet tient à des ADR immuables |
| C. Revenir à bcrypt | Remplacer `argon2-cffi` par `bcrypt`, adapter `security.py` et ses tests | Moyen | Aligne le code sur la lettre de l'extrait, mais retient l'algorithme le moins recommandé |

### Recommandation

**Option A.** Argon2id est en tête des recommandations OWASP devant bcrypt,
précisément parce que son coût mémoire rend l'attaque par matériel dédié bien
plus chère. Documenter le choix coûte moins cher que de dégrader la sécurité pour
respecter un commentaire de code.

Contenu à écrire dans ADR-005 : l'algorithme, la bibliothèque `argon2-cffi`, le
fait que les paramètres retenus sont ceux par défaut de la bibliothèque, alignés
sur le profil de la RFC 9106, et la présence de `check_needs_rehash` qui fait
migrer une empreinte vers des paramètres plus récents à la connexion suivante.

### Fenêtre de décision

À trancher **maintenant**. Les seules empreintes existantes sont fictives et
jetables. `check_needs_rehash` fait évoluer les paramètres d'un même algorithme,
mais ne sait pas migrer d'un algorithme à un autre : une fois de vrais comptes
créés, changer d'algorithme impose de conserver les deux vérificateurs et de
re-hacher à la volée pendant des mois.

---

## 2. Vérification de l'adresse email

### Constat

ADR-005 place une vérification entre l'inscription et la connexion, avec un
`GET /auth/parent/verify?token=…`. Le champ `is_verified` existe sur le modèle et
reste à `false`. La connexion ne l'exige pas, faute de quoi aucun compte ne
pourrait se connecter : **l'infrastructure ne comporte aucun service d'envoi
d'emails**. Le blocage est infrastructurel avant d'être applicatif.

### Stratégie en trois mouvements

**Premier mouvement, le transport.** Rien ne peut avancer sans lui, et le choix
mérite un ADR car il engage un fournisseur externe. En développement, ajouter un
service `mailpit` à `docker-compose.yml` : il capte tout ce qu'on lui envoie et
l'expose dans une interface web, donc le parcours devient testable sans qu'aucun
message ne parte réellement. En production, un fournisseur SMTP ou API reste à
choisir. Isoler l'envoi derrière une petite abstraction avec une implémentation
console par défaut évite que ce choix ne bloque le reste.

L'envoi doit passer par une tâche Celery, déjà en place depuis l'étape 03 : un
serveur SMTP lent ne doit pas allonger le temps de réponse de l'inscription.

**Deuxième mouvement, le jeton.** Reprendre exactement le motif des sessions,
déjà écrit et testé : jeton opaque de 32 octets, entrée Redis indexée par
`verify:<sha256(jeton)>` contenant l'identifiant du parent, durée de vie de
vingt-quatre heures, et suppression à la consommation pour garantir l'usage
unique. Prévoir un renvoi de message, lui-même limité en débit, sans quoi un
parent dont le message est perdu reste bloqué.

**Troisième mouvement, la politique.** Décider ce que `is_verified` interdit
réellement. Deux positions défendables :

- **Barrière à la connexion**, conforme à la lettre d'ADR-005, mais qui rend
  toute démonstration impossible si l'envoi tombe en panne ;
- **Barrière aux actions sensibles** : la connexion reste ouverte, mais créer un
  profil Enfant, en 06.3, exige un compte vérifié. Le drapeau devient signifiant
  sans transformer une panne d'envoi en interruption de service.

La seconde est recommandée pour le MVP, la première une fois le transport fiable.

### Rattachement au planning

Le planning est figé et aucune fiche ne couvre l'envoi d'emails. Ce travail
relève soit d'un addendum à l'étape 06, soit de l'étape 15, administration,
sécurité et exploitation. Le choix appartient au propriétaire du planning.

---

## 3. Limitation de débit sur la connexion

### Constat

`RATE_LIMIT` et `RATE_LIMIT_PERIOD` figurent dans `app/core/config.py` mais ne
sont branchés nulle part. Aujourd'hui, seul le coût d'Argon2id freine une attaque
par force brute sur `POST /auth/parent/login`. C'est la surface la plus exposée du
backend.

**Depuis 06.3, la connexion Enfant fait exception.** Six chiffres ne résistant pas
à un script, un compteur d'échecs par enfant a été branché sur
`POST /auth/child/login` et lève `RateLimitException` au-delà du plafond. Ce
compteur protège un profil, pas le service : il ne compte que par enfant, jamais
par origine, et ne couvre pas la connexion Parent. Le reste de ce point demeure
donc entier. La mécanique est décrite dans `acces-enfant.md`.

### Stratégie

**Aucune infrastructure nouvelle n'est nécessaire.** Redis est déjà une
dépendance et le chemin d'authentification l'ouvre déjà à chaque requête. Un
compteur `INCR` assorti d'un `EXPIRE` posé au premier incrément suffit.

**Compter les échecs, pas les requêtes.** Compter les requêtes pénalise un parent
qui se connecte normalement plusieurs fois ; compter les échecs ne gêne que
l'attaquant. Le compteur est remis à zéro à la première connexion réussie.

**Deux axes, tous les deux nécessaires.** Un compteur par compte arrête l'attaque
ciblée sur une adresse connue. Un compteur par adresse IP arrête le balayage
d'un grand nombre de comptes depuis une source unique. L'un sans l'autre laisse
passer la moitié des scénarios.

**Ne pas écrire les adresses email en clair dans Redis.** Indexer par
`login:fail:email:<sha256(email)>`, faute de quoi la base Redis devient un
annuaire des adresses attaquées, donc des adresses qui existent.

**Ralentir plutôt que verrouiller.** Un verrouillage dur transforme l'attaque en
déni de service : il suffit de saisir des mots de passe faux pour interdire à un
parent l'accès à son compte. Un compteur dont la durée de vie s'allonge à chaque
palier freine l'attaquant sans offrir ce levier.

**Piège à ne pas manquer.** Derrière un proxy, l'adresse IP vue par l'application
est celle du proxy. Lire `X-Forwarded-For` sans restriction rend la limite
contournable par un simple en-tête forgé ; l'en-tête ne doit être accepté que
depuis une liste de proxys connus, sinon il faut s'en tenir à l'IP de connexion.

### Rattachement au planning

L'étape 15 couvre la sécurité applicative et c'est sa place naturelle. Le risque
étant immédiat et le coût faible, un compteur d'échecs par compte peut aussi être
tiré dès la clôture de l'étape 06. Arbitrage à rendre par le propriétaire du
planning.
