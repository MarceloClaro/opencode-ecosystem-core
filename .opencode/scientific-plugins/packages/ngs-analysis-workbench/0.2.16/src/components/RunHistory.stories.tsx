import type { Meta, StoryObj } from "@storybook/react-vite";

import type { RunSummary } from "../model";
import { RunHistory } from "./RunHistory";

const recoveryRoot = "nextflow-demultiplex-20260820-010000-a114b7";

function recoveryAttempt(
  attempt_number: number,
  status: "failed" | "completed",
  summary: string,
): RunSummary {
  const run_id = attempt_number === 1 ? recoveryRoot : `nextflow-demultiplex-20260820-01${attempt_number}000-${attempt_number}f62c9`;
  const timestamp = Date.UTC(2026, 7, 20, 8, attempt_number * 8);
  return {
    registry_run_id: `registry-demultiplex-${attempt_number}`,
    run_id,
    first_run_id: recoveryRoot,
    attempt_number,
    binding: "nextflow",
    pipeline: "demultiplex",
    workflow: "nf-core/demultiplex",
    status,
    display_name: "10x iSeq dual-index BCL demultiplexing",
    analysis_summary: summary,
    failure_summary: status === "failed" ? summary : undefined,
    revision: attempt_number,
    workflow_revision: "1.7.1",
    profile: "docker",
    target: { target_id: "devbox2", provider: "ngs-analysis-workbench" },
    run_dir: `/workspaces/iseq-demultiplex/ngs_runs/nextflow/demultiplex/${run_id}`,
    pid: status === "completed" ? 39215 : 31100 + attempt_number,
    started_at_ms: timestamp,
    completed_at_ms: timestamp + 5 * 60_000,
    returncode: status === "completed" ? 0 : 1,
    created_at_ms: timestamp - 60_000,
    updated_at_ms: timestamp + 5 * 60_000,
  };
}

const recoveryAttempts = [
  recoveryAttempt(1, "failed", "Native bcl2fastq segfaulted under Apple Silicon emulation; no FASTQs were produced."),
  recoveryAttempt(2, "failed", "BCL2FASTQ requested 72 GB, exceeding devbox2's 62.8 GB available memory."),
  recoveryAttempt(3, "failed", "CheckQC setup exceeded the target's available memory after demultiplexing completed."),
  recoveryAttempt(4, "failed", "Demultiplexing completed, but output publication failed before artifacts were registered."),
  recoveryAttempt(5, "completed", "37,763 read pairs were assigned across 12 samples; 5,192,199 pairs remained undetermined."),
];

const independentFailure: RunSummary = {
  ...recoveryAttempt(1, "failed", "Artifact collection exceeded the 64 MiB transfer limit after workflow completion."),
  registry_run_id: "registry-demultiplex-independent",
  run_id: "nextflow-demultiplex-20260820-021500-c6a39d",
  first_run_id: "nextflow-demultiplex-20260820-021500-c6a39d",
  display_name: "10x iSeq demultiplexing — new analysis",
  created_at_ms: Date.UTC(2026, 7, 20, 9, 15),
  updated_at_ms: Date.UTC(2026, 7, 20, 9, 22),
};

const runningRun: RunSummary = {
  ...recoveryAttempt(1, "completed", "FastQC is running; scientific conclusions remain pending."),
  registry_run_id: "registry-rnaseq-running",
  run_id: "nfcore-rnaseq-20260820-024000-a1b2c3",
  first_run_id: "nfcore-rnaseq-20260820-024000-a1b2c3",
  pipeline: "rnaseq",
  workflow: "nf-core/rnaseq",
  status: "running",
  display_name: "Lung cohort RNA-seq",
  completed_at_ms: null,
  returncode: null,
  created_at_ms: Date.UTC(2026, 7, 20, 9, 40),
  updated_at_ms: Date.UTC(2026, 7, 20, 9, 43),
};

const runs: RunSummary[] = [...recoveryAttempts, independentFailure, runningRun];

const meta = {
  title: "NGS/Components/Run History",
  component: RunHistory,
  args: {
    loading: false,
    onOpenRun: () => undefined,
    onRefresh: () => undefined,
    runs,
  },
} satisfies Meta<typeof RunHistory>;

export default meta;
type Story = StoryObj<typeof meta>;

export const RecentRuns: Story = {};

export const RecoveryOverview: Story = {};

export const Empty: Story = {
  args: { runs: [] },
};

export const Loading: Story = {
  args: { loading: true, runs: [] },
};

export const RunningAndTerminalRunsRemainInHistory: Story = {};

export const Narrow: Story = {
  parameters: { storyWidth: 420 },
};

export const Dark: Story = {
  parameters: { theme: "dark" },
};
