#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selo de integridade de Molambudos — geração e verificação (SPEC-935-R399).

Antes deste script, `SELO_INTEGRIDADE_MERKLE.json` era um JSON avulso: ninguém
o gerava, ninguém o conferia. Ele declarava 74 fragmentos (o corpus tem 84),
359 páginas, e nenhum dos seus hashes correspondia aos arquivos reais — tinha
virado um artefato de aparência criptográfica que não sustentava alegação
nenhuma. Um selo que ninguém confere não prova nada; um que é reescrito sempre
que atrapalha prova menos ainda.

Este módulo fecha as duas pontas:

    python3 -m scripts.molambudos_selo gerar      # recalcula e grava o selo
    python3 -m scripts.molambudos_selo verificar  # confere; sai != 0 se divergir

O que o selo atesta e o que NÃO atesta está gravado no próprio JSON, no campo
`escopo`. Ele prova apenas que os arquivos listados têm os hashes listados —
não é validação externa, nem parecer editorial, nem prova de qualidade.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
SELO = BOOK / "SELO_INTEGRIDADE_MERKLE.json"

# Artefatos cujo hash entra no selo. Ausentes são registrados como null em vez
# de quebrar a geração — o miolo de impressão pode não ter sido construído.
ARTEFATOS = {
    "sha256_main_tex": "main.tex",
    "sha256_pdf": "main.pdf",
    "sha256_kdp_print_pt": "main_kdp_pt_160x230mm.pdf",
    "sha256_kdp_print_en": "main_kdp_en_160x230mm.pdf",
    "sha256_kdp_print_zh": "main_kdp_zh_160x230mm.pdf",
    "sha256_kdp_print_tri": "main_kdp_tri_160x230mm.pdf",
    "sha256_capa_pt": "capa_completa_pt_160x230mm.pdf",
    "sha256_capa_en": "capa_completa_en_160x230mm.pdf",
    "sha256_capa_zh": "capa_completa_zh_160x230mm.pdf",
}

# Paginação de cada edição. Registrada porque é ela que determina a largura da
# lombada: uma capa impressa contra a paginação errada é recusada pela gráfica.
PAGINACOES = {
    "paginas_miolo_digital_pt": "main.pdf",
    "paginas_miolo_digital_en": "main_en.pdf",
    "paginas_miolo_digital_zh": "main_zh.pdf",
    "paginas_miolo_digital_tri": "main_tri.pdf",
    "paginas_impressao_pt_160x230mm": "main_kdp_pt_160x230mm.pdf",
    "paginas_impressao_en_160x230mm": "main_kdp_en_160x230mm.pdf",
    "paginas_impressao_zh_160x230mm": "main_kdp_zh_160x230mm.pdf",
    "paginas_impressao_tri_160x230mm": "main_kdp_tri_160x230mm.pdf",
}

# Os PDFs são REGISTRADOS mas ficam FORA da comparação de integridade: o
# pdflatex embute /CreationDate, /ModDate e um /ID derivado deles, de modo que
# dois builds da mesma fonte produzem bytes diferentes. Compará-los faria o
# selo divergir a cada recompilação, sem que nada do conteúdo tivesse mudado —
# ruído que treinaria qualquer pessoa a ignorar o alarme. O selo compara o que
# vem da fonte (fragmentos, frontmatter, main.tex, contagens); os hashes de PDF
# valem como impressão digital de um build específico, para rastrear qual
# arquivo foi enviado à gráfica.
ARTEFATOS_NAO_DETERMINISTICOS = frozenset(
    k for k in (
        "sha256_pdf", "sha256_kdp_print_pt", "sha256_kdp_print_en",
        "sha256_kdp_print_zh", "sha256_kdp_print_tri",
        "sha256_capa_pt", "sha256_capa_en", "sha256_capa_zh",
    )
)

ALGORITMO = (
    "merkle-sha256-v1: folha = sha256(caminho_relativo + '\\0' + bytes do "
    "arquivo); os fragmentos entram ordenados por caminho relativo; nível "
    "interno = sha256(esquerda + direita), com nó ímpar promovido sem "
    "alteração; a raiz de uma lista vazia é sha256(b'')."
)

ESCOPO = (
    "Este selo atesta somente que os arquivos listados possuíam, no momento da "
    "geração, os hashes registrados. NÃO constitui validação externa, parecer "
    "editorial, revisão por pares nem atestado de qualidade da obra. Os hashes "
    "de PDF são registrados como impressão digital de um build específico, mas "
    "ficam fora da verificação de integridade: o pdflatex embute data de "
    "criação, logo dois builds da mesma fonte diferem em bytes. A verificação "
    "cobre o que vem da fonte — fragmentos, frontmatter, main.tex e contagens. "
    "Ver CORRIGENDUM.md."
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _folha(relativo: str, path: Path) -> str:
    h = hashlib.sha256()
    h.update(relativo.encode("utf-8"))
    h.update(b"\0")
    h.update(path.read_bytes())
    return h.hexdigest()


def merkle_root(folhas: list[str]) -> str:
    if not folhas:
        return hashlib.sha256(b"").hexdigest()
    nivel = [bytes.fromhex(f) for f in folhas]
    while len(nivel) > 1:
        proximo: list[bytes] = []
        for i in range(0, len(nivel), 2):
            if i + 1 < len(nivel):
                proximo.append(hashlib.sha256(nivel[i] + nivel[i + 1]).digest())
            else:
                proximo.append(nivel[i])          # nó ímpar promovido
        nivel = proximo
    return nivel[0].hex()


def _fragmentos() -> list[dict[str, str]]:
    """Folhas do merkle: os fragmentos das TRÊS edições.

    Até o R405 o selo cobria apenas `fragmentos/` (português). A consequência
    foi visível na prática: dois fragmentos chineses foram substituídos por
    inteiro --- CONT-05 e DOC-26, que contradiziam a cronologia da obra --- e
    o merkle root não se moveu. Um selo que não reage a mudança de conteúdo
    numa das edições publicadas não atesta a obra; atesta um terço dela.
    """
    saida = []
    for edicao in ("fragmentos", "en/fragmentos", "zh/fragmentos"):
        base = BOOK / edicao
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.tex")):
            rel = path.relative_to(BOOK).as_posix()
            saida.append({"arquivo": rel, "sha256": _folha(rel, path)})
    return saida


def _paginas(nome: str) -> int | None:
    """Páginas de um PDF, ou None se ele não puder ser lido com confiança.

    Um PDF sendo reescrito por um build concorrente abre sem erro e reporta
    **zero** páginas. Gravar esse zero no selo seria pior que não gravar nada:
    o selo passaria a afirmar, com aparência de fato medido, uma paginação que
    nunca existiu — e é a paginação que determina a largura da lombada.
    """
    pdf = BOOK / nome
    if not pdf.is_file():
        return None
    try:
        import fitz
    except ImportError:
        return None
    try:
        with fitz.open(pdf) as doc:
            total = doc.page_count
    except Exception:
        return None
    return total if total > 0 else None


def construir() -> dict:
    frags = _fragmentos()
    artefatos = {}
    for chave, nome in ARTEFATOS.items():
        p = BOOK / nome
        artefatos[chave] = _sha256(p) if p.is_file() else None

    front = sorted((BOOK / "frontmatter").glob("*.tex"))
    h = hashlib.sha256()
    for f in front:
        h.update(f.name.encode("utf-8"))
        h.update(f.read_bytes())

    selo = {
        "obra": "Molambudos — O Diário do Paciente 1.260",
        "isbn": "9798189170492",
        "data_geracao": datetime.now(timezone.utc).isoformat(),
        "gerado_por": "scripts/molambudos_selo.py (SPEC-935-R399)",
        "algoritmo": ALGORITMO,
        "escopo": ESCOPO,
        "total_fragmentos": len(frags),
        "total_frontmatter": len(front),
        **{chave: _paginas(nome) for chave, nome in PAGINACOES.items()},
        "merkle_root_fragmentos": merkle_root([f["sha256"] for f in frags]),
        "sha256_frontmatter": h.hexdigest(),
        **artefatos,
        "fragmentos": frags,
    }
    return selo


def _comparar(atual: dict, gravado: dict) -> list[str]:
    problemas: list[str] = []
    comparaveis = [c for c in ARTEFATOS if c not in ARTEFATOS_NAO_DETERMINISTICOS]
    for chave in (
        "total_fragmentos",
        "merkle_root_fragmentos",
        "sha256_frontmatter",
        *PAGINACOES,
        *comparaveis,
    ):
        if gravado.get(chave) != atual.get(chave):
            problemas.append(
                f"{chave}: selo={gravado.get(chave)!r} real={atual.get(chave)!r}"
            )
    reais = {f["arquivo"]: f["sha256"] for f in atual["fragmentos"]}
    velhos = {f["arquivo"]: f["sha256"] for f in gravado.get("fragmentos", [])}
    for arq in sorted(set(reais) | set(velhos)):
        if reais.get(arq) != velhos.get(arq):
            problemas.append(f"fragmento divergente: {arq}")
    return problemas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=("gerar", "verificar"))
    parser.add_argument("--json", action="store_true", help="saída em JSON")
    args = parser.parse_args(argv)

    atual = construir()

    if args.acao == "gerar":
        SELO.write_text(
            json.dumps(atual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if args.json:
            print(json.dumps({"acao": "gerar", "selo": str(SELO.relative_to(ROOT))}))
        else:
            print(f"selo gravado: {SELO.relative_to(ROOT)}")
            print(f"  fragmentos: {atual['total_fragmentos']}")
            print(f"  merkle root: {atual['merkle_root_fragmentos']}")
        return 0

    if not SELO.is_file():
        print("selo ausente — rode 'gerar'", file=sys.stderr)
        return 2
    gravado = json.loads(SELO.read_text(encoding="utf-8"))
    problemas = _comparar(atual, gravado)
    if args.json:
        print(json.dumps({"ok": not problemas, "problemas": problemas}, ensure_ascii=False))
    elif problemas:
        print(f"selo DIVERGENTE ({len(problemas)} problema(s)):", file=sys.stderr)
        for p in problemas[:20]:
            print(f"  {p}", file=sys.stderr)
    else:
        print("selo confere com o corpus atual")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
