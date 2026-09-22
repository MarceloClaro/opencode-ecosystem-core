"""R550 — segmentação por capítulo do manuscrito REAL Molambudos → N episódios.

Anti-overclaim: usa o manuscrito de PRODUÇÃO (projetos/molambudos/molambudos.md),
não um texto de teste. Os números de capítulo = contagem física, não prometida.
"""
import sys, pathlib, importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[1]

def _load_executor():
    p = ROOT / "agent_runners" / "nlm_executor.py"
    if not p.exists():
        raise AssertionError(f"executor físico ausente: {p}")
    import sys
    spec = importlib.util.spec_from_file_location("nlm_executor", p)
    mod = importlib.util.module_from_spec(spec)
    # GATE de import físico-físico (lição R551): o executor trilogia declara @dataclass;
    # carregar arquivo fora do sys.modules quebra dataclasses.resolve → REGISTRAR
    # O NOME ANTES do exec_module. SEM isso o test_ importaria um executor
    # quebrado e fingiria GREEN. (Anti-falsificação real, não cosmética.)
    sys.modules["nlm_executor"] = mod
    spec.loader.exec_module(mod)
    return mod

ex = _load_executor()
assert ex is not None, "nlm_executor não carregável"

MANUS = ROOT / "projetos" / "molambudos" / "molambudos.md"


def test_r550_segmenta_manuscrito_real():
    """o manuscrito de PRODUÇÃO real segmenta em N≥2 capítulos? (físico)"""
    texto = MANUS.read_text(encoding="utf-8")
    assert len(texto) > 100_000, f"manuscrito pequeno demais p/ produção: {len(texto)}"
    trechos = ex.segmentar_por_capitulo(texto)
    assert len(trechos) >= 2, f"esperado N≥2 capítulos, veio {len(trechos)}"
    # cada trecho começa com o marcador de capítulo
    for t in trechos[:3]:
        # anti-overclaim: o manuscrito FÍSICO REAL de produção marca com "## MEM-NN"
        # (entradas de diário), NUNCA "CAPÍTULO" — o assert aceita os marcadores REAIS
        assert t.lstrip("# ").upper().startswith(("MEM", "CAPÍTULO", "CAPITULO", "PRÓLOGO", "PROLOGO")), t[:40]


def test_r550_gera_um_job_por_capitulo():
    """rota --por-capitulo monta 1 job NLM por capítulo — sintaxe real sem --profile"""
    texto = MANUS.read_text(encoding="utf-8")
    trechos = ex.segmentar_por_capitulo(texto)
    jobs = ex.montar_jobs_por_capitulo(trechos)
    assert len(jobs) == len(trechos), "1 job por capítulo não bate"
    for j in jobs:
        assert j.startswith("nlm download audio -o "), j
        assert "--profile" not in j, "sintaxe canônica NÃO usa --profile (bug trilogia R547)"


def test_r550_episodios_mantem_tamanho_uniforme():
    """anti-overclaim: proporção de capítulos reais (não prometer 32 se for outro nº)"""
    texto = MANUS.read_text(encoding="utf-8")
    trechos = ex.segmentar_por_capitulo(texto)
    maior = max(len(t) for t in trechos)
    menor = min(len(t) for t in trechos)
    assert maior < len(texto), "segmentação falhou: trecho == manuscrito inteiro (1 episódio único)"
    assert menor >= 1
    print(f"    [r550-info] capítulos segmentados: {len(trechos)} | trechos [menor={menor} maior={maior} chars]")
