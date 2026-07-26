# -*- coding: utf-8 -*-
"""
Testes R144 — Console Error Analyzer (SPEC-935-R144)
====================================================
TDD do classificador automático de logs de console do navegador.

Classifica cada linha em:
  - extension  (extensões Chrome: eesel AI, searchitfastnow, refresh,
                single-player/agent-chat)
  - infrastructure (Cloudflare 524, WebSocket localhost)
  - informational (THREE.WebGLRenderer, navegação, lazy load, background)
  - unknown    (linha não reconhecida)

Requisitos: SPEC-935-R144.
"""
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest


# ── Fixture ────────────────────────────────────────────────────────────

@pytest.fixture
def analyzer():
    from scripts.console_error_analyzer import ConsoleErrorAnalyzer
    return ConsoleErrorAnalyzer()


# ── CA-1: eesel AI ────────────────────────────────────────────────────

def test_ca1_eesel_ai(analyzer):
    r = analyzer.classify("content.bundle.js:1 Initialized eesel AI with test.")
    assert r["category"] == "extension"
    assert r["source"] == "eesel AI"
    assert r["severity"] == "info"


# ── CA-2: Cloudflare 524 (infraestrutura) ─────────────────────────────

def test_ca2_cloudflare_524(analyzer):
    r = analyzer.classify(
        "main:1  Failed to load resource: the server responded with a status of 524 ()"
    )
    assert r["category"] == "infrastructure"
    assert r["source"] == "cloudflare"
    assert r["severity"] == "warning"


# ── CA-3: THREE.WebGLRenderer (informativo) ───────────────────────────

def test_ca3_three_webgl(analyzer):
    r = analyzer.classify("three.min.js:578 THREE.WebGLRenderer 73")
    assert r["category"] == "informational"
    assert r["source"] == "three.js"
    assert r["severity"] == "info"


# ── CA-4: searchitfastnow (extensão por ID) ───────────────────────────

def test_ca4_searchitfastnow(analyzer):
    r = analyzer.classify(
        "chrome-extension://biaggnjibplcfekllonekbonhfgchopo/manifest.json:1  Failed to load resource: net::ERR_FILE_NOT_FOUND"
    )
    assert r["category"] == "extension"
    assert r["source"] == "searchitfastnow"
    assert r["severity"] == "error"


# ── CA-5: Refresh extension (WebSocket) ────────────────────────────────

def test_ca5_refresh_extension(analyzer):
    r = analyzer.classify(
        "refresh.js:27 WebSocket connection to 'ws://localhost:8081/' failed:"
    )
    assert r["category"] == "extension"
    assert r["source"] == "refresh"
    assert r["severity"] == "info"


# ── CA-6: single-player / agent-chat ──────────────────────────────────

def test_ca6_single_player(analyzer):
    r = analyzer.classify(
        "single-player.bundle.js:2 Single-player is disabled because agent-chat feature flag is enabled"
    )
    assert r["category"] == "extension"
    assert r["source"] == "single-player"
    assert r["severity"] == "info"


# ── CA-7: Navegação ────────────────────────────────────────────────────

def test_ca7_navegacao(analyzer):
    r = analyzer.classify(
        "Navegou para     https://jeans-attacks-loved-biology.trycloudflare.com/index.html"
    )
    assert r["category"] == "informational"
    assert r["source"] == "navigation"
    assert r["severity"] == "info"


# ── CA-8: analyze vazio ────────────────────────────────────────────────

def test_ca8_analyze_vazio(analyzer):
    r = analyzer.analyze([])
    assert r["total"] == 0
    assert r["categories"] == {}
    assert r["lines"] == []


# ── CA-9: analyze com múltiplas linhas ─────────────────────────────────

def test_ca9_analyze_multiplas(analyzer):
    linhas = [
        "content.bundle.js:1 Initialized eesel AI with test.",
        "main:1  Failed to load resource: the server responded with a status of 524 ()",
        "three.min.js:578 THREE.WebGLRenderer 73",
    ]
    r = analyzer.analyze(linhas)
    assert r["total"] == 3
    assert r["categories"]["extension"] == 1
    assert r["categories"]["infrastructure"] == 1
    assert r["categories"]["informational"] == 1
    assert len(r["lines"]) == 3


# ── CA-10: generate_report contém resumo ───────────────────────────────

def test_ca10_relatorio_contem_resumo(analyzer):
    linhas = [
        "content.bundle.js:1 Initialized eesel AI with test.",
        "main:1  Failed to load resource: the server responded with a status of 524 ()",
    ]
    analysis = analyzer.analyze(linhas)
    report = analyzer.generate_report(analysis)
    assert "ZERO ERROS DE CÓDIGO DO SITE" in report
    assert "Extensões" in report
    assert "Infraestrutura" in report
    assert "linhas analisadas" in report.lower()
    # assert que extensões são listadas nominalmente
    assert "eesel AI" in report or "searchitfastnow" not in report


# ── Testes de borda ────────────────────────────────────────────────────

def test_linha_desconhecida(analyzer):
    r = analyzer.classify("algo completamente aleatório sem padrão conhecido")
    assert r["category"] == "unknown"
    assert r["source"] == "unknown"
    assert r["severity"] == "info"


def test_linha_vazia(analyzer):
    r = analyzer.classify("")
    assert r["category"] == "unknown"


def test_background_script(analyzer):
    r = analyzer.classify("content.bundle.js:1 Background script ready.")
    assert r["category"] == "informational"
    assert r["source"] == "background"


def test_index_iife(analyzer):
    r = analyzer.classify("index.iife.js:1 content script loaded")
    assert r["category"] == "extension"
    assert r["source"] == "eesel AI"


def test_content_script_from_background(analyzer):
    r = analyzer.classify("contentScript.js:1 from background")
    assert r["category"] == "extension"
    assert r["source"] == "eesel AI"


def test_lazy_load_intervention(analyzer):
    r = analyzer.classify(
        "index.html:1 [Intervention] Images loaded lazily and replaced with placeholders."
    )
    assert r["category"] == "informational"
    assert r["source"] == "browser"
    assert r["severity"] == "warning"


def test_stack_trace_line(analyzer):
    r = analyzer.classify("    at V (Index.bab7a582.js:11:106388)")
    assert r["category"] == "extension"
    assert r["source"] == "searchitfastnow"


def test_initClient_refresh(analyzer):
    r = analyzer.classify("initClient @ chrome-extension://imbddededgmcgfhfpcjmijokokekbkal/refresh.js:27")
    assert r["category"] == "extension"
    assert r["source"] == "refresh"
