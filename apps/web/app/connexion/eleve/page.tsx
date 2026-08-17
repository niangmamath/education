import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { ChildLoginForm } from '../../../components/auth/child-login-form';

export const metadata = {
  title: 'Connexion Élève',
  description: 'Entrer dans l’espace Élève avec le code de sa famille',
};

export default async function ConnexionElevePage({
  searchParams,
}: {
  searchParams: Promise<{ cree?: string; demande?: string }>;
}) {
  const { cree, demande } = await searchParams;

  return (
    <main className="container py-5">
      <div className="mx-auto" style={{ maxWidth: '34rem' }}>
        <Link href="/" className="d-inline-flex align-items-center gap-2 mb-4">
          <ArrowLeft size={18} aria-hidden="true" />
          Retour à l’accueil
        </Link>

        {cree ? (
          <div className="alert alert-success" role="status">
            <strong>Votre compte est créé.</strong> Connectez-vous avec le mot de
            passe que vous venez de choisir. Vous trouverez votre code de famille
            dans « Mes enfants ».
          </div>
        ) : null}
        {demande ? (
          <div className="alert alert-info" role="status">
            <strong>Ton profil est enregistré.</strong> Un adulte de ta famille
            doit l’accepter avant que tu puisses entrer. Reviens ici après.
          </div>
        ) : null}

        <div className="card border-0 shadow-sm">
          <div className="card-body p-4 p-lg-5">
            <ChildLoginForm />
          </div>
        </div>

        <div className="d-flex flex-column gap-2 mt-4">
          <p className="mb-0">Vous êtes un parent ? <Link href="/connexion">Espace Parent</Link></p>
          <p className="mb-0">Tu n’as pas encore de profil ? <Link href="/inscription/eleve">En créer un</Link></p>
        </div>
      </div>
    </main>
  );
}
