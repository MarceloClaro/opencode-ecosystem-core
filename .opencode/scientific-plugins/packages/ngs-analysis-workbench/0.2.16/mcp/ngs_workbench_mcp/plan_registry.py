"""Persist immutable execution plans outside the requested workspace."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Literal

from ngs_workbench_daemon.persistence.paths import registry_path

from .plans import NextflowRunPlan, SnakemakeRunPlan, plan_checksum

WorkflowEngine = Literal["nextflow", "snakemake"]
PlanBinding = WorkflowEngine
PlanModel = NextflowRunPlan | SnakemakeRunPlan

_PLAN_ID_PATTERN = re.compile(r"^ngs-plan-[0-9a-f]{16}$")
_SCHEMA_VERSION = 1


def _store_dir() -> Path:
    return registry_path().parent / "plans"


def _validate_binding(value: str) -> PlanBinding:
    if value not in {"nextflow", "snakemake"}:
        raise ValueError(f"unsupported plan binding: {value}")
    return value


def _validate_plan_id(value: str) -> str:
    normalized = value.strip()
    if not _PLAN_ID_PATTERN.fullmatch(normalized):
        raise ValueError("invalid plan_id; expected ngs-plan followed by 16 lowercase hex digits")
    return normalized


def _plan_model(binding: PlanBinding, payload: dict[str, Any]) -> PlanModel:
    if binding == "nextflow":
        return NextflowRunPlan.model_validate(payload)
    return SnakemakeRunPlan.model_validate(payload)


def _derive_plan_id(plan_checksum_value: str) -> str:
    """Return a compact lookup handle for one canonical plan checksum."""
    prefix = "sha256:"
    if not plan_checksum_value.startswith(prefix):
        raise ValueError("plan checksum must use the sha256 scheme")
    return f"ngs-plan-{plan_checksum_value.removeprefix(prefix)[:16]}"


def _prepare_store() -> Path:
    directory = _store_dir()
    if directory.parent.is_symlink():
        raise OSError(f"plugin state directory must not be a symlink: {directory.parent}")
    if directory.is_symlink():
        raise OSError(f"plan registry must not be a symlink: {directory}")
    directory.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(directory, 0o700)
    return directory


def _read_record(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"unknown plan_id: {path.stem}; create a fresh plan first") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read registered plan {path.stem}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != _SCHEMA_VERSION:
        raise ValueError(f"registered plan is malformed: {path.stem}")
    return value


def _write_immutable(path: Path, record: dict[str, Any]) -> None:
    payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if _read_record(path) != record:
            raise ValueError(f"plan ID collision or immutable plan changed: {path.stem}")
        return

    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.stem}.",
        suffix=".tmp",
        text=True,
    )
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary_path, path)
        except FileExistsError:
            if _read_record(path) != record:
                raise ValueError(
                    f"plan ID collision or immutable plan changed: {path.stem}"
                ) from None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        temporary_path.unlink(missing_ok=True)


def register_plan(binding: PlanBinding, payload: dict[str, Any]) -> dict[str, Any]:
    """Register a successful plan and add its native-approval identity."""
    if payload.get("ok") is not True:
        return payload

    validated_binding = _validate_binding(binding)
    plan = _plan_model(validated_binding, payload)
    plan_checksum_value = plan_checksum(plan)
    plan_name = plan.request.display_name
    plan_id = _derive_plan_id(plan_checksum_value)
    record = {
        "schema_version": _SCHEMA_VERSION,
        "binding": validated_binding,
        "plan_name": plan_name,
        "plan_id": plan_id,
        "plan_checksum": plan_checksum_value,
        "plan": plan.model_dump(mode="json"),
    }
    directory = _prepare_store()
    path = directory / f"{plan_id}.json"
    if path.is_symlink():
        raise OSError(f"registered plan must not be a symlink: {path}")
    _write_immutable(path, record)

    return {
        **payload,
        "kind": "plan",
        "status": "ready" if plan.runnable else "blocked",
        "binding": validated_binding,
        "plan_name": plan_name,
        "plan_id": plan_id,
        "plan_checksum": plan_checksum_value,
        "plan_registry": {
            "scope": "plugin_control_plane",
            "workspace_effects": False,
        },
    }


def load_approved_plan(
    plan_name: str,
    plan_id: str,
    plan_checksum_value: str,
) -> tuple[PlanBinding, PlanModel]:
    """Load and verify the exact immutable identity shown by the native host."""
    normalized_id = _validate_plan_id(plan_id)
    path = _store_dir() / f"{normalized_id}.json"
    if path.is_symlink():
        raise ValueError(f"registered plan must not be a symlink: {path}")
    record = _read_record(path)

    binding = _validate_binding(str(record.get("binding", "")))
    if record.get("plan_name") != plan_name:
        raise ValueError("plan name does not match the registered plan")
    if record.get("plan_id") != normalized_id:
        raise ValueError("registered plan ID does not match the requested plan_id")
    if record.get("plan_checksum") != plan_checksum_value:
        raise ValueError("plan checksum does not match the registered plan")

    payload = record.get("plan")
    if not isinstance(payload, dict):
        raise ValueError(f"registered plan is malformed: {normalized_id}")
    plan = _plan_model(binding, payload)
    if plan.request.display_name != plan_name:
        raise ValueError("registered plan contents do not match the approved name")
    if plan_checksum(plan) != plan_checksum_value:
        raise ValueError("registered plan contents do not match the approved checksum")
    if _derive_plan_id(plan_checksum_value) != normalized_id:
        raise ValueError("registered plan contents do not match the approved plan ID")
    return binding, plan
