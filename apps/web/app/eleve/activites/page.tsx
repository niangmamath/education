import { BookOpen } from 'lucide-react';
import { PrototypeNotice } from '../../../components/ui/prototype-notice';

export const metadata = { title: 'Activités Élève' };

export default function EleveActivitiesPage() {
  return (
    <>
      <PrototypeNotice />
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Espace Élève</p>
        <h1 className="h2 mb-2">Mes activités</h1>
        <p className="text-secondary mb-0">Choisir ou reprendre une activité courte.</p>
      </header>

      <section className="card border-0 shadow-sm">
        <div className="card-body p-4 p-lg-5 text-center">
          <span className="sc-student-icon mb-3" aria-hidden="true"><BookOpen size={28} /></span>
          <h2 className="h5">Aucune activité disponible</h2>
          <p className="text-secondary mb-0">
            Les activités seront proposées après l’implémentation du catalogue et des recommandations. Rien n’est assigné dans ce prototype.
          </p>
        </div>
      </section>
    </>
  );
}
