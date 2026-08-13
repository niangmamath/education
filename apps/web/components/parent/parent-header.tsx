import Link from 'next/link';

export function ParentHeader() {
  return (
    <header className="border-bottom bg-white">
      <div className="container-fluid px-3 px-lg-4 py-3 d-flex align-items-center justify-content-between gap-3">
        <Link href="/parent" className="d-inline-flex align-items-center gap-3 text-decoration-none">
          <span className="sc-brand-mark" aria-hidden="true">SC</span>
          <span><span className="d-block fw-bold text-dark">StudentConnect</span><span className="d-block small text-secondary">Espace Parent</span></span>
        </Link>
        <Link href="/aide" className="btn btn-outline-primary btn-sm">Aide</Link>
      </div>
    </header>
  );
}
