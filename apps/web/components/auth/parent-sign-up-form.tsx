'use client';

import { useActionState } from 'react';
import { UserPlus } from 'lucide-react';
import { registerParent, type FormState } from '../../lib/actions';

const EMPTY: FormState = { error: null };

/**
 * Opening a family, on its own address.
 *
 * Every field names what it holds so a browser can offer to remember it and
 * fill it next time. Sharing a URL with the child's form was what made that
 * impossible: one saved credential, two forms, and nothing to tell them apart.
 *
 * The rules are stated before they are broken — twelve characters — rather than
 * after. A form that only objects on submission teaches that you did something
 * wrong; one that says what it wants does not.
 */
export function ParentSignUpForm() {
  const [state, action, pending] = useActionState(registerParent, EMPTY);

  return (
    <form action={action} noValidate>
      <span className="sc-feature-icon mb-3" aria-hidden="true">
        <UserPlus size={24} />
      </span>
      <h2 className="h4">Ouvrir un compte Parent</h2>
      <p className="text-secondary">
        Vous recevrez un code de famille : c’est lui que vos enfants utiliseront
        pour se connecter.
      </p>

      {state.error ? (
        <div className="alert alert-danger" role="alert">
          {state.error}
        </div>
      ) : null}

      <div className="mb-3">
        <label htmlFor="display_name" className="form-label">
          Votre nom
        </label>
        <input
          id="display_name"
          name="display_name"
          className="form-control"
          autoComplete="name"
          required
        />
      </div>
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
      <div className="mb-3">
        <label htmlFor="password" className="form-label">
          Mot de passe
        </label>
        <input
          id="password"
          name="password"
          type="password"
          className="form-control"
          autoComplete="new-password"
          minLength={12}
          required
          aria-describedby="aide-mot-de-passe"
        />
        <div id="aide-mot-de-passe" className="form-text">
          Au moins douze caractères.
        </div>
      </div>
      <div className="mb-4">
        <label htmlFor="password_confirm" className="form-label">
          Confirmer le mot de passe
        </label>
        <input
          id="password_confirm"
          name="password_confirm"
          type="password"
          className="form-control"
          autoComplete="new-password"
          required
        />
      </div>

      <button type="submit" className="btn btn-primary" disabled={pending}>
        {pending ? 'Création…' : 'Créer le compte'}
      </button>
    </form>
  );
}
