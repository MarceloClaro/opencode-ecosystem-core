# -*- coding: utf-8 -*-
"""
Experimento de coorte — Recamán vs MMR vs estado atual (SPEC-935-R458).

Mede, em corpus-piloto controlado e determinístico, se a diversificação por
Recamán (R457) produz ganho mensurável de diversidade sem degradar relevância,
comparado com o estado atual (top-k) e um baseline MMR clássico.

Escopo honesto: resultados observados em corpus piloto; NÃO generaliza para
produção, NÃO equivale a certificação externa, NÃO promove o diversificador ao
pipeline padrão sem decisão posterior.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from rag.recaman import RecamanDiversifier, AnchorResolver, diversity
from rag.scientific import ScientificDocument, ScientificRAG

# Baselines
N_ANGLES = 6          # famílias de perspectiva (ângulos)
DOCS_PER_ANGLE = 3    # 3 docs por ângulo -> permite "monopólio" da mesma família no topo
LOSS_TOLERANCE = 0.05  # 5% de queda relativa tolerável em groundedness


# ---------------------------------------------------------------------------
# Corpus-piloto determinístico
# ---------------------------------------------------------------------------
# Cada ângulo tem um conjunto de palavras-chave que o distingue e uma "fonte"
# única (usada como âncora canônica pelo AnchorResolver / Div).
ANGLE_POOL = [
    ("metodi", "amostragem", "confundidor", "randomizacao", "replicacao"),
    ("intervencao", "contrafactual", "efeito", "tratamento", "exposicao"),
    ("poder", "tamanho_amostral", "intervalo", "confianca", "rejeicao"),
    ("vies", "selecao", "publicacao", "identificacao", "controle"),
    ("matriz", "variancia", "covariancia", "erro", "estimador"),
    ("hipotese", "significancia", "teste", "regiao", "alfa"),
]


def _doc_text(angle_kws: Tuple[str, ...]) -> str:
    # Texto determinístico: repete as palavras-chave do ângulo intercaladas com
    # termos comuns de um pseudo-artigo científico. Sem aleatoriedade.
    core = " ".join(angle_kws)
    filler = ("sintese de evidencia na literatura revisada por pares "
              "considerando rigor metodologico e limites inferenciais. ")
    return (filler + core + ". ") * 3


def build_pilot_corpus() -> Dict[str, Any]:
    """Constrói corpus-piloto controlado com A ângulos × m documentos.

    Cada ângulo mapeia para uma ``source``/``fonte`` distinta, de modo que a
    Ã¢ncora canônica (AnchorResolver) e a métrica Div(S) sejam coerentes com a
    noção de "família de perspectiva".
    """
    docs: List[ScientificDocument] = []
    angle_sources: List[str] = []
    for a_idx, kws in enumerate(ANGLE_POOL[:N_ANGLES]):
        src = f"family_{a_idx}"
        angle_sources.append(src)
        for m in range(DOCS_PER_ANGLE):
            docs.append(ScientificDocument(
                doc_id=f"doc_{a_idx}_{m}",
                title=f"Estudo do ângulo {a_idx} — item {m}",
                authors=[f"Author{a_idx}{m}"],
                year=2020 + a_idx,
                source=src,
                text=_doc_text(kws),
            ))
    return {"angles": ANGLE_POOL[:N_ANGLES], "sources": angle_sources, "documents": docs}


# ---------------------------------------------------------------------------
# Baseline MMR determinístico (similaridade por sobreposição de tokens)
# ---------------------------------------------------------------------------
def _tokenize(text: str) -> set:
    return {w for w in text.lower().split() if len(w) > 2}


def _sim_tokens(a: Any, b: Any) -> float:
    ta = _tokenize(getattr(a, "text", "") if not isinstance(a, dict) else a.get("text", ""))
    tb = _tokenize(getattr(b, "text", "") if not isinstance(b, dict) else b.get("text", ""))
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


class MMR:
    """Maximal Marginal Relevance baseline, determinístico, λ fixo.

    Seleciona guloso: na iteração, escolhe o item que maximiza
        λ·rel - (1-λ)·max_{j∈Sel} Sim(item, j)
    """

    def __init__(self, lambda_: float = 0.7):
        self.lambda_ = lambda_

    def select(self, ranked: Sequence[Any], k: int) -> List[Any]:
        ranked = list(ranked)
        if not ranked or k <= 0:
            return []
        budget = min(k, len(ranked))
        mmr: List[Any] = []
        remaining = list(ranked)
        # Primeiro: melhor relevância.
        first = remaining.pop(0)
        mmr.append(first)
        while len(mmr) < budget and remaining:
            best_idx, best_score = -1, -1e9
            for i, cand in enumerate(remaining):
                rel = float(getattr(cand, "final_score", 0) if not isinstance(cand, dict) else cand.get("final_score", 0))
                max_sim = max((_sim_tokens(cand, s) for s in mmr), default=0.0)
                score = self.lambda_ * rel - (1 - self.lambda_) * max_sim
                if score > best_score:
                    best_score, best_idx = score, i
            mmr.append(remaining.pop(best_idx))
        return mmr


# ---------------------------------------------------------------------------
# Seleção por estratégia
# ---------------------------------------------------------------------------
def _to_evidence_dicts(evs: Sequence[Any]) -> List[Dict[str, Any]]:
    out = []
    for ev in evs:
        if isinstance(ev, dict):
            out.append(ev)
        else:
            out.append({
                "doc_id": getattr(ev, "doc_id", ""),
                "source": getattr(ev, "source", "") or getattr(ev, "doc_id", ""),
                "final_score": float(getattr(ev, "final_score", 0) or 0),
                "text": getattr(ev, "text", ""),
            })
    return out


def _dedup_by_doc(evs: Sequence[Any]) -> List[Any]:
    """Mantém o melhor trailing de cada DOCUMENTO (dedup de chunks duplicados).

    O ``ScientificRAG.retrieve`` retorna um trailing por chunk do mesmo documento,
    inflando uma família no top-N. Antes de qualquer diversificação pós-ranqueamento
    é necessário operar sobre DOCUMENTOS distintos (a âncora de ``Div``); caso
    contrário, nenhum diversificador consegue espalhar — o que esconderia o efeito.
    """
    best: Dict[str, Any] = {}
    order: List[str] = []
    for ev in evs:
        doc_id = getattr(ev, "doc_id", None)
        if isinstance(ev, dict):
            doc_id = ev.get("doc_id")
        if doc_id is None:
            continue
        score = getattr(ev, "final_score", 0) if not isinstance(ev, dict) else ev.get("final_score", 0)
        score = float(score or 0)
        if doc_id not in best or score > getattr(best[doc_id], "final_score", 0) or \
                (isinstance(best[doc_id], dict) and score > best[doc_id].get("final_score", -1)):
            best[doc_id] = ev
            order.append(doc_id)
    # ordena por score decrescente, preservando a ordem de relevância
    deduped = [best[did] for did in dict.fromkeys(order)]
    deduped.sort(key=lambda ev: (
        (ev.get("final_score", 0) if isinstance(ev, dict) else getattr(ev, "final_score", 0))),
        reverse=True)
    return deduped


def _select_current(ranked: Sequence[Any], k: int) -> List[Any]:
    return list(ranked)[:k]


def _select_recaman(ranked: Sequence[Any], k: int, top_n_candidates: int) -> List[Any]:
    # Diversifica sobre um top-N de candidatos (mais amplo que o orçamento k),
    # preservando a relevância primária, como proposto no manual.
    candidates = list(ranked)[:top_n_candidates]
    d = RecamanDiversifier()
    return d.diversify(candidates, k)


def _coverage(target_families: set, selected: Sequence[Any]) -> float:
    """Fração de famílias-alvo representadas na seleção."""
    if not target_families:
        return 0.0
    got = {_family_of(s) for s in selected}
    covered = 0
    for fam in target_families:
        # qualquer doc cuja família esteja em got
        if fam in got or any(fam in g for g in got):
            covered += 1
    return covered / len(target_families)


def _family_of(item: Any) -> str:
    src = item.get("source", "") if isinstance(item, dict) else getattr(item, "source", "")
    return str(src)


def _metrics_of(selected: Sequence[Any], target_families: set, resolver: AnchorResolver) -> Dict[str, float]:
    evs = _to_evidence_dicts(selected)
    div = diversity(evs, resolver)
    scores = [float(e.get("final_score", 0)) for e in evs]
    groundedness = (sum(scores) / len(scores)) if scores else 0.0
    coverage = _coverage(target_families, evs)
    return {
        "diversity": round(div, 4),
        "groundedness": round(groundedness, 4),
        "coverage": round(coverage, 4),
    }


# ---------------------------------------------------------------------------
# Execução do coorte
# ---------------------------------------------------------------------------
def _make_query(q_idx: int, corpus: Dict[str, Any]) -> Tuple[str, set]:
    """Gera a query do coorte cobrindo, de forma EQUILIBRADA, um subconjunto de ângulos.

    Os ângulos-alvo contribuem palavras-chave de maneira proporcional (não apenas
    os primeiros da lista), garantindo que o ranking cruze genuinamente as famílias
    e que diversidade/cobertura tenham o que medir. Se cada query focasse uma única
    família, o experimento não discriminaria estratégias — o que invalidaria H2.
    """
    target = {corpus["sources"][a] for a in (q_idx, (q_idx + 1) % N_ANGLES, (q_idx + 2) % N_ANGLES)}
    target_idx = sorted({a for a in range(N_ANGLES) if corpus["sources"][a] in target})
    # Distribui palavras-chave por ângulo-alvo, em round-robin, até ~8 tokens.
    kws: List[str] = []
    per_angle = [list(corpus["angles"][a]) for a in target_idx]
    i = 0
    budget = 8
    while sum(len(pa) for pa in per_angle) > 0 and len(kws) < budget:
        pa = per_angle[i % len(per_angle)]
        if pa:
            kws.append(pa.pop(0))
        i += 1
    query = "explique e compare a evidencia para " + " ".join(kws)
    return query, target


def run_cohort(
    corpus: Dict[str, Any],
    top_n: int = 8,
    k: int = 4,
    n_queries: int = 3,
    poll_size: int = 40,
) -> Dict[str, Any]:
    """Executa o coorte e agrega métricas por estratégia.

    Args:
        corpus: saída de build_pilot_corpus().
        top_n: nº de candidatos (documentos distintos) a considerar para
               diversificação (>= k).
        k: orçamento de seleção de cada estratégia.
        n_queries: nº de queries do coorte.
        poll_size: nº de chunks a coletar do retrieve antes da deduplicação por
                   documento (precisa ser amplo para capturar mais de uma família).
    """
    rag = ScientificRAG(min_score=0.0)
    rag.index(corpus["documents"])
    resolver = AnchorResolver()
    mmr = MMR()

    per_query: List[Dict[str, Any]] = []
    agg: Dict[str, Dict[str, float]] = {
        "atual": {"diversity": 0.0, "groundedness": 0.0, "coverage": 0.0, "n": 0},
        "mmr": {"diversity": 0.0, "groundedness": 0.0, "coverage": 0.0, "n": 0},
        "recaman": {"diversity": 0.0, "groundedness": 0.0, "coverage": 0.0, "n": 0},
    }

    for q_idx in range(n_queries):
        query, target_fams = _make_query(q_idx, corpus)
        # Pool amplo: captura chunks de múltiplas famílias (o retrieve retorna
        # vários chunks/doc; cortar cedo monopolizaria uma família e impediria
        # qualquer diversificação de ser observada).
        ranked = rag.retrieve(query, top_k=poll_size)
        if not ranked:
            continue
        # Dedup de chunks por documento: diversificar opera sobre documentos,
        # não sobre chunks duplicados (gargalo real do retrieve upstream).
        ranked = _dedup_by_doc(ranked)
        if len(ranked) < 2:
            continue
        # Limita aos top_n candidatos distintos (base comum e justa p/ as 3 estratégias).
        candidates = list(ranked)[:top_n]
        sel_atual = _select_current(candidates, k)
        sel_mmr = mmr.select(candidates, k)
        sel_rec = _select_recaman(candidates, k, len(candidates))

        m_atual = _metrics_of(sel_atual, target_fams, resolver)
        m_mmr = _metrics_of(sel_mmr, target_fams, resolver)
        m_rec = _metrics_of(sel_rec, target_fams, resolver)

        # top-1 presente na seleção Recamán?
        rec_ids = [s.get("doc_id") for s in _to_evidence_dicts(sel_rec)]
        top1_id = ranked[0].doc_id

        for name, m_ in (("atual", m_atual), ("mmr", m_mmr), ("recaman", m_rec)):
            agg[name]["diversity"] += m_["diversity"]
            agg[name]["groundedness"] += m_["groundedness"]
            agg[name]["coverage"] += m_["coverage"]
            agg[name]["n"] += 1

        per_query.append({
            "query": query,
            "query_index": q_idx,
            "recaman_docs": rec_ids,
            "recaman_top1_present": (top1_id in rec_ids) or (ranked[0].doc_id in rec_ids),
            "atual": m_atual,
            "mmr": m_mmr,
            "recaman": m_rec,
        })

    # Médias por estratégia
    per_strategy: Dict[str, Dict[str, float]] = {}
    for name, a in agg.items():
        n = max(a["n"], 1)
        per_strategy[name] = {
            "diversity": round(a["diversity"] / n, 4),
            "groundedness": round(a["groundedness"] / n, 4),
            "coverage": round(a["coverage"] / n, 4),
        }

    # Veredito H2 (ganho ESTRITO, anti-empate espúrio):
    #   - Recamán deve demonstrar diversidade ESTRITAMENTE maior que o top-k
    #     (não basta empatar);
    #   - e a queda relativa de groundedness deve ser <= tolerância.
    # Registra também a comparação Recamán vs MMR (baseline clássico) para
    # honestidade: se MMR superar Recamán claramente, isso é documentado.
    rec = per_strategy["recaman"]
    atu = per_strategy["atual"]
    mmrx = per_strategy["mmr"]
    loss_rel = (atu["groundedness"] - rec["groundedness"]) / atu["groundedness"] if atu["groundedness"] else 0.0
    gain_div = rec["diversity"] - atu["diversity"]
    sustenta = (gain_div > 1e-9) and (loss_rel <= LOSS_TOLERANCE)
    # Situação: Recamán empatando é NÃO-demonstração; MMR superando é registrado.
    mmr_supera_recaman = mmrx["diversity"] > rec["diversity"] + 1e-9

    return {
        "config": {"top_n": top_n, "k": k, "n_queries": len(per_query)},
        "per_query": per_query,
        "per_strategy": per_strategy,
        "recaman": {
            "diversity": rec["diversity"],
            "groundedness": rec["groundedness"],
            "coverage": rec["coverage"],
            "gain_div_vs_atual": round(gain_div, 4),
            "loss_rel_groundedness": round(loss_rel, 4),
        },
        "comparison": {
            "mmr_div": mmrx["diversity"],
            "recaman_div": rec["diversity"],
            "mmr_supera_recaman": mmr_supera_recaman,
        },
        "verdict": "sustenta_H2" if sustenta else "refuta_H2",
        "escopo": "resultado observado em corpus-piloto controlado; nao generaliza para producao.",
    }


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------
def write_report(result: Dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


STRATEGIES = ["atual", "mmr", "recaman"]


if __name__ == "__main__":  # pragma: no cover
    corpus = build_pilot_corpus()
    res = run_cohort(corpus, top_n=8, k=4, n_queries=4)
    print("== Coorte Recamán vs MMR vs atual ==")
    for strat in STRATEGIES:
        m = res["per_strategy"][strat]
        print(f"  {strat:8s} div={m['diversity']:.3f} grounded={m['groundedness']:.3f} cov={m['coverage']:.3f}")
    print("verdict:", res["verdict"])
    write_report(res, Path(__file__).resolve().parent / "cohort_report.json")
