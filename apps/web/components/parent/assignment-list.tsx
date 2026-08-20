'use client';

import { useMemo, useState } from 'react';
import { Search } from 'lucide-react';
import { formatDateTime } from '../../lib/dates';
import type { ParentAssignment } from '../../lib/types';

const LABELS: Record<ParentAssignment['status'], { label: string; className: string }> = {
  assigned: { label: 'Donnée', className: 'sc-etat sc-etat-reporte' },
  in_progress: { label: 'En cours', className: 'sc-etat sc-etat-travail' },
  completed: { label: 'Terminée', className: 'sc-etat sc-etat-acquis' },
  cancelled: { label: 'Annulée', className: 'sc-etat sc-etat-non-acquis' },
};

const FILTERS: { value: 'all' | ParentAssignment['status']; label: string }[] = [
  { value: 'all', label: 'Toutes' },
  { value: 'assigned', label: 'Données' },
  { value: 'in_progress', label: 'En cours' },
  { value: 'completed', label: 'Terminées' },
  { value: 'cancelled', label: 'Annulées' },
];

type SortOrder = 'recent' | 'ancien';

/** The date that actually matters for a row: when it was finished if it was,
 * otherwise when it was given — never nothing, since a row with no date is a
 * row that can't be sorted or trusted. */
function relevantDate(row: ParentAssignment): string {
  return row.completed_at ?? row.cancelled_at ?? row.started_at ?? row.assigned_at;
}

/**
 * Everything given to the family, findable instead of just scrollable.
 *
 * A list-group already reads as one line per activity, which holds up for a
 * handful of them; it stops holding up once a family has been here a school
 * year and the page is two hundred lines of "Terminée". A name to search, a
 * state to filter by, and a date to sort by are what turn that page back into
 * something a parent can actually use, without touching the shape it already
 * has.
 */
export function AssignmentList({ assignments }: { assignments: ParentAssignment[] }) {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<'all' | ParentAssignment['status']>('all');
  const [order, setOrder] = useState<SortOrder>('recent');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const matching = assignments.filter((row) => {
      if (status !== 'all' && row.status !== status) return false;
      if (!q) return true;
      return (
        row.activity.title.toLowerCase().includes(q) ||
        row.child_pseudonym.toLowerCase().includes(q)
      );
    });

    return [...matching].sort((a, b) => {
      const dateA = new Date(relevantDate(a)).getTime();
      const dateB = new Date(relevantDate(b)).getTime();
      return order === 'recent' ? dateB - dateA : dateA - dateB;
    });
  }, [assignments, query, status, order]);

  return (
    <>
      <div className="d-flex flex-wrap align-items-center gap-2 mb-3">
        <div className="sc-recherche">
          <Search size={16} aria-hidden="true" />
          <input
            type="search"
            className="form-control form-control-sm"
            placeholder="Chercher un enfant ou une activité"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            aria-label="Chercher parmi les activités"
          />
        </div>
        <div className="btn-group btn-group-sm" role="group" aria-label="Filtrer par état">
          {FILTERS.map((filter) => (
            <button
              key={filter.value}
              type="button"
              className={`btn ${
                status === filter.value ? 'btn-primary' : 'btn-outline-secondary'
              }`}
              onClick={() => setStatus(filter.value)}
            >
              {filter.label}
            </button>
          ))}
        </div>
        <select
          className="form-select form-select-sm w-auto"
          value={order}
          onChange={(event) => setOrder(event.target.value as SortOrder)}
          aria-label="Trier par date"
        >
          <option value="recent">Plus récentes d’abord</option>
          <option value="ancien">Plus anciennes d’abord</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <p className="text-secondary">Aucune activité ne correspond à cette recherche.</p>
      ) : (
        <ul className="list-group">
          {filtered.map((assignment) => (
            <li className="list-group-item py-3" key={assignment.id}>
              <div className="d-flex flex-wrap align-items-center gap-2 mb-1">
                <span className={LABELS[assignment.status].className}>
                  {LABELS[assignment.status].label}
                </span>
                <span className="fw-semibold">{assignment.activity.title}</span>
                <span className="text-secondary small">
                  — {assignment.child_pseudonym}, {assignment.activity.duration_minutes}{' '}
                  minutes
                </span>
                <span className="text-secondary small ms-auto">
                  {formatDateTime(relevantDate(assignment))}
                </span>
              </div>
              {assignment.note ? (
                <p className="text-secondary small mb-0">{assignment.note}</p>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      {query || status !== 'all' ? (
        <p className="text-secondary small mt-2 mb-0">
          {filtered.length} sur {assignments.length} activité
          {assignments.length > 1 ? 's' : ''}.
        </p>
      ) : null}
    </>
  );
}
