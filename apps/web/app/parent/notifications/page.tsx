import { Bell } from 'lucide-react';
import { PrototypeNotice } from '../../../components/ui/prototype-notice';

export const metadata = { title: 'Notifications Parent' };

export default function ParentNotificationsPage() {
  return (
    <>
      <PrototypeNotice />
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Espace Parent</p>
        <h1 className="h2 mb-2">Notifications</h1>
        <p className="text-secondary mb-0">Informations qui nécessiteront une attention.</p>
      </header>

      <section className="card border-0 shadow-sm">
        <div className="card-body p-4 p-lg-5 text-center">
          <span className="sc-feature-icon mb-3" aria-hidden="true"><Bell size={24} /></span>
          <h2 className="h5">Aucune notification</h2>
          <p className="text-secondary mb-0">
            Cette page présente uniquement l’état vide. Aucune notification réelle n’est envoyée ou enregistrée.
          </p>
        </div>
      </section>
    </>
  );
}
