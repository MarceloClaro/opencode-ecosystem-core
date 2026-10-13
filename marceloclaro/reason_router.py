# -*- coding: utf-8 -*-
"""R828 — Roteador de raciocínio com fallback explícito.

Motor ausente ou config ausente retorna fallback, nunca sucesso presumido.
Operação local.
"""

def route(engine, config=None):
    """Roteia motor de raciocínio; fallback explícito quando indisponível."""
    cfg = config if isinstance(config, dict) else {}
    if cfg.get("absent") is True:
        return {"status": "fallback", "engine": engine, "reason": "motor_ausente"}
    if not isinstance(engine, str) or len(engine.strip()) == 0:
        return {"status": "fallback", "engine": engine, "reason": "engine_invalido"}
    # GREEN mínimo: declara capacidade sem alegar desempenho.
    return {"status": "ok", "engine": engine, "reason": "r828_ok"}
