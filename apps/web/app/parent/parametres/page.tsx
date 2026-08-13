import Link from 'next/link';
import { Settings } from 'lucide-react';
import { PrototypeNotice } from '../../../components/ui/prototype-notice';

export const metadata = { title: 'Paramètres Parent' };

export default function ParentSettingsPage() {
  return (
    <>
      <PrototypeNotice />
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Espace Parent</p>
        <h1 className="h2 mb-2">Paramètres</h1>
        <p className="text-secondary mb-0">Préférences futures de l’espace familial.</p>
      </header>

      <section className="card border-0 shadow-sm">
        <div className="card-body p-4">
          <span className="sc-feature-icon mb-3" aria-hidden="true"><Settings size={24} /></span>
          <h2 className="h5">Configuration non disponible</h2>
          <p className="text-secondary">
            Aucun changement de compte ou de préférence n’est enregistré dans ce prototype.
          </p>
          <Link href="/aide" className="btn btn-outline-primary">Consulter l’aide</Link>
        </div>
      </section>
    </>
  );
}
