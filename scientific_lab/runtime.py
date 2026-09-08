"""Discovery e despacho seguro da supercamada científica v4.1 instalada."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

BASELINE_CORE_COMMIT = "a5478054ceb8fc34eb0d254a30a3c451d6d864cd"
EXPECTED_VERSION = "4.1.0"
EXPECTED_PACKAGE_MANIFEST_SHA256 = "89786fcb9b461d0bffbbbaae962da69bb9ce03e2b4e56178ed2c36f15776b89e"
EXPECTED_SKILL_ARCHIVE_SHA256 = "a805894960e96b7d9aa153a0e8b73c08f5654eef8bb0289867902f9f9612bc78"
REQUIRED_CORE = (
    "marceloclaro/orchestrator.py",
    "mci/metabus.py",
    "mci/blackboard.py",
    "transformer/attention.py",
    "sdd/spec_engine.py",
    "sdd/tdd_runner.py",
    "integrations/opencode_cli.py",
    "rag/scientific.py",
)
CONTROLLERS = {
    "research": "articlesctl.py",
    "articles": "articlesctl.py",
    "mesh": "meshctl.py",
    "mission": "missionctl.py",
    "review": "reviewctl.py",
    "living": "livingctl.py",
    "synthesis": "synthesisctl.py",
    "grade": "gradectl.py",
    "causal": "causalctl.py",
    "federation": "federationctl.py",
    "production": "productionctl.py",
}


def _candidates() -> Iterable[Path]:
    explicit = os.environ.get("PESQUISADOR_UNIVERSAL_HOME")
    if explicit:
        yield Path(explicit).expanduser()
    prefix = os.environ.get("PU_PREFIX")
    if prefix:
        yield Path(prefix).expanduser() / "skill"
    yield Path.home() / ".local/share/pesquisador-universal/skill"


def _valid_skill(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "SKILL.md").is_file()
        and (path / "VERSION.json").is_file()
        and (path / "scripts/validate_contracts.py").is_file()
    )


def discover() -> Path | None:
    for candidate in _candidates():
        if _valid_skill(candidate):
            return candidate.resolve()
    return None


def _git_head(checkout: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def core_compatibility(checkout: Path) -> dict:
    checks = []
    for rel in REQUIRED_CORE:
        ok = (checkout / rel).is_file()
        checks.append({"check": rel, "status": "pass" if ok else "fail"})
    return {
        "schema_version": "1.0",
        "mode": "embedded_bridge",
        "baseline_audited_commit": BASELINE_CORE_COMMIT,
        "observed_commit": _git_head(checkout),
        "checks": checks,
        "compatible": all(item["status"] == "pass" for item in checks),
        "epistemic_authority": "none",
    }


def installed_status(home: Path | None = None) -> dict:
    path = home or discover()
    if path is None:
        return {
            "status": "not_installed",
            "home": None,
            "version": None,
            "verified_release": False,
            "message": "Instale a supercamada v4.1 ou defina PESQUISADOR_UNIVERSAL_HOME.",
        }
    try:
        version_data = json.loads((path / "VERSION.json").read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "status": "invalid",
            "home": str(path),
            "version": None,
            "verified_release": False,
            "error": str(exc),
        }
    version = version_data.get("version")
    manifest_sha = _sha256(path / "PACKAGE_MANIFEST.sha256")
    verified = version == EXPECTED_VERSION and manifest_sha == EXPECTED_PACKAGE_MANIFEST_SHA256
    return {
        "status": "installed_verified" if verified else "installed_unverified",
        "home": str(path),
        "version": version,
        "edition": version_data.get("edition"),
        "package_manifest_sha256": manifest_sha,
        "expected_package_manifest_sha256": EXPECTED_PACKAGE_MANIFEST_SHA256,
        "expected_skill_archive_sha256": EXPECTED_SKILL_ARCHIVE_SHA256,
        "verified_release": verified,
    }


def dispatch(command: str, argv: list[str], home: Path | None = None) -> int:
    root = home or discover()
    if root is None:
        print(json.dumps(installed_status(), ensure_ascii=False, indent=2))
        return 4
    status = installed_status(root)
    if not status.get("verified_release"):
        print(json.dumps(status, ensure_ascii=False, indent=2), file=sys.stderr)
        return 5
    controller = CONTROLLERS.get(command)
    if controller is None:
        print(f"comando científico desconhecido: {command}", file=sys.stderr)
        return 2
    script = root / "scripts" / controller
    if not script.is_file():
        print(f"controller ausente: {script}", file=sys.stderr)
        return 3
    return subprocess.call([sys.executable, str(script), *argv])
