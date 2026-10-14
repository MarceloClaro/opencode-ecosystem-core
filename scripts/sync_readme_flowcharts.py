#!/usr/bin/env python3
"""Sincroniza os fluxos integrais do catálogo local no README, sem usar rede."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys

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


def render_block(root: Path) -> str:
    catalog = json.loads(_inside(root, "docs/architecture/flows.json").read_text(encoding="utf-8"))
    entries = catalog["flows"]
    if not entries or len({entry["id"] for entry in entries}) != len(entries):
        raise ValueError("Catálogo vazio ou com IDs duplicados.")
    lines = [START, "## Fluxogramas operacionais completos", "",
        "Os fluxogramas abaixo são cópias integrais das mesmas fontes usadas no",
        "[mapa navegável](docs/architecture_map.html). A ordem, as descrições, as fontes",
        "e as limitações seguem o [catálogo de fluxos](docs/architecture/flows.json).",
        "A edição estrutural de referência é o snapshot `6380cfa`; estes desenhos",
        "não representam uma nova execução de todos os componentes.", "",
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
        lines.extend([f"### {number:02d}. {entry['title']}", "", entry["description"], "",
                      "```mermaid", code + "```", "",
                      f"[Fonte Mermaid]({relative}) · [Abrir SVG]({svg_relative})", "", "**Fontes de código:**", ""])
        for item in entry["sources"]:
            _inside(root, item["path"])
            if type(item["line"]) is not int or item["line"] < 1:
                raise ValueError("Linha de origem inválida.")
            lines.append(f"- [{item['path']}:{item['line']}]({item['path']}#L{item['line']}) — `{item['symbol']}`.")
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
    args = parser.parse_args(argv)
    try:
        equal = synchronize(args.root.resolve(strict=True), args.readme, check=args.check)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Erro de sincronização: {error}", file=sys.stderr)
        return 2
    print("Fluxogramas sincronizados." if equal else "Fluxogramas divergentes; regenere o README.")
    return 0 if equal else 1


if __name__ == "__main__":
    raise SystemExit(main())
