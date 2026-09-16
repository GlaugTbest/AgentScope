import { spawnSync } from 'node:child_process';
const py = process.platform === 'win32' ? '.venv\\Scripts\\python.exe' : '.venv/bin/python';
const run = (cmd, args, cwd = '.', env = {}) => { const r = spawnSync(cmd, args, { cwd, env: { ...process.env, ...env }, stdio: 'inherit', shell: process.platform === 'win32' }); if (r.status !== 0) process.exit(r.status ?? 1); };
run(py, ['-m', 'pytest', '-q']); run(py, ['-m', 'ruff', 'check', 'apps/api/src', 'packages/sdk-python/src']); run('npm', ['run', 'typecheck'], 'apps/web'); run('npm', ['run', 'lint'], 'apps/web'); run('npm', ['run', 'test'], 'apps/web'); run('npm', ['run', 'build'], 'apps/web', { NEXT_DIST_DIR: '.next-check' });
