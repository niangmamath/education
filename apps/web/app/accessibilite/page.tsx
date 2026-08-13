import Link from 'next/link';
import { InterfaceState } from '../../components/ui/interface-state';
import { PrototypeNotice } from '../../components/ui/prototype-notice';

export const metadata = {
  title: 'États et accessibilité',
  description: 'Démonstration interne des états d’interface accessibles de StudentConnect',
};

const states = [
  { kind: 'loading' as const, title: 'Chargement', description: 'Le contenu est en cours de préparation. Veuillez patienter.' },
  { kind: 'empty' as const, title: 'Aucune donnée', description: 'Aucun contenu n’est disponible pour le moment.' },
  { kind: 'error' as const, title: 'Erreur', description: 'Le contenu n’a pas pu être chargé. Une nouvelle tentative sera possible.' },
  { kind: 'success' as const, title: 'Succès', description: 'L’action a été réalisée correctement.' },
  { kind: 'forbidden' as const, title: 'Accès refusé', description: 'Cette ressource ne peut pas être consultée avec cet accès.' },
  { kind: 'authentication' as const, title: 'Connexion requise', description: 'Une connexion sera nécessaire pour ouvrir cet espace protégé.' },
  { kind: 'unavailable' as const, title: 'Contenu indisponible', description: 'Ce contenu n’est pas encore disponible dans le prototype.' },
  { kind: 'offline' as const, title: 'Réseau dégradé', description: 'La connexion semble instable. Les actions non enregistrées seront signalées.' },
];

export default function AccessibilityStatesPage() {
  return (
    <main className="container py-5" id="contenu-principal">
      <PrototypeNotice />
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Démonstration interne</p>
        <h1 className="display-6 fw-bold">États d’interface et accessibilité</h1>
        <p className="lead text-secondary mb-0">
          Chaque état associe une icône, un titre et un message. La couleur n’est jamais le seul indicateur.
        </p>
      </header>

      <div className="row g-4">
        {states.map((state) => (
          <div className="col-12 col-md-6 col-xl-4" key={state.kind}>
            <InterfaceState
              {...state}
              action={state.kind === 'authentication' ? <Link href="/connexion" className="btn btn-primary">Aller à la connexion</Link> : undefined}
            />
          </div>
        ))}
      </div>

      <section className="card border-0 shadow-sm mt-5" aria-labelledby="keyboard-title">
        <div className="card-body p-4">
          <h2 id="keyboard-title" className="h4">Contrôles manuels attendus</h2>
          <ul className="mb-0">
            <li>Parcourir tous les liens avec la touche Tab.</li>
            <li>Vérifier que le focus reste visible.</li>
            <li>Tester le zoom du navigateur à 200 %.</li>
            <li>Tester les largeurs mobile, tablette et bureau.</li>
            <li>Vérifier que les messages restent compréhensibles sans la couleur.</li>
          </ul>
        </div>
      </section>
    </main>
  );
}
