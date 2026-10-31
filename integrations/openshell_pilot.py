# -*- coding: utf-8 -*-
"""Piloto OpenShell (R992): preflight, plano de ensaios e recibos de evidência.

Instalação/inventário, execução observada e isolamento comprovado são estados
distintos. Nenhum recibo promove confiança, validação externa ou certifica
isolamento por si: somente execução real observada pode ser relatada como tal.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from typing import Any, Dict, List


def _which(name: str) -> str | None:
    return shutil.which(name)


def _version(cli: str) -> str | None:
    try:
        return subprocess.check_output([cli, "--version"], text=True,
                                       stderr=subprocess.DEVNULL, timeout=30).strip().splitlines()[0]
    except Exception:
        return None


def _container_health(runtime: str) -> str:
    try:
        subprocess.check_output([runtime, "info", "--format", "{{.Version}}"],
                                text=True, stderr=subprocess.DEVNULL, timeout=30)
        return "ready"
    except Exception:
        return "unknown"


def preflight() -> Dict[str, Any]:
    """Inventário somente leitura; nunca inicia processos persistentes nem rede."""
    cli = _which("openshell")
    runtime = _which("podman") or _which("docker")
    return {
        "status": "inventory",
        "openshell_cli": cli,
        "openshell_cli_version": _version(cli) if cli else None,
        "container_runtime": runtime,
        "container_runtime_health": _container_health(runtime) if runtime else "absent",
        "sandbox_executed": False,
        "isolation_verified": False,
        "isolation_scope": "none_observed",
        "external_validation": False,
        "confidence_promoted": False,
    }


def isolation_test_plan() -> List[Dict[str, Any]]:
    """Ensaios reais com controle positivo e negativo; nada é executado aqui."""
    return [
        {"id": "egress_hostname", "target": "egress", "positive": "reach allowed endpoint",
         "negative": "resolve/connect to a denied hostname must fail", "observed": None},
        {"id": "egress_ip", "target": "egress", "positive": "reach allowed IP",
         "negative": "connect to a raw denied IP must fail (no DNS bypass)", "observed": None},
        {"id": "egress_ipv6", "target": "egress", "positive": "allowed IPv6 route",
         "negative": "denied IPv6 must fail", "observed": None},
        {"id": "egress_dns", "target": "egress", "positive": "allowed DNS resolution",
         "negative": "denied domain must not resolve from inside", "observed": None},
        {"id": "filesystem_read", "target": "filesystem", "positive": "read mounted workspace",
         "negative": "read host path outside policy must fail", "observed": None},
        {"id": "filesystem_write", "target": "filesystem", "positive": "write into sandbox",
         "negative": "write host path outside policy must fail", "observed": None},
        {"id": "credential_egress", "target": "credentials", "positive": "synthetic credential stays in sandbox",
         "negative": "synthetic credential must not reach an unauthorized endpoint", "observed": None},
        {"id": "telemetry_optout", "target": "telemetry", "positive": "gateway starts with opt-out set",
         "negative": "verify opt-out flag is actually honored", "observed": None},
        {"id": "cleanup", "target": "lifecycle", "positive": "sandbox delete removes resources",
         "negative": "deleted sandbox leaves no running container", "observed": None},
        {"id": "recovery", "target": "lifecycle", "positive": "recreate sandbox after delete",
         "negative": "recreated sandbox does not inherit prior policy without explicit set", "observed": None},
    ]


def record_evidence(*, phase: str, observations: List[Dict[str, Any]],
                    artifacts: Dict[str, str] | None = None) -> Dict[str, Any]:
    """Recibo local com hashes; não promove confiança nem validação externa."""
    if not isinstance(phase, str) or not phase.strip() or len(phase) > 200:
        raise ValueError("Fase inválida")
    if not isinstance(observations, list) or not observations:
        raise ValueError("Observações são obrigatórias")
    normalized = []
    for obs in observations:
        if not isinstance(obs, dict) or "id" not in obs or "observed" not in obs:
            raise ValueError("Observação deve ter id e observed")
        normalized.append({"id": str(obs["id"])[:200], "observed": obs["observed"],
                           "detail": str(obs.get("detail", ""))[:2000]})
    hashes = {}
    for name, path in (artifacts or {}).items():
        hashes[name] = hashlib.sha256(open(path, "rb").read()).hexdigest()
    payload = {"schema": "openshell-pilot-v1", "phase": phase, "observations": normalized,
               "artifact_hashes": hashes, "sandbox_executed": True,
               "isolation_verified": False, "external_validation": False,
               "confidence_promoted": False, "human_review_required": True}
    return payload


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Piloto OpenShell: preflight e plano de ensaios.")
    parser.add_argument("operation", choices=("preflight", "plan"))
    args = parser.parse_args(argv)
    result = preflight() if args.operation == "preflight" else {"plan": isolation_test_plan(),
                                                                "sandbox_executed": False,
                                                                "isolation_verified": False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
