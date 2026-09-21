'use client';

import { LocaleToggle, useLocale } from './locale-toggle';
import { ThemeToggle } from './theme-toggle';

export function AppHeader() {
  const locale = useLocale(); const en = locale === 'en';
  return <header className="app-header"><a className="brand" href="/"><span className="brand-signal"/>AgentScope</a><nav className="primary-nav" aria-label={en ? 'Main navigation' : 'Navegação principal'}><a href="/agents">{en ? 'Agents' : 'Agentes'}</a><a href="/instances">{en ? 'Instances' : 'Instâncias'}</a><a href="/executions">{en ? 'Executions' : 'Execuções'}</a><a href="/efficiency">{en ? 'Efficiency' : 'Eficiência'}</a></nav><div className="header-meta"><span>{en ? 'Agent observability' : 'Observabilidade para agentes'}</span><span className="local-pill">{en ? 'Local' : 'Local'}</span><LocaleToggle/><ThemeToggle/></div></header>;
}
