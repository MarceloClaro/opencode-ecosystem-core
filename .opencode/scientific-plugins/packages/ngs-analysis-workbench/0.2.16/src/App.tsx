import { ExecutionObservationPanel } from "./components/ExecutionObservationPanel";
import { Icon } from "./design-system/Icon";
import { useEffect, useLayoutEffect, useRef, useState } from "react";

import workbenchIcon from "../assets/app-icon.png";
import { analysisSummaryMessage } from "./analysisSummary";
import { AnalysisSummaryPrompt } from "./components/AnalysisSummaryPrompt";
import { ComputeTargetCatalog } from "./components/ComputeTargetCatalog";
import { PipelineCatalog } from "./components/PipelineCatalog";
import { RunHistory } from "./components/RunHistory";
import { AttemptsToggle, RunHistorySidebar } from "./components/RunHistorySidebar";
import { useNgsWorkbench } from "./hooks/useNgsWorkbench";
import { NgsMcpClient, type NgsWorkbenchClient } from "./mcp/client";
import type { RunDetail, RunObservation, RunSummary } from "./model";
import { AnalysisReport } from "./report";
import { runStatusPresentation } from "./runStatus";
import styles from "./App.module.css";
import ui from "./styles/ui.module.css";

const defaultClient = new NgsMcpClient();

interface NgsWorkbenchAppProps {
  client?: NgsWorkbenchClient;
}

export type NgsWorkbenchViewModel = ReturnType<typeof useNgsWorkbench>;
export type WorkbenchPage = "overview" | "workflows" | "compute" | "run";

export function NgsWorkbenchApp({
  client = defaultClient,
}: NgsWorkbenchAppProps) {
  const workbench = useNgsWorkbench(client);
  return <NgsWorkbenchSurface workbench={workbench} />;
}

export function NgsWorkbenchSurface({
  workbench,
  initialPage = "overview",
}: {
  workbench: NgsWorkbenchViewModel;
  initialPage?: WorkbenchPage;
}) {
  const [page, setPage] = useState<WorkbenchPage>(initialPage);
  const [previousRunsPage, setPreviousRunsPage] = useState<"overview" | "run">(
    initialPage === "run" ? "run" : "overview",
  );
  const [lineageHead, setLineageHead] = useState<RunSummary | undefined>(
    initialPage === "run"
      ? workbench.runHistory.find(
          (run) =>
            run.registry_run_id === workbench.analysisRun?.registry_run_id,
        )
      : undefined,
  );

  useEffect(() => {
    if (
      page === "compute" &&
      workbench.computeTargets === undefined &&
      !workbench.targetsRequested
    ) {
      void workbench.loadComputeTargets();
    }
  }, [
    page,
    workbench.computeTargets,
    workbench.loadComputeTargets,
    workbench.targetsRequested,
  ]);

  useEffect(() => {
    const registryRunId =
      lineageHead?.registry_run_id ?? workbench.analysisRun?.registry_run_id;
    if (!registryRunId) return;
    const registeredRun = workbench.runHistory.find(
      (run) => run.registry_run_id === registryRunId,
    );
    if (registeredRun && registeredRun !== lineageHead)
      setLineageHead(registeredRun);
  }, [lineageHead, workbench.analysisRun, workbench.runHistory]);

  const openRunDetail = (run: RunSummary) => {
    setLineageHead(run);
    setPage("run");
    void workbench.openAnalysis(run);
  };
  const returnToOverview = () => {
    setPage("overview");
  };
  const navigate = (destination: WorkbenchPage) => {
    if (
      ["workflows", "compute"].includes(destination) &&
      !["workflows", "compute"].includes(page)
    ) {
      setPreviousRunsPage(page === "run" ? "run" : "overview");
      setPage(destination);
      return;
    }
    setPage(
      destination === "overview" && ["workflows", "compute"].includes(page)
        ? previousRunsPage
        : destination,
    );
  };

  return (
    <div
      className={`ngs-theme ${styles.shell}`}
      data-display-mode={workbench.displayMode}
    >
      <WorkbenchHeader onNavigate={navigate} page={page} />

      {workbench.error ? (
        <div className={styles.errorBanner} role="alert">
          <pre>{workbench.error}</pre>
          <button
            className={`${ui.button} ${ui.buttonQuiet}`}
            onClick={workbench.dismissError}
            type="button"
          >
            Dismiss
          </button>
        </div>
      ) : null}

      {page === "run" ? (
        <RunDetail
          onReturnToOverview={returnToOverview}
          lineageHead={lineageHead}
          workbench={workbench}
        />
      ) : page === "workflows" ? (
        <WorkflowsSurface workbench={workbench} />
      ) : page === "compute" ? (
        <ComputeSurface workbench={workbench} />
      ) : (
        <OverviewSurface workbench={workbench} onOpenRun={openRunDetail} />
      )}
    </div>
  );
}

function WorkbenchHeader({
  onNavigate,
  page,
}: {
  onNavigate: (page: WorkbenchPage) => void;
  page: WorkbenchPage;
}) {
  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <img className={styles.brandMark} src={workbenchIcon} alt="" />
        <h1 aria-label="NGS Analysis Workbench">
          <span className={styles.brandFull}>NGS Analysis Workbench</span>
          <span className={styles.brandShort} aria-hidden="true">
            NGS
          </span>
        </h1>
      </div>
      <nav className={styles.navigation} aria-label="Primary navigation">
        <button
          aria-current={["overview", "run"].includes(page) ? "page" : undefined}
          onClick={() => onNavigate("overview")}
          type="button"
        >
          Runs
        </button>
        <button
          aria-current={page === "workflows" ? "page" : undefined}
          onClick={() => onNavigate("workflows")}
          type="button"
        >
          Pipelines
        </button>
        <button
          aria-current={page === "compute" ? "page" : undefined}
          onClick={() => onNavigate("compute")}
          type="button"
        >
          Compute
        </button>
      </nav>
    </header>
  );
}

function OverviewSurface({
  workbench,
  onOpenRun,
}: {
  workbench: NgsWorkbenchViewModel;
  onOpenRun: (run: RunSummary) => void;
}) {
  return (
    <main className={styles.overview}>
      {!workbench.connected && !workbench.error ? (
        <p className={`${ui.emptyCopy} ${ui.loadingRow}`} role="status">
          <Icon name="spinner" className="ngs-spin" size={16} />
          Opening workbench…
        </p>
      ) : (
        <RunHistory
          loading={workbench.historyLoading}
          onOpenRun={onOpenRun}
          onRefresh={() => void workbench.refreshRunHistory()}
          runs={workbench.runHistory}
        />
      )}
    </main>
  );
}

function WorkflowsSurface({ workbench }: { workbench: NgsWorkbenchViewModel }) {
  return (
    <main className={styles.overview}>
      <section
        className={styles.workflowPage}
        aria-labelledby="workflow-page-heading"
      >
        <div className={ui.pageHeader}>
          <h2 className={ui.pageTitle} id="workflow-page-heading">
            Pipeline library
          </h2>
          <button
            className={`${ui.button} ${ui.buttonSecondary}`}
            disabled={workbench.catalogLoading}
            onClick={() => void workbench.loadCatalog()}
            type="button"
          >
            {workbench.catalogLoading ? (
              <Icon name="spinner" className="ngs-spin" size={16} />
            ) : null}
            {workbench.catalogLoading ? "Refreshing…" : "Refresh pipelines"}
          </button>
        </div>
        <div className={styles.pipelineIntro}>
          <p className={ui.sectionLabel}>
            Explore included and saved pipelines
          </p>
        </div>
        <PipelineCatalog
          pipelines={workbench.pipelines}
          loading={workbench.catalogLoading}
          unavailable={!workbench.connected || Boolean(workbench.error)}
        />
      </section>
    </main>
  );
}

function ComputeSurface({ workbench }: { workbench: NgsWorkbenchViewModel }) {
  return (
    <main className={styles.overview}>
      <section
        className={styles.workflowPage}
        aria-labelledby="compute-page-heading"
      >
        <div className={ui.pageHeader}>
          <h2 className={ui.pageTitle} id="compute-page-heading">
            Compute targets
          </h2>
          <button
            className={`${ui.button} ${ui.buttonSecondary}`}
            disabled={workbench.targetsLoading}
            onClick={() => void workbench.loadComputeTargets()}
            type="button"
          >
            {workbench.targetsLoading ? (
              <Icon name="spinner" className="ngs-spin" size={16} />
            ) : null}
            {workbench.targetsLoading ? "Refreshing…" : "Refresh targets"}
          </button>
        </div>
        <ComputeTargetCatalog
          error={workbench.targetsError}
          loading={workbench.targetsLoading}
          targets={workbench.computeTargets}
        />
      </section>
    </main>
  );
}

function RunDetail({
  lineageHead,
  onReturnToOverview,
  workbench,
}: {
  lineageHead?: RunSummary;
  onReturnToOverview: () => void;
  workbench: NgsWorkbenchViewModel;
}) {
  const detailRef = useRef<HTMLElement>(null);
  const toggleRef = useRef<HTMLButtonElement>(null);
  const [compactInspector, setCompactInspector] = useState(false);
  const [historyPreference, setHistoryPreference] = useState<boolean>();
  const historyOpen = historyPreference ?? !compactInspector;

  useLayoutEffect(() => {
    const element = detailRef.current;
    if (!element) return;
    const updateLayout = () => setCompactInspector(element.clientWidth <= 960);
    updateLayout();
    const observer = new ResizeObserver(updateLayout);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  const closeInspector = () => {
    setHistoryPreference(false);
    requestAnimationFrame(() => toggleRef.current?.focus());
  };
  const openInspector = () => {
    setHistoryPreference(true);
    if (!compactInspector) {
      requestAnimationFrame(() => toggleRef.current?.focus());
    }
  };
  const analysisRun =
    workbench.analysisRun?.registry_run_id === lineageHead?.registry_run_id
      ? workbench.analysisRun
      : undefined;

  return (
    <main className={styles.runDetail} ref={detailRef}>
      <div
        className={styles.runDetailLayout}
        data-history-open={historyOpen && Boolean(lineageHead)}
        data-compact-inspector={compactInspector}
      >
        <div className={styles.analysisColumn}>
          <header className={styles.detailHeader}>
            <nav className={styles.detailBreadcrumb} aria-label="Workbench pages">
              <button onClick={onReturnToOverview} type="button">
                Runs
              </button>
              <Icon name="chevron-right-sm" size={16} />
              <span aria-current="page">
                {analysisRun?.display_name ??
                  lineageHead?.display_name ??
                  analysisRun?.pipeline.title ??
                  "Run detail"}
              </span>
            </nav>
            {lineageHead && (!historyOpen || compactInspector) ? (
              <AttemptsToggle
                attemptCount={lineageHead.attempt_number}
                buttonRef={toggleRef}
                modal={compactInspector}
                onClick={historyOpen ? closeInspector : openInspector}
                open={historyOpen}
              />
            ) : null}
          </header>
          <section
            className={styles.analysisPane}
            aria-label="Analysis and execution"
            tabIndex={0}
          >
            <div className={styles.analysisContent}>
              <AnalysisSurface
                loading={workbench.detailLoading}
                onOpenArtifact={workbench.openArtifact}
                observation={workbench.analysisObservation}
                report={workbench.analysisReport?.report}
                reportError={workbench.reportError}
                reportLoading={workbench.reportLoading}
                run={analysisRun}
              />
            </div>
          </section>
        </div>
        {lineageHead ? (
          <RunHistorySidebar
            analysisLoading={workbench.detailLoading}
            analysisObservation={workbench.analysisObservation}
            analysisRun={analysisRun}
            executionInMain={
              !workbench.analysisReport?.report && !workbench.detailLoading
            }
            lineageHead={lineageHead}
            loadRunDetail={workbench.loadRunDetail}
            loadRunLineage={workbench.loadRunLineage}
            loadRunObservation={workbench.loadRunObservation}
            observationError={workbench.observationError}
            open={historyOpen}
            modal={compactInspector}
            onClose={closeInspector}
            toggleRef={toggleRef}
            onRefreshAnalysis={() => void workbench.refreshStatus()}
            refreshingAnalysis={workbench.operation === "refreshing"}
          />
        ) : null}
      </div>
    </main>
  );
}

function AnalysisSurface({
  loading,
  observation,
  onOpenArtifact,
  report,
  reportError,
  reportLoading,
  run,
}: {
  loading: boolean;
  observation?: RunObservation;
  onOpenArtifact: NgsWorkbenchViewModel["openArtifact"];
  report?: NonNullable<NgsWorkbenchViewModel["analysisReport"]>["report"];
  reportError?: string;
  reportLoading: boolean;
  run?: RunDetail;
}) {
  if (run && report) {
    return (
      <AnalysisReport
        onOpenArtifact={onOpenArtifact}
        report={report}
        runId={run.run_id}
        registryRunId={run.registry_run_id}
      />
    );
  }

  const status = run
    ? runStatusPresentation(observation?.status ?? run.status)
    : undefined;
  const summaryMessage = analysisSummaryMessage(
    run?.analysis_summary,
    reportLoading,
    reportError,
  );
  return (
    <>
      <section className={styles.analysisState} aria-live="polite">
        <h2>
          {loading
            ? "Loading analysis…"
            : run
            ? analysisStateTitle(status?.status)
            : "Analysis unavailable"}
        </h2>
        {loading ? (
          <p className={ui.emptyCopy}>Reading the durable run record.</p>
        ) : null}
        {!loading && run && summaryMessage ? (
          <p className={ui.emptyCopy}>{summaryMessage}</p>
        ) : null}
        {!loading && run && !run.analysis_summary && !reportLoading ? (
          <>
            <AnalysisSummaryPrompt registryRunId={run.registry_run_id} />
          </>
        ) : null}
        {!loading && !run ? (
          <p className={ui.emptyCopy}>
            No completed scientific report is available.
          </p>
        ) : null}
      </section>
      {!loading && run ? (
        <ExecutionObservationPanel
          observation={observation?.execution}
          workflowStatus={observation?.status ?? run.status}
        />
      ) : null}
    </>
  );
}

function analysisStateTitle(status?: string) {
  if (status === "running" || status === "starting")
    return "Analysis in progress";
  if (status === "completed" || status === "already_finished")
    return "Analysis completed";
  return "Analysis not completed";
}
