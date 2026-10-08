import { Icon, StatusIcon } from "../design-system/Icon";
import { Chip, StatusChip } from "../design-system/Chip";
import { useMemo } from "react";

import { plainTextAnalysisSummary } from "../analysisSummary";
import type { RunSummary } from "../model";
import {
  isActiveRunStatus,
  runStatusPresentation,
  type RunStatusPresentation,
} from "../runStatus";
import ui from "../styles/ui.module.css";
import styles from "./RunHistory.module.css";

interface RunHistoryProps {
  loading: boolean;
  onOpenRun: (run: RunSummary) => void;
  onRefresh: () => void;
  runs: RunSummary[];
}

export interface RunLineage {
  id: string;
  latest: RunSummary;
  runs: RunSummary[];
}

export function groupRunLineages(runs: RunSummary[]): RunLineage[] {
  const grouped = new Map<string, RunSummary[]>();
  for (const run of runs) {
    const id = run.first_run_id;
    grouped.set(id, [...(grouped.get(id) ?? []), run]);
  }
  return [...grouped.entries()]
    .map(([id, seriesRuns]) => {
      const ordered = [...seriesRuns].sort(
        (left, right) => left.attempt_number - right.attempt_number,
      );
      return { id, latest: ordered.at(-1)!, runs: ordered };
    })
    .sort(
      (left, right) =>
        runCreationTimestamp(right.latest) - runCreationTimestamp(left.latest),
    );
}

export function RunHistory({
  loading,
  onOpenRun,
  onRefresh,
  runs,
}: RunHistoryProps) {
  const series = useMemo(() => groupRunLineages(runs), [runs]);

  return (
    <section className={styles.root} aria-labelledby="run-history-heading">
      <div className={ui.pageHeader}>
        <h2 className={ui.pageTitle} id="run-history-heading">
          Runs
        </h2>
        <button
          className={`${ui.button} ${ui.buttonSecondary}`}
          disabled={loading}
          onClick={onRefresh}
          type="button"
        >
          {loading ? (
            <Icon name="spinner" className="ngs-spin" size={16} />
          ) : null}
          {loading ? "Refreshing…" : "Refresh history"}
        </button>
      </div>

      {series.length ? (
        <section aria-label="Recent analyses">
          <ol className={styles.list}>
            {series.map((item) => {
              const run = item.latest;
              return (
                <li key={item.id}>
                  <button
                    className={`${styles.row} ${styles.runButton}`}
                    disabled={loading}
                    onClick={() => onOpenRun(run)}
                    type="button"
                  >
                    <Status presentation={runStatusPresentation(run.status)} />
                    <span className={styles.historyIdentity}>
                      <strong>{run.display_name ?? run.workflow}</strong>
                      {run.analysis_summary ? (
                        <span className={styles.historySummary}>
                          {plainTextAnalysisSummary(run.analysis_summary)}
                        </span>
                      ) : null}
                      <code title={run.run_id}>{run.run_id}</code>
                    </span>
                    <RunTrace series={item} />
                    <Chip className={styles.binding}>
                      {bindingLabel(run.binding)}
                    </Chip>
                    <time dateTime={runTimeIso(run)}>{formatRunTime(run)}</time>
                  </button>
                </li>
              );
            })}
          </ol>
        </section>
      ) : (
        <p className={styles.empty} role={loading ? "status" : undefined}>
          {loading ? "Loading run history…" : "No runs yet."}
        </p>
      )}
    </section>
  );
}

function RunTrace({ series }: { series: RunLineage }) {
  const visibleRuns = series.runs.slice(-6);
  const countLabel = `${series.latest.attempt_number} workflow ${
    series.latest.attempt_number === 1 ? "attempt" : "attempts"
  }`;
  const historyLabel = series.runs
    .map(
      (run) =>
        `${run.attempt_number} ${runStatusPresentation(run.status).label}`,
    )
    .join(", ");
  return (
    <span
      className={styles.trace}
      aria-label={`${countLabel}: ${historyLabel}`}
    >
      <span className={styles.traceMarks} aria-hidden="true">
        {visibleRuns.map((run) => {
          const presentation = runStatusPresentation(run.status);
          return (
            <i key={run.registry_run_id} data-tone={presentation.tone}>
              <StatusIcon
                tone={presentation.tone}
                active={isActiveRunStatus(presentation.status)}
                size={14}
              />
            </i>
          );
        })}
      </span>
      <span>{countLabel}</span>
    </span>
  );
}

function Status({ presentation }: { presentation: RunStatusPresentation }) {
  return (
    <StatusChip
      className={styles.status}
      tone={presentation.tone}
      active={isActiveRunStatus(presentation.status)}
    >
      {presentation.label}
    </StatusChip>
  );
}

function bindingLabel(binding: string) {
  return humanize(binding);
}
function runTimestamp(run: RunSummary) {
  return (
    run.updated_at_ms ??
    run.completed_at_ms ??
    run.started_at_ms ??
    run.created_at_ms ??
    0
  );
}
function runCreationTimestamp(run: RunSummary) {
  return run.created_at_ms ?? run.started_at_ms ?? run.completed_at_ms ?? 0;
}
function runTimeIso(run: RunSummary) {
  const value = runTimestamp(run);
  return value ? new Date(value).toISOString() : "";
}
function formatRunTime(run: RunSummary) {
  const value = runTimestamp(run);
  return value ? formatTimestamp(value) : "Time unavailable";
}
function formatTimestamp(value: number) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}
function humanize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}
