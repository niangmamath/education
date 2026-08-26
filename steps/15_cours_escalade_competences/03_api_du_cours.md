# 15.3, API du cours

## Objectif

Exposer la lecture d'un cours et la vérification de ses questions, sans
jamais passer par une tentative — pour que la décision « aucune conséquence
sur la maîtrise » soit garantie par l'absence d'écriture plutôt que par une
convention à respecter.

## Prérequis

- 15.1 et 15.2 terminées ;
- `app/api/v1/fiches.py` et `app/authored/service.py` relus.

## Livrables

- `app/api/v1/cours.py` :
  - `GET /me/activities/{assignment_id}/cours` : leçon (`guidance`) et
    questions de vérification, via `open_sheet_for` renommée
    `open_authored_activity_for` (elle ne vérifiait déjà que `kind in
    AUTHORED_KINDS`, sans rien de spécifique aux fiches).
  - Une route de vérification qui appelle `app.authored.service.grade`
    directement contre l'affectation (extension de `grade` pour accepter
    un `assignment_id` plutôt qu'une `Attempt`, dont elle n'utilisait que
    ce champ) et renvoie correction et explication **sans écrire dans
    `attempts` ni `attempt_responses`**. Les trois appelants existants de
    `grade` (fiches, examen, script de démonstration) mis à jour en
    conséquence, comportement inchangé pour eux.
  - Achèvement du cours par la route générique existante
    `POST /me/activities/{id}/complete`, sans modification.
- Correction en chemin : `app/diagnostic/remediation.py:quick_repairs`
  exclut désormais explicitement `assessment` et `course`
  (`Activity.kind.not_in(_NOT_A_REPAIR)`), en plus de la bande de durée. Une
  première version restreignait à tort la sélection au seul `remediation` ;
  la suite de tests complète a montré que `quick_repairs` a toujours
  vocation à proposer une réparation en H5P ou PhET, pas seulement une
  fiche native, et la correction a été reprise en conséquence.
- Correction en chemin, trouvée par la même suite de tests :
  `GET /catalog/kinds` et le filtre de `GET /catalog/activities`
  n'excluaient que `assessment`. Un cours, donné automatiquement comme
  l'examen et non parcouru par un parent, rejoint l'exclusion
  (`app/api/v1/catalog.py:_NOT_BROWSABLE`).

## Hors périmètre

- le contenu pilote lui-même (15.4) ;
- toute route d'écriture pour l'administration du cours.

## Contrôles

- état Git et diff propres ;
- Ruff, Mypy, Pytest ;
- test dédié : répondre à une question du cours laisse
  `attempts`/`attempt_responses` inchangés et `quick_repairs` ne propose
  jamais un cours.

## Statut

Terminé.
