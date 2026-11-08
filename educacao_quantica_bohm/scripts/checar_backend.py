#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checa se um backend da Tiangong é simulador ou hardware.

Uso:
    export GJQ_API_KEY="..."
    python educacao_quantica_bohm/scripts/checar_backend.py --backend Guoji08

O script imprime `configuration().simulator`, qubits, portas, acoplamento,
propriedades e status. Se a API estiver indisponível, registra o erro e explica
a regra de decisão; não inventa o tipo do backend.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from gjq_client import GJQRuntimeService

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados_hardware"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="Guoji08")
    args = ap.parse_args()

    chave = os.environ.get("GJQ_API_KEY", "").strip()
    if not chave:
        print("GJQ_API_KEY ausente; defina a chave apenas no ambiente.", file=sys.stderr)
        return 2

    try:
        servico = GJQRuntimeService(api_key=chave)
        backend = servico.backend(args.backend)
    except Exception as exc:
        print(f"API indisponível: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("\nRegra de decisão:")
        print("- simulator=True  -> simulador")
        print("- simulator=False -> hardware")
        print("- simulator=None  -> não declarado; manter 'resultados do backend'")
        return 3

    dados = {"backend": args.backend}
    try:
        cfg = backend.configuration()
        for campo in ("backend_name", "n_qubits", "simulator", "basis_gates",
                      "coupling_map", "max_shots"):
            dados[campo] = getattr(cfg, campo, None)
    except Exception as exc:
        dados["configuration_erro"] = f"{type(exc).__name__}: {exc}"

    for nome, fn in (("status", backend.status), ("properties", backend.properties)):
        try:
            valor = fn()
            dados[nome] = str(valor)[:4000]
        except Exception as exc:
            dados[f"{nome}_erro"] = f"{type(exc).__name__}: {exc}"

    print(json.dumps(dados, indent=2, ensure_ascii=False, default=str))
    sim = dados.get("simulator")
    if sim is True:
        veredito = "simulador"
        print("\nVEREDITO: simulador (simulator=True).")
    elif sim is False:
        veredito = "hardware"
        print("\nVEREDITO: hardware (simulator=False).")
    else:
        veredito = "nao_declarado"
        print("\nVEREDITO: tipo não declarado; mantenha a linguagem 'backend'.")

    DADOS.mkdir(parents=True, exist_ok=True)
    slug = "".join(c if c.isalnum() else "_" for c in args.backend).strip("_").lower()
    saida = DADOS / f"verificacao_{slug}.json"
    dados["veredito"] = veredito
    dados["timestamp"] = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    saida.write_text(json.dumps(dados, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"JSON: {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())