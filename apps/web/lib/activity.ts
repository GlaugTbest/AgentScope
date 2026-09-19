import type { Execution } from './types';

const fallback: Record<Execution['state'], string> = {
  executing: 'Executando e aguardando nova atualização.',
  completed: 'Execução concluída.',
  failed: 'Execução encerrada com falha.',
  cancelled: 'Execução cancelada.',
};

export function activityText(execution: Execution) {
  const message = execution.metadata?.latest_activity?.message;
  return typeof message === 'string' && message.trim() ? message : fallback[execution.state];
}
