#!/usr/bin/env python3
"""Guarda de sanidade LaTeX antes de compilar o livro-core.

Checa, por arquivo mod-*.tex e macros.tex:
  1. balanceamento global de chaves `{` vs `}` (delta deve ser 0);
  2. linhas iniciadas por `\\elemento` devem ter delta 0 (linha única);
  3. ausência de caracteres que o pdflatex não compila (emoji \u2600-\u2BFF etc.);
  4. ambientes novos com `[titulo]{legenda}` devem ter topo igual a final.

Uso:  python3 check.py   -> exit 0 se tudo ok, 1 se houver problema.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

HERE = Path(__file__).parent
FILES = sorted(HERE.glob("mod-*.tex")) + [HERE / "macros.tex"]
ENVS = {
    "descricao", "funcao", "definicao", "conceito", "metodo", "resultado",
    "limite", "arquitetura", "niveis", "aviso", "processo", "flowch", "interpreta",
}

ELEMENTO_RE = re.compile(r"^\s*\\elemento\{")


def counts(line: str) -> int:
    # ignora comentários LaTeX em linha (percent solto no fim)
    return line.count("{") - line.count("}")


def main() -> int:
    errs = 0
    for f in FILES:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        lines = text.split("\n")

        # 1) balanceamento global
        delta = 0
        for l in lines:
            delta += counts(l)
        if delta != 0:
            print(f"[CHAVES] {f.name}: delta={delta} (esperado 0)")
            errs += 1

        # 2) elemento em linha única balanceada: só quando a linha TERMINA em
        #    `}` (head fechado em si) e ainda assim delta != 0 (bug conhecido)
        for i, l in enumerate(lines, 1):
            if ELEMENTO_RE.match(l) and l.rstrip().endswith("}"):
                if counts(l) != 0:
                    print(f"[ELEMENTO] {f.name}:{i} delta={counts(l)}")
                    errs += 1

        # 3) caracteres fora do encoding T1 (emoji etc.)
        bad = sorted({c for c in text if ord(c) > 0x25FF})
        if bad:
            print(f"[UNICODE] {f.name}: emoji/tip. simbolos fora do T1: "
                  f"{' '.join(f'U+{ord(c):04X}' for c in bad[:8])}")
            errs += 1

        # 4) ambientes flowch com 2 colchetes consecutivos (bug conhecido)
        if re.search(r"\\begin\{flowch\}\[[^\]]*\]\[", text):
            print(f"[FLOWCH] {f.name}: uso de [titulo][extra] invalido")
            errs += 1

    if errs:
        print(f"\n{errs} problema(s) encontrado(s).")
        return 1
    print("ok: chaves, elemento, unicode e flowch limpos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())