# Montrer la plateforme à quelqu'un, sans la déployer

## Ce qui bloque le déploiement, en une phrase

**L'API écrit les contenus dans un dossier, nginx les lit dans ce même dossier,
et sur Render un disque n'appartient qu'à un seul service.**

C'est tout. Ce n'est pas un bug, ni quelque chose qu'on aurait oublié de faire :
c'est une limite de l'hébergeur qui rencontre une exigence de sécurité.

### Pourquoi ce dossier partagé existe

ADR-012 demande que les contenus H5P soient servis depuis une **origine
séparée** : un autre nom de domaine que celui de l'application. La raison est
qu'un contenu H5P exécute du JavaScript qu'on n'a pas écrit. S'il était servi
depuis l'origine de l'application, ce JavaScript pourrait lire le cookie de
session, appeler l'API au nom de l'enfant, et lire le tableau de bord de sa
famille. Sur une origine séparée, le navigateur l'en empêche lui-même.

D'où deux programmes :

- **l'API** vérifie le paquet, l'enregistre, et l'ouvre dans `/srv/content` ;
- **nginx** sert `/srv/content` en lecture seule, sur son propre port, et vérifie
  un ticket à chaque requête.

En local, Docker Compose donne aux deux le même volume. Chacun voit ce que
l'autre a écrit. Tout fonctionne.

Sur Render, un disque persistant s'attache à **un** service. Si on le donne à
l'API, nginx ne voit rien ; si on le donne à nginx, l'API ne peut rien écrire.
Il n'y a pas de réglage pour contourner cela.

### Les trois sorties possibles

| Sortie | Coût | Quand |
|---|---|---|
| **Un tunnel vers la pile locale** | zéro | maintenant, et c'est ce que vous voulez |
| L'origine de contenu lit le stockage objet au lieu d'un disque | plusieurs jours | quand il faudra un vrai hébergement |
| API et nginx dans un seul conteneur | moyen | jamais : cela annule l'isolation |

**Le tunnel n'est pas un contournement.** La pile locale est la pile complète,
avec son origine isolée et ses tickets. Un tunnel la rend visible de l'extérieur
sans rien y changer — votre maître de stage verra le site réel, H5P compris,
c'est-à-dire plus que ce que Render pourrait montrer.

## La recette, pour demain

### 1. Démarrer la pile

```bash
docker compose up -d
docker compose ps          # api, content, postgres, redis, storage : running
```

### 2. Ouvrir les deux tunnels

**Deux, et pas un.** Le navigateur doit joindre l'application *et* l'origine de
contenu : c'est le prix de l'isolation, et c'est aussi ce qui la rend réelle.

Dans `~/.config/ngrok/ngrok.yml` :

```yaml
version: "3"
agent:
  authtoken: VOTRE_JETON
tunnels:
  web:
    proto: http
    addr: 3000
  contenu:
    proto: http
    addr: 8081
```

```bash
ngrok start --all
```

Notez les deux adresses affichées.

> Si votre offre ngrok n'autorise qu'un seul tunnel, l'alternative est
> Cloudflare Tunnel, qui en donne plusieurs gratuitement mais demande un nom de
> domaine. **Ne servez pas le contenu depuis l'origine de l'application pour
> économiser un tunnel** : c'est exactement la protection qu'ADR-012 met en
> place.

### 3. Dire à la plateforme quelles sont ses adresses publiques

Dans `.env`, à la racine :

```dotenv
CONTENT_ORIGIN_URL=https://VOTRE-CONTENU.ngrok-free.app
```

Cette adresse part dans l'iframe, donc dans le navigateur : elle doit être celle
que le navigateur peut joindre, pas `localhost`.

```bash
docker compose restart api
```

### 4. Démarrer le web en lui donnant son hôte public

```bash
cd apps/web
PUBLIC_HOST=VOTRE-WEB.ngrok-free.app pnpm run build
PUBLIC_HOST=VOTRE-WEB.ngrok-free.app pnpm run start
```

**Cette variable n'est pas facultative.** Next vérifie l'origine de chaque action
serveur pour se protéger du CSRF ; derrière un tunnel, l'hôte que voit le
navigateur n'est pas celui que voit Next, et **toute connexion échoue** — se
connecter *est* une action serveur. `PUBLIC_HOST` déclare l'hôte du tunnel, et
rien d'autre n'est ouvert : sans la variable, la liste reste vide.

### 5. Vérifier avant la démonstration, pas pendant

Depuis un autre appareil, sur le réseau mobile plutôt que le wifi de la maison —
c'est ce qui prouve que le tunnel sert vraiment :

1. la page d'accueil s'affiche ;
2. la connexion parent aboutit — si elle échoue, `PUBLIC_HOST` est en cause ;
3. l'espace enfant montre l'examen ;
4. une fiche de remédiation s'ouvre et répond ;
5. une activité H5P se joue — si le cadre reste vide, `CONTENT_ORIGIN_URL` est
   resté sur `localhost`.

## Ce qu'il faudra faire un jour

L'origine de contenu doit lire les paquets depuis le **stockage objet** au lieu
d'un disque, en gardant sa vérification de ticket. MinIO est déjà là et l'API y
écrit déjà chaque paquet vérifié : la pièce manquante est côté origine, qui sert
aujourd'hui des fichiers ouverts sur un disque.

C'est un vrai morceau de travail, pas un réglage — et rien ne presse tant qu'une
démonstration passe par un tunnel.
