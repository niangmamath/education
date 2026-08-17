import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { LoginForms } from '../../components/auth/login-forms';

export const metadata = {
  title: 'Connexion',
  description: 'Accès aux espaces Parent et Élève de StudentConnect',
};

/**
 * Two ways in, side by side, because they are not the same act.
 *
 * A parent signs in with an email and a password. A child signs in with the
 * family code, her pseudonym and a PIN — no email and no telephone, which a
 * project rule requires and which is also why the two forms cannot be merged
 * into one with a hidden switch.
 *
 * `suite` says which space the visitor was trying to reach, so the right form is
 * open when they arrive; it changes nothing about what either accepts.
 */
export default async function ConnexionPage({
  searchParams,
}: {
  searchParams: Promise<{ suite?: string; cree?: string; demande?: string }>;
}) {
  const { suite, cree, demande } = await searchParams;

  return (
    <main className="container py-5">
      <div className="mx-auto" style={{ maxWidth: '52rem' }}>
        <Link href="/" className="d-inline-flex align-items-center gap-2 mb-4">
          <ArrowLeft size={18} aria-hidden="true" />
          Retour à l’accueil
        </Link>

        <h1 className="h2 mb-1">Se connecter</h1>
        <p className="text-secondary mb-4">
          Choisissez l’espace qui vous concerne. Un enfant n’a besoin ni d’adresse
          e-mail ni de téléphone.
        </p>

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

        <LoginForms defaultTab={suite === 'eleve' ? 'eleve' : 'parent'} />

        <p className="mt-4">
          Pas encore de compte ?{' '}
          <Link href={`/inscription${suite === 'eleve' ? '?suite=eleve' : ''}`}>
            En créer un
          </Link>
        </p>
      </div>
    </main>
  );
}
