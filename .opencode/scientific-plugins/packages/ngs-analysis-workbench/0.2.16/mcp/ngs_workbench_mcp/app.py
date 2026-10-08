"""Expose NGS catalog and execution operations as MCP tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from ngs_workbench_daemon import client as daemon_client
from pydantic import Field

from . import (
    approved_execution,
    plan_registry,
    runs,
    runtime,
    ui,
)
from . import preparation as preparation_ops
from .readiness.models import ReadinessAssessment
from .runtime.models import RuntimeEnvironmentSnapshot
from .workflows import catalog_store as workflow_catalog
from .workflows import nextflow as nextflow_workflows
from .workflows import snakemake
from .workflows.catalog_store import WorkflowSaveSource
from .workflows.resolution import resolve_workflow
from .workflows.source import observe_source

mcp = FastMCP(
    "ngs-analysis-workbench",
    instructions=(
        "Use the journey skills for scientific routing and interpretation. For execution, inspect "
        "a registered compute target and its runtime, then compare compatible live workflow "
        "catalog entries without substituting methods. Resolve a material controller choice with "
        "request_user_input before readiness. Pass the same target, runtime snapshot, controller, "
        "inputs, and preparation through readiness and planning. Review the complete immutable "
        "plan in the inline App, then call execute_plan only with its returned name, ID, and "
        "checksum; only the host-native pause authorizes execution. Keep environment installation "
        "outside run preparation. Poll started runs to a terminal state, then inspect their "
        "actual local or SSH results with understand-ngs-results and submit the agent-authored "
        "local Markdown file with update_ngs_run_analysis_summary."
    ),
)


@mcp.resource(
    ui.PLAN_REVIEW_RESOURCE_URI,
    name="ngs-plan-review",
    title="NGS Plan Review",
    description="Review one checksum-bound plan and discover its approved run read-only.",
    mime_type=ui.APP_MIME_TYPE,
    meta=ui.resource_meta(
        fullscreen=False,
        prefers_border=True,
        widget_accessible=True,
    ),
)
def ngs_plan_review_app() -> str:
    """Return the read-only plan-review MCP App."""
    return ui.read_run_review_html()


@mcp.resource(
    ui.RUN_STATUS_RESOURCE_URI,
    name="ngs-run-receipt",
    title="NGS Run Receipt",
    description="Read-only refresh the durable receipt for an approved workflow run.",
    mime_type=ui.APP_MIME_TYPE,
    meta=ui.resource_meta(
        fullscreen=False,
        prefers_border=True,
        widget_accessible=True,
    ),
)
def ngs_run_status_app() -> str:
    """Return the read-only workflow receipt MCP App."""
    return ui.read_run_review_html()


@mcp.resource(
    ui.LEGACY_RUN_REVIEW_RESOURCE_URI,
    name="ngs-legacy-run-review",
    title="NGS Run Review",
    description="Restore the read-only review app saved in an earlier Codex task.",
    mime_type=ui.APP_MIME_TYPE,
    meta=ui.resource_meta(
        fullscreen=False,
        prefers_border=True,
        widget_accessible=True,
    ),
)
def ngs_legacy_run_review_app() -> str:
    """Keep historical task resources readable after the review URI migration."""
    return ui.read_run_review_html()


@mcp.tool(
    title="List available NGS workflows",
    description=(
        "List bundled and globally saved workflows with engine, source, and selection metadata."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def list_workflows(
    engine: Literal["nextflow", "snakemake"] | None = None,
    include_archived: bool = False,
) -> dict[str, Any]:
    """Return current discoverable workflow catalog entries."""
    return workflow_catalog.list_workflows(engine, include_archived=include_archived)


@mcp.tool(
    title="Save a selected NGS workflow",
    description=(
        "Create a reusable catalog entry only after the user has selected this workflow. "
        "Discovery candidates that the user has not selected must not be saved."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def save_workflow(
    workflow_id: str,
    name: str,
    engine: Literal["nextflow", "snakemake"],
    source: WorkflowSaveSource,
    description: str | None = None,
) -> dict[str, Any]:
    """Create one stable user-owned entry and its initial immutable version."""
    return workflow_catalog.save_workflow(workflow_id, name, engine, source, description)


@mcp.tool(
    title="Update a saved NGS workflow",
    description="Create and activate a new immutable version of a user-owned workflow.",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def update_workflow(workflow_id: str, source: WorkflowSaveSource) -> dict[str, Any]:
    """Version a user-owned workflow without overwriting history."""
    return workflow_catalog.update_workflow(workflow_id, source)


@mcp.tool(
    title="List workflow versions",
    annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def list_workflow_versions(workflow_id: str) -> dict[str, Any]:
    return workflow_catalog.list_workflow_versions(workflow_id)


@mcp.tool(
    title="Activate a workflow version",
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def activate_workflow_version(workflow_id: str, version_id: str) -> dict[str, Any]:
    return workflow_catalog.activate_workflow_version(workflow_id, version_id)


@mcp.tool(
    title="Archive a workflow",
    description="Hide a user-owned workflow from normal discovery without deleting its versions.",
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def archive_workflow(workflow_id: str) -> dict[str, Any]:
    return workflow_catalog.archive_workflow(workflow_id)


@mcp.tool(
    title="Restore an archived workflow",
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def restore_workflow(workflow_id: str) -> dict[str, Any]:
    return workflow_catalog.restore_workflow(workflow_id)


@mcp.tool(
    title="Inspect a compute target runtime",
    description=(
        "Issue a short-lived, server-authored snapshot of the selected local or SSH host "
        "architecture, Host PATH workflow controllers, task-environment commands, and Docker "
        "daemon. Local snapshots also inspect discovered managed environments; "
        "package subdirs provide OS/CPU evidence when available. This is read-only and does not "
        "install packages, download artifacts, inspect container images, activate environments, "
        "or start a run."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def get_runtime_environment(
    target_id: str = "local",
) -> RuntimeEnvironmentSnapshot:
    """Return a typed, short-lived snapshot for one registered target."""
    return runtime.inspect_runtime_environment(target_id=target_id)


@mcp.tool(
    title="Check Nextflow readiness",
    description=(
        "Compare one exact workflow request with a target-scoped runtime snapshot. Return sourced "
        "missing and unknown requirements without installing, downloading, writing, or starting."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def check_nextflow_readiness(
    workflow_id: str,
    run_dir: str,
    profile: str | None = None,
    runtime_snapshot_id: str | None = None,
    controller_candidate_id: str | None = None,
    target_id: str = "local",
) -> ReadinessAssessment:
    """Return provenance-bearing readiness for one cataloged Nextflow version."""
    execution_dir = runs.resolve_run_directory(run_dir, target_id)
    runs.check_run_directory(execution_dir, target_id)
    resolved = resolve_workflow(workflow_id, "nextflow")
    if resolved.version.source_kind == "remote":
        contract = resolved.version.execution.get("parameter_contract", "generic")
        if contract != "nf-core":
            return ReadinessAssessment.model_validate(
                nextflow_workflows.assess_readiness(
                    workflow_id,
                    runtime_snapshot_id,
                    target_id=target_id,
                    controller_candidate_id=controller_candidate_id,
                )
            )
        if profile is None or not profile.strip():
            raise ValueError("profile is required for curated nf-core workflow readiness")
        return ReadinessAssessment.model_validate(
            nextflow_workflows.assess_nfcore_readiness(
                workflow_id,
                profile.strip(),
                runtime_snapshot_id,
                target_id=target_id,
                workflow=resolved.version.remote_workflow,
                revision=resolved.version.revision,
                controller_candidate_id=controller_candidate_id,
            )
        )
    source = resolved.local_execution_source()
    if source is None:
        raise ValueError("Nextflow workflow source is unavailable")
    observe_source(source)
    return ReadinessAssessment.model_validate(
        nextflow_workflows.assess_readiness(
            workflow_id,
            runtime_snapshot_id,
            target_id=target_id,
            controller_candidate_id=controller_candidate_id,
        )
    )


@mcp.tool(
    title="Check Snakemake readiness",
    description="Check one cataloged Snakemake version and its run configuration.",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def check_snakemake_readiness(
    workflow_id: str,
    run_dir: str,
    config_file: str | None = None,
    runtime_snapshot_id: str | None = None,
    controller_candidate_id: str | None = None,
    target_id: str = "local",
    preparation: preparation_ops.PreparationRequest | None = None,
) -> ReadinessAssessment:
    """Return provenance-bearing readiness for one cataloged Snakemake version."""
    execution_dir = runs.resolve_run_directory(run_dir, target_id)
    runs.check_run_directory(execution_dir, target_id)
    resolved = resolve_workflow(workflow_id, "snakemake")
    source = resolved.local_execution_source()
    if source is None:
        raise ValueError("Snakemake workflow source is unavailable")
    snakemake.inspect_workflow(workflow_id, source)
    default_config = resolved.version.execution.get("default_config")
    if config_file is None and default_config is not None and target_id == "local":
        assert source.root is not None
        config_file = str(Path(source.root) / default_config)
    resolved_config = preparation_ops.resolve_input_path(config_file, target_id)
    if resolved_config is None:
        raise ValueError("config_file is required for Snakemake readiness")
    preparation_spec = preparation_ops.normalize_preparation(preparation, target_id=target_id)
    return ReadinessAssessment.model_validate(
        snakemake.assess_readiness(
            workflow_id,
            resolved_config,
            runtime_snapshot_id,
            (preparation_ops.generated_text(preparation_spec, resolved_config) or "")
            if preparation_ops.operation_for_path(preparation_spec, resolved_config) is not None
            else None,
            target_id=target_id,
            controller_candidate_id=controller_candidate_id,
        )
    )


@mcp.tool(
    title="List NGS runs",
    description="List durable run history across registered targets with bounded filters.",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def list_ngs_runs(
    statuses: list[str] | None = None,
    binding: str | None = None,
    pipeline: str | None = None,
    first_run_id: Annotated[
        str | None,
        Field(description=("Filter executions by the first_run_id returned in run history.")),
    ] = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Return recent registry summaries across targets."""
    return runs.list_registry_runs(
        statuses=statuses,
        binding=binding,
        pipeline=pipeline,
        first_run_id=first_run_id,
        limit=limit,
    )


@mcp.tool(
    title="List recent NGS run lineages",
    description="List recent workflow groups with a bounded workflow-attempt trace.",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def list_ngs_run_lineages(limit: int = 20) -> dict[str, Any]:
    """Return recent workflow groups without applying the limit to attempts."""
    return runs.list_registry_run_lineages(limit=limit)


@mcp.tool(
    title="Get NGS run",
    description="Read one local durable run record by its global registry id.",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def get_ngs_run(registry_run_id: str) -> dict[str, Any]:
    """Return one registry-backed run detail without observing its controller."""
    return runs.get_registry_run(registry_run_id)


@mcp.tool(
    title="Observe NGS run",
    description="Reconcile one run and read its controller log and execution evidence.",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
    meta=ui.inline_read_tool_meta(),
    structured_output=True,
)
def observe_ngs_run(registry_run_id: str) -> dict[str, Any]:
    """Return current lifecycle and bounded execution evidence for one run."""
    return runs.observe_registry_run(registry_run_id)


@mcp.tool(
    title="Update NGS run analysis summary",
    description=(
        "Save an agent-authored Markdown analysis for an existing run. Inspect relevant "
        "workflow outputs first, using SSH for a remote target, then write a local summary "
        "file. This tool saves that file; it does not inspect results or change run status."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def update_ngs_run_analysis_summary(
    registry_run_id: str,
    summary_path: Annotated[
        str,
        Field(description="Absolute path to the agent-authored local Markdown file."),
    ],
) -> dict[str, Any]:
    """Persist the summary in the run's internal record for detail and history views."""
    return daemon_client.request(
        "/run/analysis-summary", {"registry_run_id": registry_run_id, "summary_path": summary_path}
    )


@mcp.tool(
    title="Cancel an NGS run",
    description="Request cancellation of a running workflow by its durable registry ID.",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=ui.model_tool_meta(),
    structured_output=True,
)
def cancel_ngs_run(registry_run_id: str) -> dict[str, Any]:
    """Cancel one registered workflow through its existing durable lifecycle."""
    return runs.cancel_registry_run(registry_run_id)


@mcp.tool(
    title="Plan a Nextflow workflow",
    description=(
        "Create an approval-bound plan for a cataloged Nextflow workflow. "
        "Inspect its documentation, help, or nextflow_schema.json to identify required inputs "
        "and put workflow-specific parameters in params_file. Samplesheet formats, when used, "
        "are defined by the selected workflow and may be described by its linked input schema. "
        "Planning does not execute the workflow; use execute_plan for the approved plan."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
    meta=ui.plan_tool_meta(),
    structured_output=True,
)
def plan_nextflow(
    workflow_id: Annotated[
        str, Field(description="Selected Nextflow workflow catalog identifier.")
    ],
    run_dir: Annotated[
        str,
        Field(
            description="Absolute execution directory on the selected target; created after approval."
        ),
    ],
    params_file: Annotated[
        str | None,
        Field(
            description=(
                "Nextflow parameter file containing workflow-specific inputs, references, "
                "databases, and options. Use an absolute path on the selected target. "
                "nf-core workflows require JSON; user-saved generic workflows may also accept YAML."
            )
        ),
    ] = None,
    profile: Annotated[
        str | None,
        Field(description="Nextflow execution profiles, for example docker or singularity."),
    ] = None,
    display_name: str | None = None,
    runtime_snapshot_id: str | None = None,
    controller_candidate_id: str | None = None,
    target_id: str = "local",
    preparation: preparation_ops.PreparationRequest | None = None,
    first_run_id: Annotated[
        str | None,
        Field(
            description=(
                "Recovery root identifier returned in first_run_id by run history. "
                "Omit to start an independent workflow run."
            )
        ),
    ] = None,
) -> dict[str, Any]:
    """Plan one Nextflow workflow using its native parameters-file contract."""
    resolved = resolve_workflow(workflow_id, "nextflow")
    prepared = preparation_ops.normalize_preparation(preparation, target_id=target_id)

    if resolved.version.source_kind == "remote":
        contract = resolved.version.execution.get("parameter_contract", "generic")
        sample_sheet = None
        if contract == "nf-core" and params_file is not None:
            resolved_params = preparation_ops.resolve_input_path(params_file, target_id)
            content = (
                preparation_ops.inspect_input(
                    resolved_params, prepared, target_id, read_text=True
                ).get("content")
                if resolved_params is not None
                else None
            )
            if content is not None:
                try:
                    file_parameters = json.loads(content)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        "Nextflow parameters must be valid JSON when sample input discovery is required"
                    ) from exc
                if not isinstance(file_parameters, dict):
                    raise ValueError("Nextflow parameters must be a JSON object")
                file_input = file_parameters.get("input")
                if file_input is not None:
                    if not isinstance(file_input, str):
                        raise ValueError("the workflow input must be a sample-sheet path")
                    assert resolved_params is not None
                    resolved_input = preparation_ops.resolve_input_path(file_input, target_id)
                    sample_sheet = str(resolved_input) if resolved_input is not None else None
        planned = nextflow_workflows.plan_remote_run(
            pipeline=workflow_id,
            run_dir=run_dir,
            profile=profile or "",
            display_name=display_name,
            sample_sheet=sample_sheet,
            revision=resolved.version.revision,
            params_file=params_file,
            runtime_snapshot_id=runtime_snapshot_id,
            controller_candidate_id=controller_candidate_id,
            target_id=target_id,
            preparation_spec=prepared,
            workflow=resolved.version.remote_workflow,
            workflow_title=resolved.entry.name,
            workflow_version_id=resolved.version.id,
            parameter_contract=contract,
        )
        return plan_registry.register_plan(
            "nextflow",
            runs.bind_run_lineage(planned, "nextflow", first_run_id),
        )

    workflow_source = resolved.local_execution_source()
    if workflow_source is None:
        raise ValueError("Nextflow workflow source is unavailable")
    planned = nextflow_workflows.plan_run(
        workflow_id,
        run_dir,
        workflow_source,
        params_file=params_file,
        profile=profile,
        display_name=display_name,
        runtime_snapshot_id=runtime_snapshot_id,
        controller_candidate_id=controller_candidate_id,
        target_id=target_id,
        preparation_spec=prepared,
        workflow_version_id=resolved.version.id,
    )
    return plan_registry.register_plan(
        "nextflow",
        runs.bind_run_lineage(planned, "nextflow", first_run_id),
    )


@mcp.tool(
    title="Plan a Snakemake workflow",
    description=(
        "Create an approval-bound plan for a cataloged Snakemake workflow. "
        "Inspect its README, Snakefile, configuration schema, or examples to identify required "
        "inputs and put workflow-specific settings in config_file. A configuration can contain "
        "sample paths or reference a workflow-specific samplesheet. Planning does not execute "
        "the workflow; use execute_plan for the approved plan."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
    meta=ui.plan_tool_meta(),
    structured_output=True,
)
def plan_snakemake(
    workflow_id: Annotated[
        str, Field(description="Selected Snakemake workflow catalog identifier.")
    ],
    run_dir: Annotated[
        str,
        Field(
            description="Absolute execution directory on the selected target; created after approval."
        ),
    ],
    config_file: Annotated[
        str | None,
        Field(
            description=(
                "Workflow-specific configuration passed as --configfile, as an absolute path "
                "on the selected target. Use JSON for bundled workflows; custom workflows may "
                "also accept YAML. Local bundled workflows may provide a default configuration."
            )
        ),
    ] = None,
    cores: Annotated[
        int | None, Field(description="Number of cores available to Snakemake.")
    ] = None,
    display_name: str | None = None,
    runtime_snapshot_id: str | None = None,
    controller_candidate_id: str | None = None,
    target_id: str = "local",
    preparation: preparation_ops.PreparationRequest | None = None,
    first_run_id: Annotated[
        str | None,
        Field(
            description=(
                "Recovery root identifier returned in first_run_id by run history. "
                "Omit to start an independent workflow run."
            )
        ),
    ] = None,
) -> dict[str, Any]:
    """Plan one Snakemake workflow using its native configuration-file contract."""
    resolved = resolve_workflow(workflow_id, "snakemake")
    workflow_source = resolved.local_execution_source()
    if workflow_source is None:
        raise ValueError("Snakemake workflow source is unavailable")
    default_config = resolved.version.execution.get("default_config")
    if config_file is None and default_config is not None and target_id == "local":
        assert workflow_source.root is not None
        config_file = str(Path(workflow_source.root) / default_config)
    if config_file is None:
        raise ValueError("config_file is required for a Snakemake workflow")
    planned = snakemake.plan_run(
        pipeline=workflow_id,
        run_dir=run_dir,
        config_file=config_file,
        cores=4 if cores is None else cores,
        display_name=display_name,
        runtime_snapshot_id=runtime_snapshot_id,
        controller_candidate_id=controller_candidate_id,
        target_id=target_id,
        preparation_spec=preparation_ops.normalize_preparation(preparation, target_id=target_id),
        workflow_source=workflow_source,
        workflow_version_id=resolved.version.id,
        workflow_name=resolved.entry.name,
    )
    return plan_registry.register_plan(
        "snakemake",
        runs.bind_run_lineage(planned, "snakemake", first_run_id),
    )


@mcp.tool(
    title="Request approval to execute a reviewed NGS plan",
    description=(
        "Request host-native approval for one registered plan by name, ID, and checksum. "
        "Codex pauses this call for approval; only after approval does the server revalidate "
        "the plan, apply its preparation, and launch its exact workflow."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
    meta=ui.run_tool_meta(),
    structured_output=True,
)
def execute_plan(
    plan_name: str,
    plan_id: str,
    plan_checksum: str,
) -> dict[str, Any]:
    """Cross the native host approval boundary for one registered plan."""
    return approved_execution.execute_registered_plan(plan_name, plan_id, plan_checksum)
