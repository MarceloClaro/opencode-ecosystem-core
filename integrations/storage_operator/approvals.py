"""R1061 — aprovação de upload/purge vinculada ao hash do manifesto."""

from __future__ import annotations

import base64
import getpass
import hashlib
import hmac
import json
import os
import secrets
import socket
import time
from pathlib import Path

from . import policy

MAX_TTL = 300


class ApprovalError(Exception):
    def __init__(self, code: str, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _state(config: policy.StorageConfig) -> Path:
    path = Path(config.state_dir).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:
        pass
    return path


def _secret(config: policy.StorageConfig) -> bytes:
    target = _state(config) / "secret"
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


def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def issue_approval(config: policy.StorageConfig, scope: str, manifest_sha256: str,
                   *, ttl_seconds: int | None = None, now: int | None = None,
                   operator: str | None = None) -> dict:
    if scope not in {"upload", "purge"}:
        raise ApprovalError("scope_invalid", "escopo deve ser upload ou purge")
    if not isinstance(manifest_sha256, str) or len(manifest_sha256) != 64:
        raise ApprovalError("manifest_hash_invalid", "hash do manifesto inválido")
    ttl = 300 if ttl_seconds is None else ttl_seconds
    if type(ttl) is not int or not 1 <= ttl <= MAX_TTL:
        raise ApprovalError("ttl_invalid", f"TTL deve estar entre 1 e {MAX_TTL}")
    issued_at = int(time.time() if now is None else now)
    payload = {
        "v": 1, "scope": scope, "manifest_sha256": manifest_sha256,
        "exp": issued_at + ttl, "nonce": secrets.token_hex(16),
        "operator": operator or getpass.getuser(), "host": socket.gethostname(),
    }
    signature = hmac.new(_secret(config), _canonical(payload), hashlib.sha256).digest()
    return {"token": f"v1.{_b64(_canonical(payload))}.{_b64(signature)}",
            "expires_at": payload["exp"], "scope": scope,
            "manifest_sha256": manifest_sha256}


def verify_approval(config: policy.StorageConfig, token: str, scope: str,
                    manifest_sha256: str, *, now: int | None = None) -> dict:
    if not isinstance(token, str) or token.count(".") != 2 or not token.startswith("v1."):
        raise ApprovalError("approval_invalid", "token inválido")
    try:
        _, encoded, signature = token.split(".")
        payload = json.loads(_unb64(encoded))
        provided = _unb64(signature)
    except (ValueError, json.JSONDecodeError) as exc:
        raise ApprovalError("approval_invalid", "token inválido") from exc
    if not isinstance(payload, dict) or payload.get("v") != 1:
        raise ApprovalError("approval_invalid", "versão inválida")
    expected = hmac.new(_secret(config), _canonical(payload), hashlib.sha256).digest()
    if not hmac.compare_digest(provided, expected):
        raise ApprovalError("approval_invalid", "assinatura inválida")
    if payload.get("host") != socket.gethostname():
        raise ApprovalError("approval_mismatch", "aprovado em outro host")
    if payload.get("scope") != scope or payload.get("manifest_sha256") != manifest_sha256:
        raise ApprovalError("approval_mismatch", "aprovação não corresponde ao manifesto/escopo")
    current = int(time.time() if now is None else now)
    if int(payload.get("exp", 0)) <= current:
        raise ApprovalError("approval_expired", "aprovação expirada")
    nonce = payload.get("nonce")
    if not isinstance(nonce, str) or not nonce:
        raise ApprovalError("approval_invalid", "nonce ausente")
    used = _state(config) / "used"
    used.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(used / nonce, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ApprovalError("approval_reused", "aprovação já utilizada") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(str(payload["exp"]))
    return payload
