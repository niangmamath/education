# Runtime de contenu

## Périmètre

Cette page décrit la sous-étape 11.0 : comment un paquet vérifié devient un
contenu jouable, et pourquoi il est servi depuis une **autre origine** que
l'application. La vérification du paquet est décrite dans
`catalogue-activites.md`, l'affectation dans `affectations.md`.

## Pourquoi une seconde origine

ADR-012, condition 5 : *runtime isolé par iframe et origine dédiée avec CSP
restrictive*.

Un contenu H5P est du JavaScript tiers. Il a besoin de `eval` et de scripts en
ligne pour fonctionner du tout. Le servir depuis l'origine de l'application
reviendrait à lui donner accès aux cookies de session, au stockage local et à
tout ce que l'application y garde — et aucune CSP ne rattrape cela, puisque le
navigateur considérerait le contenu comme faisant partie du site.

La séparation est donc la mesure elle-même, et non un durcissement supplémentaire :
**le contenu tourne sur une origine qui n'a rien à voler.** Pas de cookie, pas de
stockage, aucune capacité d'atteindre quoi que ce soit qui en ait.

C'est aussi ce qui rend acceptables les `unsafe-inline` et `unsafe-eval` de sa
CSP : ils sont nécessaires au runtime H5P, et ils ne coûtent rien là où il n'y a
rien à prendre.

## Ce qui remplace le cookie : un ticket

Le corollaire de la séparation est que **le cookie de session ne voyage pas**
jusqu'à l'origine de contenu. Il fallait donc autre chose pour dire qu'une
requête est autorisée.

C'est un **ticket** : une valeur opaque, frappée par l'API quand un enfant ouvre
une activité qu'il est en train de faire, gardée trente minutes dans Redis, et
vérifiée par l'origine de contenu à chaque fichier servi.

```text
Enfant ─── GET /me/activities/{id}/content ──▶ API
                                                │ vérifie l'affectation
                                                │ frappe un ticket (Redis)
       ◀── play_url = origine/player/play.html?c=<empreinte>&t=<ticket>
       │
       └── iframe ──▶ origine de contenu ─── auth_request ──▶ API
                                                              204 ou 403
```

Le ticket ne porte **aucune identité** : il nomme une affectation et le contenu
qu'il ouvre, rien d'autre. Il est rangé sous son empreinte, exactement comme une
session : qui lit Redis apprend quels contenus sont ouverts, jamais les tickets
qui les ouvrent.

L'origine de contenu, elle, n'apprend jamais qui est qui. Elle demande, et elle
obéit.

| Requête | Réponse |
|---|---|
| ticket valide pour ce contenu | le fichier |
| ticket valide pour **un autre** contenu | `403` |
| ticket inventé, expiré, révoqué | `403` |
| aucun ticket | `403` |
| la page du lecteur, sans ticket | servie — elle ne contient rien |

Un ticket pour un autre contenu est refusé exactement comme un ticket absent :
un ticket ouvre un contenu, et rien n'aide à en deviner un second.

## Le déploiement

Un `.h5p` est une archive ; le lecteur veut un dossier. Le déploiement est
l'étape entre les deux, et c'est **là que l'archive est enfin ouverte** — après
avoir été vérifiée en 08.2, jamais avant.

```bash
# une fois : les bibliothèques et le lecteur préparés hors ligne
docker compose exec -T api python -m app.catalog deploy-runtime /tmp/prepared

# par activité : le paquet vérifié
docker compose exec -T api python -m app.catalog deploy demo-vrai-faux-01
```

L'archive est **relue depuis le bucket**, jamais depuis une copie qui traînerait
sur le disque : ce qui est servi doit être ce qui a été vérifié. Les contrôles de
chemin de l'inspection sont rejoués à l'écriture — non par méfiance envers le
premier contrôle, mais envers l'intervalle entre les deux.

L'empreinte nomme le dossier, `content/<empreinte>/`, donc redéployer les mêmes
octets est idempotent et deux paquets différents ne peuvent pas se télescoper.

Les **bibliothèques** sont préparées hors ligne, condition 3 d'ADR-012, et un
inventaire de leurs empreintes est écrit à côté d'elles : un artefact que
personne ne peut nommer n'est pas figé.

## La disposition servie

```text
/srv/content/
├── player/          le bundle h5p-standalone, et notre page play.html
├── libraries/       les bibliothèques figées, partagées par tous les contenus
├── content/<empreinte>/   un paquet ouvert
└── inventory.json   les empreintes des bibliothèques
```

Le volume est monté **en lecture seule** dans l'origine de contenu : elle sert ce
que l'API a déposé, et ne peut rien y ajouter.

`play.html` est la seule partie de cette origine que nous ayons écrite, et la
seule qui décide de ce qui en sort. Elle ne parle jamais à l'API et ne détient
aucun identifiant qui le lui permettrait : elle remonte les événements xAPI au
parent par `postMessage`, le seul canal que deux origines ont le droit de
partager.

## Ce que 11.0 ne fait pas

- **Aucune ingestion des événements xAPI** : la page les remonte par
  `postMessage`, personne ne les reçoit encore. C'est 11.1, et c'était la raison
  de construire ceci d'abord — un récepteur sans producteur ne s'éprouve qu'avec
  des requêtes fabriquées à la main.
- **Aucune intégration web** : le web n'appelle pas encore l'API, et le faire
  suppose de régler la session entre deux origines. Cela vient avec l'étape 13,
  où les dashboards sont alimentés en données réelles pour la première fois.
- Aucun antivirus, toujours, condition 2 d'ADR-012 pour la production.
- Aucune purge des contenus déployés qui ne servent plus.
