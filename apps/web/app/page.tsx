import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { PrerequisiteThread, type ThreadLink } from '../components/ui/prerequisite-thread';
import { api } from '../lib/api';
import type { PublicStats } from '../lib/types';

/**
 * La page d'accueil ouvre sur ce que le produit sait faire et que personne
 * d'autre ne montre : remonter d'une difficulté visible au prérequis qui la
 * cause. Pas une promesse, un exemple travaillé — le même que celui qu'un
 * parent verra sur la fiche de son enfant, avec le même fil.
 */

const CHAIN: ThreadLink[] = [
  {
    title: 'Poser une soustraction',
    state: 'reporte',
    verdict: 'Reportée',
    note: 'Deux tentatives, la même erreur au même endroit. Cette compétence dépend du dénombrement, qui n’est pas assuré : la proposer maintenant reviendrait à refaire échouer au même mur.',
  },
  {
    title: 'Dénombrer une collection jusqu’à 20',
    state: 'travail',
    verdict: 'À travailler maintenant',
    note: 'Le prérequis. C’est ici que la difficulté commence, et c’est donc ici qu’on travaille.',
  },
  {
    title: '« Compter les jetons » — 4 minutes',
    state: 'neutre',
    verdict: 'Proposée au parent',
    note: 'Une activité courte sur cette seule difficulté. Elle vous est proposée : c’est vous qui la donnez, ou pas.',
  },
];

const REFUSALS = [
  {
    rule: 'Une note ne remplace jamais une compétence.',
    why: 'Un pourcentage dit qu’il y a un problème sans dire lequel. Chaque réponse est rattachée à une compétence du référentiel, et c’est cette lecture-là qui est affichée.',
  },
  {
    rule: 'Une lacune est un candidat, pas un verdict.',
    why: 'Elle arrive accompagnée de la règle qui l’a produite et des réponses dont elle vient. Vous pouvez la lire, et ne pas être d’accord.',
  },
  {
    rule: 'Une observation n’écrase jamais l’historique.',
    why: 'Une réévaluation s’ajoute à ce qui a été observé. Rien ne réécrit le passé d’un enfant.',
  },
  {
    rule: 'Aucun enfant n’est comparé à un autre.',
    why: 'Pas de classement, pas de moyenne de classe, aucun niveau attribué. L’indicateur de santé scolaire s’explique en une phrase et ne se compare à rien.',
  },
  {
    rule: 'Rien n’est donné à votre place.',
    why: 'La plateforme propose les remédiations, elle ne les assigne pas. La seule exception est le test d’entrée, sans lequel elle ne sait rien.',
  },
];

export default async function HomePage() {
  const stats = await api<PublicStats>('/public/stats');

  return (
    <div className="sc-public-page d-flex min-vh-100 flex-column">
      <header className="border-bottom bg-white" aria-label="En-tête principal">
        <div className="container py-3">
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-3">
            <Link href="/" className="d-inline-flex align-items-center gap-3 text-decoration-none">
              <span className="sc-brand-mark" aria-hidden="true">SC</span>
              <span>
                <span className="sc-marque-nom d-block">StudentConnect</span>
                <span className="sc-marque-role d-block">Français et mathématiques · 6 à 11 ans</span>
              </span>
            </Link>
            <nav className="d-flex align-items-center gap-2" aria-label="Accès au compte">
              <Link href="/aide" className="btn btn-link btn-sm">Comment ça marche</Link>
              <Link href="/connexion" className="btn btn-outline-primary btn-sm">Se connecter</Link>
            </nav>
          </div>
        </div>
      </header>

      <main id="contenu-principal" className="flex-grow-1">
        <section className="sc-hero sc-reglure py-5" aria-labelledby="these-title">
          <div className="container py-lg-4">
            <div className="row g-5 align-items-start">
              <div className="col-lg-6 sc-entree">
                <p className="sc-oeilleton sc-oeilleton-indigo">Ce que fait la plateforme</p>
                <h1 id="these-title" className="sc-titre-geant mb-4">
                  Votre enfant rate ses soustractions.
                  <br />
                  Le problème est peut-être le&nbsp;dénombrement.
                </h1>
                <p className="lead mb-4">
                  Un court test d’entrée, lu réponse par réponse et compétence par
                  compétence. Quand une difficulté apparaît, la plateforme remonte
                  jusqu’au prérequis qui la cause, et propose de travailler
                  celui-là.
                </p>
                <div className="d-flex flex-wrap gap-2 mb-3">
                  <Link href="/inscription" className="btn btn-primary btn-lg">
                    Créer un compte parent
                  </Link>
                  <Link href="/connexion/eleve" className="btn btn-outline-primary btn-lg">
                    Je suis un élève
                    <ArrowRight className="ms-2" size={19} aria-hidden="true" />
                  </Link>
                </div>
                <p className="small text-secondary mb-0">
                  Un compte enfant ne demande ni adresse e-mail ni numéro de
                  téléphone : un pseudo et le code de votre famille suffisent.
                </p>
              </div>

              <div className="col-lg-6 sc-entree sc-entree-2">
                <div className="card sc-highlight-card h-100">
                  <div className="card-body p-4 p-lg-5">
                    <p className="sc-oeilleton">Exemple · Léa, CE1</p>
                    <h2 className="h4 mb-4">Comment cette conclusion a été obtenue</h2>
                    <PrerequisiteThread
                      links={CHAIN}
                      label="Chaîne de prérequis, de la difficulté observée à l’activité proposée"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {stats.ok ? (
          <section className="py-5 bg-white border-top border-bottom" aria-labelledby="chiffres-title">
            <div className="container">
              <p className="sc-oeilleton sc-oeilleton-indigo">En ce moment sur la plateforme</p>
              <h2 id="chiffres-title" className="h1 mb-4">
                Ce que ces chiffres comptent, et rien de plus
              </h2>
              <div className="row g-4">
                <div className="col-6 col-lg-3">
                  <p className="sc-chiffre-geant">{stats.data.families}</p>
                  <p className="text-secondary mb-0">
                    famille{stats.data.families > 1 ? 's' : ''} accompagnée
                    {stats.data.families > 1 ? 's' : ''}
                  </p>
                </div>
                <div className="col-6 col-lg-3">
                  <p className="sc-chiffre-geant sc-chiffre-geant-acquis">{stats.data.children}</p>
                  <p className="text-secondary mb-0">
                    enfant{stats.data.children > 1 ? 's' : ''} suivi
                    {stats.data.children > 1 ? 's' : ''}
                  </p>
                </div>
                <div className="col-6 col-lg-3">
                  <p className="sc-chiffre-geant sc-chiffre-geant-travail">
                    {stats.data.activities_completed}
                  </p>
                  <p className="text-secondary mb-0">
                    activité{stats.data.activities_completed > 1 ? 's' : ''} terminée
                    {stats.data.activities_completed > 1 ? 's' : ''}
                  </p>
                </div>
                <div className="col-6 col-lg-3">
                  <p className="sc-chiffre-geant">
                    {stats.data.competencies_covered}
                    <span className="sc-chiffre-total">/{stats.data.competencies_total}</span>
                  </p>
                  <p className="text-secondary mb-0">compétences du référentiel travaillées</p>
                </div>
              </div>
              <p className="text-secondary small mt-4 mb-0">
                Des comptes, jamais des noms : aucun de ces nombres ne se rattache à un
                enfant identifiable, et ils ne comparent rien — ni les enfants entre eux,
                ni les familles.
              </p>
            </div>
          </section>
        ) : null}

        <section className="py-5" aria-labelledby="refus-title">
          <div className="container">
            <div className="row g-5">
              <div className="col-lg-4">
                <p className="sc-oeilleton">Règles du produit</p>
                <h2 id="refus-title" className="h1 mb-3">
                  Cinq choses que la plateforme ne fera pas
                </h2>
                <p className="text-secondary mb-0">
                  Ce ne sont pas des fonctions manquantes. Ce sont des décisions,
                  tenues par les tests, et c’est à elles qu’on reconnaît un
                  diagnostic d’un bulletin.
                </p>
              </div>
              <div className="col-lg-8">
                <ul className="list-unstyled d-flex flex-column gap-4 mb-0">
                  {REFUSALS.map((item) => (
                    <li className="sc-marge" key={item.rule}>
                      <h3 className="h5 mb-1">{item.rule}</h3>
                      <p className="text-secondary mb-0">{item.why}</p>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section className="py-5 bg-white border-top" aria-labelledby="espaces-title">
          <div className="container">
            <p className="sc-oeilleton">Deux publics, deux écrans</p>
            <h2 id="espaces-title" className="h1 mb-4">
              Le parent lit le raisonnement. L’enfant voit une activité.
            </h2>
            <div className="row g-4">
              <div className="col-md-6">
                <article className="card h-100">
                  <div className="card-body p-4 p-lg-5">
                    <p className="sc-oeilleton sc-oeilleton-indigo">Espace parent</p>
                    <h3 className="h4 mb-3">Ce qui est acquis, ce qui coince, et pourquoi</h3>
                    <p className="text-secondary mb-3">
                      Chaque compétence porte son état et la lecture dont il vient.
                      Une difficulté reportée reste visible : elle est expliquée,
                      pas cachée.
                    </p>
                    <p className="text-secondary mb-0">
                      Les remédiations vous sont proposées une par une, avec leur
                      durée et la compétence qu’elles visent.
                    </p>
                  </div>
                </article>
              </div>
              <div className="col-md-6">
                <article className="card h-100">
                  <div className="card-body p-4 p-lg-5">
                    <p className="sc-oeilleton">Espace élève</p>
                    <h3 className="h4 mb-3">Une seule chose à faire, et le temps qu’elle prend</h3>
                    <p className="text-secondary mb-3">
                      Aucun diagnostic n’apparaît de ce côté-ci : ni lacune, ni
                      score, ni nom de règle. Une activité, sa durée, et ce qui a
                      déjà été réussi.
                    </p>
                    <p className="text-secondary mb-0">
                      Les activités durent de trois à sept minutes et ne portent
                      que sur une difficulté à la fois.
                    </p>
                  </div>
                </article>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-top bg-white py-4">
        <div className="container d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-2 small text-secondary">
          <span>© 2026 StudentConnect</span>
          <nav className="d-flex flex-wrap gap-3" aria-label="Liens de bas de page">
            <Link href="/aide" className="text-secondary">Aide</Link>
            <Link href="/accessibilite" className="text-secondary">Accessibilité</Link>
            <Link href="/health" className="text-secondary">État des services</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
