"""R1001: gemini-client e procedimento de reprodução — estático, sem chamada à API."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CRATE = ROOT / "integrations/gemini_client"


def _read(path: Path) -> str:
    assert path.is_file(), f"arquivo ausente: {path}"
    return path.read_text(encoding="utf-8")


def test_crate_files_exist():
    assert (CRATE / "Cargo.toml").is_file()
    assert (CRATE / "src/main.rs").is_file()
    assert (CRATE / "README.md").is_file()


def test_source_reads_credentials_from_env_not_hardcoded():
    src = _read(CRATE / "src/main.rs")
    assert "GEMINI_API_KEY" in src and "GEMINI_MODEL" in src
    assert "env::var" in src  # lê do ambiente
    assert "AIza" not in src  # nenhuma chave hardcoded
    assert "sk-" not in src


def test_source_reads_prompt_from_stdin_and_prints_text():
    src = _read(CRATE / "src/main.rs")
    assert "stdin" in src and "read_to_string" in src
    assert "print!" in src


def test_skip_verify_tls_is_present_and_scoped():
    src = _read(CRATE / "src/main.rs")
    assert "NoVerify" in src
    assert "dangerous" in src
    assert "MITM" in src and "sandbox" in src


def test_no_credentials_leaked_in_cargo_or_readme():
    cargo = _read(CRATE / "Cargo.toml")
    readme = _read(CRATE / "README.md")
    for text in (cargo, readme):
        assert "AIza" not in text


def test_reproduction_doc_covers_required_steps():
    doc = _read(ROOT / "docs/PROCEDIMENTO_OPENSHELL_GEMINI_CONSELHO.md")
    for required in ("OPENSHELL_COMPUTE_DRIVER=podman", "podman.socket", "cargo build",
                     "sandbox upload", "rest", "run_council", "GEMINI_API_KEY", "egress"):
        assert required in doc, f"procedimento omite: {required}"


def test_target_dir_not_committed_has_gitignore():
    gi = _read(CRATE / ".gitignore")
    assert "target" in gi
