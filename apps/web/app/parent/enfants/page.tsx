import Link from 'next/link';
import { UserRound } from 'lucide-react';
import { PrototypeNotice } from '../../../components/ui/prototype-notice';

export const metadata = { title: 'Enfants' };

const students = [
  {
    id: 'eleve-exemple-01',
    displayName: 'Élève exemple',
    level: 'Niveau fictif',
  },
];

export default function ParentChildrenPage() {
  return (
    <>
      <PrototypeNotice />
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Espace Parent</p>
        <h1 className="h2 mb-2">Enfants suivis</h1>
        <p className="text-secondary mb-0">
          Cette liste illustre le futur affichage des profils autorisés.
        </p>
      </header>

      {students.length === 0 ? (
        <section className="card border-0 shadow-sm">
          <div className="card-body p-4">
            <h2 className="h5">Aucun enfant associé</h2>
            <p className="text-secondary mb-0">
              L’association d’un dossier sera disponible après l’implémentation du parcours sécurisé.
            </p>
          </div>
        </section>
      ) : (
        <div className="row g-4">
          {students.map((student) => (
            <div className="col-12 col-md-6 col-xl-4" key={student.id}>
              <article className="card h-100 border-0 shadow-sm">
                <div className="card-body p-4">
                  <span className="sc-feature-icon mb-3" aria-hidden="true">
                    <UserRound size={24} />
                  </span>
                  <h2 className="h5">{student.displayName}</h2>
                  <p className="text-secondary">{student.level}</p>
                  <Link href={`/parent/enfants/${student.id}`} className="btn btn-primary">
                    Consulter le détail fictif
                  </Link>
                </div>
              </article>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
