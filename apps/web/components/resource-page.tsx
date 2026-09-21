'use client';

import { useEffect, useState } from 'react';
import { AppHeader } from './app-header';

export function ResourcePage({ title, endpoint, needsProject = false }: { title: string; endpoint: string; needsProject?: boolean }) {
  const key = `agentscope.page.${endpoint}`;
  const [project, setProject] = useState('local');
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [error, setError] = useState('');
  const load = async () => {
    const query = needsProject ? `?project_id=${encodeURIComponent(project)}` : '';
    const response = await fetch(`${endpoint}${query}`);
    const payload = await response.json();
    if (!response.ok) return setError(payload.detail || 'Não foi possível carregar os dados.');
    setItems(payload.items || []); setError(''); window.localStorage.setItem(key, project);
  };
  useEffect(() => { const saved = window.localStorage.getItem(key); if (saved) setProject(saved); }, [key]);
  useEffect(() => { load(); }, []); // Initial local view; the button applies changed persistent filters.
  return <main className="app-shell"><AppHeader/><section className="observatory standalone"><div className="controlbar"><div><span className="overline">Ambiente local</span><h1>{title}</h1><p>Dados persistidos pela API local.</p></div>{needsProject && <div className="controls"><input aria-label="Projeto" value={project} onChange={(event) => setProject(event.target.value)} /><button className="button primary" onClick={load}>Aplicar filtro</button></div>}</div>{error && <p className="notice">{error}</p>}<div className="table-wrap"><table><thead><tr><th>Identificador</th><th>Detalhes</th></tr></thead><tbody>{items.length ? items.map((item, index) => <tr key={String(item.agent_id || item.instance_id || item.execution_id || index)}><td className="mono">{String(item.agent_id || item.instance_id || item.execution_id || '—')}</td><td><pre className="json-preview">{JSON.stringify(item, null, 2)}</pre></td></tr>) : <tr><td colSpan={2}>Nenhum dado encontrado.</td></tr>}</tbody></table></div></section></main>;
}
