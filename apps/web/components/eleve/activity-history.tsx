'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import { CheckCircle2, Search } from 'lucide-react';
import { formatDateTime } from '../../lib/dates';
import type { ChildAssignment } from '../../lib/types';

type SortOrder = 'recent' | 'ancien';

/**
 * What she has already finished, kept out of her way.
 *
 * A card per activity was fine at five; it stops being fine at fifty. Once an
 * activity is done there is nothing left to act on, so it earns one line, not
 * a quarter of the screen — a search box, and when it was done, because "when
 * did she do this" is exactly what a card with no date could never answer.
 */
export function ActivityHistory({ items }: { items: ChildAssignment[] }) {
  const [query, setQuery] = useState('');
  const [order, setOrder] = useState<SortOrder>('recent');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const matching = q
      ? items.filter((row) => row.activity.title.toLowerCase().includes(q))
      : items;

    return [...matching].sort((a, b) => {
      const dateA = new Date(a.completed_at ?? a.assigned_at).getTime();
      const dateB = new Date(b.completed_at ?? b.assigned_at).getTime();
      return order === 'recent' ? dateB - dateA : dateA - dateB;
    });
  }, [items, query, order]);

  if (items.length === 0) return null;

  return (
    <section className="mt-4">
      <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
        <h2 className="h5 mb-0">Terminées</h2>
        <div className="d-flex flex-wrap align-items-center gap-2">
          <div className="sc-recherche">
            <Search size={16} aria-hidden="true" />
            <input
              type="search"
              className="form-control form-control-sm"
              placeholder="Chercher une activité"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              aria-label="Chercher parmi les activités terminées"
            />
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
      </div>

      {filtered.length === 0 ? (
        <p className="text-secondary small">
          Aucune activité terminée ne correspond à « {query} ».
        </p>
      ) : (
        <ul className="list-group sc-liste-dense">
          {filtered.map((row) => (
            <li className="list-group-item" key={row.id}>
              <Link href={`/eleve/activites/${row.id}/resultat`}>
                <CheckCircle2
                  size={16}
                  aria-hidden="true"
                  className="text-success flex-shrink-0"
                />
                <span className="fw-semibold text-truncate">{row.activity.title}</span>
                <span className="text-secondary small ms-auto flex-shrink-0">
                  {row.completed_at ? formatDateTime(row.completed_at) : '—'}
                </span>
                <span className="text-secondary small flex-shrink-0">
                  {row.activity.duration_minutes} min
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      {query ? (
        <p className="text-secondary small mt-2 mb-0">
          {filtered.length} sur {items.length} activité{items.length > 1 ? 's' : ''}.
        </p>
      ) : null}
    </section>
  );
}
