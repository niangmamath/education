'use client';

import { useActionState } from 'react';
import { UserPlus } from 'lucide-react';
import { createChild, type FormState } from '../../lib/actions';
import type { LevelChoice } from '../../lib/types';

const EMPTY: FormState = { error: null };

/**
 * Add a child profile from the parent's own space.
 *
 * Usable straight away, unlike one a child opens with the family code: the adult
 * who owns the family is the one asking, so there is nobody left to approve it.
 *
 * The secret code is chosen by the parent here and shown to nobody afterwards —
 * the platform stores only its hash, so a forgotten one is reset, never
 * recovered. The form says so while there is still time to write it down.
 */
export function AddChildForm({ levels }: { levels: LevelChoice[] }) {
  const [state, action, pending] = useActionState(createChild, EMPTY);

  return (
    <section className="card border-0 shadow-sm">
      <div className="card-body p-4">
        <div className="d-flex align-items-center gap-2 mb-3">
          <UserPlus size={20} aria-hidden="true" className="text-secondary" />
          <h2 className="h5 mb-0">Ajouter un enfant</h2>
        </div>

        {state.error ? (
          <div className="alert alert-danger" role="alert">
            {state.error}
          </div>
        ) : null}

        <form action={action} className="row g-3" noValidate>
          <div className="col-12 col-md-4">
            <label htmlFor="child-display-name" className="form-label">
              Prénom
            </label>
            <input
              id="child-display-name"
              name="display_name"
              className="form-control"
              required
            />
          </div>
          <div className="col-12 col-md-4">
            <label htmlFor="child-pseudonym" className="form-label">
              Pseudonyme
            </label>
            <input
              id="child-pseudonym"
              name="pseudonym"
              className="form-control"
              minLength={3}
              required
              aria-describedby="aide-pseudo-parent"
            />
            <div id="aide-pseudo-parent" className="form-text">
              Unique dans votre famille.
            </div>
          </div>
          <div className="col-12 col-md-4">
            <label htmlFor="child-pin" className="form-label">
              Code secret
            </label>
            <input
              id="child-pin"
              name="pin"
              inputMode="numeric"
              pattern="[0-9]*"
              className="form-control"
              required
              aria-describedby="aide-pin-parent"
            />
            <div id="aide-pin-parent" className="form-text">
              Six chiffres. Notez-le : il ne se retrouve pas, il se réinitialise.
            </div>
          </div>
          <div className="col-12">
      <div className="mb-3">
        <label htmlFor="classe-enfant" className="form-label">
          Sa classe
        </label>
        <select
          id="classe-enfant"
          name="level_code"
          className="form-select"
          defaultValue=""
          required
          aria-describedby="classe-enfant-aide"
        >
          <option value="" disabled>
            Choisir une classe
          </option>
          {levels.map((level) => (
            <option key={level.code} value={level.code}>
              {level.code.toUpperCase()}
            </option>
          ))}
        </select>
        <div id="classe-enfant-aide" className="form-text">
          Elle décide de l’examen d’entrée qu’il reçoit : il y en a un par classe.
        </div>
      </div>

            <button type="submit" className="btn btn-primary" disabled={pending}>
              {pending ? 'Création…' : 'Créer le profil'}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
