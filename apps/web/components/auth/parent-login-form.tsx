'use client';

import { useActionState } from 'react';
import { loginParent, type FormState } from '../../lib/actions';

const EMPTY: FormState = { error: null };

/**
 * One form, on a page of its own.
 *
 * The parent's and the child's sign-in used to share a URL and swap in place
 * behind two tabs. A browser cannot tell two forms at one address apart: it had
 * a single saved credential for the site and filled it into whichever form was
 * showing, which put a parent's password into a child's family code field.
 *
 * A page each is the fix, and it is not a workaround. Signing in as a parent and
 * signing in as a child are different acts with different credentials; giving
 * them one address each lets the browser save and offer the right one, which is
 * what autofill is for.
 */
export function ParentLoginForm() {
  const [state, action, pending] = useActionState(loginParent, EMPTY);

  return (
    <form action={action} noValidate>
      <h2 className="h5 mb-4">Se connecter</h2>

      {state.error ? (
        <div className="alert alert-danger" role="alert">
          {state.error}
        </div>
      ) : null}

      <div className="mb-3">
        <label htmlFor="email" className="form-label">
          Adresse e-mail
        </label>
        <input
          id="email"
          name="email"
          type="email"
          className="form-control"
          autoComplete="email"
          required
        />
      </div>
      <div className="mb-4">
        <label htmlFor="password" className="form-label">
          Mot de passe
        </label>
        <input
          id="password"
          name="password"
          type="password"
          className="form-control"
          autoComplete="current-password"
          required
        />
      </div>

      <button type="submit" className="btn btn-primary w-100" disabled={pending}>
        {pending ? 'Connexion…' : 'Se connecter'}
      </button>
    </form>
  );
}
