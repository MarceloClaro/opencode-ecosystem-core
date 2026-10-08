import type { Meta, StoryObj } from "@storybook/react-vite";

import { RunReviewSurface } from "./RunReviewApp";
import type { ReviewPlan, ReviewRun } from "./types";
import { snakemakeLogObservation } from "../fixtures/executionObservation";

const meta = {
  title: "NGS/Inline Plan and Live Receipt",
  parameters: { layout: "fullscreen" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const readyPlan: ReviewPlan = {
  binding: "snakemake",
  planName: "S10 FASTQ intake",
  planId: "ngs-plan-fae9e40d3f6c279f",
  planChecksum: "sha256:fae9e40d3f6c279f8a6b58f0a9f673067bfabcb06d019f490af85775da0bf182",
  runnable: true,
  request: {
    pipeline: "fastq_qc",
    target: { target_id: "local", provider: "ngs-analysis-workbench" },
    display_name: "S10 FASTQ intake",
    workflow: "workflows/fastq_qc/workflow/Snakefile",
    run_dir: "/tmp/test-qc/ngs_runs/snakemake/snakemake-fastq-qc-s10",
    config_file: "/tmp/test-qc/fastq-qc-config.json",
    config_sha256: "sha256:48729a01c6a60779bbacb7bc5520621df0d6ddd2e49702e26a6922b82397a739",
    workflow_sha256: "sha256:c2db94d21f4d0e84759f7e665c78bf41e970d554dbf6ac6067bf025a0d7025ee",
    cores: 4,
    run_id: "snakemake-fastq-qc-s10",
  },
  command: [
    "/opt/homebrew/bin/snakemake",
    "--snakefile",
    "/tmp/test-qc/ngs_runs/snakemake/fastq_qc/snakemake-fastq-qc-s10/workflow/Snakefile",
    "--configfile",
    "/tmp/test-qc/ngs_runs/snakemake/fastq_qc/snakemake-fastq-qc-s10/config/fastq-qc-config.json",
    "--directory",
    "/tmp/test-qc/ngs_runs/snakemake/fastq_qc/snakemake-fastq-qc-s10",
    "--cores",
    "4",
  ],
  readiness: {
    ok: true,
    scope: "local PATH",
    commands: [
      { name: "snakemake", path: "/opt/homebrew/bin/snakemake", state: "ready", version: "9.24.0" },
    ],
    blockers: [],
    warnings: [],
  },
  effects: {
    runDir: "/tmp/test-qc/ngs_runs/snakemake/snakemake-fastq-qc-s10",
    outputDir: "/tmp/test-qc/ngs_runs/snakemake/snakemake-fastq-qc-s10/results",
    workDir: "/tmp/test-qc/ngs_runs/snakemake/snakemake-fastq-qc-s10/work",
    launchLog: "/tmp/test-qc/ngs_runs/snakemake/snakemake-fastq-qc-s10/launch.log",
    localWrites: [
      "/tmp/test-qc/ngs_runs/snakemake/snakemake-fastq-qc-s10",
      "/tmp/test-qc/ngs_runs/snakemake/snakemake-fastq-qc-s10/results",
    ],
    downloads: [
      "https://raw.githubusercontent.com/nf-core/test-datasets/pinned/sample1_R1.fastq.gz",
      "https://raw.githubusercontent.com/nf-core/test-datasets/pinned/sample1_R2.fastq.gz",
    ],
    networkAccess: ["verified HTTPS download from raw.githubusercontent.com"],
  },
  preparation: {
    destinationDir: "/tmp/test-qc",
    downloadBytes: 6_412_688,
    writes: [
      "/tmp/test-qc/inputs/sample1_R1.fastq.gz",
      "/tmp/test-qc/inputs/sample1_R2.fastq.gz",
      "/tmp/test-qc/fastq-qc-config.json",
    ],
    operations: [
      {
        operation: "download_verified_file",
        path: "/tmp/test-qc/inputs/sample1_R1.fastq.gz",
        role: "SAMPLE1 read 1",
        url: "https://raw.githubusercontent.com/nf-core/test-datasets/pinned/sample1_R1.fastq.gz",
        bytes: 3_356_344,
        sha256: "sha256:b7469350e3167dcdeab6a498984030b09af4bbf17e5b5a9e8f95dc3ee352b031",
      },
      {
        operation: "download_verified_file",
        path: "/tmp/test-qc/inputs/sample1_R2.fastq.gz",
        role: "SAMPLE1 read 2",
        url: "https://raw.githubusercontent.com/nf-core/test-datasets/pinned/sample1_R2.fastq.gz",
        bytes: 3_056_344,
        sha256: "sha256:1fcbddf6dbb6d6508755477859161fa63be14246a85d4a4f75683da3f461e153",
      },
      {
        operation: "write_generated_file",
        path: "/tmp/test-qc/fastq-qc-config.json",
        bytes: 412,
        sha256: "sha256:48729a01c6a60779bbacb7bc5520621df0d6ddd2e49702e26a6922b82397a739",
        mediaType: "application/json",
      },
    ],
  },
  blockers: [],
  warnings: ["Reads will be inspected only; trimming is disabled."],
  monitoring: {
    terminal_statuses: ["completed", "failed", "canceled", "orphaned"],
    log_paths: ["/tmp/test-qc/logs/nextflow.log"],
    artifact_paths: ["/tmp/test-qc/results"],
  },
};

const scrnaPlan: ReviewPlan = {
  binding: "snakemake",
  planName: "PBMC single-cell smoke test",
  planId: "ngs-plan-2b35103408851039",
  planChecksum: "sha256:2b351034088510398a237c91fc4f842196b6e088888a767169ef689d48fd34df",
  runnable: true,
  request: {
    pipeline: "scrnaseq",
    target: { target_id: "local", provider: "ngs-analysis-workbench" },
    display_name: "PBMC single-cell smoke test",
    workflow: "workflows/scrnaseq_fastq_to_count/workflow/Snakefile",
    run_dir: "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke",
    config_file: "/tmp/ngs-scrnaseq-smoke/snakemake-config.json",
    config_sha256: "sha256:999fb57ee3837af3f9cbaa8707e4bbc2944bdf7b8ad2a1765041eb6d59c6d25e",
    workflow_sha256: "sha256:adc751413464799180a2b6b2f769bdbf251106721da68eebf2c79b127e2fc2eb",
    cores: 4,
    run_id: "snakemake-scrnaseq-smoke",
  },
  command: [
    "/tmp/ngs-runtime/bin/snakemake",
    "--snakefile",
    "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke/workflow/Snakefile",
    "--configfile",
    "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke/config/snakemake-config.json",
    "--directory",
    "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke",
    "--cores",
    "4",
  ],
  readiness: {
    ok: true,
    scope: "executable_presence_only",
    commands: [
      { name: "snakemake", path: "/tmp/ngs-runtime/bin/snakemake", state: "ready", version: "9.24.0" },
    ],
    blockers: [],
    warnings: [],
  },
  effects: {
    runDir: "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke",
    outputDir: "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke",
    workDir: "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke",
    launchLog: "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke/logs/snakemake.log",
    localWrites: [
      "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke/workflow",
      "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke/config/snakemake-config.json",
    ],
    downloads: [],
    networkAccess: [],
  },
  blockers: [],
  warnings: ["Workflow-specific effects are owned by the Snakefile and supplied config."],
  monitoring: {
    terminal_statuses: ["completed", "failed", "canceled", "orphaned"],
    log_paths: [
      "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke/logs/snakemake.log",
    ],
    artifact_paths: [
      "/tmp/ngs-scrnaseq-smoke/ngs_runs/snakemake/scrnaseq/snakemake-scrnaseq-smoke/results",
    ],
  },
};

const bulkRnaSnakemakePlan: ReviewPlan = {
  binding: "snakemake",
  planName: "Bulk RNA-seq QC · public example",
  planId: "ngs-plan-97f3e6946c25fbf9",
  planChecksum: "sha256:97f3e6946c25fbf9179fd245ff31ad47a09a2281f746bf8bc84fb933addb28d3",
  runnable: true,
  request: {
    pipeline: "rnaseq",
    target: { target_id: "local", provider: "ngs-analysis-workbench" },
    display_name: "GSE110004 counts QC",
    workflow: "workflows/bulk_rnaseq_counts_qc/workflow/Snakefile",
    run_dir: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2",
    config_file: "/tmp/ngs-bulk-rnaseq-smoke-20260806/snakemake-config.json",
    config_sha256: "sha256:1f223b846818b7a1517fef4af7d90114944284bcd1c68adfd7943420eb9b52db",
    workflow_sha256: "sha256:24c9bc287c4db718cf49209f6af05f8bbf19ebf5a33ae277b948cc31fb740bae",
    cores: 4,
    run_id: "snakemake-rnaseq-gse110004-smoke-2",
  },
  command: [
    "/tmp/ngs-scrnaseq-runtime-20260806/venv/bin/snakemake",
    "--snakefile",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2/workflow/Snakefile",
    "--configfile",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2/config/snakemake-config.json",
    "--directory",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2",
    "--cores",
    "4",
    "--printshellcmds",
    "--shared-fs-usage",
    "input-output",
    "persistence",
    "software-deployment",
    "software-deployment-cache",
    "sources",
    "storage-local-copies",
  ],
  readiness: {
    ok: true,
    scope: "executable_presence_only",
    commands: [{
      name: "snakemake",
      path: "/tmp/ngs-scrnaseq-runtime-20260806/venv/bin/snakemake",
      state: "ready",
      version: "9.24.0",
    }],
    blockers: [],
    warnings: [],
  },
  effects: {
    runDir: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2",
    outputDir: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2",
    workDir: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2",
    launchLog: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2/logs/snakemake.log",
    localWrites: [
      "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2/workflow",
      "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2/config/snakemake-config.json",
    ],
    downloads: [],
    networkAccess: [],
  },
  blockers: [],
  warnings: ["Tool and output effects are owned by the approved Snakefile and reviewed config."],
  monitoring: {
    terminal_statuses: ["completed", "failed", "canceled", "orphaned"],
    log_paths: [
      "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2/logs/snakemake.log",
    ],
    artifact_paths: [
      "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/snakemake/rnaseq/snakemake-rnaseq-gse110004-smoke-2/results",
    ],
  },
};

const bulkRnaNfcorePlan: ReviewPlan = {
  binding: "nextflow",
  planName: "Bulk RNA-seq QC · nf-core alternative",
  planId: "ngs-plan-dcebb40355863a07",
  planChecksum: "sha256:dcebb40355863a0706f894264784591c238b7da25bb50cf09970808f8125b7c4",
  runnable: true,
  request: {
    pipeline: "rnaseq",
    target: { target_id: "local", provider: "ngs-analysis-workbench" },
    display_name: "GSE110004 nf-core RNA-seq",
    workflow: "nf-core/rnaseq",
    run_dir: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2",
    profile: "test,docker",
    sample_sheet: "/tmp/ngs-bulk-rnaseq-smoke-20260806/samplesheet.csv",
    sample_sheet_sha256: "sha256:8bfd55084a46726a2005c8f38fd13f27b9f5ba7aab00c1b2bc8682276f831e36",
    revision: "3.26.0",
    params_file: "/tmp/ngs-bulk-rnaseq-smoke-20260806/nfcore-params.json",
    params_file_sha256: "sha256:24863b0175ce24ad7885875f39a8768568919b869dd16aae8372d81c172e56e1",
    trim: false,
    runtime_snapshot_id: "runtime-0123456789abcdef0123456789abcdef",
    run_id: "nfcore-rnaseq-gse110004-smoke-2",
  },
  command: [
    "/tmp/ngs-scrnaseq-runtime-20260806/bin/nextflow",
    "run",
    "nf-core/rnaseq",
    "-params-file",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/nfcore-params.json",
    "-work-dir",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/work",
    "-with-report",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/workflow/nextflow_report.html",
    "-with-timeline",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/workflow/timeline.html",
    "-with-trace",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/workflow/trace.txt",
    "-with-dag",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/workflow/dag.html",
    "-r",
    "3.26.0",
    "-profile",
    "test,docker",
    "--input",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/samplesheet.csv",
    "--outdir",
    "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/results",
  ],
  readiness: {
    ok: true,
    scope: "local_runtime_snapshot",
    snapshotId: "runtime-0123456789abcdef0123456789abcdef",
    host: { os: "darwin", arch: "arm64" },
    commands: [
      {
        name: "nextflow",
        path: "/tmp/ngs-scrnaseq-runtime-20260806/bin/nextflow",
        state: "ready",
        version: "version 26.04.6 build 0",
      },
      { name: "java", path: "/usr/bin/java", state: "ready", version: "openjdk version 26.0.1" },
      { name: "docker", path: "/usr/bin/docker", state: "ready", version: "Docker version 29.6.0" },
    ],
    docker: {
      path: "/usr/bin/docker",
      context: "desktop-linux",
      endpoint: "unix:///Users/scientist/.docker/run/docker.sock",
      endpointIsLocal: true,
      daemonReachable: true,
      serverVersion: "29.6.1",
      serverOs: "linux",
      serverArch: "arm64",
    },
    blockers: [],
    warnings: ["Container image architecture is verified only after images resolve."],
  },
  effects: {
    runDir: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2",
    outputDir: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/results",
    workDir: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/work",
    launchLog: "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/logs/nextflow.log",
    localWrites: [
      "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/results",
      "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/work",
    ],
    downloads: [
      "workflow source for nf-core/rnaseq at revision 3.26.0",
      "container images referenced by the workflow if absent from the local cache",
      "test-profile inputs referenced by the workflow if absent from the local cache",
    ],
    networkAccess: [
      "Nextflow workflow source resolution",
      "container registry access for uncached images",
      "remote test-data access declared by the workflow",
    ],
  },
  blockers: [],
  warnings: [],
  monitoring: {
    terminal_statuses: ["completed", "failed", "canceled", "orphaned"],
    log_paths: [
      "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/logs/nextflow.log",
    ],
    artifact_paths: [
      "/tmp/ngs-bulk-rnaseq-smoke-20260806/ngs_runs/nextflow/rnaseq/nfcore-rnaseq-gse110004-smoke-2/results",
    ],
  },
};

const blockedPlan: ReviewPlan = {
  ...readyPlan,
  planName: "Blocked FASTQ QC",
  planId: "ngs-plan-7ff89bfe1b71e51f",
  planChecksum: "sha256:7ff89bfe1b71e51f9add0dc01d784e3d321324e4b5669a3a10d72801b6b352f8",
  runnable: false,
  readiness: {
    ...readyPlan.readiness,
    ok: false,
    commands: [
      { name: "snakemake", path: null, state: "missing" },
    ],
    blockers: ["Snakemake is not available on PATH."],
  },
  blockers: [
    "Snakemake is not available on PATH.",
    "FastQC and MultiQC must be installed before this local plan can run.",
  ],
  warnings: [],
};

const runningRun: ReviewRun = {
  binding: "snakemake",
  registryRunId: "ngs-run-snakemake-fastq-qc-example",
  runId: "snakemake-fastq-qc-20260805-143501-a1b2c3d4",
  revision: 2,
  status: "running",
  workflow: "Local FASTQ QC",
  pid: 48172,
  runDir: "/tmp/test-qc/ngs_runs/snakemake/fastq_qc/snakemake-fastq-qc-20260805-143501-a1b2c3d4",
  command: readyPlan.command,
  warnings: ["Workflow-specific effects are owned by the Snakefile and supplied config."],
  logTail: [
    "Building DAG of jobs...",
    "[Tue Aug  5 14:35:04 2026]",
    "rule fastqc:",
    "    input: S10_L001_R1_001.fastq.gz, S10_L001_R2_001.fastq.gz",
    "    output: results/fastqc/S10_R1_fastqc.html, results/fastqc/S10_R2_fastqc.html",
  ].join("\n"),
  execution: snakemakeLogObservation,
};

const completedRun: ReviewRun = {
  ...runningRun,
  status: "completed",
  returncode: 0,
  warnings: [],
  logTail: `${runningRun.logTail}\nWorkflow completed successfully.`,
};

const failedRun: ReviewRun = {
  ...runningRun,
  status: "failed",
  returncode: 1,
  warnings: ["MultiQC was not started because one FastQC task failed."],
  logTail: `${runningRun.logTail}\nFastQC reported a truncated gzip stream for read 2.`,
};

const runActions = {
  refreshing: false,
  onRefresh: () => undefined,
};

export const Loading: Story = {
  render: () => <RunReviewSurface state="loading" />,
};

export const PlanReady: Story = {
  render: () => <RunReviewSurface state="plan" plan={readyPlan} />,
};

export const SingleCellPlanReady: Story = {
  render: () => <RunReviewSurface state="plan" plan={scrnaPlan} />,
};

export const BulkRnaSnakemakePlanReady: Story = {
  render: () => (
    <RunReviewSurface state="plan" plan={bulkRnaSnakemakePlan} />
  ),
};

export const BulkRnaNfCorePlanReady: Story = {
  render: () => <RunReviewSurface state="plan" plan={bulkRnaNfcorePlan} />,
};

export const PlanBlocked: Story = {
  render: () => <RunReviewSurface state="plan" plan={blockedPlan} />,
};

export const Running: Story = {
  render: () => (
    <RunReviewSurface state="run" run={runningRun} {...runActions} />
  ),
};

export const Completed: Story = {
  render: () => (
    <RunReviewSurface state="run" run={completedRun} {...runActions} />
  ),
};

export const Failed: Story = {
  render: () => (
    <RunReviewSurface state="run" run={failedRun} {...runActions} />
  ),
};

export const Refreshing: Story = {
  render: () => (
    <RunReviewSurface state="run" run={runningRun} {...runActions} refreshing />
  ),
};

export const ReceiptError: Story = {
  render: () => (
    <RunReviewSurface
      state="run"
      run={runningRun}
      {...runActions}
      error="The approved execution response included an incomplete receipt."
    />
  ),
};

export const InvalidResponse: Story = {
  render: () => (
    <RunReviewSurface
      state="error"
      message="The execution response was incomplete."
      payload={{ ok: true, status: "running" }}
    />
  ),
};

export const ExecutionBlocked: Story = {
  render: () => (
    <RunReviewSurface
      state="blocked"
      failure={{
        message: "runtime snapshot is unknown to this server; call get_runtime_environment again",
        recovery: "Refresh the runtime environment, then create and review a new execution plan.",
      }}
      payload={{
        ok: false,
        errors: ["runtime snapshot is unknown to this server; call get_runtime_environment again"],
      }}
    />
  ),
};

export const Narrow: Story = {
  parameters: { storyWidth: 390 },
  render: () => <RunReviewSurface state="plan" plan={readyPlan} />,
};

export const DarkRunning: Story = {
  parameters: { theme: "dark" },
  render: () => (
    <RunReviewSurface state="run" run={runningRun} {...runActions} />
  ),
};
