import { rankCandidates } from './router.mjs';

const $ = (selector) => document.querySelector(selector);
const format = (value, digits = 2) => value.toLocaleString('pt-BR', { minimumFractionDigits: digits, maximumFractionDigits: digits });
const state = { scenario: 'original', trust: 0.9, load: 0.1, bia: false, modified: false };

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
  annotation.textContent = excluded ? 'indisponível' : winner ? 'maior peso' : 'elegível';
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
    utility.textContent = `u = ${format(candidate.utility, 4)}`;
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
  $('#eligible-count').textContent = `${ranked.length} candidato${ranked.length === 1 ? '' : 's'}`;
  $('#weight-sum').textContent = format(ranked.reduce((sum, candidate) => sum + candidate.weight, 0), 4);
  const winner = ranked[0];
  $('#selected-agent').textContent = winner?.name ?? 'Nenhuma escolha';
  $('#decision-reason').textContent = !winner ? 'Nenhum candidato passou pelo filtro de elegibilidade.' : ranked.length === 1 ? 'Único candidato elegível: recebe todo o peso.' : 'Maior peso entre os candidatos elegíveis.';
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
  update();
}));
$('#trust').addEventListener('input', (event) => { state.trust = Number(event.target.value); state.modified = true; update(); });
$('#load').addEventListener('input', (event) => { state.load = Number(event.target.value); state.modified = true; update(); });
$('#include-bia').addEventListener('change', (event) => { state.bia = event.target.checked; update(); });
update();

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
