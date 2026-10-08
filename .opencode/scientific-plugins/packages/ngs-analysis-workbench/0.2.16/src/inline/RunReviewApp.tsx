import { Icon } from "../design-system/Icon";
import { StatusChip, type ChipTone } from "../design-system/Chip";
import { DisclosureSummary } from "../design-system/DisclosureSummary";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  InlineMcpClient,
  isRecord,
  type InlineSnapshot,
  type ToolPayload,
} from "./client";
import { ExecutionObservationPanel } from "../components/ExecutionObservationPanel";
import {
  mergeRunObservation,
  parseExecutionFailure,
  parsePlan,
  parseStartedRun,
  payloadErrors,
  type ReviewExecutionFailure,
  type ReviewPlan,
  type ReviewRuntimeCommand,
  type ReviewRun,
} from "./types";
import { isTerminalRunStatus } from "../runStatus";
import styles from "./RunReviewApp.module.css";

const STATUS_POLL_INTERVAL_MS = 2500;

export type RunReviewSurfaceProps =
  | { state: "loading" }
  | { state: "error"; message: string; payload?: ToolPayload }
  | { state: "blocked"; failure: ReviewExecutionFailure; payload?: ToolPayload }
  | {
      state: "plan";
      plan: ReviewPlan;
      error?: string;
    }
  | {
      state: "run";
      run: ReviewRun;
      refreshing: boolean;
      error?: string;
      onRefresh: () => void;
    };

export function RunReviewApp() {
  const client = useMemo(() => new InlineMcpClient(), []);
  const [snapshot, setSnapshot] = useState<InlineSnapshot>({});
  const [refreshedRun, setRefreshedRun] = useState<ReviewRun>();
  const [manualRefreshInFlight, setManualRefreshInFlight] = useState(false);
  const [actionError, setActionError] = useState<string>();
  const refreshInFlight = useRef(false);

  useEffect(() => {
    const unsubscribe = client.subscribe(setSnapshot);
    void client.connect().catch((error: unknown) => {
      setActionError(
        error instanceof Error
          ? error.message
          : "Could not connect the run review app.",
      );
    });
    return unsubscribe;
  }, [client]);

  const plan = useMemo(
    () => (snapshot.payload ? parsePlan(snapshot.payload) : undefined),
    [snapshot.payload],
  );
  const initialRun = useMemo(
    () =>
      snapshot.payload && !plan
        ? parseStartedRun(snapshot.payload, snapshot.input)
        : undefined,
    [plan, snapshot.input, snapshot.payload],
  );
  const run =
    refreshedRun?.registryRunId === initialRun?.registryRunId
      ? refreshedRun
      : initialRun;

  useEffect(() => {
    if (!run || isTerminalRunStatus(run.status)) return;
    void refreshRun(false);
    const timer = window.setInterval(
      () => void refreshRun(false),
      STATUS_POLL_INTERVAL_MS,
    );
    return () => window.clearInterval(timer);
  }, [client, run?.registryRunId, run?.status]);

  async function refreshRun(showBusy = true) {
    const runToRefresh = run;
    if (!runToRefresh || refreshInFlight.current) return;
    refreshInFlight.current = true;
    if (showBusy) setManualRefreshInFlight(true);
    try {
      const payload = await client.call("observe_ngs_run", {
        registry_run_id: runToRefresh.registryRunId,
      });
      setRefreshedRun((current) =>
        mergeRunObservation(
          current?.registryRunId === runToRefresh.registryRunId
            ? current
            : runToRefresh,
          payload,
        ),
      );
      setActionError(undefined);
    } catch (error: unknown) {
      setActionError(errorMessage(error));
    } finally {
      refreshInFlight.current = false;
      if (showBusy) setManualRefreshInFlight(false);
    }
  }

  const error = actionError ?? snapshot.error ?? snapshot.cancelled;

  if (!snapshot.payload && !error) return <RunReviewSurface state="loading" />;
  if (plan) {
    return <RunReviewSurface state="plan" plan={plan} error={error} />;
  }
  if (run) {
    return (
      <RunReviewSurface
        state="run"
        run={run}
        refreshing={manualRefreshInFlight}
        error={error}
        onRefresh={() => void refreshRun()}
      />
    );
  }
  const executionFailure = snapshot.payload
    ? parseExecutionFailure(snapshot.payload)
    : undefined;
  if (executionFailure) {
    return (
      <RunReviewSurface
        state="blocked"
        failure={executionFailure}
        payload={snapshot.payload}
      />
    );
  }
  return (
    <RunReviewSurface
      state="error"
      message={
        error ??
        payloadErrors(
          snapshot.payload ?? {},
          "The execution response was incomplete.",
        )
      }
      payload={snapshot.payload}
    />
  );
}

export function RunReviewSurface(props: RunReviewSurfaceProps) {
  if (props.state === "loading") return <LoadingCard />;
  if (props.state === "error")
    return <ErrorCard message={props.message} payload={props.payload} />;
  if (props.state === "blocked") {
    return (
      <ErrorCard
        message={props.failure.message}
        recovery={props.failure.recovery}
        payload={props.payload}
        title="Execution blocked"
        status="Blocked"
      />
    );
  }
  if (props.state === "plan") {
    return <PlanCard plan={props.plan} error={props.error} />;
  }
  return (
    <RunCard
      run={props.run}
      refreshing={props.refreshing}
      error={props.error}
      onRefresh={props.onRefresh}
    />
  );
}

function PlanCard({ plan, error }: { plan: ReviewPlan; error?: string }) {
  const requestLabel =
    stringValue(plan.request.display_name) ||
    stringValue(plan.request.workflow) ||
    stringValue(plan.request.pipeline);
  const sample = inputSummary(plan);

  return (
    <article
      className={`ngs-theme ${styles.card}`}
      data-tone={plan.runnable ? "ready" : "blocked"}
    >
      <Header
        eyebrow="Read-only immutable plan"
        title={plan.planName}
        status={plan.runnable ? "Ready for authorization" : "Blocked"}
        tone={plan.runnable ? "ready" : "blocked"}
      />

      <section
        className={styles.decisionSummary}
        aria-label="Execution plan summary"
      >
        <strong title={requestLabel}>{requestLabel}</strong>
        <span>
          {plan.binding === "nextflow"
            ? `${
                stringValue(plan.request.workflow).startsWith("nf-core/")
                  ? "Nextflow / nf-core"
                  : "Nextflow"
              } · ${plan.request.target.target_id}`
            : `Snakemake · ${plan.request.target.target_id}`}
        </span>
        <dl className={styles.decisionFacts}>
          <Fact label="Inputs" value={sample} />
          <Fact label="Output" value={plan.effects.outputDir} />
          <Fact label="Plan ID" value={plan.planId} />
          <Fact label="Checksum" value={plan.planChecksum} />
        </dl>
      </section>

      {plan.blockers.length ? (
        <MessageList
          tone="danger"
          title="Start is blocked"
          items={plan.blockers}
        />
      ) : null}
      {plan.warnings.length ? (
        <MessageList
          tone="warning"
          title="Review notes"
          items={plan.warnings}
        />
      ) : null}
      {error ? <InlineError message={error} /> : null}

      <div className={styles.reviewLedger}>
        {plan.preparation ? (
          <ReviewDisclosure
            title="Preparation"
            summary={preparationSummary(plan)}
          >
            <DetailBlock title="Preparation effects">
              <CodeLine
                label="Destination"
                value={plan.preparation.destinationDir}
              />
              <CodeLine
                label="Downloaded"
                value={humanBytes(plan.preparation.downloadBytes)}
              />
              <CodeLine
                label="Files"
                value={String(plan.preparation.operations.length)}
              />
            </DetailBlock>
            <DetailBlock title="Verified downloads and generated files">
              {plan.preparation.operations.map((operation) => (
                <div key={operation.path}>
                  <CodeLine
                    label={
                      operation.operation === "download_verified_file"
                        ? "Download"
                        : "Generate"
                    }
                    value={operation.path}
                  />
                  {operation.role ? (
                    <CodeLine label="Role" value={operation.role} />
                  ) : null}
                  {operation.url ? (
                    <CodeLine label="Source" value={operation.url} />
                  ) : null}
                  <CodeLine label="Size" value={humanBytes(operation.bytes)} />
                  <CodeLine label="SHA-256" value={operation.sha256} />
                </div>
              ))}
            </DetailBlock>
          </ReviewDisclosure>
        ) : null}
        <ReviewDisclosure title="Input details" summary={sample}>
          <DetailBlock title="Reviewed request">
            {inputDetailRows(plan).map((row) => (
              <CodeLine
                key={row.label}
                label={row.label}
                value={row.value}
                missing={row.missing}
              />
            ))}
          </DetailBlock>
        </ReviewDisclosure>

        <ReviewDisclosure
          title="Runtime details"
          summary={runtimeSummary(plan)}
        >
          <DetailBlock title="Execution environment">
            <CodeLine
              label="Status"
              value={plan.readiness.ok ? "Ready" : "Blocked"}
              missing={!plan.readiness.ok}
            />
            <CodeLine
              label="Compute target"
              value={`${plan.request.target.target_id} · ${plan.request.target.provider}`}
            />
            <CodeLine
              label="Probe"
              value={plan.readiness.scope || "Not reported"}
              missing={!plan.readiness.scope}
            />
            {plan.readiness.snapshotId ? (
              <CodeLine label="Snapshot" value={plan.readiness.snapshotId} />
            ) : null}
            {plan.readiness.host ? (
              <CodeLine
                label="Host"
                value={`${plan.readiness.host.os} / ${plan.readiness.host.arch}`}
              />
            ) : null}
          </DetailBlock>
          <DetailBlock title="Executables">
            {plan.readiness.commands.length ? (
              plan.readiness.commands.map((command) => (
                <CodeLine
                  key={command.name}
                  label={command.name}
                  value={runtimeCommandValue(command)}
                  missing={
                    !command.path ||
                    command.state === "missing" ||
                    command.state === "broken"
                  }
                />
              ))
            ) : (
              <p className={styles.empty}>
                No executable details were reported.
              </p>
            )}
          </DetailBlock>
          {plan.readiness.docker ? (
            <DetailBlock title="Docker daemon">
              <CodeLine
                label="Daemon"
                value={
                  plan.readiness.docker.daemonReachable
                    ? "Reachable"
                    : "Unavailable"
                }
                missing={!plan.readiness.docker.daemonReachable}
              />
              {plan.readiness.docker.path ? (
                <CodeLine label="CLI" value={plan.readiness.docker.path} />
              ) : null}
              {plan.readiness.docker.context ? (
                <CodeLine
                  label="Context"
                  value={plan.readiness.docker.context}
                />
              ) : null}
              {plan.readiness.docker.endpoint ? (
                <CodeLine
                  label="Endpoint"
                  value={plan.readiness.docker.endpoint}
                  missing={plan.readiness.docker.endpointIsLocal === false}
                />
              ) : null}
              {dockerServerSummary(plan) ? (
                <CodeLine label="Server" value={dockerServerSummary(plan)} />
              ) : null}
              {plan.readiness.docker.message ? (
                <CodeLine label="Note" value={plan.readiness.docker.message} />
              ) : null}
            </DetailBlock>
          ) : null}
          {plan.readiness.blockers.length ? (
            <DetailBlock title="Runtime blockers">
              <TextList items={plan.readiness.blockers} />
            </DetailBlock>
          ) : null}
          {plan.readiness.warnings.length ? (
            <DetailBlock title="Runtime notes">
              <TextList items={plan.readiness.warnings} />
            </DetailBlock>
          ) : null}
        </ReviewDisclosure>

        <ReviewDisclosure
          title="Execution details"
          summary={`${
            plan.effects.localWrites.length +
            (plan.effects.remoteWrites?.length ?? 0)
          } writes · ${plan.effects.downloads.length} downloads`}
        >
          <DetailBlock title="Plan identity">
            <CodeLine label="Plan name" value={plan.planName} />
            <CodeLine label="Plan ID" value={plan.planId} />
            <CodeLine label="Checksum" value={plan.planChecksum} />
          </DetailBlock>
          <DetailBlock title="Exact command">
            <pre>{formatCommand(plan.command)}</pre>
          </DetailBlock>
          <DetailBlock title="Normalized request">
            <pre>{JSON.stringify(plan.request, null, 2)}</pre>
          </DetailBlock>
          <DetailBlock title="Declared local writes">
            <PathList
              items={plan.effects.localWrites}
              empty="No local writes declared."
            />
          </DetailBlock>
          {plan.effects.remoteWrites?.length ? (
            <DetailBlock title="Declared remote writes">
              <PathList
                items={plan.effects.remoteWrites}
                empty="No remote writes declared."
              />
            </DetailBlock>
          ) : null}
          <DetailBlock title="Downloads and network">
            <PathList
              items={[...plan.effects.downloads, ...plan.effects.networkAccess]}
              empty="No downloads or network access declared."
            />
          </DetailBlock>
          <DetailBlock title="Monitoring">
            <pre>{JSON.stringify(plan.monitoring, null, 2)}</pre>
          </DetailBlock>
        </ReviewDisclosure>
      </div>

      <footer className={styles.noticeBar}>
        <strong>
          Read-only · This view cannot authorize or start execution.
        </strong>
        <p>
          {plan.runnable
            ? "Next, the agent requests execute_plan with this plan name, ID, and checksum; Codex presents one native approval."
            : "Resolve the blockers, then ask the agent to create a new immutable plan."}
        </p>
      </footer>
    </article>
  );
}

function RunCard({
  run,
  refreshing,
  error,
  onRefresh,
}: {
  run: ReviewRun;
  refreshing: boolean;
  error?: string;
  onRefresh: () => void;
}) {
  return (
    <article
      className={`ngs-theme ${styles.card}`}
      data-tone={statusTone(run.status)}
    >
      <Header
        title={
          run.displayName ??
          run.workflow ??
          (run.binding === "nextflow" ? "Nextflow run" : "Snakemake run")
        }
        status={humanize(run.status)}
        tone={statusTone(run.status)}
      />
      <section
        className={styles.decisionSummary}
        aria-label="Run status summary"
      >
        <strong>{humanize(run.status)}</strong>
        <code title={run.runId}>{run.runId}</code>
        <dl className={styles.decisionFacts}>
          {run.target ? (
            <Fact label="Compute target" value={run.target.target_id} />
          ) : null}
          <Fact
            label="Latest"
            value={
              run.logTail === null
                ? "Execution log unavailable"
                : lastLogLine(run.logTail) || "Waiting for process output"
            }
          />
          {run.returncode != null ? (
            <Fact label="Return code" value={String(run.returncode)} />
          ) : null}
        </dl>
      </section>

      {run.warnings.length ? (
        <MessageList tone="warning" title="Run notes" items={run.warnings} />
      ) : null}
      {run.failureSummary ? (
        <MessageList
          tone="danger"
          title="Recorded failure"
          items={[run.failureSummary]}
        />
      ) : null}
      {error ? <InlineError message={error} /> : null}

      <div className={styles.executionPanel}>
        <ExecutionObservationPanel
          observation={run.execution}
          workflowStatus={run.status}
        />
      </div>

      <details className={styles.details}>
        <DisclosureSummary>Live execution record</DisclosureSummary>
        <div className={styles.detailGrid}>
          <DetailBlock title="Process record">
            <CodeLine label="Registry ID" value={run.registryRunId} />
            <CodeLine
              label="PID"
              value={run.pid ? String(run.pid) : "Not recorded"}
            />
            {run.runDir ? (
              <CodeLine label="Run directory" value={run.runDir} />
            ) : null}
          </DetailBlock>
          {run.command.length ? (
            <DetailBlock title="Approved command">
              <pre>{formatCommand(run.command)}</pre>
            </DetailBlock>
          ) : null}
          <DetailBlock title="Log tail">
            <pre>
              {run.logTail === null
                ? "Execution log unavailable."
                : run.logTail || "No log output yet."}
            </pre>
          </DetailBlock>
        </div>
      </details>

      <footer className={styles.runActions}>
        <div>
          <strong>
            {isTerminalRunStatus(run.status)
              ? "Execution receipt"
              : "Live execution receipt"}
          </strong>
          <p aria-live="polite">
            {refreshing
              ? "Refreshing status, logs, and process evidence…"
              : isTerminalRunStatus(run.status)
              ? "Open NGS Analysis Workbench to inspect results, logs, and provenance."
              : "Status, logs, and process evidence refresh automatically. Open NGS Analysis Workbench for full details."}
          </p>
        </div>
        <button
          className={styles.secondaryButton}
          type="button"
          onClick={onRefresh}
          disabled={refreshing}
        >
          {refreshing ? (
            <>
              <Spinner />
              Refreshing…
            </>
          ) : (
            "Refresh"
          )}
        </button>
      </footer>
    </article>
  );
}

function Header({
  eyebrow,
  title,
  status,
  tone,
}: {
  eyebrow?: string;
  title: string;
  status: string;
  tone: string;
}) {
  const chipTone: ChipTone =
    tone === "complete"
      ? "success"
      : tone === "failed" || tone === "blocked"
      ? "danger"
      : tone === "warning" || tone === "neutral"
      ? tone
      : "info";
  return (
    <header className={styles.header}>
      <div className={styles.titleGroup}>
        <div>
          {eyebrow ? <p>{eyebrow}</p> : null}
          <h1>{title}</h1>
        </div>
      </div>
      <StatusChip
        tone={chipTone}
        active={status === "Running" || status === "Starting"}
      >
        {status}
      </StatusChip>
    </header>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.fact}>
      <dt>{label}</dt>
      <dd title={value}>{value || "—"}</dd>
    </div>
  );
}

function MessageList({
  tone,
  title,
  items,
}: {
  tone: "danger" | "warning";
  title: string;
  items: string[];
}) {
  return (
    <section
      className={styles.message}
      data-tone={tone}
      role={tone === "danger" ? "alert" : undefined}
    >
      <strong>{title}</strong>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

function InlineError({ message }: { message: string }) {
  return (
    <section className={styles.message} data-tone="danger" role="alert">
      <strong>Action failed</strong>
      <pre>{message}</pre>
    </section>
  );
}

function DetailBlock({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className={styles.detailBlock}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function ReviewDisclosure({
  title,
  summary,
  children,
}: {
  title: string;
  summary: string;
  children: React.ReactNode;
}) {
  return (
    <details className={styles.reviewDisclosure}>
      <DisclosureSummary>
        <span>{title}</span>
        <small title={summary}>{summary}</small>
      </DisclosureSummary>
      <div className={styles.detailGrid}>{children}</div>
    </details>
  );
}

function CodeLine({
  label,
  value,
  missing = false,
}: {
  label: string;
  value: string;
  missing?: boolean;
}) {
  return (
    <div className={styles.codeLine}>
      <span>{label}</span>
      <code data-missing={missing}>{value}</code>
    </div>
  );
}

function PathList({ items, empty }: { items: string[]; empty: string }) {
  return items.length ? (
    <ul className={styles.pathList}>
      {items.map((item) => (
        <li key={item}>
          <code>{item}</code>
        </li>
      ))}
    </ul>
  ) : (
    <p className={styles.empty}>{empty}</p>
  );
}

function TextList({ items }: { items: string[] }) {
  return (
    <ul className={styles.detailList}>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function LoadingCard() {
  return (
    <article
      className={`ngs-theme ${styles.card} ${styles.loading}`}
      role="status"
    >
      <div className={styles.loadingLine}>
        <Spinner />
        <div>
          <strong>Waiting for the plan response…</strong>
        </div>
      </div>
    </article>
  );
}

function ErrorCard({
  message,
  payload,
  recovery,
  title = "Could not render this response",
  status = "Error",
}: {
  message: string;
  payload?: ToolPayload;
  recovery?: string;
  title?: string;
  status?: string;
}) {
  return (
    <article className={`ngs-theme ${styles.card}`} data-tone="failed">
      <Header title={title} status={status} tone="failed" />
      <InlineError message={recovery ? `${message}\n\n${recovery}` : message} />
      {payload && isRecord(payload) ? (
        <details className={styles.details}>
          <DisclosureSummary>Raw response</DisclosureSummary>
          <pre>{JSON.stringify(payload, null, 2)}</pre>
        </details>
      ) : null}
    </article>
  );
}

function Spinner() {
  return <Icon name="spinner" className="ngs-spin" size={16} />;
}

function lastLogLine(logTail: string | null) {
  return logTail?.trim().split("\n").at(-1) ?? "";
}

function formatCommand(command: string[]) {
  return command
    .map((part) => (/\s/.test(part) ? JSON.stringify(part) : part))
    .join(" ");
}

function inputSummary(plan: ReviewPlan) {
  const sampleSheet = stringValue(plan.request.sample_sheet);
  if (sampleSheet) return fileName(sampleSheet);
  const configFile = stringValue(plan.request.config_file);
  if (configFile) return fileName(configFile);
  const read1 = stringValue(plan.request.r1);
  const read2 = stringValue(plan.request.r2);
  if (read1 && read2) return "Paired FASTQ files";
  if (read1) return fileName(read1);
  const profile = stringValue(plan.request.profile);
  if (
    profile.split(",").some((token) => token.trim().toLowerCase() === "test")
  ) {
    return "Workflow-provided test data";
  }
  return "Workflow-owned configuration";
}

function preparationSummary(plan: ReviewPlan) {
  const preparation = plan.preparation;
  if (!preparation) return "No preparation";
  const downloads = preparation.operations.filter(
    (operation) => operation.operation === "download_verified_file",
  ).length;
  const generated = preparation.operations.length - downloads;
  return `${downloads} download${downloads === 1 ? "" : "s"} · ${humanBytes(
    preparation.downloadBytes,
  )} · ${generated} generated file${generated === 1 ? "" : "s"}`;
}

function inputDetailRows(plan: ReviewPlan) {
  const labels: Record<string, string> = {
    display_name: "Run name",
    pipeline: "Pipeline",
    workflow: "Workflow",
    profile: "Profile",
    revision: "Revision",
    sample_sheet: "Sample sheet",
    sample_sheet_sha256: "Sample SHA-256",
    config_file: "Config file",
    config_sha256: "Config SHA-256",
    workflow_sha256: "Workflow SHA-256",
    params_file: "Parameters file",
    params_file_sha256: "Parameters SHA-256",
    r1: "Read 1",
    r2: "Read 2",
    trim: "Trimming",
    cores: "CPU cores",
    run_dir: "Run directory",
    run_id: "Run ID",
    runtime_snapshot_id: "Runtime snapshot",
  };
  const orderedKeys = Object.keys(labels);
  const extraKeys = Object.keys(plan.request).filter(
    (key) => !orderedKeys.includes(key),
  );
  return [
    { label: "Data source", value: inputSummary(plan), missing: false },
    ...[...orderedKeys, ...extraKeys]
      .filter((key) => key in plan.request)
      .map((key) => ({
        label: labels[key] ?? humanize(key),
        value: detailValue(plan.request[key]),
        missing: false,
      })),
  ];
}

function runtimeSummary(plan: ReviewPlan) {
  if (!plan.readiness.ok) return "Blocked";
  if (plan.readiness.host)
    return `Ready · ${plan.readiness.host.os}/${plan.readiness.host.arch}`;
  const readyCount = plan.readiness.commands.filter(
    (command) => command.path,
  ).length;
  return `Ready · ${readyCount} executable${readyCount === 1 ? "" : "s"}`;
}

function runtimeCommandValue(command: ReviewRuntimeCommand) {
  return (
    [humanize(command.state), command.version, command.path, command.message]
      .filter((value): value is string => Boolean(value))
      .join(" · ") || "Not reported"
  );
}

function dockerServerSummary(plan: ReviewPlan) {
  const docker = plan.readiness.docker;
  if (!docker) return "";
  const platform =
    docker.serverOs && docker.serverArch
      ? `${docker.serverOs}/${docker.serverArch}`
      : undefined;
  return [docker.serverVersion, platform]
    .filter((value): value is string => Boolean(value))
    .join(" · ");
}

function detailValue(value: unknown) {
  if (value == null || value === "") return "Not provided";
  if (typeof value === "boolean") return value ? "Enabled" : "Disabled";
  if (typeof value === "string" || typeof value === "number")
    return String(value);
  return JSON.stringify(value);
}

function fileName(path: string) {
  return path.split("/").filter(Boolean).at(-1) ?? path;
}

function humanBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KiB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MiB`;
}

function humanize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/^\w/, (character) => character.toUpperCase());
}

function statusTone(status: string) {
  if (status === "completed") return "complete";
  if (status === "failed") return "failed";
  if (status === "canceling" || status === "cancel_requested") return "warning";
  if (status === "canceled" || status === "orphaned") return "neutral";
  return "running";
}

function stringValue(value: unknown) {
  return typeof value === "string" ? value : "";
}

function errorMessage(error: unknown) {
  return error instanceof Error
    ? error.message
    : "Could not refresh live run status.";
}
