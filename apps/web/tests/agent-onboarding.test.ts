import { describe, expect, it } from 'vitest';
import { onboardingCopy } from '../components/agent-onboarding';

describe('agent onboarding copy', () => {
  it('explains that the SDK trace name is the manual registration name', () => {
    const copy = onboardingCopy('pt-BR');
    expect(copy.example).toContain('scope.trace("research-agent")');
    expect(copy.manualName).toContain('research-agent');
    expect(copy.privacy).toContain('capture_content=True');
  });
});
