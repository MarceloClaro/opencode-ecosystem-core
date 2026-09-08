"""Entrada nativa do Pesquisador Universal v4.2 dentro do OpenCode Core."""
from __future__ import annotations
import json, sys
from pathlib import Path
from scientific_lab.runtime import core_compatibility, dispatch, native_status, runtime_status

HELP="""Pesquisador Universal v4.2 — Native Scientific Runtime

Nativos no Core (não exigem instalação externa):
  research/articles   busca/download open-science-only
  review              protocolo, ingest, screening humano, PRISMA
  evidence            anotações e Research Evidence Graph

Avançados com fallback v4.1 verificado enquanto são internalizados:
  mesh, mission, living, synthesis, grade, causal, federation, production

Comandos de diagnóstico:
  status | core-check | doctor
"""

def _repo_root() -> Path: return Path(__file__).resolve().parents[1]

def main(argv: list[str]|None=None) -> int:
    args=list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h","--help","help"}: print(HELP); return 0
    cmd,rest=args[0],args[1:]; root=_repo_root()
    if cmd=="status": print(json.dumps(runtime_status(root),ensure_ascii=False,indent=2)); return 0
    if cmd=="core-check":
        report=core_compatibility(root); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0 if report["compatible"] else 3
    if cmd=="doctor":
        core=core_compatibility(root); native=native_status(root)
        report={"core":core,"native_scientific_runtime":native,"overall":"healthy" if core["compatible"] and native["status"]=="ready" else "degraded"}
        print(json.dumps(report,ensure_ascii=False,indent=2))
        return 0 if report["overall"]=="healthy" else 3
    return dispatch(cmd,rest,checkout=root)

if __name__=="__main__": raise SystemExit(main())
