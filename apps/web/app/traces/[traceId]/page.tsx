'use client';

import { useEffect, useState } from 'react';
import { describeSpan, redactForDisplay } from '../../../lib/trace-content';
import { buildWaterfall } from '../../../lib/waterfall';

function Payload({ label, value }: { label: string; value: unknown }) {
  if (value == null) return null;
  return <section className="payload"><h4>{label}</h4><pre>{JSON.stringify(redactForDisplay(value), null, 2)}</pre></section>;
}

export default function Detail({ params }: { params: Promise<{ traceId: string }> }) {
  const [data, setData] = useState<any>();

  useEffect(() => {
    params.then(({ traceId }) => fetch(`/api/traces/${traceId}`).then((response) => response.ok ? response.json() : null).then(setData));
  }, [params]);

  if (!data) return <main className="shell"><p className="muted">Carregando execução…</p></main>;

  const rows = buildWaterfall(data.trace, data.spans);
  return <main className="shell trace-detail">
    <a href="/" className="muted">← Todas as execuções</a>
    <header className="top"><div><div className="brand">{data.trace.agent_name}</div><div className="mono muted">{data.trace.trace_id}</div></div><strong className={data.trace.status}>{data.trace.status}</strong></header>

    <section className="execution-story" aria-labelledby="work-heading">
      <div className="section-heading"><div><h2 id="work-heading">O que foi feito</h2><p>Etapas registradas pelo agente durante esta execução.</p></div><span>{rows.length} etapas</span></div>
      <div className="execution-steps">
        {rows.map((span: Record<string, unknown> & { span_id: string; depth: number; duration_ms: number; status: string; type: string }) => {
          const description = describeSpan(span);
          return <article className={`execution-step ${span.status}`} key={span.span_id}>
            <div className="step-marker" aria-hidden="true" />
            <div className="step-body">
              <div className="step-topline"><span className="step-type">{span.type}</span><span className="mono">{span.duration_ms} ms</span></div>
              <h3 style={{ paddingLeft: span.depth * 16 }}>{description.action}</h3>
              <p>{description.outcome}</p>
              {description.hasDetails && <details><summary>Ver dados capturados</summary><div className="payload-grid"><Payload label="Entrada" value={span.input} /><Payload label="Saída" value={span.output} /><Payload label="Metadados" value={span.metadata} /><Payload label="Erro" value={span.error} /></div></details>}
            </div>
            <button className="copy-span" onClick={() => navigator.clipboard?.writeText(span.span_id)} aria-label={`Copiar ID da etapa ${description.action}`}>Copiar ID</button>
          </article>;
        })}
      </div>
    </section>

    <div className="detail-grid">
      <section><h2>Timeline</h2><div className="waterfall">{rows.map((span: any) => <button className="water-row" key={span.span_id} onClick={() => navigator.clipboard?.writeText(span.span_id)} aria-label={`Copiar ID da etapa ${span.name}`}><span style={{ paddingLeft: span.depth * 16 }}>{span.name} <small className="muted">{span.type} · {span.duration_ms}ms</small></span><span className="track"><span className={`bar ${span.status}`} style={{ left: `${span.left}%`, width: `${span.width}%` }} /></span></button>)}</div></section>
      <aside><h2>Execução</h2><p>Tokens: {data.trace.total_tokens}</p><p>Custo: ${data.trace.estimated_cost}</p><p>Etapas: {data.trace.span_count}</p><Payload label="Metadados da execução" value={data.trace.metadata} /></aside>
    </div>
  </main>;
}
