# Cours d'escalade de compétences

La brique qui manquait après l'examen par paliers (étape 14) : **rien sur la
plateforme n'enseignait**. L'examen teste un palier à froid dès que le
précédent est maîtrisé ; les fiches de remédiation (`fiches-remediation.md`)
réparent une lacune déjà constatée, sur l'hypothèse qu'un enfant a appris
ailleurs, hors plateforme. Étape 15 construit ce que cette hypothèse
supposait : un cours, natif, donné avant d'être testée plutôt qu'après avoir
échoué.

## Donné automatiquement, jamais une porte

Comme l'examen, le cours est donné par la plateforme elle-même — extension
d'un cran de la même exception (voir « La seule chose que la plateforme
assigne » dans `examen-initiation.md`), pas une nouvelle créée. Dès que
`app.assessment.tiers.next_sitting` déclare une compétence due pour le
prochain palier, `app.course.service.give_to` cherche un cours publié
travaillant sur cette compétence et l'assigne, avec la note : « Une leçon
pour découvrir cette compétence avant l'examen. Tu peux aussi passer
l'examen directement si tu penses déjà savoir. »

**Ce n'est pas un préalable obligatoire.** L'examen du palier reste
accessible sans être passé par le cours qui le précède — décision du
propriétaire, 26 août 2026 : une enfant confiante dans la matière n'a pas à
traverser une leçon pour être testée. Les deux sont donnés à la même
lecture, à partir du même `due` calculé une seule fois par
`assessment.service.give_to`, jamais l'un conditionné sur l'autre.

Une compétence déjà testée — réussie ou en échec — sort de `next_sitting`
par construction : son cours ne réapparaît donc jamais après le premier
examen. La remédiation réactive (`quick_repairs`) reste la seule réponse à
un échec.

## Une leçon native, comme une fiche

`ACTIVITY_KIND_COURSE` rejoint `assessment` et `remediation` dans
`AUTHORED_KINDS`, pour les mêmes raisons qu'ADR-017 donnait déjà aux fiches
de remédiation : le rattachement à une compétence par son code métier
n'existe nulle part ailleurs, l'origine de contenu isolée n'est pas toujours
déployée, et une leçon doit expliquer avant d'interroger — ce qu'aucune
banque de questions importée ne fait. `Activity.guidance` porte la leçon,
`authored_questions` ses questions de vérification.

## Une vérification qui ne compte pour rien

C'est la différence décisive avec une fiche. Une fiche complétée produit une
lecture de compétence par les règles de l'étape 10 — c'est ce qui lui permet
de servir de retest. **Un cours, non.** Sa route de vérification
(`POST /api/v1/me/cours/{assignment_id}/answers`) appelle
`app.authored.service.grade` directement contre l'affectation, sans qu'aucune
tentative n'existe, et ne touche jamais `attempts` ni `attempt_responses`.
Elle rend correction et explication sur-le-champ, exactement comme une
fiche, mais rien de ce qui a été répondu n'est conservé.

L'achèvement du cours lui-même — quand une enfant estime avoir fini —
emprunte la route générique déjà construite en 09.3,
`POST /api/v1/me/activities/{id}/complete`. Elle ne touche pas davantage à
une compétence : « terminer n'est pas réussir » vaut pour un cours comme
pour n'importe quelle autre activité.

La maîtrise reste décidée **uniquement** par l'examen du palier, inchangé
depuis l'étape 14.

## Ce qui existe aujourd'hui, et ce qui reste à écrire

Deux cours pilotes, sur des compétences déjà couvertes par une fiche
(`ci-fr-lettres`, `ci-ma-denombrer` — `app/demo/cours.py`) : la boucle
complète (cours, examen, en cas d'échec la fiche existante, retest) est
démontrable de bout en bout sans attendre la couverture des
cinquante-quatre compétences du référentiel. Couvrir le reste est une dette
assumée, à traiter hors étape comme HORS-04 puis HORS-09 l'ont fait pour les
fiches.

## Voir aussi

- `docs/adr/ADR-022-cours-donne-non-bloquant.md`, la décision et les
  alternatives écartées.
- `examen-initiation.md`, pour l'examen que le cours précède.
- `fiches-remediation.md`, pour la remédiation réactive qu'il ne remplace
  pas.
