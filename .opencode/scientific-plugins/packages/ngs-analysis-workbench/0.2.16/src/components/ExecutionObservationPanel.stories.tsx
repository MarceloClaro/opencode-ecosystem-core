import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, userEvent, within } from "storybook/test";

import type { ExecutionObservation } from "../model";
import {
  nextflowTraceObservation,
  snakemakeLogObservation,
} from "../fixtures/executionObservation";
import { ExecutionObservationPanel } from "./ExecutionObservationPanel";

const waitingObservation = {
  ...nextflowTraceObservation,
  evidence: {
    ...nextflowTraceObservation.evidence,
    available: false,
    reason: "trace.txt has not been produced yet",
    record_count: null,
  },
  counts: {
    total: 0,
    queued: 0,
    running: 0,
    completed: 0,
    cached: 0,
    failed: 0,
    aborted: 0,
    unknown: 0,
  },
  progress: {
    completed: 0,
    finished_attempts: 0,
    total: null,
    determinate: false,
    reason: "trace.txt has not been produced yet",
  },
  structure: {
    ...nextflowTraceObservation.structure,
    processes: [],
  },
  attempts: [],
} satisfies ExecutionObservation;

const failedObservation = {
  ...snakemakeLogObservation,
  counts: {
    total: 2,
    queued: 0,
    running: 0,
    completed: 1,
    cached: 0,
    failed: 1,
    aborted: 0,
    unknown: 0,
  },
  progress: {
    completed: 1,
    finished_attempts: 2,
    total: 3,
    determinate: true,
  },
  structure: {
    ...snakemakeLogObservation.structure,
    processes: [
      snakemakeLogObservation.structure.processes[0],
      {
        ...snakemakeLogObservation.structure.processes[1],
        counts: {
          total: 1,
          queued: 0,
          running: 0,
          completed: 0,
          cached: 0,
          failed: 1,
          aborted: 0,
          unknown: 0,
        },
      },
    ],
  },
  attempts: [
    snakemakeLogObservation.attempts[0],
    { ...snakemakeLogObservation.attempts[1], state: "failed" },
  ],
} satisfies ExecutionObservation;

const retriedEarlierProcess = {
  ...nextflowTraceObservation,
  counts: {
    ...nextflowTraceObservation.counts,
    total: nextflowTraceObservation.counts.total + 1,
    running: 1,
  },
  progress: {
    ...nextflowTraceObservation.progress,
    finished_attempts: nextflowTraceObservation.counts.total,
  },
  structure: {
    ...nextflowTraceObservation.structure,
    processes: nextflowTraceObservation.structure.processes.map((process) =>
      process.label === "FASTQC"
        ? { ...process, counts: { ...process.counts, total: 2, running: 1 } }
        : process,
    ),
  },
  attempts: [
    ...nextflowTraceObservation.attempts,
    {
      ...nextflowTraceObservation.attempts[1],
      attempt_id: "7",
      attempt_number: 2,
      state: "running",
    },
  ],
} satisfies ExecutionObservation;

const meta = {
  title: "NGS/Components/Execution Observation Panel",
  component: ExecutionObservationPanel,
  args: {
    observation: nextflowTraceObservation,
    workflowStatus: "running",
  },
} satisfies Meta<typeof ExecutionObservationPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NextflowTrace: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const heading = canvas.getByRole("heading", { name: "Task attempts" });
    for (const cell of [
      canvas.getByRole("columnheader", { name: "Process" }),
      ...canvas.getAllByRole("rowheader"),
    ]) {
      const text = document.createRange();
      text.selectNodeContents(cell);
      await expect(
        Math.abs(
          text.getBoundingClientRect().left -
            heading.getBoundingClientRect().left,
        ),
      ).toBeLessThanOrEqual(1);
    }
    const source = canvas.getByText("Nextflow trace", { selector: "p" });
    await expect(source).not.toBeVisible();
    const disclosure = canvas.getByText("Execution evidence", {
      selector: "summary",
    });
    await userEvent.click(disclosure);
    await expect(source).toBeVisible();
    disclosure.focus();
    await expect(disclosure).toHaveFocus();
    await userEvent.click(disclosure);
    await expect(disclosure.closest("details")).not.toHaveAttribute("open");
  },
};

export const SnakemakeLog: Story = {
  args: { observation: snakemakeLogObservation },
};

export const AwaitingFirstObservation: Story = {
  args: { observation: undefined },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByRole("heading", { name: "Process activity" }),
    ).toBeVisible();
    await expect(
      canvas.getByText(
        "Waiting for execution evidence from the workflow runtime.",
      ),
    ).toBeVisible();
    await expect(
      canvas.queryByText("Awaiting evidence"),
    ).not.toBeInTheDocument();
  },
};

export const WaitingForEvidence: Story = {
  args: { observation: waitingObservation },
};

export const FinishedWithoutEvidence: Story = {
  args: { observation: undefined, workflowStatus: "completed" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByRole("heading", { name: "Process activity" }),
    ).toBeVisible();
    await expect(
      canvas.getByText("Execution details are unavailable for this attempt."),
    ).toBeVisible();
    await expect(
      canvas.queryByText(/Waiting for execution evidence/),
    ).toBeNull();
  },
};

export const FailedAttempt: Story = {
  args: { observation: failedObservation, workflowStatus: "failed" },
};

export const RetriedEarlierProcessIsLatest: Story = {
  args: { observation: retriedEarlierProcess },
};

export const Narrow: Story = {
  args: { observation: snakemakeLogObservation },
  parameters: { storyWidth: 420 },
};

export const Dark: Story = {
  parameters: { theme: "dark" },
};
