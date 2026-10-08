import { useCallback, useEffect, useRef, useState } from "react";

import type {
  ComputeTarget,
  DisplayMode,
  Pipeline,
  RunDetail,
  RunObservation,
  RunReport,
  RunSummary,
} from "../model";
import type { ReportArtifact } from "../report";
import { applyHostContext, type NgsWorkbenchClient } from "../mcp/client";
import {
  getRunDetail,
  getRunReport,
  listComputeTargets,
  listPipelines,
  listRunLineages,
  listRuns,
  observeRun,
} from "../mcp/ngs";
import { isActiveRunStatus, isTerminalRunStatus, latestActiveRunFilters } from "../runStatus";
import { isCurrentObservation, mergeRunIntoHistory } from "../runRefresh";

const POLL_INTERVAL_MS = 2_500;

export function useNgsWorkbench(client: NgsWorkbenchClient) {
  const [connected, setConnected] = useState(false);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [computeTargets, setComputeTargets] = useState<ComputeTarget[]>();
  const [targetsLoading, setTargetsLoading] = useState(false);
  const [targetsRequested, setTargetsRequested] = useState(false);
  const [targetsError, setTargetsError] = useState<string>();
  const [monitoredRun, setMonitoredRun] = useState<RunSummary>();
  const [analysisRun, setAnalysisRun] = useState<RunDetail>();
  const [analysisObservation, setAnalysisObservation] = useState<RunObservation>();
  const [analysisReport, setAnalysisReport] = useState<RunReport>();
  const [runHistory, setRunHistory] = useState<RunSummary[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [observationLoading, setObservationLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [observationError, setObservationError] = useState<{
    registryRunId: string;
    message: string;
  }>();
  const [reportError, setReportError] = useState<string>();
  const [operation, setOperation] = useState<"refreshing">();
  const [error, setError] = useState<string>();
  const [displayMode, setDisplayMode] = useState<DisplayMode>("inline");
  const openAnalysisRequestId = useRef(0);
  const reportRequestId = useRef(0);
  const observationRequests = useRef(new Map<string, Promise<RunObservation>>());
  const analysisIdentity = useRef<{ registryRunId: string; revision: number } | undefined>(
    undefined,
  );
  const analysisDetail = useRef<RunDetail | undefined>(undefined);

  const loadRunLineage = useCallback((run: RunSummary) => listRuns(client, {
    first_run_id: run.first_run_id,
    limit: 200,
  }), [client]);

  const loadRunHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const histories = await listRunLineages(client);
      setRunHistory(histories);
      return histories;
    } finally {
      setHistoryLoading(false);
    }
  }, [client]);

  const loadComputeTargets = useCallback(async () => {
    setTargetsRequested(true);
    setTargetsLoading(true);
    try {
      setComputeTargets(await listComputeTargets(client));
      setTargetsError(undefined);
    } catch (targetError) {
      setTargetsError(errorMessage(targetError, "Could not load compute targets."));
    } finally {
      setTargetsLoading(false);
    }
  }, [client]);

  const refreshRunHistory = useCallback(async () => {
    try {
      await loadRunHistory();
      setError(undefined);
    } catch (historyError) {
      setError(errorMessage(historyError, "Could not load durable run history."));
    }
  }, [loadRunHistory]);

  const loadCatalog = useCallback(async () => {
    setCatalogLoading(true);
    try {
      const availablePipelines = await listPipelines(client);
      setPipelines(availablePipelines);
      setError(undefined);
      try {
        const [, activeRuns] = await Promise.all([
          loadRunHistory(),
          listRuns(client, latestActiveRunFilters()),
        ]);
        setMonitoredRun((current) => current ?? activeRuns[0]);
      } catch (historyError) {
        setError(errorMessage(historyError, "Could not load durable run history."));
      }
    } catch (catalogError) {
      setError(errorMessage(catalogError, "Could not load the workflow catalog."));
    } finally {
      setCatalogLoading(false);
    }
  }, [client, loadRunHistory]);

  useEffect(() => {
    let disposed = false;
    const updateHostContext = () => {
      const context = client.getHostContext();
      applyHostContext(context);
      if (!context || disposed) return;
      setDisplayMode(context.displayMode === "fullscreen" ? "fullscreen" : "inline");
    };
    const removeHostListener = client.onHostContextChanged(updateHostContext);

    void client.connect().then(() => {
      if (disposed) return;
      setConnected(true);
      updateHostContext();
      void loadCatalog();
    }).catch((connectionError) => {
      if (disposed) return;
      setCatalogLoading(false);
      setError(errorMessage(connectionError, "Waiting for the MCP host."));
    });

    return () => {
      disposed = true;
      removeHostListener();
    };
  }, [client, loadCatalog]);

  const loadReport = useCallback(async (run: RunDetail) => {
    if (run.status !== "completed" || run.target?.target_id !== "local") return;
    const requestId = ++reportRequestId.current;
    setReportLoading(true);
    try {
      const response = await getRunReport(client, run.registry_run_id);
      const current = analysisIdentity.current;
      if (
        current?.registryRunId !== response.registry_run_id
        || response.revision < current.revision
      ) return;
      setAnalysisReport(response);
      setReportError(undefined);
    } catch (reportFailure) {
      if (requestId === reportRequestId.current) {
        setReportError(errorMessage(reportFailure, "Could not load the completed report."));
      }
    } finally {
      if (requestId === reportRequestId.current) setReportLoading(false);
    }
  }, [client]);

  const observeOnce = useCallback((registryRunId: string) => {
    const pending = observationRequests.current.get(registryRunId);
    if (pending) return pending;
    const request = observeRun(client, registryRunId).finally(() => {
      observationRequests.current.delete(registryRunId);
    });
    observationRequests.current.set(registryRunId, request);
    return request;
  }, [client]);

  const applyObservation = useCallback(async (observation: RunObservation) => {
    setMonitoredRun((current) => (
      current?.registry_run_id === observation.registry_run_id
        && observation.revision >= current.revision
        ? {
            ...current,
            status: observation.status,
            revision: observation.revision,
            pid: observation.pid ?? null,
            returncode: observation.returncode ?? null,
          }
        : current
    ));
    const identity = analysisIdentity.current;
    if (isCurrentObservation(identity, observation)) {
      setAnalysisObservation((current) => (
        !current || observation.revision >= current.revision ? observation : current
      ));
      analysisIdentity.current = {
        registryRunId: observation.registry_run_id,
        revision: observation.revision,
      };
      const detail = analysisDetail.current;
      if (detail && isTerminalRunStatus(observation.status)) {
        await loadReport({ ...detail, status: observation.status });
      }
    }
    setRunHistory((current) => mergeRunIntoHistory(current, observation));
    if (isTerminalRunStatus(observation.status)) await loadRunHistory();
  }, [loadReport, loadRunHistory]);

  const refreshStatus = useCallback(async () => {
    if (!analysisRun) return;
    setOperation((current) => current ?? "refreshing");
    setObservationLoading(true);
    try {
      await applyObservation(await observeOnce(analysisRun.registry_run_id));
      setObservationError((current) => (
        current?.registryRunId === analysisRun.registry_run_id ? undefined : current
      ));
    } catch (statusError) {
      setObservationError({
        registryRunId: analysisRun.registry_run_id,
        message: errorMessage(statusError, "Could not refresh the run status."),
      });
    } finally {
      setObservationLoading(false);
      setOperation((current) => current === "refreshing" ? undefined : current);
    }
  }, [analysisRun, applyObservation, observeOnce]);

  const refreshMonitoredStatus = useCallback(async () => {
    if (!monitoredRun) return;
    try {
      await applyObservation(await observeOnce(monitoredRun.registry_run_id));
      setObservationError((current) => (
        current?.registryRunId === monitoredRun.registry_run_id ? undefined : current
      ));
    } catch (statusError) {
      setObservationError({
        registryRunId: monitoredRun.registry_run_id,
        message: errorMessage(statusError, "Could not refresh the active run status."),
      });
    }
  }, [applyObservation, monitoredRun, observeOnce]);

  useEffect(() => {
    if (!monitoredRun || !isActiveRunStatus(monitoredRun.status)) return;
    const refreshWhenVisible = () => {
      if (document.visibilityState === "visible") void refreshMonitoredStatus();
    };
    const interval = window.setInterval(refreshWhenVisible, POLL_INTERVAL_MS);
    window.addEventListener("focus", refreshWhenVisible);
    document.addEventListener("visibilitychange", refreshWhenVisible);
    return () => {
      window.clearInterval(interval);
      window.removeEventListener("focus", refreshWhenVisible);
      document.removeEventListener("visibilitychange", refreshWhenVisible);
    };
  }, [monitoredRun, refreshMonitoredStatus]);

  const loadRunDetail = useCallback(
    (run: RunSummary) => getRunDetail(client, run.registry_run_id, pipelines),
    [client, pipelines],
  );
  const loadRunObservation = useCallback(
    (run: RunSummary) => observeOnce(run.registry_run_id),
    [observeOnce],
  );

  const openAnalysis = useCallback(async (run: RunSummary) => {
    const requestId = ++openAnalysisRequestId.current;
    reportRequestId.current += 1;
    setReportLoading(false);
    setDetailLoading(true);
    setError(undefined);
    try {
      const detail = await loadRunDetail(run);
      if (requestId !== openAnalysisRequestId.current) return;
      analysisIdentity.current = {
        registryRunId: detail.registry_run_id,
        revision: detail.revision,
      };
      analysisDetail.current = detail;
      setAnalysisRun(detail);
      setAnalysisObservation(undefined);
      setAnalysisReport(undefined);
      setObservationError(undefined);
      setReportError(undefined);
      setObservationLoading(true);
      void observeOnce(detail.registry_run_id).then((observation) => {
        if (requestId === openAnalysisRequestId.current) void applyObservation(observation);
      }).catch((observationFailure) => {
        if (requestId === openAnalysisRequestId.current) {
          setObservationError({
            registryRunId: detail.registry_run_id,
            message: errorMessage(observationFailure, "Could not observe this run."),
          });
        }
      }).finally(() => {
        if (requestId === openAnalysisRequestId.current) setObservationLoading(false);
      });
      void loadReport(detail);
    } catch (runError) {
      if (requestId !== openAnalysisRequestId.current) return;
      setError(errorMessage(runError, "Could not open the registered run."));
    } finally {
      if (requestId === openAnalysisRequestId.current) setDetailLoading(false);
    }
  }, [applyObservation, loadReport, loadRunDetail, observeOnce]);

  const openArtifact = useCallback(async (artifact: ReportArtifact) => {
    if (!artifact.openUrl) return;
    try {
      const result = await client.openLink(artifact.openUrl);
      if (result.isError) throw new Error("The host declined to open this report.");
      setError(undefined);
    } catch (openError) {
      setError(errorMessage(openError, "Could not open the generated report."));
    }
  }, [client]);

  return {
    analysisObservation,
    analysisReport,
    analysisRun,
    catalogLoading,
    computeTargets,
    connected,
    detailLoading,
    dismissError: () => setError(undefined),
    displayMode,
    error,
    historyLoading,
    loadCatalog,
    loadComputeTargets,
    loadRunDetail,
    loadRunLineage,
    loadRunObservation,
    observationError,
    observationLoading,
    operation,
    openArtifact,
    openAnalysis,
    pipelines,
    refreshRunHistory,
    refreshStatus,
    reportError,
    reportLoading,
    runHistory,
    targetsError,
    targetsLoading,
    targetsRequested,
  };
}

function errorMessage(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
}
