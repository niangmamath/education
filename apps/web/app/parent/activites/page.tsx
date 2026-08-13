import { BookOpen } from 'lucide-react';
import { PrototypeNotice } from '../../../components/ui/prototype-notice';

export const metadata = { title: 'Activités Parent' };

export default function ParentActivitiesPage() {
  return (
    <>
      <PrototypeNotice />
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Espace Parent</p>
        <h1 className="h2 mb-2">Activités</h1>
        <p className="text-secondary mb-0">Consulter les activités recommandées et récentes.</p>
      </header>

      <section className="card border-0 shadow-sm">
        <div className="card-body p-4 p-lg-5 text-center">
          <span className="sc-feature-icon mb-3" aria-hidden="true"><BookOpen size={24} /></span>
          <h2 className="h5">Aucune activité disponible</h2>
          <p className="text-secondary mb-0">
            Les recommandations seront affichées après l’implémentation du moteur métier. Aucune activité n’est réellement assignée.
          </p>
        </div>
      </section>
    </>
  );
}
