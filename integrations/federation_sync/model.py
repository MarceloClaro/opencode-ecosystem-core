# -*- coding: utf-8 -*-
"""R1012 — modelo normalizado de artefatos federados.

Um único formato para plugin, MCP, agente, skill, comando e hook vindos de
Claude, ChatGPT/Codex, Antigravity CLI ou GitHub. O modelo é deliberadamente
puro: não lê disco, não abre rede e não executa nada.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
import unicodedata
from typing import Any, Dict, Iterable, Tuple

KINDS: Tuple[str, ...] = (
    "plugin", "mcp", "agent", "skill", "command", "hook", "prompt_pack", "lsp",
)
ECOSYSTEMS: Tuple[str, ...] = ("claude", "chatgpt", "antigravity", "github")
STATUSES: Tuple[str, ...] = ("admitted", "quarantined", "degraded", "blocked")
INSTALL_MODES: Tuple[str, ...] = (
    "metadata", "register_disabled", "materialize", "external",
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: Any, *, limit: int = 80) -> str:
    """Slug determinístico, sem acento e sem caixa — estável entre execuções."""

    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = _SLUG_RE.sub("-", text.lower()).strip("-")
    return (text or "sem-nome")[:limit].strip("-") or "sem-nome"


def canonical_json(value: Any) -> str:
    """JSON canônico para hash: chaves ordenadas, sem espaço variável."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), default=str)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _tuple_of_str(values: Iterable[Any]) -> Tuple[str, ...]:
    seen = []
    for value in values or ():
        text = str(value or "").strip()
        if text and text not in seen:
            seen.append(text)
    return tuple(seen)


@dataclass(frozen=True)
class FederatedItem:
    """Artefato externo normalizado, com proveniência e triagem anexadas."""

    ecosystem: str
    kind: str
    name: str
    parent: str = ""
    description: str = ""
    version: str = ""
    license: str = ""
    license_scope: str = ""
    source_uri: str = ""
    source_path: str = ""
    source_root: str = ""
    content_sha256: str = ""
    capabilities: Tuple[str, ...] = ()
    tags: Tuple[str, ...] = ()
    install_mode: str = "metadata"
    status: str = "degraded"
    reasons: Tuple[str, ...] = ()
    runtime_risk: str = "none"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.ecosystem not in ECOSYSTEMS:
            raise ValueError(f"ecossistema inválido: {self.ecosystem}")
        if self.kind not in KINDS:
            raise ValueError(f"tipo inválido: {self.kind}")
        if self.install_mode not in INSTALL_MODES:
            raise ValueError(f"modo de instalação inválido: {self.install_mode}")
        if self.status not in STATUSES:
            raise ValueError(f"estado inválido: {self.status}")

    # ------------------------------------------------------------------
    # Identidade
    # ------------------------------------------------------------------
    @property
    def item_id(self) -> str:
        base = f"{self.ecosystem}:{self.kind}:{slugify(self.name)}"
        if self.parent:
            base += f"@{slugify(self.parent)}"
        return base

    @property
    def admitted(self) -> bool:
        return self.status == "admitted"

    @property
    def installable(self) -> bool:
        """Instalável localmente de forma passiva (sem executar o artefato)."""

        return self.admitted and self.install_mode in {
            "register_disabled", "materialize",
        }

    # ------------------------------------------------------------------
    # Serialização
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.item_id,
            "ecosystem": self.ecosystem,
            "kind": self.kind,
            "name": self.name,
            "parent": self.parent,
            "description": self.description,
            "version": self.version,
            "license": self.license,
            "license_scope": self.license_scope,
            "source_uri": self.source_uri,
            "source_path": self.source_path,
            "source_root": self.source_root,
            "content_sha256": self.content_sha256,
            "capabilities": list(self.capabilities),
            "tags": list(self.tags),
            "install_mode": self.install_mode,
            "status": self.status,
            "reasons": list(self.reasons),
            "runtime_risk": self.runtime_risk,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "FederatedItem":
        data = dict(value)
        data.pop("id", None)
        data["capabilities"] = tuple(data.get("capabilities") or ())
        data["tags"] = tuple(data.get("tags") or ())
        data["reasons"] = tuple(data.get("reasons") or ())
        data["metadata"] = dict(data.get("metadata") or {})
        return cls(**data)

    # ------------------------------------------------------------------
    # Integração com o roteador de atenção do Core
    # ------------------------------------------------------------------
    def card(self) -> Dict[str, Any]:
        """Cartão no formato aceito por ``HarnessAttentionHead``."""

        return {
            "artifact_id": self.item_id,
            "agent_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "tags": list(self.tags),
            "capabilities": list(self.capabilities),
            "license": self.license,
            "origin": "third_party",
            "status": "ok" if self.admitted else self.status,
            "blocking": self.status == "blocked",
            "install_mode": self.install_mode,
            "ecosystem": self.ecosystem,
            "kind": self.kind,
        }


def digest_items(items: Iterable[FederatedItem]) -> str:
    """Digest do conjunto: independe da ordem de coleta."""

    payload = [item.to_dict() for item in sorted(items, key=lambda i: i.item_id)]
    return sha256_text(canonical_json(payload))
