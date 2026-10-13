/* Geometria em pixels da radiografia original; os recortes são apenas uma viewport. */
let review = null;
let reviewBaseline = null;
let reviewImageId = null;
let reviewRevision = 0;
let reviewReviewer = null;
let annotationClasses = null;
let editorSelection = null;
let editorSnapshot = null;
let editorView = null;
let editorScope = 'all';
let editorGeometry = 'all';
let editorCrop = null;
let editorAnchorTooth = null;
let polygonDraft = [];
let polygonTarget = null;
let editorTool = 'move';
let pointerDrag = null;
let brushMask = null;
let brushCursor = null;
let reviewDirty = false;
let reviewSaving = false;
let adminReviewMode = false;
let adminCsrf = '';
let adminEditLock = false;
let adminReviewPixelId = null;
let editLockTimer = null;
let reviewGeneration = 0;
let reviewSources = null;
let reviewSource = 'model';
let samRequest = null;
let samSuggestion = null;
let samTarget = null;
const anatomyLabels = new Set(['maxillary_sinus', 'mandibular_canal']);
const editorDialog = byId('annotation-editor');
const editCanvas = byId('edit-canvas');
const colors = {quadrants: '#e879f9', teeth: '#2dd4bf', findings: '#fb923c', additional: '#60a5fa'};
const findingColors = {impacted: '#fbbf24', caries: '#f87171', periapical_lesion: '#c084fc', deep_caries: '#fb923c'};
const findingNames = {impacted: 'Dente impactado', caries: 'Cárie',
  periapical_lesion: 'Lesão periapical', deep_caries: 'Cárie profunda'};
const completeGroups = ['quadrants', 'teeth', 'findings', 'additional'];
const scopedEditorGroups = new Set(['quadrants', 'teeth', 'findings']);
const editorButtonIds = ['edit-quadrants', 'edit-teeth', 'edit-tooth-masks', 'edit-findings', 'edit-additional', 'edit-anatomy'];

function setEditorButtonsDisabled(disabled) {
  for (const id of editorButtonIds) byId(id).disabled = disabled;
}

function additionalClassColor(label) {
  if (label === 'mandibular_canal') return '#f472b6';
  if (label === 'maxillary_sinus') return '#60a5fa';
  let hash = 0;
  for (const character of String(label || 'additional')) {
    hash = (hash * 31 + character.codePointAt(0)) >>> 0;
  }
  return `hsl(${hash % 360} 82% 64%)`;
}

function annotationColor(row) {
  if (row.group === 'findings') return findingColors[row.label] || additionalClassColor(row.label);
  if (row.group === 'additional') return additionalClassColor(row.label);
  return colors[row.group];
}

function feedbackHeaders() {
  return byId('key').value ? {'X-API-Key': byId('key').value} : {};
}

function reviewStatus(message, error = false) {
  byId('review-status').textContent = message;
  byId('review-status').style.color = error ? '#fca5a5' : '#94a3b8';
}

async function releaseAdminEditLock() {
  clearInterval(editLockTimer); editLockTimer = null;
  if (!adminReviewMode || !adminEditLock || !reviewImageId) return;
  adminEditLock = false;
  try {
    await fetch(`/admin/api/images/${encodeURIComponent(reviewImageId)}/edit-lock`, {
      method: 'DELETE', cache: 'no-store', keepalive: true,
      headers: {'X-Panoramica-CSRF': adminCsrf}
    });
  } catch (_) { /* The five-minute lease also releases abandoned editors. */ }
}

function startEditLockHeartbeat() {
  clearInterval(editLockTimer);
  editLockTimer = setInterval(async () => {
    if (!adminReviewMode || !adminEditLock || !reviewImageId) return;
    try {
      const response = await fetch(
        `/admin/api/images/${encodeURIComponent(reviewImageId)}/edit-lock`,
        {method: 'POST', cache: 'no-store', headers: {'X-Panoramica-CSRF': adminCsrf}}
      );
      if (response.ok) return;
      const error = await response.json();
      adminEditLock = false; clearInterval(editLockTimer); editLockTimer = null;
      setEditorButtonsDisabled(true); byId('save-feedback').disabled = true;
      reviewStatus(error.detail || 'A reserva de edicao expirou. Reabra a radiografia.', true);
    } catch (_) { /* A lease remains valid through a brief network interruption. */ }
  }, 60000);
}

function duplicateTeeth() {
  if (!review?.complete_groups.includes('teeth')) return [];
  const groups = new Map();
  for (const row of review.annotations.filter(item => item.group === 'teeth' && item.label)) {
    if (!groups.has(row.label)) groups.set(row.label, []);
    groups.get(row.label).push(row);
  }
  return [...groups.entries()].filter(([, rows]) => rows.length > 1)
    .sort(([left], [right]) => Number(left) - Number(right));
}

function showToothValidationIssues() {
  const missing = review.annotations.filter(row => row.group === 'teeth' && !row.label);
  const duplicates = duplicateTeeth();
  if (!review.complete_groups.includes('teeth') || (!missing.length && !duplicates.length)) return false;
  const status = byId('review-status');
  status.replaceChildren(); status.style.color = '#fca5a5';
  const messages = [];
  if (duplicates.length) messages.push(`FDI duplicado: ${duplicates.map(([label, rows]) => `${label} (${rows.length}x)`).join(', ')}`);
  if (missing.length) messages.push(`${missing.length} dente(s) sem numeração FDI`);
  status.append(document.createTextNode(`${messages.join(' · ')}. Escolha uma marcação para corrigir:`));
  const actions = document.createElement('div'); actions.className = 'validation-actions';
  for (const [label, rows] of duplicates) {
    rows.forEach((row, index) => {
      const button = textElement('button', '', `Editar FDI ${label} · marcação ${index + 1}`);
      button.type = 'button';
      button.addEventListener('click', () => openEditor('teeth', row.id));
      actions.append(button);
    });
  }
  missing.forEach((row, index) => {
    const button = textElement('button', '', `Definir FDI · dente ${index + 1}`);
    button.type = 'button';
    button.addEventListener('click', () => openEditor('teeth', row.id));
    actions.append(button);
  });
  status.append(actions);
  return true;
}

function syncCompleteAll() {
  const selected = completeGroups.filter(group => byId(`complete-${group}`).checked).length;
  byId('complete-all').checked = selected === completeGroups.length;
  byId('complete-all').indeterminate = selected > 0 && selected < completeGroups.length;
}

function showCompleteGroups() {
  for (const group of completeGroups) {
    byId(`complete-${group}`).checked = review.complete_groups.includes(group);
  }
  syncCompleteAll();
}

function resetFeedback() {
  resetSam();
  reviewGeneration++;
  review = null;
  reviewBaseline = null;
  reviewRevision = 0;
  reviewReviewer = null;
  reviewSources = null;
  reviewSource = 'model';
  byId('review-source-control').hidden = true;
  byId('annotation-source-status').textContent = '';
  reviewDirty = false;
  if (editorDialog.open) editorDialog.close();
  byId('feedback-panel').hidden = true;
  byId('editable-cards').hidden = true;
  byId('editable-cards').replaceChildren();
  byId('teeth').parentElement.hidden = false;
  setEditorButtonsDisabled(true);
  byId('anatomy-notes').hidden = true;
  byId('anatomy-notes').replaceChildren();
}

async function initializeFeedback(layout) {
  if (!layout.report || !layout.annotation_classes || !layout.image_id) return;
  if (adminReviewMode && adminReviewPixelId && layout.image_id !== adminReviewPixelId) {
    throw new Error('A nova análise não corresponde à radiografia aberta para revisão.');
  }
  if (!adminReviewMode) {
    adminCsrf = '';
    reviewImageId = layout.image_id;
  }
  const generation = reviewGeneration;
  reviewBaseline = structuredClone(layout.report);
  annotationClasses = layout.annotation_classes;
  const annotations = [];
  for (const [key, group, labelKey] of [
    ['teeth', 'teeth', 'fdi_candidate'], ['findings', 'findings', 'finding'],
    ['additional_information', 'additional', 'label']
  ]) {
    for (const [index, row] of (layout.report[key] || []).entries()) {
      const polygon = row.polygon_xy?.length >= 3 ? structuredClone(row.polygon_xy) : null;
      const box = [...row.bbox_xyxy];
      // Os contornos podem ultrapassar a caixa inferida em frações de pixel.
      if (polygon) {
        box[0] = Math.min(box[0], ...polygon.map(p => p[0]));
        box[1] = Math.min(box[1], ...polygon.map(p => p[1]));
        box[2] = Math.max(box[2], ...polygon.map(p => p[0]));
        box[3] = Math.max(box[3], ...polygon.map(p => p[1]));
      }
      const width = byId('original').naturalWidth, height = byId('original').naturalHeight;
      for (const point of polygon || []) {
        point[0] = Math.max(0, Math.min(width, point[0]));
        point[1] = Math.max(0, Math.min(height, point[1]));
      }
      const matches = layout.report.teeth.filter(t => t.fdi_candidate === row.fdi_candidate);
      const associated = group !== 'teeth' && row.association_status === 'candidate_requires_review' &&
        matches.length === 1 ? `teeth-${layout.report.teeth.indexOf(matches[0])}` : null;
      annotations.push({id: `${group}-${index}`, group, label: row[labelKey] ?? null, tooth_id: associated,
        bbox_xyxy: box.map((v, i) => Math.max(0, Math.min(i % 2 ? height : width, v))),
        polygon_xy: polygon, notes: '', source: 'model', model_score: row.model_score});
    }
  }
  review = {schema_version: 1, annotations, complete_groups: [], patient_group: ''};
  byId('review-age-group').value = layout.report.age_classification?.label || 'uncertain';
  reviewRevision = 0;
  reviewSource = 'model';
  reviewSources = {model: {document: structuredClone(review), baseline: reviewBaseline, dirty: false}};
  byId('review-source-control').hidden = true;
  try {
    const savedUrl = adminReviewMode
      ? `/admin/api/images/${encodeURIComponent(reviewImageId)}`
      : `/feedback/${encodeURIComponent(reviewImageId)}`;
    const response = await fetch(savedUrl, {
      headers: adminReviewMode ? {} : feedbackHeaders(), cache: 'no-store'
    });
    if (generation !== reviewGeneration) return;
    if (response.ok) {
      const saved = await response.json();
      if (saved.age_classification?.label) {
        byId('review-age-group').value = saved.age_classification.label;
      }
      if (generation !== reviewGeneration) return;
      reviewRevision = saved.revision;
      reviewReviewer = saved.reviewer || null;
      reviewSources.saved = {document: saved.document, baseline: saved.baseline, dirty: false};
      byId('review-source-control').hidden = false;
      reviewStatus(`Nova análise exibida. A revisão ${reviewRevision} continua disponível em Marcações exibidas.`);
    } else if (response.status !== 404) {
      throw new Error(`Não foi possível consultar revisões salvas (HTTP ${response.status}).`);
    } else {
      reviewStatus('Edite as marcações e salve no backend. Nenhum retreino é iniciado ao salvar.');
    }
  } catch (error) {
    if (generation !== reviewGeneration) return;
    reviewStatus(error.message, true);
  }
  byId('patient-group').value = review.patient_group;
  byId('review-source').value = reviewSource;
  updateAnnotationSource();
  showCompleteGroups();
  byId('feedback-panel').hidden = false;
  setEditorButtonsDisabled(false);
  renderEditableCards();
  await renderReviewedImages();
}

function updateAnnotationSource() {
  const versions = reviewBaseline?.provenance?.model_versions;
  const version = versions?.teeth?.version;
  const fdi = versions?.fdi?.version;
  const models = fdi ? ` · FDI ${fdi} · Segmentação ${version}` : version ? ` · ${version}` : '';
  byId('annotation-source-status').textContent = reviewSource === 'saved'
    ? `Revisão salva ${reviewRevision}${reviewReviewer ? ` · ${reviewReviewer}` : ''}${models}`
    : `Análise atual${models}`;
}

byId('review-source').addEventListener('change', async () => {
  const source = byId('review-source').value;
  if (!reviewSources?.[source] || reviewSaving) {
    byId('review-source').value = reviewSource; return;
  }
  // Guarda os dois rascunhos em memória; alternar não apaga edições nem grava no backend.
  reviewSources[reviewSource] = {document: structuredClone(review), baseline: reviewBaseline, dirty: reviewDirty};
  reviewSource = source;
  const selected = reviewSources[source];
  review = structuredClone(selected.document); reviewBaseline = selected.baseline;
  reviewDirty = selected.dirty;
  resetSam(); reviewGeneration++;
  byId('patient-group').value = review.patient_group;
  showCompleteGroups();
  updateAnnotationSource(); renderEditableCards();
  await renderReviewedImages();
  reviewStatus(`${source === 'saved' ? 'Revisão salva' : 'Análise atual'} exibida.${reviewDirty ? ' Alterações pendentes.' : ''}`);
});

function annotationName(row) {
  const name = row.group === 'additional' ? annotationClasses.additional[row.label] || row.label
    : row.group === 'findings' ? findingNames[row.label] || row.label : row.label;
  if (row.group === 'teeth') return `Dente ${name ?? 'sem FDI'}`;
  return row.group === 'quadrants' ? `Quadrante ${name}` : name;
}

function fdiLabelPosition(row, width, height, fontSize) {
  const [left, top, right, bottom] = row.bbox_xyxy;
  const lower = /^[3478]/.test(String(row.label));
  return [Math.max(fontSize, Math.min(width - fontSize, (left + right) / 2)),
    Math.max(fontSize, Math.min(height - 3, lower ? bottom + fontSize + 4 : top - 4))];
}

function renderPrintSegmentation({additionalOnly = false} = {}) {
  const original = byId('original');
  const width = original.naturalWidth, height = original.naturalHeight;
  const namespace = 'http://www.w3.org/2000/svg';
  const element = (tag, attributes) => {
    const node = document.createElementNS(namespace, tag);
    for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
    return node;
  };
  // Reutiliza o bitmap original; contornos vetoriais dispensam canvas e outro PNG.
  const svg = element('svg', {
    viewBox: `0 0 ${width} ${height}`, role: 'img',
    'aria-label': additionalOnly ? 'Radiografia com achados da IA adicional'
      : 'Radiografia com segmentação e numeração FDI, sem caixas ou descrições',
    class: additionalOnly ? 'print-additional' : 'print-segmentation', preserveAspectRatio: 'xMidYMid meet'
  });
  svg.append(element('image', {href: original.src, width, height}));
  const rows = (review?.annotations || []).filter(row => !anatomyLabels.has(row.label) &&
    (additionalOnly
      ? row.group === 'additional' && !['permanent_teeth', 'primary_teeth'].includes(row.label)
      : row.group !== 'additional'));
  for (const row of rows) {
    // Caixas sem máscara não são convertidas em contornos de segmentação.
    if (row.polygon_xy?.length >= 3) {
      svg.append(element('polygon', {
        points: row.polygon_xy.map(point => point.join(',')).join(' '),
        fill: annotationColor(row), 'fill-opacity': 0.15,
        stroke: annotationColor(row), 'stroke-width': Math.max(2, Math.min(width, height) / 350)
      }));
    } else if (additionalOnly) {
      // Achados sem máscara mantêm sua caixa real; não inventar segmentação.
      const [left, top, right, bottom] = row.bbox_xyxy;
      svg.append(element('rect', {x: left, y: top, width: right - left, height: bottom - top,
        fill: 'none', stroke: annotationColor(row),
        'stroke-width': Math.max(2, Math.min(width, height) / 350)}));
    }
  }
  if (additionalOnly) return svg;
  const fontSize = Math.max(12, Math.min(width, height) / 45);
  for (const row of rows) {
    if (row.group !== 'teeth' || row.label == null) continue;
    const [x, y] = fdiLabelPosition(row, width, height, fontSize);
    const label = element('text', {
      x, y, 'text-anchor': 'middle',
      'font-family': 'system-ui, sans-serif', 'font-size': fontSize, 'font-weight': 700,
      fill: '#ffffff', stroke: '#0f172a', 'stroke-width': 2, 'paint-order': 'stroke'
    });
    label.textContent = row.label;
    svg.append(label);
  }
  return svg;
}

function drawAnnotation(ctx, row, transform = point => point,
  {handles = false, showBox = true, showPolygon = true, showLabel = false, fillOpacity = 0,
    lineWidth = 2, labelFontSize = 12, boxHandles = handles, polygonHandles = handles} = {}) {
  ctx.strokeStyle = annotationColor(row);
  ctx.fillStyle = ctx.strokeStyle;
  ctx.lineWidth = handles ? 3 : lineWidth;
  const [x1, y1] = transform(row.bbox_xyxy.slice(0, 2));
  const [x2, y2] = transform(row.bbox_xyxy.slice(2));
  const corners = boxCorners(row).map(transform);
  if (showBox) {
    ctx.beginPath();
    corners.forEach(([x, y], index) => index ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
    ctx.closePath(); ctx.stroke();
  }
  if (showPolygon && row.polygon_xy?.length) {
    ctx.beginPath();
    row.polygon_xy.forEach((p, i) => {
      const [x, y] = transform(p);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.closePath();
    if (fillOpacity > 0 && row.polygon_xy.length >= 3) {
      ctx.save(); ctx.globalAlpha = fillOpacity; ctx.fill(); ctx.restore();
    }
    ctx.stroke();
  }
  if (showLabel) {
    const label = row.group === 'teeth' ? String(row.label ?? '?') : annotationName(row) || 'Sem classe';
    const left = Math.min(...corners.map(point => point[0]));
    const top = Math.min(...corners.map(point => point[1]));
    ctx.save();
    ctx.font = `700 ${labelFontSize}px system-ui`;
    ctx.textBaseline = 'middle';
    const padding = Math.max(4, Math.round(labelFontSize / 3));
    const height = labelFontSize + padding * 2;
    const width = Math.min(ctx.canvas.width - 2, ctx.measureText(label).width + padding * 2);
    const x = Math.max(1, Math.min(ctx.canvas.width - width - 1, left));
    const y = top >= height + 3 ? top - height - 3 : Math.min(ctx.canvas.height - height - 1, top + 3);
    ctx.fillStyle = 'rgba(7, 15, 27, 0.88)';
    ctx.fillRect(x, y, width, height);
    ctx.fillStyle = annotationColor(row);
    ctx.fillRect(x, y, 4, height);
    ctx.fillText(label, x + padding + 4, y + height / 2);
    ctx.restore();
  }
  if (handles) {
    if (boxHandles) for (const p of corners) ctx.fillRect(p[0] - 5, p[1] - 5, 10, 10);
    if (polygonHandles) for (const p of row.polygon_xy || []) {
      const [x, y] = transform(p);
      ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2); ctx.fill();
    }
  }
}

function renderEditableCards() {
  const container = byId('editable-cards');
  container.replaceChildren();
  const teeth = review.annotations.filter(a => a.group === 'teeth')
    .sort((a, b) => Number(a.label ?? 99) - Number(b.label ?? 99));
  container.hidden = !teeth.length;
  byId('teeth').parentElement.hidden = !!teeth.length;
  if (!teeth.length) return;
  byId('teeth-figure').hidden = false;
  byId('teeth').hidden = true;
  const original = byId('original');
  for (const tooth of teeth) {
    const card = document.createElement('article'); card.className = 'editable-card';
    const header = document.createElement('header');
    const edit = textElement('button', '', 'Editar'); edit.type = 'button';
    edit.addEventListener('click', () => openEditor('teeth', tooth.id, 'boxes'));
    header.append(textElement('h2', '', annotationName(tooth)), edit); card.append(header);
    const canvas = document.createElement('canvas'); canvas.width = 560; canvas.height = 220;
    const ctx = canvas.getContext('2d');
    const [x1, y1, x2, y2] = tooth.bbox_xyxy;
    const width = x2 - x1, height = y2 - y1;
    const scale = Math.min(260 / width, 185 / height);
    for (const [offset, title, marked] of [[0, 'Original (sem marcações)', false], [290, 'Marcado', true]]) {
      const left = offset + (260 - width * scale) / 2, top = 28;
      ctx.fillStyle = '#e2e8f0'; ctx.font = '14px system-ui'; ctx.fillText(title, offset + 4, 18);
      ctx.drawImage(original, x1, y1, width, height, left, top, width * scale, height * scale);
      if (marked) {
        ctx.save(); ctx.beginPath(); ctx.rect(left, top, width * scale, height * scale); ctx.clip();
        for (const row of review.annotations.filter(a => a.id === tooth.id || a.tooth_id === tooth.id)) {
          drawAnnotation(ctx, row, ([x, y]) => [left + (x - x1) * scale, top + (y - y1) * scale]);
        }
        ctx.restore();
      }
    }
    card.append(canvas);
    if (tooth.model_score != null) card.append(textElement('p', 'tooth-score', `Score original: ${tooth.model_score.toFixed(2)} · FDI exige revisão`));
    if (tooth.notes) card.append(textElement('p', '', tooth.notes));
    const associated = review.annotations.filter(a => a.tooth_id === tooth.id);
    for (const row of associated) {
      const detail = textElement('p', '', `${annotationName(row)}${row.notes ? ': ' + row.notes : ''}`);
      detail.style.color = annotationColor(row);
      card.append(detail);
    }
    if (!associated.length) card.append(textElement('p', '', 'Sem achados associados; não indica dente saudável.'));
    card.append(textElement('p', tooth.source === 'human' ? 'review-corrected' : 'review-pending',
      tooth.source === 'human' ? 'Correção manual' : 'Predição pendente de revisão'));
    container.append(card);
  }
}

function scopeRows() {
  return review.annotations.filter(row => {
    if (editorScope === 'anatomy') return anatomyLabels.has(row.label);
    if (editorScope === 'additional') return row.group === 'additional';
    if (scopedEditorGroups.has(editorScope)) return row.group === editorScope;
    if (editorScope === 'primary') return row.group !== 'additional';
    return true;
  });
}

function selectedRow() { return review.annotations.find(row => row.id === editorSelection); }

function visibleEditorRows() {
  const rows = scopeRows();
  const selected = selectedRow();
  if (!selected) return rows;
  const tool = byId('edit-tool').value;
  if (editorScope !== 'anatomy' && (tool === 'box' || tool === 'polygon')) return [selected];
  if (byId('full-image').checked) return rows;
  if (editorScope === 'anatomy') return rows;
  const toothId = selected.group === 'teeth' ? selected.id : selected.tooth_id || editorAnchorTooth;
  if (!toothId) return rows;
  return rows.filter(row => row.id === selected.id || row.id === toothId || row.tooth_id === toothId);
}

function openEditor(scope, id = null, geometry = 'all') {
  if (!review || reviewSaving) return;
  resetSam();
  editorScope = scope;
  editorGeometry = scope === 'teeth' ? geometry : 'all';
  editorSnapshot = structuredClone(review);
  editorSelection = id || scopeRows()[0]?.id || null;
  editorCrop = scope === 'all' && id ? [...selectedRow().bbox_xyxy] : null;
  editorAnchorTooth = editorCrop ? id : null;
  polygonDraft = []; polygonTarget = null; pointerDrag = null;
  byId('edit-zoom').value = '100'; byId('zoom-value').value = '100%';
  byId('full-image').checked = !editorCrop;
  byId('edit-tool').value = editorSelection ? 'move' : 'box';
  editorTool = byId('edit-tool').value;
  const titles = {
    anatomy: 'Editar seios maxilares e canal mandibular',
    additional: 'Editar anotações adicionais',
    quadrants: 'Editar quadrantes',
    teeth: editorGeometry === 'masks' ? 'Editar máscaras dentárias' : 'Editar caixas e numeração FDI',
    findings: 'Editar achados DENTEX',
  };
  byId('editor-title').textContent = titles[scope] || 'Editar marcações';
  byId('editor-hint').textContent = editorGeometry === 'masks'
    ? 'Ajuste somente o contorno da máscara. A caixa e a numeração FDI serão preservadas.'
    : editorGeometry === 'boxes'
      ? 'Mova ou redimensione somente a caixa. A máscara será preservada.'
      : 'Arraste os cantos, os vértices ou o ícone de giro abaixo da caixa.';
  refreshSelection(); fitEditorToScreen(); editorDialog.showModal(); setEditorView();
}

function fitEditorToScreen() {
  const viewport = window.visualViewport;
  for (const [property, value] of Object.entries({
    width: viewport?.width ?? innerWidth, height: viewport?.height ?? innerHeight,
    top: viewport?.offsetTop ?? 0, left: viewport?.offsetLeft ?? 0
  })) editorDialog.style.setProperty(`--editor-${property}`, `${value}px`);
}

function resizeEditor() {
  if (!editorDialog.open) return;
  fitEditorToScreen(); setEditorView({preserveHint: true});
}
window.addEventListener('resize', resizeEditor);
window.visualViewport?.addEventListener('resize', resizeEditor);
window.visualViewport?.addEventListener('scroll', resizeEditor);

function setEditorView({preserveHint = false} = {}) {
  const image = byId('original');
  if (!editorDialog.open || !image.naturalWidth || !image.naturalHeight) return;
  let bounds = [0, 0, image.naturalWidth, image.naturalHeight];
  if (!byId('full-image').checked && editorCrop) {
    const [x1, y1, x2, y2] = editorCrop;
    const margin = Math.max(30, (x2 - x1) * .6);
    bounds = [Math.max(0, x1 - margin), Math.max(0, y1 - margin),
      Math.min(image.naturalWidth, x2 + margin), Math.min(image.naturalHeight, y2 + margin)];
  }
  const zoom = Number(byId('edit-zoom').value) / 100;
  if (zoom > 1) {
    const row = selectedRow();
    const centerX = row ? (row.bbox_xyxy[0] + row.bbox_xyxy[2]) / 2 : (bounds[0] + bounds[2]) / 2;
    const centerY = row ? (row.bbox_xyxy[1] + row.bbox_xyxy[3]) / 2 : (bounds[1] + bounds[3]) / 2;
    const width = (bounds[2] - bounds[0]) / zoom;
    const height = (bounds[3] - bounds[1]) / zoom;
    const left = Math.max(0, Math.min(image.naturalWidth - width, centerX - width / 2));
    const top = Math.max(0, Math.min(image.naturalHeight - height, centerY - height / 2));
    bounds = [left, top, left + width, top + height];
  }
  editorView = bounds;
  const viewport = editCanvas.parentElement;
  if (!viewport.clientWidth || !viewport.clientHeight) return;
  const scale = Math.min(viewport.clientWidth / (bounds[2] - bounds[0]),
    viewport.clientHeight / (bounds[3] - bounds[1]));
  editCanvas.width = Math.max(1, Math.floor((bounds[2] - bounds[0]) * scale));
  editCanvas.height = Math.max(1, Math.floor((bounds[3] - bounds[1]) * scale));
  const hint = byId('editor-hint').textContent;
  redrawEditor();
  if (preserveHint) byId('editor-hint').textContent = hint;
}

new ResizeObserver(() => {
  if (editorDialog.open) setEditorView({preserveHint: true});
}).observe(editCanvas.parentElement);

function toCanvas([x, y]) {
  return [(x - editorView[0]) * editCanvas.width / (editorView[2] - editorView[0]),
    (y - editorView[1]) * editCanvas.height / (editorView[3] - editorView[1])];
}

function toImage(event) {
  const rect = editCanvas.getBoundingClientRect();
  return [Math.max(editorView[0], Math.min(editorView[2], editorView[0] + (event.clientX - rect.left) / rect.width * (editorView[2] - editorView[0]))),
    Math.max(editorView[1], Math.min(editorView[3], editorView[1] + (event.clientY - rect.top) / rect.height * (editorView[3] - editorView[1])))];
}

function redrawEditor() {
  const ctx = editCanvas.getContext('2d');
  const [x1, y1, x2, y2] = editorView;
  ctx.clearRect(0, 0, editCanvas.width, editCanvas.height);
  // Filtra só o bitmap: marcações, exportação e imagem salva mantêm suas cores e pixels.
  ctx.save();
  ctx.filter = `contrast(${byId('edit-contrast').value}%) brightness(${byId('edit-brightness').value}%)`;
  ctx.drawImage(byId('original'), x1, y1, x2 - x1, y2 - y1, 0, 0, editCanvas.width, editCanvas.height);
  ctx.restore();
  for (const row of visibleEditorRows()) {
    if (row.id !== polygonTarget) drawAnnotation(ctx, row, toCanvas, {
      handles: row.id === editorSelection && editorTool === 'move' && !samRequest && !samSuggestion,
      showBox: editorGeometry !== 'masks',
      showPolygon: editorGeometry !== 'boxes',
      boxHandles: editorGeometry !== 'masks',
      polygonHandles: editorGeometry !== 'boxes',
      showLabel: row.group === 'teeth' || row.group === 'additional'
    });
  }
  if (samSuggestion) {
    ctx.save(); ctx.strokeStyle = '#fbbf24'; ctx.fillStyle = '#fbbf2433'; ctx.lineWidth = 3;
    ctx.beginPath();
    samSuggestion.polygon_xy.forEach((point, i) => {
      const [x, y] = toCanvas(point); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y);
    });
    ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.restore();
  }
  if (pointerDrag?.mode === 'box' && pointerDrag.box) {
    drawAnnotation(ctx, {group: byId('edit-group').value, label: byId('edit-label').value,
      bbox_xyxy: pointerDrag.box}, toCanvas);
  }
  ctx.strokeStyle = '#fbbf24'; ctx.fillStyle = '#fbbf24'; ctx.lineWidth = 2;
  ctx.beginPath();
  polygonDraft.forEach((p, i) => {
    const [x, y] = toCanvas(p); if (!i) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
  for (const [index, p] of polygonDraft.entries()) {
    const [x, y] = toCanvas(p);
    ctx.beginPath(); ctx.arc(x, y, index === 0 ? 6 : 4, 0, Math.PI * 2); ctx.fill();
  }
  if (byId('edit-tool').value === 'split') {
    ctx.fillStyle = selectedRow() ? annotationColor(selectedRow()) : colors.additional;
    for (const p of selectedRow()?.polygon_xy || []) {
      const [x, y] = toCanvas(p); ctx.beginPath(); ctx.arc(x, y, 5, 0, Math.PI * 2); ctx.fill();
    }
  }
  if (brushMask && pointerDrag?.mode === 'brush') {
    ctx.save();
    ctx.globalAlpha = 0.28;
    ctx.drawImage(brushMask.canvas,
      x1 * brushMask.scale, y1 * brushMask.scale,
      (x2 - x1) * brushMask.scale, (y2 - y1) * brushMask.scale,
      0, 0, editCanvas.width, editCanvas.height);
    ctx.restore();
  }
  if (brushCursor && ['brush-add', 'brush-erase'].includes(byId('edit-tool').value)) {
    const [cx, cy] = toCanvas(brushCursor);
    const radius = Number(byId('brush-size').value) / 2 * editCanvas.width / (x2 - x1);
    ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.strokeStyle = byId('edit-tool').value === 'brush-erase' ? '#f87171' : '#5eead4';
    ctx.lineWidth = 2; ctx.setLineDash([6, 4]); ctx.stroke(); ctx.restore();
  }
  const row = selectedRow();
  if (row && editorGeometry !== 'masks' && byId('edit-tool').value === 'move' && !samRequest && !samSuggestion) {
    const corners = boxCorners(row);
    const bottom = [(corners[2][0] + corners[3][0]) / 2, (corners[2][1] + corners[3][1]) / 2];
    const [bx, by] = toCanvas(bottom), [hx, hy] = toCanvas(rotationHandle(row));
    ctx.save(); ctx.strokeStyle = annotationColor(row); ctx.fillStyle = '#111c2f'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(hx, hy); ctx.stroke();
    ctx.beginPath(); ctx.arc(hx, hy, 12, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = annotationColor(row); ctx.font = '700 17px system-ui';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('↻', hx, hy + 1); ctx.restore();
  }
  byId('edit-coordinates').textContent = row ? `Caixa (px): ${row.bbox_xyxy.map(v => v.toFixed(1)).join(', ')} · Contorno: ${row.polygon_xy?.length || 0} pontos` : 'Escolha a classe e desenhe uma caixa ou um contorno na imagem.';
  byId('finish-polygon').disabled = polygonDraft.length < 3;
  byId('delete-polygon-point').disabled = !polygonDraft.length || !!pointerDrag ||
    (!!polygonTarget && polygonDraft.length <= 3);
  byId('delete-contour').disabled = editorGeometry === 'boxes' || !row?.polygon_xy?.length || !!polygonDraft.length || !!pointerDrag;
  byId('delete-annotation').disabled = editorGeometry === 'masks' || !row;
  byId('duplicate-annotation').disabled = editorGeometry === 'masks' || !row || row.group !== 'teeth' || !!polygonDraft.length;
  byId('split-polygon').disabled = editorGeometry === 'boxes' || !row?.polygon_xy?.length || !!polygonDraft.length;
  byId('add-class').hidden = !['findings', 'additional'].includes(byId('edit-group').value);
  byId('renumber-posterior').hidden = byId('edit-group').value !== 'teeth';
  byId('renumber-posterior').disabled = editorGeometry === 'masks' || row?.group !== 'teeth' || !/^[1-4][1-8]$/.test(String(row.label || '')) ||
    !!polygonDraft.length || !!pointerDrag;
  for (const id of ['edit-group', 'edit-label', 'edit-notes', 'edit-tooth']) {
    byId(id).disabled = (editorGeometry === 'masks' && id !== 'edit-selection') || !!polygonDraft.length || (id === 'edit-group' &&
      (['anatomy', 'additional'].includes(editorScope) || scopedEditorGroups.has(editorScope))) ||
      (id === 'edit-tooth' && (!row || ['quadrants', 'teeth'].includes(row.group) || anatomyLabels.has(row.label)));
  }
  const tool = byId('edit-tool').value;
  for (const option of byId('edit-tool').options) {
    option.disabled = editorGeometry === 'boxes'
      ? !['move', 'box'].includes(option.value)
      : editorGeometry === 'masks' ? option.value === 'box' : false;
  }
  const createsAnnotation = ['anatomy', 'additional'].includes(editorScope);
  byId('brush-size-control').hidden = !['brush-add', 'brush-erase'].includes(tool);
  byId('editor-hint').textContent = tool === 'box'
    ? `Arraste na imagem para ${row && !createsAnnotation ? 'substituir a caixa selecionada' : 'criar uma nova marcação'}.`
    : tool === 'polygon'
      ? `Clique para adicionar pontos. Botão direito sobre um ponto: excluir. Delete/Backspace ou Excluir último ponto: remover o último. Clique em um ponto anterior ou em Concluir contorno para fechar. Pontos: ${polygonDraft.length}.`
      : tool === 'split' ? 'Clique em um ponto do contorno para separar e editar.'
      : tool === 'brush-add' ? (!row && editorScope === 'anatomy' && byId('edit-label').value === 'mandibular_canal'
        ? 'Pinte o canal mandibular. Ao soltar, a menor caixa será ajustada e girada automaticamente quando isso reduzir seu espaço.'
        : 'Pinte para acrescentar área ao contorno selecionado. A caixa será reajustada automaticamente.')
      : tool === 'brush-erase' ? 'Pinte para remover área do contorno selecionado. Ajuste o tamanho da borracha ao lado.'
      : row?.polygon_xy?.length ? 'Arraste os vértices, os cantos ou o ícone de giro abaixo da caixa. Separar um ponto permite editar o contorno.'
      : row ? 'Arraste a marcação, os cantos ou o ícone de giro abaixo da caixa.'
        : 'Escolha Desenhar caixa ou Desenhar contorno para criar uma marcação.';
  const samLocked = !!samRequest || !!samSuggestion;
  if (samLocked) byId('editor-hint').textContent = samSuggestion
    ? 'Aceite ou descarte a sugestão SAM para liberar a edição dos boxes e contornos.'
    : 'Aguarde o SAM concluir ou cancele a edição.';
  for (const id of ['edit-selection', 'edit-tool', 'new-annotation', 'duplicate-annotation', 'delete-contour', 'delete-annotation',
    'finish-polygon', 'delete-polygon-point', 'split-polygon', 'brush-size', 'apply-edit',
    'edit-group', 'edit-label', 'add-class', 'renumber-posterior', 'edit-notes', 'edit-tooth']) {
    if (samLocked) byId(id).disabled = true;
  }
  byId('edit-selection').disabled = samLocked;
  byId('edit-tool').disabled = samLocked;
  byId('new-annotation').disabled = samLocked;
  byId('apply-edit').disabled = samLocked;
  byId('new-annotation').disabled ||= editorGeometry === 'masks';
  byId('suggest-sam').disabled = editorGeometry === 'boxes' || samLocked || !row || !!polygonDraft.length || !!pointerDrag;
  byId('accept-sam').hidden = !samSuggestion;
  byId('discard-sam').hidden = !samSuggestion;
}

function resetSam() {
  samRequest?.abort(); samRequest = null; samSuggestion = null; samTarget = null;
  byId('sam-status').textContent = 'Selecione ou desenhe uma caixa para guiar o SAM.';
}

for (const [id, output] of [['edit-contrast', 'contrast-value'], ['edit-brightness', 'brightness-value']]) {
  byId(id).addEventListener('input', () => {
    byId(output).value = `${byId(id).value}%`;
    redrawEditor();
  });
}
byId('edit-zoom').addEventListener('input', () => {
  byId('zoom-value').value = `${byId('edit-zoom').value}%`;
  setEditorView({preserveHint: true});
});
byId('reset-display').addEventListener('click', () => {
  for (const id of ['edit-contrast', 'edit-brightness', 'edit-zoom']) {
    byId(id).value = '100'; byId(id).dispatchEvent(new Event('input'));
  }
});
byId('brush-size').addEventListener('input', () => {
  byId('brush-size-value').value = `${byId('brush-size').value} px`;
  redrawEditor();
});

byId('suggest-sam').addEventListener('click', async () => {
  const row = selectedRow(), file = byId('file').files[0];
  if (!row || samRequest || samSuggestion || polygonDraft.length || pointerDrag) return;
  if (!file) { byId('sam-status').textContent = 'Selecione o arquivo original da radiografia.'; return; }
  const controller = new AbortController(); samRequest = controller;
  const generation = reviewGeneration;
  samTarget = row.id;
  const target = row.group === 'teeth' ? 'tooth' : 'generic';
  const body = new FormData(); body.append('file', file); body.append('box', JSON.stringify(row.bbox_xyxy));
  body.append('target', target);
  if (target === 'tooth' && /^[1-4][1-8]$/.test(String(row.label || ''))) body.append('fdi', row.label);
  byId('sam-status').textContent = target === 'tooth'
    ? `SAM segmentando o dente FDI ${row.label || 'indefinido'} com contexto dentário…`
    : 'SAM calculando o contorno… O primeiro uso carrega o modelo local.';
  redrawEditor();
  try {
    const response = await fetch('/segment/sam', {method: 'POST', body, headers: feedbackHeaders(),
      cache: 'no-store', signal: controller.signal});
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Não foi possível sugerir o contorno.');
    if (samRequest !== controller || generation !== reviewGeneration || !editorDialog.open) return;
    samSuggestion = result;
    byId('sam-status').textContent = result.model === 'trained_teeth_segmentation'
      ? `FDI ${row.label || 'indefinida'} localizada e processada pelo modelo de segmentação dentária treinado. Confira o contorno amarelo.`
      : 'Sugestão SAM em amarelo. Confira o contorno e aceite ou descarte.';
  } catch (error) {
    if (samRequest === controller && error.name !== 'AbortError') byId('sam-status').textContent = error.message;
  } finally {
    if (samRequest === controller) { samRequest = null; if (editorDialog.open) redrawEditor(); }
  }
});
byId('accept-sam').addEventListener('click', () => {
  const row = review.annotations.find(a => a.id === samTarget);
  if (!row || !samSuggestion) return;
  row.polygon_xy = structuredClone(samSuggestion.polygon_xy);
  if (editorGeometry !== 'masks') {
    row.bbox_xyxy = [...samSuggestion.bbox_xyxy];
    delete row.oriented_box_xy;
  }
  const keptFDI = row.group === 'teeth' ? row.label : null;
  markChanged(row); resetSam();
  byId('sam-status').textContent = keptFDI
    ? `Contorno aceito e FDI ${keptFDI} preservada. Arraste os vértices para ajustar e aplique as alterações.`
    : 'Contorno aceito. Arraste os vértices para ajustar e use Aplicar alterações para manter.';
  byId('edit-tool').value = editorTool = 'move'; refreshSelection(); redrawEditor();
});
byId('discard-sam').addEventListener('click', () => {
  resetSam(); redrawEditor();
});

function nearPoint(point, candidate, rect = editCanvas.getBoundingClientRect()) {
  return Math.hypot((point[0] - candidate[0]) * rect.width / (editorView[2] - editorView[0]),
    (point[1] - candidate[1]) * rect.height / (editorView[3] - editorView[1])) <= 10;
}

function nearestVertex(point, points, rect = editCanvas.getBoundingClientRect()) {
  let index = -1, distance = 10;
  points.forEach((candidate, i) => {
    const current = Math.hypot(
      (point[0] - candidate[0]) * rect.width / (editorView[2] - editorView[0]),
      (point[1] - candidate[1]) * rect.height / (editorView[3] - editorView[1]));
    if (current <= distance) { index = i; distance = current; }
  });
  return index;
}

function polygonBounds(points) {
  return [Math.min(...points.map(p => p[0])), Math.min(...points.map(p => p[1])),
    Math.max(...points.map(p => p[0])), Math.max(...points.map(p => p[1]))];
}

function convexHull(points) {
  const unique = [...new Map(points.map(([x, y]) => [`${x},${y}`, [x, y]])).values()]
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  if (unique.length <= 2) return unique;
  const cross = (origin, a, b) =>
    (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (b[0] - origin[0]);
  const half = sequence => {
    const result = [];
    for (const point of sequence) {
      while (result.length >= 2 && cross(result.at(-2), result.at(-1), point) <= 0) result.pop();
      result.push(point);
    }
    return result;
  };
  const lower = half(unique), upper = half([...unique].reverse());
  lower.pop(); upper.pop();
  return [...lower, ...upper];
}

function rebuildQuadrantsFromTeeth() {
  let updated = 0;
  for (const quadrant of ['1', '2', '3', '4']) {
    const members = review.annotations.filter(row =>
      row.group === 'teeth' && new RegExp(`^${quadrant}[1-8]$`).test(String(row.label || ''))
    );
    const candidates = review.annotations.filter(
      row => row.group === 'quadrants' && String(row.label) === quadrant
    );
    const points = members.flatMap(row => row.polygon_xy?.length >= 3 ? row.polygon_xy : boxCorners(row));
    if (points.length < 3) {
      const generatedIds = new Set(
        candidates.filter(row => row.source !== 'human').map(row => row.id)
      );
      if (generatedIds.size) {
        review.annotations = review.annotations.filter(row => !generatedIds.has(row.id));
        updated += generatedIds.size;
      }
      continue;
    }
    const hull = convexHull(points);
    if (hull.length < 3) continue;
    let row = candidates.find(candidate => candidate.source !== 'human');
    if (!row && candidates.length) continue;
    if (!row) {
      row = {
        id: newAnnotationId(), group: 'quadrants', label: quadrant, bbox_xyxy: polygonBounds(hull),
        polygon_xy: hull, notes: 'Gerado a partir dos dentes com numeração FDI revisada.',
        source: 'api_derived', tooth_id: null
      };
      review.annotations.push(row);
    } else {
      row.polygon_xy = hull;
      row.bbox_xyxy = polygonBounds(hull);
      row.notes = 'Atualizado a partir dos dentes com numeração FDI revisada.';
      row.source = 'api_derived';
      row.tooth_id = null;
      delete row.oriented_box_xy;
      delete row.model_score;
    }
    updated++;
  }
  if (updated) review.complete_groups = review.complete_groups.filter(group => group !== 'quadrants');
  return updated;
}

function fitMinimumAreaBox(row) {
  const points = row.polygon_xy;
  if (!points?.length || points.length < 3) return;
  const bounds = polygonBounds(points);
  const axisArea = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]);
  const hull = convexHull(points);
  let best = null;
  for (let index = 0; index < hull.length; index++) {
    const current = hull[index], next = hull[(index + 1) % hull.length];
    const length = Math.hypot(next[0] - current[0], next[1] - current[1]);
    if (length < 1e-6) continue;
    const ux = (next[0] - current[0]) / length, uy = (next[1] - current[1]) / length;
    const vx = -uy, vy = ux;
    let minU = Infinity, maxU = -Infinity, minV = Infinity, maxV = -Infinity;
    for (const [x, y] of hull) {
      const projectedU = x * ux + y * uy, projectedV = x * vx + y * vy;
      minU = Math.min(minU, projectedU); maxU = Math.max(maxU, projectedU);
      minV = Math.min(minV, projectedV); maxV = Math.max(maxV, projectedV);
    }
    const area = (maxU - minU) * (maxV - minV);
    if (!best || area < best.area) best = {area, ux, uy, vx, vy, minU, maxU, minV, maxV};
  }
  if (!best || !Number.isFinite(best.area) || best.area >= axisArea * .99) {
    delete row.oriented_box_xy;
    row.bbox_xyxy = bounds;
    return;
  }
  const projectBack = (u, v) => [u * best.ux + v * best.vx, u * best.uy + v * best.vy];
  row.oriented_box_xy = [
    projectBack(best.minU, best.minV), projectBack(best.maxU, best.minV),
    projectBack(best.maxU, best.maxV), projectBack(best.minU, best.maxV)
  ];
  updateBoxBounds(row);
}

function boxCorners(row) {
  if (row.oriented_box_xy?.length === 4) return row.oriented_box_xy;
  const [x1, y1, x2, y2] = row.bbox_xyxy;
  return [[x1, y1], [x2, y1], [x2, y2], [x1, y2]];
}

function boxAngle(row) {
  const corners = boxCorners(row);
  return Math.atan2(corners[1][1] - corners[0][1], corners[1][0] - corners[0][0]) * 180 / Math.PI;
}

function rotationHandle(row) {
  const corners = boxCorners(row);
  const center = corners.reduce(
    (sum, point) => [sum[0] + point[0] / 4, sum[1] + point[1] / 4], [0, 0]
  );
  const bottom = [(corners[2][0] + corners[3][0]) / 2, (corners[2][1] + corners[3][1]) / 2];
  const direction = [bottom[0] - center[0], bottom[1] - center[1]];
  const length = Math.hypot(...direction) || 1;
  const offset = 34 * (editorView[2] - editorView[0]) / editCanvas.width;
  return [bottom[0] + direction[0] / length * offset,
    bottom[1] + direction[1] / length * offset];
}

function updateBoxBounds(row) {
  const points = [...boxCorners(row), ...(row.polygon_xy || [])];
  row.bbox_xyxy = polygonBounds(points);
}

function rotateBox(row, targetAngle) {
  const corners = boxCorners(row).map(point => [...point]);
  const center = corners.reduce((sum, point) => [sum[0] + point[0] / 4, sum[1] + point[1] / 4], [0, 0]);
  const radians = (targetAngle - boxAngle(row)) * Math.PI / 180;
  const cosine = Math.cos(radians), sine = Math.sin(radians);
  const rotatePoint = ([x, y]) => [
    center[0] + (x - center[0]) * cosine - (y - center[1]) * sine,
    center[1] + (x - center[0]) * sine + (y - center[1]) * cosine
  ];
  const rotated = corners.map(rotatePoint);
  const rotatedPolygon = editorGeometry === 'boxes' ? null : row.polygon_xy?.map(rotatePoint) || null;
  const image = byId('original');
  if ([...rotated, ...(rotatedPolygon || [])].some(
    ([x, y]) => x < 0 || y < 0 || x > image.naturalWidth || y > image.naturalHeight
  )) {
    return false;
  }
  row.oriented_box_xy = rotated;
  if (rotatedPolygon) row.polygon_xy = rotatedPolygon;
  if (editorGeometry === 'boxes') row.bbox_xyxy = polygonBounds(rotated);
  else updateBoxBounds(row);
  markChanged(row);
  return true;
}

function resizeOrientedBox(row, point, corner, original) {
  const corners = boxCorners(original);
  const opposite = corners[(corner + 2) % 4];
  const edge = [corners[1][0] - corners[0][0], corners[1][1] - corners[0][1]];
  const edgeLength = Math.hypot(...edge) || 1;
  const horizontal = [edge[0] / edgeLength, edge[1] / edgeLength];
  const vertical = [-horizontal[1], horizontal[0]];
  const diagonal = [point[0] - opposite[0], point[1] - opposite[1]];
  const halfWidth = Math.max(0.5, Math.abs(diagonal[0] * horizontal[0] + diagonal[1] * horizontal[1]) / 2);
  const halfHeight = Math.max(0.5, Math.abs(diagonal[0] * vertical[0] + diagonal[1] * vertical[1]) / 2);
  const center = [(point[0] + opposite[0]) / 2, (point[1] + opposite[1]) / 2];
  row.oriented_box_xy = [
    [-halfWidth, -halfHeight], [halfWidth, -halfHeight],
    [halfWidth, halfHeight], [-halfWidth, halfHeight]
  ].map(([x, y]) => [
    center[0] + x * horizontal[0] + y * vertical[0],
    center[1] + x * horizontal[1] + y * vertical[1]
  ]);
  if (editorGeometry === 'boxes') row.bbox_xyxy = polygonBounds(row.oriented_box_xy);
  else updateBoxBounds(row);
}

function polygonArea(points) {
  return Math.abs(points.reduce((sum, point, i) => {
    const next = points[(i + 1) % points.length];
    return sum + point[0] * next[1] - next[0] * point[1];
  }, 0)) / 2;
}

function createBrushMask(row = null) {
  const image = byId('original');
  const scale = Math.min(1, 768 / Math.max(image.naturalWidth, image.naturalHeight));
  const canvas = document.createElement('canvas');
  canvas.width = Math.max(1, Math.ceil(image.naturalWidth * scale));
  canvas.height = Math.max(1, Math.ceil(image.naturalHeight * scale));
  const ctx = canvas.getContext('2d');
  if (row?.polygon_xy?.length >= 3) {
    ctx.beginPath();
    row.polygon_xy.forEach(([x, y], index) => index ? ctx.lineTo(x * scale, y * scale) : ctx.moveTo(x * scale, y * scale));
    ctx.closePath(); ctx.fillStyle = '#fff'; ctx.fill();
  }
  return {canvas, ctx, scale};
}

function paintBrush(mask, from, to, erase) {
  const ctx = mask.ctx, scale = mask.scale;
  ctx.save();
  ctx.globalCompositeOperation = erase ? 'destination-out' : 'source-over';
  ctx.strokeStyle = '#fff'; ctx.fillStyle = '#fff';
  ctx.lineWidth = Number(byId('brush-size').value) * scale;
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(from[0] * scale, from[1] * scale); ctx.lineTo(to[0] * scale, to[1] * scale); ctx.stroke();
  ctx.beginPath(); ctx.arc(to[0] * scale, to[1] * scale, ctx.lineWidth / 2, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}

function maskContour(mask) {
  const {canvas, ctx, scale} = mask;
  const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
  const filled = (x, y) => x >= 0 && y >= 0 && x < canvas.width && y < canvas.height &&
    pixels[(y * canvas.width + x) * 4 + 3] > 127;
  const edges = new Map();
  const add = (ax, ay, bx, by) => {
    const key = `${ax},${ay}`;
    if (!edges.has(key)) edges.set(key, []);
    edges.get(key).push([bx, by]);
  };
  for (let y = 0; y < canvas.height; y++) for (let x = 0; x < canvas.width; x++) {
    if (!filled(x, y)) continue;
    if (!filled(x, y - 1)) add(x, y, x + 1, y);
    if (!filled(x + 1, y)) add(x + 1, y, x + 1, y + 1);
    if (!filled(x, y + 1)) add(x + 1, y + 1, x, y + 1);
    if (!filled(x - 1, y)) add(x, y + 1, x, y);
  }
  const loops = [];
  while (edges.size) {
    const startKey = edges.keys().next().value;
    const start = startKey.split(',').map(Number), loop = [start];
    let key = startKey;
    for (let guard = 0; guard < 200000; guard++) {
      const options = edges.get(key);
      if (!options?.length) break;
      const next = options.pop(); if (!options.length) edges.delete(key);
      if (next[0] === start[0] && next[1] === start[1]) break;
      loop.push(next); key = `${next[0]},${next[1]}`;
    }
    if (loop.length >= 3) loops.push(loop);
  }
  if (!loops.length) return null;
  const loop = loops.reduce((best, current) => polygonArea(current) > polygonArea(best) ? current : best);
  let simplified = loop.filter((point, index) => {
    const previous = loop[(index - 1 + loop.length) % loop.length];
    const next = loop[(index + 1) % loop.length];
    return (point[0] - previous[0]) * (next[1] - point[1]) !==
      (point[1] - previous[1]) * (next[0] - point[0]);
  });
  const stride = Math.max(1, Math.ceil(simplified.length / 2048));
  simplified = simplified.filter((_, index) => index % stride === 0);
  const image = byId('original');
  return simplified.slice(0, 4096).map(([x, y]) => [
    Math.max(0, Math.min(image.naturalWidth, x / scale)),
    Math.max(0, Math.min(image.naturalHeight, y / scale))
  ]);
}

function resizeAnnotation(row, box, original) {
  row.bbox_xyxy = box;
  if (!original.polygon_xy?.length) return;
  const [x1, y1, x2, y2] = original.bbox_xyxy;
  // Mantém o contorno dentro da caixa e evita acumular erro a cada pointermove.
  row.polygon_xy = original.polygon_xy.map(([x, y]) => [
    Math.max(box[0], Math.min(box[2], box[0] + (x - x1) / (x2 - x1) * (box[2] - box[0]))),
    Math.max(box[1], Math.min(box[3], box[1] + (y - y1) / (y2 - y1) * (box[3] - box[1])))
  ]);
}

function prepareNewAnnotation() {
  const group = byId('edit-group').value, label = byId('edit-label').value;
  editorSelection = null; polygonTarget = null;
  refreshSelection();
  byId('edit-group').value = group; refreshLabels(); byId('edit-label').value = label;
}

function refreshLabels() {
  const group = byId('edit-group').value;
  let labels = group === 'additional' ? Object.keys(annotationClasses.additional) : annotationClasses[group];
  if (group === 'additional') {
    for (const row of review.annotations.filter(item => item.group === 'additional' && item.label)) {
      if (!annotationClasses.additional[row.label]) annotationClasses.additional[row.label] = row.label;
    }
    labels = Object.keys(annotationClasses.additional);
  }
  if (editorScope === 'anatomy') labels = labels.filter(label => anatomyLabels.has(label));
  byId('edit-label').replaceChildren();
  if (group === 'teeth') byId('edit-label').append(new Option('FDI indefinido', ''));
  for (const label of labels) byId('edit-label').append(new Option(group === 'additional' ? annotationClasses.additional[label] : label, label));
}

function refreshSelection() {
  const selection = byId('edit-selection'); selection.replaceChildren();
  const rows = scopeRows(), totals = new Map(), counts = new Map();
  for (const row of rows) totals.set(annotationName(row), (totals.get(annotationName(row)) || 0) + 1);
  for (const row of rows) {
    const name = annotationName(row), index = (counts.get(name) || 0) + 1;
    counts.set(name, index);
    selection.append(new Option(totals.get(name) > 1 ? `${name} (${index})` : name, row.id));
  }
  selection.value = editorSelection ?? '';
  const row = selectedRow();
  const defaultGroup = scopedEditorGroups.has(editorScope)
    ? editorScope : ['anatomy', 'additional'].includes(editorScope) ? 'additional' : 'teeth';
  byId('edit-group').value = row?.group || defaultGroup;
  byId('edit-group').disabled = ['anatomy', 'additional'].includes(editorScope) ||
    scopedEditorGroups.has(editorScope);
  refreshLabels();
  byId('edit-label').value = row?.label ?? byId('edit-label').value;
  byId('edit-notes').value = row?.notes || '';
  byId('edit-tooth').replaceChildren(new Option('Sem vínculo', ''));
  for (const tooth of review.annotations.filter(a => a.group === 'teeth')) {
    byId('edit-tooth').append(new Option(annotationName(tooth), tooth.id));
  }
  byId('edit-tooth').value = row?.tooth_id || '';
  byId('edit-tooth').disabled = !row || ['quadrants', 'teeth'].includes(row.group) || anatomyLabels.has(row.label);
}

function markChanged(row) {
  row.source = 'human';
  review.complete_groups = review.complete_groups.filter(group => group !== row.group);
}

byId('edit-quadrants').addEventListener('click', () => openEditor('quadrants'));
byId('edit-teeth').addEventListener('click', () => openEditor('teeth', null, 'boxes'));
byId('edit-tooth-masks').addEventListener('click', () => openEditor('teeth', null, 'masks'));
byId('edit-findings').addEventListener('click', () => openEditor('findings'));
byId('edit-additional').addEventListener('click', () => openEditor('additional'));
byId('edit-anatomy').addEventListener('click', () => openEditor('anatomy'));
byId('full-image').addEventListener('change', setEditorView);
byId('edit-selection').addEventListener('change', () => {
  const id = byId('edit-selection').value;
  if (!finishPolygon()) { byId('edit-selection').value = editorSelection ?? ''; return; }
  editorSelection = id; polygonTarget = null;
  byId('edit-tool').value = editorTool = 'move'; refreshSelection(); setEditorView({preserveHint: true});
});
byId('edit-group').addEventListener('change', () => {
  const row = selectedRow(); if (!row) { refreshLabels(); redrawEditor(); return; }
  markChanged(row); row.group = byId('edit-group').value; refreshLabels();
  row.label = byId('edit-label').value || null;
  if (row.group !== 'teeth') {
    for (const linked of review.annotations.filter(a => a.tooth_id === row.id)) {
      linked.tooth_id = null; markChanged(linked);
    }
    if (editorAnchorTooth === row.id) editorAnchorTooth = null;
  }
  row.tooth_id = ['quadrants', 'teeth'].includes(row.group) || anatomyLabels.has(row.label)
    ? null : editorAnchorTooth;
  markChanged(row); refreshSelection(); redrawEditor();
});
byId('edit-label').addEventListener('change', () => {
  const row = selectedRow(); if (!row) return;
  row.label = byId('edit-label').value || null;
  if (anatomyLabels.has(row.label)) row.tooth_id = null;
  markChanged(row);
  const renumbered = row.group === 'teeth' ? renumberPosteriorTeeth(row) : [];
  const rebuiltQuadrants = row.group === 'teeth' ? rebuildQuadrantsFromTeeth() : 0;
  refreshSelection(); redrawEditor();
  if (renumbered.length) {
    byId('editor-hint').textContent = `${renumbered.length} dente(s) posterior(es) renumerado(s) automaticamente, até ${renumbered.at(-1).label}. ${rebuiltQuadrants} quadrante(s) atualizado(s).`;
  } else if (rebuiltQuadrants) {
    byId('editor-hint').textContent = `${rebuiltQuadrants} quadrante(s) atualizado(s) a partir da numeração FDI.`;
  }
});

function renumberPosteriorTeeth(row) {
  const fdi = String(row?.label || '');
  if (row?.group !== 'teeth' || !/^[1-4][1-8]$/.test(fdi) || polygonDraft.length || pointerDrag) return [];
  const quadrant = fdi[0], start = Number(fdi[1]);
  const direction = ['1', '4'].includes(quadrant) ? -1 : 1;
  const centerX = candidate => (candidate.bbox_xyxy[0] + candidate.bbox_xyxy[2]) / 2;
  const centerY = candidate => (candidate.bbox_xyxy[1] + candidate.bbox_xyxy[3]) / 2;
  const height = candidate => candidate.bbox_xyxy[3] - candidate.bbox_xyxy[1];
  const upperArch = ['1', '2'].includes(quadrant);
  const anchor = centerX(row);
  const posterior = review.annotations.filter(candidate => {
    if (candidate.id === row.id || candidate.group !== 'teeth' || direction * (centerX(candidate) - anchor) <= 0.5) return false;
    const candidateFDI = String(candidate.label || '');
    if (/^[1-4][1-8]$/.test(candidateFDI)) {
      return ['1', '2'].includes(candidateFDI[0]) === upperArch;
    }
    return Math.abs(centerY(candidate) - centerY(row)) <= Math.max(height(candidate), height(row)) * 0.8;
  })
    .sort((a, b) => direction * (centerX(a) - centerX(b)));
  const available = posterior.slice(0, Math.max(0, 8 - start));
  available.forEach((candidate, index) => {
    const label = `${quadrant}${start + index + 1}`;
    if (candidate.label !== label) {
      candidate.label = label;
      markChanged(candidate);
    }
  });
  return available;
}

byId('renumber-posterior').addEventListener('click', () => {
  const row = selectedRow();
  const fdi = String(row?.label || '');
  const available = renumberPosteriorTeeth(row);
  const rebuiltQuadrants = rebuildQuadrantsFromTeeth();
  refreshSelection(); redrawEditor();
  const last = available.length ? available.at(-1).label : fdi;
  byId('editor-hint').textContent = available.length
    ? `${available.length} dente(s) posterior(es) renumerado(s), até ${last}. ${rebuiltQuadrants} quadrante(s) atualizado(s).`
    : `Não há dentes posteriores deste quadrante para renumerar. ${rebuiltQuadrants} quadrante(s) atualizado(s).`;
});
byId('add-class').addEventListener('click', () => {
  const group = byId('edit-group').value;
  if (!['findings', 'additional'].includes(group) || polygonDraft.length || samRequest || samSuggestion) return;
  const name = window.prompt('Nome da nova classe para o banco revisado:')?.trim();
  if (!name) return;
  if (name.length > 100 || /[\u0000-\u001f\u007f]/.test(name)) {
    byId('editor-hint').textContent = 'Use um nome de classe com até 100 caracteres, sem caracteres de controle.';
    return;
  }
  if (group === 'additional') annotationClasses.additional[name] = name;
  else if (!annotationClasses.findings.includes(name)) annotationClasses.findings.push(name);
  refreshLabels();
  byId('edit-label').value = name;
  editorSelection = null; polygonTarget = null;
  refreshSelection();
  byId('edit-group').value = group; refreshLabels(); byId('edit-label').value = name;
  byId('edit-tool').value = editorTool = 'box';
  redrawEditor();
  byId('editor-hint').textContent = `Classe “${name}” criada. Desenhe a caixa da nova marcação na radiografia.`;
});
byId('edit-tooth').addEventListener('change', () => {
  const row = selectedRow(); if (!row) return;
  row.tooth_id = byId('edit-tooth').value || null; markChanged(row); redrawEditor();
});
byId('edit-notes').addEventListener('input', () => {
  const row = selectedRow(); if (!row) return; row.notes = byId('edit-notes').value; markChanged(row);
});
function newAnnotationId() {
  // randomUUID exige contexto seguro; getRandomValues também funciona em HTTP na rede local.
  return typeof crypto.randomUUID === 'function' ? crypto.randomUUID()
    : Array.from(crypto.getRandomValues(new Uint8Array(16)), byte => byte.toString(16).padStart(2, '0')).join('');
}

function createAnnotation(box, polygon = null) {
  const group = editorAnchorTooth ? 'additional' : byId('edit-group').value;
  const label = group === byId('edit-group').value ? byId('edit-label').value || null : Object.keys(annotationClasses.additional)[0];
  const row = {id: newAnnotationId(), group, label, bbox_xyxy: box,
    polygon_xy: polygon, notes: '', source: 'human', tooth_id: anatomyLabels.has(label) ? null : editorAnchorTooth};
  review.annotations.push(row); editorSelection = row.id; markChanged(row);
  return row;
}

byId('new-annotation').addEventListener('click', () => {
  if (pointerDrag || !finishPolygon()) return;
  prepareNewAnnotation();
  const newCanalWithBrush = editorScope === 'anatomy' &&
    byId('edit-label').value === 'mandibular_canal' && editorTool === 'brush-add';
  if (editorTool !== 'box' && editorTool !== 'polygon' && !newCanalWithBrush) editorTool = 'polygon';
  byId('edit-tool').value = editorTool; redrawEditor();
});
byId('duplicate-annotation').addEventListener('click', () => {
  if (pointerDrag || !finishPolygon()) return;
  const source = selectedRow();
  if (!source || source.group !== 'teeth') return;
  const image = byId('original'), offset = 12;
  const dx = image.naturalWidth - source.bbox_xyxy[2] >= offset
    ? offset : Math.max(-offset, -source.bbox_xyxy[0]);
  const dy = image.naturalHeight - source.bbox_xyxy[3] >= offset
    ? offset : Math.max(-offset, -source.bbox_xyxy[1]);
  const copy = structuredClone(source);
  copy.id = newAnnotationId();
  copy.label = null;
  copy.notes = '';
  copy.source = 'human';
  copy.tooth_id = null;
  delete copy.model_score;
  copy.bbox_xyxy = [source.bbox_xyxy[0] + dx, source.bbox_xyxy[1] + dy,
    source.bbox_xyxy[2] + dx, source.bbox_xyxy[3] + dy];
  if (source.polygon_xy) {
    if (editorGeometry === 'boxes') copy.polygon_xy = null;
    else copy.polygon_xy = source.polygon_xy.map(([x, y]) => [x + dx, y + dy]);
  }
  review.annotations.push(copy);
  editorSelection = copy.id;
  polygonDraft = []; polygonTarget = null;
  byId('edit-tool').value = editorTool = 'move';
  markChanged(copy); refreshSelection(); redrawEditor();
  byId('edit-label').focus();
  byId('editor-hint').textContent = 'Cópia criada. Escolha a nova numeração FDI e arraste a caixa para posicioná-la.';
});
byId('split-polygon').addEventListener('click', () => {
  if (pointerDrag || !selectedRow()?.polygon_xy?.length || !finishPolygon()) return;
  byId('edit-tool').value = editorTool = 'split'; redrawEditor();
});
byId('delete-contour').addEventListener('click', () => {
  if (pointerDrag || polygonDraft.length || samRequest || samSuggestion) return;
  const row = selectedRow();
  if (!row?.polygon_xy?.length) return;
  markChanged(row);
  row.polygon_xy = null;
  polygonTarget = null;
  brushMask = null;
  brushCursor = null;
  byId('edit-tool').value = editorTool = 'move';
  refreshSelection();
  redrawEditor();
  byId('editor-hint').textContent = 'Contorno removido. A caixa e os dados da marcação foram mantidos.';
});
byId('delete-annotation').addEventListener('click', () => {
  const row = selectedRow(); if (!row) return; markChanged(row);
  review.annotations = review.annotations.filter(a => a.id !== editorSelection);
  for (const linked of review.annotations.filter(a => a.tooth_id === editorSelection)) {
    linked.tooth_id = null; markChanged(linked);
  }
  if (editorAnchorTooth === editorSelection) editorAnchorTooth = null;
  editorSelection = scopeRows()[0]?.id || null; polygonDraft = []; polygonTarget = null;
  byId('edit-tool').value = editorTool = 'move'; refreshSelection(); redrawEditor();
});
byId('edit-tool').addEventListener('change', () => {
  const tool = byId('edit-tool').value;
  if (pointerDrag || !finishPolygon()) { byId('edit-tool').value = editorTool; return; }
  if (tool === 'move' && !selectedRow()) {
    editorSelection = scopeRows().at(-1)?.id || null;
    refreshSelection();
  }
  if (tool === 'split' && !selectedRow()?.polygon_xy?.length) {
    byId('edit-tool').value = editorTool; redrawEditor(); return;
  }
  if ((tool === 'polygon' && selectedRow()?.polygon_xy?.length) ||
      (['anatomy', 'additional'].includes(editorScope) &&
       (tool === 'box' || tool === 'polygon'))) prepareNewAnnotation();
  brushCursor = null; brushMask = null;
  byId('edit-tool').value = editorTool = tool; redrawEditor();
});
function finishPolygon() {
  if (!polygonDraft.length) return true;
  if (polygonDraft.length < 3) {
    byId('editor-hint').textContent = 'Desenhe pelo menos três pontos para fechar o contorno.'; return false;
  }
  const box = polygonBounds(polygonDraft);
  const area = polygonArea(polygonDraft);
  if (box[2] - box[0] < 1 || box[3] - box[1] < 1 || area < 1) {
    byId('editor-hint').textContent = 'O contorno precisa delimitar uma área. Adicione pontos fora da mesma linha.'; return false;
  }
  let row = polygonTarget ? review.annotations.find(a => a.id === polygonTarget) : selectedRow();
  if (!row || (!polygonTarget && row.polygon_xy?.length)) row = createAnnotation(box, polygonDraft);
  row.polygon_xy = polygonDraft;
  if (editorGeometry !== 'masks') row.bbox_xyxy = box;
  if (row.label === 'mandibular_canal') fitMinimumAreaBox(row);
  editorSelection = row.id; polygonDraft = []; polygonTarget = null;
  markChanged(row); byId('edit-tool').value = editorTool = 'move'; refreshSelection(); redrawEditor();
  return true;
}
byId('finish-polygon').addEventListener('click', finishPolygon);

function deletePolygonPoint(index = polygonDraft.length - 1) {
  if (pointerDrag || index < 0 || index >= polygonDraft.length) return;
  // Uma marcação reaberta deve manter ao menos três vértices.
  if (polygonTarget && polygonDraft.length <= 3) {
    byId('editor-hint').textContent = 'O contorno precisa manter pelo menos três pontos. Para apagá-lo, use Excluir contorno.';
    return;
  }
  polygonDraft.splice(index, 1);
  redrawEditor();
}
byId('delete-polygon-point').addEventListener('click', () => deletePolygonPoint());
editorDialog.addEventListener('keydown', event => {
  if (!editorDialog.open || byId('edit-tool').value !== 'polygon' || !polygonDraft.length ||
      !['Delete', 'Backspace'].includes(event.key) || event.ctrlKey || event.metaKey || event.altKey ||
      event.target.closest('input, textarea, select, [contenteditable]')) return;
  event.preventDefault(); deletePolygonPoint();
});
editCanvas.addEventListener('contextmenu', event => {
  if (byId('edit-tool').value !== 'polygon') return;
  event.preventDefault();
  const point = toImage(event), rect = editCanvas.getBoundingClientRect();
  deletePolygonPoint(nearestVertex(point, polygonDraft, rect));
});

editCanvas.addEventListener('pointerdown', event => {
  if (samRequest || samSuggestion) return;
  if (!event.isPrimary || event.button !== 0 || pointerDrag) return;
  event.preventDefault();
  editCanvas.focus({preventScroll: true});
  let row = selectedRow();
  const point = toImage(event), tool = byId('edit-tool').value;
  const rect = editCanvas.getBoundingClientRect();
  const near = p => nearPoint(point, p, rect);
  if (tool === 'move' && !row) {
    row = [...visibleEditorRows()].reverse().find(candidate => point[0] >= candidate.bbox_xyxy[0] &&
      point[0] <= candidate.bbox_xyxy[2] && point[1] >= candidate.bbox_xyxy[1] &&
      point[1] <= candidate.bbox_xyxy[3]);
    if (!row) return;
    editorSelection = row.id; refreshSelection(); redrawEditor();
  }
  if (tool === 'split') {
    const vertex = nearestVertex(point, row?.polygon_xy || [], rect);
    if (vertex < 0) { byId('editor-hint').textContent = 'Clique em um vértice para separar o contorno.'; return; }
    polygonTarget = row.id;
    // Abre a aresta após o ponto escolhido, preservando todos os vértices.
    polygonDraft = structuredClone([...row.polygon_xy.slice(vertex + 1), ...row.polygon_xy.slice(0, vertex + 1)]);
    byId('edit-tool').value = editorTool = 'polygon'; redrawEditor(); return;
  }
  if (tool === 'polygon') {
    const vertex = nearestVertex(point, polygonDraft, rect);
    if (vertex >= 0) {
      pointerDrag = {mode: 'draft-vertex', vertex, start: point, moved: false,
        originalPoint: [...polygonDraft[vertex]], pointerId: event.pointerId};
      editCanvas.setPointerCapture(event.pointerId); redrawEditor(); return;
    }
    if (polygonDraft.length >= 4096) { byId('editor-hint').textContent = 'Limite de 4096 pontos atingido. Conclua o contorno.'; return; }
    polygonDraft.push(point); redrawEditor(); return;
  }
  if (tool === 'box') {
    pointerDrag = {mode: 'box', start: point, box: [...point, ...point],
      original: row ? structuredClone(row) : null, pointerId: event.pointerId};
    editCanvas.setPointerCapture(event.pointerId); redrawEditor(); return;
  }
  if (tool === 'brush-add' || tool === 'brush-erase') {
    const canCreateCanal = tool === 'brush-add' && editorScope === 'anatomy' &&
      byId('edit-label').value === 'mandibular_canal';
    if (!row && !canCreateCanal) {
      byId('editor-hint').textContent = 'Selecione uma marcação antes de usar o pincel.'; return;
    }
    brushMask = createBrushMask(row);
    paintBrush(brushMask, point, point, tool === 'brush-erase');
    brushCursor = point;
    pointerDrag = {mode: 'brush', start: point, last: point, original: structuredClone(row),
      createNew: !row, erase: tool === 'brush-erase', pointerId: event.pointerId};
    editCanvas.setPointerCapture(event.pointerId); redrawEditor(); return;
  }
  if (!row) return;
  const [x1, y1, x2, y2] = row.bbox_xyxy;
  const corners = boxCorners(row);
  const rotate = editorGeometry !== 'masks' && tool === 'move' && near(rotationHandle(row));
  const corner = editorGeometry !== 'masks' ? corners.findIndex(near) : -1;
  const vertex = editorGeometry !== 'boxes' ? nearestVertex(point, row.polygon_xy || [], rect) : -1;
  const mode = rotate ? 'rotate' : corner >= 0 ? 'corner' : vertex >= 0 ? 'vertex' : 'move';
  if (editorGeometry === 'masks' && mode === 'move') {
    const hit = [...visibleEditorRows()].reverse().find(a => point[0] >= a.bbox_xyxy[0] &&
      point[0] <= a.bbox_xyxy[2] && point[1] >= a.bbox_xyxy[1] && point[1] <= a.bbox_xyxy[3]);
    if (hit && hit.id !== editorSelection) { editorSelection = hit.id; refreshSelection(); redrawEditor(); }
    return;
  }
  if (mode === 'move' && !(point[0] >= x1 && point[0] <= x2 && point[1] >= y1 && point[1] <= y2)) {
    const hit = [...visibleEditorRows()].reverse().find(a => point[0] >= a.bbox_xyxy[0] && point[0] <= a.bbox_xyxy[2] && point[1] >= a.bbox_xyxy[1] && point[1] <= a.bbox_xyxy[3]);
    if (hit) { editorSelection = hit.id; refreshSelection(); redrawEditor(); } return;
  }
  pointerDrag = {mode, corner, vertex, start: point, original: structuredClone(row), pointerId: event.pointerId};
  editCanvas.setPointerCapture(event.pointerId);
});
function updateDrag(event) {
  if (!pointerDrag) {
    if (['brush-add', 'brush-erase'].includes(byId('edit-tool').value)) {
      brushCursor = toImage(event); redrawEditor();
    }
    return;
  }
  if (pointerDrag.pointerId !== event.pointerId) return;
  const row = selectedRow(), point = toImage(event), drag = pointerDrag;
  if (drag.mode === 'brush') {
    paintBrush(brushMask, drag.last, point, drag.erase);
    drag.last = point; brushCursor = point; redrawEditor(); return;
  }
  if (drag.mode === 'draft-vertex') {
    if (!drag.moved && nearPoint(point, drag.start)) return;
    drag.moved = true; polygonDraft[drag.vertex] = point; redrawEditor(); return;
  }
  if (drag.mode === 'box') {
    drag.box = [Math.min(drag.start[0], point[0]), Math.min(drag.start[1], point[1]), Math.max(drag.start[0], point[0]), Math.max(drag.start[1], point[1])];
    redrawEditor(); return;
  }
  if (drag.mode === 'rotate') {
    const corners = boxCorners(drag.original);
    const center = corners.reduce(
      (sum, candidate) => [sum[0] + candidate[0] / 4, sum[1] + candidate[1] / 4], [0, 0]
    );
    const target = Math.atan2(point[1] - center[1], point[0] - center[0]) * 180 / Math.PI - 90;
    if (!rotateBox(row, target)) {
      byId('editor-hint').textContent = 'A caixa girada precisa permanecer dentro da radiografia.';
    }
    redrawEditor(); return;
  }
  const [x1, y1, x2, y2] = drag.original.bbox_xyxy;
  if (drag.mode === 'vertex') {
    row.polygon_xy = structuredClone(drag.original.polygon_xy);
    row.polygon_xy[drag.vertex] = point;
    if (editorGeometry !== 'masks') row.bbox_xyxy = polygonBounds(row.polygon_xy);
  } else if (drag.mode === 'move') {
    const dx = Math.max(-x1, Math.min(byId('original').naturalWidth - x2, point[0] - drag.start[0]));
    const dy = Math.max(-y1, Math.min(byId('original').naturalHeight - y2, point[1] - drag.start[1]));
    row.bbox_xyxy = [x1 + dx, y1 + dy, x2 + dx, y2 + dy];
    if (editorGeometry !== 'boxes' && drag.original.polygon_xy) row.polygon_xy = drag.original.polygon_xy.map(([x, y]) => [
      Math.max(row.bbox_xyxy[0], Math.min(row.bbox_xyxy[2], x + dx)),
      Math.max(row.bbox_xyxy[1], Math.min(row.bbox_xyxy[3], y + dy))
    ]);
    if (drag.original.oriented_box_xy) {
      row.oriented_box_xy = drag.original.oriented_box_xy.map(([x, y]) => [x + dx, y + dy]);
    }
  } else {
    if (drag.original.oriented_box_xy) {
      resizeOrientedBox(row, point, drag.corner, drag.original);
    } else {
      const opposite = [[x2, y2], [x1, y2], [x1, y1], [x2, y1]][drag.corner];
      resizeAnnotation(row, [Math.min(point[0], opposite[0]), Math.min(point[1], opposite[1]),
        Math.max(point[0], opposite[0]), Math.max(point[1], opposite[1])], drag.original);
    }
    if (editorGeometry === 'boxes') row.polygon_xy = structuredClone(drag.original.polygon_xy || null);
  }
  redrawEditor();
}
editCanvas.addEventListener('pointermove', updateDrag);
function endDrag(event) {
  if (!pointerDrag || pointerDrag.pointerId !== event.pointerId) return;
  const cancelled = event.type !== 'pointerup';
  if (!cancelled) updateDrag(event);
  const drag = pointerDrag;
  if (drag.mode === 'brush') {
    if (cancelled) {
      if (drag.original) Object.assign(selectedRow(), drag.original);
    } else {
      const polygon = maskContour(brushMask);
      if (polygon?.length >= 3 && polygonArea(polygon) >= 1) {
        const row = drag.createNew ? createAnnotation(polygonBounds(polygon), polygon) : selectedRow();
        row.polygon_xy = polygon;
        if (editorGeometry !== 'masks') {
          if (row.label === 'mandibular_canal') fitMinimumAreaBox(row);
          else if (row.oriented_box_xy) updateBoxBounds(row);
          else row.bbox_xyxy = polygonBounds(polygon);
        }
        markChanged(row);
      } else {
        if (drag.original) Object.assign(selectedRow(), drag.original);
        byId('editor-hint').textContent = 'O pincel precisa manter uma área contínua. O último traço foi desfeito.';
      }
    }
    pointerDrag = null; brushMask = null;
    if (editCanvas.hasPointerCapture(event.pointerId)) editCanvas.releasePointerCapture(event.pointerId);
    refreshSelection(); redrawEditor(); return;
  }
  if (drag.mode === 'draft-vertex') {
    if (cancelled) polygonDraft[drag.vertex] = drag.originalPoint;
    pointerDrag = null;
    if (editCanvas.hasPointerCapture(event.pointerId)) editCanvas.releasePointerCapture(event.pointerId);
    redrawEditor();
    if (!cancelled && !drag.moved && polygonDraft.length >= 3) finishPolygon();
    return;
  }
  let row = selectedRow();
  const box = drag.mode === 'box' ? drag.box : row.bbox_xyxy;
  const valid = box[2] - box[0] >= 1 && box[3] - box[1] >= 1 &&
    (drag.mode === 'box' || !row.polygon_xy || polygonArea(row.polygon_xy) >= 1);
  if (cancelled || !valid) {
    if (drag.original) Object.assign(row, drag.original);
  } else if (drag.mode === 'box') {
    const createNew = ['anatomy', 'additional'].includes(editorScope);
    row = createNew ? createAnnotation(box) : row || createAnnotation(box);
    delete row.oriented_box_xy;
    resizeAnnotation(row, box, createNew ? row : drag.original || row);
    if (editorGeometry === 'boxes' && drag.original) {
      row.polygon_xy = structuredClone(drag.original.polygon_xy || null);
    }
    if (row.polygon_xy && polygonArea(row.polygon_xy) < 1) Object.assign(row, drag.original);
    else markChanged(row);
  } else if (JSON.stringify(row) !== JSON.stringify(drag.original)) {
    markChanged(row);
  }
  pointerDrag = null;
  if (editCanvas.hasPointerCapture(event.pointerId)) editCanvas.releasePointerCapture(event.pointerId);
  if (row) refreshSelection();
  redrawEditor();
}
editCanvas.addEventListener('pointerup', endDrag);
editCanvas.addEventListener('pointercancel', endDrag);
editCanvas.addEventListener('lostpointercapture', endDrag);
editCanvas.addEventListener('pointerleave', () => {
  if (!pointerDrag && brushCursor) { brushCursor = null; redrawEditor(); }
});

function cancelEditor() {
  resetSam();
  const pointerId = pointerDrag?.pointerId;
  pointerDrag = null; polygonDraft = []; polygonTarget = null;
  if (pointerId !== undefined && editCanvas.hasPointerCapture(pointerId)) editCanvas.releasePointerCapture(pointerId);
  review = editorSnapshot; editorDialog.close();
}
byId('cancel-edit').addEventListener('click', cancelEditor);
editorDialog.addEventListener('cancel', event => { event.preventDefault(); cancelEditor(); });
byId('apply-edit').addEventListener('click', async () => {
  if (samRequest || samSuggestion) return;
  if (pointerDrag) { byId('editor-hint').textContent = 'Termine de arrastar antes de aplicar.'; return; }
  if (!finishPolygon()) return;
  if (editorScope === 'teeth') rebuildQuadrantsFromTeeth();
  reviewDirty = JSON.stringify(review) !== JSON.stringify(editorSnapshot) || reviewDirty;
  editorDialog.close();
  showCompleteGroups();
  renderEditableCards(); await renderReviewedImages();
  reviewStatus('Alterações aplicadas. Salve as revisões no backend.');
});

function installReviewHover(image, rows) {
  image.reviewHoverRows = rows;
  if (image.dataset.reviewHover === 'ready') return;
  image.dataset.reviewHover = 'ready';
  const tooltip = byId('review-annotation-tooltip');
  const groupNames = {quadrants: 'Quadrante', teeth: 'Dente / FDI', findings: 'Achado DENTEX', additional: 'Dental31 / anatomia'};
  image.addEventListener('pointermove', event => {
    const rect = image.getBoundingClientRect();
    if (!rect.width || !rect.height || !image.naturalWidth || !image.naturalHeight) return;
    const x = (event.clientX - rect.left) * image.naturalWidth / rect.width;
    const y = (event.clientY - rect.top) * image.naturalHeight / rect.height;
    const hit = (image.reviewHoverRows || []).filter(row => {
      const [left, top, right, bottom] = row.bbox_xyxy;
      return x >= left && x <= right && y >= top && y <= bottom;
    }).sort((a, b) => {
      const area = row => (row.bbox_xyxy[2] - row.bbox_xyxy[0]) * (row.bbox_xyxy[3] - row.bbox_xyxy[1]);
      return area(a) - area(b);
    })[0];
    if (!hit) { tooltip.classList.remove('visible'); return; }
    const color = annotationColor(hit);
    tooltip.textContent = `${annotationName(hit)} · ${groupNames[hit.group] || hit.group}`;
    tooltip.style.setProperty('--tooltip-color', color);
    tooltip.classList.add('visible');
    const margin = 12;
    tooltip.style.left = `${Math.max(margin, Math.min(event.clientX + 15, innerWidth - tooltip.offsetWidth - margin))}px`;
    tooltip.style.top = `${Math.max(margin, Math.min(event.clientY + 15, innerHeight - tooltip.offsetHeight - margin))}px`;
  });
  image.addEventListener('pointerleave', () => tooltip.classList.remove('visible'));
}

async function renderReviewedImages() {
  const generation = reviewGeneration;
  const views = [
    {id: 'annotated', downloadId: 'download',
      include: row => ['quadrants', 'teeth'].includes(row.group), mode: 'fdi'},
    {id: 'tooth-segmentation', downloadId: 'download-tooth-segmentation',
      include: row => row.group === 'teeth', mode: 'segmentation'},
    {id: 'additional-annotations', downloadId: 'download-additional',
      include: row => row.group === 'additional', mode: 'boxes'},
    {id: 'anatomy', downloadId: 'download-anatomy',
      include: row => anatomyLabels.has(row.label), mode: 'boxes'}
  ];
  for (const {id, downloadId, include, mode} of views) {
    const canvas = document.createElement('canvas');
    canvas.width = byId('original').naturalWidth; canvas.height = byId('original').naturalHeight;
    const ctx = canvas.getContext('2d'); ctx.drawImage(byId('original'), 0, 0);
    const rows = review.annotations.filter(include);
    for (const row of rows) {
      const hasContour = row.polygon_xy?.length >= 3;
      const segmentation = mode === 'segmentation';
      drawAnnotation(ctx, row, undefined, {
        showBox: mode === 'boxes' || mode === 'fdi',
        showPolygon: segmentation && hasContour,
        showLabel: (mode === 'fdi' || segmentation) && row.group === 'teeth',
        fillOpacity: segmentation && hasContour ? 0.14 : 0,
        lineWidth: Math.max(2, Math.round(Math.min(canvas.width, canvas.height) / 350)),
        labelFontSize: (mode === 'fdi' || segmentation)
          ? Math.max(16, Math.round(Math.min(canvas.width, canvas.height) / 42)) : 12});
    }
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
    if (generation !== reviewGeneration) return;
    const url = URL.createObjectURL(blob);
    if (id === 'annotated') { if (annotatedUrl) URL.revokeObjectURL(annotatedUrl); annotatedUrl = url; }
    else if (id === 'tooth-segmentation') {
      if (toothSegmentationUrl) URL.revokeObjectURL(toothSegmentationUrl);
      toothSegmentationUrl = url;
    }
    else if (id === 'additional-annotations') {
      if (additionalAnnotationsUrl) URL.revokeObjectURL(additionalAnnotationsUrl);
      additionalAnnotationsUrl = url;
    } else { if (anatomyUrl) URL.revokeObjectURL(anatomyUrl); anatomyUrl = url; }
    byId(id).src = url; byId(id).hidden = false;
    installReviewHover(byId(id), rows);
    byId(`${id}-empty`).hidden = true;
    byId(downloadId).href = url; byId(downloadId).hidden = false;
    await byId(id).decode();
  }
  byId('anatomy-status').textContent = 'Marcações revisadas manualmente. As correções são salvas pelo botão Salvar revisões no backend.';
  const notes = review.annotations.filter(a => anatomyLabels.has(a.label) && a.notes);
  byId('anatomy-notes').replaceChildren(...notes.map(a => textElement('li', '', `${annotationName(a)}: ${a.notes}`)));
  byId('anatomy-notes').hidden = !notes.length;
  // Reconstrói também a prancha para downloads e impressão usarem as correções.
  const cards = [...byId('editable-cards').children];
  const width = 1260, cardWidth = 600, margin = 20;
  const heights = cards.map(card => 285 + card.querySelectorAll('p').length * 24);
  const rowHeights = [];
  for (let i = 0; i < heights.length; i += 2) rowHeights.push(Math.max(...heights.slice(i, i + 2)));
  const sheet = document.createElement('canvas'); sheet.width = width;
  sheet.height = Math.max(180, 40 + rowHeights.reduce((sum, h) => sum + h + margin, 0));
  const ctx = sheet.getContext('2d'); ctx.fillStyle = '#0b1220'; ctx.fillRect(0, 0, sheet.width, sheet.height);
  const layout = {width: sheet.width, height: sheet.height, cards: []};
  let y = 20;
  cards.forEach((card, i) => {
    const x = margin + i % 2 * (cardWidth + margin), height = rowHeights[Math.floor(i / 2)];
    ctx.fillStyle = '#111c2f'; ctx.fillRect(x, y, cardWidth, height);
    ctx.fillStyle = '#2dd4bf'; ctx.font = '20px system-ui'; ctx.fillText(card.querySelector('h2').textContent, x + 16, y + 30);
    ctx.drawImage(card.querySelector('canvas'), x + 16, y + 45, 560, 220);
    ctx.font = '15px system-ui'; ctx.fillStyle = '#cbd5e1';
    card.querySelectorAll('p').forEach((p, index) => ctx.fillText(p.textContent, x + 16, y + 285 + index * 24, 568));
    layout.cards.push({title: card.querySelector('h2').textContent, x, y, width: cardWidth, height});
    if (i % 2 === 1) y += height + margin;
  });
  const blob = await new Promise(resolve => sheet.toBlob(resolve, 'image/png'));
  if (generation !== reviewGeneration) return;
  if (teethUrl) URL.revokeObjectURL(teethUrl);
  teethUrl = URL.createObjectURL(blob); byId('teeth').src = teethUrl;
  byId('download-teeth').href = teethUrl; teethLayout = layout;
  await byId('teeth').decode();
  if (reportInfo) reportInfo.summary = 'Marcações revisadas manualmente. Consulte as observações por dente.';
}

for (const id of ['patient-group', ...completeGroups.map(group => `complete-${group}`)]) {
  byId(id).addEventListener('change', () => {
    if (!review) return;
    review.complete_groups = completeGroups.filter(group => byId(`complete-${group}`).checked);
    review.patient_group = byId('patient-group').value;
    syncCompleteAll();
    reviewDirty = true; reviewStatus('Alterações pendentes. Salve no backend.');
  });
}
byId('complete-all').addEventListener('change', () => {
  if (!review) return;
  for (const group of completeGroups) byId(`complete-${group}`).checked = byId('complete-all').checked;
  review.complete_groups = byId('complete-all').checked ? [...completeGroups] : [];
  review.patient_group = byId('patient-group').value;
  syncCompleteAll();
  reviewDirty = true; reviewStatus('Alterações pendentes. Salve no backend.');
});
window.addEventListener('beforeunload', event => {
  if (adminReviewMode && adminEditLock && reviewImageId) {
    fetch(`/admin/api/images/${encodeURIComponent(reviewImageId)}/edit-lock`, {
      method: 'DELETE', keepalive: true, headers: {'X-Panoramica-CSRF': adminCsrf}
    });
  }
  if (reviewDirty) { event.preventDefault(); event.returnValue = ''; }
});
byId('save-feedback').addEventListener('click', async () => {
  if (!review || reviewSaving) return;
  review.patient_group = byId('patient-group').value;
  review.complete_groups = completeGroups.filter(group => byId(`complete-${group}`).checked);
  if (showToothValidationIssues()) return;
  const generation = reviewGeneration;
  reviewSaving = true; byId('save-feedback').disabled = true;
  const feedbackControls = [...byId('feedback-panel').querySelectorAll('input, select, button')];
  feedbackControls.forEach(control => control.disabled = true);
  byId('file').disabled = true; byId('submit').disabled = true;
  try {
    let response;
    if (adminReviewMode) {
      response = await fetch(`/admin/api/images/${encodeURIComponent(reviewImageId)}`, {
        method: 'PUT', cache: 'no-store',
        headers: {'Content-Type': 'application/json', 'X-Panoramica-CSRF': adminCsrf},
        body: JSON.stringify({
          document: review, revision: reviewRevision,
          age_group: byId('review-age-group').value
        })
      });
    } else {
      const body = new FormData(); body.append('file', byId('file').files[0]);
      body.append('document', JSON.stringify(review));
      body.append('baseline', JSON.stringify(reviewBaseline));
      body.append('revision', String(reviewRevision));
      response = await fetch('/feedback', {
        method: 'POST', body, headers: feedbackHeaders(), cache: 'no-store'
      });
    }
    const saved = await response.json();
    if (!response.ok) throw new Error(typeof saved.detail === 'string' ? saved.detail : 'Revisão inválida. Confira FDI, caixas e contornos.');
    if (generation !== reviewGeneration) return;
    reviewRevision = saved.revision; reviewDirty = false;
    reviewReviewer = saved.reviewer || reviewReviewer;
    if (adminReviewMode) {
      adminEditLock = false; clearInterval(editLockTimer); editLockTimer = null;
      try {
        sessionStorage.setItem(
          'panoramica-review-notice',
          `Revisão ${saved.revision} salva${saved.reviewer ? ` por ${saved.reviewer}` : ''} com sucesso.`
        );
      } catch (_) { /* O redirecionamento funciona mesmo sem armazenamento da sessão. */ }
      location.replace('/review');
      return;
    }
    reviewSources.saved = {document: structuredClone(review), baseline: reviewBaseline, dirty: false};
    byId('review-source-control').hidden = false;
    updateAnnotationSource();
    reviewStatus(`Revisão ${saved.revision} salva${saved.reviewer ? ` por ${saved.reviewer}` : ''}. Disponível para juntar ao dataset de treinamento.`);
  } catch (error) { reviewStatus(error.message, true); }
  finally {
    reviewSaving = false; byId('save-feedback').disabled = false;
    feedbackControls.forEach(control => control.disabled = false);
    byId('file').disabled = false; byId('submit').disabled = false;
  }
});
byId('export-feedback').addEventListener('click', async () => {
  if (reviewDirty) { reviewStatus('Salve as alterações antes de exportar.', true); return; }
  const group = byId('export-group').value, task = byId('export-task').value;
  byId('export-feedback').disabled = true;
  try {
    const response = await fetch(`/feedback/export?group=${group}&task=${task}`, {headers: feedbackHeaders(), cache: 'no-store'});
    if (!response.ok) { const error = await response.json(); throw new Error(error.detail); }
    const url = URL.createObjectURL(await response.blob());
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = `revisoes-${group}-${task}.zip`; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
    reviewStatus('Dataset exportado com as últimas revisões completas. Amostras sem contorno são excluídas da segmentação.');
  } catch (error) { reviewStatus(error.message, true); }
  finally { byId('export-feedback').disabled = false; }
});

async function loadAdminReview(imageId) {
  setProcessing(true);
  setStatus('Carregando radiografia e revisão salvas...');
  try {
    const encoded = encodeURIComponent(imageId);
    const sessionResponse = await fetch('/admin/api/session', {cache: 'no-store'});
    if (sessionResponse.status === 401) {
      location.assign('/review'); return;
    }
    if (!sessionResponse.ok) throw new Error(`Falha HTTP ${sessionResponse.status}.`);
    const session = await sessionResponse.json();
    adminReviewMode = true; adminCsrf = session.csrf; reviewImageId = imageId;
    const lockResponse = await fetch(`/admin/api/images/${encoded}/edit-lock`, {
      method: 'POST', cache: 'no-store', headers: {'X-Panoramica-CSRF': adminCsrf}
    });
    if (!lockResponse.ok) {
      const error = await lockResponse.json();
      throw new Error(error.detail || 'Esta radiografia ja esta sendo editada.');
    }
    adminEditLock = true; startEditLockHeartbeat();
    const [detailsResponse, imageResponse] = await Promise.all([
      fetch(`/admin/api/images/${encoded}`, {cache: 'no-store'}),
      fetch(`/admin/api/images/${encoded}/image?identity=v2`, {cache: 'no-store'})
    ]);
    if ([detailsResponse, imageResponse].some(response => response.status === 401)) {
      location.assign('/review'); return;
    }
    if (!detailsResponse.ok || !imageResponse.ok) {
      const failed = [detailsResponse, imageResponse].find(response => !response.ok);
      const error = (failed.headers.get('content-type') || '').includes('application/json')
        ? await failed.json() : null;
      throw new Error(error?.detail || `Falha HTTP ${failed.status}.`);
    }
    const saved = await detailsResponse.json();
    adminReviewPixelId = imageResponse.headers.get('X-Image-Pixel-SHA256');
    if (!adminReviewPixelId || !/^[a-f0-9]{64}$/.test(adminReviewPixelId)) {
      throw new Error('A API não informou a identidade visual da radiografia.');
    }
    const blob = await imageResponse.blob();
    clearResult();
    if (originalUrl) URL.revokeObjectURL(originalUrl);
    originalUrl = URL.createObjectURL(blob);
    byId('original').src = originalUrl;
    byId('original').hidden = false;
    byId('original-empty').hidden = true;
    await byId('original').decode();

    const file = new File([blob], `${imageId}.png`, {type: 'image/png'});
    const transfer = new DataTransfer(); transfer.items.add(file); byId('file').files = transfer.files;
    reviewImageId = imageId; reviewRevision = saved.revision;
    reviewReviewer = saved.reviewer || null;
    review = structuredClone(saved.document); reviewBaseline = saved.baseline;
    annotationClasses = saved.annotation_classes;
    reviewSource = 'saved'; reviewDirty = false;
    reviewSources = {saved: {document: structuredClone(review), baseline: reviewBaseline, dirty: false}};
    byId('review-source-control').hidden = true;
    byId('patient-group').value = review.patient_group;
    byId('review-age-group').value = saved.age_classification?.label || 'uncertain';
    showCompleteGroups();
    byId('feedback-panel').hidden = false;
    setEditorButtonsDisabled(false);
    for (const [image, empty, download] of [
      ['annotated', 'annotated-empty', 'download'],
      ['additional-annotations', 'additional-annotations-empty', 'download-additional'],
      ['anatomy', 'anatomy-empty', 'download-anatomy']
    ]) {
      byId(image).hidden = false; byId(empty).hidden = true; byId(download).hidden = false;
    }
    byId('anatomy-status').hidden = false;
    renderEditableCards();
    await renderReviewedImages();
    updateAnnotationSource();
    reviewStatus(`Revisão ${reviewRevision} carregada. Edite e salve para criar uma nova revisão.`);
    setStatus(`Detalhes da revisão ${reviewRevision}. Escolha abaixo qual grupo deseja editar.`);
  } catch (error) {
    await releaseAdminEditLock();
    setStatus(error.message || 'Não foi possível carregar a revisão.', true);
  } finally {
    setProcessing(false);
  }
}

const requestedReview = new URLSearchParams(location.search).get('review');
if (requestedReview) loadAdminReview(requestedReview);
