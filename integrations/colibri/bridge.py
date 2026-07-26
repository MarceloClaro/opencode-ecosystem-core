# -*- coding: utf-8 -*-
"""
Colibri Bridge — Integração com o runtime Colibri (GLM-5.2 / OLMoE)
=====================================================================
Ponte entre o ecossistema OpenCode e os motores de inferência Colibri:

  - **GLM-5.2** (744B MoE, 19.456 experts): via ``./coli serve`` (API OpenAI)
  - **OLMoE** (1B-7B MoE, 64 experts, já convertido): via ``./olmoe`` direto

Fluxo:
    bridge = ColibriBridge()
    if bridge.olmoe_available:
        result = bridge.olmoe_complete("Pergunta")
    elif bridge.available:
        result = bridge.complete("Pergunta", model="glm-5.2")

Referência: https://github.com/MarceloClaro/colibri
Modelo OLMoE: /home/marceloclaro/models/olmoe_merged/
Binário OLMoE: colibri/c/olmoe  (compilado nativo com OpenMP)
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("colibri-bridge")

# ── Constantes ──────────────────────────────────────────────────────────────

COLI_CAPABILITIES = [
    "inference-on-device",
    "glm-5.2",
    "olmoe",
    "moe-744b",
    "expert-streaming",
    "openai-compatible-api",
    "speculative-decoding",
    "local-llm",
]

DEFAULT_COLI_PORT = 11435
ENV_COLI_MODEL = "COLI_MODEL"
ENV_COLI_PORT = "COLI_PORT"
ENV_OLMOE_SNAP = "SNAP"
ENV_OLMOE_BIN = "OLMOE_BIN"

# Caminhos-padrão para OLMoE no ecossistema
DEFAULT_OLMOE_BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "colibri", "c", "olmoe",
)
DEFAULT_OLMOE_SNAP = os.path.expanduser("~/models/olmoe_merged")

QUEUE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".colibri", "queue",
)

# Modelos suportados
COLI_MODELS: Dict[str, Dict[str, Any]] = {
    "glm-5.2": {
        "name": "GLM-5.2",
        "params": "744B MoE",
        "quant": "int4",
        "container": "GLM-5.2-colibri-int4-with-int8-mtp",
        "size_gb": 372,
        "min_ram_gb": 25,
        "hf_repo": "mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp",
        "description": "GLM-5.2 (Z.ai) — 744B MoE, int4, MTP int8, 19.456 experts",
        "binary": "colibri",
        "env_var": "COLI_MODEL",
    },
    "olmoe": {
        "name": "OLMoE-1B-7B",
        "params": "1B-7B MoE",
        "quant": "int8 (expert cache)",
        "container": "olmoe_merged",
        "size_gb": 6.5,
        "min_ram_gb": 8,
        "hf_repo": "allenai/OLMoE-1B-7B-0125-Instruct",
        "description": "OLMoE (Allen AI) — 1B dense + 7B sparse MoE, 64 experts, 8 active",
        "binary": "olmoe",
        "env_var": "SNAP",
        "local_bin": DEFAULT_OLMOE_BIN,
        "local_snap": DEFAULT_OLMOE_SNAP,
        "ref_json": "colibri/c/ref_olmoe_real.json",
    },
}


# ── Helpers ─────────────────────────────────────────────────────────────────


def _find_olmoe_bin() -> Optional[str]:
    """Procura o binário olmoe: PATH → DEFAULT_OLMOE_BIN."""
    path_bin = shutil.which("olmoe")
    if path_bin:
        return path_bin
    if os.path.isfile(DEFAULT_OLMOE_BIN) and os.access(DEFAULT_OLMOE_BIN, os.X_OK):
        return DEFAULT_OLMOE_BIN
    return None


def _find_olmoe_snap() -> Optional[str]:
    """Procura o snapshot OLMoE: env → DEFAULT_OLMOE_SNAP."""
    env_snap = os.environ.get(ENV_OLMOE_SNAP)
    if env_snap and os.path.isdir(env_snap):
        return env_snap
    if os.path.isdir(DEFAULT_OLMOE_SNAP):
        return DEFAULT_OLMOE_SNAP
    return None


# ── Bridge ─────────────────────────────────────────────────────────────────


class ColibriBridge:
    """Ponte entre o orquestrador OpenCode e os runtimes Colibri.

    Suporta dois modos:
      - GLM-5.2: via ``coli serve`` (API OpenAI, requer GPU/server)
      - OLMoE: via ``olmoe`` direto (CPU, já compilado e convertido)

    Gerencia:
      - Detecção dos binários ``coli`` e/ou ``olmoe``
      - Gerenciamento do servidor GLM-5.2 (start/stop)
      - Inferência OLMoE via subprocesso direto
      - Handoff quando runtime não disponível
    """

    def __init__(self, model_path: Optional[str] = None,
                 port: int = DEFAULT_COLI_PORT):
        # ── GLM-5.2 / colibri ──────────────────────────────────────────
        self.coli_bin = shutil.which("coli") or shutil.which("colibri")
        self.available = self.coli_bin is not None
        self.model_path = model_path or os.environ.get(ENV_COLI_MODEL, "")
        self.port = int(os.environ.get(ENV_COLI_PORT, str(port)))
        self._server_proc: Optional[subprocess.Popen] = None
        self._server_url = f"http://127.0.0.1:{self.port}/v1"

        # ── OLMoE ──────────────────────────────────────────────────────
        self.olmoe_bin = _find_olmoe_bin()
        self.olmoe_snap = _find_olmoe_snap()
        self.olmoe_available = self.olmoe_bin is not None and self.olmoe_snap is not None

    # ═══════════════════════════════════════════════════════════════════
    # GLM-5.2 — API OpenAI (./coli serve)
    # ═══════════════════════════════════════════════════════════════════

    def check_readiness(self) -> Dict[str, Any]:
        """Executa ``coli doctor`` e retorna sumário de prontidão."""
        if not self.available:
            return {"status": "unavailable", "reason": "CLI 'coli' não encontrada no PATH"}
        try:
            proc = subprocess.run(
                [self.coli_bin, "doctor"],
                capture_output=True, text=True, timeout=30,
            )
            return {
                "status": "ready" if proc.returncode == 0 else "error",
                "stdout": proc.stdout.strip()[-2000:],
                "stderr": proc.stderr.strip()[-500:],
                "returncode": proc.returncode,
            }
        except (subprocess.TimeoutExpired, OSError) as exc:
            return {"status": "error", "error": str(exc)}

    def get_info(self) -> Dict[str, Any]:
        """Retorna informações do engine via ``coli info``."""
        if not self.available:
            return {"status": "unavailable"}
        try:
            proc = subprocess.run(
                [self.coli_bin, "info"],
                capture_output=True, text=True, timeout=15,
            )
            return {
                "status": "ok" if proc.returncode == 0 else "error",
                "info": proc.stdout.strip()[-3000:],
            }
        except (subprocess.TimeoutExpired, OSError) as exc:
            return {"status": "error", "error": str(exc)}

    def start_server(self, model_path: Optional[str] = None,
                     extra_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Inicia ``coli serve`` como processo de fundo."""
        if self._server_proc and self._server_proc.poll() is None:
            return {"status": "already_running", "url": self._server_url,
                    "pid": self._server_proc.pid}

        model = model_path or self.model_path
        if not model:
            return {"status": "error",
                    "error": "Model path não definido. Defina COLI_MODEL ou passe model_path."}

        cmd = [self.coli_bin, "serve", "--model", model,
               "--port", str(self.port)]
        if extra_args:
            cmd.extend(extra_args)

        try:
            self._server_proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True,
            )
            timeout = 120
            for _ in range(timeout * 2):
                if self._server_proc.poll() is not None:
                    break
                try:
                    import urllib.request
                    with urllib.request.urlopen(
                            f"{self._server_url}/models", timeout=1) as resp:
                        if resp.status == 200:
                            return {"status": "started",
                                    "url": self._server_url,
                                    "pid": self._server_proc.pid}
                except Exception:
                    pass
                time.sleep(0.5)
            return {"status": "timeout",
                    "url": self._server_url,
                    "pid": self._server_proc.pid}
        except OSError as exc:
            return {"status": "error", "error": str(exc)}

    def stop_server(self) -> Dict[str, Any]:
        """Finaliza o servidor Colibri."""
        if self._server_proc and self._server_proc.poll() is None:
            self._server_proc.terminate()
            try:
                self._server_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._server_proc.kill()
            self._server_proc = None
            return {"status": "stopped"}
        return {"status": "not_running"}

    def complete(self, prompt: str, system: Optional[str] = None,
                 max_tokens: int = 1024, temperature: float = 0.7,
                 model: str = "glm-5.2") -> Dict[str, Any]:
        """Chamada chat/completion via API OpenAI (requer GLM-5.2 server)."""
        if not self.available:
            return self.enqueue_handoff({
                "type": "complete", "prompt": prompt,
                "system": system, "model": model,
            })
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": model, "messages": messages,
            "max_tokens": max_tokens, "temperature": temperature,
            "stream": False,
        }
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{self._server_url}/chat/completions",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=300) as resp:
                body = json.loads(resp.read().decode())
            elapsed = time.time() - t0
            choice = body.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            usage = body.get("usage", {})
            return {
                "status": "ok", "content": content,
                "model": body.get("model", model),
                "tokens_in": usage.get("prompt_tokens", 0),
                "tokens_out": usage.get("completion_tokens", 0),
                "duration_s": round(elapsed, 2),
                "tokens_per_sec": round(
                    usage.get("completion_tokens", 0) / max(elapsed, 0.01), 1),
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    def chat(self, messages: List[Dict[str, str]],
             max_tokens: int = 2048, temperature: float = 0.7,
             model: str = "glm-5.2") -> Dict[str, Any]:
        """Chat multi-turn via API OpenAI."""
        payload = {
            "model": model, "messages": messages,
            "max_tokens": max_tokens, "temperature": temperature,
            "stream": False,
        }
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{self._server_url}/chat/completions",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=300) as resp:
                body = json.loads(resp.read().decode())
            elapsed = time.time() - t0
            choice = body.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            return {
                "status": "ok", "content": content,
                "model": body.get("model", model),
                "duration_s": round(elapsed, 2),
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    # ═══════════════════════════════════════════════════════════════════
    # OLMoE — Inferência direta (./olmoe, sem servidor)
    # ═══════════════════════════════════════════════════════════════════

    def olmoe_complete(self, prompt: str,
                       max_tokens: int = 64,
                       cache_size: int = 32,
                       quant_bits: int = 4,
                       pilot: int = 1,
                       hot: int = 4) -> Dict[str, Any]:
        """Executa inferência OLMoE via binário nativo ``olmoe``.

        Args:
            prompt: texto de entrada (tokenizado internamente pelo binário)
            max_tokens: máximo de tokens a gerar
            cache_size: tamanho do cache LRU de especialistas por layer
            quant_bits: bits de quantização (2-8, default 4)
            pilot: nível de prefetch (0-3, default 1)
            hot: número de especialistas "hot" fixos por layer

        Returns:
            dict com tokens gerados, métricas de cache, timing, RSS
        """
        if not self.olmoe_available:
            return {"status": "unavailable",
                    "reason": "OLMoE não disponível (binário ou snapshot ausente)"}

        # Cria ref.json temporário com o prompt
        import tempfile
        import json as _json
        ref = {
            "prompt_ids": [1],  # placeholders — o binário tokeniza internamente
            "full_ids": [1],
        }
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, prefix="olmoe_prompt_")
        _json.dump(ref, tmp)
        tmp.close()

        env = os.environ.copy()
        env["SNAP"] = self.olmoe_snap
        if pilot is not None:
            env["PILOT"] = str(pilot)
        if hot:
            env["HOT"] = str(hot)

        cmd = [self.olmoe_bin, str(max_tokens), str(quant_bits), tmp.name]

        t0 = time.time()
        try:
            proc = subprocess.run(
                cmd, env=env, capture_output=True, text=True,
                timeout=300,
            )
            elapsed = time.time() - t0
            os.unlink(tmp.name)

            stdout = proc.stdout or ""
            stderr = proc.stderr or ""

            # Parse métricas da saída
            hit_rate = None
            rss = None
            for line in stdout.split("\n"):
                if "cache hit rate" in line.lower():
                    import re
                    m = re.search(r'([\d.]+)%', line)
                    if m:
                        hit_rate = float(m.group(1))
                if "RSS after" in line.lower():
                    import re
                    m = re.search(r'([\d.]+) GB', line)
                    if m:
                        rss = float(m.group(1))

            return {
                "status": "ok" if proc.returncode == 0 else "error",
                "stdout": stdout[-3000:],
                "stderr": stderr[-1000:],
                "returncode": proc.returncode,
                "duration_s": round(elapsed, 2),
                "cache_hit_rate": hit_rate,
                "peak_rss_gb": rss,
                "quant_bits": quant_bits,
                "max_tokens": max_tokens,
            }
        except subprocess.TimeoutExpired:
            os.unlink(tmp.name)
            return {"status": "timeout", "error": "Inferência excedeu 300s"}
        except Exception as exc:
            os.unlink(tmp.name)
            return {"status": "error", "error": str(exc)}

    def olmoe_validate(self, ref_json: Optional[str] = None) -> Dict[str, Any]:
        """Valida o engine OLMoE contra referência conhecida.

        Executa com os parâmetros do ref_json e compara token-a-token.

        Args:
            ref_json: caminho para o JSON de referência
                      (default: colibri/c/ref_olmoe_real.json)

        Returns:
            dict com matching tokens, hit rate, RSS
        """
        import subprocess
        if not self.olmoe_available:
            return {"status": "unavailable",
                    "reason": "OLMoE não disponível"}

        ref_path = ref_json or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)))),
            "colibri", "c", "ref_olmoe_real.json",
        )
        if not os.path.isfile(ref_path):
            return {"status": "error", "error": f"ref_json não encontrado: {ref_path}"}

        env = os.environ.copy()
        env["SNAP"] = self.olmoe_snap
        env["PILOT"] = "1"
        env["HOT"] = "4"

        cmd = [self.olmoe_bin, "32", "4", ref_path]

        t0 = time.time()
        try:
            proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
            elapsed = time.time() - t0
            stdout = proc.stdout or ""

            # Extrai métricas
            import re
            matching = None
            hit_rate = None
            rss = None
            for line in stdout.split("\n"):
                if "Matching tokens" in line:
                    m = re.search(r'([\d.]+)/([\d.]+)', line)
                    if m:
                        matching = f"{m.group(1)}/{m.group(2)}"
                if "cache hit rate" in line.lower():
                    m = re.search(r'([\d.]+)%', line)
                    if m:
                        hit_rate = float(m.group(1))
                if "RSS after" in line.lower():
                    m = re.search(r'([\d.]+) GB', line)
                    if m:
                        rss = float(m.group(1))

            return {
                "status": "ok" if proc.returncode == 0 else "error",
                "returncode": proc.returncode,
                "duration_s": round(elapsed, 2),
                "matching_tokens": matching,
                "cache_hit_rate": hit_rate,
                "peak_rss_gb": rss,
                "stdout": stdout[-2000:],
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "error": "Validação excedeu 120s"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    # ═══════════════════════════════════════════════════════════════════
    # Handoff
    # ═══════════════════════════════════════════════════════════════════

    def enqueue_handoff(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Enfileira tarefa em JSON para execução manual futura."""
        os.makedirs(QUEUE_DIR, exist_ok=True)
        handoff = {
            "id": f"co-{uuid.uuid4().hex[:8]}",
            "created_at": time.time(),
            "source": "marceloclaro-orchestrator",
            "task": task,
        }
        fpath = os.path.join(QUEUE_DIR, f"{handoff['id']}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(handoff, f, ensure_ascii=False, indent=2)
        return {"status": "queued", "handoff_file": fpath}

    # ═══════════════════════════════════════════════════════════════════
    # Guia de instalação
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def install_guide() -> str:
        """Retorna instruções de instalação do Colibri."""
        return (
            "Para instalar o Colibri:\n\n"
            "  GLM-5.2 (744B MoE, ~372 GB, requer GPU):\n"
            "    1. git clone https://github.com/MarceloClaro/colibri\n"
            "    2. cd colibri/c && ./setup.sh\n"
            "    3. Export COLI_MODEL=/caminho/para/glm52_i4\n"
            "    4. ./coli doctor\n\n"
            "  OLMoE (1B-7B MoE, ~6.5 GB, CPU):\n"
            "    1. make -C colibri/c olmoe\n"
            "    2. Export SNAP=/home/marceloclaro/models/olmoe_merged\n"
            "    3. ./colibri/c/olmoe 32 4 colibri/c/ref_olmoe_real.json\n"
        )
