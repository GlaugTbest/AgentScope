import parser from '@typescript-eslint/parser';

export default [{
  ignores: ['.next/**', 'node_modules/**'],
  files: ['**/*.{ts,tsx}'],
  languageOptions: { parser, parserOptions: { ecmaFeatures: { jsx: true } } },
  rules: {},
}];
