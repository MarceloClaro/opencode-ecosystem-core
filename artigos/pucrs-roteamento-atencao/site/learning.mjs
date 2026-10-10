/** Atividades didáticas: conferem o cálculo do laboratório sem refazê-lo. */

export const MISSIONS = [
  {
    id: 'comparar',
    title: 'Mude a escolha, mantenha a equipe',
    prompt: 'Mantenha Ana disponível e altere os controles até Cid ficar em primeiro.',
    hint: 'Diminua a confiança atribuída a Ana e observe os dois pesos. Ana deve continuar disponível.',
    explanation: 'Cid passou a ter o maior peso e Ana continua na comparação. A confiança e os demais critérios podem mudar a escolha entre candidatos disponíveis. Os pesos descrevem essa comparação; não medem a chance de sucesso.',
  },
  {
    id: 'filtrar',
    title: 'Veja o filtro em ação',
    prompt: 'Deixe Cid como o único candidato disponível: Ana deve ficar fora da comparação.',
    hint: 'Use o cenário em que Ana está indisponível e mantenha Bia fora da comparação.',
    explanation: 'Ana foi excluída antes da comparação e Cid ficou como o único candidato elegível. Por isso recebe 100% do peso. Esse 100% distribui o total entre os disponíveis; não garante sucesso na tarefa.',
  },
  {
    id: 'vazio',
    title: 'Reconheça quando não há escolha',
    prompt: 'Deixe todos os candidatos indisponíveis e observe o que acontece com a escolha.',
    hint: 'Experimente o cenário sem candidatos disponíveis. A lista deve mostrar quem ficou de fora.',
    explanation: 'Ninguém passou pelo filtro de disponibilidade. O mecanismo deixa a escolha vazia, em vez de atribuir peso a um candidato que não pode atender ao pedido. Em uma aplicação, seria preciso aguardar ou buscar outra alternativa.',
  },
];

export const QUESTIONS = [
  {
    id: 'disponibilidade',
    prompt: 'Bia tem uma ótima avaliação, mas está indisponível para novas tarefas. O que o mecanismo faz?',
    options: [
      { id: 'a', text: 'Escolhe Bia, porque sua avaliação é alta.' },
      { id: 'b', text: 'Exclui Bia antes de comparar os candidatos disponíveis.' },
      { id: 'c', text: 'Mantém Bia na comparação com um peso menor.' },
    ],
    correctId: 'b',
    explanation: 'O status de Bia é indisponível, então ela fica fora antes da comparação. Carga alta, por sua vez, apenas reduz a nota de um candidato que continua disponível. A disponibilidade é uma condição para participar; uma avaliação alta não substitui essa condição.',
  },
  {
    id: 'peso',
    prompt: 'Um candidato recebeu 53% do peso. O que esse número significa?',
    options: [
      { id: 'a', text: 'Ele tem 53% de chance de executar a tarefa com sucesso.' },
      { id: 'b', text: 'Ele acertou 53% das tarefas em um novo experimento.' },
      { id: 'c', text: 'Ele recebeu essa parcela dos pesos da comparação atual.' },
    ],
    correctId: 'c',
    explanation: 'Os 53% são uma parcela do total de pesos desta comparação. Não significam 53% de chance de sucesso: o trabalho não calibrou esses pesos como probabilidades de acerto.',
  },
  {
    id: 'provas',
    prompt: 'As provas matemáticas em Lean 4 permitem afirmar o quê?',
    options: [
      { id: 'a', text: 'Certas propriedades das fórmulas foram demonstradas sob as condições declaradas.' },
      { id: 'b', text: 'Toda execução do programa e de todos os agentes está certificada.' },
      { id: 'c', text: 'O sistema terá o mesmo desempenho em qualquer aplicação real.' },
    ],
    correctId: 'a',
    explanation: 'A prova matemática demonstra propriedades do núcleo formalizado, sob condições declaradas. Ela não certifica toda execução do programa, todos os agentes ou seu desempenho em aplicações reais.',
  },
];

function assertIndex(index, collection) {
  if (!Number.isInteger(index)) {
    throw new TypeError('Informe o índice da atividade como um número inteiro.');
  }
  if (index < 0 || index >= collection.length) {
    throw new RangeError('A atividade informada não existe.');
  }
}

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function assertRoutingResult(result) {
  if (!isRecord(result) || !Array.isArray(result.ranked) || !Array.isArray(result.excluded)) {
    throw new TypeError('Informe o resultado do roteador, com as listas de candidatos comparados e excluídos.');
  }
  for (const candidate of result.ranked) {
    if (!isRecord(candidate) || typeof candidate.id !== 'string' || !candidate.id.trim() ||
        !Number.isFinite(candidate.weight) || candidate.weight < 0 || candidate.weight > 1) {
      throw new TypeError('A lista de candidatos comparados contém um resultado inválido.');
    }
  }
  for (const candidate of result.excluded) {
    if (!isRecord(candidate) || typeof candidate.reason !== 'string' || !candidate.reason.trim()) {
      throw new TypeError('Cada exclusão deve conter o motivo informado pelo roteador.');
    }
  }
}

/** Recebe diretamente {ranked, excluded} produzido por rankCandidates. */
export function evaluateMission(index, result) {
  assertIndex(index, MISSIONS);
  assertRoutingResult(result);
  const { ranked, excluded } = result;
  let complete;
  let pending;
  if (index === 0) {
    complete = ranked[0]?.id === 'cid' && ranked.some((candidate) => candidate.id === 'ana');
    pending = 'Continue explorando: Cid precisa ter o maior peso, e Ana deve continuar na comparação. Experimente diminuir a confiança de Ana.';
  } else if (index === 1) {
    complete = ranked.length === 1 && ranked[0].id === 'cid' && excluded.some((candidate) => candidate.id === 'ana');
    pending = 'Ainda há um ajuste: Cid deve ser o único candidato comparado, e Ana precisa aparecer entre os excluídos.';
  } else {
    complete = ranked.length === 0 && excluded.length >= 1;
    pending = 'O desafio pede que ninguém esteja disponível. A lista deve ficar sem escolha e mostrar os candidatos excluídos.';
  }
  return { complete, message: complete ? MISSIONS[index].explanation : pending };
}

/** Confere uma alternativa e explica o princípio tanto no acerto quanto no erro. */
export function gradeAnswer(index, answerId) {
  assertIndex(index, QUESTIONS);
  if (typeof answerId !== 'string') {
    throw new TypeError('Informe o identificador da alternativa como texto.');
  }
  const question = QUESTIONS[index];
  if (!question.options.some((option) => option.id === answerId)) {
    throw new RangeError('A alternativa informada não existe nesta pergunta.');
  }
  const correct = answerId === question.correctId;
  return {
    correct,
    message: `${correct ? 'Isso mesmo.' : 'Reveja este ponto e tente novamente.'} ${question.explanation}`,
  };
}
