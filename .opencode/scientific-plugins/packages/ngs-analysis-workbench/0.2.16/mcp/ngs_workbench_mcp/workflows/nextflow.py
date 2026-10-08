"""Plan and execute Nextflow workflows, including curated nf-core collections."""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from string import Template
from typing import Any

from ngs_workbench_daemon.hashing import sha256_bytes
from ngs_workbench_daemon.protocol import (
    ExecutionRequest,
    FileOperation,
    current_controller_environment,
    run_metadata_directory,
)
from pydantic import ValidationError

from .. import compute_targets, preparation, readiness_service, runs
from ..plans import (
    InputSummary,
    MonitoringPlan,
    NextflowPlanRequest,
    NextflowRunPlan,
    PreparationSpec,
    RemoteExecution,
    RemoteStagedFile,
    RunEffects,
    controller_launch_argv,
    normalize_display_name,
    plan_checksum,
)
from ..readiness.models import (
    ReadinessAssessment,
    ReadinessEvidence,
    RequirementSet,
    RuntimeRequirement,
)
from ..report.artifacts import RESULT_ROOTS
from .remote import staged_source_files
from .source import WorkflowSource, observe_source

BINDING = "nextflow"


def _error(*errors: str, **details: Any) -> dict[str, Any]:
    return {"ok": False, "errors": list(errors), **details}


def assess_readiness(
    workflow_id: str,
    runtime_snapshot_id: str | None = None,
    *,
    target_id: str = "local",
    controller_candidate_id: str | None = None,
    refresh: bool = False,
) -> ReadinessAssessment:
    """Observe the controller without assuming nf-core profiles or task environments."""
    requirements = RequirementSet(
        binding=BINDING,
        pipeline=workflow_id,
        requirements=[
            RuntimeRequirement(
                id="nextflow",
                layer="workflow_controller",
                capability="command",
                value="nextflow",
                source="workflow.engine",
                probe_mode="version",
            )
        ],
        warnings=["workflow-specific task software and references are not independently verified"],
    )
    target = compute_targets.resolve_compute_target(target_id)
    if target.controller_transport == "ssh" and target.executor != "local_process":
        requirements.blockers.append(
            "generic Nextflow does not yet support the selected remote task executor"
        )
    return readiness_service.assess(
        requirements,
        runtime_snapshot_id,
        target_id=target_id,
        controller_candidate_id=controller_candidate_id,
        refresh=refresh,
    )


def _remote_execution(
    *,
    target: compute_targets.ComputeTarget,
    source: WorkflowSource,
    run_dir: Path,
    metadata_dir: Path,
) -> RemoteExecution:
    if target.config_hash is None or target.host_access is None or target.workspace_root is None:
        raise ValueError("SSH target is missing its approved connection or workspace")
    remote_root = PurePosixPath(run_dir)
    staged = staged_source_files(
        source_root=Path(source.root),
        local_run_dir=metadata_dir,
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


def plan_run(
    workflow_id: str,
    run_dir: str,
    workflow_source: WorkflowSource,
    *,
    workflow_parameters: dict[str, str | int | float | bool] | None = None,
    params_file: str | None = None,
    profile: str | None = None,
    display_name: str | None = None,
    runtime_snapshot_id: str | None = None,
    controller_candidate_id: str | None = None,
    target_id: str = "local",
    preparation_spec: PreparationSpec | None = None,
    run_id: str | None = None,
    first_run_id: str | None = None,
    attempt_number: int | None = 1,
    workflow_version_id: str | None = None,
    refresh_runtime: bool = False,
) -> dict[str, Any]:
    """Create one read-only source-bound plan without curated nf-core conventions."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,95}", workflow_id):
        return _error("invalid workflow identifier")
    try:
        source = observe_source(workflow_source)
        target = compute_targets.resolve_compute_target(target_id)
        execution_dir = runs.resolve_run_directory(run_dir, target_id)
    except (OSError, ValueError) as exc:
        return _error(str(exc))
    if source.engine != BINDING:
        return _error("workflow engine does not match the Nextflow binding")
    if target.controller_transport == "ssh" and target.executor != "local_process":
        return _error("generic Nextflow does not yet support the selected remote task executor")
    resolved_run_id = run_id or _new_run_id(workflow_id)
    metadata_dir = run_metadata_directory(target_id, str(execution_dir))
    staging_dir = metadata_dir if target.controller_transport == "ssh" else execution_dir
    if (
        target.controller_transport != "ssh"
        and source.root is not None
        and execution_dir.is_relative_to(Path(source.root))
    ):
        return _error("workflow source must not contain its execution directory")
    parameters = dict(workflow_parameters or {})
    for name in parameters:
        if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", name):
            return _error(f"unsupported Nextflow workflow parameter: {name}")
    if profile is not None and (
        not profile.strip() or any(token.strip().startswith("-") for token in profile.split(","))
    ):
        return _error("profile tokens must be non-empty and must not start with '-'")
    try:
        resolved_params = preparation.resolve_input_path(params_file, target_id)
    except ValueError as exc:
        return _error(str(exc))
    blockers: list[str] = []
    params_digest = None
    if resolved_params is not None:
        try:
            params_digest = preparation.inspect_input(resolved_params, preparation_spec, target_id)[
                "sha256"
            ]
        except (OSError, ValueError) as exc:
            blockers.append(f"params_file could not be inspected: {exc}")
    if (
        target.controller_transport != "ssh"
        and source.root is not None
        and resolved_params is not None
        and resolved_params.is_relative_to(Path(source.root))
    ):
        return _error("run parameters must remain outside reusable workflow source")
    try:
        readiness = ReadinessAssessment.model_validate(
            assess_readiness(
                workflow_id,
                runtime_snapshot_id,
                target_id=target_id,
                controller_candidate_id=controller_candidate_id,
                refresh=refresh_runtime,
            )
        )
    except ValueError as exc:
        return _error(str(exc))
    if readiness.binding is not None and readiness.binding != BINDING:
        return _error("readiness does not match the selected workflow engine")
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
                remote = _remote_execution(
                    target=target,
                    source=source,
                    run_dir=execution_dir,
                    metadata_dir=metadata_dir,
                )
            except (OSError, ValueError) as exc:
                blockers.append(f"SSH workflow staging could not be resolved: {exc}")
    try:
        request = NextflowPlanRequest(
            pipeline=workflow_id,
            workflow_version_id=workflow_version_id,
            parameter_contract="generic",
            target=target.ref(),
            remote=remote,
            display_name=normalize_display_name(display_name, workflow_id),
            # LEGACY_CLEANUP(2026-09-07): Revalidating pre-lineage approvals passes None;
            # preserve absent fields/checksum until those saved plans are unsupported.
            first_run_id=first_run_id or (resolved_run_id if attempt_number is not None else None),
            attempt_number=attempt_number,
            workflow=source.entrypoint,
            run_dir=str(execution_dir),
            profile=profile or "",
            sample_sheet=None,
            sample_sheet_sha256=None,
            revision=None,
            params_file=str(resolved_params) if resolved_params is not None else None,
            params_file_sha256=params_digest,
            runtime_snapshot_id=readiness.snapshot_id,
            controller_candidate_id=(
                readiness.selected_controller.candidate_id
                if readiness.selected_controller is not None
                else controller_candidate_id
            ),
            workflow_source=source,
            workflow_parameters=parameters or None,
            run_id=resolved_run_id,
        )
    except ValidationError as exc:
        return _error(*[error["msg"] for error in exc.errors()])
    controller_root = execution_dir
    argv = [
        *controller_launch_argv(readiness, "nextflow"),
        "run",
        str(controller_root / "workflow" / source.entrypoint),
        "-output-dir",
        str(controller_root / "results"),
        "-work-dir",
        str(controller_root / "work"),
        "-with-trace",
        str(controller_root / "logs" / "nextflow.trace.txt"),
        *(["-profile", profile] if profile else []),
        *(
            [
                "-params-file",
                str(
                    resolved_params
                    if remote is not None
                    else execution_dir / "config" / resolved_params.name
                ),
            ]
            if resolved_params is not None
            else []
        ),
        *[
            f"--{name}={str(value).lower() if isinstance(value, bool) else value}"
            for name, value in sorted(parameters.items())
        ],
    ]
    approved_plan = metadata_dir / "workflow" / "approved_plan.json"
    local_writes = [
        *(preparation_spec.writes if preparation_spec is not None and remote is None else []),
        *runs.registry_effect_paths(),
        str(staging_dir),
        str(staging_dir / "workflow"),
        str(approved_plan),
        *(
            [str(execution_dir / "config" / resolved_params.name)]
            if resolved_params is not None and remote is None
            else []
        ),
        *(
            [
                str(execution_dir / "results"),
                str(execution_dir / "logs" / "nextflow.trace.txt"),
                str(execution_dir / "logs" / "nextflow.log"),
                str(execution_dir / "work"),
                str(execution_dir / ".nextflow"),
                str(execution_dir / ".nextflow.log"),
            ]
            if remote is None
            else []
        ),
    ]
    remote_writes = (
        [
            *(preparation_spec.writes if preparation_spec is not None else []),
            str(controller_root / "workflow" / "approved_plan.json"),
            str(controller_root / "workflow" / "controller.json"),
            str(controller_root / "workflow" / "controller.exit"),
            str(controller_root / "workflow" / "controller.exit.tmp"),
            str(controller_root / "logs" / "nextflow.log"),
            str(controller_root / "logs" / "nextflow.trace.txt"),
            *[str(controller_root / path) for path in RESULT_ROOTS],
            str(controller_root / "work"),
            str(controller_root / ".nextflow"),
            str(controller_root / ".nextflow.log"),
            *[item.destination for item in remote.staged_files],
        ]
        if remote is not None
        else []
    )
    effects_root = execution_dir
    draft = NextflowRunPlan(
        runnable=not blockers and readiness.status == "ready",
        request=request,
        command_argv=argv,
        readiness=readiness,
        input_summary=InputSummary(
            source="params_file" if resolved_params is not None else "missing",
            path=str(resolved_params) if resolved_params is not None else None,
            sha256=params_digest,
        ),
        effects=RunEffects(
            run_dir=str(effects_root),
            output_dir=str(effects_root / "results"),
            work_dir=str(effects_root / "work"),
            launch_log=str(effects_root / "logs" / "nextflow.log"),
            local_writes=local_writes,
            remote_writes=remote_writes,
            downloads=[
                f"{item.url} ({item.bytes} bytes, {item.sha256})"
                for item in preparation_spec.operations
                if item.url is not None
            ]
            if preparation_spec is not None
            else [],
            network_access=[
                f"verified HTTPS download from {item.url}"
                for item in preparation_spec.operations
                if item.url is not None
            ]
            if preparation_spec is not None
            else [],
        ),
        preparation=preparation_spec,
        blockers=blockers,
        warnings=readiness.warnings,
        monitoring=MonitoringPlan(
            terminal_statuses=["completed", "failed", "canceled", "orphaned"],
            log_paths=[str(effects_root / "logs" / "nextflow.log")],
            artifact_paths=[
                str(effects_root / "logs" / "nextflow.trace.txt"),
                str(effects_root / "results"),
            ],
        ),
    )
    return draft.model_dump(mode="json")


def approved_execution_request(
    approved_plan: NextflowRunPlan, approved_checksum: str
) -> ExecutionRequest | dict[str, Any]:
    """Replay generic source identity and describe only already-approved file effects."""
    request = approved_plan.request
    if request.workflow_source is None or request.workflow_source.engine != BINDING:
        return _error("approved Nextflow plan does not contain its exact workflow source")
    existing = runs.find_registered_run(request.target.target_id, request.run_dir)
    if existing is not None:
        if existing.plan_checksum != approved_checksum:
            return _error("run identity already belongs to a different approved plan")
        plan = approved_plan
    else:
        planned = plan_run(
            workflow_id=request.pipeline,
            run_dir=request.run_dir,
            workflow_source=request.workflow_source,
            workflow_parameters=request.workflow_parameters,
            params_file=request.params_file,
            profile=request.profile or None,
            display_name=request.display_name,
            runtime_snapshot_id=request.runtime_snapshot_id,
            controller_candidate_id=request.controller_candidate_id,
            target_id=request.target.target_id,
            preparation_spec=approved_plan.preparation,
            run_id=request.run_id,
            first_run_id=request.first_run_id,
            attempt_number=request.attempt_number,
            workflow_version_id=request.workflow_version_id,
            refresh_runtime=True,
        )
        if not planned.get("ok"):
            return planned
        plan = NextflowRunPlan.model_validate(planned)
    if plan_checksum(plan) != approved_checksum:
        return _error("plan checksum does not match the current workflow, parameters, or runtime")
    if not plan.runnable:
        return _error(*(plan.blockers or plan.readiness.unknowns), status="blocked")
    metadata_dir = run_metadata_directory(request.target.target_id, request.run_dir)
    run_dir = metadata_dir if request.remote is not None else Path(plan.effects.run_dir)
    source = request.workflow_source
    workflow = FileOperation(
        kind="copy_tree",
        destination=str(run_dir / "workflow"),
        source=source.root,
        source_sha256=source.source_sha256,
    )
    files = [workflow]
    if request.params_file is not None and request.remote is None:
        path = Path(request.params_file)
        files.append(
            FileOperation(
                kind="copy_file",
                destination=str(run_dir / "config" / path.name),
                source=str(path),
                source_sha256=request.params_file_sha256,
            )
        )
    files.append(
        FileOperation(
            kind="write_approved_plan",
            destination=str(metadata_dir / "workflow" / "approved_plan.json"),
        )
    )
    return ExecutionRequest(
        binding=BINDING,
        plan_checksum=approved_checksum,
        plan=plan.model_dump(mode="json"),
        files=files,
        inputs={request.params_file: request.params_file_sha256}
        if request.params_file is not None and request.params_file_sha256 is not None
        else {},
        metadata=runs.execution_metadata(plan),
        environment=current_controller_environment(),
    )


# Collection-specific conventions for curated nf-core workflows.
_STANDARD_PROFILE_TASK_ENVIRONMENTS = {
    "docker": "docker",
    "podman": "podman",
    "apptainer": "apptainer",
    "singularity": "singularity",
    "conda": "conda|mamba|micromamba",
}
_STANDARD_NON_ENVIRONMENT_PROFILES = {"test"}
_SLURM_CONFIGURATION = Template(
    """process {
    executor = 'slurm'

    withName: '.*' {
        $partition
        $account
    }
}
"""
)


def _remote_nextflow_configuration(
    target: compute_targets.ComputeTarget,
) -> str | None:
    if target.executor != "slurm":
        return None
    settings = target.executor_configuration
    partition = settings.get("partition")
    account = settings.get("account")
    return _SLURM_CONFIGURATION.substitute(
        partition=f"queue = {json.dumps(partition)}" if partition else "",
        account=f"clusterOptions = {json.dumps(f'--account={account}')}" if account else "",
    )


def resolve_runtime_requirements(
    pipeline: str,
    profile: str,
    *,
    workflow: str | None = None,
    revision: str | None = None,
) -> RequirementSet:
    """Describe what one exact curated nf-core workflow requires."""
    tokens = {token.strip().lower() for token in profile.split(",") if token.strip()}
    requirements = [
        RuntimeRequirement(
            id="nextflow",
            layer="workflow_controller",
            capability="command",
            value="nextflow",
            source="request.binding",
            detail="the nf-core collection executes workflows with Nextflow",
            probe_mode="version",
        )
    ]
    unknowns: list[str] = []
    warnings: list[str] = []
    selected_task_environments = [
        name for name in _STANDARD_PROFILE_TASK_ENVIRONMENTS if name in tokens
    ]
    unresolved_profile_tokens = sorted(
        tokens - _STANDARD_PROFILE_TASK_ENVIRONMENTS.keys() - _STANDARD_NON_ENVIRONMENT_PROFILES
    )
    if not selected_task_environments:
        unknowns.append(
            "effective task software environment is unresolved; the requested profile does not "
            "expose whether Nextflow tasks use containers, Conda, environment modules, or host "
            "tools"
        )
    elif len(selected_task_environments) > 1:
        unknowns.append(
            "multiple standard task-environment profiles were requested; resolve the effective "
            "Nextflow configuration to determine what is enabled: "
            f"{', '.join(selected_task_environments)}"
        )
    if unresolved_profile_tokens:
        warnings.append(
            "readiness preserves but does not independently interpret additional profile "
            f"components: {', '.join(unresolved_profile_tokens)}; confirm their effects from the "
            "selected workflow revision before approval"
        )

    for task_environment in selected_task_environments:
        requirements.append(
            RuntimeRequirement(
                id=f"{task_environment}-command",
                layer="task_environment",
                capability="command_group" if task_environment == "conda" else "command",
                value=_STANDARD_PROFILE_TASK_ENVIRONMENTS[task_environment],
                source="request.profile",
                detail=(
                    f"the standard {task_environment} profile enables {task_environment} "
                    "for task software"
                ),
                probe_mode="version",
            )
        )
        if task_environment == "docker":
            requirements.append(
                RuntimeRequirement(
                    id="docker-daemon",
                    layer="task_environment",
                    capability="daemon",
                    value="docker",
                    source="request.profile",
                )
            )

    return RequirementSet(
        binding="nextflow",
        pipeline=pipeline,
        requirements=requirements,
        evidence=[
            ReadinessEvidence(
                kind="requested_profile",
                source="request.profile",
                detail=profile,
            ),
            ReadinessEvidence(
                kind="workflow_binding",
                source=workflow or pipeline,
                detail=f"revision {revision}" if revision else "revision is not pinned",
            ),
        ],
        unknowns=unknowns,
        warnings=warnings,
    )


def assess_nfcore_readiness(
    pipeline: str,
    profile: str,
    runtime_snapshot_id: str | None = None,
    *,
    target_id: str = "local",
    workflow: str | None = None,
    revision: str | None = None,
    controller_candidate_id: str | None = None,
    refresh: bool = False,
) -> ReadinessAssessment:
    """Compose nf-core requirements with generic runtime observation and evaluation."""
    requirement_set = resolve_runtime_requirements(
        pipeline,
        profile,
        workflow=workflow,
        revision=revision,
    )
    return readiness_service.assess(
        requirement_set,
        runtime_snapshot_id,
        target_id=target_id,
        controller_candidate_id=controller_candidate_id,
        refresh=refresh,
    )


def _remote_content(destination: PurePosixPath, content: str) -> RemoteStagedFile:
    encoded = content.encode("utf-8")
    return RemoteStagedFile(
        destination=destination.as_posix(),
        sha256=sha256_bytes(encoded),
        bytes=len(encoded),
        content=content,
    )


def _new_run_id(pipeline: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    pipeline_slug = pipeline.replace("_", "-")[:62]
    return f"nextflow-{pipeline_slug}-{stamp}-{uuid.uuid4().hex[:8]}"


def _input_summary(
    sample_sheet: Path | None,
    sample_sheet_sha256: str | None,
    *,
    test_profile: bool,
) -> InputSummary:
    if sample_sheet is None:
        return InputSummary(source="workflow_test_profile" if test_profile else "missing")
    return InputSummary(
        source="sample_sheet",
        path=str(sample_sheet),
        sha256=sample_sheet_sha256,
    )


def build_nextflow_argv(
    *,
    nextflow_argv_prefix: list[str] | None = None,
    workflow: str,
    sample_sheet: Path | PurePosixPath | None,
    run_dir: Path | PurePosixPath,
    profile: str,
    revision: str | None,
    params_file: Path | PurePosixPath | None,
    parameter_contract: str,
) -> list[str]:
    """Build the literal argv used to start Nextflow."""
    generated_params = run_dir / "workflow" / "params.generated.json"
    argv = [
        *(nextflow_argv_prefix or ["nextflow"]),
        "run",
        workflow,
    ]
    if params_file is not None or sample_sheet is not None:
        argv.extend(["-params-file", str(params_file or generated_params)])
    argv.extend(
        [
            "-work-dir",
            str(run_dir / "work"),
            "-with-report",
            str(run_dir / "workflow" / "nextflow_report.html"),
            "-with-timeline",
            str(run_dir / "workflow" / "timeline.html"),
            "-with-trace",
            str(run_dir / "workflow" / "trace.txt"),
            "-with-dag",
            str(run_dir / "workflow" / "dag.html"),
        ]
    )
    if revision:
        argv.extend(["-r", revision])
    if profile:
        argv.extend(["-profile", profile])
    if parameter_contract == "nf-core" and params_file and sample_sheet:
        argv.extend(
            [
                "--input",
                str(sample_sheet),
                "--outdir",
                str(run_dir / "results"),
            ]
        )
    elif parameter_contract == "nf-core" and sample_sheet is None:
        argv.extend(["--outdir", str(run_dir / "results")])
    elif parameter_contract == "generic":
        argv.extend(["-output-dir", str(run_dir / "results")])
    return argv


def _plan_error(*errors: str, **details: Any) -> dict[str, Any]:
    return {"ok": False, "errors": list(errors), **details}


def plan_remote_run(
    pipeline: str,
    run_dir: str,
    profile: str,
    display_name: str | None = None,
    sample_sheet: str | None = None,
    revision: str | None = None,
    params_file: str | None = None,
    run_id: str | None = None,
    first_run_id: str | None = None,
    attempt_number: int | None = 1,
    runtime_snapshot_id: str | None = None,
    controller_candidate_id: str | None = None,
    preparation_spec: PreparationSpec | None = None,
    *,
    workflow: str | None = None,
    workflow_title: str | None = None,
    workflow_version_id: str | None = None,
    parameter_contract: str = "nf-core",
    target_id: str = "local",
    refresh_runtime: bool = False,
) -> dict[str, Any]:
    """Build a typed engine-resolved remote Nextflow plan."""
    workflow_title = workflow_title or pipeline
    if workflow is None:
        return _plan_error(f"workflow source is unavailable: {pipeline}")
    try:
        target = compute_targets.resolve_compute_target(target_id)
        execution_dir = runs.resolve_run_directory(run_dir, target_id)
    except ValueError as exc:
        return _plan_error(str(exc))
    profile_tokens_list = [token.strip() for token in profile.split(",") if token.strip()]
    profile = ",".join(profile_tokens_list)
    revision = revision.strip() if revision else None
    if (parameter_contract == "nf-core" and not profile) or any(
        token.startswith("-") for token in profile_tokens_list
    ):
        return _plan_error("profile tokens must be non-empty and must not start with '-'")
    if revision is not None and revision.startswith("-"):
        return _plan_error("revision must not start with '-'")

    try:
        resolved_sample_sheet = preparation.resolve_input_path(sample_sheet, target_id)
        resolved_params_file = preparation.resolve_input_path(params_file, target_id)
    except ValueError as exc:
        return _plan_error(str(exc))
    blockers = []
    profile_tokens = {token.strip().lower() for token in profile.split(",")}
    if (
        parameter_contract == "nf-core"
        and resolved_sample_sheet is None
        and "test" not in profile_tokens
    ):
        blockers.append("sample_sheet is required unless profile includes 'test'")
    input_hashes: dict[Path, str] = {}
    for path in (resolved_sample_sheet, resolved_params_file):
        if path is not None:
            try:
                input_hashes[path] = preparation.inspect_input(path, preparation_spec, target_id)[
                    "sha256"
                ]
            except (OSError, ValueError) as exc:
                blockers.append(f"input could not be inspected: {path}: {exc}")
    sample_sheet_sha256 = (
        input_hashes.get(resolved_sample_sheet) if resolved_sample_sheet is not None else None
    )
    params_file_sha256 = (
        input_hashes.get(resolved_params_file) if resolved_params_file is not None else None
    )

    try:
        readiness_result = (
            assess_nfcore_readiness(
                pipeline,
                profile,
                runtime_snapshot_id,
                target_id=target.target_id,
                workflow=workflow,
                revision=revision,
                controller_candidate_id=controller_candidate_id,
                refresh=refresh_runtime,
            )
            if parameter_contract == "nf-core"
            else assess_readiness(
                pipeline,
                runtime_snapshot_id,
                target_id=target.target_id,
                controller_candidate_id=controller_candidate_id,
                refresh=refresh_runtime,
            )
        )
        readiness = ReadinessAssessment.model_validate(readiness_result)
    except ValueError as exc:
        return _plan_error(str(exc))
    if readiness.binding is not None and readiness.binding != BINDING:
        return _plan_error("readiness does not match the selected workflow engine")
    readiness = readiness.model_copy(update={"binding": BINDING})
    blockers.extend(readiness.blockers)
    blockers.extend(f"readiness unresolved: {item}" for item in readiness.unknowns)
    resolved_run_id = run_id or _new_run_id(pipeline)
    metadata_dir = run_metadata_directory(target_id, str(execution_dir))
    try:
        runs.check_run_directory(execution_dir, target_id)
    except (OSError, ValueError) as exc:
        blockers.append(str(exc))

    remote = None
    controller_run_dir: Path | PurePosixPath = execution_dir
    if target.controller_transport == "ssh":
        if readiness.host is None or readiness.host.os.lower() != "linux":
            blockers.append("SSH workflow execution requires an observed Linux controller host")
        if (
            target.config_hash is None
            or target.host_access is None
            or target.workspace_root is None
        ):
            return _plan_error("SSH target is missing its approved connection or workspace")
        remote_run_dir = PurePosixPath(execution_dir)
        staged_files = []
        if resolved_params_file is None and resolved_sample_sheet is not None:
            staged_files.append(
                _remote_content(
                    remote_run_dir / "workflow" / "params.generated.json",
                    json.dumps(
                        {
                            "input": str(resolved_sample_sheet),
                            "outdir": str(remote_run_dir / "results"),
                        }
                    )
                    + "\n",
                )
            )
        if configuration := _remote_nextflow_configuration(target):
            staged_files.append(
                _remote_content(
                    remote_run_dir / "workflow" / "nextflow.config",
                    configuration,
                )
            )
        remote = RemoteExecution(
            config_hash=target.config_hash,
            host_access=target.host_access,
            workspace_root=target.workspace_root,
            run_dir=remote_run_dir.as_posix(),
            executor=target.executor,
            executor_configuration=target.executor_configuration,
            staged_files=staged_files,
        )
        controller_run_dir = remote_run_dir

    controller_argv = controller_launch_argv(readiness, "nextflow")
    if remote is not None and remote.executor == "slurm":
        controller_argv.extend(["-c", str(controller_run_dir / "workflow" / "nextflow.config")])
    argv = build_nextflow_argv(
        nextflow_argv_prefix=controller_argv,
        workflow=workflow,
        sample_sheet=resolved_sample_sheet,
        run_dir=controller_run_dir,
        profile=profile,
        revision=revision,
        params_file=resolved_params_file,
        parameter_contract=parameter_contract,
    )
    local_writes = [
        *(preparation_spec.writes if preparation_spec is not None and remote is None else []),
        *runs.registry_effect_paths(),
        str(metadata_dir / "workflow" / "approved_plan.json"),
    ]
    if remote is None:
        local_writes.extend(
            [
                str(execution_dir / "logs" / "nextflow.log"),
                str(execution_dir / "results"),
                str(execution_dir / "work"),
            ]
        )
    if remote is None and resolved_params_file is None and resolved_sample_sheet is not None:
        local_writes.append(str(execution_dir / "workflow" / "params.generated.json"))
    warnings = list(readiness.warnings)
    if not revision:
        warnings.append("no nf-core revision is pinned")
    try:
        request = NextflowPlanRequest(
            pipeline=pipeline,
            workflow_version_id=workflow_version_id,
            parameter_contract=parameter_contract,
            target=target.ref(),
            remote=remote,
            display_name=normalize_display_name(display_name, workflow_title),
            # LEGACY_CLEANUP(2026-09-07): Revalidating pre-lineage approvals passes None;
            # preserve absent fields/checksum until those saved plans are unsupported.
            first_run_id=first_run_id or (resolved_run_id if attempt_number is not None else None),
            attempt_number=attempt_number,
            workflow=workflow,
            run_dir=str(execution_dir),
            profile=profile,
            sample_sheet=str(resolved_sample_sheet) if resolved_sample_sheet else None,
            sample_sheet_sha256=sample_sheet_sha256,
            revision=revision,
            params_file=str(resolved_params_file) if resolved_params_file else None,
            params_file_sha256=params_file_sha256,
            runtime_snapshot_id=readiness.snapshot_id,
            controller_candidate_id=(
                readiness.selected_controller.candidate_id
                if readiness.selected_controller is not None
                else controller_candidate_id
            ),
            run_id=resolved_run_id,
        )
    except ValidationError as exc:
        return _plan_error(*[error["msg"] for error in exc.errors()])

    downloads = [
        f"workflow source for {workflow}"
        + (f" at revision {revision}" if revision else " at its default revision"),
    ]
    network_access = ["Nextflow workflow source resolution"]
    downloads.append("container images referenced by the workflow if absent from the local cache")
    network_access.append("container registry access for uncached images")
    if parameter_contract == "nf-core" and "test" in profile_tokens:
        downloads.append(
            "test-profile inputs referenced by the workflow if absent from the local cache"
        )
        network_access.append("remote test-data access declared by the workflow")
    if preparation_spec is not None:
        downloads.extend(
            f"{item.url} ({item.bytes} bytes, {item.sha256})"
            for item in preparation_spec.operations
            if item.url is not None
        )
        network_access.extend(
            f"verified HTTPS download from {item.url}"
            for item in preparation_spec.operations
            if item.url is not None
        )

    effects_root = execution_dir
    draft = NextflowRunPlan(
        runnable=not blockers and readiness.status == "ready",
        request=request,
        command_argv=argv,
        readiness=readiness,
        input_summary=_input_summary(
            resolved_sample_sheet,
            sample_sheet_sha256,
            test_profile="test" in profile_tokens,
        ),
        effects=RunEffects(
            run_dir=str(effects_root),
            output_dir=str(effects_root / "results"),
            work_dir=str(effects_root / "work"),
            launch_log=str(effects_root / "logs" / "nextflow.log"),
            local_writes=local_writes,
            remote_writes=(
                [
                    *(preparation_spec.writes if preparation_spec is not None else []),
                    str(controller_run_dir / "workflow" / "approved_plan.json"),
                    str(controller_run_dir / "workflow" / "nextflow_report.html"),
                    str(controller_run_dir / "workflow" / "timeline.html"),
                    str(controller_run_dir / "workflow" / "trace.txt"),
                    str(controller_run_dir / "workflow" / "dag.html"),
                    str(controller_run_dir / "workflow" / "controller.json"),
                    str(controller_run_dir / "workflow" / "controller.exit"),
                    str(controller_run_dir / "workflow" / "controller.exit.tmp"),
                    str(controller_run_dir / "logs" / "nextflow.log"),
                    str(controller_run_dir / "results"),
                    str(controller_run_dir / "work"),
                    *[item.destination for item in remote.staged_files],
                ]
                if remote is not None
                else []
            ),
            downloads=downloads,
            network_access=network_access,
        ),
        preparation=preparation_spec,
        blockers=blockers,
        warnings=warnings,
        monitoring=MonitoringPlan(
            terminal_statuses=[
                "completed",
                "failed",
                "canceled",
                "orphaned",
            ],
            log_paths=[str(effects_root / "logs" / "nextflow.log")],
            artifact_paths=[
                str(effects_root / "results"),
                str(effects_root / "workflow" / "nextflow_report.html"),
                str(effects_root / "workflow" / "timeline.html"),
                str(effects_root / "workflow" / "trace.txt"),
                str(effects_root / "workflow" / "dag.html"),
            ],
        ),
    )
    return draft.model_dump(mode="json")


def approved_nfcore_execution_request(
    approved_plan: NextflowRunPlan,
    approved_checksum: str,
    *,
    refresh_runtime: bool = True,
) -> ExecutionRequest | dict[str, Any]:
    """Revalidate one immutable plan and describe its approved daemon-owned effects."""
    approved = approved_plan.request
    existing = runs.find_registered_run(approved.target.target_id, approved.run_dir)
    if existing is not None:
        if existing.plan_checksum != approved_checksum:
            return _plan_error("run identity already belongs to a different approved plan")
        plan = approved_plan
    elif refresh_runtime:
        planned = plan_remote_run(
            pipeline=approved.pipeline,
            run_dir=approved.run_dir,
            profile=approved.profile,
            display_name=approved.display_name,
            sample_sheet=approved.sample_sheet,
            revision=approved.revision,
            params_file=approved.params_file,
            run_id=approved.run_id,
            first_run_id=approved.first_run_id,
            attempt_number=approved.attempt_number,
            runtime_snapshot_id=approved.runtime_snapshot_id,
            controller_candidate_id=approved.controller_candidate_id,
            preparation_spec=approved_plan.preparation,
            workflow=approved.workflow,
            workflow_title=approved.display_name,
            workflow_version_id=approved.workflow_version_id,
            parameter_contract=approved.parameter_contract or "nf-core",
            target_id=approved.target.target_id,
            refresh_runtime=True,
        )
        if not planned.get("ok"):
            return planned
        plan = NextflowRunPlan.model_validate(planned)
    else:
        plan = approved_plan

    current_checksum = plan_checksum(plan)
    if current_checksum != approved_checksum:
        return _plan_error(
            "plan checksum does not match the current inputs or runtime",
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
    workflow_dir = run_dir / "workflow"
    files = []
    if request.remote is None and request.params_file is None and request.sample_sheet is not None:
        files.append(
            FileOperation(
                kind="write_json",
                destination=str(workflow_dir / "params.generated.json"),
                content={"input": request.sample_sheet, "outdir": plan.effects.output_dir},
            )
        )
    files.append(
        FileOperation(
            kind="write_approved_plan",
            destination=str(metadata_dir / "workflow" / "approved_plan.json"),
        )
    )
    response = {"runtime_snapshot_id": request.runtime_snapshot_id}
    return ExecutionRequest(
        binding="nextflow",
        plan_checksum=approved_checksum,
        plan=payload,
        files=files,
        inputs={
            path: checksum
            for path, checksum in (
                (request.sample_sheet, request.sample_sheet_sha256),
                (request.params_file, request.params_file_sha256),
            )
            if path is not None and checksum is not None
        },
        metadata={"response": response, **runs.execution_metadata(plan)},
        environment=current_controller_environment(),
    )
