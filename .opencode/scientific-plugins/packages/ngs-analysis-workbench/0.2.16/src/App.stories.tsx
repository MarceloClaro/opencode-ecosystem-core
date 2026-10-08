import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  expect,
  fireEvent,
  spyOn,
  userEvent,
  waitFor,
  within,
} from "storybook/test";
import { useState } from "react";

import {
  NgsWorkbenchSurface,
  type NgsWorkbenchViewModel,
  type WorkbenchPage,
} from "./App";
import type {
  ComputeTarget,
  Pipeline,
  RunDetail,
  RunObservation,
  RunSummary,
} from "./model";
import type { AnalysisReportData } from "./report";
import { nextflowTraceObservation } from "./fixtures/executionObservation";

const meta = {
  title: "NGS/App Surfaces",
  parameters: { layout: "fullscreen", storyWidth: 1080 },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const pipelines: Pipeline[] = [
  {
    id: "fastq_qc",
    title: "FASTQ QC",
    workflow: "nf-core/demo",
    description: "Basic FASTQ quality checks with FastQC and MultiQC.",
    engine: "nextflow",
    collection: "nf-core",
    catalog: "bundled",
  },
  {
    id: "rnaseq",
    title: "Bulk RNA-seq",
    workflow: "nf-core/rnaseq",
    description: "Bulk RNA-seq alignment, quantification, and MultiQC.",
    engine: "nextflow",
    collection: "nf-core",
    catalog: "bundled",
  },
  {
    id: "rnaseq",
    title: "Bulk RNA-seq",
    workflow: "/workflows/rnaseq/Snakefile",
    description: "Alignment-free quantification with Salmon and MultiQC.",
    engine: "snakemake",
    catalog: "bundled",
    sourceKind: "local",
  },
  {
    id: "sarek",
    title: "DNA variant analysis",
    workflow: "nf-core/sarek",
    description: "Germline or somatic variant analysis using nf-core/sarek.",
    engine: "nextflow",
    collection: "nf-core",
    catalog: "bundled",
  },
  {
    id: "atacseq",
    title: "ATAC-seq",
    workflow: "nf-core/atacseq",
    description: "Alignment, QC, peak calling, and signal outputs.",
    engine: "nextflow",
    collection: "nf-core",
    catalog: "bundled",
  },
  {
    id: "lab_rnaseq",
    title: "Lab RNA quantification",
    workflow: "/workflows/lab_rnaseq",
    description: "Reusable laboratory workflow for expression quantification.",
    engine: "snakemake",
    catalog: "saved",
    sourceKind: "local",
    entrypoint: "workflow/Snakefile",
  },
];

const selectedPipeline = pipelines[1];

const computeTargets: ComputeTarget[] = [
  {
    target_id: "local",
    title: "This computer",
    controllerTransport: "local_process",
    executor: "local_process",
    workspaceAccess: "local_filesystem",
    description: "Run the workflow controller as a process on this computer.",
    executorConfiguration: {},
  },
  {
    target_id: "research-slurm",
    title: "Research Slurm",
    controllerTransport: "ssh",
    executor: "slurm",
    workspaceAccess: "remote_filesystem",
    description: "Run a workflow controller through the configured SSH target.",
    workspaceRoot: "/shared/rosalind",
    executorConfiguration: { partition: "genomics" },
  },
];

const runningRun: RunDetail = {
  binding: "nextflow",
  pipeline: selectedPipeline,
  workflow: selectedPipeline.workflow,
  target: { target_id: "local", provider: "ngs-analysis-workbench" },
  run_id: "nfcore-rnaseq-20260806-071700-a1b2c3d4",
  first_run_id: "nfcore-rnaseq-20260806-071700-a1b2c3d4",
  attempt_number: 1,
  registry_run_id: "registry-run-id",
  revision: 2,
  status: "running",
  display_name: "Lung cohort RNA-seq",
  analysis_summary:
    "Lung inflammation profiling is partially executed: FastQC completed, while Salmon quantification remains pending. No differential-expression or biological conclusions can be made yet.",
  pid: 48172,
  run_dir:
    "/workspaces/lung-rnaseq/ngs_runs/nextflow/nfcore-rnaseq-20260806-071700-a1b2c3d4",
  command_argv: [
    "nextflow",
    "run",
    "nf-core/rnaseq",
    "-r",
    "3.18.0",
    "-profile",
    "docker",
    "--input",
    "/workspaces/lung-rnaseq/samplesheet.csv",
  ],
  plan_checksum: `sha256:${"a".repeat(64)}`,
  warnings: [],
  returncode: null,
};

const runningObservation: RunObservation = {
  registry_run_id: runningRun.registry_run_id,
  revision: runningRun.revision,
  status: runningRun.status,
  pid: runningRun.pid,
  returncode: runningRun.returncode,
  failure_summary: runningRun.failure_summary,
  warnings: [],
  log_tail: [
    "executor > local (2)",
    "[52/9c2c36] process > NFCORE_RNASEQ:RNASEQ:ALIGN_STAR:STAR_ALIGN (S10) [100%] 1 of 1 ✔",
    "[a8/41faae] process > NFCORE_RNASEQ:RNASEQ:QUANTIFY_STAR_SALMON:SALMON_QUANT (S10) [50%] 1 of 2",
  ].join("\n"),
  execution: nextflowTraceObservation,
};

const completedAnalysis: AnalysisReportData = {
  title: "Bulk RNA-seq counts and quality control",
  description:
    "Alignment-free quantification and quality review for the GSE110004 lung RNA-seq cohort.",
  summary:
    "All six samples completed Salmon quantification and produced gene-level count and TPM matrices. Mapping rates were consistent across the cohort. One sample has elevated duplication and should be reviewed before differential expression, but the analysis remains usable.",
  completedAt: "August 7, 2026 at 09:42 UTC",
  duration: "14 min 32 sec",
  runDirectory:
    "/workspaces/lung-rnaseq/ngs_runs/nextflow/nfcore-rnaseq-20260805-142300-9f13a8cd",
  artifactCount: 24,
  metrics: [
    { label: "Samples", value: "6 / 6", detail: "Quantified", tone: "success" },
    {
      label: "Median mapping",
      value: "82.4%",
      detail: "Salmon mapping rate",
      tone: "success",
    },
    { label: "Genes detected", value: "18,642", detail: "Across all samples" },
    {
      label: "QC verdict",
      value: "Review",
      detail: "1 sample warning",
      tone: "warning",
    },
  ],
  warnings: [
    "GSM2956575 has elevated sequence duplication relative to the rest of the cohort.",
  ],
  entries: [
    {
      id: "fastqc_multiqc_helper",
      title: "FastQC MultiQC report",
      path: "fastqc/multiqc/multiqc_browser_helper.html",
      openUrl:
        "http://127.0.0.1:8765/fastqc/multiqc/multiqc_browser_helper.html",
      kind: "html_report",
      status: "created",
      description:
        "Read quality, duplication, adapter content, and per-sequence quality across all samples.",
    },
    {
      id: "counts_qc_review_notebook",
      title: "Counts and QC review notebook",
      path: "notebooks/bulk_rnaseq_counts_qc_review.marimo.py",
      kind: "notebook",
      status: "created",
      description:
        "Interactive review of matrices, QC verdicts, and generated reports.",
    },
    {
      id: "gene_num_reads_matrix",
      title: "Gene count matrix",
      path: "rnaseq_salmon/matrices/gene_num_reads.tsv",
      kind: "table",
      status: "created",
      description:
        "Gene-by-sample expected counts aggregated from Salmon transcripts.",
      size: "1.8 MB",
    },
    {
      id: "gene_tpm_matrix",
      title: "Gene TPM matrix",
      path: "rnaseq_salmon/matrices/gene_tpm.tsv",
      kind: "table",
      status: "created",
      description: "Gene-by-sample TPM values for downstream exploration.",
      size: "2.4 MB",
    },
    {
      id: "qc_verdict",
      title: "QC verdict",
      path: "qc/qc_verdict.json",
      kind: "json",
      status: "created",
      description:
        "Machine-readable pass, warning, and failure decisions with supporting metrics.",
      size: "4 KB",
    },
    {
      id: "normalized_samplesheet",
      title: "Normalized sample sheet",
      path: "validation/samplesheet.normalized.csv",
      kind: "table",
      status: "created",
      description:
        "Resolved input files, sample groups, layout, and row provenance.",
      size: "3 KB",
    },
  ],
  notes: [
    "Raw FASTQs and reference files were treated as read-only inputs.",
    "Use the QC verdict together with MultiQC before starting differential expression.",
  ],
  provenance: [
    { label: "Workflow", value: "local_light_snakemake_salmon" },
    { label: "Quantifier", value: "Salmon 1.10.3" },
    { label: "Reference", value: "GENCODE human release 48" },
    { label: "Manifest", value: "run_manifest.json · schema 0.4.0" },
    {
      label: "Parameter SHA256",
      value: "8bfd55084a46726a2005c8f38fd13f27b9f5ba7aab00c1b2bc8682276f831e36",
    },
  ],
  sources: [
    { label: "Scientific analysis", path: "analysis_summary.md" },
    { label: "Summary", path: "summary.md" },
    { label: "Run manifest", path: "run_manifest.json" },
    {
      label: "Review manifest",
      path: "visualizations/visualization_manifest.json",
    },
    { label: "Artifact index", path: "artifact_index.json" },
  ],
};

const completedRun: RunDetail = {
  ...runningRun,
  registry_run_id: "registry-run-completed",
  run_id: "nfcore-rnaseq-20260805-142300-9f13a8cd",
  status: "completed",
  display_name: "Baseline lung RNA-seq",
  pid: 39215,
  run_dir: completedAnalysis.runDirectory,
  returncode: 0,
};

const failedRun: RunDetail = {
  ...runningRun,
  registry_run_id: "registry-run-failed",
  run_id: "nfcore-sarek-20260804-095500-9ba87d10",
  status: "failed",
  display_name: "Tumor-normal pilot",
  analysis_summary:
    "The tumor-normal pilot failed after initial read QC because the reference index was unavailable. Only partial FastQC artifacts are verified; variant calls and biological conclusions are unsupported. Next step: inspect the existing reference configuration and failure log.",
  failure_summary: "Reference index was unavailable.",
  returncode: 1,
};

const recoveryRootRunId = "nfcore-rnaseq-20260805-134000-0a1b2c3d";
const recoveryAttempts: RunSummary[] = [
  [1, "Native bcl2fastq failed under Apple Silicon emulation."],
  [2, "BCL2FASTQ requested 72 GB, exceeding the target's 62.8 GB."],
  [3, "CheckQC setup exceeded the target's available memory."],
  [4, "Output publication failed after workflow tasks completed."],
].map(([attempt, summary]) => {
  const attemptNumber = Number(attempt);
  const runId =
    attemptNumber === 1
      ? recoveryRootRunId
      : `nfcore-rnaseq-20260805-13${
          40 + attemptNumber
        }00-${attemptNumber}b2c3d4`;
  const timestamp = Date.UTC(2026, 7, 5, 20, 30 + attemptNumber * 10);
  return {
    registry_run_id: `registry-run-recovery-${attemptNumber}`,
    run_id: runId,
    first_run_id: recoveryRootRunId,
    attempt_number: attemptNumber,
    binding: "nextflow",
    pipeline: "rnaseq",
    workflow: "nf-core/rnaseq",
    status: "failed",
    display_name: "Baseline lung RNA-seq",
    analysis_summary: String(summary),
    failure_summary: String(summary),
    revision: attemptNumber,
    workflow_revision: "3.18.0",
    profile: "docker",
    target: { target_id: "devbox2", provider: "ngs-analysis-workbench" },
    run_dir: `/workspaces/lung-rnaseq/ngs_runs/nextflow/rnaseq/${runId}`,
    pid: 39000 + attemptNumber,
    started_at_ms: timestamp,
    completed_at_ms: timestamp + 5 * 60_000,
    returncode: 1,
    created_at_ms: timestamp - 60_000,
    updated_at_ms: timestamp + 5 * 60_000,
  } satisfies RunSummary;
});
const runHistory: RunSummary[] = [
  {
    registry_run_id: runningRun.registry_run_id,
    run_id: runningRun.run_id,
    first_run_id: runningRun.run_id,
    attempt_number: 1,
    binding: "nextflow",
    pipeline: "rnaseq",
    workflow: "nf-core/rnaseq",
    status: "running",
    display_name: "Lung cohort RNA-seq",
    analysis_summary:
      "Lung inflammation profiling is partially executed; FastQC completed, while quantification and biological conclusions remain pending.",
    revision: 2,
    run_dir: runningRun.run_dir,
    pid: runningRun.pid ?? null,
    started_at_ms: Date.UTC(2026, 7, 6, 18, 8),
    completed_at_ms: null,
    returncode: null,
    created_at_ms: Date.UTC(2026, 7, 6, 18, 7),
    updated_at_ms: Date.UTC(2026, 7, 6, 18, 8),
  },
  ...recoveryAttempts,
  {
    registry_run_id: "registry-run-completed",
    run_id: "nfcore-rnaseq-20260805-142300-9f13a8cd",
    first_run_id: recoveryRootRunId,
    attempt_number: 5,
    binding: "nextflow",
    pipeline: "rnaseq",
    workflow: "nf-core/rnaseq",
    status: "completed",
    display_name: "Baseline lung RNA-seq",
    analysis_summary:
      "Six lung-cohort samples support downstream expression analysis; review one high-duplication sample first.",
    revision: 3,
    run_dir:
      "/workspaces/lung-rnaseq/ngs_runs/nextflow/nfcore-rnaseq-20260805-142300-9f13a8cd",
    pid: 39215,
    started_at_ms: Date.UTC(2026, 7, 5, 21, 23),
    completed_at_ms: Date.UTC(2026, 7, 5, 22, 41),
    returncode: 0,
    created_at_ms: Date.UTC(2026, 7, 5, 21, 22),
    updated_at_ms: Date.UTC(2026, 7, 5, 22, 41),
  },
  {
    registry_run_id: "registry-run-failed",
    run_id: "nfcore-sarek-20260804-095500-9ba87d10",
    first_run_id: "nfcore-sarek-20260804-095500-9ba87d10",
    attempt_number: 1,
    binding: "nextflow",
    pipeline: "sarek",
    workflow: "nf-core/sarek",
    status: "failed",
    display_name: "Tumor-normal pilot",
    analysis_summary:
      "The pilot failed after initial read QC because the reference index was unavailable; no variant calls are supported.",
    failure_summary: "Reference index was unavailable.",
    revision: 3,
    run_dir:
      "/workspaces/tumor-normal-sarek/ngs_runs/nextflow/nfcore-sarek-20260804-095500-9ba87d10",
    pid: 31104,
    started_at_ms: Date.UTC(2026, 7, 4, 16, 55),
    completed_at_ms: Date.UTC(2026, 7, 4, 17, 12),
    returncode: 1,
    created_at_ms: Date.UTC(2026, 7, 4, 16, 54),
    updated_at_ms: Date.UTC(2026, 7, 4, 17, 12),
  },
  {
    registry_run_id: "registry-run-snakemake",
    run_id: "snakemake-fastq-qc-20260803-081900-61af390e",
    first_run_id: "snakemake-fastq-qc-20260803-081900-61af390e",
    attempt_number: 1,
    binding: "snakemake",
    pipeline: "fastq_qc",
    workflow: "workflows/fastq_qc.smk",
    status: "completed",
    analysis_summary:
      "Intake reads passed adapter screening; base-composition bias should be reviewed against the RNA-seq library design.",
    revision: 3,
    run_dir:
      "/workspaces/fastq-intake/ngs_runs/snakemake/snakemake-fastq-qc-20260803-081900-61af390e",
    pid: 28411,
    started_at_ms: Date.UTC(2026, 7, 3, 15, 19),
    completed_at_ms: Date.UTC(2026, 7, 3, 15, 31),
    returncode: 0,
    created_at_ms: Date.UTC(2026, 7, 3, 15, 18),
    updated_at_ms: Date.UTC(2026, 7, 3, 15, 31),
  },
];

function workbench(
  overrides: Partial<NgsWorkbenchViewModel> = {},
): NgsWorkbenchViewModel {
  const selectedRun = overrides.analysisRun;
  return {
    analysisObservation: selectedRun
      ? observationForRun(selectedRun)
      : undefined,
    analysisReport:
      selectedRun?.status === "completed"
        ? {
            registry_run_id: selectedRun.registry_run_id,
            revision: selectedRun.revision,
            availability: "available",
            report: completedAnalysis,
          }
        : undefined,
    analysisRun: undefined,
    catalogLoading: false,
    computeTargets: [],
    connected: true,
    detailLoading: false,
    dismissError: () => undefined,
    displayMode: "inline",
    error: undefined,
    historyLoading: false,
    loadCatalog: async () => undefined,
    loadComputeTargets: async () => undefined,
    loadRunLineage: async (run) =>
      runHistory.filter(
        (candidate) => candidate.first_run_id === run.first_run_id,
      ),
    loadRunDetail: async (run) => detailForRun(run),
    loadRunObservation: async (run) => observationForRun(detailForRun(run)),
    observationError: undefined,
    observationLoading: false,
    operation: undefined,
    openArtifact: async () => undefined,
    openAnalysis: async () => undefined,
    pipelines,
    refreshStatus: async () => undefined,
    refreshRunHistory: async () => undefined,
    reportError: undefined,
    reportLoading: false,
    runHistory,
    targetsError: undefined,
    targetsLoading: false,
    targetsRequested: false,
    ...overrides,
  };
}

function renderSurface(
  viewModel: NgsWorkbenchViewModel,
  initialPage?: WorkbenchPage,
) {
  return (
    <StorySurface initialPage={initialPage} initialViewModel={viewModel} />
  );
}

function StorySurface({
  initialPage,
  initialViewModel,
}: {
  initialPage?: WorkbenchPage;
  initialViewModel: NgsWorkbenchViewModel;
}) {
  const [analysisRun, setAnalysisRun] = useState(initialViewModel.analysisRun);
  const [historyLoading, setHistoryLoading] = useState(
    initialViewModel.historyLoading,
  );

  const viewModel: NgsWorkbenchViewModel = {
    ...initialViewModel,
    analysisRun,
    ...(analysisRun !== initialViewModel.analysisRun
      ? {
          analysisObservation: analysisRun
            ? observationForRun(analysisRun)
            : undefined,
          analysisReport:
            analysisRun?.registry_run_id === completedRun.registry_run_id
              ? {
                  registry_run_id: analysisRun.registry_run_id,
                  revision: analysisRun.revision,
                  availability: "available" as const,
                  report: completedAnalysis,
                }
              : undefined,
        }
      : {}),
    historyLoading,
    openAnalysis: async (run) => {
      setHistoryLoading(true);
      await Promise.resolve();
      setAnalysisRun(await initialViewModel.loadRunDetail(run));
      setHistoryLoading(false);
    },
  };

  return (
    <NgsWorkbenchSurface initialPage={initialPage} workbench={viewModel} />
  );
}

function detailForRun(run: RunSummary): RunDetail {
  if (run.registry_run_id === runningRun.registry_run_id) return runningRun;
  if (run.registry_run_id === completedRun.registry_run_id) return completedRun;
  if (run.registry_run_id === failedRun.registry_run_id) return failedRun;

  const pipeline = pipelines.find(
    (candidate) =>
      candidate.id === run.pipeline && candidate.engine === run.binding,
  ) ?? {
    id: run.pipeline,
    title: run.display_name ?? run.workflow,
    workflow: run.workflow,
    description: "Registered NGS analysis run.",
  };
  return {
    binding: run.binding === "snakemake" ? "snakemake" : "nextflow",
    pipeline,
    workflow: run.workflow,
    target: run.target ?? undefined,
    run_id: run.run_id,
    first_run_id: run.first_run_id,
    attempt_number: run.attempt_number,
    registry_run_id: run.registry_run_id,
    revision: run.revision,
    status: run.status,
    display_name: run.display_name,
    analysis_summary: run.analysis_summary,
    failure_summary: run.failure_summary,
    pid: run.pid ?? undefined,
    run_dir: run.run_dir,
    command_argv: [
      run.binding === "snakemake" ? "snakemake" : "nextflow",
      "run",
      run.workflow,
    ],
    plan_checksum: `sha256:${"b".repeat(64)}`,
    warnings:
      run.status === "failed"
        ? ["The workflow exited before all tasks completed."]
        : [],
    returncode: run.returncode,
  };
}

function observationForRun(run: RunDetail): RunObservation {
  return {
    registry_run_id: run.registry_run_id,
    revision: run.revision,
    status: run.status,
    pid: run.pid,
    returncode: run.returncode,
    failure_summary: run.failure_summary,
    warnings: [],
    log_tail:
      run.status === "failed"
        ? "ERROR: A workflow process exited with a non-zero status."
        : run.status === "running"
        ? runningObservation.log_tail
        : "Workflow completed successfully.",
    execution: nextflowTraceObservation,
  };
}

export const OverviewNoActiveRun: Story = {
  render: () => renderSurface(workbench()),
};

export const RunHistoryOverview: Story = {
  render: () => renderSurface(workbench()),
};

export const RunHistoryNavigation: Story = {
  render: () => renderSurface(workbench()),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const historyFailure = canvas.getByText("Failed", {
      selector: "[data-ngs-chip]",
    });
    const failureStyle = getComputedStyle(historyFailure);
    const failureAppearance = [
      failureStyle.color,
      failureStyle.backgroundColor,
    ];
    const historyEngine = canvas.getAllByText("Nextflow", {
      selector: "[data-ngs-chip]",
    })[0];
    const chipGeometry = (element: HTMLElement) => {
      const style = getComputedStyle(element);
      return [
        style.height,
        style.borderRadius,
        style.fontSize,
        style.fontWeight,
        style.lineHeight,
        style.padding,
      ];
    };
    const historyGeometry = chipGeometry(historyFailure);
    await expect(chipGeometry(historyEngine)).toEqual(historyGeometry);
    await expect(historyFailure.querySelector(".oai-icon")).not.toBeNull();
    await expect(historyEngine.querySelector(".oai-icon")).toBeNull();
    await userEvent.click(
      canvas.getByRole("button", { name: /Completed Baseline lung RNA-seq/ }),
    );

    await expect(
      canvas.getByRole("complementary", { name: "Run history" }),
    ).toBeInTheDocument();
    await expect(
      canvas.getAllByRole("tab", { name: /Attempt \d/ }),
    ).toHaveLength(5);
    const analysisHeading = canvas.getByRole("heading", {
      name: "Bulk RNA-seq counts and quality control",
    });

    await userEvent.click(canvas.getByRole("tab", { name: /Attempt 2/ }));
    await expect(
      canvas.getByText(/BCL2FASTQ requested 72 GB/),
    ).toBeInTheDocument();
    const attemptFailure = canvas.getByText("Failed", {
      selector: "[data-ngs-chip]",
    });
    const failedAttempt = canvas.getByRole("tabpanel", {
      name: "Attempt 2: Failed",
    });
    await expect(
      within(failedAttempt).queryByRole("region", {
        name: "Execution details",
      }),
    ).toBeNull();
    await expect(
      within(failedAttempt).getByRole("heading", { name: "Recorded failure" }),
    ).toBeVisible();
    const attemptStyle = getComputedStyle(attemptFailure);
    await expect(chipGeometry(attemptFailure)).toEqual(historyGeometry);
    await expect([attemptStyle.color, attemptStyle.backgroundColor]).toEqual(
      failureAppearance,
    );
    await expect(attemptFailure.querySelector(".oai-icon")).not.toBeNull();
    const failedTabIcon = canvas
      .getByRole("tab", { name: "Attempt 2: Failed" })
      .querySelector<HTMLElement>(".oai-icon")!;
    await expect(
      failedTabIcon.style.getPropertyValue("--oai-icon-source"),
    ).toBe(
      attemptFailure
        .querySelector<HTMLElement>(".oai-icon")!
        .style.getPropertyValue("--oai-icon-source"),
    );
    await expect(
      canvas.getAllByRole("tab", { name: /Attempt \d/ }),
    ).toHaveLength(5);
    await expect(analysisHeading).toBeInTheDocument();

    const selectedTab = canvas.getByRole("tab", {
      name: "Attempt 2: Failed",
    });
    await userEvent.keyboard("{ArrowRight}");
    const nextTab = canvas.getByRole("tab", { name: /Attempt 3:/ });
    await expect(nextTab).toHaveFocus();
    await expect(nextTab).toHaveAttribute("aria-selected", "false");
    await expect(selectedTab).toHaveAttribute("aria-selected", "true");
    await userEvent.keyboard("{Enter}");
    await waitFor(() =>
      expect(nextTab).toHaveAttribute("aria-selected", "true"),
    );
    await expect(analysisHeading).toBeInTheDocument();
    await userEvent.keyboard("{Home}");
    await expect(canvas.getByRole("tab", { name: /Attempt 1:/ })).toHaveFocus();
    await userEvent.keyboard("{End}");
    await expect(canvas.getByRole("tab", { name: /Attempt 5:/ })).toHaveFocus();
    await userEvent.click(selectedTab);

    const inspector = canvas.getByRole("complementary", {
      name: "Run history",
    });
    const contextBar = canvas.getByRole("navigation", {
      name: "Workbench pages",
    }).parentElement!;
    await expect(inspector.getBoundingClientRect().top).toBe(
      contextBar.getBoundingClientRect().top,
    );
    await expect(
      within(inspector).getAllByRole("button", { name: "Close run history" }),
    ).toHaveLength(1);
    await userEvent.click(
      canvas.getByRole("button", { name: "Close run history" }),
    );
    const openToggle = canvas.getByRole("button", { name: "Open run history" });
    await expect(openToggle).toHaveAttribute("aria-expanded", "false");
    await waitFor(() => expect(openToggle).toHaveFocus());
    await expect(
      canvas.queryByRole("complementary", { name: "Run history" }),
    ).not.toBeInTheDocument();
    await expect(analysisHeading).toBeInTheDocument();

    await userEvent.keyboard("{Enter}");
    const closeToggle = canvas.getByRole("button", {
      name: "Close run history",
    });
    await expect(closeToggle).toHaveAttribute("aria-expanded", "true");
    await waitFor(() => expect(closeToggle).toHaveFocus());
    await expect(
      canvas.getByRole("tab", { name: "Attempt 2: Failed" }),
    ).toHaveAttribute("aria-selected", "true");
  },
};

export const RunHistoryClosed: Story = {
  render: () => renderSurface(workbench({ analysisRun: completedRun }), "run"),
  play: async ({ canvasElement }) => {
    await userEvent.click(
      within(canvasElement).getByRole("button", { name: "Close run history" }),
    );
  },
};

export const OverviewCompletedRunInHistory: Story = {
  render: () => renderSurface(workbench({ analysisRun: completedRun })),
};

export const OverviewScientificSummaryReady: Story = {
  render: () =>
    renderSurface(
      workbench({
        runHistory: [
          {
            ...runHistory[3],
            display_name:
              "Azure-backed Brix Snakemake FastQC: paired SRR6357072",
            analysis_summary:
              "FastQC of paired SRR6357072: 50,000 high-quality reads per mate; " +
              "review duplication and sequence-content warnings.",
          },
          ...runHistory.slice(0, 3),
        ],
      }),
    ),
};

export const OverviewRunning: Story = {
  render: () => renderSurface(workbench({ analysisRun: runningRun })),
};

export const OverviewEmptyHistory: Story = {
  render: () => renderSurface(workbench({ runHistory: [] })),
};

export const Workflows: Story = {
  render: () => renderSurface(workbench(), "workflows"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const workflowCard = canvas.getByRole("button", {
      name: /DNA variant analysis/i,
    });

    await userEvent.click(workflowCard);
    const dialog = await canvas.findByRole("dialog", {
      name: "DNA variant analysis",
    });
    await waitFor(() =>
      expect(
        within(dialog).getByText(
          "Germline or somatic variant analysis using nf-core/sarek.",
        ),
      ).toBeVisible(),
    );

    await userEvent.keyboard("{Escape}");
    await waitFor(() => expect(dialog).not.toBeInTheDocument());
    await expect(workflowCard).toHaveFocus();

    await userEvent.click(workflowCard);
    const reopenedDialog = await canvas.findByRole("dialog", {
      name: "DNA variant analysis",
    });
    await userEvent.click(
      within(reopenedDialog).getByRole("button", {
        name: "Close pipeline details",
      }),
    );
    await waitFor(() => expect(reopenedDialog).not.toBeInTheDocument());
    await expect(workflowCard).toHaveFocus();

    await userEvent.click(workflowCard);
    const backdropDialog = await canvas.findByRole("dialog", {
      name: "DNA variant analysis",
    });
    fireEvent.click(backdropDialog);
    await waitFor(() => expect(backdropDialog).not.toBeInTheDocument());
    await expect(workflowCard).toHaveFocus();
  },
};

export const Compute: Story = {
  render: () => renderSurface(workbench({ computeTargets }), "compute"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const targetRow = canvas.getByRole("button", { name: /Research Slurm/i });

    await userEvent.click(targetRow);
    const dialog = await canvas.findByRole("dialog", {
      name: "Research Slurm",
    });
    await waitFor(() =>
      expect(within(dialog).getByText("Remote filesystem")).toBeVisible(),
    );
    await userEvent.keyboard("{Escape}");
    await waitFor(() =>
      expect(canvas.queryByRole("dialog")).not.toBeInTheDocument(),
    );
    await expect(targetRow).toHaveFocus();

    await userEvent.click(targetRow);
    await userEvent.click(await canvas.findByRole("button", { name: "Close" }));
    await waitFor(() =>
      expect(canvas.queryByRole("dialog")).not.toBeInTheDocument(),
    );
    await expect(targetRow).toHaveFocus();
  },
};

export const ComputeNarrow: Story = {
  parameters: { storyWidth: 480 },
  render: () => renderSurface(workbench({ computeTargets }), "compute"),
};

export const WorkflowsEmpty: Story = {
  render: () => renderSurface(workbench({ pipelines: [] }), "workflows"),
};

export const WorkflowsLoading: Story = {
  render: () =>
    renderSurface(
      workbench({ catalogLoading: true, pipelines: [] }),
      "workflows",
    ),
};

export const FullscreenOverview: Story = {
  parameters: { hostDisplayMode: "fullscreen", storyWidth: "none" },
  render: () => renderSurface(workbench({ displayMode: "fullscreen" })),
};

export const FullscreenWorkflows: Story = {
  parameters: { hostDisplayMode: "fullscreen", storyWidth: "none" },
  render: () =>
    renderSurface(workbench({ displayMode: "fullscreen" }), "workflows"),
};

export const FullscreenRunning: Story = {
  parameters: { hostDisplayMode: "fullscreen", storyWidth: "none" },
  render: () =>
    renderSurface(
      workbench({
        analysisRun: runningRun,
        displayMode: "fullscreen",
      }),
      "run",
    ),
};

export const FullscreenResults: Story = {
  parameters: { hostDisplayMode: "fullscreen", storyWidth: "none" },
  render: () =>
    renderSurface(
      workbench({
        analysisRun: completedRun,
        displayMode: "fullscreen",
      }),
      "run",
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const count = canvas.getByText("4", { selector: "[data-ngs-chip]" });
    const taskGroup = canvas.getByRole("group", { name: "Task attempts" });
    const tasks = taskGroup.querySelector("summary")!;
    const memoryLabels = canvas.getAllByText("Peak memory", { selector: "dt" });
    await expect(memoryLabels[0]).not.toBeVisible();
    await userEvent.click(tasks);
    await waitFor(() => expect(memoryLabels[0]).toBeVisible());
    for (const label of memoryLabels) {
      await expect(label).toBeVisible();
      await expect(label.getBoundingClientRect().height).toBeLessThanOrEqual(
        parseFloat(getComputedStyle(label).lineHeight) + 1,
      );
    }
    const completed = canvas.getAllByText("Completed", {
      selector: "[data-ngs-chip]",
    });
    const analysisCompleted = canvas.getByText("Analysis completed", {
      selector: "[data-ngs-chip]",
    });
    for (const property of [
      "height",
      "fontSize",
      "borderRadius",
      "backgroundColor",
    ] as const) {
      await expect(getComputedStyle(analysisCompleted)[property]).toBe(
        getComputedStyle(completed[0])[property],
      );
    }
    // Task identity layout must not turn chip contents into a vertical grid.
    for (const chip of completed) {
      await expect(chip.getBoundingClientRect().height).toBe(
        count.getBoundingClientRect().height,
      );
      await expect(getComputedStyle(chip).display).toMatch(/^(inline-)?flex$/);
    }
    const analysisPane = canvas.getByRole("region", {
      name: "Analysis and execution",
    });
    const reportTitle = within(analysisPane).getByRole("heading", {
      name: completedAnalysis.title,
    });
    const summaryHeading = within(analysisPane).getByRole("heading", {
      name: "Analysis summary",
    });
    await expect(
      parseFloat(getComputedStyle(reportTitle).fontSize),
    ).toBeGreaterThan(parseFloat(getComputedStyle(summaryHeading).fontSize));
    const reportHeader = reportTitle.closest("header")!;
    const reportRunId = reportHeader.querySelector("code")!;
    const reportMetadata = reportRunId.parentElement!.getBoundingClientRect();
    const reportHeaderBounds = reportHeader.getBoundingClientRect();
    await expect(reportMetadata.left).toBe(reportHeaderBounds.left);
    await expect(reportMetadata.right).toBe(reportHeaderBounds.right);
    await expect(reportRunId.scrollWidth).toBeLessThanOrEqual(
      reportRunId.clientWidth,
    );
    const attemptPane = canvas.getByRole("tabpanel", {
      name: "Attempt 5: Completed",
    });
    const summaryRows = ["Status", "Finished", "Progress"].map((label) =>
      within(attemptPane)
        .getAllByText(label, { selector: "dt" })
        .find((element) => !element.closest("details"))!
        .parentElement!.getBoundingClientRect(),
    );
    await expect(
      Math.abs(
        summaryRows[1].top -
          summaryRows[0].top -
          (summaryRows[2].top - summaryRows[1].top),
      ),
    ).toBeLessThanOrEqual(1);
    await expect(within(attemptPane).queryByText("Latest task")).toBeNull();
    for (const label of ["Finished", "Progress"]) {
      const term = within(attemptPane)
        .getAllByText(label, { selector: "dt" })
        .find((element) => !element.closest("details"))!;
      await expect(getComputedStyle(term).fontSize).toBe(
        getComputedStyle(term.nextElementSibling!).fontSize,
      );
    }
    const warning = canvas.getByRole("region", { name: "Review recommended" });
    const warningIcon = warning.querySelector<HTMLElement>(".oai-icon")!;
    await expect(warningIcon.getBoundingClientRect().width).toBe(20);
    await expect(getComputedStyle(warningIcon).backgroundColor).toBe(
      getComputedStyle(warningIcon).color,
    );
    const completedTabIcon = canvas
      .getByRole("tab", { name: "Attempt 5: Completed" })
      .querySelector<HTMLElement>(".oai-icon")!;
    const completedStatusIcon = within(attemptPane)
      .getAllByText("Completed", { selector: "[data-ngs-chip]" })[0]
      .querySelector<HTMLElement>(".oai-icon")!;
    await expect(
      completedTabIcon.style.getPropertyValue("--oai-icon-source"),
    ).toBe(completedStatusIcon.style.getPropertyValue("--oai-icon-source"));
    for (const icon of [completedTabIcon, completedStatusIcon]) {
      await expect(icon.getBoundingClientRect().width).toBe(16);
      await expect(icon.getBoundingClientRect().height).toBe(16);
    }
    const refresh = within(attemptPane).getByRole("button", {
      name: "Refresh status",
    });
    await expect(refresh.textContent).toBe("");
    await expect(refresh.getBoundingClientRect().width).toBe(
      refresh.getBoundingClientRect().height,
    );
    await userEvent.hover(refresh);
    const tooltip = await canvas.findByRole("tooltip", {
      name: "Refresh status",
    });
    await expect(tooltip).toBeVisible();
    await expect(refresh).toHaveAttribute("aria-describedby", tooltip.id);
    await expect(tooltip.closest(".ngs-theme")).toBe(
      refresh.closest(".ngs-theme"),
    );
    await userEvent.unhover(refresh);
    await waitFor(() => expect(canvas.queryByRole("tooltip")).toBeNull());
    refresh.focus();
    await userEvent.tab({ shift: true });
    await userEvent.tab();
    await expect(refresh).toHaveFocus();
    await expect(await canvas.findByRole("tooltip")).toBeVisible();
    await userEvent.keyboard("{Escape}");
    await waitFor(() => expect(canvas.queryByRole("tooltip")).toBeNull());
    const heading = within(attemptPane).getByRole("heading", {
      name: "Attempt status",
    });
    await expect(refresh.getBoundingClientRect().bottom).toBeLessThanOrEqual(
      summaryRows[0].top,
    );
    await expect(
      Math.abs(
        refresh.getBoundingClientRect().top +
          refresh.getBoundingClientRect().height / 2 -
          (heading.getBoundingClientRect().top +
            heading.getBoundingClientRect().height / 2),
      ),
    ).toBeLessThanOrEqual(1);
    const contextNav = canvas.getByRole("navigation", {
      name: "Workbench pages",
    });
    const contextTop = contextNav.getBoundingClientRect().top;
    const analysisTop = analysisPane.getBoundingClientRect().top;
    const appBar = canvas.getByRole("banner").getBoundingClientRect();
    const previewFrame = canvas
      .getByRole("banner")
      .closest(".ngs-storybook-shell")!
      .getBoundingClientRect();
    await expect(appBar.left).toBe(previewFrame.left);
    await expect(appBar.right).toBe(previewFrame.right);
    const contextBar = contextNav.parentElement!.getBoundingClientRect();
    // The persistent context bar must not apply a second sticky offset inside
    // the fullscreen grid and overlap the top of the report.
    await expect(contextBar.top).toBe(appBar.bottom);
    await expect(contextBar.bottom).toBe(analysisTop);
    await expect(
      canvas
        .getByRole("complementary", {
          name: "Run history",
        })
        .getBoundingClientRect().top,
    ).toBe(contextBar.top);
    await expect(
      canvas.getByRole("tab", {
        name: "Attempt 5: Completed",
      }),
    ).toHaveTextContent("Attempt 5");
    attemptPane.scrollTop = 180;
    await expect(attemptPane.scrollTop).toBeGreaterThan(0);
    await expect(analysisPane.scrollTop).toBe(0);
    const attemptScroll = attemptPane.scrollTop;
    analysisPane.scrollTop = 180;
    await expect(analysisPane.scrollTop).toBeGreaterThan(0);
    await expect(attemptPane.scrollTop).toBe(attemptScroll);
    await expect(contextNav.getBoundingClientRect().top).toBe(contextTop);
    await expect(analysisPane.getBoundingClientRect().top).toBe(analysisTop);
    attemptPane.scrollTop = 0;
    analysisPane.scrollTop = 0;
    await userEvent.click(tasks);
    await expect(memoryLabels[0]).not.toBeVisible();
    const disclosureRows = [
      "Task attempts",
      "Execution evidence",
      "Run metadata",
      "Recorded command",
      "Execution log tail",
    ].map((name) =>
      within(attemptPane)
        .getByText(name, {
          selector:
            name === "Task attempts"
              ? "summary > span:not(.oai-icon)"
              : "summary",
        })
        .closest("summary")!
        .getBoundingClientRect(),
    );
    for (let index = 1; index < disclosureRows.length; index++) {
      await expect(disclosureRows[index].height).toBe(disclosureRows[0].height);
      await expect(
        Math.abs(disclosureRows[index].top - disclosureRows[index - 1].bottom),
      ).toBeLessThanOrEqual(1);
    }
    if (document.activeElement === attemptPane) attemptPane.blur();
  },
};

function renderAttemptHistory(attemptCount: number) {
  const attempts: RunSummary[] = Array.from(
    { length: attemptCount - 1 },
    (_, index) => ({
      ...recoveryAttempts[index % recoveryAttempts.length],
      registry_run_id: `registry-run-long-history-${index + 1}`,
      run_id: `workflow-long-history-${index + 1}`,
      attempt_number: index + 1,
    }),
  );
  const completedSummary = runHistory.find(
    (run) => run.registry_run_id === completedRun.registry_run_id,
  )!;
  attempts.push({ ...completedSummary, attempt_number: attemptCount });
  return renderSurface(
    workbench({
      analysisRun: { ...completedRun, attempt_number: attemptCount },
      displayMode: "fullscreen",
      runHistory: attempts,
      loadRunLineage: async () => attempts,
    }),
    "run",
  );
}

export const TwoAttemptHistory: Story = {
  parameters: { hostDisplayMode: "fullscreen", storyWidth: "none" },
  render: () => renderAttemptHistory(2),
  play: async ({ canvasElement }) => {
    const list = await within(canvasElement).findByRole("tablist", {
      name: "Workflow attempts",
    });
    await waitFor(() => {
      expect(within(list).getAllByRole("tab")).toHaveLength(2);
      expect(list.scrollWidth).toBeLessThanOrEqual(list.clientWidth + 1);
      expect(list).toHaveAttribute("data-overflow-left", "false");
      expect(list).toHaveAttribute("data-overflow-right", "false");
    });
  },
};

export const LongAttemptHistory: Story = {
  parameters: { hostDisplayMode: "fullscreen", storyWidth: "none" },
  render: () => renderAttemptHistory(20),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const list = await canvas.findByRole("tablist", {
      name: "Workflow attempts",
    });
    await waitFor(() =>
      expect(within(list).getAllByRole("tab")).toHaveLength(20),
    );
    const first = within(list).getByRole("tab", { name: "Attempt 1: Failed" });
    const last = within(list).getByRole("tab", {
      name: "Attempt 20: Completed",
    });
    const report = canvas.getByRole("heading", {
      name: "Bulk RNA-seq counts and quality control",
    });
    const analysisPane = canvas.getByRole("region", {
      name: "Analysis and execution",
    });
    const reportTop = report.getBoundingClientRect().top;

    const expectSelectedVisible = async (tab: HTMLElement) => {
      await waitFor(() => {
        const listRect = list.getBoundingClientRect();
        const tabRect = tab.getBoundingClientRect();
        expect(tabRect.left).toBeGreaterThanOrEqual(listRect.left - 1);
        expect(tabRect.right).toBeLessThanOrEqual(listRect.right + 1);
        const indicator = list.querySelector<HTMLElement>(
          '[role="presentation"]',
        )!;
        const indicatorRect = indicator.getBoundingClientRect();
        expect(Math.abs(indicatorRect.left - tabRect.left)).toBeLessThanOrEqual(
          1,
        );
        expect(
          Math.abs(indicatorRect.width - tabRect.width),
        ).toBeLessThanOrEqual(1);
        expect(indicatorRect.height).toBe(2);
      });
    };

    await expect(list.scrollWidth).toBeGreaterThan(list.clientWidth);
    await expectSelectedVisible(last);
    await expect(list.scrollLeft).toBeGreaterThan(0);
    await waitFor(() => {
      expect(list).toHaveAttribute("data-overflow-left", "true");
      expect(list).toHaveAttribute("data-overflow-right", "false");
    });
    await expect(getComputedStyle(list).maskImage).not.toBe("none");
    await userEvent.click(last);
    list.scrollLeft = (list.scrollWidth - list.clientWidth) / 2;
    fireEvent.scroll(list);
    await waitFor(() => {
      expect(list).toHaveAttribute("data-overflow-left", "true");
      expect(list).toHaveAttribute("data-overflow-right", "true");
    });
    await userEvent.keyboard("{Home}");
    await expect(first).toHaveFocus();
    await expect(last).toHaveAttribute("aria-selected", "true");
    await userEvent.keyboard("{Enter}");
    await expectSelectedVisible(first);
    await waitFor(() => {
      expect(list).toHaveAttribute("data-overflow-left", "false");
      expect(list).toHaveAttribute("data-overflow-right", "true");
    });
    await expect(first).toHaveAttribute("aria-selected", "true");
    await waitFor(() =>
      expect(canvas.getAllByRole("tabpanel")).toHaveLength(1),
    );
    await expect(
      canvas.getByRole("tabpanel", {
        name: "Attempt 1: Failed",
      }),
    ).toHaveAttribute("aria-labelledby", first.id);

    await userEvent.keyboard("{End}{Enter}");
    await expectSelectedVisible(last);
    await expect(last).toHaveAttribute("aria-selected", "true");
    await waitFor(() =>
      expect(canvas.getAllByRole("tabpanel")).toHaveLength(1),
    );
    await expect(
      canvas.getByRole("tabpanel", {
        name: "Attempt 20: Completed",
      }),
    ).toHaveAttribute("id", last.getAttribute("aria-controls"));
    await expect(report).toBeInTheDocument();
    await expect(report.getBoundingClientRect().top).toBe(reportTop);
    await expect(analysisPane.scrollTop).toBe(0);
  },
};

export const CompletedWithoutAnalysis: Story = {
  render: () =>
    renderSurface(
      workbench({
        analysisRun: completedRun,
        analysisReport: {
          registry_run_id: completedRun.registry_run_id,
          revision: completedRun.revision,
          availability: "available",
          report: {
            ...completedAnalysis,
            summary: "",
            sources: completedAnalysis.sources.filter(
              (source) => source.path !== "analysis_summary.md",
            ),
          },
        },
      }),
      "run",
    ),
};

export const FailedRunDetail: Story = {
  render: () => renderSurface(workbench({ analysisRun: failedRun }), "run"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const inspector = canvas.getByRole("complementary", {
      name: "Run history",
    });
    await expect(within(inspector).queryByRole("tablist")).toBeNull();
    await expect(within(inspector).queryByRole("tab")).toBeNull();
    await expect(within(inspector).queryByRole("tabpanel")).toBeNull();
    const attempt = within(inspector).getByRole("region", {
      name: "Attempt 1: Failed",
    });
    await expect(
      within(attempt).getByRole("heading", {
        name: "Attempt status",
      }),
    ).toBeVisible();
    await expect(
      within(attempt).getByRole("button", {
        name: "Refresh status",
      }),
    ).toBeVisible();
  },
};

export const NarrowOverview: Story = {
  parameters: { storyWidth: 420 },
  render: () => renderSurface(workbench({ analysisRun: runningRun })),
};

export const NarrowWorkflows: Story = {
  parameters: { storyWidth: 420 },
  render: () => renderSurface(workbench(), "workflows"),
};

export const DarkRunning: Story = {
  parameters: { theme: "dark" },
  render: () => renderSurface(workbench({ analysisRun: runningRun })),
};

export const DarkResults: Story = {
  parameters: {
    hostDisplayMode: "fullscreen",
    storyWidth: "none",
    theme: "dark",
  },
  render: () =>
    renderSurface(
      workbench({
        analysisRun: completedRun,
        displayMode: "fullscreen",
      }),
      "run",
    ),
};

// These fixtures exercise the desktop host contract without requiring a live MCP host.
export const CodexLightResults: Story = {
  ...FullscreenResults,
  parameters: { ...FullscreenResults.parameters, hostTheme: "codex-light" },
  play: async ({ canvasElement }) => {
    const action = within(canvasElement).getAllByRole("button", {
      name: "Open FastQC MultiQC report",
    })[0];
    // The host inverse token is a translucent surface. It must not dim button text.
    await expect(getComputedStyle(action).color).not.toMatch(
      /\/\s*0\.|rgba\([^)]*,\s*0\./,
    );
  },
};

export const CodexDarkResults: Story = {
  ...FullscreenResults,
  parameters: { ...FullscreenResults.parameters, hostTheme: "codex-dark" },
};

export const FallbackDarkResults: Story = {
  ...FullscreenResults,
  parameters: { ...FullscreenResults.parameters, hostTheme: "fallback-dark" },
};

export const FallbackLightResults: Story = {
  ...FullscreenResults,
  parameters: { ...FullscreenResults.parameters, hostTheme: "fallback-light" },
};

export const HostTypographyAndFocus: Story = {
  ...Workflows,
  parameters: {
    hostTheme: "codex-light",
    storyWidth: 420,
    hostVariables: {
      "--font-sans": "Georgia, serif",
      "--font-text-md-size": "16px",
      "--border-radius-sm": "8px",
      "--color-ring-primary": "rgb(103, 58, 183)",
    },
  },
  play: async (context) => {
    const canvas = within(context.canvasElement);
    const runs = canvas.getByRole("button", { name: /^Runs$/ });
    await expect(getComputedStyle(runs).fontFamily).toContain("Georgia");
    await expect(getComputedStyle(runs).fontSize).toBe("16px");
    await expect(getComputedStyle(runs).borderRadius).toBe("12px");
    await Workflows.play?.(context);
  },
};

export const NarrowRunningDetail: Story = {
  parameters: { storyWidth: 390, hostTheme: "codex-light" },
  render: () => renderSurface(workbench({ analysisRun: runningRun }), "run"),
};

export const NarrowAttemptsDrawer: Story = {
  parameters: {
    storyWidth: 390,
    hostTheme: "codex-light",
    hostDisplayMode: "fullscreen",
  },
  render: () =>
    renderSurface(
      workbench({ analysisRun: completedRun, displayMode: "fullscreen" }),
      "run",
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const toggle = canvas.getByRole("button", { name: "Open run history" });
    await waitFor(() =>
      expect(toggle).toHaveAttribute("aria-haspopup", "dialog"),
    );
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await expect(canvas.queryByRole("dialog")).not.toBeInTheDocument();
    const analysis = canvas.getByRole("heading", {
      name: "Bulk RNA-seq counts and quality control",
    });
    await expect(analysis).toBeVisible();

    await userEvent.click(toggle);
    const drawer = await canvas.findByRole("dialog", { name: "Run history" });
    await expect(drawer.matches(":modal")).toBe(true);
    await expect(drawer.contains(document.activeElement)).toBe(true);
    await expect(getComputedStyle(drawer).backgroundColor).not.toMatch(
      /\/\s*0\.|rgba\([^)]*,\s*0\./,
    );
    await userEvent.click(
      within(drawer).getByRole("tab", { name: "Attempt 2: Failed" }),
    );
    await waitFor(() =>
      expect(
        within(drawer).getByText(/BCL2FASTQ requested 72 GB/),
      ).toBeVisible(),
    );
    const refresh = within(drawer).getByRole("button", {
      name: "Refresh status",
    });
    await userEvent.hover(refresh);
    await expect(
      await within(drawer).findByRole("tooltip", { name: "Refresh status" }),
    ).toBeVisible();
    refresh.focus();
    await userEvent.keyboard("{Escape}");
    await waitFor(() =>
      expect(within(drawer).queryByRole("tooltip")).toBeNull(),
    );
    await expect(drawer.matches(":modal")).toBe(true);
    await userEvent.unhover(refresh);
    await userEvent.keyboard("{Escape}");
    await waitFor(() =>
      expect(canvas.queryByRole("dialog")).not.toBeInTheDocument(),
    );
    await expect(toggle).toHaveFocus();
    await expect(analysis).toBeVisible();

    await userEvent.click(toggle);
    await expect(
      within(drawer).getByRole("tab", { name: "Attempt 2: Failed" }),
    ).toHaveAttribute("aria-selected", "true");
    fireEvent.click(drawer);
    await waitFor(() =>
      expect(canvas.queryByRole("dialog")).not.toBeInTheDocument(),
    );
    await expect(toggle).toHaveFocus();

    await userEvent.click(toggle);
    await userEvent.click(
      within(drawer).getByRole("button", { name: "Close run history" }),
    );
    await waitFor(() =>
      expect(canvas.queryByRole("dialog")).not.toBeInTheDocument(),
    );
    await expect(toggle).toHaveFocus();
  },
};

export const OpeningWorkbench: Story = {
  render: () =>
    renderSurface(
      workbench({ connected: false, catalogLoading: true, runHistory: [] }),
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent(
      "Opening workbench",
    );
    await expect(
      canvas.queryByRole("button", { name: "Refresh history" }),
    ).not.toBeInTheDocument();
  },
};

export const HostConnectionFailed: Story = {
  render: () =>
    renderSurface(
      workbench({
        connected: false,
        catalogLoading: false,
        pipelines: [],
        error: "Could not open the workbench. The MCP host did not respond.",
      }),
      "workflows",
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("alert")).toHaveTextContent(
      "The MCP host did not respond",
    );
    await expect(
      canvas.queryByText("Opening workbench…"),
    ).not.toBeInTheDocument();
  },
};

export const ReportDetailsDisclosure: Story = {
  parameters: { storyWidth: 1280 },
  render: () => renderSurface(workbench({ analysisRun: completedRun }), "run"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(
      canvas.getByRole("button", { name: "Close run history" }),
    );
    const sources = canvas.getByText("Data sources", { selector: "summary" });
    const methods = canvas.getByText("Methods and provenance", {
      selector: "summary",
    });
    const index = canvas.getByText(/Artifact index \(/, {
      selector: "summary",
    });
    const sourceFile = canvas
      .getByText("analysis_summary.md", { selector: "span" })
      .closest("dd")!;
    await expect(sourceFile).not.toBeVisible();
    await userEvent.click(sources);
    await expect(sourceFile).toBeVisible();
    await waitFor(() =>
      expect(sourceFile.getBoundingClientRect().width).toBeGreaterThan(240),
    );
    const details = canvas.getByRole("complementary", {
      name: "Analysis details",
    });
    const folderHeading = within(details).getByRole("heading", {
      name: "Run folder",
    });
    const folderPath = within(details).getByText(
      completedAnalysis.runDirectory,
      {
        selector: "code",
      },
    );
    const actions = within(details).getByRole("group", {
      name: "Run folder actions",
    });
    const folderButtons = within(actions).getAllByRole("button");
    const note = within(details)
      .getByRole("heading", { name: "Notes" })
      .parentElement!.querySelector("li")!;
    const bodyFontSize = getComputedStyle(note).fontSize;
    for (const element of [
      folderPath,
      sourceFile,
      sourceFile.previousElementSibling!,
      sources,
      ...folderButtons,
    ]) {
      await expect(getComputedStyle(element).fontSize).toBe(bodyFontSize);
    }
    const firstAction = folderButtons[0].getBoundingClientRect();
    const secondAction = folderButtons[1].getBoundingClientRect();
    await expect(firstAction.top).toBe(secondAction.top);
    await expect(firstAction.height).toBe(secondAction.height);
    await expect(actions.getBoundingClientRect().top).toBeGreaterThanOrEqual(
      folderPath.getBoundingClientRect().bottom,
    );
    const disclosureLabel = document.createRange();
    disclosureLabel.selectNodeContents(sources.firstChild!);
    await expect(disclosureLabel.getBoundingClientRect().left).toBe(
      folderHeading.getBoundingClientRect().left,
    );
    await expect(firstAction.left).toBe(
      folderHeading.getBoundingClientRect().left,
    );
    const manifestFilename = canvas.getByText("visualization_manifest.json", {
      selector: "span",
    });
    await expect(
      manifestFilename.getBoundingClientRect().height,
    ).toBeLessThanOrEqual(
      parseFloat(getComputedStyle(manifestFilename).lineHeight) + 1,
    );
    sources.focus();
    await expect(sources).toHaveFocus();
    await userEvent.click(sources);
    await expect(sources.closest("details")).not.toHaveAttribute("open");
    await waitFor(() =>
      expect(
        index.getBoundingClientRect().top -
          methods.getBoundingClientRect().bottom,
      ).toBeLessThanOrEqual(1),
    );
    await userEvent.click(
      canvas.getByRole("button", { name: "Browse run files" }),
    );
    await expect(index.closest("details")).toHaveAttribute("open");
    await expect(
      canvas.getByRole("region", { name: "Review recommended" }),
    ).toBeVisible();
    const copy = canvas.getByRole("button", {
      name: "Copy path for Gene count matrix",
    });
    const copyIcon = copy.querySelector<HTMLElement>(".oai-icon")!;
    const idleIcon = copyIcon.style.getPropertyValue("--oai-icon-source");
    const idleIconBounds = copyIcon.getBoundingClientRect();
    // Synthetic clicks do not grant native clipboard permission in every host.
    const writeText = spyOn(
      navigator.clipboard,
      "writeText",
    ).mockResolvedValue();
    try {
      await userEvent.click(copy);
      await waitFor(() =>
        expect(copy).toHaveAttribute("data-status", "copied"),
      );
      await expect(writeText).toHaveBeenCalledWith(
        `${completedAnalysis.runDirectory}/rnaseq_salmon/matrices/gene_num_reads.tsv`,
      );
      await expect(copy).toHaveTextContent("Copied");
      await expect(
        copyIcon.style.getPropertyValue("--oai-icon-source"),
      ).not.toBe(idleIcon);
      await expect(copyIcon.getBoundingClientRect().width).toBe(16);
      await expect(copyIcon.getBoundingClientRect().height).toBe(16);
      await expect(copyIcon.getBoundingClientRect().width).toBe(
        idleIconBounds.width,
      );
    } finally {
      writeText.mockRestore();
    }
  },
};
