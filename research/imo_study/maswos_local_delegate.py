# -*- coding: utf-8 -*-
"""
MASWOS Local Delegate — R499
============================
Delegate_fn para o MaswosPipeline usando LLM on-device (Ollama local,
llama3.2) — roda os 16 estágios MASWOS offline, sem API externa.

Anti-overclaim: o LLM local apenas auxilia a redação/estruturação; os
dados empíricos do estudo (solvers determinísticos IMO) são reais e
independentes do LLM. O manuscrito declara o método de geração.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Callable

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"


def _complete(prompt: str, max_tokens: int = 900) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.4},
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read().decode())
    return body.get("response", "").strip()


def maswos_local_delegate(agent_id: str, capability: str, description: str) -> str:
    """Contrato MASWOS: (agent_id, capacidade, descrição) -> conteúdo str."""
    prompt = (
        f"Você é o estágio '{agent_id}' do pipeline acadêmico MASWOS "
        f"(capacidade: {capability}).\n"
        f"Tarefa do estágio: {description}\n\n"
        "Produza o conteúdo do estágio em português acadêmico formal, "
        "objetivo, com foco em um estudo empírico piloto sobre raciocínio "
        "automatizado em problemas da IMO. Seja específico e rigoroso; "
        "não invente dados externos."
    )
    out = _complete(prompt)
    return out or f"[estágio {agent_id} sem conteúdo gerado]"


def make_maswos_local_delegate() -> Callable[[str, str, str], str]:
    return maswos_local_delegate