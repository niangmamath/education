import { applyRemediation } from '../../lib/actions';

/**
 * Giving the proposed activities, in one act.
 *
 * What the button removes is the retyping, not the decision: nothing is assigned
 * until a parent presses it, and the platform never presses it for anyone. What
 * is already waiting for the child, or what would pass the ceiling of open
 * assignments, is skipped by the API rather than forced.
 */
export function ApplyRemediationButton({
  childId,
  count,
}: {
  childId: string;
  count: number;
}) {
  const apply = applyRemediation.bind(null, childId);

  return (
    <form action={apply}>
      <button type="submit" className="btn btn-primary">
        Donner {count > 1 ? `ces ${count} activités` : 'cette activité'}
      </button>
    </form>
  );
}
