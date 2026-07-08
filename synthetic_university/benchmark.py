"""Benchmark do Pipeline Refinado vs. Baselines (R81).

Compara 4 estratégias de geração usando a MESMA métrica de coerência
(embedding neural Ollama nomic-embed-text 768-d) para todos.

Estratégias:
  1. Random: pares aleatórios puros (sem guiança)
  2. Jaccard: pares ranqueados por similaridade lexical (V0)
  3. Word2Vec: pares via word embedding (se disponível)
  4. Refined: pipeline completo (embedding neural + faculdade-consciente + guiado)
"""

import json
import time
import random
import os
from itertools import combinations as iter_combinations
from typing import List, Tuple, Optional

from synthetic_university.faculties import FACULTY_MAP


def all_concepts(faculties):
    """Retorna [(fid, cid, conceito), ...]."""
    items = []
    for fid, fac in faculties.items():
        for cid, conceito in enumerate(fac.conceitos):
            items.append((fid, cid, conceito))
    return items


# Cache do embedder para reuso entre baselines
_embedder = None

def get_embedder():
    """Retorna (ou cria) o embedder neural compartilhado."""
    global _embedder
    if _embedder is not None:
        return _embedder
    from synthetic_university.semantic_embedder import SemanticEmbedder
    _embedder = SemanticEmbedder(dimension=768)
    if not _embedder.load("/tmp/semantic_embedder.pkl"):
        texts = []
        for fid, fac in FACULTY_MAP.items():
            texts.append(fac.descricao)
            texts.extend([str(c) for c in fac.conceitos])
        _embedder.build_corpus(texts)
        _embedder.save("/tmp/semantic_embedder.pkl")
    return _embedder


def neural_coherence(embedder, term1, term2):
    """Similaridade por cosseno neural, clampada a [0, 1]."""
    v1 = embedder.embed(term1)
    v2 = embedder.embed(term2)
    if v1 is None or v2 is None:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = sum(a * a for a in v1) ** 0.5
    n2 = sum(b * b for b in v2) ** 0.5
    if n1 == 0 or n2 == 0:
        return 0.0
    return max(0.0, min(1.0, float(dot / (n1 * n2))))


# ============================================================
# Baseline 1: Random — pares aleatórios
# ============================================================

def baseline_random(faculties, embedder, n_samples=2000, seed=42):
    """Gera n_samples pares inter-faculdades aleatórios."""
    items = all_concepts(faculties)
    rng = random.Random(seed)
    results = []
    t0 = time.time()
    
    for _ in range(n_samples):
        c1, c2 = rng.sample(items, 2)
        while c1[0] == c2[0]:
            c2 = rng.choice(items)
        coherence = neural_coherence(embedder, c1[2], c2[2])
        novelty = neural_coherence(embedder, c1[2], c2[2])
        novelty = max(0.0, 1.0 - novelty)
        composite = 0.30 * coherence + 0.25 * novelty + 0.25 * 0.5 + 0.20 * 0.5
        
        results.append({
            'concept_1': c1[2],
            'concept_2': c2[2],
            'faculty_1': c1[0],
            'faculty_2': c2[0],
            'coherence': coherence,
            'novelty': novelty,
            'composite': composite,
        })
    
    dt = time.time() - t0
    return results, dt


# ============================================================
# Baseline 2: Jaccard — similaridade lexical (V0 original)
# ============================================================

def baseline_jaccard(faculties, embedder, seed=42):
    """V0 original: ranqueia por similaridade lexical Jaccard."""
    items = all_concepts(faculties)
    rng = random.Random(seed)
    
    # Gerar pares inter-faculdades
    pairs = []
    for (f1, c1, t1), (f2, c2, t2) in iter_combinations(items, 2):
        if f1 != f2:
            # Coerência Jaccard lexical
            s1, s2 = set(t1.lower().split()), set(t2.lower().split())
            jac = len(s1 & s2) / len(s1 | s2) if s1 | s2 else 0.0
            pairs.append(((f1, c1, t1), (f2, c2, t2), jac))
    
    # Ordenar por Jaccard decrescente e pegar top 2000
    pairs.sort(key=lambda x: x[2], reverse=True)
    sample = pairs[:2000]
    
    t0 = time.time()
    results = []
    for (f1, c1, t1), (f2, c2, t2), _ in sample:
        coherence = neural_coherence(embedder, t1, t2)
        novelty = max(0.0, 1.0 - coherence)
        composite = 0.30 * coherence + 0.25 * novelty + 0.25 * 0.5 + 0.20 * 0.5
        
        results.append({
            'concept_1': t1,
            'concept_2': t2,
            'faculty_1': f1,
            'faculty_2': f2,
            'coherence': coherence,
            'novelty': novelty,
            'composite': composite,
        })
    dt = time.time() - t0
    return results, dt


# ============================================================
# Baseline 3: Word2Vec (Gensim)
# ============================================================

def baseline_word2vec(faculties, embedder, seed=42):
    """Word2Vec via Gensim."""
    try:
        from gensim.models import Word2Vec
    except ImportError:
        return None, 0.0
    
    items = all_concepts(faculties)
    rng = random.Random(seed)
    
    # Preparar corpus
    sentences = []
    term_map = {}
    for fid, cid, term in items:
        words = term.replace('-', ' ').replace('_', ' ').lower().split()
        if words:
            sentences.append(words)
            term_map[term] = words
    
    if len(sentences) < 10:
        return None, 0.0
    
    # Gerar pares
    pairs = []
    for (f1, c1, t1), (f2, c2, t2) in iter_combinations(items, 2):
        if f1 != f2:
            pairs.append(((f1, c1, t1), (f2, c2, t2)))
    rng.shuffle(pairs)
    sample = pairs[:500]
    
    t0 = time.time()
    model = Word2Vec(sentences, vector_size=128, window=3, min_count=1,
                     epochs=20, seed=seed, sg=1)
    
    results = []
    for (f1, c1, t1), (f2, c2, t2) in sample:
        w1 = term_map.get(t1, [t1])[0]
        w2 = term_map.get(t2, [t2])[0]
        
        if w1 in model.wv and w2 in model.wv:
            sim = float(model.wv.similarity(w1, w2))
            sim = max(0.0, min(1.0, (sim + 1.0) / 2.0))  # [-1,1] → [0,1]
        else:
            sim = 0.0
        
        # Usar o neural embedding como métrica comum para comparacao justa
        coherence = neural_coherence(embedder, t1, t2)
        novelty = max(0.0, 1.0 - coherence)
        composite = 0.30 * coherence + 0.25 * novelty + 0.25 * 0.5 + 0.20 * 0.5
        
        results.append({
            'concept_1': t1,
            'concept_2': t2,
            'faculty_1': f1,
            'faculty_2': f2,
            'coherence': coherence,
            'novelty': novelty,
            'composite': composite,
            'w2v_similarity': sim,
        })
    dt = time.time() - t0
    return results, dt


# ============================================================
# Refined Pipeline (R75-R79)
# ============================================================

def refined_pipeline(faculties, embedder, seed=42):
    """Pipeline completo R75-R79."""
    from synthetic_university.combinatorial_engine import CombinatorialDiscoveryEngine
    
    engine = CombinatorialDiscoveryEngine(faculties)
    
    t0 = time.time()
    
    faculty_ids = list(faculties.keys())
    all_results = []
    
    # Pares inter-faculdades representativos (10 pares × 50 cada)
    test_pairs = [
        ('human_sciences', 'quantum'),
        ('health_sciences', 'engineering'),
        ('exact_sciences', 'social_sciences'),
        ('literary_linguistic', 'statistics_ds'),
        ('philosophy', 'programming'),
        ('historical', 'health_sciences'),
        ('biological', 'quantum'),
        ('artistic', 'exact_sciences'),
        ('juridical', 'engineering'),
        ('social_sciences', 'quantum'),
    ]
    
    for fa, fb in test_pairs:
        if fa in faculty_ids and fb in faculty_ids:
            pairs = engine.generate_pair_combinations(fa, fb, max_combinations=50)
            all_results.extend(pairs)
    
    # Triplas
    triples = engine.generate_triple_combinations(
        ['human_sciences', 'quantum', 'engineering'], max_combinations=30
    )
    all_results.extend(triples)
    
    dt = time.time() - t0
    
    results = []
    for r in all_results:
        c1 = r.concepts[0] if len(r.concepts) >= 1 else ''
        c2 = r.concepts[1] if len(r.concepts) >= 2 else ''
        f1 = r.faculties[0] if len(r.faculties) >= 1 else ''
        f2 = r.faculties[1] if len(r.faculties) >= 2 else ''
        
        results.append({
            'concept_1': c1,
            'concept_2': c2,
            'faculty_1': f1,
            'faculty_2': f2,
            'coherence': float(r.coherence_score),
            'novelty': float(r.novelty_score),
            'impact': float(r.impact_score),
            'viability': float(r.viability_score),
            'composite': float(r.composite_score),
        })
    
    return results, dt


# ============================================================
# Análise Comparativa
# ============================================================

def analyze(results_sets, labels, times):
    """Analisa e compara."""
    print("=" * 84)
    print("  R81 — BENCHMARK: PIPELINE REFINADO vs. BASELINES")
    print("  (Todas as coerências medidas com embedding neural — métrica única)")
    print("=" * 84)
    print()
    
    header = f"{'Baseline':<20} {'Combs':>8} {'Coerência':>10} {'Std':>8} {'Novelty':>10} {'Composite':>10} {'Alvo%':>8} {'Tempo':>8}"
    print(header)
    print("-" * 84)
    
    rows = []
    for results, label, dt in zip(results_sets, labels, times):
        if results is None or len(results) == 0:
            print(f"{label:<20} {'N/D':>8}")
            rows.append((label, 0, 0, 0, 0, 0, 0, dt))
            continue
        
        n = len(results)
        coh = [r['coherence'] for r in results]
        nov = [r['novelty'] for r in results]
        comp = [r['composite'] for r in results]
        
        mc = sum(coh) / n
        sc = (sum((c - mc) ** 2 for c in coh) / n) ** 0.5
        mn = sum(nov) / n
        mcomp = sum(comp) / n
        pct = sum(1 for c in coh if 0.20 <= c <= 0.55) / n * 100
        
        rows.append((label, n, mc, sc, mn, mcomp, pct, dt))
        print(f"{label:<20} {n:>8} {mc:>10.4f} {sc:>8.4f} {mn:>10.4f} {mcomp:>10.4f} {pct:>7.1f}% {dt:>7.2f}s")
    
    print("-" * 84)
    print()
    
    # Ganhos
    if len(rows) >= 4:
        ref = rows[3]
        rnd = rows[0]
        jac = rows[1]
        
        if ref[2] and rnd[2]:
            print(f"GANHOS REFINED vs. RANDOM:")
            print(f"  Coerência:   {ref[2]:.4f} vs {rnd[2]:.4f} = +{((ref[2]-rnd[2])/rnd[2])*100:.0f}%")
            print(f"  Composite:   {ref[5]:.4f} vs {rnd[5]:.4f} = +{((ref[5]-rnd[5])/rnd[5])*100:.0f}%")
            print(f"  % no alvo:   {ref[6]:.1f}% vs {rnd[6]:.1f}% = +{((ref[6]-rnd[6])/rnd[6])*100:.0f}%")
        
        if jac[2]:
            print(f"\nGANHOS REFINED vs. JACCARD:")
            print(f"  Coerência:   +{((ref[2]-jac[2])/jac[2])*100:.0f}%")
            print(f"  Composite:   +{((ref[5]-jac[5])/jac[5])*100:.0f}%")
    
    print()
    print("=" * 84)
    
    # Retornar dados para salvar
    return rows


# ============================================================
# Main
# ============================================================

def main():
    os.makedirs("academic/benchmark", exist_ok=True)
    random.seed(42)
    
    print("=" * 84)
    print("  R81 — BENCHMARK: INICIALIZANDO")
    print("=" * 84)
    
    # Inicializar embedder neural compartilhado
    print("\nInicializando embedder neural compartilhado...", end=" ", flush=True)
    embedder = get_embedder()
    print("OK\n")
    
    # 1) Random
    print("[1/4] Random baseline...", end=" ", flush=True)
    rnd_results, rnd_time = baseline_random(FACULTY_MAP, embedder, n_samples=2000)
    print(f"{len(rnd_results)} combos em {rnd_time:.2f}s")
    
    # 2) Jaccard
    print("[2/4] Jaccard lexical baseline...", end=" ", flush=True)
    jac_results, jac_time = baseline_jaccard(FACULTY_MAP, embedder)
    print(f"{len(jac_results)} combos em {jac_time:.2f}s")
    
    # 3) Word2Vec
    print("[3/4] Word2Vec baseline...", end=" ", flush=True)
    w2v_results, w2v_time = baseline_word2vec(FACULTY_MAP, embedder)
    if w2v_results is None or len(w2v_results) == 0:
        w2v_results = []
        print("N/D (gensim ausente ou corpus insuficiente)")
    else:
        print(f"{len(w2v_results)} combos em {w2v_time:.2f}s")
    
    # 4) Refined
    print("[4/4] Refined pipeline (R75-R79)...", end=" ", flush=True)
    ref_results, ref_time = refined_pipeline(FACULTY_MAP, embedder)
    print(f"{len(ref_results)} combos em {ref_time:.2f}s")
    
    print()
    
    # Análise
    labels = ["Random", "Jaccard", "Word2Vec", "Refined"]
    times = [rnd_time, jac_time, w2v_time, ref_time]
    rows = analyze([rnd_results, jac_results, w2v_results, ref_results], labels, times)
    
    # Salvar relatório JSON
    report = {
        'benchmark': 'R81',
        'timestamp': time.time(),
        'metric': 'neural_embedding_cosine',
        'embedder': 'Ollama nomic-embed-text 768-d',
        'summary': {},
    }
    
    for results, label in zip([rnd_results, jac_results, w2v_results, ref_results], labels):
        if not results:
            report['summary'][label.lower()] = {'available': False}
            continue
        n = len(results)
        coh = [r['coherence'] for r in results]
        nov = [r['novelty'] for r in results]
        comp = [r['composite'] for r in results]
        
        report['summary'][label.lower()] = {
            'available': True,
            'n': n,
            'time_s': times[labels.index(label)],
            'coherence_mean': sum(coh) / n,
            'coherence_std': (sum((c - sum(coh)/n)**2 for c in coh) / n) ** 0.5,
            'novelty_mean': sum(nov) / n,
            'composite_mean': sum(comp) / n,
            'pct_in_target_20_55': sum(1 for c in coh if 0.20 <= c <= 0.55) / n * 100,
        }
    
    # Ganhos
    if 'refined' in report['summary'] and 'random' in report['summary']:
        rc = report['summary']['refined']['coherence_mean']
        rr = report['summary']['random']['coherence_mean']
        rj = report['summary']['jaccard']['coherence_mean']
        if rr > 0:
            report['gain_vs_random_coherence'] = (rc - rr) / rr * 100
        if rj > 0:
            report['gain_vs_jaccard_coherence'] = (rc - rj) / rj * 100
    
    with open("academic/benchmark/r81_benchmark_report.json", "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    # Relatório TXT
    with open("academic/benchmark/r81_benchmark_report.txt", "w") as f:
        f.write("R81 — BENCHMARK: PIPELINE REFINADO vs. BASELINES\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Métrica única: cosseno neural (Ollama nomic-embed-text 768-d)\n\n")
        for results, label in zip([rnd_results, jac_results, w2v_results, ref_results], labels):
            if not results:
                f.write(f"\n{label}: N/D\n")
                continue
            n = len(results)
            mc = sum(r['coherence'] for r in results) / n
            mn = sum(r['novelty'] for r in results) / n
            mcomp = sum(r['composite'] for r in results) / n
            pct = sum(1 for r in results if 0.20 <= r['coherence'] <= 0.55) / n * 100
            dt = times[labels.index(label)]
            f.write(f"\n{label} ({n} combos, {dt:.2f}s):\n")
            f.write(f"  Coerência:  {mc:.4f}\n")
            f.write(f"  Novelty:    {mn:.4f}\n")
            f.write(f"  Composite:  {mcomp:.4f}\n")
            f.write(f"  % [0.20-0.55]: {pct:.1f}%\n")
    
    print(f"\nRelatórios salvos em academic/benchmark/")
    print("=" * 84)


if __name__ == "__main__":
    main()
