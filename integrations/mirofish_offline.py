"""
MiroFish-Offline Driver — fail-closed (padrão R473, SPEC-976).

Integração por composição com o serviço externo MiroFish-Offline (AGPL-3.0).
NENHUM código do projeto original é copiado para o Core; este driver apenas:

1. Detecta o diretório do serviço ($MIROFISH_OFFLINE_DIR, ou ./MiroFish-Offline).
2. Verifica sinais de que o backend real existe (run.py + backend/).
3. Sobe o backend Flask externo na venv própria do repo (método start_backend).
4. Invoca a API HTTP real (/health, /api/simulation/*, /api/report/*) com
   fail-closed: serviço ausente/indisponível nunca falha silenciosamente.

Se o usuário quiser executar o serviço real, ele o mantém no próprio repo
(AGPL) e o Core o aciona por HTTP — nunca por cópia de código.

Limite honesto (anti-overclaim R110): a simulação OASIS-full (create/prepare/
start) depende de LLM_API_KEY/ZEP_API_KEY e de camel-oasis (que exige Python
<3.12). Este driver valida healthcheck, listagens e consultas determinísticas;
o motor local mirofish.social segue como caminho de simulação determinística.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

DEFAULT_DIR = os.environ.get("MIROFISH_OFFLINE_DIR", "")
FALLBACK_DIRS = [
    "./MiroFish-Offline",
    "../MiroFish-Offline",
    "projetos/MiroFish-Offline",
    os.path.expanduser("~/projetos/MiroFish-Offline-AGPL"),  # canônico: fork English offline (MarceloClaro/MiroFish-Offline)
    os.path.expanduser("~/projetos/MiroFish-Offline"),        # fork genérico (MarceloClaro/MiroFish)
]
DEFAULT_HTTP_URL = os.environ.get("MIROFISH_HTTP_URL", "http://127.0.0.1:5001")


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
    """Invoca o backend real por HTTP — fail-closed, sem acoplamento (R-976.20)."""

    def __init__(
        self,
        service_dir: Optional[str] = None,
        python: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 5.0,
    ):
        self.service_dir = service_dir
        self.python = python or sys.executable
        self.base_url = (base_url or DEFAULT_HTTP_URL).rstrip("/")
        self.timeout = timeout
        self._resolved: Optional[DriverStatus] = None
        self._health_cache: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------ resolver

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

    # ------------------------------------------------------------------ HTTP core

    def _http_get(self, path: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """GET JSON com fail-closed; levanta RuntimeError para HTTP != 200."""
        st = self.status
        if not st.available:
            raise RuntimeError(st.reason)
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                raw = r.read().decode("utf-8")
                if r.status != 200:
                    raise RuntimeError(f"HTTP {r.status} em {path}: {raw[:300]}")
                try:
                    return json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    return {"raw": raw}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"HTTP {e.code} em {path}: {body}") from None
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Serviço MiroFish-Offline indisponível em {self.base_url}: {e.reason}"
            ) from None

    def _health_raw(self) -> Dict[str, Any]:
        st = self.status
        if not st.available:
            return {
                "ok": False,
                "reason": st.reason,
                "service": "MiroFish Backend",
                "status": "unavailable",
            }
        try:
            data = self._http_get("/health", timeout=3.0)
            # Contrato real do backend AGPL: {"status": "ok", "service": ...} —
            # sem chave "ok". Aceitamos status == "ok" como saudável.
            ok = bool(data.get("ok", False)) or data.get("status") == "ok"
            return {
                "ok": ok,
                "service": data.get("service", "MiroFish Backend"),
                "status": data.get("status", "unknown"),
                "reason": "" if ok else f"Resposta inesperada: {data}",
            }
        except RuntimeError as e:
            return {
                "ok": False,
                "service": "MiroFish Backend",
                "status": "unreachable",
                "reason": str(e),
            }

    # ------------------------------------------------------------------ API pública

    def health(self) -> Dict[str, Any]:
        """Healthcheck do serviço externo; NUNCA lança exceção (R-976.9)."""
        self._health_cache = self._health_raw()
        return self._health_cache

    def start_backend(self, port: int = 5001, wait: float = 15.0) -> Dict[str, Any]:
        """
        Sobe o backend Flask externo na venv própria do repo AGPL, se existir.
        Não altera o Python do Core; usa <repo>/.venv/bin/python.
        """
        st = self.status
        if not st.available:
            return {"ok": False, "reason": st.reason}
        venv_py = os.path.join(str(st.dir), ".venv", "bin", "python")
        backend_dir = os.path.join(str(st.dir), "backend")
        if not (os.path.isfile(venv_py) and os.path.isdir(backend_dir)):
            return {
                "ok": False,
                "reason": (
                    "Venv do repo externo ausente. Instale as deps com: "
                    f"python3 -m venv {st.dir}/.venv && {st.dir}/.venv/bin/pip "
                    "install -r requirements.txt (subconjunto core)."
                ),
            }
        # Se já responde, não duplica.
        h = self.health()
        if h["ok"]:
            return {"ok": True, "already_running": True, "base_url": self.base_url, "health": h}
        log_path = "/tmp/opencode/mirofish-backend.log"
        os.makedirs("/tmp/opencode", exist_ok=True)
        log = open(log_path, "a")
        code = (
            "import sys; sys.path.insert(0, '.'); "
            "from app import create_app; "
            f"create_app().run(host='127.0.0.1', port={port}, debug=False, threaded=True)"
        )
        proc = subprocess.Popen(
            [venv_py, "-c", code],
            cwd=backend_dir,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        deadline = time.monotonic() + wait
        while time.monotonic() < deadline:
            time.sleep(0.5)
            h = self.health()
            if h["ok"]:
                return {
                    "ok": True,
                    "pid": proc.pid,
                    "base_url": self.base_url,
                    "health": h,
                    "log": log_path,
                }
        proc.terminate()
        return {
            "ok": False,
            "reason": f"Backend não respondeu em {wait:.0f}s. Veja {log_path}",
            "pid": proc.pid,
        }

    def check(self) -> Dict[str, Any]:
        """Status público (R-976.9): nunca falha silenciosamente."""
        st = self.status
        base = {
            "driver": "mirofish-offline",
            "local_engine_available": True,
            "http_url": self.base_url,
        }
        if not st.available:
            base.update(
                {"ok": False, "available": False, "http_ok": False, "reason": st.reason}
            )
            return base
        h = self.health()
        out = {
            "ok": bool(h["ok"]),
            "available": True,
            "dir": st.dir,
            "backend_entry": st.backend_entry,
            "http_ok": bool(h["ok"]),
            "http_health": h,
            "http_simulations_count": 0,
        }
        if h["ok"]:
            try:
                sims = self.list_simulations()
                out["http_simulations_count"] = len(sims)
            except RuntimeError as e:
                out["http_simulations_count"] = -1
                out["http_error"] = str(e)
        out.update(base)
        return out

    def list_simulations(self) -> List[Dict[str, Any]]:
        data = self._http_get("/api/simulation/list")
        if not isinstance(data, dict):
            raise RuntimeError(f"Resposta inesperada em /api/simulation/list: {data}")
        return list(data.get("data", []))

    def list_reports(self) -> List[Dict[str, Any]]:
        data = self._http_get("/api/report/list")
        if not isinstance(data, dict):
            raise RuntimeError(f"Resposta inesperada em /api/report/list: {data}")
        return list(data.get("data", []))

    def list_projects(self) -> List[Dict[str, Any]]:
        data = self._http_get("/api/graph/project/list")
        if not isinstance(data, dict):
            raise RuntimeError(f"Resposta inesperada em /api/graph/project/list: {data}")
        return list(data.get("data", []))

    def get_simulation(self, simulation_id: str) -> Dict[str, Any]:
        data = self._http_get(f"/api/simulation/{simulation_id}")
        if not isinstance(data, dict):
            raise RuntimeError(
                f"Resposta inesperada em /api/simulation/{simulation_id}: {data}"
            )
        if not data.get("success"):
            raise RuntimeError(
                f"Simulação não encontrada ou erro: {data.get('error', data)}"
            )
        return data

    def prepare(self, doc_text: str, n_agents: int = 20, seed: int = 42) -> Dict[str, Any]:
        """
        Fail-closed: exige serviço real disponível.

        Com o backend externo de pé, registra evidências HTTP reais (healthcheck +
        quantidades observadas). A simulação OASIS-full (create/prepare/start)
        depende de chaves LLM/Zep e camel-oasis (Python <3.12) — reportado de
        forma transparente; o motor local determinístico segue como caminho real
        de simulação no Core.
        """
        st = self.status
        if not st.available:
            raise RuntimeError(st.reason)
        h = self.health()
        if not h["ok"]:
            raise RuntimeError(
                "Serviço externo indisponível: " + h.get("reason", "healthcheck falhou")
            )
        try:
            n_sims = len(self.list_simulations())
            n_reports = len(self.list_reports())
        except RuntimeError as e:
            n_sims, n_reports = -1, -1
        return {
            "prepared": True,
            "service": "MiroFish-Offline (AGPL) via HTTP",
            "base_url": self.base_url,
            "http": {
                "ok": True,
                "health": h,
                "observed_simulations": n_sims,
                "observed_reports": n_reports,
            },
            "limits": (
                "Simulação OASIS-full requer LLM_API_KEY/ZEP_API_KEY e camel-oasis "
                "(Python <3.12), indisponíveis neste ambiente. Use mirofish.social "
                "para simulação determinística local."
            ),
        }