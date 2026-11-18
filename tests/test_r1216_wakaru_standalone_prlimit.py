"""Testes SDD/TDD para SPEC-935-R1216 — Wakaru standalone sob limites da REA."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path("/home/marceloclaro/opencode-ecosystem-core")
SPEC = ROOT / "specs" / "SPEC-935-R1216-wakaru-standalone-prlimit.md"
BASE = ROOT / ".opencode" / "rea" / "wakaru" / "1.14.0"
STANDALONE_DIR = BASE / "standalone-v1.14.0"
ASSET = STANDALONE_DIR / "wakaru-linux-x64.tar.gz"
MANIFEST = BASE / "install-manifest.json"
BIN = BASE / "bin" / "wakaru"
PRLIMIT = "/usr/bin/prlimit"
SMOKE_EVIDENCE = BASE / "recovery-smoke.json"

EXPECTED_ASSET_SHA256 = (
    "db0e620034723195ab426e94d00d55dbd8fd0106a928ada2563f1103196d09fa"
)
EXPECTED_BANNER = "wakaru 1.14.0"
EXPECTED_URL = (
    "https://github.com/pionxzh/wakaru/releases/download/v1.14.0/"
    "wakaru-linux-x64.tar.gz"
)
PRLIMIT_ARGS = [
    PRLIMIT,
    "--as=1073741824:1073741824",
    "--fsize=67108864:67108864",
    "--cpu=120:120",
    "--core=0:0",
    "--",
]
MINIMAL_ENV = {"PATH": "/usr/bin:/bin", "NO_COLOR": "1", "RAYON_NUM_THREADS": "1"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def find_standalone_executable() -> Path:
    candidates: list[Path] = []
    for path in STANDALONE_DIR.rglob("*"):
        try:
            if not path.is_file() or not os.access(path, os.X_OK):
                continue
            if path.read_bytes()[:4] != b"\x7fELF":
                continue
            candidates.append(path)
        except OSError:
            continue
    assert candidates, "nenhum executável ELF encontrado no diretório standalone"
    preferred = [p for p in candidates if "wakaru" in p.name.lower()]
    return sorted(preferred or candidates)[0]


def run_under_prlimit(command: list[str]) -> str:
    result = subprocess.run(
        [*PRLIMIT_ARGS, *command, "--version"],
        capture_output=True,
        text=True,
        timeout=30,
        env=MINIMAL_ENV,
    )
    assert result.returncode == 0, (
        f"comando falhou sob prlimit: rc={result.returncode}; "
        f"stdout={result.stdout[:500]!r}; stderr={result.stderr[:500]!r}"
    )
    return result.stdout.strip()


def test_spec_r1216_existe() -> None:
    assert SPEC.exists(), "SPEC-935-R1216 não encontrada"
    texto = SPEC.read_text(encoding="utf-8")
    assert "Wakaru standalone" in texto
    assert EXPECTED_ASSET_SHA256 in texto
    assert "/usr/bin/prlimit" in texto


def test_asset_oficial_tem_sha_esperado() -> None:
    assert ASSET.exists(), "asset standalone oficial ausente"
    assert sha256(ASSET) == EXPECTED_ASSET_SHA256


def test_executavel_standalone_e_elf() -> None:
    exe = find_standalone_executable()
    assert exe.read_bytes()[:4] == b"\x7fELF"


def test_executavel_standalone_responde_sob_prlimit() -> None:
    exe = find_standalone_executable()
    assert run_under_prlimit([str(exe)]) == EXPECTED_BANNER


def test_wrapper_ativo_responde_sob_prlimit() -> None:
    assert BIN.exists(), "wrapper REA_WAKARU_COMMAND ausente"
    assert BIN.stat().st_mode & 0o111, "wrapper não é executável"
    assert run_under_prlimit([str(BIN)]) == EXPECTED_BANNER


def test_manifest_registra_standalone_e_verificacao() -> None:
    data = load_manifest()
    standalone = data.get("standalone")
    assert isinstance(standalone, dict), "manifest sem bloco standalone"
    assert standalone.get("asset_url") == EXPECTED_URL
    assert standalone.get("asset_sha256") == EXPECTED_ASSET_SHA256
    assert standalone.get("executable_path") == str(find_standalone_executable())
    assert standalone.get("command") == str(BIN)
    assert standalone.get("execution_under_rea_prlimit_verified") is True
    assert data.get("spec") in {"SPEC-935-R1215", "SPEC-935-R1216"}


def test_evidencia_smoke_recovery_registrada() -> None:
    assert SMOKE_EVIDENCE.exists(), "evidência do smoke recovery ausente"
    data = json.loads(SMOKE_EVIDENCE.read_text(encoding="utf-8"))
    assert data.get("spec") == "SPEC-935-R1216"
    assert data.get("operation") == "recover_javascript_sources"
    assert data.get("exit_code") == 0
    assert data.get("provider") == "wakaru"
    assert data.get("input_sha256")
    assert data.get("recovered_file_count", 0) >= 1
