# -*- coding: utf-8 -*-
"""Frontend de download opt-in (M6 — SciHubEVA, SPEC-935-R480/R471).

Empacota a GUI SciHubEVA como frontend do resolvedor de acesso restrito da
R470. A GUI **nunca altera a política**: todos os gates da R470 (enabled →
policy → allowlist → auth → rights → evidence → ask) são avaliados pela
fachada ``scientific_lab.restricted_resolver`` e o recibo entregue é o
``CLIExecutionReceipt`` canônico.

Comportamento (CA7):
- sem habilitação completa R470, nenhum caminho aciona SciHubEVA (denied com
  código específico e recibo);
- com habilitação completa, o despacho gera ``CLIExecutionReceipt`` com todos
  os campos obrigatórios; o download real permanece ``pending_manual_execution``
  (esta versão não executa binário, não persiste arquivo, não usa rede).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from scientific_lab.restricted_resolver import (
    EXIT_CODES,
    RestrictedRequest,
    dispatch_restricted,
    request_from_env,
)

SCIHUBEVA_RESOLVER = "scihubeva"

VALID_TARGET_TYPES = ("doi", "pmid", "url", "query")

# Sem capacidade real de rede/execução de binário nesta versão (CA8).


@dataclass
class SciHubEVARequest:
    """Alvo de download aceito pela GUI (um único tipo por requisição)."""

    target_type: str
    target_value: str


def validate_target(request: SciHubEVARequest) -> bool:
    """Valida o alvo no formato da GUI SciHubEVA (DOI/PMID/URL/query)."""
    if request.target_type not in VALID_TARGET_TYPES:
        return False
    value = str(request.target_value or "").strip()
    if not value:
        return False
    if request.target_type == "doi":
        return value.startswith("10.")
    if request.target_type == "url":
        return value.startswith(("http://", "https://"))
    return True


def launch_argv(request: SciHubEVARequest) -> List[str]:
    """Monta argumentos do frontend como lista de strings (nunca shell)."""
    return [
        SCIHUBEVA_RESOLVER,
        f"--{request.target_type}",
        str(request.target_value).strip(),
    ]


class SciHubEVAFrontend:
    """Frontend opt-in sobre a fachada R470 (fail-closed, GUI neutra)."""

    def __init__(self) -> None:
        self.resolver = SCIHUBEVA_RESOLVER

    def submit(
        self,
        request: SciHubEVARequest,
        confirm: bool = False,
        requested_policy: Optional[str] = None,
        executor: Optional[Callable[[List[str]], None]] = None,
    ) -> Tuple[int, Dict[str, Any], Optional[Dict[str, Any]]]:
        """Despacha a requisição através dos gates da R470.

        - ``requested_policy`` é **ignorado**: a GUI nunca altera a política
          efetiva (lida do ambiente pela fachada R470).
        - ``executor`` só é chamado quando a avaliação permite; por padrão é
          None (nenhuma execução real).
        """
        if not validate_target(request):
            return (
                EXIT_CODES.get("deny_policy", 1),
                {
                    "command": "restricted-resolve",
                    "resolver": SCIHUBEVA_RESOLVER,
                    "policy_effective": "deny",
                    "enabled_effective": False,
                    "authorization_id": None,
                    "decision": "denied",
                    "deny_code": "invalid_target",
                    "timestamp_utc": "",
                    "orchestrator": "marceloclaro",
                    "hash_sha256": "",
                    "note": "Alvo inválido para a GUI (formato não aceito).",
                },
                None,
            )

        # A GUI passa apenas o resolver; política/allowlist/autorização/rights/
        # evidence vêm do ambiente (request_from_env) — nunca do frontend.
        # ``requested_policy`` é deliberadamente NÃO repassado: se o fosse, teria
        # precedência sobre o ambiente na fachada R470, permitindo a GUI alterar
        # a política — vedado por esta spec.
        restricted = request_from_env(
            resolver=SCIHUBEVA_RESOLVER,
            confirm=confirm,
        )
        exit_code, cli_receipt, download_receipt = dispatch_restricted(
            restricted, executor=executor
        )
        return exit_code, cli_receipt, download_receipt


default_scihubeva_frontend = SciHubEVAFrontend()