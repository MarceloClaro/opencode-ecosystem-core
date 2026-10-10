/** Percurso ilustrativo da organização do Core: sem temporizador ou execução. */

export const ECOSYSTEM_STEPS = Object.freeze([
  {
    id: 'request',
    title: 'Um pedido chega',
    text: 'Você informa o que precisa fazer. O pedido pode chegar por um comando ou por uma integração. Primeiro, é preciso entender o objetivo e as condições da tarefa.',
    takeaway: 'O ponto de partida é um pedido com um objetivo claro.',
  },
  {
    id: 'coordination',
    title: 'O orquestrador organiza o trabalho',
    text: 'O programa coordenador recupera o contexto e organiza o encaminhamento. Pense nele como quem organiza a equipe: distribui o trabalho e acompanha as etapas. Um quadro compartilhado de tarefas e a memória ajudam a conservar as informações.',
    takeaway: 'Coordenação conecta a tarefa, os recursos e seus registros.',
  },
  {
    id: 'router',
    title: 'O roteador compara candidatos',
    text: 'Quando o fluxo usa este mecanismo, o roteador filtra quem está apto e disponível, compara os critérios e indica o primeiro colocado. A dissertação analisa essa regra de escolha.',
    takeaway: 'Esta é a peça estudada na pesquisa.',
  },
  {
    id: 'execution',
    title: 'Execução e registro dependem do ambiente',
    text: 'Com um programa ou uma ferramenta preparada e disponível, a tarefa pode ser realizada. O coordenador acompanha as etapas e guarda os resultados para conferência. A conclusão precisa ser registrada.',
    takeaway: 'Escolher um agente e concluir uma tarefa são momentos diferentes.',
  },
].map((step) => Object.freeze(step)));

export const ECOSYSTEM_SCOPES = Object.freeze([
  {
    id: 'ecosystem',
    title: 'O ecossistema completo',
    text: 'É o ambiente completo: coordenação, agentes especializados, ferramentas, contexto e registros. Essas partes ajudam a organizar tarefas de pesquisa, desenvolvimento e apresentação.',
    tag: 'ORGANIZAÇÃO DO PROJETO',
  },
  {
    id: 'research',
    title: 'A peça investigada',
    text: 'A pesquisa examina o núcleo do roteador, com provas matemáticas e testes em cenários simulados. Os resultados se referem a essa peça e às condições estudadas.',
    tag: 'ESCOPO DA DISSERTAÇÃO',
  },
  {
    id: 'mira',
    title: 'MIRA comunica as ideias',
    text: 'O MIRA transforma manuscritos em apresentações: organiza o roteiro, prepara o texto e cria elementos visuais e animação. A conformidade interna confere regras da apresentação produzida; o mérito científico exige avaliação própria.',
    tag: 'COMUNICAÇÃO DO TRABALHO',
  },
].map((scope) => Object.freeze(scope)));

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function assertStep(step) {
  if (!Number.isInteger(step)) {
    throw new TypeError('Informe a etapa como um número inteiro.');
  }
  if (step < 0 || step >= ECOSYSTEM_STEPS.length) {
    throw new RangeError('A etapa informada não existe neste percurso.');
  }
}

function assertScope(scope) {
  if (typeof scope !== 'string') {
    throw new TypeError('Informe o identificador da perspectiva como texto.');
  }
  if (!ECOSYSTEM_SCOPES.some((item) => item.id === scope)) {
    throw new RangeError('A perspectiva informada não existe neste percurso.');
  }
}

function assertState(state) {
  if (!isRecord(state)) {
    throw new TypeError('Informe o estado do percurso com etapa e perspectiva.');
  }
  assertStep(state.step);
  assertScope(state.scope);
}

export function createTourState() {
  return { step: 0, scope: 'ecosystem' };
}

/** Retorna um novo estado; a perspectiva e a etapa podem ser escolhidas separadamente. */
export function transitionTour(state, action) {
  assertState(state);
  if (!isRecord(action) || typeof action.type !== 'string') {
    throw new TypeError('Informe uma ação válida para o percurso.');
  }
  switch (action.type) {
    case 'next':
      return { step: Math.min(state.step + 1, ECOSYSTEM_STEPS.length - 1), scope: state.scope };
    case 'previous':
      return { step: Math.max(state.step - 1, 0), scope: state.scope };
    case 'restart':
      return createTourState();
    case 'step':
      assertStep(action.value);
      return { step: action.value, scope: state.scope };
    case 'scope':
      assertScope(action.value);
      return { step: state.step, scope: action.value };
    default:
      throw new RangeError('A ação informada não existe neste percurso.');
  }
}

export function getTourView(state) {
  assertState(state);
  const step = ECOSYSTEM_STEPS[state.step];
  return {
    step,
    scope: ECOSYSTEM_SCOPES.find((scope) => scope.id === state.scope),
    canPrevious: state.step > 0,
    canNext: state.step < ECOSYSTEM_STEPS.length - 1,
    isResearchStep: step.id === 'router',
  };
}
