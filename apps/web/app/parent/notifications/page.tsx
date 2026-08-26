import { api } from '../../../lib/api';
import { requireParent } from '../../../lib/session';
import { InterfaceState } from '../../../components/ui/interface-state';
import { NotificationList } from '../../../components/parent/notification-list';
import { notificationsFor } from '../../../lib/notifications';
import type { ChildProfile, ParentAssignment } from '../../../lib/types';

export const metadata = { title: 'Ce qui a changé' };

/**
 * Everything that changed, and an honest account of what this page is not.
 *
 * Nothing is sent anywhere. No email leaves, no push is delivered, nothing is
 * stored and no read state is kept — so there is no unread count, because a
 * badge would claim a state nobody keeps. What is here is a reading of facts the
 * parent could have found by opening three other pages.
 *
 * Saying so on the page itself is the point of the step's "without misleading
 * automation": a list that looked like an inbox would promise a delivery that
 * does not exist, and a parent would stop checking.
 */
export default async function NotificationsPage() {
  await requireParent();

  const children = await api<ChildProfile[]>('/auth/children');
  if (!children.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Vos profils enfants n’ont pas pu être chargés"
        description={children.message}
      />
    );
  }

  const active = children.data.filter((child) => child.status === 'active');
  // Only the assignments: what changed is made of events, and a diagnostic
  // describes a state. Fetching one per child to derive nothing from it would
  // be work done for a list that no longer shows it.
  const assignments = await api<ParentAssignment[]>('/assignments');

  const notifications = notificationsFor(active, assignments.ok ? assignments.data : []);

  return (
    <>
      <header className="mb-4">
        <h1 className="h2 mb-1">Ce qui a changé</h1>
        <p className="text-secondary mb-0">
          Activités terminées, points d’attention et activités qui attendent.
        </p>
      </header>

      <div className="alert alert-secondary" role="note">
        <strong>Rien ne vous est envoyé.</strong> Cette page relit ce que la
        plateforme sait déjà ; aucun e-mail ni aucune alerte ne part, et rien
        n’est marqué comme lu. L’envoi viendra avec les notifications de
        l’étape 14.
      </div>

      <NotificationList notifications={notifications} />
    </>
  );
}
