import { isRecord, type ToolArguments, type ToolPayload } from "./client.ts";
import { parseExecutionObservation } from "../execution-observation.ts";
import type { ExecutionObservation } from "../model";

export type WorkflowEngine = "nextflow" | "snakemake";
export type RunBinding = WorkflowEngine;
export type ReviewPlanRequest = ToolArguments & {
  target: {
    target_id: string;
    provider: string;
  };
  run_dir: string;
  run_id: string;
};

export interface ReviewRuntimeCommand {
  name: string;
  path: string | null;
  state: string;
  version?: string;
  message?: string;
}

export interface ReviewDockerRuntime {
  path: string | null;
  context?: string;
  endpoint?: string;
  endpointIsLocal?: boolean;
  daemonReachable: boolean;
  serverVersion?: string;
  serverOs?: string;
  serverArch?: string;
  message?: string;
}

export interface ReviewPlan {
  binding: RunBinding;
  planName: string;
  planId: string;
  planChecksum: string;
  runnable: boolean;
  request: ReviewPlanRequest;
  command: string[];
  readiness: {
    ok: boolean;
    scope: string;
    snapshotId?: string;
    host?: { os: string; arch: string };
    commands: ReviewRuntimeCommand[];
    docker?: ReviewDockerRuntime;
    blockers: string[];
    warnings: string[];
  };
  effects: {
    runDir: string;
    outputDir: string;
    workDir: string;
    launchLog: string;
    localWrites: string[];
    remoteWrites?: string[];
    downloads: string[];
    networkAccess: string[];
  };
  preparation?: {
    destinationDir: string;
    downloadBytes: number;
    writes: string[];
    operations: Array<{
      operation: "download_verified_file" | "write_generated_file";
      path: string;
      role?: string;
      url?: string;
      bytes: number;
      sha256: string;
      mediaType?: string;
    }>;
  };
  blockers: string[];
  warnings: string[];
  monitoring: ToolPayload;
}

export interface ReviewRun {
  binding: RunBinding;
  registryRunId: string;
  target?: { target_id: string; provider: string };
  displayName?: string;
  runId: string;
  revision: number;
  status: string;
  workflow?: string;
  pid?: number;
  returncode?: number | null;
  failureSummary?: string | null;
  runDir?: string;
  command: string[];
  warnings: string[];
  logTail: string | null;
  execution?: ExecutionObservation;
}

export interface ReviewExecutionFailure {
  message: string;
  recovery?: string;
}

export function parseExecutionFailure(payload: ToolPayload): ReviewExecutionFailure | undefined {
  if (payload.ok !== false || !Array.isArray(payload.errors)) return undefined;

  const errors = payload.errors.filter(
    (error): error is string => typeof error === "string" && error.trim().length > 0,
  );
  if (!errors.length) return undefined;

  const snapshotUnavailable = errors.some((error) =>
    /runtime snapshot (?:is unknown to this server|has expired|expired)/i.test(error),
  );
  return {
    message: errors.join("\n"),
    ...(snapshotUnavailable
      ? { recovery: "Refresh the runtime environment, then create and review a new execution plan." }
      : {}),
  };
}

export function parsePlan(payload: ToolPayload): ReviewPlan | undefined {
  const planName = optionalString(payload.plan_name);
  const planId = optionalString(payload.plan_id);
  const planChecksum = optionalString(payload.plan_checksum);
  if (
    payload.ok !== true
    || !planName
    || !planId
    || !planChecksum
    || !isSha256(planChecksum)
    || typeof payload.runnable !== "boolean"
    || !isRecord(payload.request)
    || !isRecord(payload.readiness)
    || !isRecord(payload.effects)
  ) return undefined;

  const remoteWrites = payload.effects.remote_writes;
  if (
    remoteWrites !== undefined
    && (!Array.isArray(remoteWrites) || remoteWrites.some((path) => typeof path !== "string"))
  ) return undefined;

  const runId = stringValue(payload.request.run_id);
  const runDir = stringValue(payload.request.run_dir);
  if (!runId || !runDir) return undefined;
  const targetPayload = isRecord(payload.request.target) ? payload.request.target : undefined;
  const targetId = optionalString(targetPayload?.target_id) ?? "local";
  const targetProvider = optionalString(targetPayload?.provider) ?? "ngs-analysis-workbench";
  const request: ReviewPlanRequest = {
    ...payload.request,
    target: { target_id: targetId, provider: targetProvider },
    run_id: runId,
    run_dir: runDir,
  };

  const commands = Array.isArray(payload.readiness.commands)
    ? payload.readiness.commands.flatMap((command) => {
        if (!isRecord(command) || typeof command.name !== "string") return [];
        return [{
          name: command.name,
          path: typeof command.path === "string" ? command.path : null,
          state: typeof command.state === "string" ? command.state : "unverified",
          version: optionalString(command.version),
          message: optionalString(command.message),
        }];
      })
    : [];

  const host = isRecord(payload.readiness.host)
    && typeof payload.readiness.host.os === "string"
    && typeof payload.readiness.host.arch === "string"
    ? { os: payload.readiness.host.os, arch: payload.readiness.host.arch }
    : undefined;
  const dockerPayload = isRecord(payload.readiness.docker) ? payload.readiness.docker : undefined;
  const docker = dockerPayload && typeof dockerPayload.daemon_reachable === "boolean"
    ? {
        path: typeof dockerPayload.path === "string" ? dockerPayload.path : null,
        context: optionalString(dockerPayload.context),
        endpoint: optionalString(dockerPayload.endpoint),
        endpointIsLocal: optionalBoolean(dockerPayload.endpoint_is_local),
        daemonReachable: dockerPayload.daemon_reachable,
        serverVersion: optionalString(dockerPayload.server_version),
        serverOs: optionalString(dockerPayload.server_os),
        serverArch: optionalString(dockerPayload.server_arch),
        message: optionalString(dockerPayload.message),
      }
    : undefined;
  const preparationPayload = isRecord(payload.preparation) ? payload.preparation : undefined;
  const preparationOperations = preparationPayload && Array.isArray(preparationPayload.operations)
    ? preparationPayload.operations.flatMap((value) => {
        if (!isRecord(value)) return [];
        const operation = value.operation;
        const path = optionalString(value.path);
        const sha256 = optionalString(value.sha256);
        if (
          (operation !== "download_verified_file" && operation !== "write_generated_file")
          || !path
          || !sha256
          || typeof value.bytes !== "number"
        ) return [];
        return [{
          operation: operation as "download_verified_file" | "write_generated_file",
          path,
          role: optionalString(value.role),
          url: optionalString(value.url),
          bytes: value.bytes,
          sha256,
          mediaType: optionalString(value.media_type),
        }];
      })
    : [];
  if (
    preparationPayload
    && (!Array.isArray(preparationPayload.operations)
      || preparationOperations.length !== preparationPayload.operations.length)
  ) return undefined;

  return {
    binding: isRunBinding(payload.binding)
      ? payload.binding
      : bindingFromRequest(request),
    planName,
    planId,
    planChecksum,
    runnable: payload.runnable,
    request,
    command: stringArray(payload.command_argv),
    readiness: {
      ok: payload.readiness.ok === true,
      scope: stringValue(payload.readiness.scope),
      snapshotId: optionalString(payload.readiness.snapshot_id),
      host,
      commands,
      docker,
      blockers: stringArray(payload.readiness.blockers),
      warnings: stringArray(payload.readiness.warnings),
    },
    effects: {
      runDir: stringValue(payload.effects.run_dir),
      outputDir: stringValue(payload.effects.output_dir),
      workDir: stringValue(payload.effects.work_dir),
      launchLog: stringValue(payload.effects.launch_log),
      localWrites: stringArray(payload.effects.local_writes),
      remoteWrites: stringArray(remoteWrites),
      downloads: stringArray(payload.effects.downloads),
      networkAccess: stringArray(payload.effects.network_access),
    },
    preparation: preparationPayload
      ? {
          destinationDir: stringValue(preparationPayload.destination_dir),
          downloadBytes: typeof preparationPayload.download_bytes === "number"
            ? preparationPayload.download_bytes
            : 0,
          writes: stringArray(preparationPayload.writes),
          operations: preparationOperations,
        }
      : undefined,
    blockers: stringArray(payload.blockers),
    warnings: stringArray(payload.warnings),
    monitoring: isRecord(payload.monitoring) ? payload.monitoring : {},
  };
}

export function parseStartedRun(
  payload: ToolPayload,
  input: ToolArguments | undefined,
  plan?: ReviewPlan,
): ReviewRun | undefined {
  if (payload.ok !== true || typeof payload.run_id !== "string") return undefined;
  if (plan && payload.plan_checksum !== plan.planChecksum) return undefined;
  const registryRunId = optionalString(payload.registry_run_id);
  if (!registryRunId) return undefined;
  const binding = plan?.binding
    ?? (isRunBinding(payload.binding)
      ? payload.binding
      : input ? bindingFromRequest(input) : bindingFromRunId(payload.run_id));
  return {
    binding,
    registryRunId,
    target: plan?.request.target ?? parseTarget(payload.target),
    displayName: optionalString(payload.display_name)
      ?? (plan ? optionalString(plan.request.display_name) : undefined),
    runId: payload.run_id,
    revision: optionalNumber(payload.revision) ?? 0,
    status: stringValue(payload.status) || "running",
    workflow: optionalString(payload.workflow) ?? (plan ? optionalString(plan.request.workflow) : undefined),
    pid: optionalNumber(payload.pid),
    returncode: optionalNullableNumber(payload.returncode),
    failureSummary: optionalString(payload.failure_summary),
    runDir: optionalString(payload.run_dir) ?? plan?.effects.runDir,
    command: Array.isArray(payload.command_argv) ? stringArray(payload.command_argv) : (plan?.command ?? []),
    warnings: Array.isArray(payload.warnings) ? stringArray(payload.warnings) : (plan?.warnings ?? []),
    logTail: payload.log_tail === null ? null : stringValue(payload.log_tail),
    execution: parseExecutionObservation(payload.execution),
  };
}

export function mergeRunObservation(run: ReviewRun, payload: ToolPayload): ReviewRun {
  if (payload.ok !== true) {
    throw new Error(payloadErrors(payload, "Could not read live run status."));
  }
  const registryRunId = optionalString(payload.registry_run_id);
  if (registryRunId !== run.registryRunId) {
    throw new Error("The status response did not match the approved run receipt.");
  }
  const revision = optionalNumber(payload.revision);
  if (revision === undefined) throw new Error("The status response did not include a revision.");
  if (revision < run.revision) return run;

  return {
    ...run,
    revision,
    status: optionalString(payload.status) ?? run.status,
    pid: optionalNumber(payload.pid) ?? run.pid,
    returncode: payload.returncode === null || typeof payload.returncode === "number"
      ? payload.returncode
      : run.returncode,
    failureSummary: payload.failure_summary === null
      ? null
      : optionalString(payload.failure_summary) ?? run.failureSummary,
    warnings: stringArray(payload.warnings),
    logTail: payload.log_tail === null ? null : optionalString(payload.log_tail) ?? run.logTail,
    execution: parseExecutionObservation(payload.execution) ?? run.execution,
  };
}

export function payloadErrors(payload: ToolPayload, fallback: string) {
  const errors = stringArray(payload.errors);
  return errors.length ? errors.join("\n") : fallback;
}

function bindingFromRunId(runId: string): RunBinding {
  return runId.startsWith("nextflow-") ? "nextflow" : "snakemake";
}

function bindingFromRequest(request: ToolArguments): RunBinding {
  if (
    isRecord(request.workflow_source)
    && request.workflow_source.engine === "nextflow"
  ) return "nextflow";
  return "profile" in request ? "nextflow" : "snakemake";
}

function isRunBinding(value: unknown): value is RunBinding {
  return value === "nextflow" || value === "snakemake";
}

function stringArray(value: unknown) {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function stringValue(value: unknown) {
  return typeof value === "string" ? value : "";
}

function optionalString(value: unknown) {
  return typeof value === "string" ? value : undefined;
}

function isSha256(value: string) {
  return /^sha256:[0-9a-f]{64}$/.test(value);
}

function optionalNumber(value: unknown) {
  return typeof value === "number" ? value : undefined;
}

function optionalBoolean(value: unknown) {
  return typeof value === "boolean" ? value : undefined;
}

function optionalNullableNumber(value: unknown) {
  return value === null || typeof value === "number" ? value : undefined;
}

function parseTarget(value: unknown) {
  if (!isRecord(value)) return undefined;
  const targetId = optionalString(value.target_id);
  const provider = optionalString(value.provider);
  return targetId && provider ? { target_id: targetId, provider } : undefined;
}
