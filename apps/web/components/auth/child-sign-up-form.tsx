'use client';

import { useActionState } from 'react';
import { registerChild, type FormState } from '../../lib/actions';
import type { LevelChoice } from '../../lib/types';

const EMPTY: FormState = { error: null };

/**
 * Asking to join a family, on its own address.
 *
 * The profile waits: a family code alone must never be enough to join a family,
 * only to ask to. The form says so here, rather than letting a child discover it
 * at her first attempt to sign in.
 */
export function ChildSignUpForm({ levels }: { levels: LevelChoice[] }) {
  const [state, action, pending] = useActionState(registerChild, EMPTY);

  return (
    <form action={action} noValidate>
      <h2 className="h5 mb-4">Ton profil</h2>

      {state.error ? (
        <div className="alert alert-danger" role="alert">
          {state.error}
        </div>
      ) : null}

      <div className="mb-3">
        <label htmlFor="family_code" className="form-label">
          Code de la famille
        </label>
        <input
          id="family_code"
          name="family_code"
          className="form-control text-uppercase"
          autoComplete="organization"
          autoCapitalize="characters"
          spellCheck={false}
          required
        />
      </div>
      <div className="mb-3">
        <label htmlFor="display_name" className="form-label">
          Ton prénom
        </label>
        <input
          id="display_name"
          name="display_name"
          className="form-control"
          autoComplete="given-name"
          required
        />
      </div>
      <div className="mb-3">
        <label htmlFor="pseudonym" className="form-label">
          Le pseudo que tu veux
        </label>
        <input
          id="pseudonym"
          name="pseudonym"
          className="form-control"
          autoComplete="username"
          minLength={3}
          required
          aria-describedby="aide-pseudo"
        />
        <div id="aide-pseudo" className="form-text">
          Au moins trois lettres, et différent de celui de tes frères et sœurs.
        </div>
      </div>
      <div className="mb-4">
        <label htmlFor="pin" className="form-label">
          Choisis un code secret
        </label>
        <input
          id="pin"
          name="pin"
          type="password"
          inputMode="numeric"
          pattern="[0-9]{6}"
          className="form-control"
          autoComplete="new-password"
          required
          aria-describedby="aide-pin"
        />
        <div id="aide-pin" className="form-text">
          Six chiffres. Ne le donne à personne.
        </div>
      </div>
      <div className="mb-3">
        <label htmlFor="classe" className="form-label">
          Ta classe
        </label>
        <select
          id="classe"
          name="level_code"
          className="form-select"
          defaultValue=""
          required
          aria-describedby="classe-aide"
        >
          <option value="" disabled>
            Choisir une classe
          </option>
          {levels.map((level) => (
            <option key={level.code} value={level.code}>
              {level.label}
            </option>
          ))}
        </select>
        <div id="classe-aide" className="form-text">
          Demande à un adulte si tu n’es pas sûr.
        </div>
      </div>


      <button type="submit" className="btn btn-primary w-100" disabled={pending}>
        {pending ? 'Création…' : 'Créer mon profil'}
      </button>
    </form>
  );
}
