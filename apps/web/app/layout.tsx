import './globals.css';
import './navigation.css';
import './dashboard.css';
export const metadata={title:'AgentScope',description:'Observability for AI agents'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="pt-BR" suppressHydrationWarning><body>{children}</body></html>}
