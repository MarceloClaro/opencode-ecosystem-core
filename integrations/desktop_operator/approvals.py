"""R1060 — aprovação humana de uso único para click/type.

O token é um HMAC local vinculado a comando, app, ref e hash do texto. Não é
assinatura criptográfica de identidade humana; é um gate operacional criado
somente pela CLI `approve`, nunca pelo MCP.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path

from . import policy

MAX_TTL = 300
SENSITIVE_BINDINGS = ("command", "app", "ref", "text_sha256")


class ApprovalError(Exception):
    def __init__(self, code: str, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _state(config: policy.PolicyConfig) -> Path:
    path = Path(config.state_dir).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:
        pass
    return path


def _secret(config: policy.PolicyConfig) -> bytes:
    state = _state(config)
    target = state / "secret"
    if target.is_file():
        data = target.read_bytes()
        if len(data) != 32:
            raise ApprovalError("secret_invalid", "segredo local inválido")
        return data
    material = secrets.token_bytes(32)
    try:
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return _secret(config)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(material)
    return material


def _text_hash(text: str | None) -> str | None:
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _payload(command: str, app: str, ref: str, text: str | None, exp: int, nonce: str) -> dict:
    return {
        "v": 1,
        "command": command,
        "app": app.casefold(),
        "ref": ref,
        "text_sha256": _text_hash(text),
        "exp": exp,
        "nonce": nonce,
    }


def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def issue_approval(
    config: policy.PolicyConfig,
    command: str,
    app: str,
    ref: str,
    *,
    text: str | None = None,
    ttl_seconds: int | None = None,
    now: int | None = None,
) -> dict:
    if command not in {"click", "type"}:
        raise ApprovalError("command_denied", "aprovação só existe para click/type")
    # Reaproveita a validação de política para não emitir token de alvo negado.
    policy.build_argv(command, config, app=app, ref=ref, text=text)
    ttl = config.approval_ttl_seconds if ttl_seconds is None else ttl_seconds
    if type(ttl) is not int or not 1 <= ttl <= MAX_TTL:
        raise ApprovalError("ttl_invalid", f"TTL deve estar entre 1 e {MAX_TTL} segundos")
    issued_at = int(time.time() if now is None else now)
    payload = _payload(command, app, ref, text, issued_at + ttl, secrets.token_hex(16))
    signature = hmac.new(_secret(config), _canonical(payload), hashlib.sha256).digest()
    return {
        "token": f"v1.{_b64(_canonical(payload))}.{_b64(signature)}",
        "expires_at": payload["exp"],
        "command": command,
        "app": app,
        "ref": ref,
        "text_sha256": payload["text_sha256"],
    }


def verify_approval(
    config: policy.PolicyConfig,
    token: str,
    command: str,
    app: str,
    ref: str,
    *,
    text: str | None = None,
    now: int | None = None,
) -> dict:
    if not isinstance(token, str) or token.count(".") != 2 or not token.startswith("v1."):
        raise ApprovalError("approval_invalid", "token de aprovação inválido")
    try:
        _, encoded, signature = token.split(".")
        payload = json.loads(_unb64(encoded))
        provided = _unb64(signature)
    except (ValueError, json.JSONDecodeError) as exc:
        raise ApprovalError("approval_invalid", "token de aprovação inválido") from exc
    if not isinstance(payload, dict) or payload.get("v") != 1:
        raise ApprovalError("approval_invalid", "versão de aprovação inválida")
    expected = hmac.new(_secret(config), _canonical(payload), hashlib.sha256).digest()
    if not hmac.compare_digest(provided, expected):
        raise ApprovalError("approval_invalid", "assinatura de aprovação inválida")
    current = int(time.time() if now is None else now)
    if int(payload.get("exp", 0)) <= current:
        raise ApprovalError("approval_expired", "aprovação expirada")
    bindings = {
        "command": command,
        "app": app.casefold(),
        "ref": ref,
        "text_sha256": _text_hash(text),
    }
    for key in SENSITIVE_BINDINGS:
        if payload.get(key) != bindings[key]:
            raise ApprovalError("approval_mismatch", f"aprovação não corresponde a {key}")
    nonce = payload.get("nonce")
    if not isinstance(nonce, str) or not nonce:
        raise ApprovalError("approval_invalid", "nonce ausente")
    used_dir = _state(config) / "used"
    used_dir.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(used_dir / nonce, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ApprovalError("approval_reused", "aprovação já utilizada") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(str(payload["exp"]))
    return payload
