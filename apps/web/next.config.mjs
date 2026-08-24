/**
 * Configuration du web StudentConnect.
 *
 * @type {import('next').NextConfig}
 */

/**
 * Les hôtes publics d'où les actions serveur sont acceptées.
 *
 * Next vérifie que l'en-tête `Origin` d'une action serveur correspond à l'hôte
 * qui a rendu la page, et refuse sinon : c'est sa protection contre le CSRF, et
 * elle est utile. Derrière un tunnel — ngrok pour montrer le site à quelqu'un —
 * le navigateur envoie l'hôte public tandis que Next voit le sien, les deux ne
 * correspondent pas, et **toute connexion échoue** : se connecter est une action
 * serveur.
 *
 * `PUBLIC_HOST` déclare cet hôte, sans protocole ni barre finale. Rien n'est
 * ouvert par défaut : sans la variable, la liste est vide et le comportement
 * d'origine tient.
 */
const publicHosts = (process.env.PUBLIC_HOST ?? '')
  .split(',')
  .map((host) => host.trim().replace(/^https?:\/\//, '').replace(/\/$/, ''))
  .filter(Boolean);

const nextConfig = {
  output: 'standalone',

  typescript: {
    // Le typage est tenu par tsconfig.json et par `pnpm lint`.
    ignoreBuildErrors: false,
  },

  images: {
    unoptimized: true,
  },

  // En développement, Next refuse aussi les requêtes de développement venues
  // d'une autre origine ; le tunnel en est une.
  allowedDevOrigins: publicHosts,

  experimental: {
    serverActions: {
      allowedOrigins: publicHosts,
    },
  },

  // En-têtes de base, y compris derrière un tunnel : l'origine de contenu H5P
  // (infrastructure/nginx/content-origin.conf.template) porte déjà les siens
  // pour son propre bac à sable, mais l'application elle-même n'en avait
  // aucun. Pas de CSP ici : Next a besoin de scripts et de styles inline, et
  // la durcir sans casser le rendu demande un travail à part.
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
