import type { ReactNode } from 'react';
import { ParentHeader } from '../../components/parent/parent-header';
import { ParentNavigation } from '../../components/parent/parent-navigation';
import { requireParent } from '../../lib/session';

export default async function ParentLayout({ children }: { children: ReactNode }) {
  const session = await requireParent();

  return (
    <div className="min-vh-100 bg-body-tertiary">
      <ParentHeader displayName={session.display_name} />
      <div className="container-fluid px-3 px-lg-4 py-3">
        <div className="row g-4">
          <aside className="col-12 col-lg-3 col-xl-2">
            <ParentNavigation />
          </aside>
          <main className="col-12 col-lg-9 col-xl-10" id="contenu-parent">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
