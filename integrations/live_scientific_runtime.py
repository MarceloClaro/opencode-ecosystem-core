"""Execução externa delimitada de Hermes e MiroFish/OASIS (R667).

Um processo com exit=0 só completa o contrato se houver geração auditada do
modelo local e artefatos do próprio runtime. Nenhum motor externo é copiado.
"""
from __future__ import annotations

import csv
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
import json
import math
import os
from pathlib import Path
import re
import signal
import sqlite3
import subprocess
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit


DEFAULTS = {
    "hermes": "/home/marceloclaro/projetos/hermes-agent-r667",
    "mirofish": "/home/marceloclaro/projetos/MiroFish-Offline-AGPL",
}
ORIGINS = {
    "hermes": {"https://github.com/MarceloClaro/hermes-agent", "https://github.com/NousResearch/hermes-agent"},
    "mirofish": {"https://github.com/MarceloClaro/MiroFish-Offline", "https://github.com/666ghj/MiroFish"},
}


def validate_runtime_config(config: dict) -> dict:
    if not isinstance(config, dict):
        raise ValueError("A configuração deve ser um objeto JSON.")
    allowed = {"runtime", "prompt", "model", "base_url", "output_dir", "runtime_dir", "timeout_seconds"}
    if set(config) - allowed:
        raise ValueError("Campos de execução não permitidos.")
    out = dict(config)
    if out.get("runtime") not in DEFAULTS:
        raise ValueError("runtime deve ser hermes ou mirofish.")
    for key, maximum in (("prompt", 12000), ("model", 200), ("output_dir", 2000)):
        value = out.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > maximum or "\x00" in value:
            raise ValueError(f"{key} inválido.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/-]*", out["model"]):
        raise ValueError("Identificador de modelo inválido.")
    timeout = out.setdefault("timeout_seconds", 180)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 5 <= timeout <= 600:
        raise ValueError("timeout_seconds deve estar entre 5 e 600.")
    base = out.setdefault("base_url", "http://127.0.0.1:11434/v1")
    if not isinstance(base, str):
        raise ValueError("base_url inválida.")
    parsed = urlsplit(base)
    try:
        loopback = parsed.hostname == "localhost" or ip_address(parsed.hostname or "").is_loopback
        port = parsed.port
    except ValueError:
        loopback, port = False, None
    if (parsed.scheme != "http" or not loopback or parsed.username or parsed.password or
            parsed.query or parsed.fragment or parsed.path.rstrip("/") != "/v1" or port is None):
        raise ValueError("base_url deve apontar para /v1 em HTTP de loopback com porta explícita.")
    out["base_url"] = base.rstrip("/")
    runtime_dir = out.setdefault("runtime_dir", DEFAULTS[out["runtime"]])
    if not isinstance(runtime_dir, str) or not runtime_dir.strip() or len(runtime_dir) > 2000 or "\x00" in runtime_dir:
        raise ValueError("runtime_dir inválido.")
    return out


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def response_receipt(data: dict, request: bytes, response: bytes, http_status: int) -> dict:
    choices = data.get("choices", []) if isinstance(data, dict) else []
    message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
    usage = data.get("usage", {}) if isinstance(data, dict) else {}
    tokens = usage.get("completion_tokens", 0) if isinstance(usage, dict) else 0
    tokens = tokens if isinstance(tokens, int) and not isinstance(tokens, bool) and tokens > 0 else 0
    generated = bool(message.get("content") or message.get("tool_calls")) and tokens > 0 and http_status == 200
    return {"request_sha256": _hash(request), "response_sha256": _hash(response),
            "http_status": http_status, "generated_tokens": tokens, "generated": generated,
            "model_reported": data.get("model") if isinstance(data, dict) else None,
            "usage": usage, "evidence_scope": "local_model_response"}


def classify_execution(returncode: int, receipts: list, artifact: bool) -> dict:
    generated = any(r.get("generated") is True and r.get("http_status") == 200 and r.get("generated_tokens", 0) > 0 for r in receipts)
    completed = returncode == 0 and generated and artifact
    return {"status": "completed" if completed else "blocked", "inference_executed": generated,
            "runtime_artifact_observed": bool(artifact), "externally_validated": False,
            "human_peer_review": False, "scientific_claim_eligible": False}


def artifact_manifest(output: Path) -> dict:
    result = {}
    for path in sorted(output.rglob("*")):
        if path.is_file() and not path.is_symlink() and path.name != "manifest.json" and not path.name.endswith(".env"):
            size = path.stat().st_size
            dependency = path.relative_to(output).parts[:2] == ("hermes_home", "bin")
            maximum = 128 * 1024 * 1024 if dependency else 16 * 1024 * 1024
            if size > maximum:
                raise ValueError("Artefato excede o limite de 16 MiB.")
            sha = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(65536), b""):
                    sha.update(block)
            result[str(path.relative_to(output))] = {"path": str(path), "bytes": size,
                "sha256": sha.hexdigest(), "role": "runtime_dependency" if dependency else "runtime_artifact"}
    return result


class _AuditProxy:
    """Encaminha somente inferência local permitida; não guarda Authorization."""
    def __init__(self, base: str, model: str, output: Path, timeout: float, allow_tools: bool):
        self.receipts = []
        self.lock = threading.Lock()
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_POST(self):
                try:
                    if self.path != "/v1/chat/completions":
                        raise ValueError("endpoint não permitido")
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 0 < length <= 512 * 1024:
                        raise ValueError("requisição fora do limite")
                    data = json.loads(self.rfile.read(length))
                    if data.get("model") != model or data.get("stream") is True:
                        raise ValueError("modelo ou streaming não permitido")
                    if not allow_tools and data.get("tools"):
                        raise ValueError("ferramentas desabilitadas no Hermes")
                    data["max_tokens"] = min(data.get("max_tokens", 256) or 256, 256)
                    request = json.dumps(data, ensure_ascii=False, allow_nan=False).encode()
                    req = urllib.request.Request(base + "/chat/completions", data=request,
                                                 headers={"Content-Type": "application/json", "Authorization": "Bearer local-runtime"})
                    with urllib.request.urlopen(req, timeout=timeout) as upstream:
                        response = upstream.read(1024 * 1024 + 1)
                        if len(response) > 1024 * 1024:
                            raise ValueError("resposta fora do limite")
                        status = upstream.status
                    receipt = response_receipt(json.loads(response), request, response, status)
                    with outer.lock:
                        n = len(outer.receipts) + 1
                        if n > 16:
                            raise ValueError("limite de chamadas excedido")
                        (output / f"model_request_{n}.json").write_bytes(request)
                        (output / f"model_response_{n}.json").write_bytes(response)
                        outer.receipts.append(receipt)
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(response)))
                    self.end_headers()
                    self.wfile.write(response)
                except (ValueError, TypeError, OSError, urllib.error.URLError) as exc:
                    # A classe informa o diagnóstico, sem ecoar URLs/headers/token.
                    response = json.dumps({"error": {"message": f"Local audit rejected: {type(exc).__name__}"}}).encode()
                    self.send_response(502)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(response)))
                    self.end_headers()
                    self.wfile.write(response)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server.server_port}/v1"

    def __exit__(self, *_exc):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class LiveScientificRuntime:
    def _resolve(self, config: dict) -> dict:
        repo = Path(config["runtime_dir"]).expanduser().resolve()
        if not (repo / ".git").exists():
            raise ValueError("Checkout externo Git ausente.")
        origin = subprocess.run(["git", "remote", "get-url", "origin"], cwd=repo, text=True, capture_output=True, timeout=5, check=True).stdout.strip()
        origin = origin.removesuffix(".git")
        if origin not in ORIGINS[config["runtime"]]:
            raise ValueError("Origem Git não permitida para esse runtime.")
        entry = repo / ("hermes_cli/main.py" if config["runtime"] == "hermes" else "backend/scripts/run_twitter_simulation.py")
        candidates = [repo / ".venv/bin/python", repo / ".venv-externo/bin/python"]
        # MiroFish necessita o ambiente próprio Python3.11/OASIS já instalado.
        if config["runtime"] == "mirofish":
            candidates.reverse()
        python = next((p for p in candidates if p.is_file()), None)
        if python is None or not entry.is_file():
            raise ValueError("Entrada ou Python do runtime ausente.")
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True, timeout=5, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo, text=True, capture_output=True, timeout=5, check=True).stdout.strip())
        return {"repo": str(repo), "python": str(python), "entry": str(entry), "origin": origin,
                "commit": commit, "entry_sha256": _hash(entry.read_bytes()), "checkout_modified": dirty}

    def _command(self, config: dict, runtime: dict, output: Path, proxy_url: str) -> tuple[list, dict]:
        # Apenas variáveis operacionais e locais; nenhum segredo herdado.
        env = {key: os.environ[key] for key in ("PATH", "LANG", "LC_ALL", "HOME", "TMPDIR") if key in os.environ}
        env.update({"PYTHONUNBUFFERED": "1", "NO_PROXY": "127.0.0.1,localhost", "OPENAI_API_KEY": "local-runtime"})
        if config["runtime"] == "hermes":
            profile = output / "hermes_home"
            profile.mkdir()
            settings = {"model": {"provider": "custom", "default": config["model"], "base_url": proxy_url,
                                  "api_key": "local-runtime", "api_mode": "chat_completions", "streaming": False},
                        "platform_toolsets": {"cli": []}, "mcp_servers": {}, "agent": {"max_turns": 2},
                        "memory": {"memory_enabled": False, "user_profile_enabled": False},
                        "display": {"interface": "cli"}, "fallback_models": [],
                        "security": {"tirith_enabled": False}}
            (profile / "config.yaml").write_text(json.dumps(settings), encoding="utf-8")
            env.update({"HERMES_HOME": str(profile), "CUSTOM_BASE_URL": proxy_url, "CUSTOM_API_KEY": "local-runtime", "HERMES_SKIP_UPDATE_CHECK": "1"})
            argv = [runtime["python"], "-m", "hermes_cli.main", "chat", "--query-file", str(output / "prompt.txt"),
                    "--oneshot", "--quiet", "--provider", "custom", "--model", config["model"], "--max-turns", "2",
                    "--run-budget", str(max(1, config["timeout_seconds"] - 3)), "--ignore-rules", "--in", str(output)]
        else:
            env.update({"LLM_API_KEY": "local-runtime", "LLM_BASE_URL": proxy_url, "LLM_MODEL_NAME": config["model"],
                        "OPENAI_API_BASE_URL": proxy_url})
            scenario = {"simulation_id": "r667_local_probe", "simulation_requirement": config["prompt"], "llm_model": config["model"],
                        "time_config": {"total_simulation_hours": 1, "minutes_per_round": 60, "agents_per_hour_min": 2,
                                        "agents_per_hour_max": 2, "off_peak_activity_multiplier": 1},
                        "agent_configs": [{"agent_id": n, "activity_level": 1, "active_hours": list(range(24))} for n in range(2)],
                        "event_config": {"initial_posts": [{"poster_agent_id": 0, "content": config["prompt"]}]}}
            (output / "simulation_config.json").write_text(json.dumps(scenario, ensure_ascii=False), encoding="utf-8")
            with (output / "twitter_profiles.csv").open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["user_id", "name", "username", "user_char", "description"])
                for n, role in enumerate(("Pesquisador", "Revisor")):
                    writer.writerow([n, role, f"r667_{n}", f"Personagem sintético {role}. Responda brevemente em português. {config['prompt']}",
                                     "Perfil artificial de teste de integração; não é uma pessoa observada."])
            argv = [runtime["python"], runtime["entry"], "--config", str(output / "simulation_config.json"), "--max-rounds", "1", "--no-wait"]
        return argv, env

    def _artifact_observed(self, runtime: str, output: Path) -> bool:
        if runtime == "hermes":
            return (output / "stdout.txt").stat().st_size > 20
        db = output / "twitter_simulation.db"
        if not db.is_file():
            return False
        with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
            count = conn.execute("SELECT COUNT(*) FROM trace").fetchone()[0]
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            posts = conn.execute("SELECT COUNT(*) FROM post").fetchone()[0] if ("post",) in tables else 0
        (output / "oasis_summary.json").write_text(json.dumps({"trace_rows": count, "post_rows": posts,
            "population": "synthetic_profiles", "rounds_requested": 1, "external_oasis_database": True}), encoding="utf-8")
        return count >= 2 and posts >= 1

    def run(self, config: dict) -> dict:
        config = validate_runtime_config(config)
        output = Path(config["output_dir"]).expanduser().resolve()
        result = {"runtime": config["runtime"], "status": "blocked", "external_process_executed": False,
                  "inference_executed": False, "externally_validated": False, "human_peer_review": False,
                  "scientific_claim_eligible": False, "population": "synthetic_profiles" if config["runtime"] == "mirofish" else None}
        if output.exists():
            return {**result, "reason": "Diretório de saída já existe; resultado anterior preservado."}
        try:
            runtime = self._resolve(config)
            # A presença deve ser confirmada pelo servidor, antes da execução externa.
            with urllib.request.urlopen(config["base_url"] + "/models", timeout=10) as response:
                raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError("Inventário de modelos excede limite.")
            models = json.loads(raw)
            if config["model"] not in {item.get("id") for item in models.get("data", [])}:
                raise ValueError("Modelo solicitado não está disponível no endpoint local.")
            output.mkdir(parents=True, exist_ok=False)
            (output / "models.json").write_bytes(raw)
            (output / "prompt.txt").write_text(config["prompt"], encoding="utf-8")
            started = time.time()
            with _AuditProxy(config["base_url"], config["model"], output, config["timeout_seconds"], config["runtime"] == "mirofish") as proxy:
                argv, env = self._command(config, runtime, output, proxy.url)
                with (output / "stdout.txt").open("wb") as stdout, (output / "stderr.txt").open("wb") as stderr:
                    proc = subprocess.Popen(argv, cwd=runtime["repo"], env=env, stdout=stdout, stderr=stderr,
                                            shell=False, start_new_session=True)
                    result["external_process_executed"] = True
                    timed_out = False
                    try:
                        code = proc.wait(timeout=config["timeout_seconds"])
                    except subprocess.TimeoutExpired:
                        timed_out = True
                        os.killpg(proc.pid, signal.SIGTERM)
                        try:
                            proc.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            os.killpg(proc.pid, signal.SIGKILL)
                            proc.wait(timeout=3)
                        code = -1
                receipts = list(proxy.receipts)
            artifact = self._artifact_observed(config["runtime"], output) if code == 0 else False
            result.update(classify_execution(code, receipts, artifact))
            result.update({"process_returncode": code, "timeout": timed_out, "duration_seconds": round(time.time() - started, 3),
                           "model_calls": len(receipts), "model_receipts": receipts, "provenance": runtime,
                           "argv": argv, "output_dir": str(output), "generation_token_limit": 256})
            if result["status"] != "completed":
                result["reason"] = "Processo, geração auditada e artefato próprio não completaram o contrato; consulte os logs."
            result["limits"] = ["Inferência do modelo local executada não comprova validade científica.",
                                "Cenário de dois personagens sintéticos não representa uma população real."]
            (output / "execution.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            result["artifacts"] = artifact_manifest(output)
            (output / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            return result
        except (ValueError, OSError, RuntimeError, subprocess.SubprocessError, urllib.error.URLError, sqlite3.Error) as exc:
            result["reason"] = f"Runtime bloqueado: {type(exc).__name__}: {str(exc)[:300]}"
            if output.is_dir():
                (output / "blocked.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            return result
