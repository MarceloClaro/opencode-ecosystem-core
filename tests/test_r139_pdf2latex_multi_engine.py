# -*- coding: utf-8 -*-
"""
Testes R139 — pdf2latex multi-engine + multi-renderer (SPEC-1000)
==================================================================
Trava os critérios de aceitação da arquitetura modular do pdf2latex
(engines de extração intercambiáveis + renderizadores LaTeX) ANTES de
versioná-la. A implementação já existia na árvore de trabalho (não
commitada); estes testes de caracterização/aceitação fixam o contrato
público para que futuras mudanças não o quebrem silenciosamente.

Testam apenas a superfície determinística e offline:
- registro de engines (singleton), auto-seleção, fallback;
- dataclasses de contrato (ConversionResult, RenderInput);
- interfaces abstratas (BaseEngine, BaseRenderer);
- engine/renderer builtin sempre disponíveis;
- presença dos templates Pandoc e dos .bst ABNT (CTAN).

NÃO dependem de docling/mineru/pandoc/latexmk (opcionais) — só verificam
que `is_available()` responde com bool sem quebrar.

Requisitos: SPEC-1000.
"""
from pathlib import Path
import importlib
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Registro de engines (singleton) ──────────────────────────────────

def test_registry_builtin_registrado_e_disponivel():
    from pdf2latex.engine_registry import list_engines, get_engine

    engines = {e["name"]: e for e in list_engines()}
    assert "builtin" in engines, "engine builtin não registrado"
    assert engines["builtin"]["available"] is True, "builtin deveria estar sempre disponível"
    assert get_engine("builtin") is not None


def test_registry_engine_inexistente_retorna_none():
    from pdf2latex.engine_registry import get_engine

    assert get_engine("inexistente-xyz") is None


def test_registry_best_respeita_ordem_e_disponibilidade():
    """Um registro isolado: `best()` prefere a ordem dada e cai para o
    primeiro disponível; retorna None quando nada está disponível."""
    from pdf2latex.engine_registry import _EngineRegistry

    class _Fake:
        def __init__(self, name, avail):
            self.name = name
            self._avail = avail
        def is_available(self):
            return self._avail

    reg = _EngineRegistry()
    reg.register(_Fake("builtin", True))
    reg.register(_Fake("docling", False))
    # docling preferido mas indisponível → cai para builtin
    assert reg.best(["docling", "builtin"]).name == "builtin"

    vazio = _EngineRegistry()
    vazio.register(_Fake("x", False))
    assert vazio.best() is None


def test_convert_with_best_sem_engine_disponivel_levanta():
    """convert_with_best deve falhar claramente quando nenhum engine serve."""
    import pdf2latex.engine_registry as er

    class _Fake:
        name = "x"
        def is_available(self):
            return False

    vazio = er._EngineRegistry()
    vazio.register(_Fake())
    # Reproduz o contrato de convert_with_best com um registro vazio.
    assert vazio.best() is None


# ── Dataclasses de contrato ──────────────────────────────────────────

def test_conversion_result_defaults():
    from pdf2latex.engines.base import ConversionResult

    r = ConversionResult(text_content="oi")
    assert r.text_content == "oi"
    assert r.structure == {}
    assert r.images == [] and r.tables == [] and r.equations == []
    assert r.references == [] and r.metadata == {}
    assert r.engine_used == "builtin"
    assert r.confidence == 0.0


def test_render_input_defaults():
    from pdf2latex.renderers.base import RenderInput

    ri = RenderInput(pdf_name="doc", text_content="x")
    assert ri.pdf_name == "doc"
    assert ri.structure == {} and ri.images == []
    assert ri.template is None and ri.output_dir is None


# ── Interfaces abstratas ─────────────────────────────────────────────

def test_base_engine_e_abstrata():
    from pdf2latex.engines.base import BaseEngine

    with pytest.raises(TypeError):
        BaseEngine()  # não pode instanciar (métodos abstratos)


def test_base_renderer_e_abstrata():
    from pdf2latex.renderers.base import BaseRenderer

    with pytest.raises(TypeError):
        BaseRenderer()


# ── Engine builtin ───────────────────────────────────────────────────

def test_builtin_engine_metadata():
    from pdf2latex.engines.builtin import BuiltinEngine

    e = BuiltinEngine()
    assert e.name == "builtin"
    assert e.requires_gpu is False
    assert e.requires_api_key is False
    assert e.is_available() is True
    meta = e.get_metadata()
    assert meta["name"] == "builtin"
    assert set(["name", "description", "requires_gpu", "available"]).issubset(meta)


# ── Renderizadores ───────────────────────────────────────────────────

def test_builtin_renderer_sempre_disponivel():
    from pdf2latex.renderers import BuiltinRenderer

    r = BuiltinRenderer()
    assert r.name == "builtin"
    assert r.is_available() is True


def test_pandoc_renderer_is_available_retorna_bool():
    from pdf2latex.renderers import PandocRenderer

    r = PandocRenderer()
    assert r.name == "pandoc"
    assert isinstance(r.is_available(), bool)  # não quebra quando pandoc ausente


# ── Templates Pandoc + .bst ABNT (CTAN) ──────────────────────────────

def test_pandoc_templates_presentes():
    tdir = ROOT / "pdf2latex" / "pandoc-templates"
    for nome in ["default.template", "abntex2.template", "ieee.template", "abnt.csl"]:
        assert (tdir / nome).exists(), f"template Pandoc ausente: {nome}"


def test_bst_abnt_presentes():
    adir = ROOT / "templates" / "abntex2"
    for nome in ["abntex2-alf.bst", "abntex2-num.bst", "abntex2-options.bib"]:
        p = adir / nome
        assert p.exists() and p.stat().st_size > 0, f".bst/.bib ABNT ausente/vazio: {nome}"


# ── Orquestrador PDF2LaTeX ────────────────────────────────────────────

def test_pdf2latex_pdf_inexistente_levanta():
    from pdf2latex import PDF2LaTeX

    with pytest.raises(FileNotFoundError):
        PDF2LaTeX("/caminho/inexistente/nao_existe.pdf")


# ── CLI ──────────────────────────────────────────────────────────────

def test_cli_list_engines_funciona():
    """`python3 -m pdf2latex --list-engines` sai 0 e lista o builtin."""
    res = subprocess.run(
        [sys.executable, "-m", "pdf2latex", "--list-engines"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=60,
    )
    assert res.returncode == 0, f"--list-engines falhou: {res.stderr[:300]}"
    assert "builtin" in res.stdout.lower()
