"""Regressões de medida lexical; este arquivo não certifica os motores."""
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from scanners.noological_scanner import ECOSYSTEM_DIMENSIONS, NoologicalScanner
from scanners.pipeline import DiagnosticPipeline


RETAINED = Path(__file__).parent / "fixtures" / "r835-review-heldout.txt"
RETAINED_SHA256 = "36596b3048f3dcce8f701abb99cceb33a9e485bc9a78463e30b80359a4f5d9bf"


def scan(text):
    trail = SimpleNamespace(get_all_text=lambda: text)
    return NoologicalScanner(domain="ecosystem").scan(trail, research_domain="ecosystem")


def test_catalogo_tem_proprietario_canonico_e_aliases_declarados():
    from scanners.noological_scanner import ECOSYSTEM_CANONICAL_CATEGORIES, ECOSYSTEM_CATEGORY_ALIASES
    names = {category for dimension in ECOSYSTEM_DIMENSIONS.values() for category in dimension.categories}
    assert set(ECOSYSTEM_CANONICAL_CATEGORIES) == names
    assert ECOSYSTEM_CANONICAL_CATEGORIES["behavioral_gate"]["dimension"] == "trust_economy"
    assert ECOSYSTEM_CATEGORY_ALIASES[("protocolos", "behavioral_gate")] == "trust_economy"
    assert ECOSYSTEM_CATEGORY_ALIASES[("evolucao", "successor_generator")] == "scanners"
    assert all(tuple(record["keywords"]) for record in ECOSYSTEM_CANONICAL_CATEGORIES.values())


def test_behavioral_gate_e_successor_contam_uma_vez():
    report = scan("behavioral_gate successor_generator")
    assert report["categories_covered"] == 2
    assert report["total_categories"] == len({c for d in ECOSYSTEM_DIMENSIONS.values() for c in d.categories})
    assert report["dimensions"]["protocolos"]["category_aliases"] == {"behavioral_gate": "trust_economy.behavioral_gate"}
    layer = report["ecosystem_layers"]["diagnostico_evolucao"]
    assert layer["covered"] == 1
    assert layer["total_categories"] == len({c for key in ("scanners", "evolucao") for c in ECOSYSTEM_DIMENSIONS[key].categories})


@pytest.mark.parametrize("text", ["", "z3 staking sdd tdd"])
def test_vazio_e_palavras_solta_nao_certificam_cobertura(text):
    report = scan(text)
    assert report["overall_coverage_pct"] < 100
    assert report["functional_validation"] is False
    assert report["externally_validated"] is False
    assert report["measurement_kind"] == "lexical_category_mentions"
    assert all(d["confidence"] is None for d in report["dimensions"].values())
    if not text:
        assert report["overall_density"] == 0
        assert report["categories_covered"] == 0
    else:
        assert report["categories_covered"] == 4


def test_negacao_nao_ativa_alias():
    report = scan("Não existe behavioral_gate. Não existe successor_generator.")
    assert report["categories_covered"] == 0


def test_corpus_retido_nao_chama_autodescoberta_e_registra_medida(monkeypatch):
    text = RETAINED.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert digest == RETAINED_SHA256, "o corpus retido foi alterado; a origem deve ser revista"
    pipeline = DiagnosticPipeline(domain="ecosystem")
    def forbidden(*args):
        pytest.fail("corpus retido foi enriquecido com os próprios arquivos")
    monkeypatch.setattr(pipeline, "_build_ecosystem_corpus", forbidden)
    monkeypatch.setattr("scanners.pipeline.metabus.publish_subsystem_event", lambda *args, **kwargs: None)
    report = pipeline.run(text, domain="ecosystem", corpus_mode="retained", corpus_id="human-review-r3", expected_corpus_sha256=digest)
    measure = report["measurement"]
    assert measure["input_sha256"] == digest
    assert measure["measured_corpus_sha256"] == digest
    assert measure["measured_bytes"] == len(text.encode("utf-8"))
    assert measure["kind"] == "retained_input_lexical"
    assert measure["corpus_id"] == "human-review-r3"
    assert measure["functional_validation"] is False
    assert measure["externally_validated"] is False
    assert report["noological"]["coverage"] == scan(text)["overall_coverage_pct"]
    assert report["noological"]["summary"]["categories_covered"] == 4
    assert report["noological"]["coverage"] == 5


@pytest.mark.parametrize("kwargs", [
    {"corpus_id": "r3", "expected_corpus_sha256": "0" * 64},
    {"expected_corpus_sha256": hashlib.sha256(b"x").hexdigest()},
    {"corpus_id": "r3"},
])
def test_retido_exige_identidade_e_hash_exato(kwargs):
    with pytest.raises(ValueError):
        DiagnosticPipeline(domain="ecosystem").run("x", domain="ecosystem", corpus_mode="retained", **kwargs)


def isolated_inventory(tmp_path, monkeypatch):
    """Arquivos físicos locais, isolados das edições concorrentes do checkout."""
    for name in ("noological_scanner", "pipeline", "teleological_scanner", "potentiality_scanner"):
        path = tmp_path / "scanners" / f"{name}.py"
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"class {name.title().replace('_', '')}:\n    pass\n", encoding="utf-8")
    monkeypatch.setattr("scanners.pipeline.__file__", str(tmp_path / "scanners" / "pipeline.py"))


def test_cache_da_autodescoberta_inclui_entrada(tmp_path, monkeypatch):
    isolated_inventory(tmp_path, monkeypatch)
    pipeline = DiagnosticPipeline(domain="ecosystem")
    first = pipeline._build_ecosystem_corpus("R835-entrada-primeira")
    second = pipeline._build_ecosystem_corpus("R835-entrada-segunda")
    assert "R835-entrada-primeira" in first
    assert "R835-entrada-segunda" in second
    assert "R835-entrada-primeira" not in second


def test_corpus_reproduzivel_em_execucoes_independentes(tmp_path, monkeypatch):
    isolated_inventory(tmp_path, monkeypatch)
    first = DiagnosticPipeline(domain="ecosystem")._build_ecosystem_corpus("R835")
    second = DiagnosticPipeline(domain="ecosystem")._build_ecosystem_corpus("R835")
    assert first == second
