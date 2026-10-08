import { CopyButton } from "../components/CopyButton";
import { DisclosureSummary } from "../design-system/DisclosureSummary";
import { Fragment, useRef } from "react";

import styles from "./AnalysisReport.module.css";
import ui from "../styles/ui.module.css";
import type { AnalysisReportData } from "./types";

export function ReportDetails({ report }: { report: AnalysisReportData }) {
  const artifactIndexRef = useRef<HTMLDetailsElement>(null);

  const browseRunFiles = () => {
    const artifactIndex = artifactIndexRef.current;
    if (!artifactIndex) return;
    artifactIndex.open = true;
    artifactIndex.scrollIntoView({
      behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "instant"
        : "smooth",
      block: "nearest",
    });
  };

  return (
    <aside className={styles.sideColumn} aria-label="Analysis details">
      <section
        className={styles.runLocation}
        aria-labelledby="report-run-location-heading"
      >
        <h3 id="report-run-location-heading">Run folder</h3>
        <div className={styles.runDirectory}>
          <code title={report.runDirectory}>{report.runDirectory}</code>
          <div
            className={styles.runDirectoryActions}
            role="group"
            aria-label="Run folder actions"
          >
            <CopyButton
              value={report.runDirectory}
              accessibleLabel="Copy run folder path"
              variant="secondary"
            />
            <button
              aria-controls="report-artifact-index"
              aria-label="Browse run files"
              className={`${ui.button} ${ui.buttonSecondary}`}
              onClick={browseRunFiles}
              title="Browse run files"
              type="button"
            >
              Browse files
            </button>
          </div>
        </div>
      </section>

      {report.notes.length ? (
        <section className={styles.notes}>
          <h3>Notes</h3>
          <ul>
            {report.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </section>
      ) : null}

      <div className={styles.disclosureGroup}>
        <details className={`${styles.disclosure} ${styles.runData}`}>
          <DisclosureSummary chevronPosition="end">
            Data sources
          </DisclosureSummary>
          <dl>
            {report.sources.map((source) => (
              <DataSource
                key={source.path}
                label={source.label}
                value={source.path}
              />
            ))}
          </dl>
        </details>

        <details className={styles.disclosure}>
          <DisclosureSummary chevronPosition="end">
            Methods and provenance
          </DisclosureSummary>
          <dl>
            {report.provenance.map((item) => (
              <div key={item.label}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        </details>
        <details
          className={styles.disclosure}
          id="report-artifact-index"
          ref={artifactIndexRef}
        >
          <DisclosureSummary chevronPosition="end">
            Artifact index ({report.artifactCount}
            {report.artifactCountTruncated ? "+" : ""})
          </DisclosureSummary>
          {report.entries.length < report.artifactCount ||
          report.artifactCountTruncated ? (
            <p className={styles.artifactPreviewNote}>
              Showing {report.entries.length} of {report.artifactCount}
              {report.artifactCountTruncated ? "+" : ""} files.
            </p>
          ) : null}
          <ul className={styles.allArtifacts}>
            {report.entries.map((entry) => (
              <li key={entry.id}>
                <span>{entry.title}</span>
                <small title={entry.path}>{entry.path}</small>
              </li>
            ))}
          </ul>
        </details>
      </div>
    </aside>
  );
}

function DataSource({ label, value }: { label: string; value: string }) {
  const segments = value.split("/");
  return (
    <div>
      <dt>{label}</dt>
      <dd title={value}>
        {segments.map((segment, index) => (
          <Fragment key={index}>
            <span className={styles.pathSegment}>
              {segment}
              {index < segments.length - 1 ? "/" : ""}
            </span>
            {index < segments.length - 1 ? <wbr /> : null}
          </Fragment>
        ))}
      </dd>
    </div>
  );
}
