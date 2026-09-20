import { describe, expect, it } from 'vitest';
import { resolveTheme } from '../lib/theme';

describe('resolveTheme', () => {
  it('keeps an explicit saved preference', () => {
    expect(resolveTheme('light', true)).toBe('light');
  });

  it('uses the system preference only when no valid preference was saved', () => {
    expect(resolveTheme(null, true)).toBe('dark');
    expect(resolveTheme('unknown', false)).toBe('light');
  });
});
