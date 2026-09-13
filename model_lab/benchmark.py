# -*- coding: utf-8 -*-
"""Benchmark didático determinístico do currículo minimind (M5 — R479).

Simula uma curva de treinamento (pretrain) com seed fixa e gera um relatório
de reprodutibilidade. Nenhum gradiente é calculado; a simulação é hermética,
rápida e sem rede. Quando não há GPU, o relatório marca a limitação de
hardware explicitamente (CA6 da SPEC-935-R471).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class ReproducibilityReport:
    seed: int
    device: str
    steps: int
    losses: Tuple[float, ...]
    hardware_limitation: bool
    reproducibility_note: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "seed": str(self.seed),
            "device": self.device,
            "steps": str(self.steps),
            "final_loss": f"{self.losses[-1]:.6f}" if self.losses else "n/a",
            "hardware_limitation": str(self.hardware_limitation),
            "reproducibility_note": self.reproducibility_note,
            "losses": ", ".join(f"{x:.6f}" for x in self.losses),
        }


class MiniMindBenchmark:
    """Simulação determinística de treinamento 64M (pretrain breve)."""

    def __init__(self, seed: int, device: str = "none") -> None:
        self.seed = seed
        self.device = device

    def run(self, steps: int = 10) -> ReproducibilityReport:
        rng = random.Random(self.seed)
        initial = 2.0 + rng.uniform(0.0, 0.5)  # loss inicial varia com o seed
        decay = 0.05 + rng.uniform(0.0, 0.02)  # taxa de decaimento varia com o seed
        losses: List[float] = [initial * math.exp(-decay * i) for i in range(1, steps + 1)]

        hardware_limitation = self.device != "cuda"
        note = (
            f"Reprodutibilidade: seed {self.seed}, device {self.device}, "
            f"{steps} passos de pretrain simulado (64M). Resultados determinísticos "
            f"para o mesmo seed; limitação de hardware documentada e sem overclaim "
            f"(SPEC-935-R471 CA6)."
        )
        return ReproducibilityReport(
            seed=self.seed,
            device=self.device,
            steps=steps,
            losses=tuple(losses),
            hardware_limitation=hardware_limitation,
            reproducibility_note=note,
        )