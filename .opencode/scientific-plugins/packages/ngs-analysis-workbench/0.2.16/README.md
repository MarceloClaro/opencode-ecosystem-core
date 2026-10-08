# NGS Analysis Workbench

The NGS Analysis Workbench supports three focused lanes:

- FASTQ QC, with optional trimming
- bulk RNA-seq
- single-cell or single-nucleus RNA-seq

The live nf-core catalog also includes other executable assays, without adding curated scientific design or interpretation guidance for those analyses.

It separates scientific intent from execution. A requested outcome such as bulk RNA-seq quantification is not the same decision as selecting `nf-core/rnaseq`, a bundled Snakemake workflow, or a local or SSH compute target.

## User journey

Five active skills cover the non-linear analysis journey:

| Skill | Responsibility |
| --- | --- |
| `ngs-analysis-workbench` | Route broad, ambiguous, resume, and cross-journey requests |
| `understand-ngs-data` | Establish an evidence-backed starting point |
| `design-ngs-analysis` | Define the scientific model, evidence contract, and validity gates |
| `run-ngs-analysis` | Discover implementations, check readiness, plan, approve, run, monitor, and recover |
| `understand-ngs-results` | Connect completed file-backed evidence to the original objective |

The skills share a partial `AnalysisContext` containing the objective,
materials, scientific model, sourced evidence, typed artifacts, open questions,
and the next user-owned decision. It is an agent handoff contract, not a user
form, linear state machine, durable store, or authorization record.

Scientific references are loaded only for the relevant assay and decision.
Callable tools and live catalogs remain the executable source of truth; the
plugin does not expose one skill per workflow.

## Execution contract

The MCP server supports two workflow engines: Nextflow and Snakemake. Workflows
can come from a curated collection such as nf-core, a selected online source,
or a local directory copied into the workflow catalog.

Catalog presence means an adapter can construct a plan. It does not establish
runtime readiness, scientific equivalence, or support for biological
interpretation.

Every execution uses the same boundary:

1. Inspect a registered compute target and its runtime.
2. Compare scientifically compatible live workflow bindings.
3. Choose an absolute `run_dir` on that target, resolve any material controller
   choice, and check readiness for the exact request.
4. Register one immutable plan containing normalized inputs, optional typed
   preparation, exact argv, effects, blockers, monitoring, and one canonical
   checksum.
5. Review the plan in the passive inline App.
6. Call `execute_plan(plan_name, plan_id, plan_checksum)`; only the Codex
   host's native pause can authorize that call.
7. Revalidate, apply the checksum-bound preparation, start once, and poll the
   durable run to a terminal state.

Environment installation, licensed inputs, large reusable references,
unsupported hosts, and machine-level changes remain outside the run plan.
Engine completion proves execution, not scientific validity.

## Compute targets

The separate [compute MCP](./mcp/ngs_compute_mcp/README.md) configures and inspects local and SSH targets. Runtime inspection takes `target_id`; readiness and planning take `target_id + run_dir`. The target's `workspace_root` supplies a default proposal; a run may use another writable absolute location. Approved execution creates the chosen directory.

Inputs, parameter files, configurations, and samplesheets use absolute paths on the selected target. Preparation creates approved input files directly there; reusable local workflow source is staged from its immutable catalog version. Both engines support Linux SSH local-process targets; curated nf-core Nextflow also supports an existing Slurm executor.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for runtime layers, persistence,
component ownership, plan identity, and failure behavior.

## Apps and durable state

The plugin ships two self-contained React surfaces:

- The full Workbench is hosted by the separate `ngs-app` MCP and provides an
  app-only, read-only view of runs, workflows, and configured compute targets.
- The compact inline App renders passive plan review and live run receipts.

Agent-visible planning and execution tools remain on `ngs-analysis-workbench`;
compute registration and inspection remain on `ngs-compute`. Their inline Apps
remain attached to the agent tools that produce them.

Neither App can authorize, execute, or cancel work. The agent requests
execution; the Codex host authorizes the exact tool call; the MCP server
revalidates it and submits the approved work to the local Workbench daemon.

SQLite under the local plugin state root owns run lifecycle and history. Public `target + run_dir` identifies execution, with scientific outputs under `<run_dir>/results`. Approval records, source staging, and submitted analyses live in internal local state.

Workbench provides controller log tails and structured execution evidence for local and SSH runs. Codex inspects workflow outputs, writes a local Markdown analysis, and submits it with `update_ngs_run_analysis_summary(registry_run_id, summary_path)`. The daemon saves the summary in the run record; detail and history display it on refresh or reopen.

One local daemon owns workflow execution independently of individual MCP servers, so a replacement server can continue monitoring or cancel a run. If the daemon exits, its successor stops only explicitly owned local process groups and marks those runs as orphaned. Running SSH controllers can be recovered after their durable remote identity is verified.

## Build and install from source

`codex plugin add` installs an already-built plugin; it does not generate MCP
App assets. From the plugin root:

```bash
npm ci
npm run build
test -s mcp/mcp-app.html
test -s mcp/mcp-inline.html
```

If the same development version is already installed, remove and re-add that
exact marketplace entry so Codex rebuilds its versioned cache:

```bash
codex plugin remove ngs-analysis-workbench@<marketplace> --json
codex plugin add ngs-analysis-workbench@<marketplace> --json
```

Verify the installed cache, start all three cached MCP servers using
`.mcp.json`, and require non-empty `resources/read` responses for the global
`ui://ngs-app/main.html` resource and the inline
`ui://ngs-analysis-workbench/plan-review.html` resource. Importing a Python
package or listing tools alone does not prove that the bundled Apps are
loadable.

The generated `mcp/mcp-app.html` and `mcp/mcp-inline.html` files are
gitignored. Published plugin payloads must include both. Open a new Codex task
after replacement; fully quit and reopen Codex if the desktop still retains an
older plugin snapshot.

Before releasing, run `npm run check:release` from the canonical monorepo
source. It rebuilds both Apps in memory and verifies their SHA-256 hashes
against `manage/blob_data.hashes`, so passing source tests cannot conceal a
stale published UI. If it fails, rebuild and upload the App assets using
Applied blob data, then rerun the check. A release version bump alone does not
refresh the compiled Apps.

The maintained-plugins CI runs this check for NGS plugin, release-manifest,
CI-configuration, and root Node-version changes, including during merge. It
uses the monorepo's pinned Node runtime and a clean `npm ci` install; stale
hashes fail the job. The check does not upload assets or publish a release.

## Public demonstrations

Each bundled Snakemake workflow includes a runnable public example in its
`config/config.json`. Supply a project-specific configuration with absolute target paths
to skip the example downloads.

These are technical demonstrations, not biological studies. Preserve workflow,
input, reference, runtime, and result provenance, and do not treat successful
execution as support for a biological claim.

## Development

Start the Workbench MCP server from `mcp/`:

```bash
PYTHONPATH=. uv run --no-project --isolated \
  --with-requirements ./requirements.txt \
  python -m ngs_workbench_mcp
```

Codex starts all three packaged servers through `mcp/start_server` on
macOS/Linux or the matching `mcp/start_server.cmd` on Windows. The launchers
restore common user-local tool directories to `PATH`, prefer Codex's bundled
Python and pip, and fall back to `python3` on `PATH` (`python` is also supported
on Windows). Startup does not use `uv`. The first launch of a plugin venv
version creates `$CODEX_HOME/cache/ngs-analysis-workbench/venvs/<version>`;
later launches reuse that environment. Update `mcp/PLUGIN_VENV_VERSION`
whenever `mcp/requirements.txt` changes. A shared installation lock protects
concurrent first launches.

Run Python tests from the same directory:

```bash
PYTHONPATH=. uv run --no-project --isolated \
  --with-requirements ./requirements.txt \
  python -m unittest discover -s ../tests -p 'test_*.py'
```

Frontend checks:

```bash
npm run typecheck
npm run test:inline
npm run build:storybook
```

The package-lock check rejects cluster-specific Socket Firewall registry URLs
so the source lockfile remains portable.
