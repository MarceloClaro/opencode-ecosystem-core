# -*- coding: utf-8 -*-
"""Testes da Fase 3 da SPEC-935-R471 (subspec SPEC-935-R479):
M4 — Workbench de supervisão (DeepSeekGUI) e
M5 — Modelos pequenos reprodutíveis (minimind).

Cobertura: CA5 (workbench aponta para workspaces do Core; licenças PolyForm
Perimeter vs MIT registradas em THIRD_PARTY_NOTICES), CA6 (currículo minimind
com plano determinístico e relatório de reprodutibilidade; limitação de
hardware documentada explicitamente quando não há GPU), CA8 (hermético),
invariantes 2 (opt-in), 5 (sem credenciais), 8 (anti-overclaim).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# M4 — Workbench de supervisão (DeepSeekGUI)
# ---------------------------------------------------------------------------

class TestDeepSeekGUIWorkbench:
    def test_inactive_without_config(self, monkeypatch) -> None:
        """Invariante 2: ausência de configuração equivale a inatividade."""
        from workbench.deepseek_gui import DeepSeekGUIWorkbench

        monkeypatch.delenv("DEEPSEEK_GUI_ENABLED", raising=False)
        monkeypatch.delenv("DEEPSEEK_GUI_WORKSPACE", raising=False)
        wb = DeepSeekGUIWorkbench(repo_root=str(ROOT))
        assert wb.active() is False

    def test_active_with_env(self, monkeypatch) -> None:
        from workbench.deepseek_gui import DeepSeekGUIWorkbench

        monkeypatch.setenv("DEEPSEEK_GUI_WORKSPACE", "academic")
        wb = DeepSeekGUIWorkbench(repo_root=str(ROOT), enabled_by_env=True)
        assert wb.active() is True

    def test_validates_core_workspace(self, monkeypatch) -> None:
        from workbench.deepseek_gui import DeepSeekGUIWorkbench

        monkeypatch.setenv("DEEPSEEK_GUI_WORKSPACE", "academic")
        wb = DeepSeekGUIWorkbench(repo_root=str(ROOT), enabled_by_env=True)
        assert wb.validate_workspace("academic") is True
        assert wb.validate_workspace("pesquisa") is True
        assert wb.validate_workspace("publications") is True

    def test_rejects_paths_outside_core(self, monkeypatch) -> None:
        from workbench.deepseek_gui import DeepSeekGUIWorkbench

        wb = DeepSeekGUIWorkbench(repo_root=str(ROOT), enabled_by_env=True)
        assert wb.validate_workspace("/etc") is False
        assert wb.validate_workspace("../..") is False
        assert wb.validate_workspace("/root") is False
        assert wb.validate_workspace("") is False

    def test_launch_config_receipt_carries_license_and_limitation(self, monkeypatch) -> None:
        from workbench.deepseek_gui import DeepSeekGUIWorkbench

        monkeypatch.setenv("DEEPSEEK_GUI_WORKSPACE", "academic")
        wb = DeepSeekGUIWorkbench(repo_root=str(ROOT), enabled_by_env=True)
        cfg = wb.launch_config()
        assert cfg["workspace"] == "academic"
        assert cfg["license_product"] == "PolyForm Perimeter 1.0.1"
        assert cfg["license_upstream"] == "MIT"
        assert "redistribuição competitiva" in cfg["limitation"].lower()
        # Invariante 5: recibo sem credenciais
        joined = " ".join(str(v) for v in cfg.values()).lower()
        assert "token" not in joined and "api_key" not in joined

    def test_harness_reference_resolves_to_real_module(self) -> None:
        """O workbench referencia o harness realmente presente no Core."""
        from workbench.deepseek_gui import HARNESS_MODULE

        mod = __import__(HARNESS_MODULE, fromlist=["bridged"])
        assert hasattr(mod, "bridge") or hasattr(mod, "reasoning_loop")


# ---------------------------------------------------------------------------
# M5 — Modelos pequenos reprodutíveis (minimind)
# ---------------------------------------------------------------------------

class TestMiniMindCurriculum:
    def test_stages_in_canonical_order(self) -> None:
        from model_lab.curriculum import MINIMIND_STAGES

        assert MINIMIND_STAGES == (
            "tokenizer", "pretrain", "sft", "rlhf", "dpo", "moe", "distill", "quant",
        )

    def test_plan_is_deterministic_with_seed(self) -> None:
        from model_lab.curriculum import MiniMindCurriculum

        plan1 = MiniMindCurriculum().plan(seed=42)
        plan2 = MiniMindCurriculum().plan(seed=42)
        assert plan1 == plan2
        assert plan1[0]["stage"] == "tokenizer"
        assert plan1[-1]["stage"] == "quant"

    def test_plan_varies_with_seed(self) -> None:
        from model_lab.curriculum import MiniMindCurriculum

        plan1 = MiniMindCurriculum().plan(seed=1)
        plan2 = MiniMindCurriculum().plan(seed=2)
        assert plan1 != plan2

    def test_curriculum_exposes_model_config(self) -> None:
        from model_lab.curriculum import MiniMindCurriculum

        cfg = MiniMindCurriculum().model_config
        assert cfg["params_millions"] == 64
        assert cfg["name"] == "minimind-64M"


class TestHardwareProbe:
    def test_probe_returns_device_and_note(self) -> None:
        from model_lab.hardware import HardwareProbe

        probe = HardwareProbe(device_factory=lambda: "none")
        info = probe.probe()
        assert info["device"] in ("cuda", "cpu", "none")
        assert info["note"]

    def test_limitation_documented_without_gpu(self) -> None:
        from model_lab.hardware import HardwareProbe

        probe = HardwareProbe(device_factory=lambda: "none")
        info = probe.probe()
        assert "limitação" in info["limitation"].lower()

    def test_gpu_note_mentions_acceleration(self) -> None:
        from model_lab.hardware import HardwareProbe

        probe = HardwareProbe(device_factory=lambda: "cuda")
        info = probe.probe()
        assert "cuda" in info["note"].lower()


class TestMiniMindBenchmark:
    def test_reproducibility_report_deterministic(self) -> None:
        from model_lab.benchmark import MiniMindBenchmark

        r1 = MiniMindBenchmark(seed=7, device="none").run(steps=10)
        r2 = MiniMindBenchmark(seed=7, device="none").run(steps=10)
        assert r1.as_dict() == r2.as_dict()
        assert r1.seed == 7
        assert len(r1.losses) == 10

    def test_different_seed_different_curve(self) -> None:
        from model_lab.benchmark import MiniMindBenchmark

        r1 = MiniMindBenchmark(seed=1, device="none").run(steps=10)
        r2 = MiniMindBenchmark(seed=99, device="none").run(steps=10)
        assert r1.losses != r2.losses

    def test_report_marks_hardware_limitation_without_gpu(self) -> None:
        """CA6: sem GPU, a limitação de hardware é documentada explicitamente."""
        from model_lab.benchmark import MiniMindBenchmark

        report = MiniMindBenchmark(seed=7, device="none").run(steps=5)
        assert report.hardware_limitation is True
        assert report.reproducibility_note

    def test_report_no_overclaim(self) -> None:
        from model_lab.benchmark import MiniMindBenchmark

        report = MiniMindBenchmark(seed=7, device="none").run(steps=5)
        text = " ".join(report.as_dict().values())
        low = text.lower()
        for banned in ("superhuman", "verificado", "qualis a1", "superação"):
            assert banned not in low

    def test_monotonic_loss_trend_in_pretrain_stage(self) -> None:
        """Curva de pretrain simulada deve ser estritamente decrescente."""
        from model_lab.benchmark import MiniMindBenchmark

        report = MiniMindBenchmark(seed=7, device="none").run(steps=20)
        assert all(report.losses[i] > report.losses[i + 1] for i in range(len(report.losses) - 1))


# ---------------------------------------------------------------------------
# Licenças em THIRD_PARTY_NOTICES (CA5)
# ---------------------------------------------------------------------------

class TestThirdPartyNotices:
    def test_notices_file_exists_and_covers_fase3(self) -> None:
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        assert "PolyForm Perimeter" in notices
        assert "minimind" in notices
        assert "Apache-2.0" in notices
        assert "DeepSeekGUI" in notices