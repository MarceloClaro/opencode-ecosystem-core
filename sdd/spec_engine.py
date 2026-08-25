# -*- coding: utf-8 -*-
"""
SDD Engine — Specification-Driven Development
=============================================
Motor de especificações do ecossistema. Implementa:

1. `Specification`: especificação executável com critérios de aceitação
   verificáveis (funções booleanas) e invariantes.
2. `SpecRegistry`: registro central que carrega as specs formais de `specs/*.md`
   (frontmatter YAML) e as specs dinâmicas criadas em tempo de execução.
3. `SpecVerifier`: verificador que valida entregas contra critérios de
   aceitação ANTES de qualquer `task.complete` (modo estrito).

Fluxo SDD: ESPECIFICAR → RED → GREEN → REFACTOR → VERIFICAR

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import os
import re
import glob
import uuid
import logging
import unicodedata
import hashlib
import json
import threading
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List, Any, Callable, Optional, Tuple

import yaml

from mci.metabus import metabus

logger = logging.getLogger("sdd-engine")
logger.setLevel(logging.INFO)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS_DIR = os.path.join(REPO_ROOT, "specs")


class AcceptanceCriterion:
    """Critério de aceitação verificável programaticamente (TDD-friendly)."""

    def __init__(self, criterion_id: str, description: str,
                 check_fn: Optional[Callable[[Any], bool]] = None,
                 requires_trusted_test_evidence: bool = False):
        self.criterion_id = criterion_id
        self.description = description
        # check_fn recebe a entrega (output) e retorna True/False
        self.check_fn = check_fn or (lambda output: bool(output))
        # Critérios extraídos de Markdown são contratos formais. Diferente dos
        # critérios programáticos legados, eles só podem ficar verdes com a
        # evidência emitida pelo runtime após executar o ``test_file`` da spec.
        self.requires_trusted_test_evidence = requires_trusted_test_evidence

    def check(self, output: Any) -> bool:
        try:
            return bool(self.check_fn(output))
        except Exception as e:
            logger.warning(f"Critério {self.criterion_id} lançou exceção: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {"criterion_id": self.criterion_id, "description": self.description}


class Specification:
    """Especificação executável de uma tarefa ou componente (SDD)."""

    def __init__(self, spec_id: str, title: str, objective: str,
                 criteria: Optional[List[AcceptanceCriterion]] = None,
                 invariants: Optional[List[str]] = None,
                 non_goals: Optional[List[str]] = None,
                 component: str = "", test_file: str = "",
                 *, evidence_contract_mode: str = "legacy",
                 evidence_contract_valid: bool = False,
                 evidence_contract_error: Optional[str] = None,
                 evidence_contract_sha256: Optional[str] = None,
                 criterion_test_targets: Optional[Mapping[str, Tuple[str, ...]]] = None,
                 declared_status: str = "draft",
                 evidence_contract_declared: bool = False,
                 evidence_contract_test_file: Optional[str] = None):
        self.spec_id = spec_id
        self.title = title
        self.objective = objective
        self.criteria = criteria or []
        self.invariants = invariants or []
        self.non_goals = non_goals or []
        self.component = component
        self.test_file = test_file
        self.status = "draft"  # draft -> red -> green -> verified
        # Os campos abaixo são sempre expostos, inclusive para specs legadas.
        # Isso evita que consumidores inferam a modalidade pela ausência de um
        # atributo e deixa explícito que a rota histórica não é granular v1.
        self.evidence_contract_mode = evidence_contract_mode
        self.evidence_contract_valid = evidence_contract_valid
        self.evidence_contract_error = evidence_contract_error
        self.evidence_contract_sha256 = evidence_contract_sha256
        self.criterion_test_targets = MappingProxyType(
            {
                criterion_id: tuple(targets)
                for criterion_id, targets in (criterion_test_targets or {}).items()
            }
        )
        self.declared_status = declared_status
        # Metadado interno usado para não degradar silenciosamente um contrato
        # declarado, porém inválido, para a rota legada permissiva.
        self._evidence_contract_declared = evidence_contract_declared
        # Vínculo físico canônico no momento do carregamento. O SHA cobre o
        # contrato YAML; este campo impede ampliar ``test_file`` depois disso.
        self._evidence_contract_test_file = evidence_contract_test_file

    def add_criterion(self, description: str,
                      check_fn: Optional[Callable[[Any], bool]] = None) -> AcceptanceCriterion:
        criterion = AcceptanceCriterion(
            f"{self.spec_id}-AC{len(self.criteria) + 1}", description, check_fn
        )
        self.criteria.append(criterion)
        return criterion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec_id": self.spec_id,
            "title": self.title,
            "objective": self.objective,
            "component": self.component,
            "test_file": self.test_file,
            "status": self.status,
            "declared_status": self.declared_status,
            "criteria": [c.to_dict() for c in self.criteria],
            "invariants": self.invariants,
            "non_goals": self.non_goals,
            "requires_trusted_test_evidence": self.requires_trusted_test_evidence,
            "evidence_contract_mode": self.evidence_contract_mode,
            "evidence_contract_valid": self.evidence_contract_valid,
            "evidence_contract_error": self.evidence_contract_error,
            "evidence_contract_sha256": self.evidence_contract_sha256,
            "criterion_test_targets": {
                criterion_id: list(targets)
                for criterion_id, targets in self.criterion_test_targets.items()
            },
        }

    @property
    def requires_trusted_test_evidence(self) -> bool:
        """Indica se algum contrato formal exige prova emitida pelo runtime."""
        return any(
            criterion.requires_trusted_test_evidence
            for criterion in self.criteria
        )

    @property
    def requires_criterion_runtime_records(self) -> bool:
        """Indica que critérios Markdown não podem usar a prova global legada."""
        return bool(
            self._evidence_contract_declared
            or self.evidence_contract_mode == _CRITERION_RUNTIME_V1_MODE
        )


def _parse_spec_frontmatter(content: str) -> Dict[str, Any]:
    """Lê o frontmatter YAML, preservando o parser legado como contingência."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    yaml_text = match.group(1)
    try:
        meta = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as exc:
        # Mantém a compatibilidade com frontmatters históricos que o parser
        # anterior aceitava, ainda que não sejam YAML estrito.
        logger.debug("Frontmatter YAML inválido; usando parser legado: %s", exc)
        meta = {}
        for line in yaml_text.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()

    return dict(meta) if isinstance(meta, Mapping) else {}


_MARKDOWN_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
_MARKDOWN_CRITERION_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s+`(?P<criterion_id>[^`]+)`"
    r"(?P<description>.*)$"
)
_EVIDENCE_CONTAINER_KEYS = (
    "evidence",
    "criteria_evidence",
    "criteria",
    "criteria_results",
)
_POSITIVE_EVIDENCE_STATUSES = frozenset({"passed", "verified", "green", "success"})
_CRITERION_RUNTIME_V1_MODE = "criterion-runtime-v1"
_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
_RUNTIME_TEST_EVIDENCE_SEAL = object()
_RUNTIME_CRITERION_RECORD_SEAL = object()
_UNSET_RUNTIME_RUN_SEAL = object()
_CONSUMED_STRICT_EXECUTIONS: set[str] = set()
_CONSUMED_STRICT_EXECUTIONS_LOCK = threading.Lock()


def _contains_control_character(value: str) -> bool:
    """Recusa NUL, quebras de linha e controles em alvos de pytest."""
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


def _canonical_relative_repo_path(
    path_text: Any,
    *,
    require_input_canonical: bool,
) -> Optional[str]:
    """Retorna um caminho relativo, resolvido e contido no checkout.

    A variante estrita também exige que o texto declarado já seja a forma
    canônica POSIX. Assim ``./tests/a.py``, ``tests/../tests/a.py``, barras
    duplicadas e links que mudam a localização física não entram no contrato.
    """
    if not isinstance(path_text, str) or not path_text or "\x00" in path_text:
        return None
    if path_text != path_text.strip() or _contains_control_character(path_text):
        return None
    if "\\" in path_text or path_text.startswith("-"):
        return None

    candidate_text = path_text
    if not require_input_canonical:
        # ``tests/`` é o default histórico de ``run_pytest``. A execução segue
        # segura e a saída é canônica, sem quebrar esse chamador legado.
        candidate_text = candidate_text.rstrip("/")
        if not candidate_text:
            return None

    parts = candidate_text.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None

    candidate = Path(candidate_text)
    if candidate.is_absolute():
        return None
    try:
        root = Path(REPO_ROOT).resolve()
        resolved = (root / candidate).resolve()
        relative = resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    if relative == Path("."):
        return None

    canonical = relative.as_posix()
    if require_input_canonical and canonical != path_text:
        return None
    return canonical


def _is_safe_pytest_selector(selector: str) -> bool:
    """Valida a parte ``::`` de um nodeid sem aceitar opções disfarçadas."""
    if (
        not selector
        or selector != selector.strip()
        or _contains_control_character(selector)
    ):
        return False
    # Componentes usuais incluem classe, função e parametrização. Um componente
    # iniciado por hífen nunca é um seletor canônico e poderia mascarar opção.
    return all(
        component
        and component not in {".", ".."}
        and not component.startswith("-")
        for component in selector.split("::")
    )


def _canonical_pytest_target(
    test_target: Any,
    *,
    require_nodeid: bool = False,
    require_input_canonical: bool = False,
) -> Optional[str]:
    """Normaliza um alvo pytest seguro, relativo e contido no repositório.

    O terminador ``--`` usado pelo executor continua sendo a última barreira de
    CLI. Esta validação antecipa a recusa de caminhos/seletores que poderiam
    tornar um contrato ambíguo ou introduzir uma opção como alvo.
    """
    if not isinstance(test_target, str) or not test_target or "\x00" in test_target:
        return None
    if test_target != test_target.strip() or _contains_control_character(test_target):
        return None
    if test_target.lstrip().startswith("-"):
        return None

    path_text, separator, selector = test_target.partition("::")
    if require_nodeid and not separator:
        return None
    if separator and not _is_safe_pytest_selector(selector):
        return None

    canonical_path = _canonical_relative_repo_path(
        path_text,
        require_input_canonical=require_input_canonical,
    )
    if canonical_path is None:
        return None
    canonical_target = (
        f"{canonical_path}::{selector}" if separator else canonical_path
    )
    if require_input_canonical and canonical_target != test_target:
        return None
    return canonical_target


def _validate_criterion_test_target(
    test_target: Any,
    test_file: Any,
) -> Tuple[Optional[str], Optional[str]]:
    """Valida um nodeid v1 contra o ``test_file`` e o checkout local."""
    canonical_test_file = _canonical_spec_test_file(test_file)
    if canonical_test_file is None:
        return None, "test_file ausente, inválido ou fora do repositório"

    canonical_target = _canonical_pytest_target(
        test_target,
        require_nodeid=True,
        require_input_canonical=True,
    )
    if canonical_target is None:
        return None, "nodeid relativo/canônico inválido ou com opção/escape"

    target_path_text = canonical_target.split("::", 1)[0]
    try:
        root = Path(REPO_ROOT).resolve()
        target_path = (root / target_path_text).resolve()
        test_root = (root / canonical_test_file).resolve()
    except (OSError, RuntimeError):
        return None, "não foi possível resolver nodeid ou test_file"

    if not target_path.is_file():
        return None, f"arquivo do nodeid inexistente: {target_path_text}"
    if not (test_root.is_file() or test_root.is_dir()):
        return None, f"test_file inexistente: {canonical_test_file}"
    try:
        target_path.relative_to(test_root)
    except ValueError:
        return None, "nodeid não está contido no test_file declarado"
    return canonical_target, None


class CriterionRuntimeRecord:
    """Registro imutável e selado de um nodeid executado para um critério."""

    __slots__ = (
        "spec_id",
        "test_file",
        "criterion_id",
        "test_target",
        "executed",
        "passed",
        "returncode",
        "summary",
        "error",
        "passed_count",
        "failed_count",
        "skipped_count",
        "xfailed_count",
        "xpassed_count",
        "error_count",
        "collected_count",
        "contract_sha256",
        "execution_id",
        "_run_seal",
        "_seal",
        "_frozen",
    )

    def __init__(
        self,
        *,
        spec_id: str,
        test_file: str,
        criterion_id: str,
        test_target: str,
        executed: bool,
        passed: bool,
        returncode: Optional[int],
        summary: str,
        error: Optional[str],
        passed_count: int,
        failed_count: int,
        skipped_count: int,
        xfailed_count: int,
        xpassed_count: int,
        error_count: int,
        collected_count: int,
        contract_sha256: Optional[str],
        execution_id: str,
        _run_seal: object,
        _seal: object,
    ) -> None:
        if _seal is not _RUNTIME_CRITERION_RECORD_SEAL:
            raise TypeError(
                "CriterionRuntimeRecord só pode ser emitido pelo runtime de testes."
            )
        for name, value in (
            ("spec_id", spec_id),
            ("test_file", test_file),
            ("criterion_id", criterion_id),
            ("test_target", test_target),
            ("executed", executed),
            ("passed", passed),
            ("returncode", returncode),
            ("summary", summary),
            ("error", error),
            ("passed_count", passed_count),
            ("failed_count", failed_count),
            ("skipped_count", skipped_count),
            ("xfailed_count", xfailed_count),
            ("xpassed_count", xpassed_count),
            ("error_count", error_count),
            ("collected_count", collected_count),
            ("contract_sha256", contract_sha256),
            ("execution_id", execution_id),
            ("_run_seal", _run_seal),
            ("_seal", _seal),
        ):
            object.__setattr__(self, name, value)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError("CriterionRuntimeRecord é imutável.")
        object.__setattr__(self, name, value)

    def to_dict(self) -> Dict[str, Any]:
        """Projeta o registro auditável sem expor seus selos privados."""
        return {
            "spec_id": self.spec_id,
            "test_file": self.test_file,
            "criterion_id": self.criterion_id,
            "test_target": self.test_target,
            "executed": self.executed,
            "passed": self.passed,
            "returncode": self.returncode,
            "summary": self.summary,
            "error": self.error,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "xfailed_count": self.xfailed_count,
            "xpassed_count": self.xpassed_count,
            "error_count": self.error_count,
            "collected_count": self.collected_count,
            "contract_sha256": self.contract_sha256,
        }


class TrustedTestEvidence:
    """Resultado imutável de um teste que só o runtime pode emitir.

    O objeto não é um protocolo serializável nem é construível por payload do
    agente. O selo de identidade privado impede autoatestado por dados de
    agentes, evitando que um dicionário com os mesmos campos seja confundido
    com a evidência obtida pela execução do pytest.
    Ele não é uma fronteira de segurança contra código arbitrário no mesmo processo.
    """

    __slots__ = (
        "spec_id",
        "test_file",
        "executed",
        "passed",
        "returncode",
        "summary",
        "error",
        "scope",
        "external_validation",
        "contract_sha256",
        "criterion_records",
        "execution_id",
        "_run_seal",
        "_seal",
        "_frozen",
    )

    def __init__(
        self,
        spec_id: str,
        test_file: str,
        *,
        executed: bool,
        passed: bool,
        returncode: Optional[int],
        summary: str,
        error: Optional[str],
        contract_sha256: Optional[str],
        criterion_records: Tuple[CriterionRuntimeRecord, ...],
        execution_id: str,
        _run_seal: object,
        _seal: object,
    ):
        if _seal is not _RUNTIME_TEST_EVIDENCE_SEAL:
            raise TypeError(
                "TrustedTestEvidence só pode ser emitida pelo runtime de testes."
            )
        object.__setattr__(self, "spec_id", spec_id)
        object.__setattr__(self, "test_file", test_file)
        object.__setattr__(self, "executed", executed)
        object.__setattr__(self, "passed", passed)
        object.__setattr__(self, "returncode", returncode)
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "error", error)
        # Toda prova emitida por este módulo é local. Esses campos não são
        # parâmetros do construtor para não abrirem alegações de certificação.
        object.__setattr__(self, "scope", "local_runtime")
        object.__setattr__(self, "external_validation", False)
        object.__setattr__(self, "contract_sha256", contract_sha256)
        object.__setattr__(self, "criterion_records", tuple(criterion_records))
        object.__setattr__(self, "execution_id", execution_id)
        object.__setattr__(self, "_run_seal", _run_seal)
        object.__setattr__(self, "_seal", _seal)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError("TrustedTestEvidence é imutável.")
        object.__setattr__(self, name, value)

    def to_dict(self) -> Dict[str, Any]:
        """Expõe metadados auditáveis sem expor o selo interno."""
        return {
            "spec_id": self.spec_id,
            "test_file": self.test_file,
            "executed": self.executed,
            "passed": self.passed,
            "returncode": self.returncode,
            "summary": self.summary,
            "error": self.error,
            "scope": self.scope,
            "external_validation": self.external_validation,
            "contract_sha256": self.contract_sha256,
            "criterion_records": tuple(
                record.to_dict()
                if type(record) is CriterionRuntimeRecord
                else {"invalid_record": True}
                for record in self.criterion_records
            ),
        }


def _canonical_spec_test_file(test_file: Any) -> Optional[str]:
    """Normaliza um ``test_file`` relativo, recusando escapes do repositório."""
    if not isinstance(test_file, str) or not test_file.strip() or "\x00" in test_file:
        return None

    candidate = Path(test_file)
    if candidate.is_absolute():
        return None

    try:
        root = Path(REPO_ROOT).resolve()
        resolved = (root / candidate).resolve()
    except (OSError, RuntimeError):
        return None
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        return None
    if relative == Path("."):
        return None
    return relative.as_posix()


def _issue_trusted_test_evidence(
    spec_id: str,
    test_file: str,
    *,
    executed: bool,
    passed: bool,
    returncode: Optional[int],
    summary: str,
    error: Optional[str] = None,
    contract_sha256: Optional[str] = None,
    criterion_records: Tuple[CriterionRuntimeRecord, ...] = (),
    execution_id: Optional[str] = None,
    _run_seal: object = _UNSET_RUNTIME_RUN_SEAL,
) -> TrustedTestEvidence:
    """Emite evidência selada; uso restrito ao runtime em ``tdd_runner``."""
    if _run_seal is _UNSET_RUNTIME_RUN_SEAL:
        _run_seal = object()
    if execution_id is None:
        execution_id = uuid.uuid4().hex
    return TrustedTestEvidence(
        spec_id=spec_id,
        test_file=test_file,
        executed=executed,
        passed=passed,
        returncode=returncode,
        summary=summary,
        error=error,
        contract_sha256=contract_sha256,
        criterion_records=tuple(criterion_records),
        execution_id=execution_id,
        _run_seal=_run_seal,
        _seal=_RUNTIME_TEST_EVIDENCE_SEAL,
    )


def _issue_criterion_runtime_record(
    *,
    spec_id: str,
    test_file: str,
    criterion_id: str,
    test_target: str,
    executed: bool,
    passed: bool,
    returncode: Optional[int],
    summary: str,
    error: Optional[str],
    passed_count: int,
    failed_count: int,
    skipped_count: int,
    xfailed_count: int,
    xpassed_count: int,
    error_count: int,
    collected_count: int,
    contract_sha256: Optional[str],
    execution_id: str,
    _run_seal: object,
) -> CriterionRuntimeRecord:
    """Emite um registro individual; somente o runner conhece o selo de execução."""
    return CriterionRuntimeRecord(
        spec_id=spec_id,
        test_file=test_file,
        criterion_id=criterion_id,
        test_target=test_target,
        executed=executed,
        passed=passed,
        returncode=returncode,
        summary=summary,
        error=error,
        passed_count=passed_count,
        failed_count=failed_count,
        skipped_count=skipped_count,
        xfailed_count=xfailed_count,
        xpassed_count=xpassed_count,
        error_count=error_count,
        collected_count=collected_count,
        contract_sha256=contract_sha256,
        execution_id=execution_id,
        _run_seal=_run_seal,
        _seal=_RUNTIME_CRITERION_RECORD_SEAL,
    )


def _matches_trusted_test_evidence(
    evidence: Any,
    spec: Specification,
) -> bool:
    """Valida identidade, vínculo e êxito da evidência de execução real."""
    expected_test_file = _canonical_spec_test_file(spec.test_file)
    return (
        type(evidence) is TrustedTestEvidence
        and evidence._seal is _RUNTIME_TEST_EVIDENCE_SEAL
        and evidence.spec_id == spec.spec_id
        and expected_test_file is not None
        and evidence.test_file == expected_test_file
        and evidence.scope == "local_runtime"
        and evidence.external_validation is False
        and evidence.executed is True
        and evidence.passed is True
        and type(evidence.returncode) is int
        and evidence.returncode == 0
    )


def _normalise_markdown_heading(heading: str) -> str:
    """Normaliza títulos Markdown para comparação tolerante a acentos e numeração."""
    normalized = unicodedata.normalize("NFKD", heading)
    normalized = normalized.encode("ascii", "ignore").decode("ascii").casefold()
    normalized = re.sub(r"^\s*\d+(?:\.\d+)*[.)]?\s*", "", normalized)
    return " ".join(normalized.split())


def _is_executable_criteria_heading(heading: str) -> bool:
    """Informa se o título inicia uma seção de contratos executáveis."""
    return _normalise_markdown_heading(heading).startswith(
        "criterios de aceitacao executaveis"
    )


def _clean_criterion_description(raw_description: str) -> str:
    """Remove o separador visual entre o ID Markdown e sua descrição."""
    return raw_description.lstrip(" \t—–-:").strip()


def _parse_executable_acceptance_criteria(content: str) -> List[Tuple[str, str]]:
    """Extrai apenas itens com ID em crase da seção executável da spec.

    Seções narrativas de critérios continuam deliberadamente fora do parser:
    elas não possuem um esquema de evidência estável e não devem alterar o
    comportamento das specs legadas.
    """
    criteria: List[Tuple[str, str]] = []
    seen_ids = set()
    active = False
    section_level = 0
    current_id: Optional[str] = None
    current_description: List[str] = []

    def flush_current() -> None:
        nonlocal current_id, current_description
        if current_id is None:
            return
        if current_id in seen_ids:
            logger.warning(
                "Critério executável duplicado ignorado: %s", current_id
            )
        else:
            seen_ids.add(current_id)
            criteria.append((current_id, " ".join(current_description).strip()))
        current_id = None
        current_description = []

    in_code_fence = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        heading_match = _MARKDOWN_HEADING_RE.match(line)
        if heading_match:
            heading_level = len(heading_match.group(1))
            if active and heading_level <= section_level:
                flush_current()
                break
            if _is_executable_criteria_heading(heading_match.group(2)):
                flush_current()
                active = True
                section_level = heading_level
            continue

        if not active:
            continue

        criterion_match = _MARKDOWN_CRITERION_RE.match(line)
        if criterion_match:
            flush_current()
            criterion_id = criterion_match.group("criterion_id").strip()
            if criterion_id:
                current_id = criterion_id
                description = _clean_criterion_description(
                    criterion_match.group("description")
                )
                if description:
                    current_description.append(description)
            continue

        if current_id is not None and stripped and line[:1].isspace():
            current_description.append(stripped)

    if active:
        flush_current()
    return criteria


_MISSING_EVIDENCE_CONTRACT = object()


def _canonical_evidence_contract_sha256(contract: Mapping[str, Any]) -> str:
    """Calcula SHA-256 do contrato na serialização JSON canônica UTF-8.

    Chaves são ordenadas, separadores são estáveis e a ordem declarada dentro
    de cada lista de nodeids é preservada. Assim o fingerprint não depende da
    formatação YAML nem da ordem de chaves do frontmatter.
    """
    canonical = json.dumps(
        contract,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _validate_evidence_contract(
    raw_contract: Any,
    *,
    declared: bool,
    criterion_ids: List[str],
    test_file: str,
) -> Tuple[str, bool, Optional[str], Optional[str], Mapping[str, Tuple[str, ...]]]:
    """Valida e normaliza o contrato granular de frontmatter em fail-closed."""
    if not declared:
        return "legacy", False, None, None, MappingProxyType({})

    if not isinstance(raw_contract, Mapping):
        return (
            "invalid",
            False,
            "evidence_contract deve ser um mapa YAML.",
            None,
            MappingProxyType({}),
        )

    raw_mode = raw_contract.get("mode")
    mode = raw_mode if isinstance(raw_mode, str) and raw_mode else "invalid"
    errors: List[str] = []
    allowed_keys = {"version", "mode", "criteria"}
    unexpected_keys = set(raw_contract) - allowed_keys
    missing_keys = allowed_keys - set(raw_contract)
    if missing_keys:
        errors.append(
            "campos obrigatórios ausentes: " + ", ".join(sorted(missing_keys))
        )
    if unexpected_keys:
        errors.append(
            "campos não reconhecidos: " + ", ".join(sorted(map(str, unexpected_keys)))
        )
    if type(raw_contract.get("version")) is not int or raw_contract.get("version") != 1:
        errors.append("version deve ser o inteiro 1")
    if raw_contract.get("mode") != _CRITERION_RUNTIME_V1_MODE:
        errors.append(f"mode deve ser {_CRITERION_RUNTIME_V1_MODE!r}")

    raw_targets = raw_contract.get("criteria")
    if not isinstance(raw_targets, Mapping):
        errors.append("criteria deve ser um mapa criterion_id→lista de nodeids")
        raw_targets = {}

    expected_ids = set(criterion_ids)
    target_ids = set(raw_targets) if isinstance(raw_targets, Mapping) else set()
    non_string_ids = [criterion_id for criterion_id in target_ids if not isinstance(criterion_id, str)]
    if non_string_ids:
        errors.append("criteria contém criterion_id não textual")
    missing_ids = expected_ids - target_ids
    extra_ids = target_ids - expected_ids
    if missing_ids:
        errors.append(
            "sem nodeids para critérios Markdown: " + ", ".join(sorted(missing_ids))
        )
    if extra_ids:
        errors.append(
            "nodeids declarados para critérios inexistentes: "
            + ", ".join(sorted(map(str, extra_ids)))
        )
    if not criterion_ids:
        errors.append("contrato granular exige ao menos um critério Markdown")

    normalized_targets: Dict[str, Tuple[str, ...]] = {}
    for criterion_id in criterion_ids:
        targets = raw_targets.get(criterion_id) if isinstance(raw_targets, Mapping) else None
        if not isinstance(targets, list) or not targets:
            errors.append(
                f"{criterion_id}: a associação deve ser uma lista não vazia de nodeids"
            )
            continue
        normalized_for_criterion: List[str] = []
        for target in targets:
            canonical_target, target_error = _validate_criterion_test_target(
                target,
                test_file,
            )
            if canonical_target is None:
                errors.append(f"{criterion_id}: {target_error}")
                continue
            if canonical_target in normalized_for_criterion:
                errors.append(f"{criterion_id}: nodeid duplicado: {canonical_target}")
                continue
            normalized_for_criterion.append(canonical_target)
        if len(normalized_for_criterion) != len(targets):
            continue
        normalized_targets[criterion_id] = tuple(normalized_for_criterion)

    if errors:
        return mode, False, "; ".join(errors), None, MappingProxyType({})

    canonical_contract: Dict[str, Any] = {
        "version": 1,
        "mode": _CRITERION_RUNTIME_V1_MODE,
        "criteria": {
            criterion_id: list(normalized_targets[criterion_id])
            for criterion_id in sorted(normalized_targets)
        },
    }
    return (
        _CRITERION_RUNTIME_V1_MODE,
        True,
        None,
        _canonical_evidence_contract_sha256(canonical_contract),
        MappingProxyType(normalized_targets),
    )


def _evidence_for_criterion(output: Any, criterion_id: str) -> Any:
    """Obtém evidência explícita de um contrato sem inferi-la de outro ID."""
    if not isinstance(output, Mapping):
        return None

    for container_key in _EVIDENCE_CONTAINER_KEYS:
        container = output.get(container_key)
        if isinstance(container, Mapping) and criterion_id in container:
            return container[criterion_id]
        if isinstance(container, (list, tuple)):
            for item in container:
                if not isinstance(item, Mapping):
                    continue
                item_id = item.get("criterion_id", item.get("id"))
                if item_id == criterion_id:
                    return item

    # Também permite o formato compacto {"id-do-criterio": {...}}, que
    # permanece estruturado e inequivocamente vinculado ao contrato.
    return output.get(criterion_id)


def _is_positive_evidence(evidence: Any) -> bool:
    """Aceita somente sinais positivos explícitos; valores truthy não bastam."""
    if evidence is True:
        return True
    if not isinstance(evidence, Mapping):
        return False
    if evidence.get("passed") is True or evidence.get("verified") is True:
        return True
    status = evidence.get("status")
    return isinstance(status, str) and status.casefold() in _POSITIVE_EVIDENCE_STATUSES


def _check_structured_evidence(criterion_id: str) -> Callable[[Any], bool]:
    """Cria o verificador fechado de um critério extraído do Markdown."""
    return lambda output: _is_positive_evidence(
        _evidence_for_criterion(output, criterion_id)
    )


def _metadata_text(meta: Dict[str, Any], key: str, default: str = "") -> str:
    """Converte metadados YAML em texto sem propagar ``None`` ao domínio SDD."""
    value = meta.get(key, default)
    return value if isinstance(value, str) else str(value) if value is not None else default


class SpecRegistry:
    """Registro central de especificações (formais + dinâmicas)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpecRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.specs: Dict[str, Specification] = {}
        self._initialized = True
        self.load_formal_specs()

    def load_formal_specs(self, specs_dir: str = SPECS_DIR) -> int:
        """Carrega as especificações formais de specs/*.md."""
        count = 0
        for path in sorted(glob.glob(os.path.join(specs_dir, "SPEC-*.md"))):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                meta = _parse_spec_frontmatter(content)
                spec_id = meta.get("spec_id")
                if not spec_id:
                    continue
                parsed_criteria = _parse_executable_acceptance_criteria(content)
                test_file = _metadata_text(meta, "test_file")
                declared_status = _metadata_text(meta, "status", "draft")
                raw_contract = meta.get(
                    "evidence_contract",
                    _MISSING_EVIDENCE_CONTRACT,
                )
                contract_declared = raw_contract is not _MISSING_EVIDENCE_CONTRACT
                (
                    contract_mode,
                    contract_valid,
                    contract_error,
                    contract_sha256,
                    criterion_test_targets,
                ) = _validate_evidence_contract(
                    raw_contract,
                    declared=contract_declared,
                    criterion_ids=[criterion_id for criterion_id, _ in parsed_criteria],
                    test_file=test_file,
                )
                spec = Specification(
                    spec_id=_metadata_text(meta, "spec_id"),
                    title=_metadata_text(meta, "title"),
                    objective=(
                        "Especificação formal do componente "
                        f"{_metadata_text(meta, 'component')}"
                    ),
                    component=_metadata_text(meta, "component"),
                    test_file=test_file,
                    evidence_contract_mode=contract_mode,
                    evidence_contract_valid=contract_valid,
                    evidence_contract_error=contract_error,
                    evidence_contract_sha256=contract_sha256,
                    criterion_test_targets=criterion_test_targets,
                    declared_status=declared_status,
                    evidence_contract_declared=contract_declared,
                    evidence_contract_test_file=(
                        _canonical_spec_test_file(test_file)
                        if contract_valid
                        else None
                    ),
                )
                # Um contrato declarado (inclusive um contrato malformado) não
                # pode herdar ``green`` do frontmatter. A promoção depende de
                # evidência runtime emitida na execução corrente.
                spec.status = "red" if contract_declared else declared_status
                for criterion_id, description in parsed_criteria:
                    spec.criteria.append(
                        AcceptanceCriterion(
                            criterion_id=criterion_id,
                            description=description,
                            check_fn=_check_structured_evidence(criterion_id),
                            requires_trusted_test_evidence=True,
                        )
                    )
                self.specs[spec.spec_id] = spec
                metabus.publish_subsystem_event(
                    "sdd",
                    "spec.loaded",
                    {
                        "spec_id": spec.spec_id,
                        "title": spec.title,
                        "status": spec.status,
                        "criteria_count": len(spec.criteria),
                        "evidence_contract_mode": spec.evidence_contract_mode,
                        "evidence_contract_valid": spec.evidence_contract_valid,
                    },
                    source_agent="spec_registry",
                )
                count += 1
            except Exception as e:
                logger.error(f"Erro ao carregar spec {path}: {e}")
        logger.info(f"{count} especificações formais carregadas.")
        return count

    def create_task_spec(self, title: str, objective: str,
                         criteria_descriptions: Optional[List[str]] = None) -> Specification:
        """Cria uma especificação dinâmica para uma tarefa (usada pelos agentes)."""
        spec_id = f"TSPEC-{uuid.uuid4().hex[:8]}"
        spec = Specification(spec_id, title, objective)
        for desc in (criteria_descriptions or []):
            spec.add_criterion(desc)
        spec.status = "red"  # nasce em RED: critérios definidos, entrega ainda ausente
        self.specs[spec_id] = spec
        metabus.publish_subsystem_event(
            "sdd",
            "spec.created",
            {"spec_id": spec_id, "title": title, "criteria_count": len(spec.criteria)},
            source_agent="spec_registry",
        )
        metabus.memory.upsert_semantic_topic(
            "sdd.specs",
            lesson=f"Spec dinâmica criada: {spec_id} ({title}).",
            metadata={"last_spec_id": spec_id},
        )
        return spec

    def get(self, spec_id: str) -> Optional[Specification]:
        return self.specs.get(spec_id)

    def coverage_report(self) -> Dict[str, Any]:
        """Relatório de cobertura: quais componentes têm spec e teste vinculados."""
        return {
            "total_specs": len(self.specs),
            "formal": [s.to_dict() for s in self.specs.values() if s.spec_id.startswith("SPEC-")],
            "dynamic": [s.to_dict() for s in self.specs.values() if s.spec_id.startswith("TSPEC-")],
        }


def _strict_contract_targets_for_spec(
    spec: Specification,
) -> Optional[Mapping[str, Tuple[str, ...]]]:
    """Revalida a configuração v1 antes de confiar nela no verificador.

    A checagem no carregamento é a primeira barreira. Esta segunda checagem
    impede que uma mutação posterior dos atributos públicos da spec altere os
    alvos sem também invalidar o fingerprint canônico do contrato.
    """
    if (
        spec.evidence_contract_mode != _CRITERION_RUNTIME_V1_MODE
        or spec.evidence_contract_valid is not True
        or not isinstance(spec.evidence_contract_sha256, str)
        or not _SHA256_HEX_RE.fullmatch(spec.evidence_contract_sha256)
        or not isinstance(spec.criterion_test_targets, Mapping)
    ):
        return None

    canonical_test_file = _canonical_spec_test_file(spec.test_file)
    if (
        canonical_test_file is None
        or canonical_test_file != getattr(spec, "_evidence_contract_test_file", None)
    ):
        return None

    criterion_ids = [
        criterion.criterion_id
        for criterion in spec.criteria
        if criterion.requires_trusted_test_evidence
    ]
    expected_ids = set(criterion_ids)
    if not criterion_ids or set(spec.criterion_test_targets) != expected_ids:
        return None

    normalized_targets: Dict[str, Tuple[str, ...]] = {}
    for criterion_id in criterion_ids:
        targets = spec.criterion_test_targets.get(criterion_id)
        if type(targets) is not tuple or not targets:
            return None
        normalized_for_criterion: List[str] = []
        for target in targets:
            canonical_target, _target_error = _validate_criterion_test_target(
                target,
                spec.test_file,
            )
            if (
                canonical_target is None
                or canonical_target != target
                or canonical_target in normalized_for_criterion
            ):
                return None
            normalized_for_criterion.append(canonical_target)
        normalized_targets[criterion_id] = tuple(normalized_for_criterion)

    canonical_contract: Dict[str, Any] = {
        "version": 1,
        "mode": _CRITERION_RUNTIME_V1_MODE,
        "criteria": {
            criterion_id: list(normalized_targets[criterion_id])
            for criterion_id in sorted(normalized_targets)
        },
    }
    if _canonical_evidence_contract_sha256(canonical_contract) != spec.evidence_contract_sha256:
        return None
    return MappingProxyType(normalized_targets)


def _record_has_passing_runtime_outcome(record: CriterionRuntimeRecord) -> bool:
    """Aplica os gates de coleta e resultado a um único nodeid v1."""
    count_names = (
        "passed_count",
        "failed_count",
        "skipped_count",
        "xfailed_count",
        "xpassed_count",
        "error_count",
        "collected_count",
    )
    if any(type(getattr(record, name)) is not int for name in count_names):
        return False
    if any(getattr(record, name) < 0 for name in count_names):
        return False
    return (
        record.executed is True
        and record.passed is True
        and type(record.returncode) is int
        and record.returncode == 0
        and record.error is None
        and record.passed_count >= 1
        and record.collected_count >= 1
        and record.failed_count == 0
        and record.skipped_count == 0
        and record.xfailed_count == 0
        and record.xpassed_count == 0
        and record.error_count == 0
    )


def _validate_criterion_runtime_evidence(
    evidence: Any,
    spec: Specification,
) -> Tuple[bool, Dict[str, bool]]:
    """Valida registros v1 por critério sem confiar em uma suíte global.

    O primeiro booleano é a validade global (todos os nodeids exigidos
    passaram). O mapa preserva a granularidade: uma falha em ``beta`` não
    transforma automaticamente o registro válido e selado de ``alpha`` em
    falha. Estruturas adulteradas, contudo, falham integralmente.
    """
    expected_targets = _strict_contract_targets_for_spec(spec)
    criterion_results = {
        criterion.criterion_id: False
        for criterion in spec.criteria
        if criterion.requires_trusted_test_evidence
    }
    if expected_targets is None:
        return False, criterion_results

    expected_test_file = _canonical_spec_test_file(spec.test_file)
    if (
        type(evidence) is not TrustedTestEvidence
        or evidence._seal is not _RUNTIME_TEST_EVIDENCE_SEAL
        or evidence.spec_id != spec.spec_id
        or expected_test_file is None
        or evidence.test_file != expected_test_file
        or evidence.scope != "local_runtime"
        or evidence.external_validation is not False
        or evidence.contract_sha256 != spec.evidence_contract_sha256
        or not isinstance(evidence.execution_id, str)
        or not evidence.execution_id
        or type(evidence.criterion_records) is not tuple
    ):
        return False, criterion_results

    expected_pairs = {
        (criterion_id, target)
        for criterion_id, targets in expected_targets.items()
        for target in targets
    }
    records_by_pair: Dict[Tuple[str, str], CriterionRuntimeRecord] = {}
    for record in evidence.criterion_records:
        if (
            type(record) is not CriterionRuntimeRecord
            or record._seal is not _RUNTIME_CRITERION_RECORD_SEAL
            or record.spec_id != spec.spec_id
            or record.test_file != expected_test_file
            or record.contract_sha256 != spec.evidence_contract_sha256
            or record.execution_id != evidence.execution_id
            or record._run_seal is not evidence._run_seal
        ):
            return False, criterion_results
        pair = (record.criterion_id, record.test_target)
        if pair not in expected_pairs or pair in records_by_pair:
            return False, criterion_results
        records_by_pair[pair] = record

    for criterion_id, targets in expected_targets.items():
        records = [records_by_pair.get((criterion_id, target)) for target in targets]
        criterion_results[criterion_id] = bool(records) and all(
            record is not None and _record_has_passing_runtime_outcome(record)
            for record in records
        )

    all_criteria_passed = bool(criterion_results) and all(criterion_results.values())
    envelope_is_green = (
        evidence.executed is True
        and evidence.passed is True
        and type(evidence.returncode) is int
        and evidence.returncode == 0
        and evidence.error is None
    )
    return all_criteria_passed and envelope_is_green, criterion_results


def _consume_strict_runtime_execution(evidence: TrustedTestEvidence) -> bool:
    """Permite apenas uma promoção por execução selada, bloqueando replay."""
    with _CONSUMED_STRICT_EXECUTIONS_LOCK:
        if evidence.execution_id in _CONSUMED_STRICT_EXECUTIONS:
            return False
        _CONSUMED_STRICT_EXECUTIONS.add(evidence.execution_id)
        return True


class SpecVerifier:
    """
    Verificador SDD/TDD: valida entregas contra os critérios de aceitação.
    Implementa a transição RED → GREEN do ciclo TDD.
    """

    def __init__(self, registry: Optional[SpecRegistry] = None):
        self.registry = registry or SpecRegistry()

    def verify(
        self,
        spec_id: str,
        output: Any,
        *,
        trusted_test_evidence: Optional[TrustedTestEvidence] = None,
    ) -> Dict[str, Any]:
        """Executa todos os critérios da spec contra a entrega.

        Critérios extraídos de Markdown não aceitam campos declarados pela
        entrega como prova. Eles exigem uma ``TrustedTestEvidence`` emitida pelo
        runtime para o ``test_file`` registrado na própria especificação.
        Critérios programáticos e specs legadas preservam o contrato histórico.
        """
        spec = self.registry.get(spec_id)
        if spec is None:
            return {"spec_id": spec_id, "verified": False,
                    "error": "Especificação não encontrada."}

        output_present = output is not None
        runtime_evidence_required = spec.requires_trusted_test_evidence
        uses_criterion_runtime_records = bool(
            runtime_evidence_required and spec.requires_criterion_runtime_records
        )
        strict_criterion_results: Dict[str, bool] = {}
        if uses_criterion_runtime_records:
            runtime_evidence_valid, strict_criterion_results = (
                _validate_criterion_runtime_evidence(trusted_test_evidence, spec)
            )
            # Uma execução completa é consumida na primeira tentativa com uma
            # entrega. Isso impede que o mesmo objeto selado seja reciclado em
            # outra promoção após a saída do agente mudar.
            if runtime_evidence_valid and output_present:
                if not _consume_strict_runtime_execution(trusted_test_evidence):
                    runtime_evidence_valid = False
                    strict_criterion_results = {
                        criterion_id: False
                        for criterion_id in strict_criterion_results
                    }
        else:
            runtime_evidence_valid = (
                _matches_trusted_test_evidence(trusted_test_evidence, spec)
                if runtime_evidence_required
                else False
            )
        results = []
        for criterion in spec.criteria:
            # Uma entrega ausente não pode ser promovida por uma função de
            # critério permissiva. Contratos Markdown só podem ser aprovados
            # pela execução de teste vinculada e selada pelo runtime, nunca
            # por ``{"evidence": {"id": {"passed": True}}}`` do agente.
            if criterion.requires_trusted_test_evidence:
                if uses_criterion_runtime_records:
                    passed = output_present and strict_criterion_results.get(
                        criterion.criterion_id,
                        False,
                    )
                else:
                    passed = output_present and runtime_evidence_valid
            else:
                passed = output_present and criterion.check(output)
            results.append({
                "criterion_id": criterion.criterion_id,
                "description": criterion.description,
                "passed": passed,
            })

        all_passed = all(r["passed"] for r in results) if results else False
        spec.status = "green" if all_passed else "red"

        result = {
            "spec_id": spec_id,
            "verified": all_passed,
            "status": spec.status,
            "criteria_results": results,
            "passed_count": sum(1 for r in results if r["passed"]),
            "total_count": len(results),
            "runtime_evidence_required": runtime_evidence_required,
            "runtime_evidence_valid": runtime_evidence_valid,
            "evidence_contract_mode": spec.evidence_contract_mode,
            "evidence_contract_valid": spec.evidence_contract_valid,
            "evidence_contract_error": spec.evidence_contract_error,
            "evidence_contract_sha256": spec.evidence_contract_sha256,
            "criterion_runtime_records_required": uses_criterion_runtime_records,
        }
        if isinstance(trusted_test_evidence, TrustedTestEvidence):
            result["trusted_test_evidence"] = trusted_test_evidence.to_dict()
        metabus.publish_subsystem_event(
            "sdd",
            "spec.verified",
            {
                "spec_id": spec_id,
                "verified": all_passed,
                "passed_count": result["passed_count"],
                "total_count": result["total_count"],
            },
            source_agent="spec_verifier",
        )
        metabus.memory.update_topic_confidence("sdd", 1.0 if all_passed else 0.4)
        return result


# Singletons globais
spec_registry = SpecRegistry()
spec_verifier = SpecVerifier(spec_registry)
