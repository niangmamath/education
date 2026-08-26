/**
 * What has changed, derived from what the platform already knows.
 *
 * **Only events belong here.** A gap is a *state*: it holds until the child
 * works on it, so listing it under "what changed" would leave the same three
 * lines sitting there for weeks, and each of them is already counted on the
 * child's card above. States go where they can be acted on — the child's page —
 * and this list keeps to things that happened, each with the date it happened.
 *
 * They also age out. A list that never empties stops being read.
 *
 * The step asks for notifications "without misleading automation", and the
 * honest reading of that is severe: **nothing is delivered anywhere**. No email
 * leaves, no push is sent, nothing is stored, and there is no read state — so
 * there is no unread badge either, because a badge would claim a state nobody
 * keeps.
 *
 * What exists is a reading of facts the parent could have found by opening the
 * other pages: an activity finished, an activity waiting a long time. Computing
 * it here rather than in the API is deliberate too — a
 * notification model, with its delivery, its channels and its read state, is
 * step 14's subject, and inventing half of it now would leave that step
 * arguing with a half-built one.
 *
 * Everything here is therefore a **presentation**, and the page says so in as
 * many words rather than letting a bell icon imply otherwise.
 */

import type { ChildProfile, ParentAssignment } from './types';

export type Notification = {
  id: string;
  kind: 'finished' | 'waiting';
  childId: string;
  childName: string;
  title: string;
  detail: string;
  at: string;
  href: string;
};

/** An activity owed for longer than this is worth mentioning, not chasing. */
const WAITING_DAYS = 7;

/** Past this, it is history rather than news, and history has its own pages. */
const RECENT_DAYS = 30;

export function notificationsFor(
  children: ChildProfile[],
  assignments: ParentAssignment[],
): Notification[] {
  const names = new Map(children.map((child) => [child.id, child.display_name]));
  const notifications: Notification[] = [];

  for (const assignment of assignments) {
    const name = names.get(assignment.child_id);
    if (!name) continue;

    if (assignment.status === 'completed' && assignment.completed_at) {
      notifications.push({
        id: `finished:${assignment.id}`,
        kind: 'finished',
        childId: assignment.child_id,
        childName: name,
        title: `${name} a terminé « ${assignment.activity.title} »`,
        detail: 'Le détail de ce que cette activité a montré est sur sa page.',
        at: assignment.completed_at,
        href: `/parent/enfants/${assignment.child_id}`,
      });
      continue;
    }

    if (assignment.status === 'assigned' && olderThan(assignment.assigned_at, WAITING_DAYS)) {
      notifications.push({
        id: `waiting:${assignment.id}`,
        kind: 'waiting',
        childId: assignment.child_id,
        childName: name,
        title: `« ${assignment.activity.title} » attend depuis plus d’une semaine`,
        detail: 'Rien n’est en retard : une activité n’a de date que si vous lui en donnez une.',
        at: assignment.assigned_at,
        href: `/parent/enfants/${assignment.child_id}`,
      });
    }
  }


  return notifications
    .filter((notification) => within(notification.at, RECENT_DAYS))
    .sort((a, b) => b.at.localeCompare(a.at));
}

function olderThan(iso: string, days: number): boolean {
  const at = Date.parse(iso);
  if (Number.isNaN(at)) return false;
  return Date.now() - at > days * 24 * 60 * 60 * 1000;
}

function within(iso: string, days: number): boolean {
  const at = Date.parse(iso);
  // An unreadable date is kept rather than dropped: losing a real event over a
  // parsing failure is worse than showing one line too many.
  if (Number.isNaN(at)) return true;
  return Date.now() - at <= days * 24 * 60 * 60 * 1000;
}
