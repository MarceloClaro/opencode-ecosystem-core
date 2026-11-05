"""R1063 — parser de comandos de voz em português e confirmação."""

from __future__ import annotations

import re

WAKE = re.compile(r"^(core|assistente|marcelo)\b[,:\s]*", re.IGNORECASE)
CLICK = re.compile(r"\b(?:clicar|clique|apertar|pressionar)\s+(?:em|no|na|o|a)?\s*(.+)$", re.IGNORECASE)
WRITE = re.compile(r"\b(?:escrever|digitar|ditar)\s+(.+)$", re.IGNORECASE)
READ = re.compile(r"\b(?:o que (?:está|esta) na tela|ler (?:a )?tela|descrever (?:a )?tela|onde estou)\b", re.IGNORECASE)
STOP = re.compile(r"\b(?:parar|pare|encerrar|sair|desligar)\b", re.IGNORECASE)
PRESS = re.compile(r"\b(?:apertar|pressionar|ativar)\b", re.IGNORECASE)
ASK = re.compile(r"\b(?:perguntar|pergunte|pedir|peça|opencode)\s+(.+)$", re.IGNORECASE)


def has_wake(text: str) -> bool:
    return bool(WAKE.search(text or ""))


def strip_wake(text: str) -> str:
    return WAKE.sub("", (text or "").strip(), count=1).strip()


def parse_command(text: str) -> dict:
    raw = (text or "").strip()
    if not has_wake(raw):
        return {"intent": "ambient", "text": raw}
    command = strip_wake(raw)
    if STOP.search(command):
        return {"intent": "stop"}
    if READ.search(command):
        return {"intent": "read"}
    match = CLICK.search(command)
    if match:
        return {"intent": "click", "target": match.group(1).strip(" .")}
    match = WRITE.search(command)
    if match:
        return {"intent": "write", "text": match.group(1).strip()}
    match = ASK.search(command)
    if match:
        return {"intent": "ask", "text": match.group(1).strip()}
    if PRESS.search(command):
        return {"intent": "press"}
    return {"intent": "unknown", "text": command}


def is_confirmation(text: str) -> bool:
    return bool(re.search(r"\b(sim|confirmo|confirmar|pode|claro|ok)\b", (text or "").casefold()))


def is_denial(text: str) -> bool:
    return bool(re.search(r"\b(não|nao|cancelar|cancela|pare)\b", (text or "").casefold()))
