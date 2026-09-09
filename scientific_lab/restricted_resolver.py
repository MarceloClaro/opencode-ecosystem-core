"""Fachada mínima fail-closed para resolvedor de acesso restrito opcional (R470).

Aviso não-jurídico: este módulo não constitui parecer jurídico, não valida
titularidade nem autoriza violação de controles de acesso, paywalls, termos
contratuais ou medidas tecnológicas de proteção. A juridicidade varia por
jurisdição, contrato institucional e licença editorial; cabe exclusivamente ao
operador humano declarante. Referências normativas: SPEC-935-R470 (esta
capacidade opt-in), SPEC-935-R468 (scihub-cli ausente do padrão), SPEC-935-R469
(rejeição de default restrito com fail-closed) e SECURITY.md (vedação de
contorno sem autorização explícita). Hash de recibo provê auditabilidade,
não direito.

Comportamento: desabilitado por omissão; ausência de configuração equivale a
negação auditável. Nenhum binário externo é executado nesta versão: o caminho
autorizado retorna recibo `allowed` com status `pending_manual_execution`,
sem persistir arquivo e sem tráfego de rede. Argumentos são sempre
representados como lista de strings; esta fachada não realiza invocação via
interpretador de comandos.
"""
from __future__ import annotations

import datetime as _dt
import hashlib as _hashlib
import json as _json
import os as _os
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field

POLICY_DEFAULT = "open_science_only"

RESTRICTED_POLICIES = ("deny", "ask", "allow")

LIMITATIONS = [
    "no-redistribution",
    "original-rights-retained",
    "jurisdiction-dependent",
    "not-legal-advice",
]

EXIT_CODES = {
    "missing_enable": 10,
    "deny_policy": 11,
    "unknown_resolver": 12,
    "missing_authorization": 13,
    "missing_rights": 14,
    "missing_evidence": 15,
    "ask_confirmation_required": 16,
}

_ENV_ENABLED = "RESTRICTED_RESOLVER_ENABLED"
_ENV_POLICY = "RESTRICTED_RESOLVER_POLICY"
_ENV_ALLOWLIST = "RESTRICTED_RESOLVER_ALLOWLIST"
_ENV_AUTHZ = "RESTRICTED_RESOLVER_AUTHORIZATION_ID"
_ENV_RIGHTS = "RESTRICTED_RESOLVER_RIGHTS_BASIS"
_ENV_EVIDENCE = "RESTRICTED_RESOLVER_EVIDENCE_REF"


@_dataclass
class RestrictedRequest:
    """Pedido de resolução restrita (somente dados; sem efeitos colaterais)."""

    resolver: str | None = None
    authorization_id: str | None = None
    rights_basis: str | None = None
    evidence_ref: str | None = None
    enable: bool = False
    policy: str = "deny"
    allowlist: list = _field(default_factory=list)
    confirm: bool = False


def _now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_policy(value: object) -> str:
    text = str(value or "").strip().lower()
    if text in RESTRICTED_POLICIES:
        return text
    return "deny"


def _parse_allowlist(raw: object) -> list:
    if isinstance(raw, (list, tuple)):
        return [str(item).strip() for item in raw if str(item).strip()]
    text = str(raw or "").replace(";", ",")
    return [part.strip() for part in text.split(",") if part.strip()]


def _non_empty(value: object) -> bool:
    return bool(value is not None and str(value).strip())


def request_from_env(
    resolver: str | None = None,
    authorization_id: str | None = None,
    rights_basis: str | None = None,
    evidence_ref: str | None = None,
    enable: bool | None = None,
    policy: str | None = None,
    allowlist: object = None,
    confirm: bool = False,
) -> RestrictedRequest:
    """Constrói pedido a partir de env RESTRICTED_RESOLVER_* com defaults deny/0/vazio.

    Parâmetros explícitos não-None têm precedência sobre o ambiente; quando
    ausentes, lê-se o ambiente. Qualquer ambiguidade resulta em negação
    posterior (fail-closed): habilitação exige valor exato "1", política
    desconhecida normaliza para "deny" e allowlist ausente equivale a vazia.
    """
    if enable is None:
        enable = _os.getenv(_ENV_ENABLED, "").strip() == "1"
    if policy is None:
        policy = _normalize_policy(_os.getenv(_ENV_POLICY, "deny"))
    else:
        policy = _normalize_policy(policy)
    if allowlist is None:
        allowlist = _parse_allowlist(_os.getenv(_ENV_ALLOWLIST, ""))
    else:
        allowlist = _parse_allowlist(allowlist)
    if authorization_id is None:
        authorization_id = _os.getenv(_ENV_AUTHZ, "") or ""
    if rights_basis is None:
        rights_basis = _os.getenv(_ENV_RIGHTS, "") or ""
    if evidence_ref is None:
        evidence_ref = _os.getenv(_ENV_EVIDENCE, "") or ""
    return RestrictedRequest(
        resolver=resolver,
        authorization_id=authorization_id,
        rights_basis=rights_basis,
        evidence_ref=evidence_ref,
        enable=bool(enable),
        policy=policy,
        allowlist=list(allowlist),
        confirm=bool(confirm),
    )


def _hash_receipt(receipt: dict) -> str:
    canonical = {key: value for key, value in receipt.items() if key != "hash_sha256"}
    payload = _json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return _hashlib.sha256(payload).hexdigest()


def evaluate(request: RestrictedRequest) -> tuple:
    """Avalia gates na ordem: enabled, policy, allowlist, auth, rights, evidence, ask.

    Retorna (decision, deny_code, receipt). `decision` é "allowed" ou "denied";
    `deny_code` é None quando permitido. O recibo segue o contrato
    CLIExecutionReceipt da R470 com command, resolver, policy_effective,
    enabled_effective, authorization_id, decision, deny_code, timestamp_utc,
    orchestrator e hash_sha256.
    """
    policy_effective = _normalize_policy(request.policy)
    enabled_effective = bool(request.enable)
    allowlist_effective = _parse_allowlist(request.allowlist)
    resolver_name = str(request.resolver).strip() if _non_empty(request.resolver) else "none"
    authz = str(request.authorization_id).strip() if _non_empty(request.authorization_id) else None

    decision = "allowed"
    deny_code = None
    if not enabled_effective:
        decision, deny_code = "denied", "missing_enable"
    elif policy_effective == "deny":
        decision, deny_code = "denied", "deny_policy"
    elif policy_effective not in ("allow", "ask"):
        decision, deny_code = "denied", "deny_policy"
    elif resolver_name == "none" or resolver_name not in allowlist_effective:
        decision, deny_code = "denied", "unknown_resolver"
    elif not _non_empty(request.authorization_id):
        decision, deny_code = "denied", "missing_authorization"
    elif not _non_empty(request.rights_basis):
        decision, deny_code = "denied", "missing_rights"
    elif not _non_empty(request.evidence_ref):
        decision, deny_code = "denied", "missing_evidence"
    elif policy_effective == "ask" and not bool(request.confirm):
        decision, deny_code = "denied", "ask_confirmation_required"

    receipt = {
        "command": "restricted-resolve",
        "resolver": resolver_name,
        "policy_effective": policy_effective,
        "enabled_effective": enabled_effective,
        "authorization_id": authz,
        "decision": decision,
        "deny_code": deny_code,
        "timestamp_utc": _now_utc(),
        "orchestrator": "marceloclaro",
    }
    receipt["hash_sha256"] = _hash_receipt(receipt)
    return decision, deny_code, receipt


def build_argv(request: RestrictedRequest) -> list:
    """Monta argumentos do resolvedor como lista de strings.

    Retorna sempre uma lista, nunca uma string única, para que o chamador
    jamais precise de interpolação por interpretador de comandos. Documentado:
    nenhum caminho deste módulo executa binário externo nem recorre a shell.
    """
    resolver_name = str(request.resolver).strip() if _non_empty(request.resolver) else "none"
    return ["restricted-resolver", "--resolver", resolver_name]


def dispatch_restricted(request: RestrictedRequest, executor=None) -> tuple:
    """Despacha de forma contida, sem executar binário real nesta versão.

    Se a avaliação negar, retorna (exit_code específico, cli_receipt, None).
    Se permitir, monta a lista de argumentos, notifica o `executor` fake
    opcional (somente in-memory, que recebe a lista) e retorna
    (0, cli_receipt, download_receipt) com status `pending_manual_execution`,
    limitações fixas e sem persistir arquivo. Códigos: 10 missing_enable,
    11 deny_policy, 12 unknown_resolver, 13 missing_authorization,
    14 missing_rights, 15 missing_evidence, 16 ask_confirmation_required.
    """
    decision, deny_code, cli_receipt = evaluate(request)
    if decision != "allowed":
        return EXIT_CODES.get(deny_code, 1), cli_receipt, None
    argv = build_argv(request)
    if executor is not None:
        executor(argv)
    download_receipt = {
        "schema_version": "1.0",
        "command": "restricted-resolve",
        "resolver": cli_receipt["resolver"],
        "rights_basis_human_declared": str(request.rights_basis or "").strip()
        + " [nao verificado pelo sistema]",
        "authorization_id": cli_receipt["authorization_id"],
        "evidence_ref": str(request.evidence_ref or "").strip(),
        "limitations": list(LIMITATIONS),
        "status": "pending_manual_execution",
        "path": None,
        "bytes": 0,
        "sha256": None,
        "timestamp_utc": _now_utc(),
        "orchestrator": "marceloclaro",
    }
    return 0, cli_receipt, download_receipt
