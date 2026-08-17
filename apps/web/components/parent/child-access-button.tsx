import { setChildAccess } from '../../lib/actions';

/**
 * Open or close a profile's access.
 *
 * Opening is also what hands a child her initiation assessment, the first time.
 * Closing keeps everything she has done: a profile turned off is a door shut,
 * not a history erased.
 */
export function ChildAccessButton({
  childId,
  open,
}: {
  childId: string;
  open: boolean;
}) {
  const act = setChildAccess.bind(null, childId, open);

  return (
    <form action={act}>
      <button
        type="submit"
        className={`btn btn-sm ${open ? 'btn-success' : 'btn-outline-secondary'}`}
      >
        {open ? 'Activer' : 'Désactiver'}
      </button>
    </form>
  );
}
