import { Dashboard } from '../components/dashboard';
import { ThemeToggle } from '../components/theme-toggle';
export default function Page(){return <main className="app-shell"><header className="app-header"><a className="brand" href="/"><span className="brand-signal"/>AgentScope</a><div className="header-meta"><span>Observabilidade para agentes</span><span className="local-pill">Local</span><ThemeToggle/></div></header><Dashboard/></main>}
