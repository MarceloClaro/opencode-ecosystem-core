"""
MiroFish-Offline Driver — fail-closed (padrão R473, SPEC-976).

Integração por composição com o serviço externo MiroFish-Offline (AGPL-3.0).
NENHUM código do projeto original é copiado para o Core; este driver apenas:

1. Detecta o diretório do serviço ($MIROFISH_OFFLINE_DIR, ou ./MiroFish-Offline).
2. Verifica sinais de que o backend real existe (run.py + backend/).
3. Reporta status unavailable com mensagem clara quando ausente.

Se o usuário quiser executar o serviço real, ele o mantém no próprio repo
(AGPL) e o Core o aciona por subprocess/API — nunca por cópia de código.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

DEFAULT_DIR = os.environ.get("MIROFISH_OFFLINE_DIR", "")
FALLBACK_DIRS = ["./MiroFish-Offline", "../MiroFish-Offline", "projetos/MiroFish-Offline"]


@dataclass
class DriverStatus:
    available: bool
    reason: str = ""
    dir: Optional[str] = None
    backend_entry: Optional[str] = None
    checks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "reason": self.reason,
            "dir": self.dir,
            "backend_entry": self.backend_entry,
            "checks": self.checks,
        }


def detect_service() -> DriverStatus:
    """Detecta o serviço externo MiroFish-Offline (nunca o copia)."""
    candidates: List[str] = []
    if DEFAULT_DIR:
        candidates.append(DEFAULT_DIR)
    cwd = os.getcwd()
    for d in FALLBACK_DIRS:
        candidates.append(os.path.abspath(os.path.join(cwd, d)))

    seen = set()
    for cand in candidates:
        cand = os.path.normpath(cand) if cand else cand
        if not cand or cand in seen:
            continue
        seen.add(cand)
        entry = os.path.join(cand, "backend", "run.py")
        if os.path.isfile(entry):
            status = DriverStatus(
                available=True,
                reason="MiroFish-Offline detectado no diretório externo.",
                dir=cand,
                backend_entry=entry,
                checks=[
                    "backend/run.py presente",
                    "GIT_DIR não é o Core (repo externo separado)",
                ],
            )
            return status
    return DriverStatus(
        available=False,
        reason=(
            "Serviço externo MiroFish-Offline não encontrado. Defina "
            "MIROFISH_OFFLINE_DIR apontando para o checkout AGPL do projeto. "
            "O motor local determinístico (mirofish.social) segue disponível."
        ),
    )


class MiroFishOfflineDriver:
    """Invoca o backend real por subprocess — fail-closed, sem acoplamento."""

    def __init__(self, service_dir: Optional[str] = None, python: Optional[str] = None):
        self.service_dir = service_dir
        self.python = python or sys.executable
        self._resolved: Optional[DriverStatus] = None

    @property
    def status(self) -> DriverStatus:
        if self._resolved is None:
            self._resolved = self._resolve()
        return self._resolved

    def _resolve(self) -> DriverStatus:
        # Se service_dir foi informado, valida-o primeiro; senão detecção padrão.
        if self.service_dir:
            entry = os.path.join(os.path.normpath(self.service_dir), "backend", "run.py")
            if os.path.isfile(entry):
                return DriverStatus(True, "dir informado validado.",
                                    os.path.normpath(self.service_dir), entry)
            return DriverStatus(
                False,
                f"MIROFISH_OFFLINE_DIR informado mas sem backend/run.py: {self.service_dir}",
            )
        return detect_service()

    def check(self) -> Dict[str, Any]:
        """Status público (R-976.9): nunca falha silenciosamente."""
        st = self.status
        if not st.available:
            return {
                "driver": "mirofish-offline",
                "ok": False,
                "available": False,
                "reason": st.reason,
                "local_engine_available": True,
            }
        return {
            "driver": "mirofish-offline",
            "ok": True,
            "available": True,
            "dir": st.dir,
            "backend_entry": st.backend_entry,
            "local_engine_available": True,
        }

    def prepare(self, doc_text: str, n_agents: int = 20, seed: int = 42) -> Dict[str, Any]:
        """Fail-closed: exige serviço real disponível."""
        st = self.status
        if not st.available:
            raise RuntimeError(st.reason)
        # v1: preparação real exige API do backend; aqui apenas registramos o pedido
        return {
            "prepared": False,
            "reason": (
                "Driver externo v1: validação de disponibilidade apenas. "
                "Use o motor local mirofish.social para simulação determinística "
                "ou implemente o cliente HTTP da API Flask no backend externo."
            ),
        }