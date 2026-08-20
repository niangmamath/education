import Link from 'next/link';
import { api } from '../../../lib/api';
import { requireParent } from '../../../lib/session';
import { InterfaceState } from '../../../components/ui/interface-state';
import { ProgressCharts } from '../../../components/eleve/progress-charts';
import type { ChildProfile, Progress } from '../../../lib/types';

export const metadata = { title: 'Progression' };

/**
 * Every active child, the same charts her own page shows her.
 *
 * Nothing extra rides along: this reads `/children/{id}/progress`, the
 * competency-by-competency record, not the diagnostic — a parent already has
 * that on each child's own page, with the difficulties and the rule that named
 * them. This page exists because the parent nav had no way to see progress
 * across children at a glance, one chart apiece, without opening each one.
 */
export default async function ParentProgressionPage() {
  await requireParent();
  const children = await api<ChildProfile[]>('/auth/children');

  if (!children.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Vos profils enfants n’ont pas pu être chargés"
        description={children.message}
      />
    );
  }

  const active = children.data.filter((child) => child.status === 'active');

  if (active.length === 0) {
    return (
      <InterfaceState
        kind="empty"
        title="Aucun enfant actif"
        description="La progression apparaît ici une fois qu’un profil est actif."
      />
    );
  }

  const results = await Promise.all(
    active.map((child) => api<Progress>(`/children/${child.id}/progress`)),
  );

  return (
    <>
      <header className="mb-4">
        <h1 className="h2 mb-1">Progression</h1>
        <p className="text-secondary mb-0">Compétence par compétence, pour chaque enfant.</p>
      </header>

      {active.map((child, index) => {
        const progress = results[index];
        return (
          <section className="mb-5" key={child.id}>
            <div className="d-flex align-items-center justify-content-between mb-3">
              <h2 className="h4 mb-0">{child.display_name}</h2>
              <Link href={`/parent/enfants/${child.id}`} className="btn btn-outline-primary btn-sm">
                Voir le diagnostic
              </Link>
            </div>

            {!progress.ok ? (
              <InterfaceState
                kind="unavailable"
                title="Sa progression n’a pas pu être chargée"
                description={progress.message}
              />
            ) : progress.data.competencies.length === 0 ? (
              <InterfaceState
                kind="empty"
                title="Rien à montrer pour l’instant"
                description="Rien n’a encore été terminé."
              />
            ) : (
              <ProgressCharts
                competencies={progress.data.competencies}
                linkBase={`/parent/enfants/${child.id}/competences`}
              />
            )}
          </section>
        );
      })}
    </>
  );
}
