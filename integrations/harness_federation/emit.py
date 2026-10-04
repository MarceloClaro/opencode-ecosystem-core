# -*- coding: utf-8 -*-
"""
HarnessEmitter — portabilidade de artefatos multi-harness ao Core (SPEC-935-R621)
==============================================================================
Converte artefatos normalizados de Claude/Codex/Antigravity/ChatGPT nos
formatos nativos do OpenCode Ecosystem Core:

- **skill**  → ``.opencode/skills/<slug>/SKILL.md``
- **agent**  → ``.opencode/agents/<slug>.md``
- **hook**   → ``.opencode/hooks/manifests/<slug>.json`` (manifesto *declarativo*)
- **plugin** → ``.codex-plugin/plugin.json`` normalizado (Codex/ChatGPT)
- **prompt_pack** → ``SKILL_CHATGPT.md`` normalizado (instruções de Custom GPT)

Duas garantias tornam o port confiável:

1. **Fidelidade** (INV-R621.3) — o corpo emitido é o corpo de origem; o hash
   ``content_sha256`` é transportado no frontmatter de proveniência e pode ser
   reconferido a qualquer momento. O emissor nunca reescreve conteúdo.
2. **Não execução** (INV-R621.4) — hooks de terceiro são *registrados como
   dados*. O comando upstream jamais é executado por este módulo; decidir
   executá-lo é ato humano, mediante leitura do manifesto.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .artifact import NON_BLOCKING_REASONS, HarnessArtifact, parse_frontmatter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _yaml_block_scalar(value: str) -> str:
    """Serializa texto longo como escalar YAML de bloco (``>-``), seguro para aspas."""

    return ">-\n" + "\n".join(f"  {line}".rstrip() for line in (value or "").splitlines())


def _provenance_block(artifact: HarnessArtifact) -> str:
    """Bloco de proveniência, em YAML, gravado ao final do frontmatter."""

    lines = [
        "x-proveniencia:",
        f"  ecossistema: {artifact.ecosystem}",
        f"  tipo: {artifact.kind}",
        f"  origem: {artifact.origin}",
        f"  raiz: {artifact.source_root}",
        f"  caminho_origem: {artifact.source_path}",
        f"  licenca: {artifact.license or '(nao declarada)'}",
        f"  versao: {artifact.version or '(nao declarada)'}",
        f"  sha256_corpo: {artifact.content_sha256}",
        f"  sha256_arquivo_origem: {artifact.source_file_sha256 or '(arquivo ausente)'}",
        "  importado_por: SPEC-935-R621",
    ]
    if artifact.capabilities:
        lines.append("  capacidades:")
        lines.extend(f"    - {_yaml_inline(cap)}" for cap in artifact.capabilities)
    if artifact.tags:
        lines.append("  etiquetas:")
        lines.extend(f"    - {_yaml_inline(tag)}" for tag in artifact.tags)
    if artifact.hook_events:
        lines.append("  eventos:")
        lines.extend(f"    - {_yaml_inline(event)}" for event in artifact.hook_events)
    return "\n".join(lines)


def _yaml_inline(value: str) -> str:
    """Cita um escalar YAML quando necessário (aspas duplas escapadas)."""

    text = str(value)
    if text == "" or any(ch in text for ch in ':#\n"\'{}[],&*?|<>=!%@`') or text.strip() != text:
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


class HarnessEmitter:
    """Grava artefatos normalizados nos diretórios nativos do OpenCode Core."""

    def __init__(
        self,
        repo_root: str = REPO_ROOT,
        *,
        dry_run: bool = False,
    ) -> None:
        self.repo_root = os.path.abspath(repo_root)
        self.dry_run = dry_run

    # ------------------------------------------------------------------
    # Utilidades de escrita
    # ------------------------------------------------------------------
    def _write(self, path: str, content: str) -> Dict[str, Any]:
        """Escreve o arquivo de forma idempotente e relata o que houve."""

        existed = os.path.isfile(path)
        previous = ""
        if existed:
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    previous = handle.read()
            except OSError:
                previous = ""
        changed = previous != content
        if changed and not self.dry_run:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)
        return {
            "path": path,
            "existed": existed,
            "changed": changed,
            "written": bool(changed and not self.dry_run),
            "bytes": len(content.encode("utf-8")),
        }

    def _refuse_degraded(self, artifact: HarnessArtifact) -> Optional[Dict[str, Any]]:
        """
        Devolve o relatório de recusa quando o artefato não é apto a emissão.

        Só recusa por razões **bloqueantes** (INV-R621.1). Licença não declarada
        é aviso: o artefato é portado com a ausência registrada no bloco de
        proveniência, e quem o reutilizar verá exatamente o que falta.
        """

        blocking = [r for r in artifact.degraded_reasons if r not in NON_BLOCKING_REASONS]
        if not blocking:
            return None
        return {
            "status": "refused",
            "artifact_id": artifact.artifact_id,
            "reasons": list(artifact.degraded_reasons),
            "blocking_reasons": blocking,
        }

    def _read_body(self, artifact: HarnessArtifact) -> str:
        """Corpo de origem sem o frontmatter — é o que será portado verbatim."""

        try:
            with open(artifact.source_path, "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            return ""
        front, body = parse_frontmatter(text)
        if front:
            return body
        return text

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------
    def emit_skill(self, artifact: HarnessArtifact) -> Dict[str, Any]:
        """Porta uma skill para ``.opencode/skills/<slug>/SKILL.md``."""

        refusal = self._refuse_degraded(artifact)
        if refusal:
            return refusal
        body = self._read_body(artifact)
        front = [
            "---",
            f"name: {_yaml_inline(artifact.slug)}",
            f"description: {_yaml_block_scalar(artifact.description)}",
            _provenance_block(artifact),
            "---",
            "",
        ]
        content = "\n".join(front) + body.lstrip("\n")
        result = self._write(os.path.join(self.repo_root, ".opencode", "skills", artifact.slug, "SKILL.md"), content)
        return {
            "status": "emitted",
            "artifact_id": artifact.artifact_id,
            "target": "opencode.skill",
            "body_sha256": artifact.content_sha256,
            "source_file_sha256": artifact.source_file_sha256,
            **result,
        }

    # ------------------------------------------------------------------
    # Agentes
    # ------------------------------------------------------------------
    def emit_agent(self, artifact: HarnessArtifact) -> Dict[str, Any]:
        """Porta um subagente para ``.opencode/agents/<slug>.md``."""

        refusal = self._refuse_degraded(artifact)
        if refusal:
            return refusal
        body = self._read_body(artifact)
        front = [
            "---",
            f"name: {_yaml_inline(artifact.slug)}",
            f"description: {_yaml_block_scalar(artifact.description)}",
            "mode: subagent",
            "temperature: 0.3",
            "permission:",
            "  read: allow",
            "  glob: allow",
            "  edit: deny",
            "  bash: deny",
            _provenance_block(artifact),
            "---",
            "",
        ]
        content = "\n".join(front) + body.lstrip("\n")
        result = self._write(os.path.join(self.repo_root, ".opencode", "agents", f"{artifact.slug}.md"), content)
        return {
            "status": "emitted",
            "artifact_id": artifact.artifact_id,
            "target": "opencode.agent",
            "body_sha256": artifact.content_sha256,
            "source_file_sha256": artifact.source_file_sha256,
            **result,
        }

    # ------------------------------------------------------------------
    # Hooks (declarativos, nunca executados)
    # ------------------------------------------------------------------
    def emit_hooks(self, artifact: HarnessArtifact) -> Dict[str, Any]:
        """
        Registra o manifesto de hooks em ``.opencode/hooks/manifests/``.

        O manifesto emitido é **inerte**: carrega os eventos e comandos
        upstream com o estado ``"execution": "blocked_pending_human_review"``.
        Importar um hook de terceiro é registrá-lo; executá-lo é outro ato.
        """

        refusal = self._refuse_degraded(artifact)
        if refusal:
            return refusal
        manifest = {
            "spec_id": "SPEC-935-R621",
            "name": artifact.name,
            "ecosystem": artifact.ecosystem,
            "origin": artifact.origin,
            "license": artifact.license or None,
            "source_path": artifact.source_path,
            "content_sha256": artifact.content_sha256,
            "source_file_sha256": artifact.source_file_sha256,
            "execution": "blocked_pending_human_review",
            "events": list(artifact.hook_events),
            "commands": list(artifact.hook_commands),
        }
        content = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        result = self._write(
            os.path.join(self.repo_root, ".opencode", "hooks", "manifests", f"{artifact.slug}.json"),
            content,
        )
        return {
            "status": "emitted",
            "artifact_id": artifact.artifact_id,
            "target": "opencode.hook_manifest",
            "executed": False,
            # Mesma chave do relatório de lote: quem lê o resultado de um
            # artefato só não deveria precisar saber se pediu um ou o outro.
            "hooks_executed": False,
            **result,
        }

    # ------------------------------------------------------------------
    # Exportação Codex / ChatGPT
    # ------------------------------------------------------------------
    def export_codex_plugin(self, artifact: HarnessArtifact) -> Dict[str, Any]:
        """Normaliza um artefato no manifesto ``.codex-plugin/plugin.json``."""

        refusal = self._refuse_degraded(artifact)
        if refusal:
            return refusal
        manifest = {
            "name": f"r621-{artifact.slug}",
            "version": artifact.version or "0.1.0",
            "description": artifact.description,
            "author": {"name": "Marcelo Claro Laranjeira"},
            "keywords": list(artifact.tags),
            "interface": {
                "displayName": artifact.name,
                "shortDescription": artifact.description[:180],
                "longDescription": artifact.description,
                "developerName": "MARCELO CLARO LARANJEIRA",
                "capabilities": list(artifact.capabilities) or ["skills"],
                "defaultPrompt": list(artifact.metadata.get("default_prompts") or []),
            },
            "skills": "./skills",
        }
        content = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        result = self._write(
            os.path.join(self.repo_root, ".codex-plugin", "r621", f"{artifact.slug}", "plugin.json"),
            content,
        )
        return {
            "status": "emitted",
            "artifact_id": artifact.artifact_id,
            "target": "codex.plugin",
            **result,
        }

    def export_chatgpt_instructions(self, artifact: HarnessArtifact) -> Dict[str, Any]:
        """Exporta um artefato como documento de instruções de Custom GPT."""

        refusal = self._refuse_degraded(artifact)
        if refusal:
            return refusal
        # O corpo é portado **verbatim** (INV-R621.3): todo o aviso de migração
        # vive no frontmatter, para que a região portada continue comparável
        # byte a byte com a origem e verificável pelo sha256 declarado.
        body = self._read_body(artifact)
        header = [
            "---",
            "spec_id: SPEC-935-R621",
            f"nome: {_yaml_inline(artifact.name)}",
            f"ecossistema_origem: {artifact.ecosystem}",
            f"origem: {artifact.origin}",
            f"licenca: {artifact.license or '(nao declarada)'}",
            f"sha256_origem: {artifact.content_sha256}",
            "destino: chatgpt.custom_gpt.instructions",
            "aviso: >-",
            "  Documento derivado de um artefato de agente externo por migração"
            " mecânica, não semântica. Revise antes de usar como Instructions"
            " de um Custom GPT.",
            "---",
            "",
        ]
        content = "\n".join(header) + body.lstrip("\n")
        result = self._write(
            os.path.join(self.repo_root, "harness_federation", "chatgpt", f"{artifact.slug}", "SKILL_CHATGPT.md"),
            content,
        )
        return {
            "status": "emitted",
            "artifact_id": artifact.artifact_id,
            "target": "chatgpt.instructions",
            **result,
        }

    # ------------------------------------------------------------------
    # despacho em lote
    # ------------------------------------------------------------------
    def dispatch(self, artifact: HarnessArtifact) -> Dict[str, Any]:
        """
        Emite um artefato no destino correspondente ao seu ``kind``.

        Público por decisão: o port de artefato é uma operação do dia a dia
        (importar um plugin específico, reemitir uma skill) e não deve exigir
        que o chamador conheça a tabela interna de emissores.
        """

        if artifact.kind == "skill":
            return self.emit_skill(artifact)
        if artifact.kind == "agent":
            return self.emit_agent(artifact)
        if artifact.kind == "hook":
            return self.emit_hooks(artifact)
        if artifact.kind == "plugin":
            return self.export_codex_plugin(artifact)
        if artifact.kind == "prompt_pack":
            return self.export_chatgpt_instructions(artifact)
        return {
            "status": "skipped",
            "artifact_id": artifact.artifact_id,
            "reason": f"sem emissor para kind={artifact.kind}",
        }

    def emit_all(
        self,
        artifacts: Iterable[HarnessArtifact],
        *,
        kinds: Optional[Tuple[str, ...]] = None,
        require_license: bool = False,
    ) -> Dict[str, Any]:
        """
        Emite o lote e devolve o relatório consolidado.

        ``require_license=False`` (padrão) porta também artefatos sem licença
        declarada, gravando a ausência no bloco de proveniência — é o que
        permite estudioar o material de terceiros sem mascará-lo. Com
        ``require_license=True`` o operador exige licença declarada e os
        artefatos sem ela são recusados, com o motivo registrado.
        """

        selected = [a for a in artifacts if kinds is None or a.kind in kinds]

        emitted: List[Dict[str, Any]] = []
        refused: List[Dict[str, Any]] = []
        skipped: List[Dict[str, Any]] = []

        for artifact in selected:
            # `require_license` recusa e **registra**. Filtrar a lista antes do
            # laço faria o relatório dizer "nada recusado" enquanto metade do
            # lote sumia — o oposto de fail-closed e impossível de auditar.
            if require_license and "license_undeclared" in artifact.degraded_reasons:
                refused.append({
                    "spec_id": "SPEC-935-R621",
                    "status": "refused",
                    "target": "none",
                    "artifact_id": artifact.artifact_id,
                    "kind": artifact.kind,
                    "reasons": list(artifact.degraded_reasons),
                    "blocking_reasons": list(artifact.blocking_reasons) + ["license_required_by_operator"],
                })
                continue
            report = self.dispatch(artifact)
            if report.get("status") == "emitted":
                emitted.append(report)
            elif report.get("status") == "refused":
                refused.append(report)
            else:
                skipped.append(report)

        by_target: Dict[str, int] = {}
        for report in emitted:
            by_target[report["target"]] = by_target.get(report["target"], 0) + 1

        return {
            "spec_id": "SPEC-935-R621",
            "dry_run": self.dry_run,
            "selected": len(selected),
            "emitted": len(emitted),
            "refused": len(refused),
            "skipped": len(skipped),
            "by_target": by_target,
            "emitted_paths": sorted({r["path"] for r in emitted}),
            "refused_detail": refused,
            "skipped_detail": skipped,
            "hooks_executed": False,
            # INV-R621.6: "synchronized" só é dito quando nada foi recusado.
            "synchronized": bool(selected) and not refused and not skipped,
        }
