"""Validate standalone source provenance for every literature skill."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "references" / "source-links.json"
CONTRACT_PATH = ROOT / "references" / "source-presentation.md"
HELPER_PATH = ROOT / "scripts" / "literature_source_contract.py"
MARKER = "<!-- source-presentation-contract:v2 -->"


def validate() -> list[str]:
    errors: list[str] = []
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"Could not load source registry: {exc}"]
    entries = registry.get("skills")
    if registry.get("schema_version") != 2 or not isinstance(entries, dict):
        return ["Source registry must have schema_version=2 and a skills object"]
    skills = sorted(path for path in (ROOT / "skills").iterdir() if (path / "SKILL.md").is_file())
    expected = {skill.name for skill in skills}
    for name in sorted(expected - entries.keys()):
        errors.append(f"Missing registry entry for {name}")
    for name in sorted(entries.keys() - expected):
        errors.append(f"Unexpected registry entry for {name}")
    try:
        presentation = CONTRACT_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"Could not load source-presentation contract: {exc}"]
    for phrase in (
        "claim-adjacent",
        "supports_claim",
        "checked_sources",
        "Raw JSON",
        "never invent",
    ):
        if phrase.casefold() not in presentation.casefold():
            errors.append(f"Source-presentation contract is missing {phrase!r}")
    for skill in skills:
        doc = (skill / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            MARKER,
            f"Use the `{skill.name}` entry in `../../references/source-links.json`",
            "claim-adjacent",
            "canonical_url",
            "raw or machine-readable output unchanged",
            "../../references/source-presentation.md",
            "checked_sources",
        ):
            if phrase not in doc:
                errors.append(f"{skill.name}: missing required source or packaging rule {phrase!r}")
        if "No additional runtime references" in doc or "package limited to" in doc:
            errors.append(
                f"{skill.name}: packaging guidance contradicts shared helper requirements"
            )
        clients = [
            path for path in (skill / "scripts").glob("*.py") if not path.name.startswith("test_")
        ]
        if not clients:
            errors.append(f"{skill.name}: no runtime clients")
        for client in clients:
            source = client.read_text(encoding="utf-8")
            try:
                ast.parse(source, filename=str(client))
            except SyntaxError as exc:
                errors.append(f"{skill.name}: invalid client {client.name}: {exc}")
            if "apply_source_contract" not in source or "literature_source_contract" not in source:
                errors.append(
                    f"{skill.name}: client {client.name} does not use the plugin source contract"
                )
            if "write_text(raw" in source or "json.dumps(data, indent=2)" in source:
                errors.append(
                    f"{skill.name}: client {client.name} re-encodes requested raw HTTP bytes"
                )
        entry = entries.get(skill.name)
        if not isinstance(entry, dict):
            continue
        if not isinstance(entry.get("source_name"), str) or not entry["source_name"].strip():
            errors.append(f"{skill.name}: source_name must be nonempty")
        homepage = entry.get("homepage_url")
        if not isinstance(homepage, str) or urlsplit(homepage).scheme != "https":
            errors.append(f"{skill.name}: homepage_url must be an HTTPS URL")
        mappings = entry.get("record_url_templates")
        if not isinstance(mappings, list):
            errors.append(f"{skill.name}: record_url_templates must be a list")
            continue
        for mapping in mappings:
            if not isinstance(mapping, dict):
                errors.append(f"{skill.name}: invalid record mapping")
                continue
            template = mapping.get("template")
            if (
                not isinstance(template, str)
                or not template.startswith("https://")
                or "{id}" not in template
            ):
                errors.append(f"{skill.name}: canonical templates must be HTTPS and contain {{id}}")
            fields = mapping.get("identifier_fields")
            if (
                not isinstance(fields, list)
                or not fields
                or not all(isinstance(field, str) for field in fields)
            ):
                errors.append(f"{skill.name}: canonical mappings need explicit identifier fields")
    try:
        ast.parse(HELPER_PATH.read_text(encoding="utf-8"), filename=str(HELPER_PATH))
    except (OSError, SyntaxError) as exc:
        errors.append(f"Invalid plugin-local source helper: {exc}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    entries = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["skills"]
    count = sum(len(entry["record_url_templates"]) for entry in entries.values())
    print(
        f"Source contract validated: {len(entries)} literature skills and {count} canonical URL templates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
