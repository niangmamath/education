import Link from 'next/link';
import { SignOutButton } from '../ui/sign-out-button';

export function EleveHeader({ displayName }: { displayName: string }) {
  return (
    <header className="border-bottom bg-white">
      <div className="container-fluid px-3 px-lg-4 py-3 d-flex align-items-center justify-content-between gap-3">
        <Link href="/eleve" className="d-inline-flex align-items-center gap-3 text-decoration-none">
          <span className="sc-student-brand" aria-hidden="true">SC</span>
          <span>
            <span className="sc-marque-nom d-block">StudentConnect</span>
            <span className="sc-marque-role d-block">Espace élève</span>
          </span>
        </Link>
        <div className="d-flex align-items-center gap-2">
          <span className="small text-secondary d-none d-sm-inline">{displayName}</span>
          <Link href="/aide" className="btn btn-outline-secondary btn-sm">Besoin d’aide ?</Link>
          <SignOutButton label="Quitter" />
        </div>
      </div>
    </header>
  );
}
