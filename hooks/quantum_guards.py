# -*- coding: utf-8 -*-
"""Guardas da fábrica do livro quântico (SPEC-935-R1099).

Funções puras, sem rede e sem escrita fora do log de auditoria. Elas não
aprovam ciência: bloqueiam segredos literais, hardware sem simulação prévia e
claims de prova formal sem compilação verificável.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "educacao_quantica_bohm"
LEAN = ROOT / "livro-core" / "lean" / "QuantumTrails.lean"
AUDIT = Path.home() / ".cache" / "opencode-hooks" / "quantum-audit.jsonl"

_KEY_PATTERNS = (
    re.compile(r"GJQ_API_KEY\s*=\s*[\"'][A-Za-z0-9_\-]{16,}[\"']"),
    re.compile(r"[\"']api_key[\"']\s*:\s*[\"'][0-9a-f]{32}[\"']", re.I),
    re.compile(r"GJQ_API_KEY\s*[:=]\s*[A-Za-z0-9_\-]{16,}"),
)


def find_hardcoded_api_key(text: str) -> list[str]:
    """Retorna padrões encontrados, sem imprimir o valor da chave."""
    achados = []
    for i, padrao in enumerate(_KEY_PATTERNS):
        if padrao.search(text or ""):
            achados.append(f"padrao_{i + 1}")
    return achados


def check_hardware_without_sim(command: str, data_dir: Path | None = None) -> dict[str, Any]:
    """Se o comando pede --real, exige o JSON simulado do --only correspondente."""
    texto = command or ""
    if "--real" not in texto:
        return {"allow": True, "reason": "sem hardware"}
    m = re.search(r"--only\s+(E(?:0[1-9]|1[0-8]))", texto)
    if not m:
        return {"allow": True, "reason": "sem --only; o script exige simulação global"}
    exp_id = m.group(1)
    base = data_dir if data_dir is not None else BOOK / "dados_experimentos"
    caminho = base / f"{exp_id}.json"
    if not caminho.is_file():
        return {"allow": False, "reason": f"{exp_id} sem JSON simulado; rode --sim antes de --real"}
    return {"allow": True, "reason": f"{exp_id} tem JSON simulado"}


def check_lean_claim(text: str) -> dict[str, Any]:
    """Se o texto declara prova formal, exige Lean sem sorry/admit."""
    texto = text or ""
    if not re.search(r"\b(provado|verificado|machine-checked|compila sem)\b", texto, re.I):
        return {"allow": True, "reason": "sem claim de prova"}
    if not LEAN.is_file():
        return {"allow": False, "reason": "claim de prova sem arquivo Lean"}
    fonte = LEAN.read_text(encoding="utf-8")
    if re.search(r"\bsorry\b", fonte) or re.search(r"\badmit\b", fonte):
        return {"allow": False, "reason": "Lean contém sorry/admit"}
    return {"allow": True, "reason": "Lean presente, sem sorry/admit; compilação ainda deve ser executada"}


def audit(evento: str, payload: dict[str, Any]) -> bool:
    """Anexa evento JSONL com hash; nunca grava chaves."""
    try:
        safe = {k: ("[REDACTED]" if "key" in k.lower() or "token" in k.lower() else v)
                for k, v in payload.items()}
        safe["evento"] = evento
        safe["ts"] = datetime.now(timezone.utc).isoformat()
        safe["payload_sha256"] = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest()
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(safe, ensure_ascii=False) + "\n")
        return True
    except (OSError, TypeError, ValueError):
        return False


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--command", default="", help="comando bash a inspecionar")
    ap.add_argument("--text", default="", help="texto a inspecionar")
    args = ap.parse_args()
    chaves = find_hardcoded_api_key(args.command + "\n" + args.text)
    hardware = check_hardware_without_sim(args.command)
    lean = check_lean_claim(args.text)
    permitido = not chaves and hardware["allow"] and lean["allow"]
    resultado = {
        "allow": permitido,
        "hardcoded_key": chaves,
        "hardware": hardware,
        "lean": lean,
    }
    audit("quantum_guard", {"permitido": permitido, "command": args.command, "text": args.text})
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if permitido else 1


if __name__ == "__main__":
    raise SystemExit(main())
