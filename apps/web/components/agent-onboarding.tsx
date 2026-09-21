'use client';

import { useEffect } from 'react';

export function onboardingCopy(locale: 'pt-BR' | 'en') {
  if (locale === 'en') return {
    title: 'Connect an agent', example: 'with scope.trace("research-agent") as trace:', manualName: 'Use research-agent as the manual registration name.', automatic: 'Instrumented agents appear automatically after their first trace or activity event.', privacy: 'capture_content=True is optional. Redact sensitive data before sending it.', close: 'Close',
  };
  return {
    title: 'Como conectar um agente', example: 'with scope.trace("research-agent") as trace:', manualName: 'Use research-agent como o nome no cadastro manual.', automatic: 'Agentes instrumentados aparecem automaticamente após o primeiro trace ou evento de atividade.', privacy: 'capture_content=True é opcional. Redija dados sensíveis antes de enviá-los.', close: 'Fechar',
  };
}

export function AgentOnboarding({ open, locale, onClose }: { open: boolean; locale: 'pt-BR' | 'en'; onClose: () => void }) {
  const copy = onboardingCopy(locale);
  useEffect(() => {
    if (!open) return;
    const close = (event: KeyboardEvent) => event.key === 'Escape' && onClose();
    window.addEventListener('keydown', close); return () => window.removeEventListener('keydown', close);
  }, [open, onClose]);
  if (!open) return null;
  return <div className="onboarding-backdrop" role="presentation" onMouseDown={onClose}><section className="onboarding-dialog" role="dialog" aria-modal="true" aria-labelledby="agent-help-title" onMouseDown={(event) => event.stopPropagation()}><div className="section-heading"><h2 id="agent-help-title">{copy.title}</h2><button className="copy-span" onClick={onClose}>{copy.close}</button></div><p>{copy.automatic}</p><pre className="onboarding-code">from agentscope import AgentScope{`\n`}scope = AgentScope(){`\n`}{copy.example}{`\n`}    pass</pre><p>{copy.manualName}</p><p className="onboarding-privacy">{copy.privacy}</p></section></div>;
}
