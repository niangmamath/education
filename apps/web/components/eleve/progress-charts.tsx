'use client';

import Link from 'next/link';
import { useState } from 'react';
import type { CompetencyProgress, Outcome } from '../../lib/types';
import { OUTCOME_CLASSES, OUTCOME_LABELS } from '../../lib/types';

const BAR_COLOR: Record<Outcome, string> = {
  mastered: 'var(--sc-acquis)',
  partial: 'var(--sc-travail)',
  not_mastered: 'var(--sc-reporte)',
};

const ORDER: Outcome[] = ['mastered', 'partial', 'not_mastered'];

/**
 * Two small charts, and neither one ranks anything.
 *
 * The competency list already refuses to sort worst-first, on purpose — this
 * page is not where a child reads that she is behind. Both charts keep that
 * rule: the summary bar is a tally, not a comparison, and the per-competency
 * bars stay in the same order the list already uses (by code), never
 * re-sorted by how well she did — clicking a legend entry only **filters**
 * which rows show, it never reorders them by score.
 *
 * A bar's own length is the one number this page shows her — the ratio the
 * text row beside it already states in words — never a rank against her
 * other competencies or anyone else's.
 */
export function ProgressCharts({
  competencies,
  linkBase = '/eleve/progression',
}: {
  competencies: CompetencyProgress[];
  /** Where a row links to, given the competency code appended to it. `null`
   * renders rows as plain, unlinked information — for a context, like the
   * parent's cross-child view, that has nowhere of its own to send a click
   * to yet. */
  linkBase?: string | null;
}) {
  const [filter, setFilter] = useState<Outcome | 'all'>('all');

  const counts: Record<Outcome, number> = { mastered: 0, partial: 0, not_mastered: 0 };
  for (const row of competencies) {
    counts[row.latest_outcome] += 1;
  }
  const total = competencies.length;
  const shown =
    filter === 'all' ? competencies : competencies.filter((row) => row.latest_outcome === filter);

  return (
    <div className="mb-4">
      <ul className="d-flex flex-wrap gap-2 list-unstyled mb-3">
        {(['all', ...ORDER] as const).map((option) => (
          <li key={option}>
            <button
              type="button"
              className={`btn btn-sm d-flex align-items-center gap-2 ${
                filter === option ? 'btn-primary' : 'btn-outline-secondary'
              }`}
              aria-pressed={filter === option}
              onClick={() => setFilter(option)}
            >
              {option !== 'all' ? (
                <span
                  className="sc-legende-puce"
                  style={{ background: BAR_COLOR[option] }}
                  aria-hidden="true"
                />
              ) : null}
              {option === 'all' ? 'Toutes' : OUTCOME_LABELS[option]} (
              {option === 'all' ? total : counts[option]})
            </button>
          </li>
        ))}
      </ul>

      <div
        className="sc-graphe-empile mb-4"
        role="img"
        aria-label={ORDER.map((o) => `${OUTCOME_LABELS[o]} : ${counts[o]}`).join(', ')}
      >
        {ORDER.map((outcome) =>
          counts[outcome] > 0 ? (
            <span
              key={outcome}
              style={{
                width: `${(counts[outcome] / total) * 100}%`,
                background: BAR_COLOR[outcome],
              }}
              title={`${OUTCOME_LABELS[outcome]} : ${counts[outcome]}`}
            />
          ) : null,
        )}
      </div>

      <ul className="list-group">
        {shown.map((row) => {
          const ratio =
            row.answered_total > 0 ? row.correct_total / row.answered_total : 0;
          const content = (
            <>
              <div className="d-flex flex-wrap align-items-center gap-2 mb-2">
                <span className={OUTCOME_CLASSES[row.latest_outcome]}>
                  {OUTCOME_LABELS[row.latest_outcome]}
                </span>
                <span className="fw-semibold">{row.competency_code}</span>
              </div>
              <div className="d-flex align-items-center gap-3 mb-2">
                <span className="sc-graphe-barre flex-grow-1" role="presentation">
                  {ratio > 0 ? (
                    <span
                      style={{
                        width: `${ratio * 100}%`,
                        background: BAR_COLOR[row.latest_outcome],
                      }}
                    />
                  ) : null}
                </span>
                <span
                  className="small text-secondary flex-shrink-0"
                  style={{ width: '3.5em' }}
                >
                  {row.correct_total}/{row.answered_total}
                </span>
              </div>
              <p className="text-secondary small mb-0">{row.explanation}</p>
            </>
          );

          return (
            <li className="list-group-item p-0" key={row.competency_code}>
              {linkBase ? (
                <Link
                  href={`${linkBase}/${row.competency_code}`}
                  className="d-block text-reset text-decoration-none p-3"
                >
                  {content}
                </Link>
              ) : (
                <div className="p-3">{content}</div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
