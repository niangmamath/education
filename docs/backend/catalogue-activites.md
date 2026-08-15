# Catalogue d'activités

## Périmètre

Cette page décrit l'étape 08 : ce qu'est une activité, comment un paquet H5P
entre dans la plateforme, et comment le catalogue se lit. Le référentiel est
décrit dans `referentiel-competences.md`, son import dans
`import-referentiel.md`.

## Le catalogue n'est pas versionné

Le référentiel l'est, parce que des traces le désignent : une tentative de
l'étape 10 doit rester lisible dans l'édition où elle a été écrite. Le catalogue
est autre chose — un **travail éditorial**. L'exercice qui entraîne l'addition
posée l'entraîne encore après une révision du programme.

C'est pourquoi une activité nomme les compétences qu'elle travaille **par leur
code métier** et non par leur ligne. `cm1-math-num-01` désigne la même compétence
d'une édition à l'autre, donc le catalogue survit à la publication d'une nouvelle
édition au lieu d'être reconstruit avec elle. ADR-013 pose la décision et ses
contreparties.

**Le prix en est un lien sans clé étrangère.** Un code qui ne désigne rien est
accepté par la base. Ce lien mort ne casse aucune lecture : l'activité est
simplement absente des résultats filtrés sur ce code — un silence, plus dangereux
qu'une erreur. D'où la commande de vérification, à passer après chaque
publication d'édition :

```bash
docker compose exec -T api python -m app.catalog check
```

```text
Édition    : fictif-2026-01
Liens      : 1
Catalogue cohérent avec l'édition en vigueur.
```

Elle nomme les liens morts, et aussi les activités reliées à aucune compétence :
celles-là ne pourront jamais être recommandées par l'étape 12, ce qui est un
silence du même genre. Code de retour `5` dès qu'il y a quelque chose à corriger.

## Quatre tables

```text
catalog_activities              une activité, son type, sa durée, son statut
├── catalog_activity_competencies  les codes de compétences qu'elle travaille
├── catalog_activity_questions     quelle question travaille quelle compétence
└── catalog_h5p_packages           le paquet vérifié qu'elle joue, le cas échéant
```

`catalog_activity_questions` est arrivée après l'étape 08, avec la dette de
l'étape 10, et elle est **facultative** — c'est tout son intérêt. Sans ses
lignes, la plateforme ne sait pas quelle question porte quelle compétence, et la
lecture d'une tentative vaut pour toutes les compétences de l'activité : grossier
mais honnête. Avec elles, chaque question ne compte que pour ce qu'elle travaille,
et une compétence sans question à elle ne reçoit aucun résultat plutôt qu'un
résultat emprunté.

Rien dans un paquet H5P ne dit cette association ; elle est donc déclarée par qui
enregistre l'activité, seul à la connaître. La lecture qui s'en sert est décrite
dans `tentatives-resultats.md`.

Une activité est `draft`, puis `published`, puis `archived`. Elle ne disparaît
jamais : les résultats des étapes 10 à 12 continueront de la désigner.

Sa durée est bornée entre une et soixante minutes par une contrainte. Un Quick
Repair dure trois à sept minutes, ce qui est une règle produit ; rien dans le
catalogue ne doit prétendre ne prendre aucun temps, ni durer une heure et demie.

## Un paquet H5P n'entre que par une commande

ADR-006 exclut tout éditeur H5P, ADR-012 n'autorise que `H5P.TrueFalse 1.8` et
refuse tout autre type par défaut. Il n'y a donc **ni éditeur ni route de
téléversement** : un paquet est vérifié, stocké et enregistré par quelqu'un qui a
accès au serveur.

```bash
docker compose exec -T api python -m app.catalog register \
  demo-vrai-faux-01 /tmp/paquet.h5p \
  --licence "CC BY 4.0" --source "https://example.org/paquet"
```

```text
Activité   : demo-vrai-faux-01
Type H5P   : H5P.TrueFalse 1.8, autorisé par ADR-012
Empreinte  : 9914c27552f00aa91d4a29e85f6a299b11f984030c3451658fb0246f84b07f3c
Taille     : 1056130 octets
Objet      : packages/9914c2…f3c.h5p
Paquet enregistré.
```

### Ce que la vérification refuse

Un `.h5p` est une archive zip, donc une **entrée non fiable**. L'archive est lue
sans jamais être extraite : rien n'est écrit sur le disque, donc un nom d'entrée
forgé n'a nulle part où s'échapper.

| Refus | Pourquoi |
|---|---|
| type hors ADR-012 | refusé par défaut, avant que le moindre octet n'atteigne le bucket |
| chemin remontant, `../` | *zip slip*, l'attaque classique de l'extraction d'archive |
| chemin absolu | même famille |
| plus de 500 entrées | un paquet n'en a pas besoin |
| déploiement au-delà de cent fois le poids | bombe de décompression, l'intention est sans objet |
| au-delà de 20 Mo, ou vide | bornes simples, et les bornes simples sont celles qui tiennent |
| pas une archive, pas de `h5p.json`, JSON invalide | le fichier ne dit pas ce qu'il joue |

**Le refus du type est doublé par une contrainte en base.** Une règle applicative
se relâche par un changement de configuration ; une contrainte `CHECK` demande
une migration et un amendement d'ADR-012. C'est exactement la friction que la
décision réclamait.

L'empreinte est calculée sur les octets lus, donc ce qui est enregistré est ce
qui a été vérifié, et non ce qu'un nom de fichier prétendait. Elle nomme aussi
l'objet dans le bucket, si bien que les mêmes octets ne s'y trouvent jamais deux
fois.

L'ordre des opérations compte : vérification, puis stockage, puis écriture de la
ligne — et si l'écriture échoue, l'objet est retiré. Un objet sans ligne serait
un orphelin que personne ne revérifiera.

## Les lectures

```text
GET /api/v1/catalog/activities
GET /api/v1/catalog/activities/{code}
GET /api/v1/catalog/kinds
```

**Seules les activités publiées sont servies.** Un brouillon répond exactement
comme une activité qui n'existe pas : savoir qu'une activité se prépare ne
regarde pas un client.

Toute session authentifiée peut lire, Parent comme Enfant, sur le même
raisonnement que les routes du référentiel : ce n'est pas une donnée
personnelle, les deux espaces en ont besoin, et deux chemins de lecture pour la
même donnée finissent par diverger.

| Filtre | Effet |
|---|---|
| `competency` | les activités qui travaillent ce code — la question de l'étape 12 |
| `kind` | `h5p`, `phet` ou `video` |
| `max_duration` | plafond en minutes, le filtre dont un Quick Repair a besoin |

Les filtres se combinent. Un code inconnu rend une page vide plutôt qu'une
erreur. L'ordre est total, durée puis code, pour qu'aucune ligne ne se voie deux
fois ni jamais au fil des pages. Une activité qui travaille deux compétences est
comptée une fois.

**Aucune réponse ne dit où vit un paquet.** Un client apprend qu'une activité
joue `H5P.TrueFalse 1.8` ; ni la clé d'objet, ni l'empreinte, ni la licence, ni
la provenance ne sortent. L'origine de contenu isolée d'ADR-012 est ce qui
remettra le fichier, et aucun chemin de bucket n'a sa place chez un client.

## Ce que l'étape 08 ne fait pas

- Aucune affectation d'une activité à un enfant : c'est l'étape 09.
- Aucun résultat, aucune tentative : étapes 10 et 11.
- Aucune remise de paquet au navigateur : l'origine de contenu isolée reste à
  construire, avec sa CSP et son endpoint xAPI authentifié.
- Aucun antivirus dans le contrôle des paquets : ADR-012 l'exige pour la
  production, et aucun scanner n'est disponible dans l'environnement de stage.
- Aucun import de masse du catalogue : les activités se créent une à une, ce qui
  suffit à un catalogue de démonstration.
