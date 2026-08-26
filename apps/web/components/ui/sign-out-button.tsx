import { logout } from '../../lib/actions';

/**
 * Signing out is a form and not a link, because it changes something.
 *
 * A link would be followed by any prefetch, any crawler and any accidental
 * middle-click, and the session would end without anybody asking.
 *
 * `redirectTo` sends a parent back to `/connexion` and a child back to
 * `/connexion/eleve` — each header binds its own, so signing out lands on the
 * sign-in page for the space just left, not a generic one.
 */
export function SignOutButton({
  label,
  redirectTo,
}: {
  label: string;
  redirectTo: string;
}) {
  return (
    <form action={logout.bind(null, redirectTo)}>
      <button type="submit" className="btn btn-link btn-sm text-secondary px-1">
        {label}
      </button>
    </form>
  );
}
