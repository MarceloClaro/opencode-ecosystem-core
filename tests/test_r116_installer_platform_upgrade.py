# -*- coding: utf-8 -*-
"""
Testes R116 — Instalação multiplataforma, ícone próprio, integração
Claude CLI e manual/helpdesk do marceloclaro (TDD: RED -> GREEN -> REFACTOR)
=============================================================================
Testa: OpenCodeCLIIntegration (bug do provision.sh), AntigravityBridge
com binário correto (agy), correção de descrição do catálogo, doctor com
check de CLIs externas, helpdesk mapeando pendências para sugestões,
geração do ícone, sintaxe dos scripts de instalação/desinstalação, e
presença/conteúdo de MANUAL.md/AGENTS.md/installer/README.md.

Requisitos (SPEC-935-R116):
  - OpenCodeCLIIntegration.generate_config() funciona (bug real do
    provision.sh, que já chamava essa API antes dela existir)
  - AntigravityBridge aponta para "agy" por padrão (nome real do binário)
  - Catálogo de agentes não trunca descrições em "<!--"
  - doctor() inclui o check external_clis
  - helpdesk() mapeia cada check warn/fail para uma sugestão em linguagem simples
  - assets/generate_icon.py produz icon.png/icon.ico válidos
  - Scripts de instalação/desinstalação (Windows/Linux/macOS) têm sintaxe válida
  - MANUAL.md, AGENTS.md, installer/README.md existem com conteúdo mínimo
"""

import copy
import os
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(autouse=True)
def _isolate_metacognitive_memory():
    """Ver justificativa em tests/test_r108_marceloclaro_scientific_fusion.py."""
    from mci.metabus import metabus
    from sdd.loop_spec import loop_spec_registry

    memory_snapshot = (
        copy.deepcopy(metabus.memory.episodic),
        copy.deepcopy(metabus.memory.semantic),
        copy.deepcopy(metabus.memory.confidence_ledger),
    )
    loops_snapshot = dict(loop_spec_registry.loops)
    yield
    metabus.memory.episodic, metabus.memory.semantic, metabus.memory.confidence_ledger = memory_snapshot
    metabus.memory._save()
    loop_spec_registry.loops = loops_snapshot


# ── 1. OpenCodeCLIIntegration (bug do provision.sh) ──────────────────

class TestOpenCodeCLIIntegration:
    def test_generate_config_writes_valid_opencode_json(self, tmp_path):
        from integrations.opencode_cli import OpenCodeCLIIntegration
        import json

        integ = OpenCodeCLIIntegration(str(tmp_path))
        # generate_config() grava sempre em CONFIG_PATH real (raiz do repo,
        # ver docstring da classe) — aqui só validamos que roda sem erro e
        # que o resultado no repo real continua consistente.
        path = integ.generate_config()
        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        assert "marceloclaro" in config["agent"]
        assert config["agent"]["marceloclaro"]["mode"] == "primary"

    def test_check_returns_true_for_valid_config(self):
        from integrations.opencode_cli import OpenCodeCLIIntegration
        integ = OpenCodeCLIIntegration(REPO_ROOT)
        assert integ.check() is True


# ── 2. AntigravityBridge aponta para o binário real ──────────────────

class TestAntigravityBridgeBinaryName:
    def test_default_cli_command_is_agy_not_antigravity(self):
        from integrations.antigravity.bridge import AntigravityBridge
        bridge = AntigravityBridge()
        assert bridge.cli_command == "agy"
        assert bridge.cli_command != "antigravity"

    def test_custom_cli_command_still_configurable(self):
        from integrations.antigravity.bridge import AntigravityBridge
        bridge = AntigravityBridge(cli_command="algum-outro-binario-inexistente")
        assert bridge.cli_command == "algum-outro-binario-inexistente"
        assert bridge.available is False


# ── 3. Catálogo de agentes: descrição não trunca em "<!--" ───────────

class TestCatalogDescriptionBugFix:
    def test_no_definition_starts_with_html_comment(self):
        from marceloclaro.catalog_loader import load_catalog_definitions
        defs = load_catalog_definitions()
        bad = [d for d in defs if d["description"].strip().startswith("<!--")]
        assert bad == [], f"{len(bad)} agente(s) ainda com descrição truncada em '<!--': {[d['agent_id'] for d in bad]}"

    def test_prefers_frontmatter_description_field(self, tmp_path):
        from marceloclaro import catalog_loader

        sample_dir = tmp_path / "catalog"
        sample_dir.mkdir()
        (sample_dir / "exemplo.md").write_text(
            "<!--\n  comentario de instrucao\n-->\n\n"
            "---\nname: exemplo\ndescription: Descricao autoral vinda do frontmatter\n---\n\n"
            "# Titulo\n\nTexto do corpo que nao deveria ser usado como descricao.\n",
            encoding="utf-8",
        )
        defs = catalog_loader.load_catalog_definitions(catalog_dir=str(sample_dir))
        assert len(defs) == 1
        assert defs[0]["description"] == "Descricao autoral vinda do frontmatter"


# ── 4. doctor(): check de CLIs externas ──────────────────────────────

class TestDoctorExternalClis:
    def test_check_external_clis_reports_warn_not_fail_when_missing(self, monkeypatch):
        from marceloclaro import doctor as doctor_mod
        monkeypatch.setattr(doctor_mod.shutil, "which", lambda name: None)
        check = doctor_mod._check_external_clis()
        assert check.status == "warn"  # nunca fail — CLIs sao opcionais
        n = len(doctor_mod.EXTERNAL_CLIS)
        assert f"{n}/{n}" in check.detail  # R120 adicionou scihub-cli (5ª CLI)

    def test_check_external_clis_reports_pass_when_all_present(self, monkeypatch):
        from marceloclaro import doctor as doctor_mod
        monkeypatch.setattr(doctor_mod.shutil, "which", lambda name: f"/usr/bin/{name}")
        check = doctor_mod._check_external_clis()
        assert check.status == "pass"

    def test_run_doctor_includes_external_clis_check(self):
        from marceloclaro.doctor import run_doctor
        report = run_doctor()
        names = [c["name"] for c in report["checks"]]
        assert "external_clis" in names


# ── 5. helpdesk(): sugestões em linguagem simples ────────────────────

class TestHelpdesk:
    def test_healthy_report_has_no_guidance(self, monkeypatch):
        from marceloclaro import helpdesk as helpdesk_mod

        monkeypatch.setattr(helpdesk_mod, "run_doctor", lambda: {
            "overall": "healthy", "checks": [{"name": "x", "status": "pass", "detail": "ok"}],
            "checks_total": 1, "checks_passed": 1, "checks_warned": 0, "checks_failed": 0,
            "duration_seconds": 0.0,
        })
        report = helpdesk_mod.run_helpdesk()
        assert report["overall"] == "healthy"
        assert report["guidance"] == []

    def test_warn_check_gets_a_suggestion(self, monkeypatch):
        from marceloclaro import helpdesk as helpdesk_mod

        monkeypatch.setattr(helpdesk_mod, "run_doctor", lambda: {
            "overall": "degraded",
            "checks": [{"name": "external_clis", "status": "warn", "detail": "claude ausente"}],
            "checks_total": 1, "checks_passed": 0, "checks_warned": 1, "checks_failed": 0,
            "duration_seconds": 0.0,
        })
        report = helpdesk_mod.run_helpdesk()
        assert len(report["guidance"]) == 1
        assert report["guidance"][0]["check"] == "external_clis"
        assert "claude ausente" in report["guidance"][0]["suggestion"]

    def test_orchestrator_helpdesk_method_delegates(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        report = orch.helpdesk()
        assert "overall" in report
        assert "guidance" in report
        assert "doctor_report" in report


# ── 6. Geração do ícone ──────────────────────────────────────────────

class TestIconGeneration:
    def test_icon_files_exist_and_are_non_trivial(self):
        png = os.path.join(REPO_ROOT, "assets", "icon.png")
        ico = os.path.join(REPO_ROOT, "assets", "icon.ico")
        assert os.path.exists(png) and os.path.getsize(png) > 500
        assert os.path.exists(ico) and os.path.getsize(ico) > 500

    def test_iconset_directory_has_required_sizes(self):
        iconset = os.path.join(REPO_ROOT, "assets", "icon.iconset")
        assert os.path.isdir(iconset)
        names = set(os.listdir(iconset))
        for required in ("icon_16x16.png", "icon_128x128.png", "icon_256x256.png"):
            assert required in names


# ── 7. Sintaxe dos scripts de instalação/desinstalação ───────────────

class TestInstallerScriptsSyntax:
    @pytest.mark.parametrize("script", [
        "installer/common/install_clis.sh",
        "installer/windows/provision.sh",
        "installer/linux/install.sh",
        "installer/linux/uninstall.sh",
        "installer/macos/install.sh",
        "installer/macos/uninstall.sh",
        "installer/macos/build_icns.sh",
    ])
    def test_bash_syntax_is_valid(self, script):
        path = os.path.join(REPO_ROOT, script)
        assert os.path.exists(path), f"{script} não encontrado"
        result = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
        assert result.returncode == 0, f"bash -n falhou para {script}: {result.stderr}"

    def test_provision_sh_references_all_four_clis(self):
        path = os.path.join(REPO_ROOT, "installer", "windows", "provision.sh")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for fn in ("install_opencode_cli", "install_antigravity_cli", "install_claude_code_cli", "install_ollama_cli"):
            assert fn in content

    def test_uninstall_scripts_require_confirmation_for_destructive_actions(self):
        ps1 = os.path.join(REPO_ROOT, "installer", "windows", "Uninstall-OpenCodeEcosystem.ps1")
        with open(ps1, "r", encoding="utf-8") as f:
            content = f.read()
        assert "CONFIRMO" in content
        assert "RemoveWSLDistro" in content
        assert "RemoveWSLFeature" in content


# ── 8. Documentação (MANUAL.md, AGENTS.md, installer/README.md) ──────

class TestDocumentation:
    @pytest.mark.parametrize("doc_path,min_size", [
        ("MANUAL.md", 500),
        ("AGENTS.md", 300),
        (os.path.join("installer", "README.md"), 300),
    ])
    def test_doc_exists_with_minimum_content(self, doc_path, min_size):
        path = os.path.join(REPO_ROOT, doc_path)
        assert os.path.exists(path), f"{doc_path} não encontrado"
        assert os.path.getsize(path) >= min_size

    def test_claude_md_mentions_doctor_and_helpdesk(self):
        path = os.path.join(REPO_ROOT, "CLAUDE.md")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "doctor" in content
        assert "helpdesk" in content
        # Preserva a instrucao de idioma original (nao deve ser removida)
        assert "português brasileiro" in content.lower() or "pt-br" in content.lower() or "pt-BR" in content

    def test_readme_no_longer_points_broken_guia_manual_link(self):
        path = os.path.join(REPO_ROOT, "README.md")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Guia Manual](ARCHITECTURE.md)" not in content
        assert "installer/README.md" in content

    def test_manual_md_covers_cli_menu_options(self):
        path = os.path.join(REPO_ROOT, "MANUAL.md")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for keyword in ("Blackboard", "doctor", "helpdesk", "Ajuda"):
            assert keyword in content


# ── 9. Desktop path detection (WSL) ───────────────────────────────────

class TestDesktopPathDetection:
    def test_is_wsl_detection_does_not_crash(self):
        from publishing.production import _is_wsl
        assert isinstance(_is_wsl(), bool)

    def test_detect_desktop_path_returns_nonempty_string(self):
        from publishing.production import _detect_desktop_path
        result = _detect_desktop_path()
        assert isinstance(result, str) and len(result) > 0

    def test_build_livro_tritemo_no_longer_hardcodes_marce_user(self):
        path = os.path.join(REPO_ROOT, "build_livro_tritemo.py")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert '"/mnt/c/Users/marce/Desktop"' not in content
