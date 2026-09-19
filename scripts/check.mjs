import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';
const py = process.platform === 'win32' ? '.venv\\Scripts\\python.exe' : '.venv/bin/python';
const run = (cmd, args, cwd = '.', env = {}) => { const isWindowsNpm = process.platform === 'win32' && cmd === 'npm'; const executable = isWindowsNpm ? process.execPath : cmd; const commandArgs = isWindowsNpm ? [resolve(process.execPath, '..', 'node_modules', 'npm', 'bin', 'npm-cli.js'), ...args] : args; const r = spawnSync(executable, commandArgs, { cwd, env: { ...process.env, ...env }, stdio: 'inherit' }); if (r.status !== 0) process.exit(r.status ?? 1); };
run(py, ['-m', 'pytest', '-q']); run(py, ['-m', 'ruff', 'check', 'apps/api/src', 'packages/sdk-python/src']); run('npm', ['run', 'typecheck'], 'apps/web'); run('npm', ['run', 'lint'], 'apps/web'); run('npm', ['run', 'test'], 'apps/web'); run('npm', ['run', 'build'], 'apps/web', { NEXT_DIST_DIR: '.next-check' });
