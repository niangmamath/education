'use client';

import { useActionState } from 'react';
import { ArrowUpRight, GraduationCap } from 'lucide-react';
import { promoteChild, setChildLevel } from '../../lib/actions';
import type { LevelChoice } from '../../lib/types';

/**
 * La classe d'un élève : la déclarer, la corriger, ou passer à la suivante.
 *
 * Deux gestes qui se ressemblent et qui ne sont pas le même. **Passer en classe
 * supérieure** est un fait de la scolarité, et la plateforme ne le décide pas :
 * elle ne connaît ni l'école de l'enfant, ni son année, ni ce qu'un conseil de
 * maîtres a tranché. **Corriger la classe** rattrape une saisie, ou en donne une
 * à un profil ouvert avant que la plateforme ne la demande.
 *
 * Le bouton de passage nomme la classe d'arrivée plutôt que de dire « passer » :
 * un parent doit voir où il envoie son enfant avant d'appuyer, pas après.
 */
export function LevelControls({
  childId,
  levelCode,
  levelLabel,
  levels,
}: {
  childId: string;
  levelCode: string | null;
  levelLabel: string | null;
  levels: LevelChoice[];
}) {
  const [, correct, correcting] = useActionState(
    async (_: null, formData: FormData) => {
      await setChildLevel(childId, formData);
      return null;
    },
    null,
  );

  const position = levels.findIndex((level) => level.code === levelCode);
  const following = position >= 0 ? levels[position + 1] : undefined;

  return (
    <section className="card mb-4">
      <div className="card-body p-4">
        <p className="sc-oeilleton">Classe</p>

        {levelCode ? (
          <p className="h5 mb-3">
            <GraduationCap size={18} aria-hidden="true" className="me-2" />
            {levelLabel ?? levelCode}
          </p>
        ) : (
          <div className="sc-etat-ecran sc-etat-ecran-travail p-3 mb-3">
            <p className="fw-semibold mb-1">La classe n’est pas déclarée.</p>
            <p className="mb-0 text-secondary">
              Sans elle, cet élève ne reçoit aucun examen d’entrée : il y en a un
              par classe, et la plateforme ne devine pas laquelle.
            </p>
          </div>
        )}

        {following ? (
          <form action={promoteChild.bind(null, childId)} className="mb-3">
            <button type="submit" className="btn btn-outline-primary">
              Passer en {following.label}
              <ArrowUpRight size={18} aria-hidden="true" className="ms-2" />
            </button>
            <p className="text-secondary small mt-2 mb-0">
              Le palier de compétences monte et l’examen de la nouvelle classe
              est donné. Rien n’est effacé : tout ce qui a été observé jusqu’ici
              reste, et c’est ce qui permet de remonter une lacune ancienne.
            </p>
          </form>
        ) : levelCode ? (
          <p className="text-secondary small">
            Dernière classe de l’élémentaire : la suite est le collège, que cette
            plateforme ne couvre pas.
          </p>
        ) : null}

        <form action={correct} className="d-flex flex-wrap align-items-end gap-2">
          <div>
            <label htmlFor={`classe-${childId}`} className="form-label">
              {levelCode ? 'Corriger la classe' : 'Déclarer la classe'}
            </label>
            <select
              id={`classe-${childId}`}
              name="level_code"
              className="form-select"
              defaultValue={levelCode ?? ''}
              required
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
          </div>
          <button type="submit" className="btn btn-outline-secondary" disabled={correcting}>
            {correcting ? 'Un instant…' : 'Enregistrer'}
          </button>
        </form>
      </div>
    </section>
  );
}
