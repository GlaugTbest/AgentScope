import { spawn } from 'node:child_process';
import { resolve } from 'node:path';

const root = process.cwd();
const py = process.platform === 'win32'
  ? resolve(root, '.venv', 'Scripts', 'python.exe')
  : resolve(root, '.venv', 'bin', 'python');
const webCommand = process.platform === 'win32' ? process.execPath : 'npm';
const webArgs = process.platform === 'win32'
  ? [resolve(process.execPath, '..', 'node_modules', 'npm', 'bin', 'npm-cli.js'), 'run', 'dev']
  : ['run', 'dev'];
const api = spawn(py, ['-m', 'uvicorn', 'agentscope_api.main:app', '--host', '127.0.0.1', '--port', '8000'], { stdio: 'inherit', cwd: resolve(root, 'apps/api') });
const web = spawn(webCommand, webArgs, { stdio: 'inherit', cwd: resolve(root, 'apps/web') });
const stop = () => { api.kill(); web.kill(); process.exit(); };
process.on('SIGINT', stop); process.on('SIGTERM', stop);
api.on('exit', code => { if (code) stop(); }); web.on('exit', code => { if (code) stop(); });
