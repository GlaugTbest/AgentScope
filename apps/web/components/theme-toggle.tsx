'use client';

import { useEffect, useState } from 'react';
import { resolveTheme, type Theme } from '../lib/theme';

const key = 'agentscope.theme';

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme | null>(null);

  useEffect(() => {
    const next = resolveTheme(window.localStorage.getItem(key), window.matchMedia('(prefers-color-scheme: dark)').matches);
    setTheme(next);
    document.documentElement.dataset.theme = next;
  }, []);

  function toggle() {
    if (!theme) return;
    const next: Theme = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.dataset.theme = next;
    window.localStorage.setItem(key, next);
  }

  return <button className="theme-toggle" type="button" onClick={toggle} disabled={!theme} aria-label={theme === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'}>{theme === 'dark' ? 'Tema claro' : 'Tema escuro'}</button>;
}
