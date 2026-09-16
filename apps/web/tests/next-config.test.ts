import { describe, expect, it } from 'vitest';
import { getDistDir } from '../next.config';

describe('Next artifact directory', () => {
  it('uses an explicit directory for isolated builds', () => {
    expect(getDistDir({ NEXT_DIST_DIR: '.next-check' })).toBe('.next-check');
  });

  it('keeps the development cache as the default', () => {
    expect(getDistDir({})).toBe('.next');
  });
});
