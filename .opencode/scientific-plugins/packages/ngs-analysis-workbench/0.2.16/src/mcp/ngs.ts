import type {
  ComputeTarget,
  ComputeTargetRef,
  OperationResult,
  Pipeline,
  RunDetail,
  RunObservation,
  RunReport,
  RunSummary,
} from "../model";
import { parseAnalysisReport } from "../report/parse";
import { parseExecutionObservation } from "../execution-observation";
import type { McpToolCaller } from "./client";

interface CatalogPayload {
  workflows: Array<{
    workflow_id: string;
    name: string;
    engine: "nextflow" | "snakemake";
    description: string | null;
    catalog: "bundled" | "user";
    source:
      | { kind: "local"; root: string; entrypoint: string; source_sha256: string }
      | { kind: "remote"; workflow: string; revision: string };
    collection?: string;
  }>;
}

interface RunDetailPayload extends OperationResult {
  binding: string;
  pipeline: string;
  workflow: string;
  run_id: string;
  first_run_id: string;
  attempt_number: number;
  display_name?: string;
  command_argv?: string[];
  status: string;
  registry_run_id: string;
  revision: number;
  started_at_ms?: number | null;
  completed_at_ms?: number | null;
  returncode?: number | null;
  pid?: number;
  run_dir: string;
  plan_checksum: string;
  profile?: string | null;
  workflow_revision?: string | null;
  workflow_source?: Record<string, unknown>;
  input_summary?: RunSummary["input_summary"];
  runtime_summary?: unknown;
  warnings: string[];
  target?: ComputeTargetRef | null;
  analysis_summary?: string;
  failure_summary?: string | null;
}

interface RunObservationPayload extends OperationResult {
  registry_run_id: string;
  revision: number;
  status: string;
  pid?: number | null;
  returncode?: number | null;
  failure_summary?: string | null;
  log_tail?: string | null;
  execution?: unknown;
  warnings?: string[];
}

interface RunReportPayload extends OperationResult {
  registry_run_id: string;
  revision: number;
  availability: RunReport["availability"];
  report?: unknown;
}

interface RunHistoryPayload extends OperationResult {
  runs?: RunSummary[];
}

interface ComputeTargetsPayload {
  targets?: unknown;
}

export async function listPipelines(client: McpToolCaller): Promise<Pipeline[]> {
  const payload = await client.call<CatalogPayload>("list_workflows", {});
  return payload.workflows.map((workflow) => ({
    id: workflow.workflow_id,
    title: workflow.name,
    workflow:
      workflow.source.kind === "remote"
        ? workflow.source.workflow
        : workflow.source.root,
    description: workflow.description ?? "",
    engine: workflow.engine,
    collection: workflow.collection,
    catalog: workflow.catalog === "user" ? "saved" : "bundled",
    sourceKind: workflow.source.kind,
    revision: workflow.source.kind === "remote" ? workflow.source.revision : undefined,
    entrypoint: workflow.source.kind === "local" ? workflow.source.entrypoint : undefined,
    sourceSha256:
      workflow.source.kind === "local" ? workflow.source.source_sha256 : undefined,
  }));
}

export async function listComputeTargets(client: McpToolCaller): Promise<ComputeTarget[]> {
  const payload = await client.call<ComputeTargetsPayload>("list_compute_target_summaries", {});
  if (!Array.isArray(payload.targets)) throw new Error("The MCP did not return a compute target list.");
  return payload.targets.map((value) => {
    if (!isRecord(value)) throw new Error("The MCP returned an invalid compute target.");
    const configuration = isRecord(value.executor_configuration)
      ? Object.fromEntries(Object.entries(value.executor_configuration).filter((entry): entry is [string, string] => typeof entry[1] === "string"))
      : {};
    return {
      target_id: requiredString(value, "target_id"),
      title: requiredString(value, "title"),
      controllerTransport: requiredString(value, "controller_transport"),
      executor: requiredString(value, "executor"),
      workspaceAccess: requiredString(value, "workspace_access"),
      description: requiredString(value, "description"),
      workspaceRoot: typeof value.workspace_root === "string" ? value.workspace_root : undefined,
      executorConfiguration: configuration,
    };
  });
}

export async function listRuns(
  client: McpToolCaller,
  filters: Record<string, unknown>,
): Promise<RunSummary[]> {
  const payload = await client.call<RunHistoryPayload>("list_ngs_runs", filters);
  assertSuccessful(payload, "Could not load durable run history.");
  if (!Array.isArray(payload.runs)) {
    throw new Error("The MCP did not return a run list.");
  }
  return payload.runs;
}

export async function listRunLineages(
  client: McpToolCaller,
  limit = 20,
): Promise<RunSummary[]> {
  const payload = await client.call<RunHistoryPayload>("list_ngs_run_lineages", { limit });
  assertSuccessful(payload, "Could not load durable run history.");
  if (!Array.isArray(payload.runs)) {
    throw new Error("The MCP did not return a run lineage list.");
  }
  return payload.runs;
}

export async function getRunDetail(
  client: McpToolCaller,
  registryRunId: string,
  pipelines: Pipeline[],
): Promise<RunDetail> {
  const payload = await client.call<RunDetailPayload>("get_ngs_run", {
    registry_run_id: registryRunId,
  });
  assertSuccessful(payload, "Could not read the registered run.");
  if (payload.registry_run_id !== registryRunId) {
    throw new Error("The MCP returned a different registered run.");
  }
  const pipeline = pipelines.find((candidate) =>
    candidate.id === payload.pipeline && (!candidate.engine || candidate.engine === payload.binding)
  ) ?? {
    id: payload.pipeline,
    title: payload.display_name ?? payload.pipeline,
    workflow: payload.workflow,
    description: "Restored from durable run history.",
  };
  return {
    binding: payload.binding,
    pipeline: { ...pipeline, workflow: payload.workflow },
    workflow: payload.workflow,
    target: payload.target ?? undefined,
    run_id: payload.run_id,
    first_run_id: payload.first_run_id,
    attempt_number: payload.attempt_number,
    registry_run_id: payload.registry_run_id,
    revision: payload.revision,
    status: payload.status,
    display_name: payload.display_name,
    analysis_summary: payload.analysis_summary,
    failure_summary: payload.failure_summary,
    pid: payload.pid,
    started_at_ms: payload.started_at_ms,
    completed_at_ms: payload.completed_at_ms,
    run_dir: payload.run_dir,
    command_argv: Array.isArray(payload.command_argv) ? payload.command_argv : [],
    plan_checksum: payload.plan_checksum,
    profile: payload.profile,
    workflow_revision: payload.workflow_revision,
    workflow_source: payload.workflow_source,
    input_summary: payload.input_summary,
    runtime_summary: payload.runtime_summary,
    warnings: payload.warnings,
    returncode: payload.returncode,
  };
}

export async function observeRun(
  client: McpToolCaller,
  registryRunId: string,
): Promise<RunObservation> {
  const payload = await client.call<RunObservationPayload>("observe_ngs_run", {
    registry_run_id: registryRunId,
  });
  assertSuccessful(payload, "Could not observe the registered run.");
  if (payload.registry_run_id !== registryRunId) {
    throw new Error("The MCP observed a different registered run.");
  }
  const execution = parseExecutionObservation(payload.execution);
  if (!execution) throw new Error("The MCP returned invalid execution evidence.");
  return {
    registry_run_id: payload.registry_run_id,
    revision: payload.revision,
    status: payload.status,
    pid: payload.pid,
    returncode: payload.returncode,
    failure_summary: payload.failure_summary,
    log_tail: typeof payload.log_tail === "string" ? payload.log_tail : null,
    execution,
    warnings: Array.isArray(payload.warnings) ? payload.warnings : [],
  };
}

export async function getRunReport(
  client: McpToolCaller,
  registryRunId: string,
): Promise<RunReport> {
  const payload = await client.call<RunReportPayload>("get_ngs_run_report", {
    registry_run_id: registryRunId,
  });
  assertSuccessful(payload, "Could not read the registered run report.");
  if (payload.registry_run_id !== registryRunId) {
    throw new Error("The MCP returned a report for a different registered run.");
  }
  return {
    registry_run_id: payload.registry_run_id,
    revision: payload.revision,
    availability: payload.availability,
    report: parseAnalysisReport(payload.report),
  };
}

function assertSuccessful<T extends OperationResult>(
  payload: T,
  fallback: string,
): asserts payload is T & { ok: true } {
  if (payload.ok) return;
  if (payload.errors?.length) throw new Error(payload.errors.join("\n"));
  if (payload.readiness) throw new Error(JSON.stringify(payload.readiness, null, 2));
  throw new Error(fallback);
}

function requiredString(value: Record<string, unknown>, key: string): string {
  const field = value[key];
  if (typeof field !== "string" || !field) throw new Error("The MCP returned an invalid compute target.");
  return field;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}
