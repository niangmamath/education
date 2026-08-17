import type { Metadata, Viewport } from 'next';
import { Atkinson_Hyperlegible, Bricolage_Grotesque, DM_Mono } from 'next/font/google';
import 'bootstrap/dist/css/bootstrap.min.css';
import './globals.css';

/**
 * Trois rôles, trois fontes, et une d'entre elles est un choix argumenté.
 *
 * **Atkinson Hyperlegible** porte le texte courant. Elle a été dessinée par le
 * Braille Institute pour que les lettres qu'on confond cessent de se
 * ressembler : le b et le d, le p et le q, le I et le l et le 1. Cette
 * plateforme est lue par des enfants de six ans qui sont en train d'apprendre à
 * distinguer le b du d — c'est littéralement une des questions de l'examen
 * d'initiation. Une fonte qui rend cette distinction plus dure est un obstacle
 * ajouté à celui qu'on mesure.
 *
 * C'est la version d'origine et non « Next », qui est pourtant plus riche en
 * graisses : Next n'a pas de métriques de repli dans Next.js, donc le texte
 * saute au moment où la fonte arrive. Un décalage de mise en page sur toute la
 * page vaut plus cher que deux graisses de moins.
 *
 * **Bricolage Grotesque** porte les titres, resserrée en chasse aux grandes
 * tailles. **DM Mono** porte les codes de compétence, les durées et les
 * décomptes : ce qui s'aligne en colonne et se lit comme une donnée.
 */
const display = Bricolage_Grotesque({
  subsets: ['latin', 'latin-ext'],
  axes: ['opsz', 'wdth'],
  display: 'swap',
  variable: '--font-display',
});

const texte = Atkinson_Hyperlegible({
  subsets: ['latin', 'latin-ext'],
  weight: ['400', '700'],
  display: 'swap',
  variable: '--font-texte',
});

const chiffres = DM_Mono({
  subsets: ['latin', 'latin-ext'],
  weight: ['400', '500'],
  display: 'swap',
  variable: '--font-chiffres',
});

export const metadata: Metadata = {
  title: {
    default: 'StudentConnect - Plateforme EdTech',
    template: '%s | StudentConnect',
  },
  description: 'Plateforme éducative pour les élèves de 6 à 11 ans et leurs parents',
  keywords: ['education', 'edtech', 'élèves', 'parents', 'remédiation'],
  authors: [{ name: 'tidianesarrndiaye-org' }],
  openGraph: {
    type: 'website',
    locale: 'fr_FR',
    url: 'https://studentconnect.example.com',
    siteName: 'StudentConnect',
    title: 'StudentConnect - Plateforme EdTech',
    description: 'Plateforme éducative pour les élèves de 6 à 11 ans et leurs parents',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'StudentConnect - Plateforme EdTech',
    description: 'Plateforme éducative pour les élèves de 6 à 11 ans et leurs parents',
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: '#3b3fa8',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr" data-scroll-behavior="smooth">
      <body className={`${display.variable} ${texte.variable} ${chiffres.variable}`}>
        {children}
      </body>
    </html>
  );
}
