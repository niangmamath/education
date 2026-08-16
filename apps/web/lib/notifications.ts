/**
 * What has changed, derived from what the platform already knows.
 *
 * The step asks for notifications "without misleading automation", and the
 * honest reading of that is severe: **nothing is delivered anywhere**. No email
 * leaves, no push is sent, nothing is stored, and there is no read state — so
 * there is no unread badge either, because a badge would claim a state nobody
 * keeps.
 *
 * What exists is a reading of facts the parent could have found by opening three
 * pages: an activity finished, a difficulty confirmed, an activity waiting for a
 * long time. Computing it here rather than in the API is deliberate too — a
 * notification model, with its delivery, its channels and its read state, is
 * step 14's subject, and inventing half of it now would leave that step
 * arguing with a half-built one.
 *
 * Everything here is therefore a **presentation**, and the page says so in as
 * many words rather than letting a bell icon imply otherwise.
 */

import type { ChildProfile, Diagnostic, ParentAssignment } from './types';

export type Notification = {
  id: string;
  kind: 'finished' | 'attention' | 'waiting';
  childId: string;
  childName: string;
  title: string;
  detail: string;
  at: string;
  href: string;
};

/** An activity owed for longer than this is worth mentioning, not chasing. */
const WAITING_DAYS = 7;

export function notificationsFor(
  children: ChildProfile[],
  assignments: ParentAssignment[],
  diagnostics: { child: ChildProfile; diagnostic: Diagnostic | null }[],
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
        detail: 'Le détail de ce qu’elle a montré est sur sa page.',
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

  for (const { child, diagnostic } of diagnostics) {
    if (!diagnostic) continue;
    // Only what the platform would actually propose working on. A gap deferred
    // behind a prerequisite is real and shown on the child's page, but raising
    // it here would push a parent towards the competency we chose not to work
    // on yet.
    for (const gap of diagnostic.localized_gaps.filter((row) => row.blocked_by === null)) {
      notifications.push({
        id: `attention:${child.id}:${gap.competency_code}`,
        kind: 'attention',
        childId: child.id,
        childName: child.display_name,
        title: `Point d’attention pour ${child.display_name} : ${
          gap.competency_label ?? gap.competency_code
        }`,
        detail: gap.explanation,
        at: gap.last_seen_at,
        href: `/parent/enfants/${child.id}`,
      });
    }
  }

  return notifications.sort((a, b) => b.at.localeCompare(a.at));
}

function olderThan(iso: string, days: number): boolean {
  const at = Date.parse(iso);
  if (Number.isNaN(at)) return false;
  return Date.now() - at > days * 24 * 60 * 60 * 1000;
}
