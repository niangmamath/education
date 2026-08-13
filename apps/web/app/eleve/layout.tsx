import type { ReactNode } from 'react';
import { EleveHeader } from '../../components/eleve/eleve-header';
import { EleveNavigation } from '../../components/eleve/eleve-navigation';

export default function EleveLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-vh-100 sc-student-page">
      <EleveHeader />
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
