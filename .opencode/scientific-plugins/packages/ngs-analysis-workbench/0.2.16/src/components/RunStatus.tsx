import { useId } from "react";
import { DisclosureSummary } from "../design-system/DisclosureSummary";
import { Icon } from "../design-system/Icon";
import { StatusChip } from "../design-system/Chip";
import { TooltipIconButton } from "../design-system/TooltipIconButton";
import type { RunDetail, RunObservation, RunSummary } from "../model";
import {
  isActiveRunStatus,
  isTerminalRunStatus,
  runStatusPresentation,
} from "../runStatus";
import { ExecutionObservationPanel } from "./ExecutionObservationPanel";
import ui from "../styles/ui.module.css";
import styles from "./RunStatus.module.css";

interface RunStatusProps {
  run: RunDetail;
  observation?: RunObservation;
  summary?: RunSummary;
  busy: boolean;
  compact?: boolean;
  showExecution?: boolean;
  onRefresh?: () => void;
}

export function RunStatus({
  run,
  observation,
  summary,
  busy,
  compact = false,
  showExecution = true,
  onRefresh,
}: RunStatusProps) {
  const headingId = useId();
  const failureId = useId();
  const current = observation ?? run;
  const status = runStatusPresentation(current.status);
  const terminal = isTerminalRunStatus(current.status);
  const timing =
    terminal && summary?.completed_at_ms
      ? { label: "Finished", timestamp: summary.completed_at_ms }
      : summary?.started_at_ms
      ? { label: "Started", timestamp: summary.started_at_ms }
      : undefined;
  const refreshButton = !onRefresh ? null : compact ? (
    <TooltipIconButton
      label="Refresh status"
      icon="regenerate"
      busy={busy}
      onClick={onRefresh}
    />
  ) : (
    <button
      className={`${ui.button} ${ui.buttonSecondary}`}
      disabled={busy}
      aria-busy={busy}
      onClick={onRefresh}
      type="button"
    >
      {busy ? <Icon name="spinner" className="ngs-spin" size={16} /> : null}
      Refresh status
    </button>
  );

  return (
    <section
      className={styles.runStatus}
      data-compact={compact}
      aria-labelledby={headingId}
    >
      {compact ? (
        <>
          <div className={styles.heading}>
            <h3 id={headingId}>Attempt status</h3>
            {refreshButton}
          </div>
          <dl className={styles.statusSummary}>
            <div>
              <dt>Status</dt>
              <dd>
                <StatusChip
                  tone={status.tone}
                  active={isActiveRunStatus(current.status)}
                >
                  {status.label}
                </StatusChip>
              </dd>
            </div>
            {timing ? (
              <div>
                <dt>{timing.label}</dt>
                <dd>
                  <time dateTime={new Date(timing.timestamp).toISOString()}>
                    {formatTimestamp(timing.timestamp)}
                  </time>
                </dd>
              </div>
            ) : null}
          </dl>
        </>
      ) : (
        <div className={styles.heading}>
          <div>
            <h2 id={headingId}>
              {summary
                ? `Attempt ${summary.attempt_number}`
                : run.pipeline.title}
            </h2>
          </div>
          <StatusChip
            tone={status.tone}
            active={isActiveRunStatus(current.status)}
          >
            {status.label}
          </StatusChip>
        </div>
      )}

      {[...run.warnings, ...(observation?.warnings ?? [])].length ? (
        <div className={styles.warningList}>
          {[...run.warnings, ...(observation?.warnings ?? [])].map(
            (warning) => (
              <p key={warning}>{warning}</p>
            ),
          )}
        </div>
      ) : null}

      {current.failure_summary ? (
        <section className={styles.failureReason} aria-labelledby={failureId}>
          <h3 id={failureId}>Recorded failure</h3>
          <p>{current.failure_summary}</p>
        </section>
      ) : null}

      {showExecution ? (
        <ExecutionObservationPanel
          compact={compact}
          showHeading={!compact}
          showLatestAttempt={!compact || current.status !== "completed"}
          observation={observation?.execution}
          workflowStatus={current.status}
        />
      ) : null}

      <details className={styles.technicalDetails}>
        <DisclosureSummary chevronPosition="end">
          Run metadata
        </DisclosureSummary>
        <dl className={styles.runFacts}>
          <div>
            <dt>Run ID</dt>
            <dd>
              <code>{run.run_id}</code>
            </dd>
          </div>
          {summary ? (
            <div>
              <dt>Attempt</dt>
              <dd>{summary.attempt_number}</dd>
            </div>
          ) : null}
          <div>
            <dt>Workflow</dt>
            <dd>
              <code>{run.pipeline.workflow}</code>
            </dd>
          </div>
          {summary?.workflow_revision ? (
            <div>
              <dt>Workflow version</dt>
              <dd>{summary.workflow_revision}</dd>
            </div>
          ) : null}
          {summary?.profile ? (
            <div>
              <dt>Profile</dt>
              <dd>{summary.profile}</dd>
            </div>
          ) : null}
          {run.target ? (
            <div>
              <dt>Compute target</dt>
              <dd>
                <code>{run.target.target_id}</code>
              </dd>
            </div>
          ) : null}
          {summary?.started_at_ms ? (
            <div>
              <dt>Started</dt>
              <dd>
                <time dateTime={new Date(summary.started_at_ms).toISOString()}>
                  {formatTimestamp(summary.started_at_ms)}
                </time>
              </dd>
            </div>
          ) : null}
          {summary?.completed_at_ms ? (
            <div>
              <dt>Finished</dt>
              <dd>
                <time
                  dateTime={new Date(summary.completed_at_ms).toISOString()}
                >
                  {formatTimestamp(summary.completed_at_ms)}
                </time>
              </dd>
            </div>
          ) : null}
          {current.pid ? (
            <div>
              <dt>PID</dt>
              <dd>{current.pid}</dd>
            </div>
          ) : null}
          {current.returncode != null ? (
            <div>
              <dt>Return code</dt>
              <dd>{current.returncode}</dd>
            </div>
          ) : null}
          {run.run_dir ? (
            <div>
              <dt>Run directory</dt>
              <dd>
                <code>{run.run_dir}</code>
              </dd>
            </div>
          ) : null}
        </dl>
      </details>

      <details className={styles.technicalDetails}>
        <DisclosureSummary chevronPosition="end">
          Recorded command
        </DisclosureSummary>
        <code>{run.command_argv.join(" ")}</code>
      </details>

      <details className={styles.technicalDetails}>
        <DisclosureSummary chevronPosition="end">
          Execution log tail
        </DisclosureSummary>
        <pre>
          {observation?.log_tail || "No verified execution log is available."}
        </pre>
      </details>

      {!compact && refreshButton ? (
        <div className={styles.statusActions}>{refreshButton}</div>
      ) : null}
    </section>
  );
}

function formatTimestamp(value: number) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}
