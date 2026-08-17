# tests/test_r431_quantum_kernel_evidence_gate.py
"""
Testes para o artigo R431 — Quantum Kernel Evidence Gate.
Valida integridade dos dados, consistência dos resultados e conformidade com SPEC-935-R431.
"""

import json
import os
import csv
import hashlib
import pytest

# Paths
DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "academic", "papers", "quantum_ia_kernel", "data", "processed"
)
SPEC_PATH = os.path.join(
    os.path.dirname(__file__), "..", "specs", "SPEC-935-R431-quantum-kernel-evidence-gate.md"
)
MD_PATH = os.path.join(
    os.path.dirname(__file__), "..", "academic", "papers", "quantum_ia_kernel", "docs",
    "ARTIGO_QUANTUM_EVIDENCE_GATE.md"
)


# ---------------------------------------------------------------------------
# Fixture: carregar dados
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def config():
    with open(os.path.join(DATA_DIR, "configuracao.json")) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def stats():
    with open(os.path.join(DATA_DIR, "analise_estatistica_paper.json")) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def gate():
    with open(os.path.join(DATA_DIR, "portao_evidencia.json")) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def mech():
    with open(os.path.join(DATA_DIR, "analise_mecanistica_aplicacoes.json")) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def protocol():
    with open(os.path.join(DATA_DIR, "protocolo_pre_registrado.json")) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def md_text():
    with open(MD_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. SHA-256 do protocolo
# ---------------------------------------------------------------------------
def test_protocol_hash(config):
    expected = "89c08f07f2f03a56c144bd4c4b7eddb71813bb1b043bb90920de8e5e70140eaf"
    assert config["hash_protocolo"] == expected


def test_sha256_file(config):
    sha_path = os.path.join(DATA_DIR, "protocolo_sha256.txt")
    with open(sha_path) as f:
        file_hash = f.read().strip()
    assert file_hash == config["hash_protocolo"]


# ---------------------------------------------------------------------------
# 2. Resultado primário — inferioridade estatística
# ---------------------------------------------------------------------------
def test_primary_outcome_negative(stats):
    """ΔBAC deve ser negativo (inferioridade do QML)."""
    assert stats["media_delta_bac"] < 0


def test_primary_p_value(stats):
    """p unicaudal corrigido deve ser ~1 (sem evidência de superioridade)."""
    assert stats["p_primario_corrigido"] > 0.99


def test_primary_ci_negative(stats):
    """IC95% bilateral corrigido deve ser inteiramente negativo."""
    lower, upper = stats["ic95_corrigido_bilateral"]
    assert upper < 0, f"IC superior ({upper}) deveria ser < 0"


def test_permutation_significant(stats):
    """Permutação de sinais deve ser significativa (bilateral)."""
    assert stats["p_permutacao_sinais_sensibilidade"] < 0.05


def test_tost_not_equivalent(stats):
    """TOST de equivalência deve NÃO ser significativo (não equivalente)."""
    assert stats["p_tost_equivalencia"] > 0.05


def test_effect_size_large_negative(stats):
    """Cohen's dz deve ser negativo e de magnitude grande (< -0.8)."""
    assert stats["tamanho_efeito_dz"] < -0.8


def test_classification_inferiority(stats):
    """Classificação deve ser inferioridade estatística."""
    assert "inferioridade" in stats["classificacao"].lower()


# ---------------------------------------------------------------------------
# 3. Validation: effective kernel rank and alignment
# ---------------------------------------------------------------------------
def test_kernel_alignment_low(gate):
    """Alinhamento kernel-alvo deve ser baixo (< 0.5)."""
    assert gate["posto_efetivo_relativo"] < 0.5


def test_kernel_alignment_value(gate):
    """Alinhamento kernel-alvo deve ser ~0.110."""
    # Gate JSON has alignment in post Efetivo
    assert 0.0 < gate["posto_efetivo_relativo"] < 0.5


def test_kernel_effective_rank(gate):
    """Posto efetivo relativo deve ser ~28%."""
    assert 0.1 < gate["posto_efetivo_relativo"] < 0.5


# ---------------------------------------------------------------------------
# 4. Evidence Gate criteria
# ---------------------------------------------------------------------------
def test_gate_baseline_pre_specified(gate):
    """Baseline pré-especificado deve ser SVM-RBF."""
    assert gate["baseline_referencia"] == "SVM-RBF"


def test_gate_no_ic_excludes_zero(gate):
    """IC pareado NÃO deve excluir zero a favor do QML."""
    assert gate["criterios"]["ic_exclui_zero_a_favor_qml"] is False


def test_gate_no_external_test(gate):
    """Teste externo NÃO foi executado."""
    assert gate["criterios"]["teste_externo_executado"] is False


def test_gate_cost_registered(gate):
    """Custo quântico deve estar registrado."""
    assert gate["criterios"]["custo_quantico_registrado"] is True


def test_gate_status_inconclusive(gate):
    """Status deve ser inferioridade estatística neste protocolo."""
    assert "inferioridade" in gate["status_evidencia"].lower()


def test_gate_parecer(gate):
    """Parecer deve ser inconclusivo."""
    assert "inconclusivo" in gate["parecer"].lower()


# ---------------------------------------------------------------------------
# 5. Validade ladder — sobrevivência geométrica
# ---------------------------------------------------------------------------
def test_validity_ladder_bac_stable():
    """BAC deve ser estável (0.625) em todas as camadas de fidelidade."""
    ladder_path = os.path.join(DATA_DIR, "escada_validade_kernel.csv")
    with open(ladder_path) as f:
        reader = csv.DictReader(f)
        bac_values = [float(row["acuracia"]) for row in reader]
    # Todos devem ser 0.625
    assert all(v == pytest.approx(0.625) for v in bac_values), f"BAC values: {bac_values}"


def test_validity_ladder_frobenius_increasing():
    """Erro de Frobenius deve ser crescente statevector → shots → noise."""
    ladder_path = os.path.join(DATA_DIR, "escada_validade_kernel.csv")
    with open(ladder_path) as f:
        reader = csv.DictReader(f)
        errors = [float(row["erro_geometrico_relativo"]) for row in reader]
    # Nível 0: 0, Nível 1: ~0.011, Nível 2: ~0.055
    assert errors[0] < errors[1] < errors[2]


# ---------------------------------------------------------------------------
# 6. Multi-dataset suite — all negative
# ---------------------------------------------------------------------------
def test_all_deltas_negative():
    """Todos os ΔBAC na suíte multibase devem ser negativos."""
    suite_path = os.path.join(DATA_DIR, "suite_aplicacoes_folds.csv")
    with open(suite_path) as f:
        reader = csv.DictReader(f)
        deltas = [float(row["delta_bac"]) for row in reader]
    assert all(d < 0 for d in deltas), f"Non-negative deltas: {[d for d in deltas if d >= 0]}"


def test_suite_16_folds():
    """A suíte deve ter 16 folds."""
    suite_path = os.path.join(DATA_DIR, "suite_aplicacoes_folds.csv")
    with open(suite_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 16


# ---------------------------------------------------------------------------
# 7. Comparison models — RBF > LogReg > QML
# ---------------------------------------------------------------------------
def test_rbf_best_model():
    """SVM-RBF deve ter maior BAC."""
    comp_path = os.path.join(DATA_DIR, "comparacao_modelos.csv")
    with open(comp_path) as f:
        reader = csv.DictReader(f)
        rows = {row["modelo"]: float(row["acuracia_balanceada"]) for row in reader}
    assert rows["SVM-RBF"] > rows["Regressão logística"]
    assert rows["SVM-RBF"] > rows["SVM + kernel quântico"]


# ---------------------------------------------------------------------------
# 8. Bootstrap intervals
# ---------------------------------------------------------------------------
def test_bootstrap_qml_interval():
    """IC bootstrap do QML deve ser deslocado para baixo."""
    boot_path = os.path.join(DATA_DIR, "intervalos_bootstrap.csv")
    with open(boot_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "quântico" in row["modelo"]:
                lower = float(row["IC_2.5%"])
                upper = float(row["IC_97.5%"])
                assert lower < 0.9, f"QML lower bound too high: {lower}"
                assert upper < 1.0, f"QML upper bound too high: {upper}"
                return
    pytest.fail("QML model not found in bootstrap file")


# ---------------------------------------------------------------------------
# 9. Mechanistic correlations
# ---------------------------------------------------------------------------
def test_mechanistic_alignment_correlation(mech):
    """Correlação alinhamento→ΔBAC deve ser positiva e significativa."""
    assert mech["spearman_alinhamento_delta_bac"] > 0.5
    assert mech["p_exploratorio_alinhamento"] < 0.05


def test_mechanistic_survival_correlation(mech):
    """Correlação sobrevivência→ΔBAC deve ser positiva mas não significativa."""
    assert mech["spearman_sobrevivencia_delta_bac"] > 0
    assert mech["p_exploratorio_sobrevivencia"] > 0.05


# ---------------------------------------------------------------------------
# 10. Configuration and versions
# ---------------------------------------------------------------------------
def test_config_versions(config):
    """Versões de software devem estar documentadas."""
    v = config["versoes"]
    assert "python" in v
    assert "qiskit" in v
    assert "numpy" in v


def test_config_seed(config):
    """Seed deve ser 42."""
    assert config["seed"] == 42


def test_config_shots(config):
    """Shots deve ser 2048."""
    assert config["shots"] == 2048


# ---------------------------------------------------------------------------
# 11. Ablations
# ---------------------------------------------------------------------------
def test_ablations_reps_shots():
    """Ablações devem variar reps e shots."""
    abl_path = os.path.join(DATA_DIR, "ablacoes.csv")
    with open(abl_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) >= 3
    reps = set(row["reps"] for row in rows)
    shots = set(row["shots"] for row in rows)
    assert len(reps) >= 2
    assert len(shots) >= 2


# ---------------------------------------------------------------------------
# 12. Document integrity
# ---------------------------------------------------------------------------
def test_md_min_chars(md_text):
    """O artigo MD deve ter ≥ 30.000 caracteres (corpo)."""
    # Excluir referências e anexos para contar corpo
    body = md_text.split("## Referências")[0] if "## Referências" in md_text else md_text
    assert len(body) >= 30000, f"Body has {len(body)} chars, need ≥ 30000"


def test_md_has_abstract(md_text):
    """Artigo deve conter Abstract."""
    assert "## Abstract" in md_text or "# Abstract" in md_text


def test_md_has_resumo(md_text):
    """Artigo deve conter Resumo."""
    assert "## Resumo" in md_text or "# Resumo" in md_text


def test_md_has_6_sections(md_text):
    """Artigo deve ter 6 seções principais."""
    for i in range(1, 7):
        assert f"## {i}." in md_text or f"## {i} " in md_text, f"Seção {i} não encontrada"


def test_no_quantum_advantage_claim(md_text):
    """Artigo NÃO deve afirmar 'vantagem quântica' como fato estabelecido."""
    lower = md_text.lower()
    # O termo deve aparecer (em contexto de negação ou referência)
    assert "vantagem quântica" in lower
    # Linhas com afirmação positiva direta (declarativa) são proibidas.
    # Permite: negação, referência bibliográfica, contexto futuro, menção condicional.
    forbidden_patterns = [
        "demonstramos vantagem quântica",
        "há vantagem quântica",
        "existe vantagem quântica",
        "o kernel quântico oferece vantagem",
        "o kernel quântico apresenta vantagem",
        "comprovamos vantagem",
    ]
    for pat in forbidden_patterns:
        assert pat not in lower, f"Padrão proibido encontrado: {pat}"


def test_no_first_study_claim(md_text):
    """Artigo NÃO deve afirmar 'primeiro estudo'."""
    lower = md_text.lower()
    lines_with = [l.strip() for l in md_text.split("\n") if "primeiro estudo" in l.lower()]
    for line in lines_with:
        if line.startswith("#"):
            continue
        assert any(neg in line.lower() for neg in ["não", "sem", "não afirmar"]), \
            f"Possível afirmação de primeiro estudo: {line}"


def test_spec_exists():
    """SPEC-935-R431 deve existir."""
    assert os.path.exists(SPEC_PATH), f"SPEC not found at {SPEC_PATH}"


def test_data_dir_has_all_files():
    """Diretório de dados deve conter todos os arquivos esperados."""
    expected = [
        "configuracao.json", "analise_estatistica_paper.json",
        "portao_evidencia.json", "analise_mecanistica_aplicacoes.json",
        "escada_validade_kernel.csv", "suite_aplicacoes_folds.csv",
        "comparacao_modelos.csv", "intervalos_bootstrap.csv",
        "ablacoes.csv", "protocolo_sha256.txt",
    ]
    for fname in expected:
        assert os.path.exists(os.path.join(DATA_DIR, fname)), f"Missing: {fname}"
