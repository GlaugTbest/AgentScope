'use client';

import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { activityText } from '../lib/activity';
import { useLocale } from './locale-toggle';
import type { Agent, Execution, Trace } from '../lib/types';

const number = new Intl.NumberFormat('pt-BR');
const stamp = (date: string) => new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: 'short' }).format(new Date(date));

export function Dashboard() {
  const locale = useLocale();
  const en = locale === 'en';
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [data, setData] = useState<any>();
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [status, setStatus] = useState('');
  const [creating, setCreating] = useState(false);
  const [running, setRunning] = useState(false);
  const [notice, setNotice] = useState('');
  const active = useMemo(() => agents.find((agent) => agent.agent_id === selected) ?? null, [agents, selected]);

  const load = useCallback(async () => {
    try {
      const query = new URLSearchParams();
      if (status) query.set('status', status);
      if (active) query.set('agent_name', active.name);
      const suffix = query.toString() ? `?${query}` : '';
      const [agentsResponse, tracesResponse, summaryResponse, executionsResponse, latencyResponse] = await Promise.all([
        fetch('/api/agents'), fetch(`/api/traces${suffix}`), fetch(`/api/traces/summary${suffix}`), fetch('/api/executions?state=executing'), fetch(`/api/metrics/latency${suffix}`),
      ]);
      if (![agentsResponse, tracesResponse, summaryResponse, executionsResponse, latencyResponse].every((response) => response.ok)) throw new Error();
      const nextAgents = (await agentsResponse.json()).items as Agent[];
      setAgents(nextAgents);
      setSelected((current) => current && nextAgents.some((agent) => agent.agent_id === current) ? current : nextAgents[0]?.agent_id ?? null);
      setData({ traces: await tracesResponse.json(), summary: await summaryResponse.json(), latency: await latencyResponse.json() });
      setExecutions((await executionsResponse.json()).items as Execution[]);
    } catch {
      setNotice(en ? 'Unable to refresh data. Check the local API.' : 'Não foi possível atualizar os dados. Verifique a API local.');
    }
  }, [active?.name, status, en]);

  useEffect(() => {
    load();
    const timer = setInterval(() => { if (!document.hidden) load(); }, 3000);
    return () => clearInterval(timer);
  }, [load]);

  useEffect(() => {
    const saved = window.localStorage.getItem('agentscope.dashboard.filters');
    if (!saved) return;
    try { const filters = JSON.parse(saved); if (typeof filters.status === 'string') setStatus(filters.status); if (typeof filters.selected === 'string') setSelected(filters.selected); } catch { window.localStorage.removeItem('agentscope.dashboard.filters'); }
  }, []);

  useEffect(() => { window.localStorage.setItem('agentscope.dashboard.filters', JSON.stringify({ status, selected })); }, [status, selected]);

  async function createAgent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const name = String(form.get('name') || '').trim();
    if (!name) return;
    setCreating(true);
    const response = await fetch('/api/agents', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, description: String(form.get('description') || '').trim() || null }) });
    const payload = await response.json();
    setCreating(false);
    if (!response.ok) return setNotice(payload.detail || (en ? 'Unable to create this agent.' : 'Não foi possível cadastrar este agente.'));
    event.currentTarget.reset();
    setSelected(payload.agent_id);
    setNotice(en ? 'Agent created. Run the demo to generate the first trace.' : 'Agente criado. Rode a demo para gerar o primeiro trace.');
    await load();
  }

  async function demo() {
    if (!active) return;
    setRunning(true);
    setNotice(en ? 'Running the scenario and recording spans…' : 'Executando cenário sintético e gravando spans…');
    const response = await fetch(`/api/agents/${active.agent_id}/demo`, { method: 'POST' });
    const payload = await response.json();
    setRunning(false);
    if (!response.ok) return setNotice(payload.detail || (en ? 'The demo did not finish.' : 'A demo não foi concluída.'));
    setNotice(en ? `Demo complete: ${payload.span_count} spans stored for ${active.name}.` : `Demo concluída: ${payload.span_count} spans persistidos para ${active.name}.`);
    await load();
  }

  const summary = data?.summary;
  return <div className="workbench">
    <aside className="agents-panel" aria-label={en ? 'Agents' : 'Agentes'}>
      <div className="panel-heading"><span>{en ? 'Agents' : 'Agentes'}</span><span className="count">{agents.length}</span></div>
      <div className="agent-list">{agents.length ? agents.map((agent) => <button className={`agent-row ${agent.agent_id === selected ? 'selected' : ''}`} key={agent.agent_id} onClick={() => setSelected(agent.agent_id)}><span className="agent-mark">{agent.name.slice(0, 1).toUpperCase()}</span><span><strong>{agent.name}</strong><small>{agent.description || (en ? 'No description' : 'Sem descrição')}</small></span></button>) : <p className="empty-mini">{en ? 'No agents yet. Create the first one to begin.' : 'Ainda não há agentes. Crie o primeiro para começar.'}</p>}</div>
      <form className="agent-form" onSubmit={createAgent}><label htmlFor="agent-name">{en ? 'New agent' : 'Novo agente'}</label><input id="agent-name" name="name" placeholder="ex.: research-agent" maxLength={200} required /><input name="description" placeholder={en ? 'Optional description' : 'Descrição opcional'} maxLength={500} /><button className="button ghost" disabled={creating}>{creating ? (en ? 'Creating…' : 'Criando…') : (en ? 'Create agent' : 'Cadastrar agente')}</button></form>
    </aside>
    <section className="observatory">
      <div className="controlbar"><div><span className="overline">{en ? 'Local environment' : 'Ambiente local'}</span><h1>{active ? active.name : (en ? 'Agent observatory' : 'Observatório de agentes')}</h1><p>{active?.description || (en ? 'Create an agent to begin an observability session.' : 'Crie um agente para começar uma sessão de observabilidade.')}</p></div><div className="controls"><select aria-label={en ? 'Filter traces by status' : 'Filtrar traces por status'} value={status} onChange={(event) => setStatus(event.target.value)}><option value="">{en ? 'All results' : 'Todos os resultados'}</option><option value="success">{en ? 'Successful' : 'Com sucesso'}</option><option value="error">{en ? 'Failed' : 'Com erro'}</option></select><button className="button primary" onClick={demo} disabled={!active || running}>{running ? (en ? 'Running demo…' : 'Executando demo…') : (en ? 'Run demo' : 'Rodar demo')}</button></div></div>
      {notice && <div className="notice" role="status">{notice}</div>}
      {summary && <div className="metrics">{[['Traces', summary.total_traces], ['Concluídos', summary.success_rate == null ? '—' : `${Math.round(summary.success_rate * 100)}%`], ['P50', data.latency?.p50_ms == null ? '—' : `${Math.round(data.latency.p50_ms)} ms`], ['P95', data.latency?.p95_ms == null ? '—' : `${Math.round(data.latency.p95_ms)} ms`], ['P99', data.latency?.p99_ms == null ? '—' : `${Math.round(data.latency.p99_ms)} ms`], ['Tokens', number.format(summary.total_tokens)], ['Custo estimado', `$${summary.estimated_cost}`], ['Falhas', summary.failed_traces]].map(([label, value]) => <div className="metric" key={String(label)}><span>{label}</span><strong>{value}</strong></div>)}</div>}
      {executions.length > 0 && <section className="activity-feed" aria-live="polite"><div><h2>Atividade ao vivo</h2><p>Atualizações registradas pelos próprios agentes.</p></div><ul>{executions.map((execution) => <li key={execution.execution_id}><span className="live-dot" /><div><strong>{execution.agent_name}</strong><p>{activityText(execution)}</p></div><time dateTime={execution.last_event_at}>{stamp(execution.last_event_at)}</time></li>)}</ul></section>}
      <div className="trace-head"><div><h2>Execuções recentes</h2><p>Dados persistidos pela API; atualização automática a cada 3 segundos.</p></div><span className="live-dot">Ao vivo</span></div>
      {!data ? <div className="loading-lines"><i /><i /><i /></div> : data.traces.total === 0 ? <div className="empty-traces"><h2>Seu espaço está pronto para uma primeira execução.</h2><p>{active ? 'A demo cria planejamento, busca, retrieval e resposta — tudo salvo neste painel.' : 'Cadastre um agente à esquerda. Depois, o modo demo produzirá traces reais.'}</p>{active && <button className="button primary" onClick={demo}>Criar trace de demonstração</button>}</div> : <div className="table-wrap"><table><thead><tr><th>Execução</th><th>Resultado</th><th>Duração</th><th>Tokens</th><th>Custo</th><th>Spans</th><th>Início</th></tr></thead><tbody>{data.traces.items.map((trace: Trace) => <tr data-link key={trace.trace_id} onClick={() => location.href = `/traces/${trace.trace_id}`}><td><strong>{trace.agent_name}</strong><small className="mono">{trace.trace_id.slice(0, 8)}</small></td><td><span className={`status ${trace.status}`}>{trace.status === 'success' ? 'Concluído' : 'Com erro'}</span></td><td>{trace.duration_ms} ms</td><td>{number.format(trace.total_tokens)}</td><td>${trace.estimated_cost}</td><td>{trace.span_count}</td><td>{stamp(trace.start_time)}</td></tr>)}</tbody></table></div>}
    </section>
  </div>;
}
