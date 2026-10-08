# -*- coding: utf-8 -*-
"""
execute_notebook.py — Executa o notebook OdontoCA v1.3.5 sem alterar o original.

Injeta LOCAL_TABLE_S1 apontando para a copia local verificada por SHA-256, de
modo que a execucao nao dependa de rede nem do path /tmp original (que e
volatile). Grava o notebook executado em um arquivo separado e reporta o
resultado de cada celula de codigo.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

HERE = Path(__file__).resolve().parent.parent  # raiz do odonto/
DEFAULT_NB = HERE / "OdontoCA_v1_3_5_INTERFACE_REPRODUTIVEL.ipynb"
LOCAL_SOURCE = HERE / "manuscript_assets" / "robust_audit" / "Table_S1.xlsx"
EXPECTED_SHA = "b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def inject_local_source(nb, source_path: Path) -> bool:
    """Rewrite LOCAL_TABLE_S1_UI in the first code cell. True if injected."""
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        text = cell.source
        if "LOCAL_TABLE_S1_UI" not in text:
            continue
        old = 'LOCAL_TABLE_S1_UI = "" #@param {type:"string"}'
        if old not in text:
            print("  [aviso] padrao de LOCAL_TABLE_S1_UI nao reconhecido; "
                  "a execucao podera tentar download")
            return False
        cell.source = text.replace(
            old,
            f'LOCAL_TABLE_S1_UI = "{source_path}" '
            '#@param {type:"string"}  # injetado por execute_notebook.py',
        )
        return True
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebook", type=Path, default=DEFAULT_NB)
    ap.add_argument("--out", type=Path, default=HERE / "OdontoCA_v1_3_5_EXECUTED.ipynb")
    ap.add_argument("--timeout", type=int, default=3600, help="segundos por celula")
    ap.add_argument("--allow-download", action="store_true",
                    help="nao injetar fonte local; deixa o notebook baixar")
    args = ap.parse_args(argv)

    digest = sha256_file(LOCAL_SOURCE)
    print(f"fonte local SHA-256: {digest}")
    if digest != EXPECTED_SHA:
        print("FALHA-CLOSED: hash da fonte local diverge do fixado no manuscrito")
        return 2
    print("hash confere com o valor travado no manuscrito.")

    nb = nbformat.read(args.notebook, as_version=4)
    if not args.allow_download:
        ok = inject_local_source(nb, LOCAL_SOURCE)
        print(f"fonte local injetada: {ok}")

    client = NotebookClient(
        nb,
        timeout=args.timeout,
        kernel_name="python3",
        allow_errors=True,
        resources={"metadata": {"path": str(HERE)}},
    )
    started = time.time()
    try:
        client.execute()
    except CellExecutionError as exc:
        print(f"\nERRO DE EXECUCAO: {exc}")
        return 1
    elapsed = time.time() - started

    nbformat.write(nb, args.out)
    print(f"notebook executado gravado em: {args.out.name}  ({elapsed:.1f}s)")

    errors, ok, empty = [], 0, 0
    print("\n--- resultado por celula de codigo ---")
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        errs = [o for o in cell.get("outputs", []) if o.get("output_type") == "error"]
        head = cell.source.strip().splitlines()
        label = head[0][:58] if head else ""
        if errs:
            errors.append((i, errs[0].get("ename"), errs[0].get("evalue")))
            print(f"  {i:3d} ERRO  {errs[0].get('ename')}: {errs[0].get('evalue')}")
        elif cell.get("outputs"):
            ok += 1
        else:
            empty += 1
    print(f"\nresumo: {ok} com saida | {empty} sem saida | {len(errors)} com erro")
    if errors:
        print("\nERROS:")
        for i, name, val in errors:
            print(f"  celula {i}: {name}: {val}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
