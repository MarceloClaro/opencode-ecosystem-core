"""Contratos documentais da reconciliação da SPEC-935-R448."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOC_PATHS = (
    "README.md",
    "MANUAL.md",
    "ARCHITECTURE.md",
    "installer/README.md",
    "installer/windows/README.md",
)
NETWORK_PIPE = re.compile(
    r"(?:curl|wget|irm|invoke-webrequest)\b[^\n|]*\|\s*"
    r"(?:bash|sh|zsh|iex|powershell|pwsh)\b",
    re.IGNORECASE,
)


def _document(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_documentation_never_offers_network_content_to_an_interpreter() -> None:
    """A instrução pública também deve manter a instalação local e revisável."""
    for relative_path in DOC_PATHS:
        assert not NETWORK_PIPE.search(_document(relative_path)), relative_path


def test_installation_guide_requires_version_ref_and_sha256() -> None:
    """A procedência local combina versão, revisão Git imutável e checksum."""
    guide = _document("installer/README.md")

    for marker in (
        "ECOSYSTEM_VERSION",
        "ECOSYSTEM_REF",
        "SHA-256",
        "git checkout --detach",
    ):
        assert marker in guide
    assert "CommonInstallerSha256" in guide


def test_manual_has_one_mira_option_and_only_real_direct_commands() -> None:
    """O manual espelha o menu e os handlers canônicos da CLI."""
    manual = _document("MANUAL.md")

    assert len(re.findall(r"\|\s*`\[10\]`", manual)) == 1
    assert "imobench" not in manual.lower()
    for command in (
        "status",
        "agents",
        "doctor",
        "helpdesk",
        "ajuda",
        "pesquisa",
        "apresentacao",
        "apm audit",
        "amplify",
        "aletheia",
        "deepthink",
        "alphaproof",
        "erdos",
        "lean4",
        "egraph",
        "geometry",
        "autoformalize",
        "shortcuts",
        "clinical",
    ):
        assert f"python3 -m marceloclaro.cli {command}" in manual


def test_structural_counts_are_consistent_in_operational_documents() -> None:
    """As contagens expostas vêm da configuração e do diagnóstico atuais."""
    for relative_path in DOC_PATHS:
        content = _document(relative_path)
        for marker in ("19 checks", "6 MCPs", "209 agentes"):
            assert marker in content, f"{marker!r} ausente em {relative_path}"


def test_docs_do_not_promote_unqualified_readiness_or_perfection_claims() -> None:
    """Métricas internas não podem ser apresentadas como mérito externo."""
    combined = "\n".join(_document(relative_path).lower() for relative_path in DOC_PATHS)

    for claim in ("production ready", "production_ready", "superhuman", "100%"):
        assert claim not in combined
    assert "não constituem certificação externa" in combined


def test_installer_docs_use_the_virtualenv_after_they_create_it() -> None:
    """Instruções pós-instalação não devem voltar ao interpretador global."""
    guide = _document("installer/README.md")
    windows = _document("installer/windows/README.md")

    assert ".venv/bin/python -m marceloclaro.cli doctor" in guide
    assert "cd ~/opencode-ecosystem-core && .venv/bin/python -m marceloclaro.cli doctor" in windows
