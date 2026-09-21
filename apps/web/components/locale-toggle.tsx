'use client';

import { useEffect, useState } from 'react';

export type Locale = 'pt-BR' | 'en';
const key = 'agentscope.locale';

export function useLocale() {
  const [locale, setLocale] = useState<Locale>('pt-BR');
  useEffect(() => {
    const apply = () => setLocale(window.localStorage.getItem(key) === 'en' ? 'en' : 'pt-BR');
    apply(); window.addEventListener('agentscope:locale', apply);
    return () => window.removeEventListener('agentscope:locale', apply);
  }, []);
  return locale;
}

export function LocaleToggle() {
  const locale = useLocale();
  function toggle() {
    const next: Locale = locale === 'pt-BR' ? 'en' : 'pt-BR';
    window.localStorage.setItem(key, next); document.documentElement.lang = next;
    window.dispatchEvent(new Event('agentscope:locale'));
  }
  return <button className="locale-toggle" type="button" onClick={toggle} aria-label={locale === 'pt-BR' ? 'Switch to English' : 'Mudar para português'}>{locale === 'pt-BR' ? 'English' : 'Português'}</button>;
}
