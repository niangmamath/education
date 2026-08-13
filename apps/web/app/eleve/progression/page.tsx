import { BarChart3 } from 'lucide-react';
import { PrototypeNotice } from '../../../components/ui/prototype-notice';

export const metadata = { title: 'Progression Élève' };

export default function EleveProgressionPage() {
  return (
    <>
      <PrototypeNotice />
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Espace Élève</p>
        <h1 className="h2 mb-2">Ma progression</h1>
        <p className="text-secondary mb-0">Comprendre les acquis et la prochaine étape.</p>
      </header>

      <section className="card border-0 shadow-sm">
        <div className="card-body p-4 p-lg-5 text-center">
          <span className="sc-student-icon mb-3" aria-hidden="true"><BarChart3 size={28} /></span>
          <h2 className="h5">Progression indisponible</h2>
          <p className="text-secondary mb-0">
            Aucun résultat, pourcentage ou score fictif n’est présenté comme calculé. Aucun classement entre élèves ne sera affiché.
          </p>
        </div>
      </section>
    </>
  );
}
