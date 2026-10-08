# -*- coding: utf-8 -*-
"""Compatibilidade de invocação de skills Reversa (SPEC-935-R471).

O Reversa moderno distingue skills ``model-invoked`` de ``user-invoked``.
Skills user-invoked podem trazer ``disable-model-invocation: true`` no
``SKILL.md`` e/ou ``policy.allow_implicit_invocation: false`` em
``agents/openai.yaml``. Um orquestrador não deve tentar chamá-las implicitamente
pelo nome; deve ler o ``SKILL.md`` e executar as instruções no contexto atual.
"""

from __future__ import annotations

import os
import re
import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

import yaml

_SKILL_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_FRONTMATTER_RE = re.compile(r"\A\s*---\s*\n(.*?)\n---", re.DOTALL)

_DEFAULT_SKILL_ROOTS = (
    ".agents/skills",
    ".claude/skills",
    ".kiro/skills",
    ".opencode/skills",
    "agents",
    "skills",
)


@dataclass(frozen=True)
class SkillDispatchDecision:
    """Decisão determinística de handoff entre orquestrador e skill."""

    skill_name: str
    found: bool
    skill_path: Optional[str]
    openai_policy_path: Optional[str]
    user_invoked: bool
    execution_mode: str
    reason: str
    instruction: str
    instruction_root: Optional[str] = None
    source_skill_path: Optional[str] = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ReversaSkillDispatcher:
    """Resolve skills locais e escolhe a forma segura de invocação.

    A classe não executa código nem chama modelos. Ela apenas inspeciona os
    metadados locais e devolve a decisão de handoff para o orquestrador.
    """

    def __init__(
        self,
        project_root: str | Path = ".",
        extra_roots: Optional[Iterable[str | Path]] = None,
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.extra_roots = tuple(Path(root) for root in (extra_roots or ()))

    @staticmethod
    def _validate_name(skill_name: str) -> str:
        if not isinstance(skill_name, str):
            raise ValueError("Nome de skill deve ser uma string.")
        name = skill_name.strip()
        if not name or len(name) > 240 or ".." in name or not _SKILL_NAME_RE.fullmatch(name):
            raise ValueError(f"Nome de skill inválido: {skill_name!r}")
        return name

    def _candidate_roots(self, project_root: Optional[str | Path] = None) -> list[Path]:
        root = Path(project_root).resolve() if project_root is not None else self.project_root
        candidates: list[Path] = []

        env_roots = os.environ.get("REVERSA_SKILLS_ROOT", "")
        for raw in env_roots.split(os.pathsep):
            if raw.strip():
                candidates.append(Path(raw).expanduser().resolve())

        for extra in self.extra_roots:
            candidates.append((root / extra).resolve() if not extra.is_absolute() else extra.resolve())
        candidates.extend((root / rel).resolve() for rel in _DEFAULT_SKILL_ROOTS)

        unique: list[Path] = []
        seen: set[str] = set()
        for candidate in candidates:
            key = os.path.normcase(str(candidate))
            if key not in seen:
                seen.add(key)
                unique.append(candidate)
        return unique

    def resolve_skill(
        self,
        skill_name: str,
        project_root: Optional[str | Path] = None,
    ) -> Optional[Path]:
        name = self._validate_name(skill_name)
        for root in self._candidate_roots(project_root):
            candidate = root / name / "SKILL.md"
            if candidate.is_file():
                if not candidate.resolve().is_relative_to(root.resolve()):
                    raise ValueError("source_path_escape")
                return candidate.resolve()
        return None

    @staticmethod
    def _frontmatter(text: str) -> str:
        match = _FRONTMATTER_RE.search(text)
        return match.group(1) if match else ""

    def plan(
        self,
        skill_name: str,
        project_root: Optional[str | Path] = None,
    ) -> SkillDispatchDecision:
        name = self._validate_name(skill_name)
        skill_path = self.resolve_skill(name, project_root)
        if skill_path is None:
            return SkillDispatchDecision(
                skill_name=name,
                found=False,
                skill_path=None,
                openai_policy_path=None,
                user_invoked=False,
                execution_mode="native-or-read",
                reason="SKILL.md não encontrado nas raízes locais conhecidas.",
                instruction=(
                    f"Tente a ativação nativa de {name}; se a engine recusar invocação "
                    "implícita, localize o SKILL.md instalado, leia-o e execute-o no contexto atual."
                ),
            )

        return self.plan_path(skill_path, skill_name=name)

    def plan_path(self, skill_path: str | Path, *, skill_name: Optional[str] = None,
                  trusted_source_roots: Optional[Iterable[str | Path]] = None) -> SkillDispatchDecision:
        """Lê uma fonte explícita já resolvida pelo orquestrador, sem invocá-la."""
        raw_path = Path(skill_path).absolute()
        if not raw_path.resolve().is_relative_to(raw_path.parent.resolve()):
            raise ValueError("source_path_escape")
        skill_path = raw_path.resolve()
        name = self._validate_name(skill_path.parent.name if skill_name is None else skill_name)
        if skill_path.stat().st_size > 128 * 1024:
            raise ValueError("skill_too_large")
        with skill_path.open("rb") as handle:
            raw_text = handle.read(128 * 1024 + 1)
        if len(raw_text) > 128 * 1024:
            raise ValueError("skill_too_large")
        text = raw_text.decode("utf-8-sig")
        try:
            frontmatter = yaml.safe_load(self._frontmatter(text)) or {}
        except yaml.YAMLError as exc:
            raise ValueError("invalid_invocation_policy") from exc
        if not isinstance(frontmatter, dict):
            raise ValueError("invalid_invocation_policy")
        from integrations.harness_federation.artifact import invocation_policy, support_snapshot
        merged_policy, policy_reasons = invocation_policy(frontmatter)
        if policy_reasons:
            raise ValueError(policy_reasons[0])
        disable_model = merged_policy["disable_model_invocation"]
        source_value = frontmatter.get("x-source-skill-path")
        root_value = frontmatter.get("x-source-instruction-root")
        if source_value is not None and (not isinstance(source_value, str) or not source_value or len(source_value) > 4096):
            raise ValueError("invalid_source_provenance")
        if root_value is not None and (not isinstance(root_value, str) or not root_value or len(root_value) > 4096):
            raise ValueError("invalid_source_provenance")
        source_path = Path(source_value) if source_value is not None else skill_path
        source_root = Path(root_value) if root_value is not None else source_path.parent
        if source_value is not None:
            permitted = [*self._candidate_roots(), *(Path(p).resolve() for p in (trusted_source_roots or ()))]
            if not source_path.is_absolute() or not any(source_path.resolve().is_relative_to(p) for p in permitted):
                raise ValueError("source_root_untrusted")
        if not source_path.resolve().is_relative_to(source_root.resolve()):
            raise ValueError("source_path_escape")
        expected_hash = frontmatter.get("x-source-skill-sha256")
        if expected_hash is not None and (not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)):
            raise ValueError("invalid_source_provenance")
        if expected_hash and source_path.is_file() and source_path.stat().st_size > 128 * 1024:
            raise ValueError("skill_too_large")
        if expected_hash and (not source_path.is_file() or hashlib.sha256(source_path.read_bytes()).hexdigest() != expected_hash):
            raise ValueError("source_changed")

        _, support_reasons = support_snapshot(str(skill_path.parent))
        if support_reasons:
            raise ValueError(support_reasons[0])

        openai_policy = skill_path.parent / "agents" / "openai.yaml"
        openai_disallows = merged_policy["allow_implicit_invocation"] is False
        if openai_policy.is_file():
            if not openai_policy.resolve().is_relative_to(skill_path.parent):
                raise ValueError("support_path_escape")
            try:
                data = yaml.safe_load(openai_policy.read_text(encoding="utf-8-sig")) or {}
            except yaml.YAMLError as exc:
                raise ValueError("invalid_invocation_policy") from exc
            policy = data.get("policy", {}) if isinstance(data, dict) else None
            if not isinstance(policy, dict):
                raise ValueError("invalid_invocation_policy")
            allow = policy.get("allow_implicit_invocation")
            if allow is not None and not isinstance(allow, bool):
                raise ValueError("invalid_invocation_policy")
            merged_policy, policy_reasons = invocation_policy(frontmatter, policy)
            if policy_reasons:
                raise ValueError(policy_reasons[0])
            disable_model = merged_policy["disable_model_invocation"]
            openai_disallows = merged_policy["allow_implicit_invocation"] is False

        user_invoked = disable_model or openai_disallows
        policy_path = str(openai_policy) if openai_policy.is_file() else None

        if user_invoked:
            reasons = []
            if disable_model:
                reasons.append("disable-model-invocation=true")
            if openai_disallows:
                reasons.append("allow_implicit_invocation=false")
            return SkillDispatchDecision(
                skill_name=name,
                found=True,
                skill_path=str(skill_path),
                openai_policy_path=policy_path,
                user_invoked=True,
                execution_mode="read-and-execute",
                instruction_root=str(skill_path.parent),
                source_skill_path=str(source_path),
                reason="; ".join(reasons),
                instruction=(
                    f"NÃO invoque {name} implicitamente pelo Skill tool/subagente. "
                    f"Leia {skill_path} e execute suas instruções no contexto atual, "
                    "preservando o estado do pipeline e a intenção CONTINUAR do usuário."
                ),
            )

        return SkillDispatchDecision(
            skill_name=name,
            found=True,
            skill_path=str(skill_path),
            openai_policy_path=policy_path,
            user_invoked=False,
            execution_mode="native-or-read",
            instruction_root=str(skill_path.parent),
            source_skill_path=str(source_path),
            reason="A skill não proíbe invocação implícita nos metadados detectados.",
            instruction=(
                f"A ativação nativa de {name} é permitida. Se a engine não suportar "
                f"ativação por nome, leia {skill_path} e execute no contexto atual."
            ),
        )


def plan_skill_handoff(
    skill_name: str,
    project_root: str | Path = ".",
) -> dict[str, object]:
    """API funcional curta para integrações e diagnósticos."""

    return ReversaSkillDispatcher(project_root=project_root).plan(skill_name).to_dict()
