# -*- coding: utf-8 -*-
"""
Env Loader — carregador leve de `.env` (sem dependências) — SPEC-935-R128.
==========================================================================
Lê um arquivo `.env` (protegido pelo `.gitignore`) e injeta as variáveis
no ambiente do processo, para que o ecossistema reconheça chaves como
`OPENAI_API_KEY`/`OLLAMA_HOST` sem que o usuário precise exportá-las à
mão (importante para acessibilidade).

Princípios:
- Por padrão NÃO sobrescreve variáveis já definidas no ambiente
  (`override=False`) — o que já está no shell tem prioridade.
- Silencioso e à prova de falhas: `.env` ausente ou linha malformada não
  quebram nada.
- Nunca imprime valores (segredos não vão para log/saída).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Optional[str] = None, override: bool = False) -> int:
    """Carrega variáveis de um arquivo `.env` para `os.environ`.

    Retorna quantas variáveis foram efetivamente definidas. Não lança
    exceção se o arquivo não existir. Não imprime valores.
    """
    env_path = Path(path) if path else (_REPO_ROOT / ".env")
    if not env_path.exists():
        return 0

    defined = 0
    try:
        raw = env_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0

    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        if s.startswith("export "):
            s = s[len("export "):].lstrip()
        key, _, value = s.partition("=")
        key = key.strip()
        if not key:
            continue
        # remove aspas simples/duplas ao redor do valor, se houver
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if not override and key in os.environ:
            continue
        if value == "":
            continue  # não sobrescreve com vazio (modelo .env.example)
        os.environ[key] = value
        defined += 1
    return defined
