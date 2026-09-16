import { describe, expect, it } from 'vitest';
import { buildWaterfall } from '../lib/waterfall';

describe('buildWaterfall', () => {
  it('nests children and safely renders zero-duration traces', () => {
    const rows = buildWaterfall({ start_time: '2026-01-01T00:00:00Z', end_time: '2026-01-01T00:00:00Z' }, [
      { span_id: 'parent', parent_span_id: null, start_time: '2026-01-01T00:00:00Z', end_time: '2026-01-01T00:00:00Z' },
      { span_id: 'child', parent_span_id: 'parent', start_time: '2026-01-01T00:00:00Z', end_time: '2026-01-01T00:00:00Z' },
    ]);
    expect(rows.map((row) => row.depth)).toEqual([0, 1]);
    expect(rows.every((row) => Number.isFinite(row.left) && Number.isFinite(row.width))).toBe(true);
  });
});
