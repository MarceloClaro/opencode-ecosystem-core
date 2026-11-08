#!/usr/bin/env bash
# ============================================================================
# quantum_secret_guard.sh — bloqueia chave GJQ literal em fontes do livro.
# Não imprime o valor; lista apenas arquivos. Exit 0 = GRANTED, 1 = DENIED.
# Uso: quantum_secret_guard.sh [ARQUIVO_OU_DIR ...]
# ============================================================================
set -u
python3 - "$@" <<'PY'
import re
import sys
from pathlib import Path

roots = [Path(p) for p in sys.argv[1:]] or [
    Path("educacao_quantica_bohm/livro_pixel"),
    Path("educacao_quantica_bohm/scripts"),
    Path("livro-core/lean"),
    Path("integrations/livro_quantico_mcp.py"),
    Path("hooks/quantum_guards.py"),
]
patterns = [
    re.compile(r'GJQ_API_KEY\s*=\s*["\'][A-Za-z0-9_-]{16,}["\']'),
    re.compile(r'"api_key"\s*:\s*"[0-9a-f]{32}"', re.I),
]
exts = {".py", ".md", ".sh", ".json", ".toml", ".yaml", ".yml"}
found = []
for root in roots:
    if root.is_file():
        files = [root]
    elif root.is_dir():
        files = [p for p in root.rglob("*") if p.is_file() and p.suffix in exts]
    else:
        continue
    for path in files:
        if any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(pat.search(text) for pat in patterns):
            found.append(str(path))
if found:
    print("quantum_secret_guard: DENIED — chave literal em: " + ", ".join(found[:5]), file=sys.stderr)
    raise SystemExit(1)
print("quantum_secret_guard: GRANTED — nenhuma chave literal nas fontes inspecionadas")
PY
