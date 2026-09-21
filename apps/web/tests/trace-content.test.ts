import { describe, expect, it } from 'vitest';
import { describeSpan, redactForDisplay } from '../lib/trace-content';

describe('trace content presentation', () => {
  it('shows a concise completed action without exposing sensitive fields', () => {
    const summary = describeSpan({
      name: 'search-documents',
      type: 'tool',
      status: 'success',
      output: { documents: 3, answer: 'Três documentos relevantes foram encontrados.' },
    });

    expect(summary).toEqual({
      action: 'search-documents',
      outcome: 'Três documentos relevantes foram encontrados.',
      hasDetails: true,
    });
  });

  it('redacts credential-like values before they reach an execution card', () => {
    expect(redactForDisplay({
      answer: 'Resposta segura',
      authorization: 'Bearer private-value',
      nested: { token: 'secret-token' },
    })).toEqual({
      answer: 'Resposta segura',
      authorization: '[redacted]',
      nested: { token: '[redacted]' },
    });
  });

  it('redacts bearer credentials found in free-form captured text', () => {
    expect(redactForDisplay('Authorization: Bearer private-value')).toBe('Authorization: Bearer [redacted]');
  });
});
