/** Cálculos de mídia e reflexões editoriais: não dependem de tempos inventados. */
const isFiniteNumber = value => typeof value === 'number' && Number.isFinite(value);
const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));

export function formatTime(seconds) {
  if (!isFiniteNumber(seconds) || seconds < 0) return '00:00';
  const wholeSeconds = Math.floor(seconds);
  const hours = Math.floor(wholeSeconds / 3600);
  const minutes = Math.floor((wholeSeconds % 3600) / 60);
  const remainder = wholeSeconds % 60;
  const pair = value => String(value).padStart(2, '0');
  return hours > 0
    ? `${pair(hours)}:${pair(minutes)}:${pair(remainder)}`
    : `${pair(minutes)}:${pair(remainder)}`;
}

export function seekPosition(current, delta, duration) {
  if (![current, delta, duration].every(isFiniteNumber) || duration <= 0) return 0;
  // Normalize stale positions before applying the requested move.
  return clamp(clamp(current, 0, duration) + delta, 0, duration);
}

export function progressPercent(current, duration) {
  if (![current, duration].every(isFiniteNumber) || duration <= 0) return 0;
  // Clamp before dividing so even extreme finite inputs stay finite.
  return (clamp(current, 0, duration) / duration) * 100;
}

export const REFLECTIONS = [
  {
    id: 'projeto',
    title: 'O projeto e a pesquisa',
    prompt: 'O que a pesquisa estuda dentro do ecossistema?',
    answer: 'O OpenCode Ecosystem Core organiza agentes, ferramentas e registros de trabalho. A dissertação investiga uma peça desse conjunto: o roteamento, que compara candidatos e escolhe quem recebe uma tarefa. O MIRA ajuda a apresentar as ideias; ele não é o mecanismo de roteamento estudado.',
    href: '#ecossistema',
    linkLabel: 'Explorar o projeto',
  },
  {
    id: 'pesos',
    title: 'Pesos e chances de sucesso',
    prompt: 'Ana recebe cerca de 53% do peso. Isso significa 53% de chance de sucesso?',
    answer: 'Não. O peso representa a parcela de Ana na comparação entre os candidatos disponíveis. Ele não foi calibrado como probabilidade de sucesso. No exemplo, a tarefa inteira seria encaminhada ao primeiro colocado; os pesos não dividem o trabalho em porcentagens.',
    href: '#laboratorio',
    linkLabel: 'Experimentar os pesos',
  },
  {
    id: 'provas',
    title: 'O alcance das provas',
    prompt: 'As provas matemáticas garantem que todos os agentes funcionarão?',
    answer: 'Não. As provas estabelecem propriedades da fórmula sobre números reais, sob as condições declaradas. Elas não certificam todo o programa, o funcionamento de todos os agentes ou a execução de tarefas reais. Os experimentos sintéticos também têm alcance limitado.',
    href: '#evidencias',
    linkLabel: 'Conhecer os resultados',
  },
];
