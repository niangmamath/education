import { defineConfig, globalIgnores } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';
import nextTypeScript from 'eslint-config-next/typescript';

export default defineConfig([
  ...nextVitals,
  ...nextTypeScript,

  {
    rules: {
      // React impose la signature d'une action de formulaire — l'état précédent
      // puis les données — même quand l'action n'a besoin d'aucun des deux. Le
      // tiret bas est la façon convenue de dire « ce paramètre existe pour la
      // forme » ; sans cette règle, il faudrait inventer un usage factice.
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },

  globalIgnores([
    '.next/**',
    'out/**',
    'build/**',
    'coverage/**',
    'next-env.d.ts',
    '*.tsbuildinfo',
  ]),
]);
