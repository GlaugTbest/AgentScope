import type { NextConfig } from 'next';

export const getDistDir = (env: Record<string, string | undefined> = process.env) => env.NEXT_DIST_DIR || '.next';

const config: NextConfig = {
  distDir: getDistDir(),
  allowedDevOrigins: ['127.0.0.1'],
};
export default config;
