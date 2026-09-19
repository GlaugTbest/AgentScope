import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn, spawnSync } from 'node:child_process';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const apiRoot = join(root, 'apps', 'api');
const webRoot = join(root, 'apps', 'web');
const python = process.platform === 'win32'
  ? join(root, '.venv', 'Scripts', 'python.exe')
  : join(root, '.venv', 'bin', 'python');
const databaseDirectory = mkdtempSync(join(tmpdir(), 'agentscope-e2e-'));
const databaseUrl = `sqlite:///${join(databaseDirectory, 'agentscope.db').replaceAll('\\', '/')}`;
const environment = {
  ...process.env,
  AGENTSCOPE_API_KEY: 'e2e',
  AGENTSCOPE_DATABASE_URL: databaseUrl,
};

const migration = spawnSync(python, ['-m', 'alembic', '-c', 'alembic.ini', 'upgrade', 'head'], {
  cwd: apiRoot,
  env: environment,
  encoding: 'utf8',
});
if (migration.status !== 0) {
  process.stderr.write(migration.stderr || migration.stdout || 'Could not prepare the E2E database.');
  process.exit(migration.status || 1);
}

const api = spawn(python, ['-m', 'uvicorn', 'agentscope_api.main:app', '--host', '127.0.0.1', '--port', '8100'], {
  cwd: apiRoot,
  env: environment,
  stdio: 'inherit',
});
const web = spawn(process.execPath, [join(webRoot, 'node_modules', 'next', 'dist', 'bin', 'next'), 'dev', '-p', '3100'], {
  cwd: webRoot,
  env: { ...environment, AGENTSCOPE_API_URL: 'http://127.0.0.1:8100' },
  stdio: 'inherit',
});

let stopping = false;
function stop(exitCode = 0) {
  if (stopping) return;
  stopping = true;
  api.kill();
  web.kill();
  process.exit(exitCode);
}

api.on('exit', (code) => { if (!stopping) stop(code || 1); });
web.on('exit', (code) => { if (!stopping) stop(code || 1); });
process.once('SIGINT', () => stop());
process.once('SIGTERM', () => stop());
