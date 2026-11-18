"""Testes SDD/TDD para SPEC-935-R1215 — instalação isolada do Wakaru 1.14.0."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path("/home/marceloclaro/opencode-ecosystem-core")
SPEC = ROOT / "specs" / "SPEC-935-R1215-wakaru-isolado.md"
BASE = ROOT / ".opencode" / "rea" / "wakaru" / "1.14.0"
TGZ = BASE / "wakaru-1.14.0.tgz"
MANIFEST = BASE / "install-manifest.json"
PACKAGE_JSON = BASE / "node_modules" / "wakaru" / "package.json"
BIN = BASE / "bin" / "wakaru"
CODEX_CONFIG = Path("/mnt/c/Users/marce/.codex/config.toml")

EXPECTED_SHA512 = (
    "sha512-gJ4LJQtkrF7b1oaXMWXqqiThIZl4t3HA+tSbSqHCuqxruljWZKD5tRLvdYhEY3MTFkin5tGFusLr6QByatJqyA=="
)
EXPECTED_REVISION = "8219bf5016a063d7fb215101a8c45d5959ec733f"
EXPECTED_REGISTRY = "https://registry.npmjs.org/wakaru/-/wakaru-1.14.0.tgz"
EXPECTED_REPOSITORY = "https://github.com/pionxzh/wakaru"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_spec_r1215_existe() -> None:
    assert SPEC.exists(), "SPEC-935-R1215 não encontrada"
    texto = SPEC.read_text(encoding="utf-8")
    assert "Wakaru 1.14.0" in texto
    assert "REA_WAKARU_COMMAND" in texto


def test_manifest_registra_fonte_e_integridade() -> None:
    data = load_manifest()
    assert data["package"] == "wakaru"
    assert data["version"] == "1.14.0"
    assert data["license"] == "Apache-2.0"
    assert data["source"]["registry"] == EXPECTED_REGISTRY
    assert data["source"]["repository"] == EXPECTED_REPOSITORY
    assert data["source"]["revision"] == EXPECTED_REVISION
    assert data["integrity"]["npm_sha512"] == EXPECTED_SHA512
    assert TGZ.exists(), "tarball oficial ausente"
    assert data["integrity"]["tarball_sha256"] == sha256(TGZ)


def test_pacote_instalado_tem_metadata_esperada() -> None:
    assert PACKAGE_JSON.exists(), "wakaru não instalado no diretório isolado"
    package = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    assert package["name"] == "wakaru"
    assert package["version"] == "1.14.0"
    assert package["license"] == "Apache-2.0"


def test_wrapper_respeita_banner_exigido_pela_rea() -> None:
    assert BIN.exists(), "wrapper bin/wakaru ausente"
    assert BIN.stat().st_mode & 0o111, "wrapper bin/wakaru não é executável"
    saida = subprocess.check_output([str(BIN), "--version"], text=True).strip()
    assert saida == "wakaru 1.14.0", f"banner inesperado: {saida!r}"
    data = load_manifest()
    assert data["version_banner"]["raw"].strip() == "wakaru 1.14.0"
    assert data["version_banner"]["normalized"] == "wakaru 1.14.0"


def test_prlimit_disponivel() -> None:
    assert shutil.which("prlimit") == "/usr/bin/prlimit"


def test_config_codex_permaneceu_intacta() -> None:
    assert CODEX_CONFIG.exists(), "config.toml do Codex não encontrado"
    data = load_manifest()
    antes = data["guardrails"]["codex_config_sha256_before"]
    depois = data["guardrails"]["codex_config_sha256_after"]
    atual = sha256(CODEX_CONFIG)
    assert antes == depois == atual, "config.toml do Codex foi alterada"


def test_sem_efeitos_colaterais_declarados() -> None:
    data = load_manifest()
    guard = data["guardrails"]
    assert guard["global_install"] is False
    assert guard["scripts_executed"] is False
    assert guard["rea_bridge_patched"] is False
    assert guard["app_asar_modified"] is False
    assert guard["runtime_key_read"] is False
    assert guard["mcp_config_changed"] is False
    assert guard["environment_persisted"] is False
