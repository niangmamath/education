import type { ReactNode } from 'react';
import { EleveHeader } from '../../components/eleve/eleve-header';
import { EleveNavigation } from '../../components/eleve/eleve-navigation';
import { requireChild } from '../../lib/session';

/**
 * The guard is here rather than in a middleware, and deliberately.
 *
 * A middleware would decide from the cookie's presence, which says nothing: a
 * cookie whose session Redis no longer holds looks exactly like a valid one.
 * Asking the API is the only way to know, and it is the API that decides.
 */
export default async function EleveLayout({ children }: { children: ReactNode }) {
  const session = await requireChild();

  return (
    <div className="min-vh-100 sc-student-page">
      <EleveHeader displayName={session.display_name} />
      <div className="container-fluid px-3 px-lg-4 py-3">
        <div className="row g-4">
          <aside className="col-12 col-lg-3 col-xl-2">
            <EleveNavigation />
          </aside>
          <main className="col-12 col-lg-9 col-xl-10" id="contenu-eleve">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
