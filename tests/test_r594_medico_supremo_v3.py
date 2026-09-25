"""
Testes R-205.v3 / ciclo R594 — Integração do skill v3.0 "conselho-longitudinal"
exportado do plugin Médico Virtual Supremo (gpt-6ceee9ff15bc7f1a4007d43b810f1876,
v0.4.0) ao Core.

Valida:
- SKILL.md v3.0 presente em skills/medico_virtual_supremo/SKILL.md (fonte de
  verdade das instruções, com rodapé obrigatório e anti-overclaim).
- 7 referências instrucionais em skills/medico_virtual_supremo/references/.
- API programática list_references()/load_reference() (fail-closed).
- Release v3.0 exposto sem quebrar get_version()==2.0.0 (compat R205).
- Paridade com o manifesto exportado plugin.json (name/version/author).
Regras SDD/TDD estritas: RED antes da integração, GREEN depois.
"""
import json
from pathlib import Path

import pytest

ECOSYSTEM = Path(__file__).resolve().parents[1]
SKILL_DIR = ECOSYSTEM / "skills" / "medico_virtual_supremo"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES_DIR = SKILL_DIR / "references"
PLUGIN_JSON = ECOSYSTEM / "medicos" / "plugin.json"

REFERENCE_NAMES = [
    "SKILL_CHATGPT",
    "diagnostico-diferencial",
    "fontes-diagnosticas",
    "conselho-multiespecialidades",
    "anamnese-longitudinal",
    "opcoes-terapeuticas",
    "integracoes-referencias",
]


# --------------------------------------------------------------------------
# 1. SKILL.md v3.0 integrado
# --------------------------------------------------------------------------
class TestSkillMdV3:
    def test_skill_md_presente(self):
        assert SKILL_MD.exists(), f"SKILL.md v3.0 não copiado para {SKILL_MD}"
        content = SKILL_MD.read_text(encoding="utf-8")
        assert len(content) > 5000

    def test_frontmatter_e_versao_v3(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "description:" in content
        assert "Médico Virtual Supremo" in content
        assert "3.0" in content
        assert "conselho-longitudinal" in content

    def test_secoes_novas_v3_presentes(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        for marker in [
            "Conselho clínico multiespecialidades",
            "Anamnese longitudinal e reconstrução reversa",
            "Possibilidades terapêuticas",
            "Arquitetura, ferramentas e dados externos",
            "Auditoria final",
            "Rodapé obrigatório",
            "fail-closed",
        ]:
            assert marker in content, f"marcador v3.0 ausente: {marker!r}"

    def test_rodape_obrigatorio_anti_overclaim(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "não substitui avaliação profissional" in content
        assert "revisão humana" in content
        assert "Médico Virtual Supremo v3.0" in content
        assert "instagram.com/marceloclaro.geomaker" in content

    def test_limites_seguranca(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "SAMU 192" in content
        assert "Nunca prescreva" in content
        assert "LGPD" in content


# --------------------------------------------------------------------------
# 2. Referências instrucionais v3.0
# --------------------------------------------------------------------------
class TestReferencesV3:
    @pytest.mark.parametrize("ref_name", REFERENCE_NAMES)
    def test_referencia_existe_e_nao_vazia(self, ref_name):
        path = REFERENCES_DIR / f"{ref_name}.md"
        assert path.exists(), f"referência ausente: {ref_name}"
        content = path.read_text(encoding="utf-8")
        assert len(content.strip()) >= 300, f"referência vazia/curta: {ref_name}"

    def test_todas_referencias_listadas(self):
        files = sorted(p.name for p in REFERENCES_DIR.glob("*.md"))
        expected = sorted(f"{n}.md" for n in REFERENCE_NAMES)
        assert files == expected, f"esperado {expected}, obteve {files}"


# --------------------------------------------------------------------------
# 3. API programática (list_references / load_reference) — fail-closed
# --------------------------------------------------------------------------
class TestReferenceApi:
    def test_list_references_tem_7(self):
        from skills.medico_virtual_supremo.skill import list_references

        refs = list_references()
        assert isinstance(refs, list)
        assert len(refs) == len(REFERENCE_NAMES)
        assert set(refs) == set(REFERENCE_NAMES)

    def test_load_reference_conteudo(self):
        from skills.medico_virtual_supremo.skill import load_reference

        content = load_reference("conselho-multiespecialidades")
        assert content is not None
        assert "conselho" in content.lower()
        assert len(content) > 500

    def test_load_reference_anonima_fail_closed(self):
        from skills.medico_virtual_supremo.skill import load_reference

        assert load_reference("inexistente") is None
        assert load_reference("") is None

    def test_load_reference_aceita_sufixo(self):
        from skills.medico_virtual_supremo.skill import load_reference

        assert load_reference("opcoes-terapeuticas.md") is not None


# --------------------------------------------------------------------------
# 4. Release v3.0 exposto + compatibilidade R205
# --------------------------------------------------------------------------
class TestReleaseCompat:
    def test_skill_v3_release(self):
        from skills.medico_virtual_supremo.skill import SKILL_V3_RELEASE

        assert SKILL_V3_RELEASE == "3.0-conselho-longitudinal"

    def test_get_version_continua_2_0_0(self):
        from skills.medico_virtual_supremo.skill import get_version

        assert get_version() == "2.0.0"  # compat: test_r205 linha 477

    def test_analisar_smoke_estrutura_v3(self):
        from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill

        r = MedicoVirtualSupremoSkill().analisar(
            "patient_education", "O que é hipertensão?"
        )
        corpo = r.get("resposta_medico_virtual_supremo", {})
        for campo in [
            "meta", "safety", "data_quality", "clinical_summary",
            "assessment", "plan_for_human_review", "evidence", "audit",
            "mandatory_footer",
        ]:
            assert campo in corpo, f"campo v3.0 ausente na resposta: {campo}"
        assert corpo["audit"].get("status") in (
            "aprovado", "bloqueado", "inconclusivo", "requer_escalonamento",
        )


# --------------------------------------------------------------------------
# 5. Paridade com o manifesto do plugin exportado
# --------------------------------------------------------------------------
class TestPluginManifestParity:
    def test_plugin_json_parity(self):
        data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        assert data["name"] == "gpt-6ceee9ff15bc7f1a4007d43b810f1876"
        assert data["version"] == "0.4.0"
        assert data["author"]["name"] == "MARCELO CLARO LARANJEIRA"
        assert "conselho multiespecialidades" in data["description"]
        interface = data["extensions"]["com.openai"]["interface"]
        assert interface["displayName"] == "Médico Virtual Supremo"

    def test_codigo_plugin_correspondente(self):
        import skills.medico_virtual_supremo.skill as skill_mod

        assert skill_mod.PLUGIN_SOURCE_VERSION == "0.4.0"
        assert skill_mod.PLUGIN_SOURCE_ID == "gpt-6ceee9ff15bc7f1a4007d43b810f1876"

    def test_codigo_nao_instala_motores_externos(self):
        # anti-overclaim: a skill não deve prometer MiroFish/Neo4j executados
        import skills.medico_virtual_supremo.skill as skill_mod

        assert "não instala" in skill_mod.PLUGIN_SOURCE_NOTE
        assert "Neo4j" in skill_mod.PLUGIN_SOURCE_NOTE or "MiroFish" in skill_mod.PLUGIN_SOURCE_NOTE