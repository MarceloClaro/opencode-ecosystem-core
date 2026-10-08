import { Tabs } from "@base-ui/react/tabs";
import { Icon, StatusIcon } from "../design-system/Icon";
import { useDialogMotion } from "../design-system/useDialogMotion";
import { useEffect, useRef, useState, type RefObject } from "react";

import type { RunDetail, RunObservation, RunSummary } from "../model";
import { isActiveRunStatus, runStatusPresentation } from "../runStatus";
import { RunStatus } from "./RunStatus";
import styles from "./RunHistorySidebar.module.css";

const TAB_EDGE_FADE = 24;

function revealTab(list: HTMLElement, tab: HTMLElement) {
  const left = tab.offsetLeft;
  const right = left + tab.offsetWidth;
  if (left < list.scrollLeft + TAB_EDGE_FADE) {
    list.scrollLeft = Math.max(0, left - TAB_EDGE_FADE);
  } else if (right > list.scrollLeft + list.clientWidth - TAB_EDGE_FADE) {
    list.scrollLeft = right - list.clientWidth + TAB_EDGE_FADE;
  }
}

export function AttemptsToggle({
  attemptCount,
  buttonRef,
  modal = false,
  onClick,
  open,
}: {
  attemptCount: number;
  buttonRef?: RefObject<HTMLButtonElement | null>;
  modal?: boolean;
  onClick: () => void;
  open: boolean;
}) {
  return (
    <button
      aria-label={open ? "Close run history" : "Open run history"}
      aria-controls="run-attempts-panel"
      aria-expanded={open}
      aria-haspopup={modal && !open ? "dialog" : undefined}
      className={styles.historyToggle}
      onClick={onClick}
      ref={buttonRef}
      type="button"
    >
      <span>Run history · {attemptCount}</span>
      <Icon name="menu" size={16} />
    </button>
  );
}

export function RunHistorySidebar({
  analysisLoading,
  analysisObservation,
  analysisRun,
  executionInMain = false,
  lineageHead,
  loadRunDetail,
  loadRunLineage,
  loadRunObservation,
  observationError,
  open,
  modal,
  onClose,
  toggleRef,
  onRefreshAnalysis,
  refreshingAnalysis,
}: {
  analysisLoading: boolean;
  analysisObservation?: RunObservation;
  analysisRun?: RunDetail;
  executionInMain?: boolean;
  lineageHead: RunSummary;
  loadRunDetail: (run: RunSummary) => Promise<RunDetail>;
  loadRunLineage: (run: RunSummary) => Promise<RunSummary[]>;
  loadRunObservation: (run: RunSummary) => Promise<RunObservation>;
  observationError?: { registryRunId: string; message: string };
  open: boolean;
  modal: boolean;
  onClose: () => void;
  toggleRef: RefObject<HTMLButtonElement | null>;
  onRefreshAnalysis: () => void;
  refreshingAnalysis: boolean;
}) {
  const [attempts, setAttempts] = useState<RunSummary[]>([lineageHead]);
  const multipleAttempts = attempts.length > 1;
  const [selectedAttemptId, setSelectedAttemptId] = useState(
    lineageHead.registry_run_id,
  );
  const [detailCache, setDetailCache] = useState<Record<string, RunDetail>>({});
  const [observationCache, setObservationCache] = useState<
    Record<string, RunObservation>
  >({});
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string>();
  const detailRequestId = useRef(0);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const closeDialog = useDialogMotion(dialogRef);
  const tabListRef = useRef<HTMLDivElement>(null);
  const [tabOverflow, setTabOverflow] = useState({ left: false, right: false });

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!modal || !dialog) return;
    if (open && !dialog.open) dialog.showModal();
    else if (!open && dialog.open) dialog.close();
  }, [modal, open]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 });
  }, [selectedAttemptId]);

  useEffect(() => {
    if (!open) return;
    const list = tabListRef.current;
    if (!list) return;
    const updateOverflow = () => {
      const left = list.scrollLeft > 1;
      const right = list.scrollLeft + list.clientWidth < list.scrollWidth - 1;
      setTabOverflow((current) =>
        current.left === left && current.right === right
          ? current
          : { left, right },
      );
    };
    const revealSelectedTab = () => {
      const tab = list.querySelector<HTMLElement>('[role="tab"][data-active]');
      if (!tab || !list.clientWidth) return;
      revealTab(list, tab);
      updateOverflow();
    };
    revealSelectedTab();
    // Reopening or resizing the inspector can change the available tab width.
    // Scroll only this strip, without moving the report or drawer vertically.
    const observer = new ResizeObserver(revealSelectedTab);
    observer.observe(list);
    list
      .querySelectorAll('[role="tab"]')
      .forEach((tab) => observer.observe(tab));
    list.addEventListener("scroll", updateOverflow, { passive: true });
    return () => {
      observer.disconnect();
      list.removeEventListener("scroll", updateOverflow);
    };
  }, [attempts.length, selectedAttemptId, open, modal]);

  useEffect(() => {
    let disposed = false;
    setAttempts([lineageHead]);
    setSelectedAttemptId(lineageHead.registry_run_id);
    setDetailCache({});
    setObservationCache({});
    setDetailError(undefined);
    void loadRunLineage(lineageHead)
      .then((loaded) => {
        if (!disposed && loaded.length) {
          const ordered = [...loaded].sort(
            (left, right) => left.attempt_number - right.attempt_number,
          );
          setAttempts(ordered);
          setSelectedAttemptId((current) =>
            ordered.some((attempt) => attempt.registry_run_id === current)
              ? current
              : lineageHead.registry_run_id,
          );
        }
      })
      .catch(() => {
        // The selected execution remains usable if lineage history cannot be loaded.
      });
    return () => {
      disposed = true;
    };
  }, [lineageHead.first_run_id, lineageHead.registry_run_id, loadRunLineage]);

  useEffect(() => {
    setAttempts((current) =>
      current.map((attempt) =>
        attempt.registry_run_id === lineageHead.registry_run_id
          ? lineageHead
          : attempt,
      ),
    );
  }, [lineageHead]);

  useEffect(() => {
    if (
      selectedAttemptId === lineageHead.registry_run_id &&
      analysisRun?.registry_run_id === lineageHead.registry_run_id
    ) {
      setDetailLoading(false);
      setDetailError(undefined);
    }
  }, [analysisRun, lineageHead.registry_run_id, selectedAttemptId]);

  const selectedAttempt =
    attempts.find((attempt) => attempt.registry_run_id === selectedAttemptId) ??
    lineageHead;

  const refreshSelectedObservation = () => {
    const requestId = ++detailRequestId.current;
    setDetailLoading(true);
    setDetailError(undefined);
    void loadRunObservation(selectedAttempt)
      .then((observation) => {
        if (requestId !== detailRequestId.current) return;
        setObservationCache((current) => ({
          ...current,
          [selectedAttemptId]: observation,
        }));
      })
      .catch((error: unknown) => {
        if (requestId !== detailRequestId.current) return;
        setDetailError(
          error instanceof Error
            ? error.message
            : "Could not observe this workflow attempt.",
        );
      })
      .finally(() => {
        if (requestId === detailRequestId.current) setDetailLoading(false);
      });
  };

  const selectAttempt = (attempt: RunSummary) => {
    const requestId = ++detailRequestId.current;
    setSelectedAttemptId(attempt.registry_run_id);
    setDetailError(undefined);
    if (attempt.registry_run_id === lineageHead.registry_run_id) {
      setDetailLoading(false);
      return;
    }
    if (detailCache[attempt.registry_run_id]) {
      setDetailLoading(false);
      return;
    }
    setDetailLoading(true);
    void loadRunDetail(attempt)
      .then((detail) => {
        if (requestId !== detailRequestId.current) return;
        setDetailCache((current) => ({
          ...current,
          [attempt.registry_run_id]: detail,
        }));
      })
      .catch((error: unknown) => {
        if (requestId !== detailRequestId.current) return;
        setDetailError(
          error instanceof Error
            ? error.message
            : "Could not load this workflow attempt.",
        );
      })
      .finally(() => {
        if (requestId === detailRequestId.current) setDetailLoading(false);
      });
  };

  const contents = (
    <Tabs.Root
      className={styles.attemptTabs}
      value={selectedAttemptId}
      onValueChange={(value) => {
        const attempt = attempts.find((item) => item.registry_run_id === value);
        if (attempt) selectAttempt(attempt);
      }}
    >
      <header className={styles.runHistoryPaneHeader}>
        <AttemptsToggle
          attemptCount={lineageHead.attempt_number}
          buttonRef={modal || !open ? undefined : toggleRef}
          onClick={modal ? closeDialog : onClose}
          open
        />
      </header>

      {multipleAttempts ? (
        <div className={styles.tabStrip}>
          <Tabs.List
            className={styles.attemptSelector}
            aria-label="Workflow attempts"
            activateOnFocus={false}
            data-overflow-left={tabOverflow.left}
            data-overflow-right={tabOverflow.right}
            onFocusCapture={(event) => {
              if (
                event.target instanceof HTMLElement &&
                event.target.getAttribute("role") === "tab"
              ) {
                revealTab(event.currentTarget, event.target);
              }
            }}
            ref={tabListRef}
          >
            {attempts.map((attempt) => (
              <Tabs.Tab
                className={styles.attemptTab}
                key={attempt.registry_run_id}
                value={attempt.registry_run_id}
                aria-label={`Attempt ${attempt.attempt_number}: ${
                  runStatusPresentation(attempt.status).label
                }`}
              >
                <span
                  className={styles.attemptStatus}
                  data-tone={runStatusPresentation(attempt.status).tone}
                >
                  <StatusIcon
                    tone={runStatusPresentation(attempt.status).tone}
                    active={isActiveRunStatus(attempt.status)}
                  />
                </span>
                Attempt {attempt.attempt_number}
              </Tabs.Tab>
            ))}
            <Tabs.Indicator className={styles.tabIndicator} />
          </Tabs.List>
        </div>
      ) : null}

      <div className={styles.panelsViewport}>
        {attempts.map((attempt) => {
          const isSelected = attempt.registry_run_id === selectedAttemptId;
          const isAnalysis =
            attempt.registry_run_id === analysisRun?.registry_run_id;
          const detail = isAnalysis
            ? analysisRun
            : detailCache[attempt.registry_run_id];
          const observation = isAnalysis
            ? analysisObservation
            : observationCache[attempt.registry_run_id];
          const error = isSelected
            ? detailError ??
              (observationError?.registryRunId === attempt.registry_run_id
                ? observationError.message
                : undefined)
            : undefined;
          return (
            <Tabs.Panel
              className={styles.paneBody}
              key={attempt.registry_run_id}
              value={attempt.registry_run_id}
              ref={isSelected ? scrollRef : undefined}
              role={multipleAttempts ? "tabpanel" : "region"}
              aria-label={
                multipleAttempts
                  ? undefined
                  : `Attempt ${attempt.attempt_number}: ${
                      runStatusPresentation(attempt.status).label
                    }`
              }
              aria-busy={isSelected && detailLoading}
            >
              {error ? (
                <p className={styles.runHistoryError} role="alert">
                  {error}
                </p>
              ) : null}
              {detail ? (
                <RunStatus
                  busy={
                    isAnalysis
                      ? refreshingAnalysis
                      : isSelected && detailLoading
                  }
                  compact
                  showExecution={!executionInMain || !isAnalysis}
                  observation={observation}
                  onRefresh={
                    isAnalysis ? onRefreshAnalysis : refreshSelectedObservation
                  }
                  run={detail}
                  summary={attempt}
                />
              ) : (
                <section className={styles.attemptLoading} aria-live="polite">
                  <h3>
                    {(isSelected && detailLoading) ||
                    (isAnalysis && analysisLoading)
                      ? `Loading attempt ${attempt.attempt_number}…`
                      : "Attempt details unavailable"}
                  </h3>
                </section>
              )}
            </Tabs.Panel>
          );
        })}
      </div>
    </Tabs.Root>
  );

  return modal ? (
    <dialog
      aria-label="Run history"
      className={styles.drawer}
      id="run-attempts-panel"
      onCancel={(event) => {
        event.preventDefault();
        closeDialog();
      }}
      onKeyDown={(event) => {
        if (event.key === "Escape") {
          event.preventDefault();
          closeDialog();
        }
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) closeDialog();
      }}
      onClose={onClose}
      ref={dialogRef}
    >
      {contents}
    </dialog>
  ) : (
    <aside
      aria-label="Run history"
      className={styles.runHistoryPane}
      hidden={!open}
      id="run-attempts-panel"
    >
      {contents}
    </aside>
  );
}
