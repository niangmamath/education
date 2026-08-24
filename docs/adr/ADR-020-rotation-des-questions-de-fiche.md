# ADR-020, Une réserve de huit questions par fiche, quatre tirées à chaque tentative

- Statut : Accepté
- Date : 24 août 2026

## Contexte

Les quinze fiches de remédiation posaient chacune exactement quatre questions
fixes, toujours les mêmes, toujours dans le même ordre. Le propriétaire a
signalé qu'un enfant qui reprend une fiche — parce que le diagnostic la lui
repropose, ou parce qu'un parent la redonne — voit littéralement les quatre
mêmes questions une seconde fois, ce qui invite à mémoriser la réponse plutôt
qu'à retravailler la compétence.

L'examen d'entrée n'est **pas** concerné : le propriétaire l'a explicitement
laissé hors périmètre. Il se passe une fois par classe, à l'inscription et à
chaque passage (ADR-018) ; la question de la répétition ne s'y pose pas de la
même façon, et ADR-019 venait déjà de tripler son nombre de questions par
compétence pour une raison différente — mesurer une compétence, pas éviter
une reprise.

## Décision

### Une réserve de huit, quatre servies

Chaque fiche passe de quatre questions à une réserve de huit. À chaque lecture
de la fiche, `app.authored.service.questions_of` en tire quatre au hasard —
`FICHE_QUESTIONS_SERVED`, une constante posée dans `app.api.v1.fiches` plutôt
que dans le module de lecture, pour la même raison que toute autre politique
propre à un type d'activité : ce module lit des questions, il ne décide pas
combien en montrer. L'examen ne passe jamais ce paramètre et continue de
recevoir sa réserve entière, exactement comme avant.

### Le tirage est stable pour une tentative, pas pour la fiche

Le tirage utilise `random.Random(seed).sample(...)`, où `seed` est l'identifiant
de la tentative en cours (`app.attempts.service.running_attempt`, nouvellement
public). Tant qu'une tentative reste ouverte, chaque lecture de la fiche
retire exactement les mêmes quatre questions, dans le même ordre : un enfant
qui recharge la page ne doit pas voir les questions changer sous ses yeux
pendant qu'elle y répond. Une nouvelle tentative — la fiche reprise depuis le
début — porte un nouvel identifiant et tire donc à nouveau.

Aucune migration, aucune colonne ajoutée : l'identifiant de la tentative
existe déjà et suffit de graine. Avant qu'une tentative existe (l'enfant n'a
pas encore appuyé sur « commencer »), la lecture tire sans graine fixe ; la
page ne montre de toute façon que la leçon à ce moment-là, jamais les
questions elles-mêmes.

### Le contenu, pas seulement le mécanisme

Les quatre questions ajoutées par fiche (soixante au total) reprennent le même
style, la même compétence et la même explication après chaque réponse que les
quatre déjà écrites — aucune ne recopie une question de l'examen sur la même
compétence, pour que les deux réserves restent réellement distinctes.

## Conséquences

**Cent vingt questions de fiche existent désormais**, contre soixante avant.
`test_the_bank_has_room_to_draw_from` épingle que chaque fiche déborde
strictement ce qu'une tentative en sert, pour que la rotation ne redevienne
pas silencieusement un service intégral si une fiche future oublie d'écrire
plus de quatre questions.

**Les trente-neuf compétences encore sans fiche devront viser huit questions
dès l'écriture**, et non quatre suivies d'un rattrapage — la dette mesurée par
`test_the_sheets_cover_the_competencies_they_are_written_for` ne change pas de
nombre pour autant : c'est une convention pour ce qui reste à écrire, pas une
correction de ce qui existe déjà.

**Le tirage ne peut pas se démontrer par un seul appel HTTP.** L'identifiant
d'une tentative est généré côté serveur ; rien ne permet à un test de le
choisir pour forcer deux tirages à différer. `TestTheDrawItself` vérifie donc
la fonction directement, avec des graines choisies à l'avance et déjà connues
pour produire des tirages différents — zéro dépendance au hasard réel dans la
suite de tests.

## Alternatives écartées

**Ajouter une colonne pour mémoriser les questions déjà servies.** Aurait
permis d'éviter toute répétition entre deux tentatives consécutives, mais
demandait une migration et une politique de purge (que faire après la
dixième tentative, quand la réserve est épuisée ?) pour un problème que le
tirage aléatoire résout déjà en pratique, avec 70 combinaisons possibles sur
une réserve de huit.

**Étendre la réserve de l'examen de la même façon.** Écarté par le
propriétaire : l'examen mesure une compétence une fois par classe, il n'est
jamais repris de la même façon qu'une fiche, et le tripler par ADR-019
répondait déjà à un besoin différent.
