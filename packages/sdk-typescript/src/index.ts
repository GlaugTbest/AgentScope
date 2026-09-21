export type EventType = 'execution.started' | 'activity.updated' | 'span.started' | 'span.ended' | 'execution.completed' | 'execution.failed';
type Json = Record<string, unknown>;
type EventPayload = { event_id: string; schema_version: '1.0'; type: EventType; source: string; project_id: string; agent_name: string; agent_id?: string; instance_id: string; execution_id: string; occurred_at: string; payload: Json };
type Transport = { sendEvents(events: EventPayload[]): Promise<void>; sendTrace(trace: Json): Promise<void> };

const sensitive = new Set(['api_key', 'authorization', 'password', 'secret', 'token']);
const id = () => crypto.randomUUID();
const now = () => new Date().toISOString();
function sanitize(value: unknown): unknown { if (Array.isArray(value)) return value.map(sanitize); if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value as Json).map(([key, item]) => [key, sensitive.has(key.toLowerCase()) ? '[REDACTED]' : sanitize(item)])); return value; }

class HttpTransport implements Transport {
  constructor(private endpoint: string, private apiKey: string) {}
  async sendEvents(events: EventPayload[]) { await this.post('/v1/events', { events }); }
  async sendTrace(trace: Json) { await this.post('/v1/ingest', trace); }
  private async post(path: string, body: unknown) { const response = await fetch(`${this.endpoint.replace(/\/$/, '')}${path}`, { method: 'POST', headers: { Authorization: `Bearer ${this.apiKey}`, 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); if (!response.ok) throw new Error(`AgentScope transport failed: ${response.status}`); }
}

export class AgentScope {
  readonly instanceId = id();
  private pending: EventPayload[] = [];
  private failures = 0;
  private transport: Transport;
  constructor(options: { endpoint?: string; apiKey?: string; projectId?: string; agentId?: string; transport?: Transport } = {}) { this.endpoint = options.endpoint ?? 'http://127.0.0.1:8000'; this.apiKey = options.apiKey ?? 'dev'; this.projectId = options.projectId ?? 'local'; this.agentId = options.agentId; this.transport = options.transport ?? new HttpTransport(this.endpoint, this.apiKey); }
  readonly endpoint: string; readonly apiKey: string; readonly projectId: string; readonly agentId?: string;
  trace(agentName: string, metadata: Json = {}) { return new Trace(this, agentName, metadata); }
  emit(type: EventType, trace: Trace, payload: Json = {}) { this.pending.push({ event_id: id(), schema_version: '1.0', type, source: 'agentscope-typescript', project_id: this.projectId, agent_name: trace.agentName, agent_id: this.agentId, instance_id: this.instanceId, execution_id: trace.id, occurred_at: now(), payload: sanitize(payload) as Json }); }
  async flush() { const events = this.pending.splice(0); if (!events.length) return; try { await this.transport.sendEvents(events); } catch { this.failures += events.length; } }
  diagnostics() { return { pending: this.pending.length, failed: this.failures }; }
  async sendTrace(trace: Json) { try { await this.transport.sendTrace(trace); } catch { this.failures += 1; } }
}

export class Trace {
  readonly id = id(); readonly spans: Json[] = []; private started = now();
  constructor(readonly scope: AgentScope, readonly agentName: string, readonly metadata: Json) { scope.emit('execution.started', this, { metadata }); }
  activity(message: string, details: Json = {}) { this.scope.emit('activity.updated', this, { message, ...details }); }
  startSpan(type: string, name: string, metadata: Json = {}) { const span = { span_id: id(), trace_id: this.id, parent_span_id: null, type, name, start_time: now(), metadata: sanitize(metadata), status: 'success' }; this.scope.emit('span.started', this, { span_id: span.span_id, name, span_type: type }); return span; }
  endSpan(span: Json, options: { inputTokens?: number; outputTokens?: number; estimatedCost?: string; error?: Json } = {}) { const finished = { ...span, end_time: now(), input_tokens: options.inputTokens ?? 0, output_tokens: options.outputTokens ?? 0, estimated_cost: options.estimatedCost ?? '0', error: options.error ? sanitize(options.error) : null, status: options.error ? 'error' : 'success', input: null, output: null }; this.spans.push(finished); this.scope.emit('span.ended', this, { span_id: span.span_id, status: finished.status }); }
  async end(error?: Error) { const end = now(); const failure = error ? { type: error.name, message: error.message } : null; this.scope.emit(error ? 'execution.failed' : 'execution.completed', this, failure ? { error: failure } : {}); await this.scope.sendTrace({ trace: { trace_id: this.id, agent_name: this.agentName, start_time: this.started, end_time: end, status: error ? 'error' : 'success', metadata: sanitize(this.metadata), error: failure }, spans: this.spans }); await this.scope.flush(); }
}
