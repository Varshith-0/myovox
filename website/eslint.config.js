import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist', 'node_modules']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
  },
  // The MediaLayer scrubs the <video>/poster elements imperatively in a RAF loop
  // (mutating refs and element styles outside React rendering). The React-Compiler
  // immutability rule (which assumes hook values are pure) doesn't apply there.
  {
    files: ['src/components/media/**/*.tsx'],
    rules: {
      'react-hooks/immutability': 'off',
    },
  },
])
