#!/usr/bin/env python3
"""Sincroniza os fluxos integrais do catálogo local no README, sem usar rede."""
from __future__ import annotations

import argparse
import ast
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from urllib.parse import quote

START = "<!-- core-flowcharts:start -->"
END = "<!-- core-flowcharts:end -->"
ANCHOR = "## Limites de segurança e operação"


def _inside(root: Path, relative: str) -> Path:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative or ":" in relative:
        raise ValueError(f"Caminho relativo inválido: {relative}")
    resolved = (root / relative).resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError(f"Fonte fora da raiz ou inválida: {relative}")
    return resolved


def _ast_anchors(tree: ast.AST) -> list[tuple[str, int]]:
    anchors = []

    def walk(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}.{child.name}" if prefix else child.name
                anchors.append((name, child.lineno))
                walk(child, name)
            else:
                walk(child, prefix)

    walk(tree)
    return anchors


def refresh_source_anchors(root: Path) -> dict:
    """Atualiza âncoras somente contra manifesto worktree já revalidado.

    Arquivos não rastreados, privados, removidos, com symlink ou que mudaram
    após a coleta são recusados. O catálogo não é escrito se alguma âncora falhar.
    """
    root = Path(root).resolve(strict=True)
    folder = root / "docs/architecture"
    if folder.is_symlink() or not folder.is_dir() or not folder.resolve(strict=True).is_relative_to(root):
        raise ValueError("Diretório de arquitetura fora da raiz ou inválido")
    inventory_candidate = root / "docs/architecture/architecture-inventory.json"
    catalog_candidate = root / "docs/architecture/flows.json"
    if inventory_candidate.is_symlink() or catalog_candidate.is_symlink():
        raise ValueError("Inventário e catálogo de fluxos não podem ser symlinks")
    inventory_path = _inside(root, "docs/architecture/architecture-inventory.json")
    catalog_path = _inside(root, "docs/architecture/flows.json")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    git = inventory.get("git", {})
    if git.get("source") != "worktree" or not git.get("commit") or not git.get("worktree_sha256"):
        raise ValueError("Inventário worktree com commit-base e identidade obrigatórios")
    manifest = {row.get("path"): row for row in git.get("source_manifest", [])}
    if not manifest:
        raise ValueError("Manifesto de fontes worktree vazio")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    updated = 0
    for flow in catalog.get("flows", []):
        for source in flow.get("sources", []):
            relative = source.get("path")
            entry = manifest.get(relative)
            if entry is None:
                raise ValueError(f"Fonte ausente do manifesto worktree: {relative}")
            path = root / relative
            if any(part.is_symlink() for part in (path, *path.parents) if part != root):
                raise ValueError(f"Symlink recusado como âncora: {relative}")
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"Fonte rastreada ausente ou não regular: {relative}")
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if digest != entry.get("sha256"):
                raise ValueError(f"Fonte diverge do manifesto worktree: {relative}")
            symbol = source.get("symbol")
            if path.suffix == ".py" and symbol:
                text = data.decode("utf-8-sig")
                candidates = _ast_anchors(ast.parse(text, filename=relative))
                exact = [line for name, line in candidates if name == symbol]
                matches = exact or [line for name, line in candidates if name.rsplit(".", 1)[-1] == symbol.rsplit(".", 1)[-1]]
                if len(matches) != 1:
                    raise ValueError(f"Âncora ausente ou ambígua: {relative}:{symbol}")
                source["line"] = matches[0]
            else:
                if type(source.get("line")) is not int or source["line"] < 1:
                    raise ValueError(f"Linha da âncora inválida: {relative}")
            source["sha256"] = digest
            source["origin"] = "worktree_tracked"
            updated += 1
    catalog["source"] = {
        "review": "R916",
        "mode": "worktree",
        "base_commit": git["commit"],
        "worktree_sha256": git["worktree_sha256"],
        "changed_paths": sorted(git.get("changed_paths", [])),
        "deleted_paths": sorted(git.get("deleted_paths", [])),
        "excluded_paths": sorted(git.get("excluded_paths", [])),
        "scope": "current_tracked_production_sources; non-source index metadata from base Git",
    }
    payload = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    descriptor, temporary = tempfile.mkstemp(dir=folder, prefix=".flows-", suffix=".tmp")
    try:
        os.chmod(temporary, catalog_path.stat().st_mode & 0o777)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, catalog_path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {"updated_anchors": updated, "base_commit": git["commit"],
            "worktree_sha256": git["worktree_sha256"],
            "changed_paths": len(git.get("changed_paths", [])),
            "deleted_paths": len(git.get("deleted_paths", []))}


def refresh_current_sources(root: Path) -> dict:
    """Recalcula âncoras a partir do checkout atual, sem inventário histórico.

    O modo `current` declara explicitamente que os hashes são do worktree, não
    de um permalink. Arquivos não rastreados, symlinks e símbolos ambíguos são
    recusados; a escrita é atômica.
    """
    root = Path(root).resolve(strict=True)
    folder = root / "docs/architecture"
    if folder.is_symlink() or not folder.is_dir() or not folder.resolve(strict=True).is_relative_to(root):
        raise ValueError("Diretório de arquitetura fora da raiz ou inválido")
    catalog_path = _inside(root, "docs/architecture/flows.json")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    updated = 0
    for flow in catalog.get("flows", []):
        for source in flow.get("sources", []):
            relative = source.get("path")
            path = _inside(root, relative)
            if path.is_symlink() or any(part.is_symlink() for part in path.parents if part != root):
                raise ValueError(f"Symlink recusado como âncora: {relative}")
            tracked = subprocess.run(
                ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", relative],
                capture_output=True, text=True, check=False)
            if tracked.returncode:
                raise ValueError(f"Fonte não rastreada: {relative}")
            data = path.read_bytes()
            if path.suffix == ".py" and source.get("symbol"):
                text = data.decode("utf-8-sig")
                candidates = _ast_anchors(ast.parse(text, filename=relative))
                exact = [line for name, line in candidates if name == source["symbol"]]
                matches = exact or [line for name, line in candidates
                                    if name.rsplit(".", 1)[-1] == source["symbol"].rsplit(".", 1)[-1]]
                if len(matches) != 1:
                    raise ValueError(f"Âncora ausente ou ambígua: {relative}:{source['symbol']}")
                source["line"] = matches[0]
            elif type(source.get("line")) is not int or source["line"] < 1:
                raise ValueError(f"Linha da âncora inválida: {relative}")
            source["sha256"] = hashlib.sha256(data).hexdigest()
            source["origin"] = "worktree_tracked"
            updated += 1
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    catalog["source"] = {
        "review": "R1057",
        "mode": "current",
        "base_commit": head,
        "scope": "current tracked worktree sources; hashes and lines recomputed; no execution claim",
    }
    payload = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    descriptor, temporary = tempfile.mkstemp(dir=folder, prefix=".flows-", suffix=".tmp")
    try:
        os.chmod(temporary, catalog_path.stat().st_mode & 0o777)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, catalog_path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {"updated_anchors": updated, "base_commit": head, "mode": "current"}


def render_block(root: Path) -> str:
    catalog = json.loads(_inside(root, "docs/architecture/flows.json").read_text(encoding="utf-8"))
    entries = catalog["flows"]
    if not entries or len({entry["id"] for entry in entries}) != len(entries):
        raise ValueError("Catálogo vazio ou com IDs duplicados.")
    catalog_source = catalog.get("source", {})
    if catalog_source.get("mode") == "worktree":
        source_notice = (f"Fontes do checkout atual; base Git `{catalog_source.get('base_commit')}`; "
            f"identidade worktree `{catalog_source.get('worktree_sha256')}`. "
            f"{len(catalog_source.get('changed_paths', []))} arquivos rastreados modificados e "
            f"{len(catalog_source.get('deleted_paths', []))} removidos foram contabilizados; fontes não rastreadas não entram.")
    elif catalog_source.get("mode") == "current":
        source_notice = (f"Fontes rastreadas do checkout atual; base Git `{catalog_source.get('base_commit')}`. "
            "Hashes e linhas foram recalculados no R1057; a apresentação é SVG e a fonte Mermaid fica em auditoria.")
    else:
        source_notice = "Fontes do snapshot Git declarado no catálogo."
    manifest_path = root / "docs/architecture/animated/manifest.json"
    gif_by_flow = {}
    if manifest_path.is_file():
        for row in json.loads(manifest_path.read_text(encoding="utf-8")).get("diagrams", []):
            for origin in row.get("origins", []):
                if origin.get("flow_id"):
                    gif_by_flow[origin["flow_id"]] = row["id"]
    lines = [START, "## Fluxogramas operacionais completos", "",
        "Os fluxogramas abaixo são cópias integrais das mesmas fontes usadas no",
        "[mapa navegável](docs/architecture_map.html). A ordem, as descrições, as fontes",
        "e as limitações seguem o [catálogo de fluxos](docs/architecture/flows.json).",
        "A edição e a origem das fontes estão declaradas no catálogo e no inventário.", source_notice,
        "Estes desenhos não representam uma nova execução de todos os componentes.", "",
        "### Legenda e critérios de leitura", "",
        "| Elemento | Como interpretar |",
        "|---|---|",
        "| Retângulo | Componente, etapa, dado ou artefato indicado pelo rótulo. |",
        "| Losango | Decisão ou condição; siga o texto de cada saída. |",
        "| Grupo delimitado | Subsistema ou fronteira de responsabilidade. Não implica isolamento de rede. |",
        "| Seta contínua | Direção de controle, dado ou composição conforme o título e o rótulo; não implica chamada direta entre todas as caixas. |",
        "| Seta pontilhada | Caminho condicional, dependência opcional ou relação explicativa; leia o rótulo e os limites do fluxo. |",
        "| Cores | Auxílio visual de agrupamento; nomes e rótulos conservam a informação sem depender da cor. |",
        "| Fonte de código | Âncora de arquivo, símbolo e linha no retrato documentado; não é recibo de execução. |", "",
        "Instalação, disponibilidade, autenticação, inferência concluída, entrega aceita",
        "e validação externa são estados distintos. Evidências de uma operação local",
        "valem apenas para seu escopo. Referências a agentes ou ferramentas opcionais",
        "não garantem saldo, licença, credenciais, isolamento ou funcionamento atual.", "",
        "No grafo estrutural integral, a seta tem significado mais restrito:",
        "**módulo importador → dependência Python declarada**. Consulte a",
        "[fonte Mermaid integral](docs/architecture/dependencies.mmd), o",
        "[SVG equivalente](docs/architecture/dependencies-mermaid.svg) e o",
        "[guia da legenda e reprodução](docs/architecture/MERMAID_INTEGRAL.md).", "",
    ]
    for number, entry in enumerate(entries, 1):
        if PurePosixPath(entry["file"]).is_absolute():
            raise ValueError("Fonte de fluxo deve usar caminho relativo.")
        relative = "docs/architecture/" + entry["file"]
        source = _inside(root, relative)
        if source.suffix != ".mmd":
            raise ValueError("Fonte de fluxo deve ser Mermaid (.mmd).")
        svg_relative = str(PurePosixPath(relative).with_suffix(".svg"))
        _inside(root, svg_relative)
        code = source.read_text(encoding="utf-8")
        if "```" in code or not code.endswith("\n"):
            raise ValueError("Fonte deve terminar com newline e não conter cercas Markdown.")
        title = html.escape(entry["title"], quote=True)
        gif_link = ""
        if entry["id"] in gif_by_flow:
            gif_relative = f"docs/architecture/animated/{gif_by_flow[entry['id']]}.gif"
            _inside(root, gif_relative)
            gif_link = f" · [GIF animado]({gif_relative})"
        lines.extend([f"### {number:02d}. {entry['title']}", "", entry["description"], "",
                      f'<img src="{svg_relative}" alt="{title} — diagrama estático" width="100%">', "",
                      f"[Abrir SVG]({svg_relative}) · [Fonte Mermaid]({relative}){gif_link}", "",
                      "<details>", "<summary>Fonte Mermaid (auditoria)</summary>", "",
                      "```mermaid", code + "```", "", "</details>", "",
                      "**Fontes de código:**", ""])
        for item in entry["sources"]:
            source_path = _inside(root, item["path"])
            if type(item["line"]) is not int or item["line"] < 1:
                raise ValueError("Linha de origem inválida.")
            data = source_path.read_bytes()
            text = data.decode("utf-8-sig")
            if item["line"] > len(text.splitlines()):
                raise ValueError(f"Âncora além do arquivo: {item['path']}")
            if item.get("sha256") and hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise ValueError(f"Âncora com fonte modificada: {item['path']}")
            if source_path.suffix == ".py" and item.get("symbol"):
                name = item["symbol"].split(".")[-1]
                if not any(isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                           and node.name == name and node.lineno == item["line"]
                           for node in ast.walk(ast.parse(text))):
                    raise ValueError(f"Âncora não corresponde ao símbolo: {item['path']}:{item['line']}")
            if catalog_source.get("mode") == "worktree" and item["path"] in catalog_source.get("changed_paths", []):
                anchor = f"`{item['path']}:{item['line']}` (fonte local modificada; não é permalink da base)"
            elif catalog_source.get("mode") == "worktree":
                quoted = "/".join(quote(part) for part in item["path"].split("/"))
                anchor = f"[{item['path']}:{item['line']}](https://github.com/MarceloClaro/opencode-ecosystem-core/blob/{catalog_source['base_commit']}/{quoted}#L{item['line']})"
            else:
                anchor = f"[{item['path']}:{item['line']}]({item['path']}#L{item['line']})"
            lines.append(f"- {anchor} — `{item['symbol']}`.")
        lines.extend(["", "**Limitações:**", ""])
        lines.extend(f"- {limitation}" for limitation in entry["limitations"])
        lines.append("")
    lines.extend(["Para atualizar esta seção, execute na raiz", "`python3 scripts/sync_readme_flowcharts.py`. Para conferir sem escrever, use",
                  "`python3 scripts/sync_readme_flowcharts.py --check`.", "", END])
    return "\n".join(lines)


def synchronize(root: Path, readme: str, *, check: bool = False) -> bool:
    destination = _inside(root, readme)
    before = destination.read_bytes()
    start, end = START.encode(), END.encode()
    if before.count(start) != before.count(end) or before.count(start) > 1:
        raise ValueError("Marcadores ausentes, duplicados ou incompletos.")
    block = render_block(root).encode("utf-8")
    if start in before:
        first, last = before.index(start), before.index(end)
        if last < first:
            raise ValueError("Marcadores invertidos.")
        after = before[:first] + block + before[last + len(end):]
    else:
        anchor = ANCHOR.encode("utf-8")
        if before.count(anchor) != 1:
            raise ValueError("Âncora única para inclusão não encontrada.")
        first = before.index(anchor)
        after = before[:first] + block + b"\n\n" + before[first:]
    if check:
        return before == after
    if after != before:
        destination.write_bytes(after)
    return True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--refresh-sources", action="store_true",
                        help="Atualiza âncoras a partir do inventário worktree e do manifesto SHA-256.")
    parser.add_argument("--refresh-current", action="store_true",
                        help="Recalcula hashes e linhas a partir do checkout atual, sem inventário histórico.")
    args = parser.parse_args(argv)
    try:
        if (args.refresh_sources or args.refresh_current) and args.check:
            raise ValueError("Refresh de fontes não pode ser combinado com --check")
        if args.refresh_sources and args.refresh_current:
            raise ValueError("Escolha apenas um modo de refresh")
        root = args.root.resolve(strict=True)
        if args.refresh_current:
            refresh = refresh_current_sources(root)
        elif args.refresh_sources:
            refresh = refresh_source_anchors(root)
        else:
            refresh = None
        equal = synchronize(root, args.readme, check=args.check)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Erro de sincronização: {error}", file=sys.stderr)
        return 2
    if refresh:
        print(json.dumps({"status": "refreshed_and_synchronized", **refresh}, ensure_ascii=False))
    else:
        print("Fluxogramas sincronizados." if equal else "Fluxogramas divergentes; regenere o README.")
    return 0 if equal else 1


if __name__ == "__main__":
    raise SystemExit(main())
