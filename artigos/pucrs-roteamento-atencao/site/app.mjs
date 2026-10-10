import { rankCandidates } from './router.mjs';
import { MISSIONS, QUESTIONS, evaluateMission, gradeAnswer } from './learning.mjs';
import { createTourState, transitionTour, getTourView } from './ecosystem.mjs';

const $ = (selector) => document.querySelector(selector);
const format = (value, digits = 2) => value.toLocaleString('pt-BR', { minimumFractionDigits: digits, maximumFractionDigits: digits });
const state = { scenario: 'original', trust: 0.9, load: 0.1, bia: false, modified: false };
let missionIndex = 0;
let missionTouched = false;
const discoveries = new Set();

function candidates() {
  const empty = state.scenario === 'empty';
  return [
    { id: 'ana', name: 'Ana', semantic: 0.8417, trust: state.trust, load: state.load, capabilities: ['pesquisa', 'sintese'], status: empty || state.scenario === 'unavailable' ? 'busy' : 'available' },
    { id: 'cid', name: 'Cid', semantic: 0.7703, trust: 0.7, load: 0.4, capabilities: ['pesquisa', 'sintese'], status: empty ? 'busy' : 'available' },
    { id: 'bia', name: 'Bia', semantic: 0.8, trust: 0.88, load: 0.2, capabilities: ['pesquisa', 'sintese'], status: state.bia && !empty ? 'available' : 'busy' },
  ];
}

function row(candidate, winner = false) {
  const element = document.createElement('div');
  const excluded = 'reason' in candidate;
  element.className = `candidate-row${excluded ? ' excluded' : ''}${winner ? ' winner' : ''}`;
  const avatar = document.createElement('span');
  avatar.className = 'avatar';
  avatar.textContent = candidate.name[0];
  avatar.setAttribute('aria-hidden', 'true');
  const middle = document.createElement('div');
  const title = document.createElement('div');
  title.className = 'candidate-name';
  title.textContent = candidate.name;
  const annotation = document.createElement('small');
  annotation.textContent = excluded ? 'indisponível' : winner ? 'primeiro da lista' : 'participa';
  title.append(annotation);
  const meter = document.createElement('div');
  meter.className = 'candidate-meter';
  meter.setAttribute('aria-hidden', 'true');
  if (!excluded) {
    const fill = document.createElement('i');
    fill.style.setProperty('--weight', `${candidate.weight * 100}%`);
    meter.append(fill);
  }
  middle.append(title, meter);
  const number = document.createElement('div');
  number.className = 'candidate-value';
  number.textContent = excluded ? 'Fora da soma' : `${format(candidate.weight * 100)}%`;
  if (!excluded) {
    const utility = document.createElement('small');
    utility.textContent = `nota = ${format(candidate.utility, 4)}`;
    number.append(utility);
  }
  element.append(avatar, middle, number);
  return element;
}

function update() {
  const source = candidates();
  const { ranked, excluded } = rankCandidates(source, ['pesquisa', 'sintese']);
  $('#trust-value').textContent = format(state.trust);
  $('#load-value').textContent = format(state.load);
  $('#trust').value = state.trust;
  $('#load').value = state.load;
  $('#include-bia').checked = state.bia;
  $('#trust').disabled = state.scenario === 'empty' || state.scenario === 'unavailable';
  $('#load').disabled = state.scenario === 'empty' || state.scenario === 'unavailable';
  $('#include-bia').disabled = state.scenario === 'empty';
  const list = $('#ranking');
  list.replaceChildren();
  ranked.forEach((candidate, index) => list.append(row(candidate, index === 0)));
  excluded.forEach((candidate) => list.append(row(candidate)));
  $('#eligible-count').textContent = `${ranked.length} participante${ranked.length === 1 ? '' : 's'}`;
  $('#weight-sum').textContent = format(ranked.reduce((sum, candidate) => sum + candidate.weight, 0), 4);
  const winner = ranked[0];
  $('#selected-agent').textContent = winner?.name ?? 'Nenhuma escolha';
  $('#decision-reason').textContent = !winner ? 'Ninguém está disponível para atender ao pedido. O mecanismo aguarda uma alternativa.' : ranked.length === 1 ? `${winner.name} é o único participante disponível e recebe todas as fichas da comparação.` : `${winner.name} ficou em primeiro ao combinar as quatro notas. Os demais participantes continuam na comparação.`;
  $('#weight-meaning').textContent = winner ? 'Os pesos equivalem a 100% das fichas repartidas. Não representam chance de sucesso.' : 'Sem participantes, não há fichas para repartir: a soma é zero.';
  updateMission({ ranked, excluded });
  $('#demo-note').textContent = state.scenario === 'original' && !state.modified && !state.bia ? 'Valores arredondados do exemplo do trabalho. O contexto e Bia são ilustrativos.' : 'Exemplo didático modificado. Estes valores não são resultados experimentais do artigo.';
  const table = $('#criteria-table');
  table.replaceChildren();
  for (const candidate of source) {
    const entry = ranked.find((item) => item.id === candidate.id);
    const tr = document.createElement('tr');
    [candidate.name, format(candidate.semantic, 4), format(candidate.trust), format(candidate.load), entry ? format(entry.utility, 4) : 'Excluído'].forEach((value) => {
      const td = document.createElement('td'); td.textContent = value; tr.append(td);
    });
    table.append(tr);
  }
  document.querySelectorAll('[data-scenario]').forEach((button) => {
    const selected = button.dataset.scenario === state.scenario;
    button.classList.toggle('active', selected);
    button.setAttribute('aria-pressed', String(selected));
  });
}

document.querySelectorAll('[data-scenario]').forEach((button) => button.addEventListener('click', () => {
  Object.assign(state, { scenario: button.dataset.scenario, trust: 0.9, load: button.dataset.scenario === 'load' ? 1 : 0.1, bia: false, modified: false });
  missionTouched = true;
  update();
}));
$('#trust').addEventListener('input', (event) => { state.trust = Number(event.target.value); state.modified = true; missionTouched = true; update(); });
$('#load').addEventListener('input', (event) => { state.load = Number(event.target.value); state.modified = true; missionTouched = true; update(); });
$('#include-bia').addEventListener('change', (event) => { state.bia = event.target.checked; missionTouched = true; update(); });
function updateMission(result) {
  const mission = MISSIONS[missionIndex];
  const feedback = evaluateMission(missionIndex, result);
  if (feedback.complete && missionTouched) discoveries.add(missionIndex);
  $('#mission-label').textContent = `DESAFIO ${missionIndex + 1} DE ${MISSIONS.length}`;
  $('#mission-title').textContent = mission.title;
  $('#mission-prompt').textContent = mission.prompt;
  $('#mission-hint').textContent = mission.hint;
  const discovered = discoveries.has(missionIndex);
  $('#mission-feedback').classList.toggle('complete', discovered);
  $('#mission-feedback').textContent = discovered ? feedback.complete ? `Descoberta feita. ${feedback.message}` : 'Você já concluiu este desafio. Continue explorando ou avance para o próximo.' : missionTouched ? feedback.message : 'Experimente os controles abaixo. O resultado aparece a cada mudança.';
  $('#mission-progress').value = discoveries.size;
  $('#mission-progress-label').textContent = `${discoveries.size} de ${MISSIONS.length} descobertas`;
  $('#mission-next').disabled = !discovered;
  $('#mission-next').textContent = missionIndex === MISSIONS.length - 1 ? 'Refazer desafios ↻' : 'Próximo desafio →';
}
$('#mission-hint-button').addEventListener('click', () => {
  const open = $('#mission-hint').hidden;
  $('#mission-hint').hidden = !open;
  $('#mission-hint-button').setAttribute('aria-expanded', String(open));
  $('#mission-hint-button').textContent = open ? 'Ocultar pista' : 'Quero uma pista';
});
$('#mission-next').addEventListener('click', () => {
  if (missionIndex === MISSIONS.length - 1) { missionIndex = 0; discoveries.clear(); }
  else missionIndex += 1;
  missionTouched = false;
  Object.assign(state, { scenario: 'original', trust: 0.9, load: 0.1, bia: false, modified: false });
  $('#mission-hint').hidden = true;
  $('#mission-hint-button').setAttribute('aria-expanded', 'false');
  $('#mission-hint-button').textContent = 'Quero uma pista';
  update();
  $('#mission-title').setAttribute('tabindex', '-1');
  $('#mission-title').focus({ preventScroll: true });
});
update();

const storySteps = [
  { title: 'Um pedido chega', text: 'Você precisa reunir informações e escrever um resumo. Antes de escolher quem vai ajudar, é preciso entender quais capacidades o pedido exige.', takeaway: 'Primeiro, entenda a tarefa.', gate: 'Entender o pedido ↓', ana: 'Pode ajudar', cid: 'Pode ajudar', bia: 'Indisponível', caption: 'Uma analogia para entender o mecanismo. Nenhum programa é executado aqui.' },
  { title: 'Só participa quem pode atender', text: 'Ana e Cid têm as capacidades pedidas e estão disponíveis. Bia não aceita novas tarefas neste momento, então fica fora antes de comparar as notas.', takeaway: 'Uma ótima avaliação não substitui a disponibilidade.', gate: 'Filtro: disponível + capacidades ↓', ana: 'Participa', cid: 'Participa', bia: 'Fora da comparação', caption: 'Estar indisponível exclui. Ter muita carga é diferente: reduz a nota, mas não exclui por si só.' },
  { title: 'As notas viram pesos', text: 'Comparamos quanto cada programa combina com o pedido, suas capacidades, confiança e carga. Imagine repartir 100 fichas: Ana recebe cerca de 53 e Cid, 47.', takeaway: 'As fichas mostram a comparação. Não são chances de sucesso.', gate: 'Comparar os quatro critérios ↓', ana: 'Nota ≈ 0,9175', cid: 'Nota ≈ 0,8161', bia: 'Fora da comparação', caption: 'Os números partem do exemplo Ana/Cid do trabalho. As fichas foram arredondadas para explicar a ideia.' },
  { title: 'O maior peso define a escolha', text: 'Ana tem o maior peso neste exemplo, então receberia a tarefa. Cid continua apto. As fichas servem para comparar: a tarefa seria encaminhada apenas ao primeiro colocado. Se as notas ou a disponibilidade mudarem, a escolha também pode mudar.', takeaway: 'A escolha tem uma razão que podemos acompanhar.', gate: 'Maior peso → Ana', ana: 'Escolhida no exemplo', cid: 'Continua apto', bia: 'Fora da comparação', caption: 'O laboratório mostra como a escolha muda. A animação ilustra a decisão; não executa os programas.' },
];
let storyIndex = 0;
function showStory(index, focus = false) {
  storyIndex = Math.max(0, Math.min(storySteps.length - 1, index));
  const step = storySteps[storyIndex];
  $('.story-shell').dataset.stage = String(storyIndex);
  $('#story-step').textContent = `ETAPA ${storyIndex + 1} DE ${storySteps.length}`;
  $('#story-title').textContent = step.title;
  $('#story-explanation').textContent = step.text;
  $('#story-takeaway').textContent = step.takeaway;
  $('#team-gate').textContent = step.gate;
  $('#team-ana-state').textContent = step.ana;
  $('#team-cid-state').textContent = step.cid;
  $('#team-bia-state').textContent = step.bia;
  $('#story-caption').textContent = step.caption;
  $('#attention-tokens').hidden = storyIndex < 2;
  $('#story-prev').disabled = storyIndex === 0;
  $('#story-next').hidden = storyIndex === storySteps.length - 1;
  $('#story-try').hidden = storyIndex !== storySteps.length - 1;
  document.querySelectorAll('[data-story]').forEach((button) => button.setAttribute('aria-pressed', String(Number(button.dataset.story) === storyIndex)));
  if (focus) { $('#story-title').setAttribute('tabindex', '-1'); $('#story-title').focus({ preventScroll: true }); }
}
document.querySelectorAll('[data-story]').forEach((button) => button.addEventListener('click', () => showStory(Number(button.dataset.story))));
$('#story-prev').addEventListener('click', () => showStory(storyIndex - 1, true));
$('#story-next').addEventListener('click', () => showStory(storyIndex + 1, true));
showStory(0);

let quizIndex = 0;
function renderQuestion(focus = false) {
  const question = QUESTIONS[quizIndex];
  $('#quiz-count').textContent = `PERGUNTA ${quizIndex + 1} DE ${QUESTIONS.length}`;
  $('#quiz-question').textContent = question.prompt;
  $('#quiz-options').setAttribute('aria-labelledby', 'quiz-question');
  $('#quiz-options').replaceChildren();
  for (const option of question.options) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'quiz-option';
    button.setAttribute('aria-pressed', 'false');
    const letter = document.createElement('span');
    letter.textContent = option.id.toUpperCase();
    letter.setAttribute('aria-hidden', 'true');
    const copy = document.createElement('span');
    copy.textContent = option.text;
    button.append(letter, copy);
    button.addEventListener('click', () => {
      const feedback = gradeAnswer(quizIndex, option.id);
      document.querySelectorAll('.quiz-option').forEach((item) => { item.setAttribute('aria-pressed', String(item === button)); item.classList.remove('correct', 'retry'); });
      button.classList.add(feedback.correct ? 'correct' : 'retry');
      $('#quiz-feedback').textContent = feedback.message;
      $('#quiz-feedback').classList.toggle('correct', feedback.correct);
      $('#quiz-next').disabled = !feedback.correct;
      if (feedback.correct) document.querySelectorAll('.quiz-option').forEach((item) => { if (item !== button) item.disabled = true; });
    });
    $('#quiz-options').append(button);
  }
  $('#quiz-feedback').classList.remove('correct');
  $('#quiz-feedback').textContent = 'Escolha uma alternativa para ver a explicação.';
  $('#quiz-next').disabled = true;
  $('#quiz-next').textContent = quizIndex === QUESTIONS.length - 1 ? 'Concluir e retomar as ideias →' : 'Próxima pergunta →';
  if (focus) { $('#quiz-question').setAttribute('tabindex', '-1'); $('#quiz-question').focus({ preventScroll: true }); }
}
$('#quiz-next').addEventListener('click', () => {
  if (quizIndex < QUESTIONS.length - 1) { quizIndex += 1; renderQuestion(true); }
  else {
    $('#quiz-question-panel').hidden = true;
    $('#quiz-summary').hidden = false;
    const title = $('#quiz-summary h3'); title.setAttribute('tabindex', '-1'); title.focus({ preventScroll: true });
  }
});
$('#quiz-restart').addEventListener('click', () => {
  quizIndex = 0;
  $('#quiz-summary').hidden = true;
  $('#quiz-question-panel').hidden = false;
  renderQuestion(true);
});
renderQuestion();

let ecosystemState = createTourState();
function renderEcosystem(focus = false) {
  const view = getTourView(ecosystemState);
  const container = $('#ecosystem-tour');
  container.dataset.step = String(ecosystemState.step);
  container.dataset.scope = ecosystemState.scope;
  container.style.setProperty('--tour-progress', `${ecosystemState.step / 3 * 100}%`);
  $('#eco-step-count').textContent = `ETAPA ${ecosystemState.step + 1} DE 4`;
  $('#eco-step-title').textContent = view.step.title;
  $('#eco-step-text').textContent = view.step.text;
  $('#eco-step-takeaway').textContent = view.step.takeaway;
  $('#eco-prev').disabled = !view.canPrevious;
  $('#eco-next').disabled = !view.canNext;
  $('#eco-research-link').hidden = !view.isResearchStep;
  $('#eco-scope-tag').textContent = view.scope.tag;
  $('#eco-scope-title').textContent = view.scope.title;
  $('#eco-scope-text').textContent = view.scope.text;
  $('#eco-mira-path').hidden = ecosystemState.scope !== 'mira';
  document.querySelectorAll('[data-eco-stage]').forEach((button) => button.setAttribute('aria-pressed', String(Number(button.dataset.ecoStage) === ecosystemState.step)));
  document.querySelectorAll('[data-eco-scope]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.ecoScope === ecosystemState.scope)));
  document.querySelectorAll('[data-eco-resource]').forEach((link) => { link.hidden = link.dataset.ecoResource !== ecosystemState.scope; });
  if (focus) { $('#eco-step-title').setAttribute('tabindex', '-1'); $('#eco-step-title').focus({ preventScroll: true }); }
}
function moveEcosystem(action, focus = false) { ecosystemState = transitionTour(ecosystemState, action); renderEcosystem(focus); }
document.querySelectorAll('[data-eco-stage]').forEach((button) => button.addEventListener('click', () => moveEcosystem({ type: 'step', value: Number(button.dataset.ecoStage) })));
document.querySelectorAll('[data-eco-scope]').forEach((button) => button.addEventListener('click', () => moveEcosystem({ type: 'scope', value: button.dataset.ecoScope })));
$('#eco-prev').addEventListener('click', () => moveEcosystem({ type: 'previous' }, true));
$('#eco-next').addEventListener('click', () => moveEcosystem({ type: 'next' }, true));
$('#eco-restart').addEventListener('click', () => moveEcosystem({ type: 'restart' }, true));
for (const selector of ['[data-eco-stage]', '[data-eco-scope]']) {
  const buttons = [...document.querySelectorAll(selector)];
  buttons.forEach((button, index) => button.addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key) || event.altKey || event.ctrlKey || event.metaKey) return;
    event.preventDefault(); event.stopPropagation();
    const target = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 : Math.max(0, Math.min(buttons.length - 1, index + (event.key === 'ArrowRight' ? 1 : -1)));
    buttons[target].focus(); buttons[target].click();
  }));
}
renderEcosystem();

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let paused = reducedMotion.matches;
function updateMotion() {
  document.body.classList.toggle('paused', paused);
  $('#motion-toggle').setAttribute('aria-pressed', String(paused));
  $('#motion-toggle').setAttribute('aria-label', paused ? 'Retomar movimento' : 'Pausar movimento');
  $('#motion-toggle').innerHTML = `<span aria-hidden="true">${paused ? '▷' : 'Ⅱ'}</span> ${paused ? 'Retomar movimento' : 'Pausar movimento'}`;
}
$('#motion-toggle').addEventListener('click', () => { paused = !paused; updateMotion(); });
reducedMotion.addEventListener('change', (event) => { if (event.matches) paused = true; updateMotion(); });
updateMotion();

const slides = [...document.querySelectorAll('.presentation-section')];
let presenting = false;
let currentSlide = 0;
let previousScroll = 0;
function showSlide(index, focus = true) {
  currentSlide = Math.max(0, Math.min(slides.length - 1, index));
  slides.forEach((slide, i) => slide.classList.toggle('current-slide', i === currentSlide));
  $('#slide-count').textContent = `${currentSlide + 1} / ${slides.length}`;
  $('#slide-title').textContent = slides[currentSlide].dataset.title;
  $('#slide-prev').disabled = currentSlide === 0;
  $('#slide-next').disabled = currentSlide === slides.length - 1;
  window.scrollTo({ top: 0, behavior: 'instant' });
  if (focus) {
    const title = slides[currentSlide].querySelector('h1,h2');
    title.setAttribute('tabindex', '-1');
    title.focus({ preventScroll: true });
  }
}
function startPresentation() {
  previousScroll = window.scrollY;
  presenting = true;
  document.body.classList.add('presenting');
  $('#presentation-bar').hidden = false;
  showSlide(0);
}
function closePresentation() {
  presenting = false;
  document.body.classList.remove('presenting');
  $('#presentation-bar').hidden = true;
  slides.forEach((slide) => slide.classList.remove('current-slide'));
  window.scrollTo({ top: previousScroll, behavior: 'instant' });
  $('#presentation-start').focus({ preventScroll: true });
}
$('#presentation-start').addEventListener('click', startPresentation);
$('#presentation-close').addEventListener('click', closePresentation);
$('#slide-prev').addEventListener('click', () => showSlide(currentSlide - 1));
$('#slide-next').addEventListener('click', () => showSlide(currentSlide + 1));
document.addEventListener('keydown', (event) => {
  if (!presenting) return;
  if (event.key === 'Escape') { event.preventDefault(); closePresentation(); return; }
  if (event.target.closest('input,textarea,select,summary') || event.altKey || event.ctrlKey || event.metaKey) return;
  if (event.key === 'ArrowRight' || event.key === 'PageDown') { event.preventDefault(); showSlide(currentSlide + 1); }
  if (event.key === 'ArrowLeft' || event.key === 'PageUp') { event.preventDefault(); showSlide(currentSlide - 1); }
  if (event.key === 'Home') { event.preventDefault(); showSlide(0); }
  if (event.key === 'End') { event.preventDefault(); showSlide(slides.length - 1); }
});
document.querySelectorAll('a[href^="#"]').forEach((link) => link.addEventListener('click', (event) => {
  if (!presenting) return;
  const target = slides.findIndex((slide) => `#${slide.id}` === link.getAttribute('href'));
  if (target >= 0) { event.preventDefault(); showSlide(target); }
}));
