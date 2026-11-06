#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate de verificação dos artefatos do artigo (SPEC-986 local).

Uso: python3 scripts/verificar_artefatos.py [--pdf] [--docx]
Sem flags, verifica apenas os Markdown. Retorna 1 se qualquer critério falhar.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ORIGINAL = BASE / "00_ORIGINAL.md"
HASH_FILE = BASE / "00_ORIGINAL.sha256"
CORRIGIDO = BASE / "01_ARTIGO_CORRIGIDO_ABNT.md"
FINAL = BASE / "02_ARTIGO_QUALIS_A1.md"

FALHAS: list[str] = []
OK: list[str] = []


def check(cond: bool, msg: str) -> None:
    (OK if cond else FALHAS).append(msg)


def palavras(texto: str) -> int:
    return len(re.findall(r"\b[\wÀ-ÿ]+\b", texto))


def referencias(texto: str) -> list[str]:
    if "# REFERÊNCIAS" not in texto:
        return []
    bloco = texto.split("# REFERÊNCIAS", 1)[1]
    entradas = []
    for linha in bloco.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]+,\s", linha) or re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zà-ÿ]+,\s", linha):
            entradas.append(linha)
    return entradas


def checar_markdown(caminho: Path, min_pal: int, max_pal: int, esperadas: int) -> None:
    if not caminho.exists():
        check(False, f"{caminho.name}: arquivo ausente")
        return
    texto = caminho.read_text(encoding="utf-8")
    n = palavras(texto)
    check(min_pal <= n <= max_pal, f"{caminho.name}: {n} palavras (esperado {min_pal}-{max_pal})")

    proibidos = [
        "Silva *et al*., 2015", "Silva et al., 2015",
        "De Paula Nunes", "DE PAULA NUNES",
        "De Oliveira Fam", "DE OLIVEIRA FAM",
        "Mendonça e Oliveira", "MENDONÇA e OLIVEIRA",
        "Do Nascimento e Da Cruz", "DO NASCIMENTO",
        "Da Silva e Arantes", "DA SILVA",
        "p 01", "p 03", "p 0",
        "\\.", "  \n",
    ]
    for p in proibidos:
        check(p not in texto, f"{caminho.name}: ausência de resíduo {p!r}")

    # Citações órfãs: sobrenomes citados que não aparecem nas referências.
    refs = referencias(texto)
    check(len(refs) == esperadas, f"{caminho.name}: {len(refs)} referências (esperado {esperadas})")

    corpus = " ".join(refs)
    sobrenomes = ["Costa", "Couto", "Fam", "Maia", "Nascimento", "Nunes", "Ribeiro",
                  "Santos", "Schmidt", "Silva", "Togashi", "Bezerra"]
    for s in sobrenomes:
        check(s in texto, f"{caminho.name}: citação a {s}")
        check(s.upper() in corpus.upper() or s == "Silva", f"{caminho.name}: referência de {s}")

    # Pares autor-ano que devem existir.
    for par in ["2013", "2015", "2016", "2019", "2020", "2021", "2022"]:
        check(par in texto, f"{caminho.name}: ano {par} presente")


def checar_hash() -> None:
    if not ORIGINAL.exists() or not HASH_FILE.exists():
        check(False, "original/hash ausente")
        return
    esperado = HASH_FILE.read_text(encoding="utf-8").split()[0]
    atual = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
    check(esperado == atual, f"00_ORIGINAL.md: hash íntegro ({atual[:12]}…)")


def checar_pdf(pdf: Path) -> None:
    if not pdf.exists():
        check(False, f"{pdf.name}: ausente")
        return
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info)
    check(bool(m) and abs(float(m.group(1)) - 595.28) < 2 and abs(float(m.group(2)) - 841.89) < 2,
          f"{pdf.name}: página A4 ({m.group(1)}x{m.group(2)})" if m else f"{pdf.name}: página A4 (não detectada)")
    txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
    check(len(txt) > 8000, f"{pdf.name}: texto extraível ({len(txt)} chars)")
    check("REFERÊNCIAS" in txt.upper(), f"{pdf.name}: seção de referências presente")
    check("\ufffd" not in txt and "??" not in txt, f"{pdf.name}: sem glifos ausentes")


def checar_docx(docx: Path) -> None:
    if not docx.exists():
        check(False, f"{docx.name}: ausente")
        return
    try:
        from docx import Document  # type: ignore
        from docx.shared import Cm  # type: ignore
    except Exception as exc:  # pragma: no cover
        check(False, f"{docx.name}: python-docx indisponível ({exc})")
        return
    doc = Document(str(docx))
    sec = doc.sections[0]
    margens = (sec.top_margin.cm, sec.left_margin.cm, sec.bottom_margin.cm, sec.right_margin.cm)
    check(abs(margens[0] - 3) < 0.1 and abs(margens[1] - 3) < 0.1 and abs(margens[2] - 2) < 0.1 and abs(margens[3] - 2) < 0.1,
          f"{docx.name}: margens 3/3/2/2 cm (obtido {margens})")
    normal = doc.styles["Normal"]
    check(normal.font.name == "Times New Roman", f"{docx.name}: fonte Normal Times New Roman")
    check(normal.font.size is not None and abs(normal.font.size.pt - 12) < 0.1, f"{docx.name}: corpo 12 pt")
    check(doc.paragraphs and len(doc.paragraphs) > 40, f"{docx.name}: conteúdo presente ({len(doc.paragraphs)} parágrafos)")


def main() -> int:
    checar_hash()
    checar_markdown(CORRIGIDO, 3500, 5200, 14)
    checar_markdown(FINAL, 4500, 7000, 14)
    if "--pdf" in sys.argv:
        for nome in ["01_ARTIGO_CORRIGIDO_ABNT.pdf", "02_ARTIGO_QUALIS_A1.pdf"]:
            checar_pdf(BASE / nome)
    if "--docx" in sys.argv:
        for nome in ["01_ARTIGO_CORRIGIDO_ABNT.docx", "02_ARTIGO_QUALIS_A1.docx"]:
            checar_docx(BASE / nome)

    for msg in OK:
        print(f"PASS  {msg}")
    for msg in FALHAS:
        print(f"FAIL  {msg}")
    print(f"\n{len(OK)} PASS / {len(FALHAS)} FAIL")
    return 1 if FALHAS else 0


if __name__ == "__main__":
    raise SystemExit(main())
