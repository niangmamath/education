import Link from 'next/link';
import { ArrowLeft, CircleHelp } from 'lucide-react';

export const metadata = {
  title: 'Aide',
  description: 'Aide et informations sur le prototype StudentConnect',
};

const topics = [
  {
    title: 'À quoi sert StudentConnect ?',
    text: 'StudentConnect prépare un suivi simple des apprentissages pour les élèves de 6 à 11 ans et leurs parents.',
  },
  {
    title: 'Les espaces Parent et Élève sont-ils disponibles ?',
    text: 'Non. Les parcours sont documentés et seront créés progressivement pendant les prochaines sous-étapes UX.',
  },
  {
    title: 'Les informations affichées sont-elles réelles ?',
    text: 'Non. Les écrans de cette étape utilisent uniquement des exemples fictifs et ne contiennent aucune donnée personnelle.',
  },
];

export default function AidePage() {
  return (
    <main className="container py-5">
      <div className="mx-auto" style={{ maxWidth: '52rem' }}>
        <Link href="/" className="d-inline-flex align-items-center gap-2 mb-4">
          <ArrowLeft size={18} aria-hidden="true" />
          Retour à l’accueil
        </Link>

        <header className="mb-4">
          <span className="sc-feature-icon mb-3" aria-hidden="true"><CircleHelp size={24} /></span>
          <p className="badge rounded-pill text-bg-primary mb-3">Prototype UX</p>
          <h1 className="display-6 fw-bold">Aide et informations</h1>
          <p className="lead text-secondary">Comprendre le périmètre actuel de StudentConnect.</p>
        </header>

        <div className="vstack gap-3">
          {topics.map((topic) => (
            <section className="card border-0 shadow-sm" key={topic.title}>
              <div className="card-body p-4">
                <h2 className="h5">{topic.title}</h2>
                <p className="text-secondary mb-0">{topic.text}</p>
              </div>
            </section>
          ))}
        </div>

        <div className="alert alert-info mt-4" role="note">
          <strong>Besoin d’assistance ?</strong> Le canal de contact sera défini avant la mise à disposition du MVP.
        </div>
      </div>
    </main>
  );
}
