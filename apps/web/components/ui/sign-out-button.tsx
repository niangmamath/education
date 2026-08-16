import { logout } from '../../lib/actions';

/**
 * Signing out is a form and not a link, because it changes something.
 *
 * A link would be followed by any prefetch, any crawler and any accidental
 * middle-click, and the session would end without anybody asking.
 */
export function SignOutButton({ label }: { label: string }) {
  return (
    <form action={logout}>
      <button type="submit" className="btn btn-link btn-sm text-secondary px-1">
        {label}
      </button>
    </form>
  );
}
