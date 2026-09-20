export type Theme = 'dark' | 'light';

export function resolveTheme(savedTheme: string | null, systemPrefersDark: boolean): Theme {
  if (savedTheme === 'dark' || savedTheme === 'light') return savedTheme;
  return systemPrefersDark ? 'dark' : 'light';
}
