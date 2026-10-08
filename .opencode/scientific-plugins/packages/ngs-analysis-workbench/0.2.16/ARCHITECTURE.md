# NGS Analysis Workbench Architecture

The plugin has four runtime components. Three separately initialized MCP
servers share one local daemon and one packaged Python environment. The global
App has its own process and app-only tool permissions; agent operations and
their inline views remain on their domain MCPs.

```text
ngs_app_mcp -----------+
ngs_compute_mcp -------+--> ngs_workbench_daemon
ngs_workbench_mcp -----+
```

## Component Ownership

### App MCP

`ngs_app_mcp` owns the human-facing global Runs, Workflows, and Compute shell.
Its tools are app-visible only and read bounded projections; it cannot assess
readiness, configure targets, approve execution, launch workflows, or cancel
runs. The full-screen App is process-isolated from agent tools, while inline
plan and run views stay with the Workbench tools that produce them.

### Compute MCP

`ngs_compute_mcp` owns the user-facing compute target operations:

- List the built-in local target and configured SSH-accessible targets.
- Register SSH access, a default `workspace_root`, and optional Slurm executor, partition, and account settings.
- Return observed host, executable, filesystem, and scheduler facts.

It does not define workflows, assess scientific readiness, approve execution,
launch controllers, or import the Workbench MCP.

### Workbench MCP

`ngs_workbench_mcp` owns scientific and workflow-specific behavior:

- Discover and define nf-core/Nextflow and Snakemake workflows.
- Resolve workflow requirements and compare them with target observations.
- Produce immutable plans containing exact commands, effects, and inputs.
- Revalidate a registered plan after the host grants native approval.
- Construct workflow-specific file operations and scientific run metadata.
- Present run history, bounded artifacts, and scientific results.

Planning is read-only. `execute_plan(plan_name, plan_id, plan_checksum)` is the
only execution approval surface.

### Workbench Daemon

`ngs_workbench_daemon` owns persistent infrastructure and execution:

- Maintain the single SQLite run registry, migrations, and workspace identities.
- Persist configured compute targets and their configuration identities.
- Elect one authenticated local daemon for the canonical private state root.
- Validate and consume an exact single-use native execution receipt.
- Reserve a durable run before filesystem preparation or controller launch.
- Apply explicit, checksum-bound file operations without workflow inference.
- Own local processes, SSH transport, logs, cancellation, and recovery.
- Record revision-guarded run lifecycle transitions and terminal results.

The daemon does not import an MCP, load the Workbench plan registry, select
workflow software, or special-case an analysis pipeline.

## Execution And Approval

1. Compute MCP configures or inspects a target through the daemon.
2. Workbench MCP resolves workflow requirements against observed target facts.
3. Workbench MCP registers one immutable workflow plan in private local state,
   binding an absolute execution `run_dir` on the chosen target.
4. The user authorizes its exact name, plan ID, and checksum through the
   existing native `execute_plan` boundary.
5. Workbench MCP reloads the registered plan, revalidates its inputs and
   runtime, and describes its exact files, input checksums, and run metadata.
6. Workbench MCP issues one short-lived native receipt that binds the complete
   execution request, including those workflow-specific effects.
7. The daemon validates the execution request and receipt, consumes the receipt once, reserves the run in its SQLite registry, and applies approved effects.
8. The daemon launches and monitors the local or SSH controller, persists
   transitions, and exposes status, cancellation, and bounded execution evidence.

Repeated approval of the same run identity must not launch a second controller.
An unapproved, modified, or already-consumed execution request cannot create a
workspace identity, reserve a run, write workflow files, or launch a process.

## Persistence And Recovery

There is one daemon-owned SQLite registry and one immutable Workbench plan
registry. Do not create a second run registry, a second approval surface, or a
separate scheduling framework.

SQLite is the source of truth for run identities, lifecycle revisions, and
events. Private local state holds approved plans, source staging, and submitted
analyses. The execution directory holds deployed workflow source, controller
logs, work files, and results on the selected target.

The daemon records ownership and process identity before acknowledging active
execution. MCP restarts do not stop daemon-owned runs. A replacement daemon
reconciles only runs owned by its predecessor; remote recovery must verify the
durable remote controller identity before resuming observation or cancellation.

## SSH And Slurm

SSH is a controller-host transport, not a scheduler. Slurm is an execution
backend selected on an existing target, not a target or a workflow definition.
No daemon is installed on the remote host.

Remote inspection executes a fixed, directly testable Python probe. It is read-only, keeps Nextflow offline, refuses nonlocal Docker endpoints, and observes `sbatch` and `squeue` for Slurm targets without claiming worker readiness or shared-filesystem access.

Nextflow and Snakemake support local-process execution on Linux SSH controller hosts; curated nf-core Nextflow workflows additionally support existing Slurm executors. Workflow source and controller configuration are deployed after approval. Parameter files, configurations, and samplesheets remain at their absolute target-side paths with approval-bound input checksums. Preparation runs on that target under the controller's cancellation and recovery lifecycle, before engine execution. Workflow outputs remain under `<run_dir>/results` on the target.

Runtime inspection takes `target_id`; readiness and planning take
`target_id + run_dir`. The configured `workspace_root` is a default proposal.
Readiness checks the chosen directory's writable parent, including locations
outside that root, and approved execution creates the new directory.

Plan effects and monitoring paths describe the actual execution target.
Internal run records are derived from `target_id + run_dir` under the plugin
state root. Public responses expose `target + run_dir`; history and detail use
the durable `registry_run_id`. Historical runs retain their original audit plans.

Monitoring is independent of scientific outputs: bounded controller tails and
native engine files are read directly over SSH without local persistence. Each
engine has one local/SSH parser. Shell-enabled Codex verifies the approved target
and inspects selected remote results for the final conversational interpretation,
including historical, partial, and recovered runs; it does not rerun to recover
interpretation or create a remote summary file.

## Product Boundaries

The global App and inline views are read-only projections. The global App is
hosted by `ngs_app_mcp`; inline plan and run views are hosted by
`ngs_workbench_mcp`. Neither view can authorize, execute, or cancel work
independently.

Runtime installation, reusable references, licensed inputs, machine-level
configuration, and other environment changes are separate user-approved
operations. A completed controller establishes execution success, not
scientific correctness.
