import { Star } from 'lucide-react';
import { PrototypeNotice } from '../../../components/ui/prototype-notice';

export const metadata = { title: 'Récompenses Élève' };

export default function EleveRewardsPage() {
  return (
    <>
      <PrototypeNotice />
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Espace Élève</p>
        <h1 className="h2 mb-2">Mes récompenses</h1>
        <p className="text-secondary mb-0">Un futur espace pour reconnaître les actions accomplies.</p>
      </header>

      <section className="card border-0 shadow-sm">
        <div className="card-body p-4 p-lg-5 text-center">
          <span className="sc-student-icon mb-3" aria-hidden="true"><Star size={28} /></span>
          <h2 className="h5">Aucune récompense attribuée</h2>
          <p className="text-secondary mb-0">
            Le prototype ne distribue aucun point et ne promet aucune récompense. Les futurs encouragements décriront l’effort ou l’action réalisée.
          </p>
        </div>
      </section>
    </>
  );
}
