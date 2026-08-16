# Tableaux de bord

Le premier moment où le web appelle l'API. La décision d'architecture est
ADR-016 ; les données viennent des étapes 09 à 12, sans qu'aucune ne soit
recalculée ici.

## Le chemin d'une donnée

```
navigateur  ──►  Next.js (serveur)  ──►  API
   │                (cookie de session lu ici)
   │
   └── iframe ──►  origine de contenu (nginx)
                        │  postMessage
                        ▼
                   Next.js /api/xapi  ──►  API
```

**Le navigateur ne connaît que l'origine du web.** Il ne détient ni adresse
d'API, ni jeton. `API_URL` est une variable du serveur et n'est jamais
`NEXT_PUBLIC_`.

Les mutations passent par des **actions serveur** nommées une par une — se
connecter, commencer une activité, terminer une tentative, donner les
remédiations. Il n'y a pas de proxy générique : ce qui n'a pas d'action n'est pas
atteignable depuis le navigateur.

`POST /api/xapi` est la seule route d'API du web, et elle existe parce que seul
le navigateur peut relayer ce que dit le runtime de contenu.

## Ce que voit l'Élève

| Page | Ce qu'elle montre |
|---|---|
| `/eleve` | L'activité en cours d'abord, puis ce qu'il y a à faire, sa progression en une phrase, et de quoi s'entraîner |
| `/eleve/activites` | Tout ce qui lui a été donné, ce qui est dû en premier |
| `/eleve/activites/[id]` | Le contenu, dans son iframe, et le bouton « J'ai terminé » |
| `/eleve/activites/[id]/resultat` | Ce que l'activité a montré, avec la phrase de chaque conclusion |
| `/eleve/progression` | Chaque compétence observée et son dernier mot |

**L'activité en cours passe avant tout le reste.** C'est le seul élément
réellement urgent de la page, et l'enterrer sous la liste de ce qui reste serait
le plus sûr moyen qu'elle ne soit jamais finie.

**Aucun diagnostic nulle part.** Ni score, ni lacune, ni nom de règle. Ce qui lui
est proposé, ce sont des activités et leur durée. Ses résultats et sa progression
restent à sa disposition et s'expliquent chacun — c'est la *présentation comme
diagnostic* qui est réservée à l'adulte.

**Rien n'est classé par ordre de gravité.** Les compétences sont listées comme
l'API les rend, par code. Une page qui s'ouvrirait sur les échecs serait une page
sur l'échec.

## Ce que voit le Parent

| Page | Ce qu'elle montre |
|---|---|
| `/parent` | Ses enfants, la santé académique de chacun, les points d'attention, ce qui a changé |
| `/parent/enfants` | Les profils, leur état, et le code de la famille |
| `/parent/enfants/[id]` | Le diagnostic complet, avec ses raisons, et le bouton qui donne les activités proposées |
| `/parent/activites` | Tout ce qui a été donné, annulations comprises |
| `/parent/notifications` | Ce qui a changé, et ce que cette page n'est pas |
| `/parent/parametres` | La famille, et les règles publiées |

**Chaque conclusion porte la phrase qui l'a produite.** Un parent qui ne peut pas
discuter une conclusion se fait seulement dire quoi penser.

**Les lacunes reportées sont montrées à part**, avec ce qu'elles attendent. Rien
n'est proposé pour elles délibérément, et un silence qu'un parent ne peut pas
s'expliquer se lirait comme un oubli.

**Un point d'attention reporté n'est pas compté** sur le tableau de bord ni dans
les notifications : le signaler pousserait vers la compétence que la plateforme a
justement décidé de ne pas travailler encore.

## Les notifications ne notifient rien

C'est la lecture stricte du « sans automatisme trompeur » de la fiche, et elle
est assumée : **rien n'est envoyé nulle part**. Aucun e-mail ne part, aucune
alerte n'est poussée, rien n'est stocké, et il n'y a pas d'état « lu » — donc pas
de pastille de non-lus, parce qu'une pastille revendiquerait un état que personne
ne tient.

Ce qui existe est une **relecture** de faits qu'un parent aurait trouvés en
ouvrant trois pages : une activité terminée, une difficulté à confirmer, une
activité qui attend depuis plus d'une semaine. La page le dit en toutes lettres.

Le calcul est fait côté web et non dans l'API, délibérément : un modèle de
notification, avec sa remise, ses canaux et son état de lecture, est le sujet de
l'étape 14, et en inventer la moitié maintenant laisserait cette étape discuter
avec une demi-implémentation.

## La boucle du MVP, enfin entière

```
Parent donne une activité
→ l'enfant la commence
→ le contenu H5P se joue sur son origine isolée
→ ses événements xAPI remontent par postMessage, puis par /api/xapi
→ l'enfant termine, la tentative est lue
→ la lacune et le score sont recalculés
→ le tableau de bord Parent le montre
```

Chaque flèche a été éprouvée sur la pile vivante à la clôture de l'étape.

## Ce que l'étape 13 ne fait pas

- **Aucune modification de profil.** Créer, activer et désactiver un enfant
  restent des appels d'API sans écran ; c'est de l'administration, et c'est
  l'étape 15.
- **Aucune notification remise.** Étape 14.
- **Aucun écran de récompenses.** Rien ne les calcule, et une page qui en
  montrerait mentirait.
- **Aucun test automatisé du web.** La CI web tient TypeScript, ESLint et le
  build ; les parcours ont été éprouvés à la main sur la pile vivante et les
  preuves sont dans le rapport. C'est une dette, et elle est écrite comme telle.
