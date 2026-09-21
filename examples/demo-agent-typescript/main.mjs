import { AgentScope } from '../../packages/sdk-typescript/dist/index.js';
const scope = new AgentScope({ apiKey: process.env.AGENTSCOPE_API_KEY || 'dev' });
const trace = scope.trace('typescript-local-agent', { example: true });
trace.activity('Executando ferramenta local');
const span = trace.startSpan('tool', 'uppercase');
const result = 'agentscope'.toUpperCase();
trace.endSpan(span, { outputTokens: result.length });
await trace.end();
console.log(result);
