const sensitiveKey = /api[_-]?key|authorization|password|secret|token/i;

export function redactForDisplay(value: unknown): unknown {
  if (typeof value === 'string') return value.replace(/(bearer\s+)[^\s,;]+/gi, '$1[redacted]');
  if (Array.isArray(value)) return value.map(redactForDisplay);
  if (!value || typeof value !== 'object') return value;
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [
    key,
    sensitiveKey.test(key) ? '[redacted]' : redactForDisplay(item),
  ]));
}

function concise(value: unknown): string | null {
  if (typeof value === 'string') return value.trim() || null;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (!value || typeof value !== 'object') return null;
  const record = value as Record<string, unknown>;
  for (const key of ['answer', 'result', 'message', 'summary', 'content']) {
    const candidate = concise(record[key]);
    if (candidate) return candidate;
  }
  const serialized = JSON.stringify(value);
  return serialized.length > 180 ? `${serialized.slice(0, 177)}…` : serialized;
}

export function describeSpan(span: Record<string, unknown>) {
  const output = redactForDisplay(span.output);
  const input = redactForDisplay(span.input);
  const outcome = concise(output) || concise(input) || (span.status === 'error' ? 'A etapa terminou com erro.' : 'Etapa concluída sem conteúdo capturado.');
  return {
    action: typeof span.name === 'string' ? span.name : 'Etapa sem nome',
    outcome,
    hasDetails: output != null || input != null || span.metadata != null || span.error != null,
  };
}
