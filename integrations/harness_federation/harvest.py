# -*- coding: utf-8 -*-
"""
HarnessHarvester — descoberta real de artefatos multi-harness (SPEC-935-R621)
===========================================================================
Varre o sistema de arquivos em busca de skills, subagentes, comandos slash,
hooks e especificações nos quatro ecossistemas de agente suportados:

- **Claude Code** — ``~/.claude`` (usuário, cache de plugins, marketplaces) e
  ``<repo>/.claude`` (projeto).
- **Antigravity (Google)** — ``~/.gemini/antigravity-cli/builtin/skills`` e
  ``<repo>/.antigravity``.
- **Codex (OpenAI)** — ``~/.codex`` e os manifestos ``.codex-plugin/plugin.json``
  espalhados pelo repositório.
- **ChatGPT** — prompt packs ``SKILL_CHATGPT.md`` e políticas ``openai.yaml``.

Princípio: *se o arquivo não existe, o artefato não existe*. Nenhuma contagem
é constante no código, e raízes que se sobrepõem são podadas na varredura para
que o mesmo arquivo nunca seja contado duas vezes.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import os
import re
import shutil
from collections import Counter
from dataclasses import replace
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .artifact import (
    HarnessArtifact,
    build_artifact,
    parse_frontmatter,
    parse_hook_manifest,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Subdiretórios que nunca contêm artefatos relevantes e tornariam a varredura
# lenta e ruidosa (grandes, gerados ou versionados por fora).
_SKIP_DIRS = frozenset({
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".ruff_cache", "LiteRT-LM-main", "backups", ".backups", "cache", "tmp",
    "conversations", "annotations", "crashes", "log", "scratch", "updater",
})

# Diretórios que já são nativos do próprio Core e não devem ser reingeridos
# como artefato "de fora" (o Core é a destino, não a origem).
_NATIVE_DIRS = frozenset({".opencode", "integrations", "transformer", "sdd", "mci", "tests", "specs"})

# SPEC-935-R648: raízes externas opt-in via ambiente.
# Formato: entradas separadas por os.pathsep, cada uma
# "ecossistema|rotulo|origem|caminho". Ecossistemas válidos: os quatro
# suportados; origem vazia vira "third_party". Malformadas/inexistentes são
# ignoradas (nunca fail). Raízes são máquina-específicas: nada de /tmp.
_EXTRA_ROOTS_ENV = "HARNESS_FED_EXTRA_ROOTS"
_EXTRA_ECOSYSTEMS = frozenset({"claude", "antigravity", "codex", "chatgpt"})

# Caminhos de origem que são cópias vendorizadas de terceiros.
_THIRD_PARTY_MARKERS = ("plugins/cache", "plugins/marketplaces", "deepseek-harness")

_MAX_DEPTH = 8


def _read_text(path: str, *, limit: int = 400_000) -> str:
    """Lê texto com teto de tamanho; arquivo ilegível devolve string vazia."""

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)
    except (OSError, UnicodeError):
        return ""


def _iter_files(
    root: str,
    *,
    suffixes: Tuple[str, ...],
    max_depth: int = _MAX_DEPTH,
    exclude_roots: Tuple[str, ...] = (),
) -> Iterable[str]:
    """
    Percorre ``root`` em profundidade limitada devolvendo arquivos casados.

    ``exclude_roots`` poda subárvores já cobertas por outra raiz da mesma
    federação — sem isso, ``~/.claude`` e ``~/.claude/plugins/cache`` contariam
    os mesmos ``SKILL.md`` duas vezes.
    """

    root = os.path.abspath(root)
    if not os.path.isdir(root):
        return
    pruned = tuple(
        os.path.abspath(path) for path in exclude_roots
        if os.path.abspath(path) != root and os.path.abspath(path).startswith(root + os.sep)
    )
    root_depth = root.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in _SKIP_DIRS
            and not d.startswith(".git")
            and not os.path.join(dirpath, d) in pruned
        ]
        if dirpath.count(os.sep) - root_depth >= max_depth:
            dirnames[:] = []
        dirnames.sort()
        for filename in sorted(filenames):
            if filename.endswith(suffixes):
                yield os.path.join(dirpath, filename)


def _origin_for(path: str, default: str = "first_party") -> str:
    """
    Classifica a procedência pelo caminho, sem adivinhação.

    ``third_party`` quando o caminho contém um marcador conhecido de cache,
    marketplace ou vendoring; caso contrário devolve ``default``.

    O ``default`` importa: chamar isto numa raiz do usuário (``~/.claude``,
    ``~/.codex``) com ``"first_party"`` descrevia como código do próprio projeto
    um arquivo que a pessoa escreveu — e pagava a procedência máxima (1.00) a um
    artefato que ninguém auditou. Quem é do usuário continua sendo do usuário.
    """

    normalized = os.path.abspath(path).replace(os.sep, "/").lower()
    for marker in _THIRD_PARTY_MARKERS:
        if f"/{marker}/" in f"/{normalized}" or normalized.startswith(f"{marker}/"):
            return "third_party"
    return default


# Diretórios genéricos que não nomeiam o artefato: ao nomear um artefato pelo
# seu diretório, é preciso subir até um nome que realmente identifique o dono.
_GENERIC_DIRS = frozenset({"references", "skills", "instructions", "assets", "prompts", "commands", "agents", "hooks"})

# Diretórios de versão (`6.1.1`, `1.0.0`, `unknown`, `v2`) identify o *release*,
# não o plugin. Nomear um artefato por eles colapsaria plugins distintos.
_VERSION_DIR_RE = re.compile(r"^(?:v?\d+(?:\.\d+)*|unknown|latest|main|dev)$", re.IGNORECASE)

_HEADING_RE = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*#*$")


def _leading_summary(text: str, *, max_chars: int = 240) -> str:
    """
    Deduz uma descrição a partir do corpo quando o frontmatter não a traz.

    Ordem: primeiro parágrafo SIGNIFICATIVO (isto é, não o título H1 nem
    badges de um parágrafo imediatamente abaixo dele), depois o primeiro
    cabeçalho. É inferência declarada, não invenção: a origem fica sempre em
    ``metadata['description_source']`` para que a auditoria possa conferir.
    """

    lines = [line.rstrip() for line in (text or "").splitlines()]
    title = ""
    for line in lines:
        heading = _HEADING_RE.match(line.strip())
        if heading:
            title = heading.group("title").strip()
            break

    paragraph: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if paragraph:
                break
            continue
        if _HEADING_RE.match(stripped):
            if paragraph:
                break
            continue
        if stripped.lstrip("![").startswith("!") or stripped.startswith(("http://", "https://", "<!--")):
            continue  # badge, imagem ou comentário: não descreve o artefato
        if title and stripped.lstrip("# ").strip() == title:
            continue  # repetição do próprio título
        paragraph.append(stripped)
        if sum(len(p) for p in paragraph) >= max_chars:
            break

    if paragraph:
        summary = " ".join(paragraph)[:max_chars].strip()
        if summary:
            return summary
    return title[:max_chars].strip()


def _owning_name(path: str, *, stop_at: str = "") -> str:
    """
    Nomeia um artefato pelo diretório que realmente lhe pertence.

    ``a/b/references/SKILL_CHATGPT.md`` não se chama "references": o nome é
    ``a/b``. A subida para em ``stop_at`` (a raiz do repositório, tipicamente)
    ou no primeiro diretório cujo nome não seja genérico nem de versão.
    """

    directory = os.path.dirname(os.path.abspath(path))
    stop = os.path.abspath(stop_at) if stop_at else ""
    while True:
        base = os.path.basename(directory)
        parent = os.path.dirname(directory)
        if stop and parent == stop:
            return base
        if base and base not in _GENERIC_DIRS and not _VERSION_DIR_RE.match(base) and parent != directory:
            return base
        if parent == directory:
            return base or os.path.splitext(os.path.basename(path))[0]
        directory = parent


class HarnessHarvester:
    """Inventaria artefatos dos ecossistemas Claude, Codex, Antigravity e ChatGPT."""

    def __init__(
        self,
        repo_root: str = REPO_ROOT,
        home: Optional[str] = None,
    ) -> None:
        self.repo_root = os.path.abspath(repo_root)
        self.home = os.path.abspath(home or os.path.expanduser("~"))
        self._scanned_roots: List[Dict[str, Any]] = []
        self._missing_roots: List[Dict[str, Any]] = []
        self._duplicate_count = 0

    # ------------------------------------------------------------------
    # Roots por ecossistema
    # ------------------------------------------------------------------
    def _extra_root_specs(self) -> List[Dict[str, Any]]:
        """Raízes opt-in de HARNESS_FED_EXTRA_ROOTS (SPEC-935-R648)."""
        raw = os.environ.get(_EXTRA_ROOTS_ENV, "")
        specs: List[Dict[str, Any]] = []
        for entry in raw.split(os.pathsep):
            entry = entry.strip()
            if not entry:
                continue
            parts = entry.split("|")
            if len(parts) != 4:
                continue
            ecosystem, label, origin, root = (p.strip() for p in parts)
            if ecosystem not in _EXTRA_ECOSYSTEMS or not label or not root:
                continue
            if not os.path.isdir(root):
                continue
            specs.append({
                "ecosystem": ecosystem,
                "root": os.path.abspath(root),
                "label": label,
                "origin": origin or "third_party",
            })
        return specs

    def _root_specs(self) -> List[Dict[str, Any]]:
        """Raízes varridas, marcadas com ecossistema, rótulo e origem."""

        return [
            # --- Claude Code (usuário + plugins + projeto) ---
            {"ecosystem": "claude", "root": os.path.join(self.home, ".claude"),
             "label": "claude:user", "origin": "user"},
            {"ecosystem": "claude", "root": os.path.join(self.home, ".claude", "plugins", "cache"),
             "label": "claude:plugin_cache", "origin": "third_party"},
            {"ecosystem": "claude", "root": os.path.join(self.home, ".claude", "plugins", "marketplaces"),
             "label": "claude:marketplace", "origin": "third_party"},
            {"ecosystem": "claude", "root": os.path.join(self.repo_root, ".claude"),
             "label": "claude:project", "origin": "first_party"},
            # --- Antigravity (Google) ---
            {"ecosystem": "antigravity",
             "root": os.path.join(self.home, ".gemini", "antigravity-cli", "builtin", "skills"),
             "label": "antigravity:builtin_skills", "origin": "first_party"},
            {"ecosystem": "antigravity", "root": os.path.join(self.repo_root, ".antigravity"),
             "label": "antigravity:project", "origin": "first_party"},
            {"ecosystem": "antigravity", "root": os.path.join(self.repo_root, "scripts", "cloud"),
             "label": "antigravity:cloud_scripts", "origin": "first_party"},
            # --- Codex (OpenAI) ---
            {"ecosystem": "codex", "root": os.path.join(self.home, ".codex"),
             "label": "codex:user", "origin": "user"},
            # padrão AGENTS.md (Codex/agents) vendorizado no repositório
            {"ecosystem": "codex", "root": os.path.join(self.repo_root, "deepseek-harness"),
             "label": "codex:agents_standard", "origin": "third_party"},
            # --- ChatGPT / Codex: varredura do repositório ---
            {"ecosystem": "chatgpt", "root": self.repo_root,
             "label": "chatgpt:project", "origin": "first_party"},
        ] + self._extra_root_specs()

    # ------------------------------------------------------------------
    # Construtores por tipo de artefato
    # ------------------------------------------------------------------
    def _skill_from(self, path: str, *, ecosystem: str, origin: str, source_root: str) -> HarnessArtifact:
        text = _read_text(path)
        front, body = parse_frontmatter(text)
        default_name = os.path.basename(os.path.dirname(path)) or os.path.basename(path).replace("SKILL.md", "").strip(".md")
        metadata = front.get("metadata") if isinstance(front.get("metadata"), dict) else {}
        return build_artifact(
            ecosystem=ecosystem,
            kind="skill",
            name=str(front.get("name") or default_name),
            description=str(front.get("description") or ""),
            source_path=path,
            body=body if front else text,
            source_root=source_root,
            origin=_origin_for(path, default="user") if origin == "user" else origin,
            version=str(front.get("version") or ""),
            capabilities=front.get("capabilities") or front.get("allowed-tools") or (metadata or {}).get("capabilities"),
            tags=[*(metadata or {}).get("tags", []), *(front.get("tags") or [])],
            metadata={"frontmatter_keys": sorted(str(k) for k in front)},
        )

    def _agent_from(self, path: str, *, ecosystem: str, origin: str, source_root: str) -> HarnessArtifact:
        text = _read_text(path)
        front, body = parse_frontmatter(text)
        # Um subagente sem frontmatter não é órfão: ele se descreve no
        # primeiro parágrafo ou no primeiro cabeçalho do corpo. Sem esse
        # fallback, todo subagente Markdown puro seria descartado como
        # "missing_description" e o inventário mentiria sobre a cobertura.
        description = str(front.get("description") or "")
        if not description:
            description = _leading_summary(body or text)
        return build_artifact(
            ecosystem=ecosystem,
            kind="agent",
            name=str(front.get("name") or os.path.basename(path)[: -len(".md")]),
            description=description,
            source_path=path,
            body=body if front else text,
            source_root=source_root,
            origin=_origin_for(path, default="user") if origin == "user" else origin,
            version=str(front.get("version") or ""),
            capabilities=front.get("capabilities") or front.get("tools") or front.get("allowed-tools"),
            tags=front.get("tags"),
            metadata={
                "mode": str(front.get("mode") or "subagent"),
                "model": str(front.get("model") or ""),
                "description_source": "frontmatter" if str(front.get("description") or "") else "body_inferred",
            },
        )

    def _command_from(self, path: str, *, ecosystem: str, origin: str, source_root: str) -> HarnessArtifact:
        text = _read_text(path)
        front, body = parse_frontmatter(text)
        return build_artifact(
            ecosystem=ecosystem,
            kind="command",
            name=os.path.basename(path)[: -len(".md")],
            description=str(front.get("description") or ""),
            source_path=path,
            body=body if front else text,
            source_root=source_root,
            origin=_origin_for(path, default="user") if origin == "user" else origin,
            capabilities=front.get("allowed-tools"),
            metadata={
                "disable_model_invocation": bool(front.get("disable-model-invocation", False)),
                "argument_hint": str(front.get("argument-hint") or ""),
            },
        )

    def _hook_from(self, path: str, *, ecosystem: str, origin: str, source_root: str) -> HarnessArtifact:
        text = _read_text(path)
        events, commands = parse_hook_manifest(text)
        # O manifesto vive em `<plugin>/hooks/hooks.json`: nomeá-lo "hooks"
        # colapsaria todos os plugins num artefato só.
        name = _owning_name(path) or os.path.basename(path).replace(".json", "")
        if name == os.path.basename(os.path.dirname(path)):
            name = os.path.basename(path).replace(".json", "")
        return build_artifact(
            ecosystem=ecosystem,
            kind="hook",
            name=name,
            description=f"Manifesto de hooks ({len(events)} eventos, {len(commands)} comandos)",
            source_path=path,
            body=text,
            source_root=source_root,
            origin=_origin_for(path, default="user") if origin == "user" else origin,
            hook_events=events,
            hook_commands=commands,
            metadata={"event_count": len(events), "command_count": len(commands)},
        )

    def _spec_from(self, path: str, *, ecosystem: str, origin: str, source_root: str, name: str) -> HarnessArtifact:
        text = _read_text(path)
        front, body = parse_frontmatter(text)
        first_line = next((ln.strip("# ").strip() for ln in (body or text).splitlines() if ln.strip()), "")
        return build_artifact(
            ecosystem=ecosystem,
            kind="spec",
            name=name,
            description=str(front.get("description") or first_line or "Especificação de projeto"),
            source_path=path,
            body=body if front else text,
            source_root=source_root,
            origin=_origin_for(path, default="user") if origin == "user" else origin,
            version=str(front.get("spec_id") or ""),
            tags=[front.get("spec_id")] if front.get("spec_id") else None,
            metadata={"heading": first_line[:200]},
        )

    def _codex_plugin_from(self, path: str, *, source_root: str) -> HarnessArtifact:
        text = _read_text(path)
        try:
            manifest = json.loads(text)
        except (ValueError, TypeError):
            manifest = {}
        interface = manifest.get("interface") if isinstance(manifest.get("interface"), dict) else {}
        prompts = interface.get("defaultPrompt") or []
        return build_artifact(
            ecosystem="codex",
            kind="plugin",
            name=str(interface.get("displayName") or manifest.get("name")
                     or os.path.basename(os.path.dirname(os.path.dirname(path)))),
            description=str(manifest.get("description") or interface.get("shortDescription") or ""),
            source_path=path,
            body=text,
            source_root=source_root,
            origin=_origin_for(path),
            license_declared=str(manifest.get("license") or ""),
            version=str(manifest.get("version") or ""),
            capabilities=interface.get("capabilities") or ["skills"],
            tags=manifest.get("keywords"),
            metadata={
                "developer_name": str(interface.get("developerName") or ""),
                "default_prompts": [str(p) for p in prompts if isinstance(p, str)],
                "category": str(interface.get("category") or ""),
                "skills_dir": str(manifest.get("skills") or ""),
            },
        )

    def _chatgpt_pack_from(self, path: str, *, source_root: str, name: str) -> HarnessArtifact:
        text = _read_text(path)
        front, body = parse_frontmatter(text)
        lines = [ln.strip() for ln in (body or text).splitlines() if ln.strip()]
        subtitle = next((ln.lstrip("> ").strip() for ln in lines[:12] if ln.startswith(">")), "")
        return build_artifact(
            ecosystem="chatgpt",
            kind="prompt_pack",
            name=name,
            description=str(front.get("description") or subtitle or "Prompt pack para Custom GPT"),
            source_path=path,
            # `body if front else text`: um prompt pack pode ter frontmatter e
            # corpo vazio. Com `body or text`, o corpo vazio fazia cair no
            # arquivo inteiro e o hash passava a cobrir o frontmatter — o que
            # quebra a prova de "corpo verbatim" exatamente no caso mais frágil.
            body=body if front else text,
            source_root=source_root,
            origin=_origin_for(path),
            version=str(front.get("versao") or front.get("version") or ""),
            tags=[front.get("categoria")] if front.get("categoria") else None,
            metadata={"target": "chatgpt.custom_gpt.instructions"},
        )

    def _openai_policy_from(self, path: str, *, source_root: str, name: str) -> HarnessArtifact:
        text = _read_text(path)
        data: Any = None
        try:
            import yaml  # noqa: PLC0415 - dependência opcional em tempo de carga

            data = yaml.safe_load(text)
        except Exception:
            data = None
        if not isinstance(data, dict):
            from .artifact import _minimal_yaml_load  # noqa: PLC0415

            data = _minimal_yaml_load(text)
        policy = data.get("policy") if isinstance(data.get("policy"), dict) else data
        return build_artifact(
            ecosystem="chatgpt",
            kind="spec",
            name=name,
            description=str(policy.get("description") or f"Política de invocação para {name}"),
            source_path=path,
            body=text,
            source_root=source_root,
            origin=_origin_for(path),
            capabilities=[key for key in ("allow", "deny") if key in policy],
            metadata={
                "allow_implicit_invocation": policy.get("allow_implicit_invocation"),
                "disable_model_invocation": policy.get("disable_model_invocation"),
            },
        )

    def _handoff_from(self, path: str, *, source_root: str) -> HarnessArtifact:
        """Handoff pendente do Antigravity vira artefato de tipo ``spec``."""

        text = _read_text(path)
        try:
            data = json.loads(text)
        except (ValueError, TypeError):
            data = {}
        prompt = data.get("prompt") or data.get("task") or ""
        return build_artifact(
            ecosystem="antigravity",
            kind="spec",
            name=str(data.get("id") or os.path.splitext(os.path.basename(path))[0]),
            description=f"Handoff pendente: {str(prompt)[:160]}" if prompt else "Handoff pendente do Antigravity",
            source_path=path,
            body=text,
            source_root=source_root,
            origin="first_party",
            metadata={"state": str(data.get("status") or data.get("state") or "queued")},
        )

    # ------------------------------------------------------------------
    # Varredura
    # ------------------------------------------------------------------
    def discover(self) -> List[HarnessArtifact]:
        """Executa a varredura completa e devolve os artefatos normalizados."""

        self._scanned_roots = []
        self._missing_roots = []
        self._duplicate_count = 0
        specs = self._root_specs()
        all_roots = tuple(spec["root"] for spec in specs)
        by_path: Dict[str, HarnessArtifact] = {}
        by_content: Dict[Tuple[str, str, str], HarnessArtifact] = {}

        def _add(artifact: HarnessArtifact) -> None:
            """
            Deduplicação em dois níveis.

            Por caminho: a mesma raiz nunca varre o mesmo arquivo duas vezes.
            Por conteúdo: árvores duplicadas (um clone aninhado do mesmo
            repositório) contêm arquivos byte-idênticos; contá-los inflaria o
            inventário. A duplicata é registrada em ``duplicate_paths`` em vez
            de ser descartada em silêncio — o relatório precisa poder explicar
            por que 138 caminhos renderam 69 artefatos.
            """

            key = (artifact.ecosystem, artifact.kind, os.path.abspath(artifact.source_path))
            if key in by_path:
                return
            content_key = (artifact.ecosystem, artifact.kind, artifact.slug, artifact.content_sha256)
            existing = by_content.get(content_key)
            if existing is not None:
                # Mantém o caminho mais curto como canônico (determinístico).
                if len(artifact.source_path) < len(existing.source_path):
                    existing_paths = [artifact.source_path, *existing.duplicate_paths]
                    by_path[key] = artifact
                    by_content[content_key] = replace(
                        artifact, duplicate_paths=sorted(set(existing_paths) - {artifact.source_path})
                    )
                    by_path[(artifact.ecosystem, artifact.kind, existing.source_path)] = by_content[content_key]
                else:
                    by_content[content_key] = replace(
                        existing, duplicate_paths=sorted({*existing.duplicate_paths, artifact.source_path})
                    )
                return
            by_path[key] = artifact
            by_content[content_key] = artifact

        for spec in specs:
            root, ecosystem, origin, label = spec["root"], spec["ecosystem"], spec["origin"], spec["label"]
            if not os.path.isdir(root):
                self._missing_roots.append({
                    "ecosystem": ecosystem, "label": label, "path": root, "reason": "root_absent",
                })
                continue
            self._scanned_roots.append({
                "ecosystem": ecosystem, "label": label, "path": root, "origin": origin,
            })
            self._scan_root(root, ecosystem=ecosystem, origin=origin, label=label,
                            exclude_roots=all_roots, add=_add)

        unique: Dict[str, HarnessArtifact] = {}
        for artifact in by_content.values():
            unique[artifact.artifact_id] = artifact
        # A contagem de duplicatas vem de `duplicate_paths`, não de
        # `len(by_path) - len(unique)`: no ramo em que o canônico é preservado, o
        # caminho duplicado é registrado no artefato mas não entra em `by_path`,
        # então a subtração reportava zero duplicatas numa varredura que
        # comprovadamente tinha uma. A diferença é justamente o número que o
        # relatório precisa explicar.
        self._duplicate_count = sum(len(a.duplicate_paths) for a in unique.values())
        return sorted(unique.values(), key=lambda a: (a.ecosystem, a.kind, a.artifact_id))

    def _scan_root(
        self,
        root: str,
        *,
        ecosystem: str,
        origin: str,
        label: str,
        exclude_roots: Tuple[str, ...],
        add,
    ) -> None:
        def files(*suffixes: str) -> List[str]:
            return list(_iter_files(root, suffixes=suffixes, exclude_roots=exclude_roots))

        if ecosystem == "claude":
            for path in files("SKILL.md"):
                add(self._skill_from(path, ecosystem=ecosystem, origin=origin, source_root=label))
            for path in files(".md"):
                parts = path.replace(os.sep, "/").split("/")
                if "agents" in parts:
                    add(self._agent_from(path, ecosystem=ecosystem, origin=origin, source_root=label))
                elif "commands" in parts:
                    add(self._command_from(path, ecosystem=ecosystem, origin=origin, source_root=label))
            for path in files("hooks.json", "hooks-cursor.json"):
                add(self._hook_from(path, ecosystem=ecosystem, origin=origin, source_root=label))
            for name in ("CLAUDE.md", "settings.json", "settings.local.json"):
                candidate = os.path.join(root, name)
                if os.path.isfile(candidate):
                    add(self._spec_from(candidate, ecosystem=ecosystem, origin=origin,
                                        source_root=label, name=name))

        elif ecosystem == "antigravity":
            for path in files("SKILL.md"):
                add(self._skill_from(path, ecosystem=ecosystem, origin=origin, source_root=label))
            if label == "antigravity:project":
                agents_md = os.path.join(self.repo_root, "AGENTS.md")
                if os.path.isfile(agents_md):
                    add(self._spec_from(agents_md, ecosystem=ecosystem, origin=origin,
                                        source_root=label, name="AGENTS.md"))
                queue = os.path.join(root, "queue")
                for path in _iter_files(queue, suffixes=(".json",)):
                    add(self._handoff_from(path, source_root=label))
            elif label == "antigravity:cloud_scripts":
                # Cada diretório de serviço_cloud é uma skill (o `SKILL.md` já
                # foi colhido acima); os demais `.md` são runbooks de apoio.
                for path in files(".md"):
                    if os.path.basename(path) == "SKILL.md":
                        continue
                    add(self._spec_from(path, ecosystem=ecosystem, origin=origin,
                                        source_root=label,
                                        name=os.path.relpath(path, root).replace(os.sep, "/")))

        elif ecosystem == "codex":
            # O padrão AGENTS.md vive em `.agents/` (e em `.codex-plugin/`).
            # Other trees inside the vendored repo — `.claude/skills` is a byte
            # copy of `.agents/skills` — are *not* Codex artifacts, and counting
            # them would double the inventory while attributing them to the
            # wrong ecosystem.
            agents_tree = "/.agents/"
            for path in files(".md"):
                if agents_tree not in f"/{path.replace(os.sep, '/')}":
                    continue
                parts = path.replace(os.sep, "/").split("/")
                if "prompts" in parts:
                    add(self._command_from(path, ecosystem=ecosystem, origin=origin, source_root=label))
                elif "agents" in parts:
                    add(self._agent_from(path, ecosystem=ecosystem, origin=origin, source_root=label))
            for path in files("SKILL.md"):
                if agents_tree not in f"/{path.replace(os.sep, '/')}":
                    continue
                add(self._skill_from(path, ecosystem=ecosystem, origin=origin, source_root=label))
            agents_md = os.path.join(root, "AGENTS.md")
            if os.path.isfile(agents_md):
                add(self._spec_from(agents_md, ecosystem=ecosystem, origin=origin,
                                    source_root=label, name="AGENTS.md"))

        elif ecosystem == "chatgpt":
            for path in files("plugin.json"):
                if os.path.basename(os.path.dirname(path)) == ".codex-plugin":
                    add(self._codex_plugin_from(path, source_root=label))
            for path in files("SKILL_CHATGPT.md"):
                add(self._chatgpt_pack_from(path, source_root=label,
                                            name=_owning_name(path, stop_at=self.repo_root)))
            for path in files("openai.yaml"):
                add(self._openai_policy_from(path, source_root=label,
                                              name=_owning_name(path, stop_at=self.repo_root)))
            for name in ("AGENTS.md", "CLAUDE.md"):
                candidate = os.path.join(root, name)
                if os.path.isfile(candidate):
                    add(self._spec_from(candidate, ecosystem=ecosystem, origin=origin,
                                        source_root=label, name=name))

    # ------------------------------------------------------------------
    # Inventário
    # ------------------------------------------------------------------
    def inventory(self) -> Dict[str, Any]:
        """
        Relatório de prontidão com contagens **derivadas da varredura real**.

        Separa ``discovered`` de ``emitted`` e lista as raízes ausentes: um
        ecossistema com raiz ausente nunca é reportado como sincronizado
        (INV-R621.6).
        """

        artifacts = self.discover()
        by_ecosystem: Dict[str, Dict[str, int]] = {}
        by_kind: Dict[str, int] = {}
        by_origin: Dict[str, int] = {}
        degraded: List[Dict[str, Any]] = []

        for artifact in artifacts:
            bucket = by_ecosystem.setdefault(artifact.ecosystem, {})
            bucket[artifact.kind] = bucket.get(artifact.kind, 0) + 1
            by_kind[artifact.kind] = by_kind.get(artifact.kind, 0) + 1
            by_origin[artifact.origin] = by_origin.get(artifact.origin, 0) + 1
            if artifact.degraded_reasons:
                degraded.append({
                    "artifact_id": artifact.artifact_id,
                    "kind": artifact.kind,
                    "reasons": list(artifact.degraded_reasons),
                })

        # A lista `degraded` é longa e quase homogênea: 286 entradas com a mesma
        # razão `license_undeclared` dizem muito menos do que "286: 1 aviso de
        # licença, 3 sem descrição". O histograma por razão é o que torna a
        # lista acionável, e ele é derivado da mesma varredura.
        by_reason: Counter = Counter()
        for entry in degraded:
            by_reason.update(entry["reasons"])

        present = sorted({r["ecosystem"] for r in self._scanned_roots})
        missing_ecosystems = sorted({r["ecosystem"] for r in self._missing_roots} - set(present))
        binaries = {name: bool(shutil.which(name)) for name in ("claude", "codex", "agy", "gemini")}

        return {
            "spec_id": "SPEC-935-R621",
            "repo_root": self.repo_root,
            "discovered": len(artifacts),
            "duplicates_collapsed": self._duplicate_count,
            "emitted": 0,
            "by_ecosystem": by_ecosystem,
            "by_kind": by_kind,
            "by_origin": by_origin,
            "by_status": {"ok": len(artifacts) - len(degraded), "degraded": len(degraded)},
            "degraded_by_reason": dict(by_reason.most_common()),
            "blocking": sum(1 for a in artifacts if a.blocking_reasons),
            "degraded": degraded,
            "roots_scanned": list(self._scanned_roots),
            "roots_missing": list(self._missing_roots),
            "ecosystems_present": present,
            "ecosystems_missing": missing_ecosystems,
            "binaries": binaries,
            "synchronized": bool(artifacts) and not missing_ecosystems and not degraded,
            # `synchronized` acima é deliberadamente estrito: qualquer aviso
            # impede a afirmação de paridade. `synchronized_strict` diz quem
            # realmente bloqueia, para que o operador não tenha de abrir os 286
            # registros degradados para descobrir que 286 é o número que espera.
            "synchronized_strict": bool(artifacts) and not missing_ecosystems and not any(
                a.blocking_reasons for a in artifacts
            ),
        }
