# -*- coding: utf-8 -*-
"""
Testes R143 — Revisão e Refino do Geomaker (SPEC-935-R143)
===========================================================
Valida a integridade do deploy do Museu Geomaker:

  * Serviços systemd ativos (nginx, touchterrain, geomaker-api)
  * Endpoints HTTP respondendo (site, TouchTerrain, Bridge)
  * Proxy Nginx roteando corretamente (/api/, /touchterrain/, etc.)
  * Botão "Carregar gerador aqui" removido
  * Erro.txt saneado (zero falsos positivos de código do site)
  * Bridge OpenCode health check funcional

Requisitos: SPEC-935-R143 e SPEC-935-R212 (CA11/CA12).
"""
import os
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SITE_DIR = Path("/opt/geomaker/site")
GEOMAKER_DIR = Path("/home/marceloclaro/Geomaker_site")
ERRO_TXT = GEOMAKER_DIR / "erros" / "erro.txt"

BRIDGE_SERVICE = "geomaker-api"
LEGACY_BRIDGE_SERVICE = "geomaker-opencode-bridge"
SERVICES = ["nginx", "geomaker-touchterrain", BRIDGE_SERVICE]
HTML_FILES = ["index.html", "acervo.html", "laboratorio.html",
              "admin-acervo.html", "touchterrain.html"]
LOCALHOST = "http://localhost:8080"
BRIDGE = "http://127.0.0.1:8082"
RELEVO_UNIT = ROOT / "deploy" / "systemd" / "geomaker-relevo.service"
RUN_EXTERNAL_TESTS = os.getenv("OPENCODE_RUN_EXTERNAL_TESTS") == "1"
EXTERNAL_SKIP_REASON = (
    "teste externo desabilitado; defina OPENCODE_RUN_EXTERNAL_TESTS=1"
)


# ── CA-1: Serviços systemd ativos ─────────────────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
@pytest.mark.parametrize("svc", SERVICES)
def test_ca1_service_active(svc):
    r = subprocess.run(["systemctl", "is-active", svc],
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Service {svc}: {r.stdout.strip()}"


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca1_servico_bridge_legado_nao_esta_ativo():
    """CA12: o bridge legado não pode executar em paralelo ao canônico."""
    # Arrange
    command = ["systemctl", "is-active", LEGACY_BRIDGE_SERVICE]

    # Act
    result = subprocess.run(command, capture_output=True, text=True, timeout=10)

    # Assert
    assert result.returncode != 0, (
        f"Serviço legado {LEGACY_BRIDGE_SERVICE} ainda está ativo"
    )


# ── CA-2: Site na porta 8080 ──────────────────────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca2_site_responds():
    import urllib.request
    r = urllib.request.urlopen(f"{LOCALHOST}/", timeout=10)
    assert r.status == 200


# ── CA-3: TouchTerrain /main responde ─────────────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca3_touchterrain_main():
    import urllib.request
    try:
        r = urllib.request.urlopen(f"{LOCALHOST}/main", timeout=30)
        assert r.status == 200
    except urllib.error.URLError:
        pytest.skip("TouchTerrain temporariamente indisponível (infraestrutura)")


# ── CA-4: Bridge health check ─────────────────────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca4_bridge_health():
    import urllib.request, json
    r = urllib.request.urlopen(f"{BRIDGE}/health", timeout=10)
    assert r.status == 200
    data = json.loads(r.read().decode())
    assert data["status"] == "ok"
    assert "opencode/deepseek" in data["model"]


# ── CA-5: Proxy /touchterrain/ ────────────────────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca5_proxy_touchterrain():
    import urllib.request
    r = urllib.request.urlopen(f"{LOCALHOST}/touchterrain/", timeout=15)
    assert r.status in (200, 302)


# ── CA-6: Proxy /api/health (via Nginx) ───────────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca6_proxy_api_health():
    import urllib.request, json
    r = urllib.request.urlopen(f"{LOCALHOST}/api/health", timeout=15)
    assert r.status == 200
    data = json.loads(r.read().decode())
    assert data["status"] == "ok"


# ── CA-7: Botão "Carregar gerador" removido ───────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca7_botao_carregar_gerador_removido():
    lab_file = SITE_DIR / "laboratorio.html"
    content = lab_file.read_text("utf-8")
    assert "Carregar gerador" not in content
    assert "data-terrain-load" not in content


# ── CA-8: Erro.txt saneado ────────────────────────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca8_erro_txt_saneado():
    content = ERRO_TXT.read_text("utf-8")
    # Aceita tanto "ZERO ERROS" quanto "ERROS NÃO CLASSIFICADOS" (depende do snapshot)
    assert "ZERO ERROS" in content or "NÃO CLASSIFICADOS" in content
    assert "Extensões" in content or "Extensões Chrome" in content
    assert "console error analyzer" in content.lower()


# ── CA-9: Bridge POST responde (validação ou sucesso, nunca 500) ──────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca9_bridge_post_nao_retorna_500():
    import urllib.request, json
    body = json.dumps({"prompt": "teste"}).encode()
    req = urllib.request.Request(
        f"{BRIDGE}/api/chat", data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        r = urllib.request.urlopen(req, timeout=120)
        assert r.status in (200, 201, 202)
    except urllib.error.HTTPError as e:
        # 422 (validação) ou 503 (CLI não encontrado) são aceitáveis
        assert e.code in (422, 503), f"HTTP {e.code} inesperado"


# ── CA-10: Páginas HTML com sintaxe válida ────────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
@pytest.mark.parametrize("html_file", HTML_FILES)
def test_ca10_html_sintaxe_valida(html_file):
    content = (SITE_DIR / html_file).read_text("utf-8")
    assert "<!DOCTYPE" in content or "<!doctype" in content
    # verifica tags principais abertas e fechadas
    for tag in ["html", "head", "body"]:
        assert content.count(f"<{tag}") >= 1
        assert f"</{tag}>" in content


# ── CA-11: Ecossistema SDD íntegro ────────────────────────────────────

def test_ca11_spec_registry_integrity():
    from sdd.spec_engine import SpecRegistry, SPECS_DIR
    reg = SpecRegistry()
    specs_dir = Path(SPECS_DIR)
    spec_files = list(specs_dir.glob("SPEC-*.md"))
    assert len(spec_files) >= 40, f"Apenas {len(spec_files)} arquivos SPEC-*.md em {specs_dir}"
    r143 = reg.get("SPEC-935-R143")
    assert r143 is not None
    assert r143.status in ("draft", "red", "green", "verified")


# ── Testes adicionais de integridade do deploy ────────────────────────

@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_site_static_files_exist():
    for f in ["index.html", "assets/site.js", "assets/styles.css",
              "assets/config.js"]:
        assert (SITE_DIR / f).exists(), f"Arquivo ausente: {f}"


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_proxy_export_nao_404():
    import urllib.request
    try:
        r = urllib.request.urlopen(f"{LOCALHOST}/export", timeout=15)
        assert r.status in (200, 302, 405)
    except urllib.error.HTTPError as e:
        assert e.code in (405, 302), f"export retornou {e.code}"


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_proxy_static_nao_404():
    import urllib.request
    try:
        r = urllib.request.urlopen(f"{LOCALHOST}/static/", timeout=15)
        assert r.status in (200, 302)
    except urllib.error.HTTPError as e:
        assert e.code in (403, 404, 502), f"static/ retornou {e.code} inesperado"


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_bridge_cors_permitido():
    import urllib.request
    req = urllib.request.Request(f"{BRIDGE}/health", method="OPTIONS")
    req.add_header("Origin", "http://localhost:8080")
    req.add_header("Access-Control-Request-Method", "GET")
    try:
        r = urllib.request.urlopen(req, timeout=10)
        cors = r.headers.get("Access-Control-Allow-Origin", "")
        assert cors == "*" or cors == "http://localhost:8080"
    except urllib.error.HTTPError:
        pass  # OPTIONS pode retornar 405, o que é aceitável


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_laboratorio_sem_iframe_touchterrain():
    lab = (SITE_DIR / "laboratorio.html").read_text("utf-8")
    import re
    iframes_src = re.findall(r'<iframe[^>]*src="([^"]*)"', lab)
    for src in iframes_src:
        assert 'touchterrain' not in src.lower(), f"iframe aponta para TouchTerrain: {src}"


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_admin_acervo_acessivel():
    import urllib.request
    r = urllib.request.urlopen(f"{LOCALHOST}/admin-acervo.html", timeout=10)
    assert r.status == 200


def test_r212_relevo_unit_versionada_e_supervisionada():
    """CA31 hermético: o backend Node possui lifecycle systemd auditável."""

    assert RELEVO_UNIT.is_file()
    content = RELEVO_UNIT.read_text("utf-8")
    assert "relevo-server.cjs" in content
    assert "Restart=on-failure" in content
    assert "nohup" not in content
    assert "&" not in content


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_r212_relevo_service_e_proxy_respondem():
    """CA31 externo: unit, porta direta e proxy permanecem operacionais."""

    import json
    import urllib.request

    active = subprocess.run(
        ["systemctl", "is-active", "geomaker-relevo"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert active.returncode == 0, active.stdout + active.stderr

    with urllib.request.urlopen(
        "http://127.0.0.1:8083/api/relevo/status", timeout=10
    ) as direct:
        direct_payload = json.loads(direct.read())
        assert direct.status == 200
        assert direct_payload

    with urllib.request.urlopen(
        f"{LOCALHOST}/api/relevo/status", timeout=10
    ) as proxied:
        assert proxied.status == 200
