import { api } from '../../../lib/api';
import { requireChild } from '../../../lib/session';
import { InterfaceState } from '../../../components/ui/interface-state';
import { ProgressCharts } from '../../../components/eleve/progress-charts';
import type { Progress } from '../../../lib/types';

export const metadata = { title: 'Ma progression' };

/**
 * Her own progress, in her own words.
 *
 * No score and no gap: the health score and the difficulties named from it are
 * for the adult who can put them in context. What is here is what she did and
 * what each competency was last read as — every line carrying the sentence the
 * API built from the counts it stored.
 *
 * Nothing has an order of merit. The competencies are listed as the API returns
 * them, by code, and not sorted worst-first: a page that opened on failures
 * would be a page about failing. `ProgressCharts` can filter by outcome on a
 * click, but filtering is not sorting — it only changes which rows show, never
 * the order they show in.
 */
export default async function ProgressionPage() {
  await requireChild();
  const progress = await api<Progress>('/me/progress');

  if (!progress.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Ta progression n’a pas pu être chargée"
        description={progress.message}
      />
    );
  }

  const { competencies, attempts_completed } = progress.data;

  return (
    <>
      <header className="mb-4">
        <h1 className="h2 mb-1">Ma progression</h1>
        <p className="text-secondary mb-0">
          {attempts_completed > 0
            ? `${attempts_completed} activité${attempts_completed > 1 ? 's terminées' : ' terminée'}.`
            : 'Tu n’as pas encore terminé d’activité.'}
        </p>
      </header>

      {competencies.length === 0 ? (
        <InterfaceState
          kind="empty"
          title="Rien à montrer pour l’instant"
          description="Termine une activité et tu verras apparaître ce qu’elle a montré."
        />
      ) : (
        <ProgressCharts competencies={competencies} />
      )}
    </>
  );
}
