#!/usr/bin/env python3
"""Empacota o pacote final de submissão RBEP (R425).

Gera outputs/submission/ARTIGO_RBEP_SUBMISSAO_submissao_<DATA>.zip com:
  01_manuscrito/  (DOCX + PDF + MD)
  02_carta/       (CARTA_AO_EDITOR.md)
  03_revisao/     (peer_review_r422.md)
  04_dados/       (JSONs de proveniência R412–R423)
  README_SUBMISSAO.md
  MANIFEST_SUBMISSAO.json (sha256 de cada arquivo)

Offline; não altera o manuscrito. Uso:
    python3 scripts/empacotar_submissao.py
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import date
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent  # academic/papers/arm_education_audit
OUTPUTS = PAPER / "outputs"
DESTINO = OUTPUTS / "submission"
EXCLUIR_SUFIXOS = {".aux", ".log", ".out", ".fdb_latexmk", ".fls"}
EXCLUIR_NOMES = {"__pycache__"}

README_SUBMISSAO = """# Pacote de submissão — RBEP/INEP

**Manuscrito:** "Educação terciária e trajetórias de renda: evidência
associativa de painel com validação cruzada agrupada por país (135
economias, 1960–2023)"

**Autor:** Marcelo Claro Laranjeira — ORCID: https://orcid.org/0000-0001-8996-2887

**Data:** {data}

## Conteúdo

- `01_manuscrito/` — ARTIGO_RBEP_SUBMISSAO.docx (formato de submissão),
  ARTIGO_RBEP_SUBMISSAO.pdf (conferência tipográfica, 20 páginas) e
  ARTIGO_RBEP_SUBMISSAO.md (fonte canônica em Markdown).
- `02_carta/` — Carta ao editor (ineditismo, conflitos, financiamento,
  autoria, ciência aberta).
- `03_revisao/` — Relatório do blind peer review emulado (12 achados,
  0 bloqueios; correções aplicadas nos ciclos R422 e R423).
- `04_dados/` — Proveniência numérica JSON (SHA-256 por artefato) dos
  ciclos R412–R423; cada número citado no manuscrito tem entrada
  correspondente.

## Notas de conduta

- Este pacote é um **candidato a submissão**: nenhuma alegação de aceite,
  classificação Qualis ou prontidão editorial é feita.
- A adequação às normas ABNT (NBR 10520 e NBR 6023) foi verificada por
  testes automatizados, mas a decisão final de publicação pertence
  exclusivamente ao corpo editorial da RBEP.
- Dados e código completos (incluindo pipelines de download, análise e
  exportação DOCX) estão no repositório de auditoria
  `academic/papers/arm_education_audit/`.
- Ponto de conferência humana pendente: revisão final do resumo em espanhol
  e decisão de envio (gate editorial humano, conforme as regras do projeto).

## Checklist antes do upload

1. [ ] Conferir resumo em espanhol (Título en español / Resumen).
2. [ ] Confirmar metadados do autor (nome completo e ORCID).
3. [ ] Conferir o arquivo DOCX em editor compatível (Word/LibreOffice).
4. [ ] Enviar DOCX + carta no portal da RBEP; manter PDF e dados como
      material suplementar se o sistema aceitar.
5. [ ] Registrar o comprovante de submissão no repositório.
"""


def sha256(arquivo: Path) -> str:
    h = hashlib.sha256()
    with arquivo.open("rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def montar_itens() -> list[tuple[str, Path]]:
    """Retorna lista (caminho_no_zip, caminho_no_disco)."""
    latex = PAPER / "latex"
    docx = OUTPUTS / "docx"
    expanded = OUTPUTS / "expanded"
    itens: list[tuple[str, Path]] = [
        ("01_manuscrito/ARTIGO_RBEP_SUBMISSAO.docx", docx / "ARTIGO_RBEP_SUBMISSAO.docx"),
        ("01_manuscrito/ARTIGO_RBEP_SUBMISSAO.pdf", latex / "ARTIGO_RBEP_SUBMISSAO.pdf"),
        ("01_manuscrito/ARTIGO_RBEP_SUBMISSAO.md", PAPER / "ARTIGO_RBEP_SUBMISSAO.md"),
        ("02_carta/CARTA_AO_EDITOR.md", PAPER / "CARTA_AO_EDITOR.md"),
        ("03_revisao/peer_review_r422.md", OUTPUTS / "review" / "peer_review_r422.md"),
    ]
    for prov in sorted(expanded.glob("provenance*.json")):
        itens.append((f"04_dados/{prov.name}", prov))
    return itens


def gerar_manifest(itens: list[tuple[str, Path]]) -> dict:
    entradas = []
    for caminho_zip, caminho_disco in itens:
        entradas.append({
            "arquivo": caminho_zip,
            "sha256": sha256(caminho_disco),
            "bytes": caminho_disco.stat().st_size,
        })
    return {
        "pacote": "ARTIGO_RBEP_SUBMISSAO — submissão RBEP/INEP",
        "gerado_em": date.today().isoformat(),
        "autor": "Marcelo Claro Laranjeira",
        "orcid": "https://orcid.org/0000-0001-8996-2887",
        "nota": "Pacote preparado por script (R425); revisão final e decisão de "
                "submissão permanecem sob responsabilidade humana. Sem qualquer "
                "alegação de aceite ou prontidão editorial.",
        "arquivos": entradas,
    }


def principal() -> None:
    itens = montar_itens()
    faltando = [p for _, p in itens if not p.exists()]
    if faltando:
        raise FileNotFoundError(f"Arquivos ausentes: {faltando}")

    DESTINO.mkdir(parents=True, exist_ok=True)
    manifest = gerar_manifest(itens)
    nome_zip = DESTINO / f"ARTIGO_RBEP_SUBMISSAO_submissao_{date.today().isoformat()}.zip"

    with zipfile.ZipFile(nome_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for caminho_zip, caminho_disco in itens:
            zf.write(caminho_disco, caminho_zip)
        zf.writestr("README_SUBMISSAO.md", README_SUBMISSAO.format(data=date.today().isoformat()))
        zf.writestr("MANIFEST_SUBMISSAO.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    # também grava o manifest solto ao lado do zip (versionável)
    (DESTINO / "MANIFEST_SUBMISSAO.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Pacote gerado: {nome_zip} ({nome_zip.stat().st_size / 1024:.1f} KiB)")
    print(f"Arquivos: {len(itens)} + MANIFEST_SUBMISSAO.json")


if __name__ == "__main__":
    principal()
