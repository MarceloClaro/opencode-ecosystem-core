"""SPEC-935-R915 — atualização local do conector NotebookLM para 0.15.6.

Teste hermético: confere a pinagem declarada, a coerência dos recibos
publicados e, **somente se a distribuição estiver instalada no ambiente**,
a versão efetivamente presente. Nenhuma chamada de rede, nenhuma leitura de
notebooks, nenhuma divulgação de credencial ou título.

A separação é explícita: o recibo prova o que foi executado no ciclo R915;
o teste não afirma que a versão instalada hoje é a mesma, e não afirma
validação externa das operações Google.
"""

from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REQS = ROOT / "requirements-notebook.txt"
RUNTIME = ROOT / "docs/evidence/r915/runtime.json"
REGRESSION = ROOT / "docs/evidence/r915/regression.txt"
VERIFICATION = ROOT / "docs/verification-notebooklm-update-r915.json"
SPEC = ROOT / "specs/SPEC-935-R915-atualizacao-notebooklm.md"

PACOTE = "notebooklm-mcp-cli"
VERSAO_ALVO = "0.15.6"
VERSAO_ANTERIOR = "0.11.6"


def _pins() -> dict[str, str]:
    pins: dict[str, str] = {}
    for linha in REQS.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "==" not in linha:
            continue
        nome, versao = linha.split("==", 1)
        pins[nome.strip()] = versao.strip()
    return pins


def test_requisitos_declaram_a_distribuicao_alvo_e_as_dependencias_mantidas():
    pins = _pins()
    assert pins.get(PACOTE) == VERSAO_ALVO
    assert pins.get("fastmcp") == "3.2.3"
    assert pins.get("mcp") == "1.28.1"


def test_spec_declara_o_arquivo_de_teste_vinculado():
    texto = SPEC.read_text(encoding="utf-8")
    assert "test_file: tests/test_r915_atualizacao_notebooklm.py" in texto


def test_recibo_de_runtime_declara_a_migracao_com_limites():
    dados = json.loads(RUNTIME.read_text(encoding="utf-8"))
    assert dados["round_id"] == "R915"
    assert dados["version_before"] == VERSAO_ANTERIOR
    assert dados["version_after"] == VERSAO_ALVO
    assert dados["package_source"].endswith("/0.15.6/")
    assert dados["catalog"]["mcp_tool_count"] > 0
    assert dados["catalog"]["cli_entry_count"] > 0
    # O recibo não podeograduar validação externa.
    assert "external_validation" not in dados


def test_recibo_de_verificacao_tem_pip_check_e_instalacao_registrada():
    dados = json.loads(VERIFICATION.read_text(encoding="utf-8"))
    assert dados["round_id"] == "R915"
    assert dados["package_version"] == VERSAO_ALVO
    assert dados["pip_check"]["returncode"] == 0
    assert "No broken requirements found" in dados["pip_check"]["stdout"]
    mudancas = dados["changed_distributions"]
    assert mudancas[PACOTE]["before"] == VERSAO_ANTERIOR
    assert mudancas[PACOTE]["after"] == VERSAO_ALVO
    nomes = {item["name"] for item in dados["installation"]}
    assert PACOTE in nomes
    for item in dados["installation"]:
        assert re.fullmatch(r"[0-9a-f]{64}", item["sha256"])


def test_regressao_registrada_foi_verde_sem_erro():
    texto = REGRESSION.read_text(encoding="utf-8")
    assert re.search(r"\d+ passed", texto)
    assert " failed" not in texto
    assert "error" not in texto.lower()


def test_versao_instalada_confere_com_a_pinagem_quando_presente():
    """Se a distribuição estiver instalada, a versão deve bater com o pin.

    Ausência da distribuição no ambiente não é falha: é apenas ausência de
    observação local. O teste não instala, não atualiza e não usa rede.
    """
    try:
        instalada = importlib.metadata.version(PACOTE)
    except importlib.metadata.PackageNotFoundError:
        return
    assert instalada == VERSAO_ALVO
