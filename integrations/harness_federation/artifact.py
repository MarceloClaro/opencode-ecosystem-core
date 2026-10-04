# -*- coding: utf-8 -*-
"""
Modelo canônico de artefato de agente multi-harness (SPEC-935-R621)
===================================================================
Normaliza skills, subagentes, comandos slash, hooks e especificações
originados nos ecossistemas Claude Code, Codex, Antigravity e ChatGPT em
uma única estrutura comparável, auditável e portável.

O ponto de partida é a recusa de duas práticas comuns e enganosas:

1. **Declarar o que se propõe em vez do que existe.** Um relatório que diz
   "Claude está integrado" porque existe um ``CLAUDE.md`` no repositório não
   inventariou nada. Aqui cada artefato só existe se o arquivo existir e for
   legível, e carrega o caminho de origem que o comprova.
2. **Confundir procedência.** Um plugin de terceiro no cache do Claude é
   artefato *de terceiro*, mesmo instalado localmente. O modelo carrega
   ``origin`` (``first_party`` / ``third_party`` / ``user``) para que o
   roteador possa penalizar origem não auditada.

Fail-closed: artefato incompleto nasce ``degraded`` com razão explícita, e o
emissor recusa-se a promovê-lo a artefato íntegro.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Tuple

try:  # PyYAML é dependência do SDD (sdd/spec_engine.py); o fallback cobre o caso raro.
    import yaml
except Exception:  # pragma: no cover - só dispara em ambiente sem PyYAML
    yaml = None  # type: ignore[assignment]

ECOSYSTEMS: Tuple[str, ...] = ("claude", "codex", "antigravity", "chatgpt")

KINDS: Tuple[str, ...] = ("skill", "agent", "command", "hook", "spec", "plugin", "prompt_pack")

# Formatos de destino que exigem `description` para o artefato ser utilizável.
_KINDS_REQUIRING_DESCRIPTION = frozenset({"skill", "agent", "command"})

# Degradações que rebaixam a confiança do artefato mas **não** impedem sua
# portabilidade. Licença não declarada é um aviso de procedência: o artefato
# pode ser lido eStudyado, apenas não deve ser reusado como material próprio
# sem revisão. As demais razões (nome ausente, origem inacessível, hook sem
# eventos) tornam o artefato inapto, e a portabilidade é recusada.
NON_BLOCKING_REASONS = frozenset({"license_undeclared"})

_FRONT_RE = re.compile(r"\A﻿?---[ \t]*\r?\n(?P<yaml>.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str, *, fallback: str = "artefato") -> str:
    """
    Converte um nome em slug kebab-case seguro para nome de arquivo.

    O acento é removido por NFD **antes** da substituição: sem isso,
    "Código" virava "c-digo", porque o caractere acentuado já não casa com
    `[a-z0-9]` e cada acento produzia um hífen próprio. A remoção é
    determinística e sem perda de identidade — "código" e "codigo" geram o
    mesmo destino, que é o comportamento desejado.
    """

    normalized = (value or "").strip().lower().replace("_", "-").replace("/", "-")
    decomposed = unicodedata.normalize("NFD", normalized)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    slug = _SLUG_RE.sub("-", without_accents).strip("-")
    return slug or fallback


def sha256_of(text: str) -> str:
    """Hash estável do conteúdo — é a prova de que o port não alterou o corpo."""

    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _file_sha256(path: str) -> str:
    """
    Hash do arquivo de origem em disco, ou string vazia se ele não existir.

    Confere com ``sha256sum``: é a verificação que um humano pode refazer sem
    depender deste código. Arquivo ausente devolve vazio (e não o hash do
    vazio), para não fabricar uma prova de integridade que ninguém confereu.
    """

    if not path or not os.path.isfile(path):
        return ""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _coerce_text(value: Any) -> str:
    """Achata qualquer escalar YAML em texto; ``None``/dict viram string vazia."""

    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _coerce_list(value: Any) -> List[str]:
    """Normaliza o campo de capacidades/tags em lista de strings não vazias."""

    if value is None:
        return []
    if isinstance(value, str):
        parts = [p.strip() for p in re.split(r"[,;|]", value)]
        return [p for p in parts if p]
    if isinstance(value, (list, tuple, set)):
        out: List[str] = []
        for item in value:
            if isinstance(item, dict):
                text = _coerce_text(item.get("name") or item.get("id"))
            else:
                text = _coerce_text(item)
            if text:
                out.append(text)
        return out
    text = _coerce_text(value)
    return [text] if text else []


def _minimal_yaml_load(raw: str) -> Dict[str, Any]:
    """
    Parser de último recurso para o subconjunto de YAML usado em frontmatters
    de skill/agent: ``chave: valor``, listas ``- item`` e listas inline ``[a, b]``.
    Só é acionado quando PyYAML está ausente ou falha.
    """

    result: Dict[str, Any] = {}
    current_key: Optional[str] = None
    for raw_line in raw.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        stripped = raw_line.strip()
        if stripped.startswith("- "):
            if current_key is None:
                continue
            result.setdefault(current_key, [])
            if isinstance(result[current_key], list):
                result[current_key].append(stripped[2:].strip().strip("'\""))
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value in (">", "|", ">-", "|-"):
            result[key] = ""
            current_key = key
            continue
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            result[key] = [p.strip().strip("'\"") for p in inner.split(",") if p.strip()]
            current_key = key
            continue
        if value == "":
            result[key] = []
            current_key = key
            continue
        result[key] = value.strip("'\"")
        current_key = key
    return result


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Separa o bloco YAML inicial do corpo do documento.

    Devolve ``({}, texto)`` quando não há frontmatter — o corpo continua
    íntegro e legível, apenas sem metadados.
    """

    if not text:
        return {}, ""
    match = _FRONT_RE.match(text)
    if not match:
        return {}, text
    raw_yaml = match.group("yaml")
    body = text[match.end():]
    data: Dict[str, Any] = {}
    if yaml is not None:
        try:
            loaded = yaml.safe_load(raw_yaml)
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = _minimal_yaml_load(raw_yaml)
    else:
        data = _minimal_yaml_load(raw_yaml)
    return data, body


def parse_hook_manifest(text: str) -> Tuple[List[str], List[str]]:
    """
    Lê um manifesto ``hooks.json`` no formato Claude
    (``{"hooks": {"<Evento>": [{"hooks": [{"command": "..."}]}]}}``)
    e devolve ``(eventos, comandos)``.

    Tolera o formatoachatado (``{"PreToolUse": [...]}``) e o formato lista
    (``[...]``) sem inventar eventos que não estejam no arquivo.
    """

    import json

    if not text or not text.strip():
        return [], []
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return [], []

    container: Any = data
    if isinstance(data, dict) and isinstance(data.get("hooks"), dict):
        container = data["hooks"]
    elif isinstance(data, dict) and isinstance(data.get("hooks"), list):
        return [], []

    events: List[str] = []
    commands: List[str] = []

    def _collect(node: Any) -> None:
        if isinstance(node, dict):
            command = node.get("command")
            if isinstance(command, str) and command.strip():
                commands.append(command.strip())
            for key in ("hooks", "command", "matcher", "type"):
                value = node.get(key)
                if isinstance(value, (list, dict)):
                    _collect(value)
                elif key == "command" and isinstance(value, str) and value.strip():
                    commands.append(value.strip())
        elif isinstance(node, list):
            for item in node:
                _collect(item)
        elif isinstance(node, str) and node.strip():
            commands.append(node.strip())

    if isinstance(container, dict):
        for event, matchers in container.items():
            events.append(str(event))
            _collect(matchers)
    elif isinstance(container, list):
        _collect(container)

    # Ordem de declaração, não alfabética: quem lê o manifesto precisa ver os
    # eventos na sequência em que o upstream os escreveu, porque essa ordem é
    # parte do comportamento do hook.
    return list(dict.fromkeys(events)), list(dict.fromkeys(commands))


def _detect_license(source_path: str, metadata: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Descobre a licença declarada do artefato. Devolve ``(licença, declarada?)``.

    Procura (a) campo de licença nos metadados do próprio artefato, (b) manifesto
    do plugin (``plugin.json`` / ``package.json``) na árvore ancestral, que é
    onde o Claude Code publica a licença do plugin. Inventar licença violaria o
    INV-R621.1, então a ausência é registrada como degradação, não preenchida.
    """

    declared = _coerce_text(metadata.get("license"))
    if declared:
        return declared, True

    directory = os.path.dirname(os.path.abspath(source_path)) if source_path else ""
    for _ in range(5):
        if not directory or not os.path.isdir(directory):
            break
        for manifest_name in ("plugin.json", "package.json", ".claude-plugin/plugin.json"):
            manifest_path = os.path.join(directory, manifest_name)
            if os.path.isfile(manifest_path):
                try:
                    import json

                    with open(manifest_path, "r", encoding="utf-8") as handle:
                        manifest = json.load(handle)
                except Exception:
                    manifest = None
                if isinstance(manifest, dict):
                    found = _coerce_text(manifest.get("license"))
                    if found:
                        return found, True
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return "", False


@dataclass(frozen=True)
class HarnessArtifact:
    """Artefato normalizado de um ecossistema de agente externo."""

    ecosystem: str
    kind: str
    name: str
    description: str
    source_path: str
    source_root: str = ""
    origin: str = "user"
    license: str = ""
    version: str = ""
    capabilities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    hook_events: List[str] = field(default_factory=list)
    hook_commands: List[str] = field(default_factory=list)
    content_sha256: str = ""
    source_file_sha256: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    degraded_reasons: List[str] = field(default_factory=list)
    duplicate_paths: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Identidade e estado
    # ------------------------------------------------------------------
    @property
    def artifact_id(self) -> str:
        """
        Identificador estável e **único**: ``ecossistema:kind:origem:slug``.

        O ``kind`` precisa entrar na chave. Sem ele, um prompt pack e uma
        política que compartilhem nome (o caso real de
        ``medicos/SKILL_CHATGPT.md`` e ``medicos/agents/openai.yaml``)
        colidiriam no mesmo identificador — e um sobrescreveria o outro no
        registro, silenciosamente.
        """

        return f"{self.ecosystem}:{self.kind}:{self.origin}:{slugify(self.name)}"

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def status(self) -> str:
        return "degraded" if self.degraded_reasons else "ok"

    @property
    def available(self) -> bool:
        """Só é disponível se o arquivo de origem realmente existir."""

        return bool(self.source_path) and os.path.isfile(self.source_path)

    # ------------------------------------------------------------------
    # Validação fail-closed
    # ------------------------------------------------------------------
    def validate(self) -> List[str]:
        """
        Devolve a lista de motivos de degradação. Uma lista vazia significa
        artefato apto a emissão; qualquer item impede a promoção silenciosa.
        """

        reasons: List[str] = []
        if self.ecosystem not in ECOSYSTEMS:
            reasons.append(f"unknown_ecosystem:{self.ecosystem}")
        if self.kind not in KINDS:
            reasons.append(f"unknown_kind:{self.kind}")
        if not self.name.strip():
            reasons.append("missing_name")
        if self.kind in _KINDS_REQUIRING_DESCRIPTION and not self.description.strip():
            reasons.append("missing_description")
        if not self.content_sha256:
            reasons.append("missing_content_sha256")
        if self.kind == "hook":
            if not self.hook_events:
                reasons.append("hook_without_events")
            if not self.hook_commands:
                reasons.append("hook_without_commands")
        if not self.available:
            reasons.append("source_not_found")
        return reasons

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "ecosystem": self.ecosystem,
            "kind": self.kind,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "source_path": self.source_path,
            "source_root": self.source_root,
            "origin": self.origin,
            "license": self.license,
            "version": self.version,
            "capabilities": list(self.capabilities),
            "tags": list(self.tags),
            "hook_events": list(self.hook_events),
            "hook_commands": list(self.hook_commands),
            "content_sha256": self.content_sha256,
            "source_file_sha256": self.source_file_sha256,
            "status": self.status,
            "available": self.available,
            "degraded_reasons": list(self.degraded_reasons),
            "duplicate_paths": list(self.duplicate_paths),
            "metadata": dict(self.metadata),
        }

    @property
    def blocking_reasons(self) -> List[str]:
        """
        Degradações que realmente impedem o uso do artefato.

        Licença não declarada é aviso, não bloqueio: tratá-la como bloqueio
        tornaria `unavailable` quase todo artefato de terceiros (a maioria dos
        plugins não declara licença por skill) e esvaziaria a cabeça `harness`
        justamente onde ela tem mais a dizer.
        """

        return [r for r in self.degraded_reasons if r not in NON_BLOCKING_REASONS]

    def agent_card(self) -> Dict[str, Any]:
        """
        Converte o artefato em *agent card* no formato consumido pelo
        ``AttentionRouter`` (agent_id, capabilities, status, confiança, carga).
        """

        blocked = bool(self.blocking_reasons) or not self.available
        return {
            "agent_id": self.artifact_id,
            "artifact_id": self.artifact_id,
            "name": self.name,
            "capabilities": list(self.capabilities),
            "status": "unavailable" if blocked else "available",
            "confidence_score": 0.0 if self.degraded_reasons else 0.7,
            "load": 0.0,
            "ecosystem": self.ecosystem,
            "kind": self.kind,
            "origin": self.origin,
            "license": self.license,
        }


def build_artifact(
    *,
    ecosystem: str,
    kind: str,
    name: str,
    description: str,
    source_path: str,
    body: str = "",
    source_root: str = "",
    origin: str = "user",
    license_declared: str = "",
    version: str = "",
    capabilities: Any = None,
    tags: Any = None,
    hook_events: Any = None,
    hook_commands: Any = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> HarnessArtifact:
    """
    Constrói o artefato aplicando a validação fail-closed uma única vez.

    Dois hashes, com finalidades distintas e que não devem ser confundidos:

    - ``content_sha256`` cobre só o **corpo** (sem o frontmatter). É o que
      sobrevive à reescrita de metadados no destino e o que a deduplicação usa.
    - ``source_file_sha256`` cobre o **arquivo inteiro** de origem. É a prova
      de integridade que se confere contra o disco com ``sha256sum``.
    """

    meta = dict(metadata or {})
    license_value = _coerce_text(license_declared) or _coerce_text(meta.get("license"))
    declared = bool(license_value)
    if not declared:
        license_value, declared = _detect_license(source_path, meta)

    artifact = HarnessArtifact(
        ecosystem=ecosystem,
        kind=kind,
        name=name.strip(),
        description=description.strip(),
        source_path=os.path.abspath(source_path) if source_path else "",
        source_root=source_root,
        origin=origin,
        license=license_value,
        version=_coerce_text(version),
        capabilities=_coerce_list(capabilities),
        tags=_coerce_list(tags),
        hook_events=_coerce_list(hook_events),
        hook_commands=_coerce_list(hook_commands),
        content_sha256=sha256_of(body),
        source_file_sha256=_file_sha256(source_path),
        metadata=meta,
    )
    reasons = artifact.validate()
    if not declared:
        # INV-R621.1: licença ausente nunca é preenchida por suposição. A
        # degradação é registrada como aviso — ela rebaixa a confiança no
        # roteamento, mas não torna o artefato ilegível.
        reasons.append("license_undeclared")
    return replace(artifact, degraded_reasons=reasons)
