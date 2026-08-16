import Link from 'next/link';
import { AlertTriangle, CheckCircle2, Clock3 } from 'lucide-react';
import type { Notification } from '../../lib/notifications';

const ICONS = {
  finished: CheckCircle2,
  attention: AlertTriangle,
  waiting: Clock3,
} as const;

const TONES = {
  finished: 'text-success',
  attention: 'text-warning-emphasis',
  waiting: 'text-secondary',
} as const;

/**
 * A list of what changed, and nothing that pretends to be more.
 *
 * No unread count and no bell: there is no read state anywhere, and a badge
 * would claim one. Each line links to the page that can explain it, because a
 * notice a parent cannot follow up is only an interruption.
 */
export function NotificationList({ notifications }: { notifications: Notification[] }) {
  if (notifications.length === 0) {
    return (
      <p className="text-secondary mb-0">
        Rien de nouveau depuis votre dernière visite.
      </p>
    );
  }

  return (
    <ul className="list-group">
      {notifications.map((notification) => {
        const Icon = ICONS[notification.kind];
        return (
          <li className="list-group-item py-3" key={notification.id}>
            <div className="d-flex gap-3">
              <Icon
                size={20}
                aria-hidden="true"
                className={`${TONES[notification.kind]} flex-shrink-0 mt-1`}
              />
              <div>
                <Link href={notification.href} className="fw-semibold text-decoration-none">
                  {notification.title}
                </Link>
                <p className="text-secondary small mb-0">{notification.detail}</p>
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
