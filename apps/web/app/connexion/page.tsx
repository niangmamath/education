import Link from 'next/link';
import { ArrowLeft, LockKeyhole } from 'lucide-react';

export const metadata = {
  title: 'Connexion',
  description: 'Prototype du futur accès à StudentConnect',
};

export default function ConnexionPage() {
  return (
    <main className="container py-5">
      <div className="mx-auto" style={{ maxWidth: '42rem' }}>
        <Link href="/" className="d-inline-flex align-items-center gap-2 mb-4">
          <ArrowLeft size={18} aria-hidden="true" />
          Retour à l’accueil
        </Link>

        <section className="card border-0 shadow-sm">
          <div className="card-body p-4 p-lg-5">
            <span className="sc-feature-icon mb-3" aria-hidden="true">
              <LockKeyhole size={24} />
            </span>
            <p className="badge rounded-pill text-bg-primary mb-3">Prototype UX</p>
            <h1 className="display-6 fw-bold">Connexion à StudentConnect</h1>
            <p className="lead text-secondary">
              L’authentification n’est pas encore implémentée. Aucun identifiant ne doit être saisi sur cette page prototype.
            </p>

            <div className="alert alert-warning" role="status">
              <strong>Données fictives.</strong> Ce formulaire visuel sera ajouté après la conception et la validation de la sécurité des sessions.
            </div>

            <div className="d-flex flex-wrap gap-3 mt-4">
              <Link href="/" className="btn btn-primary">Revenir à l’accueil</Link>
              <Link href="/aide" className="btn btn-outline-primary">Consulter l’aide</Link>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
