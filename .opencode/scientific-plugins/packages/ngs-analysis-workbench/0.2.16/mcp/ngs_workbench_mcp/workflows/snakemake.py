"""Run bundled Snakemake workflows through one generic MCP lifecycle."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from ngs_workbench_daemon.protocol import (
    ExecutionRequest,
    FileOperation,
    current_controller_environment,
    run_metadata_directory,
)
from pydantic import ValidationError

from .. import compute_targets, preparation, readiness_service, runs
from ..compute_targets import ComputeTarget
from ..plans import (
    InputSummary,
    MonitoringPlan,
    PreparationSpec,
    RemoteExecution,
    RunEffects,
    SnakemakePlanRequest,
    SnakemakeRunPlan,
    controller_launch_argv,
    normalize_display_name,
    plan_checksum,
)
from ..readiness.models import (
    ReadinessAssessment,
    RequirementSet,
    RuntimeRequirement,
)
from .remote import staged_source_files
from .source import WorkflowSource, observe_source, source_sha256

BINDING = "snakemake"


def describe_remote_execution(
    *,
    target: ComputeTarget,
    source_root: Path,
    local_run_dir: Path,
    run_dir: Path,
) -> RemoteExecution:
    """Bind workflow source deployment without transferring scientific inputs."""
    if target.config_hash is None or target.host_access is None or target.workspace_root is None:
        raise ValueError("SSH target is missing its approved connection or workspace")
    remote_root = PurePosixPath(run_dir)
    staged = staged_source_files(
        source_root=source_root,
        local_run_dir=local_run_dir,
        remote_run_dir=remote_root,
    )

    return RemoteExecution(
        config_hash=target.config_hash,
        host_access=target.host_access,
        workspace_root=target.workspace_root,
        run_dir=remote_root.as_posix(),
        executor="local_process",
        staged_files=staged,
    )


def _new_run_id(pipeline: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    pipeline_slug = pipeline.replace("_", "-")[:61]
    return f"snakemake-{pipeline_slug}-{stamp}-{uuid.uuid4().hex[:8]}"


def _plan_error(*errors: str, **details: Any) -> dict[str, Any]:
    return {"ok": False, "errors": list(errors), **details}


def resolve_runtime_requirements(
    workflow_id: str,
    config_file: Path,
    config_text: str | None = None,
) -> RequirementSet:
    """Check only the controller shared by bundled and external workflows."""
    blockers = (
        [f"config_file does not exist or is not a file: {config_file}"]
        if config_text is None and not config_file.is_file()
        else []
    )
    return RequirementSet(
        binding=BINDING,
        pipeline=workflow_id,
        requirements=[
            RuntimeRequirement(
                id="snakemake",
                layer="workflow_controller",
                capability="command",
                value="snakemake",
                source="request.binding",
                detail="the Snakemake binding executes workflows with Snakemake",
                probe_mode="version",
            )
        ],
        blockers=blockers,
    )


def assess_readiness(
    workflow_id: str,
    config_file: Path,
    runtime_snapshot_id: str | None = None,
    config_text: str | None = None,
    *,
    target_id: str = "local",
    controller_candidate_id: str | None = None,
    refresh: bool = False,
) -> ReadinessAssessment:
    """Compose workflow requirements with generic runtime observation and evaluation."""
    target = compute_targets.resolve_compute_target(target_id)
    config_blockers = []
    if target.controller_transport == "ssh" and config_text is None:
        try:
            preparation.inspect_input(config_file, None, target_id)
            config_text = ""
        except (OSError, ValueError) as exc:
            config_blockers.append(str(exc))
            config_text = ""
    requirement_set = resolve_runtime_requirements(
        workflow_id,
        config_file,
        config_text,
    )
    requirement_set.blockers.extend(config_blockers)
    if target.controller_transport == "ssh" and target.executor != "local_process":
        requirement_set.blockers.append(
            "Snakemake does not support the selected remote task executor"
        )
    return readiness_service.assess(
        requirement_set,
        runtime_snapshot_id,
        target_id=target_id,
        controller_candidate_id=controller_candidate_id,
        refresh=refresh,
    )


def _sha256_tree(root: Path) -> str:
    return source_sha256(root)


def inspect_workflow(pipeline: str, source: WorkflowSource) -> WorkflowSource:
    """Identify an explicit source without changing bundled workflow ownership."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,95}", pipeline):
        raise ValueError("invalid workflow identifier")
    observed = observe_source(source)
    if observed.engine != BINDING:
        raise ValueError("workflow engine does not match the Snakemake binding")
    return observed


def _config_target(run_dir: Path | PurePosixPath, config_file: Path) -> Path | PurePosixPath:
    return run_dir / "config" / config_file.name


def build_snakemake_argv(
    request: SnakemakePlanRequest,
    run_dir: Path | PurePosixPath,
    *,
    snakemake_argv_prefix: list[str],
) -> list[str]:
    """Build the literal argv for any approved Snakemake workflow."""
    return [
        *snakemake_argv_prefix,
        "--snakefile",
        str(run_dir / "workflow" / request.workflow_source.entrypoint),
        "--configfile",
        (
            request.config_file
            if request.remote is not None
            else str(_config_target(run_dir, Path(request.config_file)))
        ),
        "--directory",
        str(run_dir / "results"),
        "--cores",
        str(request.cores),
        "--printshellcmds",
    ]


def plan_run(
    pipeline: str,
    run_dir: str,
    config_file: str,
    cores: int = 4,
    run_id: str | None = None,
    first_run_id: str | None = None,
    attempt_number: int | None = 1,
    workflow_version_id: str | None = None,
    display_name: str | None = None,
    runtime_snapshot_id: str | None = None,
    controller_candidate_id: str | None = None,
    preparation_spec: PreparationSpec | None = None,
    *,
    target_id: str = "local",
    refresh_runtime: bool = False,
    workflow_source: WorkflowSource,
    workflow_name: str | None = None,
) -> dict[str, Any]:
    """Build a read-only plan for any approved Snakemake workflow."""
    try:
        observed_source = inspect_workflow(pipeline, workflow_source)
    except ValueError as exc:
        return _plan_error(str(exc))
    try:
        target = compute_targets.resolve_compute_target(target_id)
        execution_dir = runs.resolve_run_directory(run_dir, target_id)
    except ValueError as exc:
        return _plan_error(str(exc))
    if target.controller_transport == "ssh" and target.executor != "local_process":
        return _plan_error("Snakemake does not support the selected remote task executor")
    resolved_run_id = run_id or _new_run_id(pipeline)
    metadata_dir = run_metadata_directory(target_id, str(execution_dir))
    staging_dir = metadata_dir if target.controller_transport == "ssh" else execution_dir
    if target.controller_transport != "ssh" and execution_dir.is_relative_to(
        Path(observed_source.root)
    ):
        return _plan_error("workflow source must not contain its execution directory")

    try:
        resolved_config = preparation.resolve_input_path(config_file, target_id)
    except ValueError as exc:
        return _plan_error(str(exc))
    if resolved_config is None:
        return _plan_error("config_file is required")
    config_text = (
        ""
        if target.controller_transport == "ssh"
        else preparation.generated_text(preparation_spec, resolved_config)
    )
    blockers: list[str] = []
    config_sha256 = None
    try:
        snapshot = preparation.inspect_input(resolved_config, preparation_spec, target_id)
        config_sha256 = snapshot["sha256"]
    except (OSError, ValueError) as exc:
        blockers.append(str(exc))

    workflow_sha256 = None
    workflow_root = Path(observed_source.root)
    snakefile = workflow_root / observed_source.entrypoint
    if not workflow_root.is_dir() or not snakefile.is_file():
        blockers.append(f"approved Snakefile does not exist: {snakefile}")
    else:
        workflow_sha256 = _sha256_tree(workflow_root)

    try:
        readiness_arguments: dict[str, Any] = {
            "target_id": target.target_id,
            "controller_candidate_id": controller_candidate_id,
            "refresh": refresh_runtime,
        }
        readiness = ReadinessAssessment.model_validate(
            assess_readiness(
                pipeline,
                resolved_config,
                runtime_snapshot_id,
                config_text,
                **readiness_arguments,
            )
        )
    except ValueError as exc:
        return _plan_error(str(exc))
    if readiness.binding is not None and readiness.binding != BINDING:
        return _plan_error("readiness does not match the selected workflow engine")
    readiness = readiness.model_copy(update={"binding": BINDING})
    blockers.extend(readiness.blockers)
    blockers.extend(f"readiness unresolved: {item}" for item in readiness.unknowns)
    try:
        runs.check_run_directory(execution_dir, target_id)
    except (OSError, ValueError) as exc:
        blockers.append(str(exc))

    remote = None
    if target.controller_transport == "ssh":
        if readiness.host is None or readiness.host.os.lower() != "linux":
            blockers.append("SSH workflow execution requires an observed Linux controller host")
        else:
            try:
                remote = describe_remote_execution(
                    target=target,
                    source_root=workflow_root,
                    local_run_dir=metadata_dir,
                    run_dir=execution_dir,
                )
            except (OSError, ValueError) as exc:
                blockers.append(f"SSH workflow staging could not be resolved: {exc}")

    try:
        request = SnakemakePlanRequest(
            pipeline=pipeline,
            workflow_version_id=workflow_version_id,
            target=target.ref(),
            remote=remote,
            display_name=normalize_display_name(display_name, workflow_name or pipeline),
            # LEGACY_CLEANUP(2026-09-07): Revalidating pre-lineage approvals passes None;
            # preserve absent fields/checksum until those saved plans are unsupported.
            first_run_id=first_run_id or (resolved_run_id if attempt_number is not None else None),
            attempt_number=attempt_number,
            workflow=observed_source.entrypoint,
            run_dir=str(execution_dir),
            config_file=str(resolved_config),
            config_sha256=config_sha256,
            workflow_sha256=workflow_sha256,
            cores=cores,
            runtime_snapshot_id=readiness.snapshot_id,
            controller_candidate_id=(
                readiness.selected_controller.candidate_id
                if readiness.selected_controller is not None
                else controller_candidate_id
            ),
            workflow_source=observed_source,
            run_id=resolved_run_id,
        )
    except ValidationError as exc:
        return _plan_error(*[error["msg"] for error in exc.errors()])

    config_target = _config_target(execution_dir, resolved_config)
    launch_log = execution_dir / "logs" / "snakemake.log"
    approved_plan = metadata_dir / "workflow" / "approved_plan.json"
    controller_run_dir = execution_dir
    effects_root = execution_dir
    draft = SnakemakeRunPlan(
        runnable=not blockers and readiness.status == "ready",
        request=request,
        command_argv=build_snakemake_argv(
            request,
            controller_run_dir,
            snakemake_argv_prefix=controller_launch_argv(readiness, "snakemake"),
        ),
        readiness=readiness,
        input_summary=InputSummary(
            source="config_file",
            path=str(resolved_config),
            sha256=config_sha256,
        ),
        effects=RunEffects(
            run_dir=str(effects_root),
            output_dir=str(effects_root / "results"),
            work_dir=str(effects_root / "results"),
            launch_log=str(effects_root / "logs" / "snakemake.log"),
            local_writes=[
                *(
                    preparation_spec.writes
                    if preparation_spec is not None and remote is None
                    else []
                ),
                *runs.registry_effect_paths(),
                *([str(metadata_dir)] if remote is not None else []),
                str(staging_dir / "workflow"),
                *([str(config_target)] if remote is None else []),
                str(approved_plan),
                *(
                    [
                        str(execution_dir / "results"),
                        str(execution_dir / "results" / ".snakemake"),
                        str(launch_log),
                    ]
                    if remote is None
                    else []
                ),
            ],
            remote_writes=(
                [
                    *(preparation_spec.writes if preparation_spec is not None else []),
                    str(controller_run_dir / "workflow" / "approved_plan.json"),
                    str(controller_run_dir / "workflow" / "controller.json"),
                    str(controller_run_dir / "workflow" / "controller.exit"),
                    str(controller_run_dir / "workflow" / "controller.exit.tmp"),
                    str(controller_run_dir / "logs" / "snakemake.log"),
                    str(controller_run_dir / "results"),
                    str(controller_run_dir / "results" / ".snakemake"),
                    *[item.destination for item in remote.staged_files],
                ]
                if remote is not None
                else []
            ),
            downloads=(
                [
                    f"{item.url} ({item.bytes} bytes, {item.sha256})"
                    for item in preparation_spec.operations
                    if item.url is not None
                ]
                if preparation_spec is not None
                else []
            ),
            network_access=(
                [
                    f"verified HTTPS download from {item.url}"
                    for item in preparation_spec.operations
                    if item.url is not None
                ]
                if preparation_spec is not None
                else []
            ),
        ),
        preparation=preparation_spec,
        blockers=blockers,
        warnings=[
            (
                "workflow-specific inputs, executable overrides, containers, outputs, and "
                "network effects are owned by the approved Snakefile and supplied config"
            ),
            *readiness.warnings,
        ],
        monitoring=MonitoringPlan(
            terminal_statuses=["completed", "failed", "canceled", "orphaned"],
            log_paths=[
                str(effects_root / "logs" / "snakemake.log"),
                str(effects_root / "results" / ".snakemake" / "log"),
            ],
            artifact_paths=[
                str(effects_root / "results" / "artifact_index.json"),
                str(resolved_config if remote is not None else config_target),
            ],
        ),
    )
    return draft.model_dump(mode="json")


def approved_execution_request(
    approved_plan: SnakemakeRunPlan,
    approved_checksum: str,
    *,
    refresh_runtime: bool = True,
) -> ExecutionRequest | dict[str, Any]:
    """Revalidate one bundled workflow and describe only its approved file effects."""
    approved = approved_plan.request
    existing = runs.find_registered_run(approved.target.target_id, approved.run_dir)
    if existing is not None:
        if existing.plan_checksum != approved_checksum:
            return _plan_error("run identity already belongs to a different approved plan")
        plan = approved_plan
    elif refresh_runtime:
        planned = plan_run(
            pipeline=approved.pipeline,
            run_dir=approved.run_dir,
            config_file=approved.config_file,
            cores=approved.cores,
            run_id=approved.run_id,
            first_run_id=approved.first_run_id,
            attempt_number=approved.attempt_number,
            workflow_version_id=approved.workflow_version_id,
            display_name=approved.display_name,
            runtime_snapshot_id=approved.runtime_snapshot_id,
            controller_candidate_id=approved.controller_candidate_id,
            preparation_spec=approved_plan.preparation,
            target_id=approved.target.target_id,
            refresh_runtime=True,
            workflow_source=approved.workflow_source,
        )
        if not planned.get("ok"):
            return planned
        plan = SnakemakeRunPlan.model_validate(planned)
    else:
        plan = approved_plan

    current_checksum = plan_checksum(plan)
    if current_checksum != approved_checksum:
        return _plan_error(
            "plan checksum does not match the current config, workflow, or runtime",
            expected_checksum=current_checksum,
            supplied_checksum=approved_checksum,
        )
    if not plan.runnable:
        return _plan_error(
            *(plan.blockers or plan.readiness.unknowns),
            status="blocked",
            readiness=plan.readiness.model_dump(mode="json"),
        )

    payload = plan.model_dump(mode="json")
    request = plan.request
    metadata_dir = run_metadata_directory(request.target.target_id, request.run_dir)
    run_dir = metadata_dir if request.remote is not None else Path(plan.effects.run_dir)
    workflow_operation = FileOperation(
        kind="copy_tree",
        destination=str(run_dir / "workflow"),
        source=request.workflow_source.root,
        source_sha256=request.workflow_sha256,
    )
    config = Path(request.config_file)
    files = [
        workflow_operation,
        *(
            [
                FileOperation(
                    kind="copy_file",
                    destination=str(run_dir / "config" / config.name),
                    source=str(config),
                    source_sha256=request.config_sha256,
                )
            ]
            if request.remote is None
            else []
        ),
        FileOperation(
            kind="write_approved_plan",
            destination=str(metadata_dir / "workflow" / "approved_plan.json"),
        ),
    ]
    return ExecutionRequest(
        binding=BINDING,
        plan_checksum=approved_checksum,
        plan=payload,
        files=files,
        inputs=(
            {request.config_file: request.config_sha256}
            if request.remote is not None and request.config_sha256 is not None
            else {}
        ),
        metadata=runs.execution_metadata(plan),
        environment=current_controller_environment(),
    )
