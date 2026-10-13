"""Sincroniza inventários delimitados dos guias locais (SPEC-935-R822)."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = (
    "README.md", "MANUAL.md", "ARCHITECTURE.md", "CLAUDE.md", "PROGRESS.md",
    "installer/README.md", "installer/windows/README.md",
)


def _replace_block(text: str, name: str, content: str) -> str:
    start = f"<!-- {name}:start -->"
    end = f"<!-- {name}:end -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"Marcadores ausentes ou duplicados: {name}.")
    first = text.index(start) + len(start)
    last = text.index(end)
    if last < first:
        raise ValueError(f"Marcadores invertidos: {name}.")
    return text[:first] + "\n" + content + "\n" + text[last:]


def _runtime_diagram(agents: int, mcps: int) -> str:
    return f"""```mermaid
flowchart TB
    Usuario2[Usuário ou automação] --> CLI2[CLI marceloclaro]
    CLI2 --> Orq2[MarceloClaroOrchestrator]
    Orq2 --> Router[AttentionRouter]
    Orq2 --> SpecRegistry2[SpecRegistry]
    Orq2 --> SpecVerifier2[SpecVerifier]
    Orq2 --> TDDRunner2[TDDRunner]
    Orq2 --> MetaBus2[MetaBus]
    Orq2 --> Blackboard2[Blackboard]
    Orq2 --> MCP2[{mcps} MCPs configurados]
    Orq2 --> Agents2[{agents} agentes configurados]
    Orq2 --> Mira2[mira-presenter]
    Mira2 --> Deck2[MiraDeckPipeline]
    Deck2 --> Engine2[MiraEngine]
```"""


def synchronize(root: Path, check_count: int, *, write: bool = False) -> list[str]:
    """Confere tudo antes de escrever; conteúdo fora dos blocos é preservado."""
    root = Path(root)
    config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("A configuração deve ser um objeto JSON.")
    for key in ("agent", "mcp", "command"):
        if not isinstance(config.get(key), dict):
            raise ValueError(f"A configuração {key} deve ser um objeto JSON.")
    agents, mcps, commands = (len(config[key]) for key in ("agent", "mcp", "command"))
    pending = {}
    for name in DOCUMENTS:
        path = root / name
        old = path.read_text(encoding="utf-8")
        config_link = os.path.relpath(root / "opencode.json", path.parent).replace(os.sep, "/")
        doctor_link = os.path.relpath(root / "marceloclaro/doctor.py", path.parent).replace(os.sep, "/")
        content = (
            f"**{agents} agentes** · **{mcps} MCPs** · **{commands} comandos** · **{check_count} checks**\n\n"
            f"Inventário derivado de [opencode.json]({config_link}) e do "
            f"[diagnóstico estrutural]({doctor_link}). Contagens de configuração "
            "e checks não comprovam disponibilidade, autenticação, inferência "
            "ou validação externa.\n\n"
            "Para conferir estes blocos, execute na raiz "
            "`.venv/bin/python scripts/reconcile_operational_docs.py --check`; "
            "para sincronizá-los, execute o mesmo comando sem `--check`."
        )
        new = _replace_block(old, "core-state", content)
        if name == "ARCHITECTURE.md":
            listing = "\n".join(f"{index}. `{server}`;" for index, server in enumerate(sorted(config["mcp"]), 1))
            new = _replace_block(new, "core-mcp", listing)
        if name == "README.md":
            new = _replace_block(new, "core-runtime-diagram", _runtime_diagram(agents, mcps))
        if new != old:
            pending[name] = new
    if write:
        for name, content in pending.items():
            (root / name).write_text(content, encoding="utf-8")
    return list(pending)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Conferir ou sincronizar os inventários dos guias.")
    parser.add_argument("--check", action="store_true", help="Conferir sem modificar documentos.")
    args = parser.parse_args(argv)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from marceloclaro.doctor import run_doctor

    try:
        report = run_doctor()
        changed = synchronize(ROOT, check_count=len(report["checks"]), write=not args.check)
    except (OSError, ValueError) as exc:
        print(f"Sincronização interrompida: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"mode": "check" if args.check else "sync", "changed_documents": changed}, ensure_ascii=False))
    return int(args.check and bool(changed))


if __name__ == "__main__":
    raise SystemExit(main())
