import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { ParentLoginForm } from '../../components/auth/parent-login-form';

export const metadata = {
  title: 'Connexion Parent',
  description: 'Se connecter à l’espace Parent de StudentConnect',
};

/**
 * Une adresse par rôle, et la page le dit.
 *
 * La colonne de gauche n'est pas une décoration : elle nomme le rôle avant le
 * formulaire, pour qu'un parent arrivé ici par erreur reparte tout de suite vers
 * la page de son enfant plutôt que d'essayer ses identifiants dans un champ qui
 * n'est pas le sien.
 *
 * Seul le message `cree` est traité ici. `demande` appartient à la page de
 * l'élève, qui est celle où l'inscription d'un enfant renvoie.
 */
export default async function ConnexionParentPage({
  searchParams,
}: {
  searchParams: Promise<{ cree?: string }>;
}) {
  const { cree } = await searchParams;

  return (
    <main className="container py-5">
      <Link href="/" className="d-inline-flex align-items-center gap-2 mb-5">
        <ArrowLeft size={18} aria-hidden="true" />
        Retour à l’accueil
      </Link>

      <div className="row g-5 justify-content-center align-items-start">
        <div className="col-lg-5 col-xl-4">
          <p className="sc-oeilleton sc-oeilleton-indigo">Connexion</p>
          <h1 className="mb-3">Espace parent</h1>
          <p className="text-secondary">
            Vous y trouvez le diagnostic de chaque enfant, la règle qui l’a
            produit, et les remédiations que la plateforme vous propose.
          </p>
          <p className="sc-marge mb-0">
            Votre enfant ne se connecte pas ici.{' '}
            <Link href="/connexion/eleve">Sa page est celle-là</Link>, avec son
            pseudo et le code de la famille.
          </p>
        </div>

        <div className="col-lg-6 col-xl-5">
          {cree ? (
            <div className="alert alert-success" role="status">
              <strong>Votre compte est créé.</strong> Connectez-vous avec le mot de
              passe que vous venez de choisir. Votre code de famille vous attend
              dans « Enfants ».
            </div>
          ) : null}

          <div className="sc-feuille-auth">
            <ParentLoginForm />
          </div>

          <p className="mt-4 mb-0 text-secondary">
            Pas encore de compte ? <Link href="/inscription">En créer un</Link>
          </p>
        </div>
      </div>
    </main>
  );
}
