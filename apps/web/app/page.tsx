import { Dashboard } from '../components/dashboard';
export default function Page(){return <main className="app-shell"><header className="app-header"><a className="brand" href="/"><span className="brand-signal"/>AgentScope</a><div className="header-meta"><span>Observabilidade para agentes</span><span className="local-pill">Local</span></div></header><Dashboard/></main>}
