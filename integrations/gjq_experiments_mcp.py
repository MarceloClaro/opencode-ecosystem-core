"""MCP local para executar e auditar experimentos no backend GJQ/Tiangong.

O servidor chama o script canônico `08_experimentos_18.py` como subprocesso.
Não lê a chave para o retorno, não a grava e não executa sem `confirm=True`.
A simulação local é pré-requisito para o hardware.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "educacao_quantica_bohm" / "laboratorio_leitor"
SCRIPT = LAB / "08_experimentos_18.py"
DADOS = LAB / "dados"
BACKENDS = ("Guoji08", "Baihua")
EXPERIMENTS = {
    "E01": "Base |0⟩", "E02": "Base |1⟩ e leitura", "E03": "Superposição H|0⟩",
    "E04": "Interferência H-Z-H", "E05": "Estado de Bell", "E06": "GHZ de 4 qubits",
    "E07": "CHSH", "E08": "Gerador quântico de números", "E09": "Codificação de amplitude",
    "E10": "Classificador XOR (VQC)", "E11": "Interferência de dois qubits",
    "E12": "QFT de 3 qubits", "E13": "Produto tensorial |01⟩", "E14": "Ruído de fase",
    "E15": "GHZ via QASM 2.0", "E16": "Esfera de Bloch", "E17": "Interferência de três qubits",
    "E18": "Amostragem binomial",
}
PY = ROOT / ".venv-quantum" / "bin" / "python"
if not PY.is_file():
    PY = Path(sys.executable)

_KEY_PATTERNS = (
    re.compile(r'GJQ_API_KEY\s*=\s*["\'][^"\']+["\']'),
    re.compile(r'"api_key"\s*:\s*"[^"]+"', re.I),
    re.compile(r'GJQ_API_KEY\s*[:=]\s*\S+'),
)


def _redact(text: str) -> str:
    for pat in _KEY_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text


def _key_present() -> bool:
    return bool(os.environ.get("GJQ_API_KEY", "").strip())


def _load(exp_id: str) -> dict[str, Any]:
    path = DADOS / f"{exp_id}.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _counts_audit(counts: Any, shots: int | None = None) -> dict[str, Any]:
    blocos = counts if isinstance(counts, list) else [counts]
    saida = []
    for i, bloco in enumerate(blocos):
        if not isinstance(bloco, dict):
            raise ValueError("counts inválidos")
        total = sum(int(v) for v in bloco.values())
        probs = {str(k): int(v) / total for k, v in bloco.items()} if total else {}
        ep = {k: (p * (1 - p) / total) ** 0.5 if total else 0 for k, p in probs.items()}
        saida.append({
            "bloco": i,
            "total": total,
            "shots_esperados": shots if shots is not None else total,
            "probabilidades": {k: round(v, 6) for k, v in probs.items()},
            "erro_padrao": {k: round(v, 6) for k, v in ep.items()},
            "alerta": None if shots is None or total == shots else f"soma {total} != shots {shots}",
        })
    return {"ok": all(item["alerta"] is None for item in saida), "blocos": saida}


def _validate(exp_id: str, backend: str, shots: int) -> None:
    if exp_id not in EXPERIMENTS:
        raise ValueError("exp_id deve ser E01–E18")
    if backend not in BACKENDS:
        raise ValueError("backend deve ser Guoji08 ou Baihua")
    if isinstance(shots, bool) or not isinstance(shots, int) or not 1 <= shots <= 10000:
        raise ValueError("shots deve estar entre 1 e 10000")


def _run(args: list[str], timeout: int) -> dict[str, Any]:
    comando = [str(PY), str(SCRIPT), *args]
    env = os.environ.copy()
    proc = subprocess.run(
        comando, cwd=str(LAB), capture_output=True, text=True,
        timeout=timeout, env=env,
    )
    return {
        "returncode": proc.returncode,
        "stdout": _redact(proc.stdout[-6000:]),
        "stderr": _redact(proc.stderr[-6000:]),
        "command": " ".join(comando[1:]),
    }


def create_server() -> FastMCP:
    server = FastMCP("gjq-experiments")
    readonly = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    execute = ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True)

    @server.tool(name="gjq_status", annotations=readonly)
    def gjq_status() -> dict:
        """Verifica chave, SDK, script e backends sem acessar a rede."""
        import importlib.util

        return {
            "api_key_present": _key_present(),
            "gjq_client_present": importlib.util.find_spec("gjq_client") is not None,
            "script_present": SCRIPT.is_file(),
            "python": str(PY),
            "experiments": len(EXPERIMENTS),
            "backends": list(BACKENDS),
            "executed": False,
        }

    @server.tool(name="gjq_catalog", annotations=readonly)
    def gjq_catalog() -> dict:
        """Lista E01–E18 e os comandos de simulação/hardware."""
        return {
            "experiments": [
                {
                    "id": exp_id,
                    "nome": nome,
                    "sim": f"python 08_experimentos_18.py --sim --only {exp_id}",
                    "hardware": f"python 08_experimentos_18.py --real --backend Guoji08 --only {exp_id}",
                }
                for exp_id, nome in EXPERIMENTS.items()
            ]
        }

    @server.tool(name="gjq_prepare", annotations=readonly)
    def gjq_prepare(
        exp_id: str,
        backend: Literal["Guoji08", "Baihua"] = "Guoji08",
        shots: int = 1024,
    ) -> dict:
        """Valida parâmetros e exige JSON simulado antes do hardware."""
        _validate(exp_id, backend, shots)
        sim = DADOS / f"{exp_id}.json"
        return {
            "exp_id": exp_id,
            "backend": backend,
            "shots": shots,
            "sim_present": sim.is_file(),
            "ready": sim.is_file() and _key_present(),
            "missing": [] if sim.is_file() else [f"rode --sim --only {exp_id}"],
            "api_key_present": _key_present(),
            "executed": False,
        }

    @server.tool(name="gjq_sim", annotations=execute)
    def gjq_sim(exp_id: str, shots: int = 1024, seed: int = 42, confirm: bool = False) -> dict:
        """Roda a simulação local; exige confirm=True e não usa rede."""
        _validate(exp_id, "Guoji08", shots)
        if confirm is not True:
            raise ValueError("confirm=True é obrigatório para executar")
        r = _run(["--sim", "--only", exp_id, "--shots", str(shots), "--seed", str(seed)], 180)
        return {**r, "result": _load(exp_id), "kind": "simulation"}

    @server.tool(name="gjq_run", annotations=execute)
    def gjq_run(
        exp_id: str,
        backend: Literal["Guoji08", "Baihua"] = "Guoji08",
        shots: int = 1024,
        timeout: int = 900,
        confirm: bool = False,
    ) -> dict:
        """Executa no backend; exige confirm=True, chave e simulação prévia."""
        _validate(exp_id, backend, shots)
        if confirm is not True:
            raise ValueError("confirm=True é obrigatório para executar no hardware")
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente", "executed": False}
        if not (DADOS / f"{exp_id}.json").is_file():
            return {"status": "blocked", "reason": f"rode --sim --only {exp_id}", "executed": False}
        r = _run(["--real", "--backend", backend, "--only", exp_id,
                  "--shots", str(shots), "--timeout", str(timeout)], timeout + 120)
        return {**r, "result": _load(exp_id), "kind": "hardware", "backend": backend}

    @server.tool(name="gjq_result", annotations=readonly)
    def gjq_result(exp_id: str) -> dict:
        """Lê o JSON do experimento e devolve simulado, real e auditoria."""
        if exp_id not in EXPERIMENTS:
            raise ValueError("exp_id deve ser E01–E18")
        d = _load(exp_id)
        if not d:
            return {"status": "missing", "exp_id": exp_id}
        real = d.get("real") or {}
        audit = _counts_audit(real.get("counts", []), real.get("shots")) if real.get("counts") else None
        return {"exp_id": exp_id, "simulado": d.get("simulado"), "real": real, "audit": audit}

    @server.tool(name="gjq_audit", annotations=readonly)
    def gjq_audit(exp_id: str) -> dict:
        """Audita task IDs, backend, shots, timestamp e soma dos counts."""
        if exp_id not in EXPERIMENTS:
            raise ValueError("exp_id deve ser E01–E18")
        d = _load(exp_id)
        real = d.get("real") or {}
        counts = real.get("counts") or []
        audit = _counts_audit(counts, real.get("shots")) if counts else {"ok": False, "blocos": []}
        return {
            "exp_id": exp_id,
            "backend": real.get("backend"),
            "shots": real.get("shots"),
            "task_ids": real.get("task_ids", []),
            "timestamp": real.get("timestamp"),
            "audit": audit,
            "limit": "Soma correta não prova fidelidade, emaranhamento ou vantagem quântica.",
        }

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
