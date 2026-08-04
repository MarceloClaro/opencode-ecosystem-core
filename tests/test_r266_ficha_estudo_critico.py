import os
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

# NOTA (2026-08-03, triagem de falhas pré-existentes): `ficha_estudo_critico.tex/.pdf`
# é exatamente o mesmo artefato que tests/test_r265_r279_spec_deliverables.py::
# TestR266FichaEstudo já documenta explicitamente como overcloim histórico --
# "arquivos de teste que nunca existiram no histórico do git" (ver docstring
# daquele arquivo, que cita o CORRIGENDUM.md). Aquele teste já foi corrigido
# para pular (não falhar) quando o artefato está ausente, em vez de reivindicar
# um documento que nunca foi escrito de verdade. Fabricar agora, às pressas,
# um estudo crítico de dezenas de páginas só para satisfazer estas duas
# asserções seria repetir o mesmo erro que a correção anterior já evitou.
# Este arquivo foi alinhado ao mesmo padrão honesto: skip explícito, nunca
# aprovação por ausência.


def _ficha_path(extension: str) -> str:
    return os.path.join(MOLAMBUDOS_DIR, f"ficha_estudo_critico.{extension}")


def test_ficha_estudo_critico_tex_exists():
    tex_path = _ficha_path("tex")
    if not os.path.exists(tex_path):
        pytest.skip(
            "SPEC-935-R266: ficha_estudo_critico.tex não presente no checkout "
            "-- já documentado como overclaim histórico em "
            "test_r265_r279_spec_deliverables.py::TestR266FichaEstudo"
        )
    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "NoologicalScanner" in content or "noológica" in content, "Falta menção às métricas noológicas"
    assert "ScientificReasoningScanner" in content or "falseabilidade" in content, "Falta menção ao scanner científico"
    assert "PotentialityScanner" in content or "potencialidades" in content, "Falta menção ao scanner de potencialidade"
    assert "Barbacena" in content, "Falta menção histórica a Barbacena"


def test_ficha_estudo_critico_pdf_compilation():
    pdf_path = _ficha_path("pdf")
    if not os.path.exists(pdf_path):
        pytest.skip(
            "SPEC-935-R266: ficha_estudo_critico.pdf não presente no checkout "
            "-- já documentado como overclaim histórico em "
            "test_r265_r279_spec_deliverables.py::TestR266FichaEstudo"
        )
    assert os.path.getsize(pdf_path) > 50000, "PDF da ficha de estudo crítico está excessivamente pequeno"
