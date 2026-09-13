# -*- coding: utf-8 -*-
"""Currículo de modelos pequenos reprodutíveis (M5 — minimind, SPEC-935-R479).

Material didático e plano determinístico inspirado no currículo minimind
(jingyaogong/minimind, Apache-2.0): tokenizer → pretrain → SFT → RLHF → DPO
→ MoE → distill → quant, para um modelo de 64M de parâmetros voltado a
pipelines científicos. Nenhum treinamento real é executado por este módulo.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List

MINIMIND_STAGES: tuple = (
    "tokenizer",
    "pretrain",
    "sft",
    "rlhf",
    "dpo",
    "moe",
    "distill",
    "quant",
)

_STAGE_DESCRIPTIONS = {
    "tokenizer": "Tokenização de corpus científico (BPE) com vocabulário de ~32k.",
    "pretrain": "Pré-treino autoregressivo (cross-entropy) em corpus aberto.",
    "sft": "Fine-tuning supervisionado com instruções científicas.",
    "rlhf": "Alinhamento por RLHF com feedback humano.",
    "dpo": "Otimização direta de preferências (DPO) sobre pares escolhido/rejeitado.",
    "moe": "Expansão Mixture-of-Experts para escala eficiente de parâmetros.",
    "distill": "Destilação para modelos on-device (LiteRT-LM/Colibri como alvos).",
    "quant": "Quantização (INT8/INT4) para implantação em hardware local.",
}

MODEL_CONFIG: Dict[str, Any] = {
    "name": "minimind-64M",
    "params_millions": 64,
}


class MiniMindCurriculum:
    """Plano didático determinístico do currículo minimind."""

    def __init__(self) -> None:
        self.model_config = dict(MODEL_CONFIG)

    def plan(self, seed: int) -> List[Dict[str, Any]]:
        rng = random.Random(seed)
        plan: List[Dict[str, Any]] = []
        for order, stage in enumerate(MINIMIND_STAGES):
            plan.append({
                "stage": stage,
                "order": order,
                "description": _STAGE_DESCRIPTIONS[stage],
                "epochs": 1 + rng.randrange(3),
                "learning_rate": round(rng.uniform(1e-5, 3e-4), 7),
                "batch_size": rng.choice([8, 16, 32]),
            })
        return plan


default_curriculum = MiniMindCurriculum()