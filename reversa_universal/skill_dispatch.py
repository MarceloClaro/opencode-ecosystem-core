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
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

_SKILL_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_FRONTMATTER_RE = re.compile(r"\A\s*---\s*\n(.*?)\n---", re.DOTALL)
_DISABLE_MODEL_RE = re.compile(
    r"(?mi)^\s*disable-model-invocation\s*:\s*true\s*(?:#.*)?$"
)
_OPENAI_IMPLICIT_FALSE_RE = re.compile(
    r"(?mi)^\s*allow_implicit_invocation\s*:\s*false\s*(?:#.*)?$"
)

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
        name = str(skill_name).strip()
        if not name or not _SKILL_NAME_RE.fullmatch(name):
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

        text = skill_path.read_text(encoding="utf-8")
        frontmatter = self._frontmatter(text)
        disable_model = bool(_DISABLE_MODEL_RE.search(frontmatter))

        openai_policy = skill_path.parent / "agents" / "openai.yaml"
        openai_disallows = False
        if openai_policy.is_file():
            openai_disallows = bool(
                _OPENAI_IMPLICIT_FALSE_RE.search(openai_policy.read_text(encoding="utf-8"))
            )

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
