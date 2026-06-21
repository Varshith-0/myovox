import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist', 'node_modules', 'scripts/_assets']),
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
  // Build-time Node scripts (the head baker) — plain JS, Node globals.
  {
    files: ['scripts/**/*.{js,mjs}'],
    extends: [js.configs.recommended],
    languageOptions: {
      globals: globals.node,
      sourceType: 'module',
    },
  },
  // The 3D layer mutates three.js objects (uniforms, transforms) imperatively in
  // useFrame — outside React rendering. The React-Compiler immutability rule
  // (which assumes hook values are pure) doesn't apply to that pattern.
  {
    files: ['src/components/three/**/*.tsx'],
    rules: {
      'react-hooks/immutability': 'off',
    },
  },
])
