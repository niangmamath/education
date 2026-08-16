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
  searchParams: Promise<{ suite?: string }>;
}) {
  const { suite } = await searchParams;

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

        <LoginForms defaultTab={suite === 'eleve' ? 'eleve' : 'parent'} />
      </div>
    </main>
  );
}
