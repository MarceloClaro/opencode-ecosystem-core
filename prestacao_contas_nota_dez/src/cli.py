# -*- coding: utf-8 -*-
"""
CLI do plugin Auditor e Executor de Prestação de Contas (Prêmio Escola Nota Dez)
=================================================================================
Comandos:
  audit   <pdf_diligencia> [--cache DIR] [--out DIR]
          → parse da diligência + checklist + score interno + relatório
  execute <json_do_audit> [--controle CSV] [--minuta MD]
          → gera minuta de ofício-resposta e planilha a partir do audit

Exemplos:
  python3 -m prestacao_contas_nota_dez.src.cli audit \
      "/mnt/c/Users/marce/OneDrive/Documentos/img20260924_14524484.pdf" \
      --out exemplos/
  python3 -m prestacao_contas_nota_dez.src.cli execute exemplos/audit_xxx.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .assistente import gerar_sugestoes, gerar_sugestoes_arquivo
from .auditor import auditar_diligencia, calcular_score
from .diligencia import parse_diligencia
from .executor import gerar_controle_csv, gerar_minuta_arquivo
from .ocr import ocr_pdf
from .relatorio import gerar_relatorio_arquivo


def _cmd_audit(args: argparse.Namespace) -> int:
    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f"ERRO: PDF não encontrado: {pdf}", file=sys.stderr)
        return 1
    print(f"OCR de {pdf.name} ...", file=sys.stderr)
    paginas = ocr_pdf(pdf, cache_dir=Path(args.cache), workers=args.workers)
    texto = "\n".join(paginas.values())
    doc = parse_diligencia(texto, fonte=str(pdf))
    checklist = auditar_diligencia(doc)
    score = calcular_score(checklist)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = pdf.stem
    audit_json = out_dir / f"audit_{base}.json"
    (out_dir / f"minuta_{base}.md").write_text(
        "<!-- preenchido pelo comando execute -->\n", encoding="utf-8"
    )
    payload = {
        "fonte": str(pdf),
        "doc": doc,
        "checklist": checklist,
        "score": score,
    }
    audit_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"score": score, "checklist": len(checklist), "json": str(audit_json)}, ensure_ascii=False, indent=2))
    return 0


def _cmd_execute(args: argparse.Namespace) -> int:
    audit_json = Path(args.json)
    if not audit_json.exists():
        print(f"ERRO: JSON de auditoria não encontrado: {audit_json}", file=sys.stderr)
        return 1
    payload = json.loads(audit_json.read_text(encoding="utf-8"))
    doc = payload["doc"]
    checklist = payload["checklist"]
    score = payload.get("score") or calcular_score(checklist)
    out_dir = audit_json.parent

    minuta_path = out_dir / f"minuta_{Path(doc['fonte']).stem}.md"
    sugestoes = None
    if args.aplicar:
        sugestoes = gerar_sugestoes(checklist)
    gerar_minuta_arquivo(doc, checklist, minuta_path, sugestoes=sugestoes)
    controle_path = out_dir / f"controle_{Path(doc['fonte']).stem}.csv"
    gerar_controle_csv(checklist, controle_path)
    relatorio_path = out_dir / f"relatorio_{Path(doc['fonte']).stem}.md"
    gerar_relatorio_arquivo(doc, checklist, score, relatorio_path)
    print(json.dumps(
        {"score": score, "minuta": str(minuta_path), "controle": str(controle_path),
         "relatorio": str(relatorio_path),
         "sugestoes_aplicadas": bool(sugestoes)},
        ensure_ascii=False, indent=2))
    return 0


def _cmd_sugerir(args: argparse.Namespace) -> int:
    audit_json = Path(args.json)
    if not audit_json.exists():
        print(f"ERRO: JSON de auditoria não encontrado: {audit_json}", file=sys.stderr)
        return 1
    payload = json.loads(audit_json.read_text(encoding="utf-8"))
    doc = payload["doc"]
    checklist = payload["checklist"]
    sugestoes = gerar_sugestoes(checklist)
    out_dir = audit_json.parent
    destino = out_dir / f"sugestoes_{Path(doc['fonte']).stem}.md"
    gerar_sugestoes_arquivo(doc, sugestoes, destino)
    print(json.dumps(
        {"sugestoes": len(sugestoes), "arquivo": str(destino)},
        ensure_ascii=False, indent=2))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="prestacao_contas_nota_dez")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_audit = sub.add_parser("audit", help="Audita um PDF de diligência")
    p_audit.add_argument("pdf")
    p_audit.add_argument("--cache", default="/tmp/opencode/pcn_ocr_cache", help="Dir de cache OCR")
    p_audit.add_argument("--out", default="exemplos", help="Dir de saída")
    p_audit.add_argument("--workers", type=int, default=4)
    p_audit.set_defaults(func=_cmd_audit)

    p_exec = sub.add_parser("execute", help="Gera minuta + controle a partir do audit JSON")
    p_exec.add_argument("json")
    p_exec.add_argument("--aplicar", action="store_true",
                        help="Preenche células da minuta com sugestões marcadas [SUGESTÃO – REVISAR]")
    p_exec.set_defaults(func=_cmd_execute)

    p_sug = sub.add_parser("sugerir", help="Gera sugestões de preenchimento (para revisão humana)")
    p_sug.add_argument("json")
    p_sug.set_defaults(func=_cmd_sugerir)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())