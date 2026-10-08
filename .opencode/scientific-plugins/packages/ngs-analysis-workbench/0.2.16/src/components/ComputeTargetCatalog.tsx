import { Icon } from "../design-system/Icon";
import { Chip } from "../design-system/Chip";
import { useDialogMotion } from "../design-system/useDialogMotion";
import { Fragment, useEffect, useRef, useState } from "react";

import type { ComputeTarget } from "../model";
import ui from "../styles/ui.module.css";
import styles from "./ComputeTargetCatalog.module.css";

export function ComputeTargetCatalog({
  targets,
  loading,
  error,
}: {
  targets?: ComputeTarget[];
  loading: boolean;
  error?: string;
}) {
  const [selectedId, setSelectedId] = useState<string>();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const selected = targets?.find((target) => target.target_id === selectedId);

  useEffect(() => {
    if (selected && dialogRef.current && !dialogRef.current.open)
      dialogRef.current.showModal();
    if (selectedId && targets && !selected) {
      setSelectedId(undefined);
      queueMicrotask(() => triggerRef.current?.focus());
    }
  }, [selected, selectedId, targets]);

  const closeDetails = useDialogMotion(dialogRef);
  return (
    <section className={styles.root} aria-label="Configured compute targets">
      {error ? (
        <p className={styles.notice} role="alert">
          {error}
          {targets?.length ? " Showing previously loaded targets." : ""}
        </p>
      ) : null}
      {targets?.length ? (
        <>
          <h3 className={ui.sectionLabel}>Configured targets</h3>
          <ul className={styles.list}>
            {targets.map((target) => (
              <li key={target.target_id}>
                <button
                  aria-haspopup="dialog"
                  className={styles.row}
                  onClick={(event) => {
                    triggerRef.current = event.currentTarget;
                    setSelectedId(target.target_id);
                  }}
                  type="button"
                >
                  <span className={styles.identity}>
                    <strong>{target.title}</strong>
                    <code>{target.target_id}</code>
                  </span>
                  <span className={styles.facts}>
                    {[
                      ...new Set([target.controllerTransport, target.executor]),
                    ].map((fact) => (
                      <Chip key={fact}>{label(fact)}</Chip>
                    ))}
                  </span>
                  <span className={styles.state}>
                    {target.target_id === "local" ? "Built in" : "Configured"}
                  </span>
                  <Icon name="chevron-right-sm" size={16} />
                </button>
              </li>
            ))}
          </ul>
          <p className={styles.note}>
            Target configuration is managed through Codex. Configured does not
            mean workflow-ready.
          </p>
        </>
      ) : !error ? (
        <p className={styles.notice} role={loading ? "status" : undefined}>
          {loading
            ? "Loading compute targets…"
            : "No compute targets are available."}
        </p>
      ) : null}
      {selected ? (
        <dialog
          aria-labelledby="compute-target-title"
          className={styles.dialog}
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
          onClick={(event) => {
            if (event.target === event.currentTarget) closeDetails();
          }}
          onClose={() => {
            setSelectedId(undefined);
            queueMicrotask(() => triggerRef.current?.focus());
          }}
          ref={dialogRef}
        >
          <header>
            <div>
              <code>{selected.target_id}</code>
              <h3 id="compute-target-title">{selected.title}</h3>
            </div>
            <button
              aria-label="Close"
              className={`${ui.button} ${ui.buttonQuiet} ${ui.iconButton}`}
              onClick={closeDetails}
              type="button"
            >
              <Icon name="close-medium" size={20} />
            </button>
          </header>
          <p>{selected.description}</p>
          <dl>
            <dt>Transport</dt>
            <dd>{label(selected.controllerTransport)}</dd>
            <dt>Executor</dt>
            <dd>{label(selected.executor)}</dd>
            <dt>Workspace access</dt>
            <dd>{label(selected.workspaceAccess)}</dd>
            {selected.workspaceRoot ? (
              <>
                <dt>Workspace root</dt>
                <dd>{selected.workspaceRoot}</dd>
              </>
            ) : null}
            {Object.entries(selected.executorConfiguration).map(
              ([key, value]) => (
                <Fragment key={key}>
                  <dt>{label(key)}</dt>
                  <dd>{value}</dd>
                </Fragment>
              ),
            )}
          </dl>
          <small>Workflow readiness is checked separately for each plan.</small>
        </dialog>
      ) : null}
    </section>
  );
}

function label(value: string) {
  if (value === "ssh") return "SSH";
  const words = value.replaceAll("_", " ");
  return words[0]?.toUpperCase() + words.slice(1);
}
