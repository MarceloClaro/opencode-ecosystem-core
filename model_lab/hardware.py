# -*- coding: utf-8 -*-
"""Probe de hardware local para treinamento didático (M5 — SPEC-935-R479).

Sem GPU (ou sem torch instalado), a limitação de hardware é documentada
explicitamente (SPEC-935-R471 CA6): nenhuma alegação de viabilidade de
treinamento é feita sem o hardware correspondente.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

_NO_GPU_LIMITATION = (
    "Limitação de hardware: sem GPU, treinamento 64M completo não é viável em "
    "horas; execução limitada a simulação didática e documentação, sem "
    "overclaim (SPEC-935-R471 CA6)."
)


class HardwareProbe:
    """Detecção de dispositivo para treinamento (injetável e sem rede)."""

    def __init__(self, device_factory: Optional[Callable[[], str]] = None) -> None:
        self._device_factory = device_factory or self._detect_device

    @staticmethod
    def _detect_device() -> str:
        try:
            import torch  # type: ignore

            if torch.cuda.is_available():
                return "cuda"
            return "cpu"
        except Exception:
            return "none"

    def probe(self) -> Dict[str, Any]:
        device = self._device_factory()
        if device == "cuda":
            note = "Aceleração CUDA detectada: treinamento curto viável em hardware local (depende da GPU)."
            limitation = "Treinamento curto 64M viável em hardware local; viabilidade integral depende da GPU e do tempo disponível."
        elif device == "cpu":
            note = "Aceleração apenas por CPU (torch presente sem CUDA): treinamento lento e limitado."
            limitation = _NO_GPU_LIMITATION
        else:
            note = "Sem aceleração detectada (torch ausente ou sem GPU)."
            limitation = _NO_GPU_LIMITATION
        return {"device": device, "note": note, "limitation": limitation}


default_hardware_probe = HardwareProbe()