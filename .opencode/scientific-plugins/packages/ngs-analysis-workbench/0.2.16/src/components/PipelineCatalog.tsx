import { Chip } from "../design-system/Chip";
import { useEffect, useRef, useState } from "react";

import { Icon } from "../design-system/Icon";
import { useDialogMotion } from "../design-system/useDialogMotion";

import type { Pipeline } from "../model";
import ui from "../styles/ui.module.css";
import styles from "./PipelineCatalog.module.css";

interface PipelineCatalogProps {
  pipelines: Pipeline[];
  loading: boolean;
  unavailable?: boolean;
}

function pipelineIdentity(pipeline: Pipeline) {
  return `${pipeline.engine ?? "workflow"}:${pipeline.id}`;
}

export function PipelineCatalog({
  pipelines,
  loading,
  unavailable = false,
}: PipelineCatalogProps) {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const selectedPipeline = pipelines.find(
    (pipeline) => pipelineIdentity(pipeline) === selectedWorkflow,
  );
  const groups = [
    {
      title: "Saved pipelines",
      showHeading: true,
      items: pipelines.filter((pipeline) => pipeline.catalog === "saved"),
    },
    {
      title: "Included pipelines",
      showHeading: false,
      items: pipelines.filter((pipeline) => pipeline.catalog !== "saved"),
    },
  ];

  useEffect(() => {
    if (selectedPipeline && dialogRef.current && !dialogRef.current.open) {
      dialogRef.current.showModal();
    }
  }, [selectedPipeline]);

  const closeDetails = useDialogMotion(dialogRef);

  function handleDialogClosed() {
    setSelectedWorkflow(undefined);
    queueMicrotask(() => triggerRef.current?.focus());
  }

  return (
    <section className={styles.catalog} aria-label="Pipeline library">
      {!pipelines.length ? (
        <p className={ui.emptyCopy} role={loading ? "status" : undefined}>
          {loading
            ? "Loading pipelines…"
            : unavailable
            ? "The pipeline library is unavailable."
            : "No pipelines are available."}
        </p>
      ) : (
        groups.map(({ title, items, showHeading }) =>
          items.length ? (
            <section className={styles.group} key={title} aria-label={title}>
              {showHeading ? (
                <h3 className={styles.groupTitle}>{title}</h3>
              ) : null}
              <ul className={styles.pipelineList}>
                {items.map((pipeline) => {
                  const identity = pipelineIdentity(pipeline);

                  return (
                    <li className={styles.pipelineItem} key={identity}>
                      <button
                        aria-haspopup="dialog"
                        className={styles.pipelineCard}
                        onClick={(event) => {
                          triggerRef.current = event.currentTarget;
                          setSelectedWorkflow(identity);
                        }}
                        type="button"
                      >
                        <span className={styles.pipelineIdentity}>
                          <span className={styles.pipelineTitle}>
                            {pipeline.title}
                          </span>
                          <span className={styles.pipelineWorkflow}>
                            {pipeline.sourceKind === "local"
                              ? pipeline.id
                              : pipeline.workflow}
                          </span>
                          {pipeline.description ? (
                            <span className={styles.pipelineDescription}>
                              {pipeline.description}
                            </span>
                          ) : null}
                        </span>
                        <span className={styles.badges}>
                          {pipeline.engine ? (
                            <Chip>
                              {pipeline.engine === "nextflow"
                                ? "Nextflow"
                                : "Snakemake"}
                            </Chip>
                          ) : null}
                          {pipeline.collection ? (
                            <Chip>{pipeline.collection}</Chip>
                          ) : null}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          ) : null,
        )
      )}

      {selectedPipeline ? (
        <dialog
          aria-labelledby="workflow-details-title"
          aria-modal="true"
          className={styles.detailsDialog}
          onClick={(event) => {
            if (event.target === event.currentTarget) closeDetails();
          }}
          onClose={handleDialogClosed}
          onKeyDown={(event) => {
            if (event.key === "Escape") {
              event.preventDefault();
              closeDetails();
            }
          }}
          onCancel={(event) => {
            event.preventDefault();
            closeDetails();
          }}
          ref={dialogRef}
        >
          <header className={styles.dialogHeader}>
            <div className={styles.dialogIdentity}>
              <span className={styles.pipelineWorkflow}>
                {selectedPipeline.sourceKind === "local"
                  ? selectedPipeline.id
                  : selectedPipeline.workflow}
              </span>
              <h3 id="workflow-details-title">{selectedPipeline.title}</h3>
            </div>
            <button
              aria-label="Close pipeline details"
              className={`${ui.button} ${ui.buttonQuiet} ${ui.iconButton}`}
              onClick={closeDetails}
              type="button"
            >
              <Icon name="close-medium" size={20} />
            </button>
          </header>
          {selectedPipeline.description ? (
            <p className={styles.dialogDescription}>
              {selectedPipeline.description}
            </p>
          ) : null}
          <dl className={styles.details}>
            <dt>Source</dt>
            <dd>
              {selectedPipeline.sourceKind === "local"
                ? "Local pipeline"
                : selectedPipeline.workflow}
            </dd>
            {selectedPipeline.entrypoint ? (
              <>
                <dt>Entrypoint</dt>
                <dd>{selectedPipeline.entrypoint}</dd>
              </>
            ) : null}
            {selectedPipeline.revision ? (
              <>
                <dt>Revision</dt>
                <dd>{selectedPipeline.revision}</dd>
              </>
            ) : null}
            {selectedPipeline.sourceSha256 ? (
              <>
                <dt>Source SHA-256</dt>
                <dd>{selectedPipeline.sourceSha256}</dd>
              </>
            ) : null}
          </dl>
        </dialog>
      ) : null}
    </section>
  );
}
