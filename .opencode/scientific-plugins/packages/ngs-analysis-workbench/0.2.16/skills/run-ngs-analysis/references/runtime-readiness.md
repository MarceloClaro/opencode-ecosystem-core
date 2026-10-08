# Runtime readiness and setup

Use this only when `run-ngs-analysis` needs controller, task-environment,
reference, or setup details.

## Observe before planning

1. Select a registered target and inspect its server-authored runtime facts.
2. Treat candidate `recommended` values as provenance ranking, not the final
   task recommendation; prefer compatible manifest- and lock-backed evidence.
3. Preserve conflicting or incomplete platform evidence as unknown. Presence
   does not prove that a binary is runnable.
4. Keep Host PATH visible with its reproducibility limitation; it may be the
   right choice for an explicit current-environment smoke.
5. Preserve the selected target, controller, and runtime snapshot through readiness and planning; execution refreshes and revalidates the runtime before launching.

Do not modify system Python. Prefer lockfile-backed Pixi, then isolated
Conda/Mamba/Micromamba, or workflow-supported containers.

## Resolve one native configuration choice

Resolve controller selection after `get_runtime_environment` and before
`check_nextflow_readiness` or `check_snakemake_readiness`:

- Consume an explicit user choice instead of asking again.
- Select one unambiguous compatible managed candidate when no material choice
  remains.
- Otherwise call `request_user_input` with one concise question and two or
  three live candidates or a legitimate setup path. Include version, source,
  and the relevant tradeoff.
- Recommend Host PATH for an explicit smoke when appropriate; normally
  recommend the strongest compatible managed provenance for a scientific run.
- If only Host PATH is currently available, offer it alongside preparing a
  managed environment. This is a pending configuration decision, not a failed
  readiness check.
- Only when `request_user_input` is unavailable or fails before rendering,
  present the same bounded options in chat.

Map the selection to its exact server-issued candidate ID and continue in the
same turn. Route environment changes to a separate proposal.

## Readiness semantics

`missing` is an observed absent requirement; `unknown` means readiness was not
established. A missing command or unreachable daemon blocks execution. A
custom nf-core profile whose effective configuration is unresolved, or a
Snakemake workflow without native deployment metadata or a workflow-owned
runtime contract, is unknown and is not ready.

For Slurm, observed `sbatch` and `squeue` establish only controller-host scheduler access. Worker software and shared-filesystem access remain unknown even when overall readiness is `ready`; disclose both before native approval. SSH inspection observes the remote Host PATH and performs bounded managed-environment discovery; incomplete discovery remains unknown.

Task environments such as Docker, Apptainer, and Conda are not workflow
backends. Runtime fit may distinguish implementations operationally but does
not make their scientific methods equivalent. After an environment change,
refresh runtime and create a new plan.
