import Link from 'next/link';
import { ArrowRight, BarChart3, BookOpen, Rocket, Users } from 'lucide-react';

const features = [
  {
    icon: BookOpen,
    title: 'Arbre de compétences',
    description: 'Modélisation des prérequis et dépendances entre compétences.',
  },
  {
    icon: BarChart3,
    title: 'Suivi compréhensible',
    description: 'Des indicateurs expliqués aux familles, sans score fictif présenté comme réel.',
  },
  {
    icon: Users,
    title: 'Espaces distincts',
    description: 'Des parcours séparés pour les parents et les élèves de 6 à 11 ans.',
  },
  {
    icon: Rocket,
    title: 'Activités courtes',
    description: 'Des exercices ciblés et de courte durée, à valider dans le futur produit.',
  },
];

export default function HomePage() {
  return (
    <div className="sc-public-page d-flex min-vh-100 flex-column">
      <header className="border-bottom bg-white" aria-label="En-tête principal">
        <div className="container py-3">
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-3">
            <Link href="/" className="d-inline-flex align-items-center gap-3 text-decoration-none">
              <span className="sc-brand-mark" aria-hidden="true">SC</span>
              <span>
                <span className="d-block fw-bold text-dark">StudentConnect</span>
                <span className="d-block small text-secondary">Plateforme EdTech</span>
              </span>
            </Link>
            <span className="badge rounded-pill text-bg-warning">Prototype UX</span>
          </div>
        </div>
      </header>

      <main id="contenu-principal" className="flex-grow-1">
        <section className="sc-hero py-5">
          <div className="container py-lg-4">
            <div className="row align-items-center g-5">
              <div className="col-lg-7">
                <p className="badge rounded-pill text-bg-primary mb-3">Exemple fictif</p>
                <h1 className="display-4 fw-bold mb-3">Suivre les apprentissages, simplement.</h1>
                <p className="lead text-secondary mb-4">
                  StudentConnect prépare un espace clair pour les élèves de 6 à 11 ans et leurs parents.
                </p>
                <div className="d-flex flex-wrap gap-3">
                  <Link href="/connexion" className="btn btn-primary btn-lg">
                    Se connecter
                    <ArrowRight className="ms-2" size={20} aria-hidden="true" />
                  </Link>
                  <Link href="/aide" className="btn btn-outline-primary btn-lg">Découvrir le projet</Link>
                </div>
                <p className="small text-secondary mt-3 mb-0">
                  Les parcours présentés sont des prototypes. L’authentification et les données métier ne sont pas encore implémentées.
                </p>
              </div>
              <div className="col-lg-5">
                <div className="card border-0 shadow-sm sc-highlight-card">
                  <div className="card-body p-4 p-lg-5">
                    <h2 className="h4">Deux expériences complémentaires</h2>
                    <ul className="list-unstyled mb-0 mt-4">
                      <li className="d-flex gap-3 mb-3">
                        <span className="sc-list-marker" aria-hidden="true">1</span>
                        <span><strong>Espace Parent</strong><br /><span className="text-secondary">Synthèse, difficultés et prochaines actions.</span></span>
                      </li>
                      <li className="d-flex gap-3">
                        <span className="sc-list-marker" aria-hidden="true">2</span>
                        <span><strong>Espace Élève</strong><br /><span className="text-secondary">Objectifs courts, activités et progression simple.</span></span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="py-5 bg-white" aria-labelledby="fonctionnalites-title">
          <div className="container">
            <div className="mb-4">
              <p className="text-uppercase fw-semibold text-primary small mb-2">Vision du MVP</p>
              <h2 id="fonctionnalites-title" className="h1 mb-2">Un accompagnement lisible</h2>
              <p className="text-secondary mb-0">Ces éléments décrivent le périmètre cible, pas des fonctions déjà disponibles.</p>
            </div>
            <div className="row g-4">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <div className="col-md-6 col-xl-3" key={feature.title}>
                    <article className="card h-100 border-0 shadow-sm">
                      <div className="card-body p-4">
                        <span className="sc-feature-icon mb-3" aria-hidden="true"><Icon size={24} /></span>
                        <h3 className="h5">{feature.title}</h3>
                        <p className="text-secondary mb-0">{feature.description}</p>
                      </div>
                    </article>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="py-5" aria-labelledby="etat-title">
          <div className="container">
            <div className="card border-primary-subtle bg-primary-subtle">
              <div className="card-body p-4 p-lg-5 d-lg-flex align-items-center justify-content-between gap-4">
                <div>
                  <h2 id="etat-title" className="h3">Le socle technique est en cours de construction</h2>
                  <p className="mb-0 text-secondary">Consultez la route technique pour vérifier l’état local des services.</p>
                </div>
                <Link href="/health" className="btn btn-primary mt-3 mt-lg-0 flex-shrink-0">Vérifier l’état technique</Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-top bg-white py-4">
        <div className="container d-flex flex-column flex-sm-row justify-content-between gap-2 small text-secondary">
          <span>© 2026 StudentConnect.</span>
          <span>Prototype avec Next.js 16 et Bootstrap 5.3.8.</span>
        </div>
      </footer>
    </div>
  );
}
