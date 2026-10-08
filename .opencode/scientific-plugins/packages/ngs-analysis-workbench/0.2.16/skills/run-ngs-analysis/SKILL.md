---
name: run-ngs-analysis
description: Make an NGS analysis executable through live workflow discovery, readiness, immutable compound planning, native execution approval, monitoring, cancellation, and recovery. Use to bind an implementation, prepare or execute a plan, or operate a durable run.
---

# Run NGS Analysis

Read [AnalysisContext](../../references/analysis-context.md). Bind an existing
scientific design to one reviewable execution without changing its method or
claim boundary. If no analysis plan exists, route scientific work to
[design-ngs-analysis](../design-ngs-analysis/SKILL.md); allow an explicitly
limited engine smoke, reproduction, or operational diagnostic without one.

## Discover and bind

Treat callable tools and live catalogs as authoritative:

1. List targets with `list_compute_targets`. If the user requests an existing unregistered SSH or Slurm host, call `configure_ssh_target` with its `target_id`, `title`, SSH alias, default `workspace_root`, executor, and optional partition/account.
2. Inspect the selected target with `inspect_compute_target` when applicable, then call `get_runtime_environment(target_id)`.
3. List current workflows from the live catalog. Also consider an explicit
   user-provided or agent-created local source and external workflow candidates.
4. If no suitable catalog entry exists, use available web, GitHub, internal
   repository, or existing filesystem capabilities to locate native Nextflow or
   Snakemake workflows. Do not request a Workbench backend search API.
5. Inspect each serious candidate's README, native entrypoint, imported modules, environment and
   configuration declarations, license, assay, endpoint, and revision before
   proposing it. A description or repository popularity is
   not evidence that its method, outputs, or runtime are suitable.
6. Keep Found, Suitable, and Selected distinct. Present the suitable candidate
   and its exact version to the user when they have not already selected one.
   Rejected or merely discovered candidates must not be saved or downloaded.
7. After the user selects a candidate, call `save_workflow` once if it is not
   already cataloged. Save an online Nextflow workflow by its native locator and
   immutable revision; do not download it merely to catalog it. Save a local
   workflow by its absolute root and native entrypoint, keeping samples,
   credentials, caches, and outputs outside that root. If the user supplied an
   exact workflow and version and explicitly asked to use it, that is already a
   selection. Use `update_workflow` only when the user intends to version an
   existing user-owned entry.
8. Compare method and scope separately from engine, runtime fit, and target.
   Both engines support local and Linux SSH local-process targets; curated
   nf-core Nextflow also supports existing Slurm executors.
9. Follow [runtime readiness](references/runtime-readiness.md) for controller
   selection and missing or unknown requirements.

Repository inspection and catalog persistence do not approve workflow
execution. Never execute repository scripts, installation commands, workflow
dry-runs, or setup hooks during discovery.

For bundled Snakemake, read `<workflow_root>/config/README.md` before building
the config. For a Nextflow workflow from the nf-core collection, read
[profile selection](references/nfcore-profile-selection.md) after selecting the
binding. Read [runtime readiness](references/runtime-readiness.md) when checking
controllers, setup, or references.

## Check and plan

Choose one new absolute `run_dir` on the selected `target_id`. Use the target's
`workspace_root`, when present, as a default location for proposing a run
subdirectory. An explicit writable location under `/data`, `/projects`, or
`/scratch` is equally valid. Readiness checks the chosen path; leave creation
to approved execution.

Call `check_nextflow_readiness` or `check_snakemake_readiness` with the selected
`workflow_id`, `target_id`, and `run_dir`, then call the matching planner with
the same catalog entry, location, inputs, runtime snapshot, controller
candidate, and typed preparation. Put Nextflow parameters in `params_file` and Snakemake settings in
`config_file`. These files and samplesheets use absolute paths on the selected
target, either already present or produced by approved preparation. The plan
binds their file identities. Preserve the workflow's native parameter and
samplesheet semantics, including scalar labels; filesystem inputs referenced
within them must be valid on that target.

Keep `unknown` distinct from `missing`; disclose Slurm worker and
shared-filesystem uncertainty even when scheduler control-plane readiness is
`ready`.

If readiness or planning is blocked, synthesize the scientific objective,
observed blocker, unexecuted workflow, absent artifacts, unsupported scientific
claims, and next safe decision. Follow
[understand-ngs-results](../understand-ngs-results/SKILL.md) using only the
available readiness/design evidence. If no run exists, do not create a registry
entry or run directory merely to persist a summary.

Review the returned plan in the inline App. Add its `plan_name`, `plan_id`, and
`plan_checksum` as an `execution_plan` artifact without replacing the
scientific plan.

## Preserve authorization boundaries

Put verified downloads and generated JSON, CSV, or text files in the typed
`preparation` field with an absolute `destination_dir` on the selected target.
Approved preparation creates them directly there before engine execution.
Keep installation, licensed inputs, large reusable
references, downloads without exact sizes and SHA-256 digests, and machine-level
changes outside the run plan.

The plan App is passive. Call `execute_plan` only with its exact returned identity; the host-native pause is the sole authorization for preparation and execution.
When the returned plan is runnable and the original request includes running, executing, or generating results subject only to native approval, call `execute_plan` in the same turn; this requests approval and does not bypass it.
Stop after planning only when the user explicitly requested plan-only review or a material blocker or unresolved decision remains.
Never ask for execution approval in prose, structured choices, or `request_user_input`; those do not authorize execution.
After denial, stop until a new user request.

## Monitor and hand off

After start, preserve `registry_run_id`, `target`, and `run_dir`. Call
`get_ngs_run` once for durable context, then poll `observe_ngs_run`; an
initially unavailable observation must not trigger another start. Add a `run_receipt`
artifact. Cancel only when requested, using `cancel_ngs_run`. MCP reconnection
preserves the run identity. Replacing the local daemon orphans its active local
runs but can recover verified remote SSH controllers.

Stop observation polling when the run reaches a terminal state, then call
`get_ngs_run` once more for its final durable state. The workflow is
finished, but the agent's handoff is not: inspect results, write the analysis,
and submit it as described below before completing the task, or report the exact
inspection/submission blocker. Do not wait for a summary file to appear.

For every completed, partially executed, failed, canceled, or orphaned run,
always follow
[understand-ngs-results](../understand-ngs-results/SKILL.md) with the original
scientific question, experimental goal and context, decision, scientific model,
analysis plan, IDs, paths, result projection when present, observed process
attempts, failure reason, bounded logs, and provenance, even when the user did
not separately ask for interpretation. For SSH, use the verified direct-SSH
handoff in that skill: results remain under `<run_dir>/results` on `target`,
while Workbench supplies controller logs and structured execution evidence.
Apply this handoff to historical runs and recovered controllers too; never
rerun merely to recover interpretation. Distinguish partial outputs from completed results,
and return the
model-authored synthesis of scientific context, true lifecycle, observed
findings, unsupported claims, blockers, and next step. After inspecting actual
results, write the agent-authored review to a local Markdown file for either
target. Call `update_ngs_run_analysis_summary(registry_run_id,
summary_path)` with that file's absolute local path and confirm it was saved.
Return the same synthesis in the conversation. For SSH, never write the summary
remotely or copy the result tree locally. A submission failure does not change
the workflow's terminal status and must not trigger another execution.
A status, report link, or list of files alone is not the final answer. Select
maintained scientific guidance from independently observed assay, input state,
endpoint, method, and actual output semantics; custom identifiers do not block
an otherwise applicable policy. If these facts cannot establish a maintained
policy, report only operational evidence and explicit scientific limitations.

Return the operational outcome, blockers, plan and approval state, run
lifecycle, and next permitted action. Runnable or completed does not mean
scientifically valid.
