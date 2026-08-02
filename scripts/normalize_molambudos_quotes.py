# -*- coding: utf-8 -*-
"""Normaliza aspas neutras PT/EN de Molambudos para pares tipográficos.

SPEC-935-R358. O script só altera ``\textquotedbl`` que não seja seguido de
``left``/``right``, ignora comentários TeX e falha se um arquivo tiver número
ímpar de comandos neutros.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
NEUTRAL_QUOTE = re.compile(r"\\textquotedbl(?!left|right)")


def _split_comment(line: str) -> tuple[str, str]:
    r"""Separa conteúdo ativo e comentário, respeitando ``\%`` escapado."""

    for index, character in enumerate(line):
        if character != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return line[:index], line[index:]
    return line, ""


def normalize_neutral_quotes(content: str) -> tuple[str, int]:
    """Converte pares neutros em left/right sem alterar o restante do TeX."""

    converted = 0
    output: list[str] = []

    def replacement(_match: re.Match[str]) -> str:
        nonlocal converted
        command = (
            r"\textquotedblleft"
            if converted % 2 == 0
            else r"\textquotedblright"
        )
        converted += 1
        return command

    for line in content.splitlines(keepends=True):
        active, comment = _split_comment(line)
        output.append(NEUTRAL_QUOTE.sub(replacement, active) + comment)
    if converted % 2:
        raise ValueError(
            f"arquivo contém {converted} comandos \\textquotedbl ativos (ímpar)"
        )
    return "".join(output), converted


def fragment_paths(book_root: Path) -> list[Path]:
    paths: list[Path] = []
    for relative in ("fragmentos", "en/fragmentos"):
        paths.extend(sorted((book_root / relative).glob("**/*.tex")))
    return paths


def normalize_book(book_root: Path, check: bool = False) -> tuple[int, int]:
    changed_files = 0
    converted_commands = 0
    for path in fragment_paths(book_root):
        content = path.read_text(encoding="utf-8")
        normalized, converted = normalize_neutral_quotes(content)
        if not converted:
            continue
        changed_files += 1
        converted_commands += converted
        if not check:
            path.write_text(normalized, encoding="utf-8")
    return changed_files, converted_commands


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-root", type=Path, default=DEFAULT_BOOK)
    parser.add_argument(
        "--check",
        action="store_true",
        help="não altera arquivos; retorna 1 se ainda houver aspas neutras",
    )
    args = parser.parse_args()
    files, commands = normalize_book(args.book_root.resolve(), check=args.check)
    print(f"arquivos={files}; comandos_neutros={commands}; check={args.check}")
    return 1 if args.check and commands else 0


if __name__ == "__main__":
    raise SystemExit(main())
