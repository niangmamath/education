import { startActivity } from '../../lib/actions';

/**
 * Taking up an activity, as a form.
 *
 * Starting is a change and not a navigation, so it is a `POST` and not a link.
 * The API makes it idempotent — starting twice returns the same thing — so a
 * double tap on a slow connection costs nothing, which is exactly the case a
 * child on a household tablet is most likely to produce.
 */
export function StartActivityButton({
  assignmentId,
  label,
}: {
  assignmentId: string;
  label: string;
}) {
  const start = startActivity.bind(null, assignmentId);

  return (
    <form action={start}>
      <button type="submit" className="btn btn-primary btn-lg">
        {label}
      </button>
    </form>
  );
}
