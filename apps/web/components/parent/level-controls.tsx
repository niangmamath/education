'use client';

import { useActionState } from 'react';
import { ArrowUpRight, GraduationCap } from 'lucide-react';
import { promoteChild, setChildLevel, type FormState } from '../../lib/actions';
import type { LevelChoice } from '../../lib/types';

const EMPTY: FormState = { error: null };

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
 *
 * **Tout refus est affiché.** La première version jetait la réponse de l'API :
 * le bouton semblait ne rien faire, et rien ne disait si le geste avait échoué
 * ou si la page n'avait pas fini de se recharger. C'est ainsi qu'un défaut
 * d'adresse — une route appelée sans son préfixe — a pu passer pour une
 * manipulation ratée.
 *
 * **Le menu de correction se remonte à chaque classe reçue**, via `key` sur le
 * `<select>`. Sans elle, une correction réussie change bien la classe — le
 * badge au-dessus le montre — mais le menu, non contrôlé, reste figé sur la
 * classe qu'affichait la page à son premier chargement : Next.js met à jour
 * l'arbre par-dessus le même `<select>` plutôt que de le recréer, et React
 * n'applique `defaultValue` qu'au montage. Un parent qui corrige deux fois de
 * suite voit alors sa première correction « revenir » dans le menu, alors
 * qu'elle a bien été enregistrée.
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
  const [declared, declare, declaring] = useActionState(
    setChildLevel.bind(null, childId),
    EMPTY,
  );
  const [promoted, promote, promoting] = useActionState(
    promoteChild.bind(null, childId),
    EMPTY,
  );

  const position = levels.findIndex((level) => level.code === levelCode);
  const following = position >= 0 ? levels[position + 1] : undefined;
  const refusal = declared.error ?? promoted.error;

  return (
    <section className="card mb-4">
      <div className="card-body p-4">
        <p className="sc-oeilleton">Classe</p>

        {levelCode ? (
          <p className="h5 d-flex align-items-center gap-2 mb-3">
            <GraduationCap size={18} aria-hidden="true" />
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

        {refusal ? (
          <div className="alert alert-danger" role="alert">
            {refusal}
          </div>
        ) : null}

        {following ? (
          <form action={promote} className="mb-4">
            <button type="submit" className="btn btn-outline-primary" disabled={promoting}>
              {promoting ? 'Un instant…' : `Passer en ${following.label}`}
              <ArrowUpRight size={18} aria-hidden="true" className="ms-2" />
            </button>
            <p className="text-secondary small mt-2 mb-0">
              Le palier de compétences monte et l’examen de la nouvelle classe est
              donné. Rien n’est effacé : tout ce qui a été observé jusqu’ici reste,
              et c’est ce qui permet de remonter une lacune ancienne.
            </p>
          </form>
        ) : levelCode ? (
          <p className="text-secondary small">
            Dernière classe de l’élémentaire : la suite est le collège, que cette
            plateforme ne couvre pas.
          </p>
        ) : null}

        <form action={declare} className="d-flex flex-wrap align-items-end gap-2">
          <div>
            <label htmlFor={`classe-${childId}`} className="form-label">
              {levelCode ? 'Corriger la classe' : 'Déclarer la classe'}
            </label>
            <select
              key={levelCode ?? 'aucune'}
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
          <button type="submit" className="btn btn-outline-secondary" disabled={declaring}>
            {declaring ? 'Un instant…' : 'Enregistrer'}
          </button>
        </form>
      </div>
    </section>
  );
}
