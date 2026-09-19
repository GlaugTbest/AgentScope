import { describe, expect, it } from 'vitest';
import { activityText } from '../lib/activity';

describe('activityText', () => {
  it('uses an event message when the agent supplied one', () => {
    expect(activityText({ execution_id: 'run', agent_name: 'researcher', state: 'executing', last_event_at: '2026-01-01T00:00:00Z', metadata: { latest_activity: { message: 'Consultando documentos' } } })).toBe('Consultando documentos');
  });

  it('makes the absence of activity explicit without inferring hidden reasoning', () => {
    expect(activityText({ execution_id: 'run', agent_name: 'researcher', state: 'executing', last_event_at: '2026-01-01T00:00:00Z', metadata: {} })).toBe('Executando e aguardando nova atualização.');
  });
});
