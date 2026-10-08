import { useId } from "react";
import { Icon } from "../design-system/Icon";
import { Chip, StatusChip, type ChipTone } from "../design-system/Chip";
import { DisclosureSummary } from "../design-system/DisclosureSummary";
import { isTerminalRunStatus } from "../runStatus";
import type {
  AttemptCounts,
  ExecutionObservation,
  ExecutionProcess,
} from "../model";
import styles from "./ExecutionObservationPanel.module.css";

interface ExecutionObservationPanelProps {
  compact?: boolean;
  showHeading?: boolean;
  showLatestAttempt?: boolean;
  observation?: ExecutionObservation;
  workflowStatus?: string;
}

const MAX_VISIBLE_ATTEMPTS = 50;

export function ExecutionObservationPanel({
  compact = false,
  showHeading = true,
  showLatestAttempt = true,
  observation,
  workflowStatus,
}: ExecutionObservationPanelProps) {
  const headingId = useId();
  const attemptsId = useId();
  const terminal = isTerminalRunStatus(workflowStatus ?? "");
  const missingEvidence = terminal
    ? "Execution details are unavailable for this attempt."
    : "Waiting for execution evidence from the workflow runtime.";
  if (!observation) {
    // The compact inspector already exposes the terminal status, failures and
    // log disclosure. An empty activity section adds no actionable detail.
    if (compact && terminal) return null;
    return (
      <section
        className={styles.panel}
        data-compact={compact}
        data-show-heading={showHeading}
        aria-labelledby={showHeading ? headingId : undefined}
        aria-label={!showHeading ? "Execution details" : undefined}
      >
        {showHeading ? <ObservationHeading headingId={headingId} /> : null}
        <p className={styles.waiting}>{missingEvidence}</p>
      </section>
    );
  }

  if (!observation.evidence.available) {
    return (
      <section
        className={styles.panel}
        data-compact={compact}
        data-show-heading={showHeading}
        aria-labelledby={showHeading ? headingId : undefined}
        aria-label={!showHeading ? "Execution details" : undefined}
      >
        {showHeading ? <ObservationHeading headingId={headingId} /> : null}
        <p className={styles.waiting}>
          {observation.evidence.reason ?? missingEvidence}
        </p>
      </section>
    );
  }

  const processes = observation.structure.processes;
  const attempts = observation.attempts.slice(-MAX_VISIBLE_ATTEMPTS);
  const latestAttempt = observation.attempts.at(-1);
  const latestProcess =
    latestAttempt?.process_label ||
    latestAttempt?.process ||
    "Waiting for first attempt";
  const finished =
    observation.progress.finished_attempts ??
    finishedAttempts(observation.counts);

  return (
    <section
      className={styles.panel}
      data-compact={compact}
      data-show-heading={showHeading}
      aria-labelledby={showHeading ? headingId : undefined}
      aria-label={!showHeading ? "Execution details" : undefined}
    >
      {showHeading ? <ObservationHeading headingId={headingId} /> : null}

      <dl className={styles.summary}>
        <div>
          <dt>{compact ? "Progress" : "Observed progress"}</dt>
          <dd>
            {observation.progress.determinate &&
            observation.progress.total != null
              ? `${observation.progress.completed} / ${observation.progress.total}`
              : `${finished} finished`}
          </dd>
        </div>
        {showLatestAttempt ? (
          <div>
            <dt>{compact ? "Latest task" : "Latest observed"}</dt>
            <dd title={latestProcess}>{latestProcess}</dd>
          </div>
        ) : null}
        {!compact ? (
          <div>
            <dt>Task attempts</dt>
            <dd>{observation.counts.total}</dd>
          </div>
        ) : null}
      </dl>

      {!compact && processes.length ? (
        <ProcessRail processes={processes} workflowStatus={workflowStatus} />
      ) : !processes.length ? (
        <p className={styles.waiting}>
          The trace exists; no complete task records have been flushed yet.
        </p>
      ) : null}

      {attempts.length && compact ? (
        <details
          className={styles.compactAttempts}
          aria-labelledby={attemptsId}
          open={workflowStatus === "failed" || undefined}
        >
          <DisclosureSummary chevronPosition="end">
            <span id={attemptsId}>Task attempts</span>
            <Chip>{observation.counts.total}</Chip>
          </DisclosureSummary>
          {observation.counts.total > attempts.length ? (
            <p className={styles.waiting}>
              Latest {attempts.length} of {observation.counts.total}
            </p>
          ) : null}
          <ol>
            {attempts.map((attempt) => (
              <li key={attempt.attempt_id}>
                <header>
                  <span className={styles.attemptIdentity}>
                    <strong title={attempt.process}>
                      {attempt.process_label}
                    </strong>
                    {attempt.sample_or_shard ? (
                      <small>{attempt.sample_or_shard}</small>
                    ) : null}
                  </span>
                  <StatusPill state={attempt.state} />
                </header>
                <dl>
                  <div>
                    <dt>Peak memory</dt>
                    <dd>{attempt.peak_rss ?? "—"}</dd>
                  </div>
                  <div>
                    <dt>Duration</dt>
                    <dd>{attempt.duration ?? attempt.realtime ?? "—"}</dd>
                  </div>
                </dl>
              </li>
            ))}
          </ol>
        </details>
      ) : attempts.length ? (
        <div
          className={styles.tableRegion}
          role="region"
          aria-label="Observed task attempts"
          tabIndex={0}
        >
          <div className={styles.tableHeading}>
            <h4>Task attempts</h4>
            {observation.counts.total > attempts.length ? (
              <span>
                Showing latest {attempts.length} of {observation.counts.total}
              </span>
            ) : null}
          </div>
          <table>
            <thead>
              <tr>
                <th scope="col">Process</th>
                <th scope="col">Sample / shard</th>
                <th scope="col">Duration</th>
                <th scope="col">Peak memory</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {attempts.map((attempt) => (
                <tr key={attempt.attempt_id}>
                  <th scope="row" title={attempt.process}>
                    {attempt.process_label}
                  </th>
                  <td title={attempt.sample_or_shard ?? undefined}>
                    {attempt.sample_or_shard ?? "—"}
                  </td>
                  <td>{attempt.duration ?? attempt.realtime ?? "—"}</td>
                  <td>{attempt.peak_rss ?? "—"}</td>
                  <td>
                    <StatusPill state={attempt.state} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      <details className={styles.evidenceDetails}>
        <DisclosureSummary chevronPosition={compact ? "end" : "start"}>
          Execution evidence
        </DisclosureSummary>
        <p>{evidenceLabel(observation)}</p>
        <p>{observation.progress.reason ?? observation.evidence.coverage}</p>
        {observation.evidence.ignored_record_count ? (
          <p>
            {observation.evidence.ignored_record_count} incomplete record
            {observation.evidence.ignored_record_count === 1 ? "" : "s"} ignored
          </p>
        ) : null}
      </details>
    </section>
  );
}

function ObservationHeading({ headingId }: { headingId: string }) {
  return (
    <header className={styles.heading}>
      <h3 id={headingId}>Process activity</h3>
    </header>
  );
}

function ProcessRail({
  processes,
  workflowStatus,
}: {
  processes: ExecutionProcess[];
  workflowStatus?: string;
}) {
  return (
    <ol
      className={styles.rail}
      aria-label="Processes discovered from execution evidence"
    >
      {processes.map((process) => {
        const state = processState(process.counts, workflowStatus);
        return (
          <li data-state={state} key={process.name} title={process.name}>
            <span aria-hidden="true">
              <Icon
                name={
                  state === "completed"
                    ? "check-md"
                    : state === "failed"
                    ? "close-medium"
                    : state === "running"
                    ? "spinner"
                    : "info-sm"
                }
                className={state === "running" ? "ngs-spin" : undefined}
                size={20}
              />
            </span>
            <strong>{process.label}</strong>
          </li>
        );
      })}
    </ol>
  );
}

function StatusPill({ state }: { state: string }) {
  const tone: ChipTone =
    state === "completed" || state === "cached"
      ? "success"
      : state === "failed" || state === "aborted"
      ? "danger"
      : state === "running"
      ? "info"
      : "neutral";
  return (
    <StatusChip tone={tone} active={state === "running"}>
      {humanize(state)}
    </StatusChip>
  );
}

function processState(counts: AttemptCounts, workflowStatus?: string) {
  if (counts.running) return "running";
  if (counts.queued) return "queued";
  if (workflowStatus === "completed" && counts.completed + counts.cached > 0)
    return "completed";
  if (
    ["failed", "canceled", "orphaned"].includes(workflowStatus ?? "") &&
    (counts.failed || counts.aborted)
  )
    return "failed";
  if (
    counts.total &&
    counts.completed + counts.cached === counts.total &&
    workflowStatus &&
    ["completed", "failed", "canceled", "orphaned"].includes(workflowStatus)
  )
    return "completed";
  if (counts.completed || counts.cached) return "observed";
  return "unknown";
}

function finishedAttempts(counts: AttemptCounts) {
  return counts.completed + counts.cached + counts.failed + counts.aborted;
}

function evidenceLabel(observation: ExecutionObservation) {
  if (observation.evidence.kind === "nextflow_trace") return "Nextflow trace";
  if (observation.evidence.kind === "snakemake_native_log")
    return "Snakemake log";
  return observation.evidence.kind.replaceAll("_", " ");
}

function humanize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/^\w/, (character) => character.toUpperCase());
}
