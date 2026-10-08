import type { RunObservation, RunSummary } from "./model";

export function isCurrentObservation(
  identity: { registryRunId: string; revision: number } | undefined,
  observation: Pick<RunObservation, "registry_run_id" | "revision">,
): boolean {
  return identity?.registryRunId === observation.registry_run_id
    && observation.revision >= identity.revision;
}

export function mergeRunIntoHistory(
  runs: RunSummary[],
  refreshedRun: Pick<
    RunObservation,
    | "pid"
    | "registry_run_id"
    | "returncode"
    | "revision"
    | "status"
  >,
): RunSummary[] {
  return runs.map((run) => (
    run.registry_run_id === refreshedRun.registry_run_id
      && refreshedRun.revision >= run.revision
      ? {
          ...run,
          status: refreshedRun.status,
          revision: refreshedRun.revision,
          pid: refreshedRun.pid ?? null,
          returncode: refreshedRun.returncode ?? null,
        }
      : run
  ));
}
