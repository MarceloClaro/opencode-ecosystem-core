# NGS Compute MCP

`ngs-compute` configures and inspects existing compute targets through the shared local Workbench daemon. It does not define workflows, assess scientific readiness, install software, approve execution, or start workflow controllers.

## Tools

- `list_compute_targets()` returns the built-in `local` target and configured SSH targets.
- `configure_ssh_target(target_id, title, ssh_alias, workspace_root, executor, partition, account)` registers an existing SSH host and optional scheduler settings. The default executor is `local_process`; `partition` and `account` are optional.
- `inspect_compute_target(target_id, executable_paths)` observes existing host, executable, filesystem, and scheduler facts without installing or modifying remote software. `executable_paths` is optional.

## SSH Targets

Use an existing SSH alias and an absolute remote workspace path. Remote workflow execution requires an observed Linux controller host.

```json
{
  "target_id": "lab",
  "title": "Lab compute host",
  "ssh_alias": "lab-host",
  "workspace_root": "/shared/ngs",
  "executor": "local_process"
}
```

The local daemon persists nonsecret SSH references and target configuration. No daemon is installed on the remote host. SSH access and required workflow software must already exist.

## Slurm Targets

Set `executor="slurm"` when configuring an SSH target. Add `partition` or `account` only when the existing cluster requires them. Slurm is a scheduler on the selected SSH target, not a separate target or workflow engine.

Inspection observes `sbatch`, `squeue`, and bounded managed environments on the controller host. It does not verify worker software or shared-filesystem access; report those facts as unknown even if the scheduler control plane is ready.

## Workflow Handoff

Pass the configured `target_id` to the Workbench MCP's `get_runtime_environment`, engine-specific `check_nextflow_readiness` or `check_snakemake_readiness`, and `plan_nextflow` or `plan_snakemake` tools. Nextflow and Snakemake support Linux SSH targets using the local-process executor; curated nf-core Nextflow workflows additionally support existing Slurm executors. Workflow approval stays with the Workbench `execute_plan` tool and its host-native approval prompt.

## Development

Start the compute MCP from `mcp/`:

```bash
PYTHONPATH=. uv run --no-project --isolated \
  --with-requirements ./requirements.txt \
  python -m ngs_compute_mcp
```
