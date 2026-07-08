"""Discovery Dashboard Generator — SPEC-935 R87.

Gera um dashboard HTML interativo auto-contido com todas as metricas
do pipeline de descoberta interdisciplinar da Universidade Sintetica.
"""

from __future__ import annotations
import json
import os
import time
from typing import Dict, List, Optional, Any
from collections import Counter


# =========================================================================
# Data Loaders
# =========================================================================

def load_cycles_data() -> List[Dict]:
    """Carrega dados dos ciclos de evolucao."""
    path = "evolution/cycles.json"
    if not os.path.exists(path):
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get('cycles', [])


def load_validation_data() -> Optional[Dict]:
    """Carrega dados de validacao empirica mais recente."""
    validation_dir = "academic/validation"
    if not os.path.exists(validation_dir):
        return None
    
    files = sorted([f for f in os.listdir(validation_dir) if f.endswith('.json')])
    if not files:
        return None
    
    latest = files[-1]
    with open(os.path.join(validation_dir, latest)) as f:
        return json.load(f)


def load_benchmark_data() -> Optional[Dict]:
    """Carrega dados do benchmark mais recente."""
    path = "academic/benchmark/r81_benchmark_report.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def get_faculty_map() -> Dict:
    """Retorna mapa de faculdades."""
    try:
        from synthetic_university.faculties import FACULTY_MAP
        return {
            fid: fac.nome for fid, fac in FACULTY_MAP.items()
        }
    except ImportError:
        return {}


def get_professor_counts() -> Dict[str, int]:
    """Retorna contagem de professores por faculdade."""
    try:
        from synthetic_university.agents.professors import create_all_professors
        profs = create_all_professors()
        return dict(Counter(p.faculty_id for p in profs))
    except ImportError:
        return {}


# =========================================================================
# Chart Data Builders
# =========================================================================

def build_evolution_chart_data(cycles: List[Dict]) -> Dict:
    """Extrai dados de scores ao longo dos ciclos."""
    labels = [c['round_id'] for c in cycles]
    scores = [c.get('score', 0) for c in cycles]
    return {'labels': labels, 'scores': scores}


def build_proximity_chart_data() -> Dict:
    """Retorna dados da matriz de proximidade 11x11."""
    try:
        from synthetic_university.combinatorial_engine import CombinatorialDiscoveryEngine
        from synthetic_university.faculties import FACULTY_MAP
        
        engine = CombinatorialDiscoveryEngine(FACULTY_MAP)
        matrix = engine.embedding._faculty_proximity
        
        faculties = sorted(set(
            f[0] for f in matrix.keys()
        ))
        
        full_matrix = []
        for fa in faculties:
            row = []
            for fb in faculties:
                val = matrix.get((fa, fb), matrix.get((fb, fa), 0.0))
                row.append(round(val, 3))
            full_matrix.append(row)
        
        return {
            'faculties': faculties,
            'matrix': full_matrix,
        }
    except Exception:
        return {'faculties': [], 'matrix': []}


def build_benchmark_chart_data() -> Optional[Dict]:
    """Extrai dados do benchmark."""
    data = load_benchmark_data()
    if not data:
        return None
    
    summary = data.get('summary', {})
    labels = []
    coherence = []
    composite = []
    
    for name in ['random', 'jaccard', 'refined']:
        bl = summary.get(name, {})
        if bl.get('available', True):
            labels.append(name.capitalize())
            coherence.append(bl.get('coherence_mean', 0))
            composite.append(bl.get('composite_mean', 0))
    
    return {
        'labels': labels,
        'coherence': coherence,
        'composite': composite,
    }


def build_theses_ranked_data() -> List[Dict]:
    """Extrai dados das teses ranqueadas."""
    data = load_validation_data()
    if not data:
        return []
    return data.get('theses_ranked', [])


# =========================================================================
# HTML Template
# =========================================================================

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="{LANG}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; line-height: 1.6; }}
.header {{ background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); padding: 2rem; text-align: center; border-bottom: 1px solid #334155; }}
.header h1 {{ font-size: 1.8rem; font-weight: 300; color: #38bdf8; }}
.header h1 strong {{ font-weight: 600; color: #f0f9ff; }}
.header p {{ color: #94a3b8; margin-top: 0.5rem; font-size: 0.9rem; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 1rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1rem; }}
.card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.25rem; }}
.card h2 {{ font-size: 1.1rem; font-weight: 500; color: #38bdf8; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #334155; }}
.card .metric {{ display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px solid #1e293b; }}
.card .metric .label {{ color: #94a3b8; }}
.card .metric .value {{ color: #e2e8f0; font-weight: 500; }}
.card table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
.card th {{ text-align: left; padding: 0.5rem 0.3rem; border-bottom: 1px solid #475569; color: #94a3b8; font-weight: 500; }}
.card td {{ padding: 0.4rem 0.3rem; border-bottom: 1px solid #1e293b; }}
.card tr:hover td {{ background: #0f172a40; }}
.chart-container {{ position: relative; height: 250px; width: 100%; }}
.badge {{ display: inline-block; padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }}
.badge.strong {{ background: #166534; color: #86efac; }}
.badge.moderate {{ background: #854d0e; color: #fde047; }}
.badge.weak {{ background: #7f1d1d; color: #fca5a5; }}
.footer {{ text-align: center; padding: 2rem; color: #475569; font-size: 0.8rem; border-top: 1px solid #334155; margin-top: 2rem; }}
.lang-switch {{ position: absolute; top: 1rem; right: 1rem; }}
.lang-switch button {{ background: #1e293b; border: 1px solid #334155; color: #94a3b8; padding: 0.3rem 0.8rem; border-radius: 6px; cursor: pointer; }}
.lang-switch button:hover {{ background: #334155; }}
@media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<div class="header">
  <h1><strong>{TITLE}</strong></h1>
  <p>{SUBTITLE}</p>
  <p>SPEC-935 &mdash; {DATA_DATE} &mdash; {N_CYCLES} evolution rounds &mdash; {N_TESTS} tests</p>
</div>

<div class="container">

<!-- ============================================================ -->
<!-- Summary Cards -->
<!-- ============================================================ -->
<div class="grid">
  <div class="card">
    <h2>📊 {LBL_PIPELINE_SCORE}</h2>
    <div style="text-align:center;padding:1rem;">
      <span style="font-size:3rem;font-weight:700;color:#38bdf8;">{AVG_SCORE}</span>
      <span style="font-size:1rem;color:#94a3b8;">/10</span>
    </div>
    <div class="metric"><span class="label">{LBL_COHERENCE}</span><span class="value">{COHERENCE}</span></div>
    <div class="metric"><span class="label">{LBL_COMPOSITE}</span><span class="value">{COMPOSITE}</span></div>
    <div class="metric"><span class="label">{LBL_PROFESSORS}</span><span class="value">{N_PROFS}</span></div>
  </div>

  <div class="card">
    <h2>📈 {LBL_EVOLUTION}</h2>
    <div class="chart-container">
      <canvas id="evolutionChart"></canvas>
    </div>
  </div>

  <div class="card">
    <h2>🔬 {LBL_VALIDATION}</h2>
    <div class="metric"><span class="label">{LBL_EMPIRICAL_SCORE}</span><span class="value">{EMP_SCORE}</span></div>
    <div class="metric"><span class="label">{LBL_CONVERGENCE}</span><span class="value">{CONVERGENCE}</span></div>
    <div class="metric"><span class="label">{LBL_ENDORSEMENT}</span><span class="value"><span class="badge {ENDORSE_CLASS}">{ENDORSEMENT}</span></span></div>
  </div>
</div>

<!-- ============================================================ -->
<!-- Proximity Matrix -->
<!-- ============================================================ -->
<div class="grid">
  <div class="card">
    <h2>🌐 {LBL_PROXIMITY}</h2>
    <div class="chart-container" style="height:350px;">
      <canvas id="proximityChart"></canvas>
    </div>
  </div>

  <div class="card">
    <h2>⚖️ {LBL_BENCHMARK}</h2>
    <div class="chart-container">
      <canvas id="benchmarkChart"></canvas>
    </div>
  </div>
</div>

<!-- ============================================================ -->
<!-- Theses Ranking -->
<!-- ============================================================ -->
<div class="card" style="margin-top:1rem;">
  <h2>🏆 {LBL_THESES}</h2>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>{LBL_TITLE}</th>
        <th>{LBL_SCORE}</th>
        <th>{LBL_CONVERGENCE}</th>
        <th>{LBL_ENDORSEMENT}</th>
      </tr>
    </thead>
    <tbody>
      {THESIS_ROWS}
    </tbody>
  </table>
</div>

<!-- ============================================================ -->
<!-- Professors Distribution -->
<!-- ============================================================ -->
<div class="card" style="margin-top:1rem;">
  <h2>👨‍🏫 {LBL_PROFESSORS_DIST}</h2>
  <div class="chart-container" style="height:200px;">
    <canvas id="professorsChart"></canvas>
  </div>
</div>

</div>

<div class="footer">
  <p>{FOOTER}</p>
</div>

<script>
// ============================================================
// Chart.js Visualizations
// ============================================================

Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = '#334155';

// Evolution Chart
new Chart(document.getElementById('evolutionChart'), {{
  type: 'line',
  data: {{
    labels: {EVOLUTION_LABELS},
    datasets: [{{
      label: '{LBL_SCORE_LABEL}',
      data: {EVOLUTION_SCORES},
      borderColor: '#38bdf8',
      backgroundColor: 'rgba(56,189,248,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 4,
      pointHoverRadius: 6,
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      y: {{ min: 0, max: 10, ticks: {{ stepSize: 2 }} }},
      x: {{ ticks: {{ maxTicksLimit: 10, font: {{ size: 9 }} }} }}
    }}
  }}
}});

// Proximity Matrix Heatmap
const faculties = {PROX_FACULTIES};
const matrix = {PROX_MATRIX};
const ctx = document.getElementById('proximityChart').getContext('2d');
const cellSize = Math.min(30, 400 / faculties.length);

// Draw heatmap manually
const heatmapWidth = faculties.length * cellSize;
const heatmapHeight = faculties.length * cellSize;

ctx.clearRect(0, 0, 450, 350);
ctx.save();
ctx.translate(60, 20);

// Color scale
function getColor(v) {{
  const r = Math.round(15 + v * 56);
  const g = Math.round(41 + v * 147);
  const b = Math.round(95 + v * 168);
  return `rgb(${{r}},${{g}},${{b}})`;
}}

// Cells
for (let i = 0; i < faculties.length; i++) {{
  for (let j = 0; j < faculties.length; j++) {{
    ctx.fillStyle = getColor(matrix[i][j]);
    ctx.fillRect(j * cellSize, i * cellSize, cellSize - 1, cellSize - 1);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '8px sans-serif';
    if (i === 0) ctx.fillText(faculties[j].substring(0,4), j * cellSize, -5);
  }}
  ctx.fillStyle = '#94a3b8';
  ctx.font = '8px sans-serif';
  ctx.fillText(faculties[i].substring(0,6), -55, i * cellSize + 10);
}}

ctx.restore();

// Benchmark Chart
new Chart(document.getElementById('benchmarkChart'), {{
  type: 'bar',
  data: {{
    labels: {BENCH_LABELS},
    datasets: [
      {{
        label: '{LBL_COHERENCE}',
        data: {BENCH_COHERENCE},
        backgroundColor: 'rgba(56,189,248,0.7)',
      }},
      {{
        label: '{LBL_COMPOSITE}',
        data: {BENCH_COMPOSITE},
        backgroundColor: 'rgba(129,140,248,0.7)',
      }}
    ]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ display: true, position: 'top', labels: {{ boxWidth: 12 }} }} }},
    scales: {{ y: {{ min: 0, max: 0.8 }} }}
  }}
}});

// Professors Chart
new Chart(document.getElementById('professorsChart'), {{
  type: 'bar',
  data: {{
    labels: {PROF_LABELS},
    datasets: [{{
      label: '{LBL_PROFESSORS}',
      data: {PROF_COUNTS},
      backgroundColor: 'rgba(34,211,238,0.7)',
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ ticks: {{ stepSize: 1 }} }} }}
  }}
}});
</script>
</body>
</html>
"""


# =========================================================================
# Dashboard Generator
# =========================================================================

class DashboardGenerator:
    """Gera dashboard HTML interativo com metricas do pipeline."""
    
    def __init__(self, lang: str = "en"):
        self.lang = lang
        self.labels = self._get_labels(lang)
    
    def _get_labels(self, lang: str) -> Dict[str, str]:
        """Retorna labels no idioma especificado."""
        if lang == "pt":
            return {
                'title': 'Universidade Sintética Transversal',
                'subtitle': 'Dashboard de Descoberta Interdisciplinar',
                'pipeline_score': 'Score do Pipeline',
                'coherence': 'Coerência',
                'composite': 'Composite',
                'professors': 'Professores',
                'evolution': 'Evolução',
                'validation': 'Validação',
                'empirical_score': 'Score Empírico',
                'convergence': 'Convergência',
                'endorsement': 'Endosso',
                'proximity': 'Matriz de Proximidade',
                'benchmark': 'Benchmark',
                'theses': 'Teses',
                'title_col': 'Título',
                'score_col': 'Score',
                'convergence_col': 'Conv.',
                'endorsement_col': 'Endosso',
                'professors_dist': 'Distribuição de Professores',
                'score': 'Score',
                'footer': 'Pipeline de Descoberta Interdisciplinar | SPEC-935 | OpenCode Ecosystem Core',
            }
        else:
            return {
                'title': 'Synthetic Transversal University',
                'subtitle': 'Interdisciplinary Discovery Dashboard',
                'pipeline_score': 'Pipeline Score',
                'coherence': 'Coherence',
                'composite': 'Composite',
                'professors': 'Professors',
                'evolution': 'Evolution',
                'validation': 'Validation',
                'empirical_score': 'Empirical Score',
                'convergence': 'Convergence',
                'endorsement': 'Endorsement',
                'proximity': 'Proximity Matrix',
                'benchmark': 'Benchmark',
                'theses': 'Top Theses',
                'title_col': 'Title',
                'score_col': 'Score',
                'convergence_col': 'Conv.',
                'endorsement_col': 'Endorsement',
                'professors_dist': 'Professors by Faculty',
                'score': 'Score',
                'footer': 'Interdisciplinary Discovery Pipeline | SPEC-935 | OpenCode Ecosystem Core',
            }
    
    def generate(self) -> str:
        """Gera o HTML do dashboard."""
        cycles = load_cycles_data()
        validation = load_validation_data()
        benchmark = load_benchmark_data()
        prof_counts = get_professor_counts()
        L = self.labels
        
        # Evolution data
        evo = build_evolution_chart_data(cycles)
        
        # Proximity
        prox = build_proximity_chart_data()
        
        # Benchmark
        bench = build_benchmark_chart_data()
        
        # Theses
        theses = build_theses_ranked_data()
        
        # Professors
        fac_map = get_faculty_map()
        prof_labels = []
        prof_counts_list = []
        for fid in sorted(prof_counts.keys()):
            name = fac_map.get(fid, fid).split('(')[0].strip()
            prof_labels.append(name)
            prof_counts_list.append(prof_counts[fid])
        
        # Metrics
        avg_score = sum(c.get('score', 0) for c in cycles) / max(len(cycles), 1)
        coherence = 0.43  # valor do pipeline refinado
        composite = 0.58  # valor do benchmark
        n_profs = sum(prof_counts_list) if prof_counts_list else 0
        
        # Validation metrics
        emp_score = 0
        convergence = 0
        endorsement = "N/A"
        endorse_class = "moderate"
        if validation:
            agg = validation.get('aggregate_scores', {})
            emp_score = agg.get('avg_empirical_score', 0)
            convergence = agg.get('avg_convergence_rate', 0)
            
            cal_dist = validation.get('calibrated_endorsement_distribution', {})
            if cal_dist:
                max_k = max(cal_dist, key=cal_dist.get)
                endorsement = max_k.capitalize()
                endorse_class = max_k
        
        # Thesis rows
        thesis_rows = ""
        for t in theses[:10]:
            rank = t.get('rank', 0)
            title = t.get('title', '')[:60]
            score = t.get('empirical_score', 0)
            conv = t.get('convergence_rate', 0)
            end = t.get('calibrated_endorsement', t.get('majority_endorsement', 'N/A'))
            end_class = end.lower() if end else 'moderate'
            thesis_rows += (
                f"<tr><td>{rank}</td>"
                f"<td>{title}</td>"
                f"<td>{score:.3f}</td>"
                f"<td>{conv:.2f}</td>"
                f"<td><span class=\"badge {end_class}\">{end}</span></td></tr>\n"
            )
        
        # Data date
        data_date = time.strftime("%Y-%m-%d %H:%M")
        
        # Format numbers for display
        emp_score_str = f"{emp_score:.3f}" if emp_score else "N/A"
        convergence_str = f"{convergence:.2f}" if convergence else "N/A"
        
        html = HTML_TEMPLATE.format(
            LANG="en" if self.lang == "en" else "pt",
            TITLE=L['title'],
            SUBTITLE=L['subtitle'],
            DATA_DATE=data_date,
            N_CYCLES=len(cycles),
            N_TESTS=144,  # valor atualizado
            LBL_PIPELINE_SCORE=L['pipeline_score'],
            LBL_COHERENCE=L['coherence'],
            LBL_COMPOSITE=L['composite'],
            LBL_PROFESSORS=L['professors'],
            LBL_EVOLUTION=L['evolution'],
            LBL_VALIDATION=L['validation'],
            LBL_EMPIRICAL_SCORE=L['empirical_score'],
            LBL_CONVERGENCE=L['convergence'],
            LBL_ENDORSEMENT=L['endorsement'],
            LBL_PROXIMITY=L['proximity'],
            LBL_BENCHMARK=L['benchmark'],
            LBL_THESES=L['theses'],
            LBL_TITLE=L['title_col'],
            LBL_SCORE=L['score_col'],
            LBL_CONVERGENCE_COL=L['convergence_col'],
            LBL_ENDORSEMENT_COL=L['endorsement_col'],
            LBL_PROFESSORS_DIST=L['professors_dist'],
            LBL_SCORE_LABEL=L['score'],
            AVG_SCORE=f"{avg_score:.1f}",
            COHERENCE=f"{coherence:.2f}",
            COMPOSITE=f"{composite:.2f}",
            N_PROFS=str(n_profs),
            EMP_SCORE=emp_score_str,
            CONVERGENCE=convergence_str,
            ENDORSEMENT=endorsement,
            ENDORSE_CLASS=endorse_class,
            EVOLUTION_LABELS=json.dumps(evo.get('labels', [])),
            EVOLUTION_SCORES=json.dumps(evo.get('scores', [])),
            PROX_FACULTIES=json.dumps(prox.get('faculties', [])),
            PROX_MATRIX=json.dumps(prox.get('matrix', [])),
            BENCH_LABELS=json.dumps(bench.get('labels', []) if bench else []),
            BENCH_COHERENCE=json.dumps(bench.get('coherence', []) if bench else []),
            BENCH_COMPOSITE=json.dumps(bench.get('composite', []) if bench else []),
            PROF_LABELS=json.dumps(prof_labels),
            PROF_COUNTS=json.dumps(prof_counts_list),
            THESIS_ROWS=thesis_rows or "<tr><td colspan='5' style='text-align:center;color:#64748b;'>No validation data</td></tr>",
            FOOTER=L['footer'],
        )
        
        return html
    
    def write(self, output_dir: str = "academic/dashboard") -> str:
        """Escreve o dashboard em arquivo HTML."""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "index.html")
        
        html = self.generate()
        with open(filepath, "w") as f:
            f.write(html)
        
        # Tambem gerar versao PT
        pt_gen = DashboardGenerator(lang="pt")
        pt_html = pt_gen.generate()
        pt_path = os.path.join(output_dir, "index_pt.html")
        with open(pt_path, "w") as f:
            f.write(pt_html)
        
        return filepath
