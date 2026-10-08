import { StatusChip } from "../design-system/Chip";
import ui from "../styles/ui.module.css";
import styles from "./AnalysisReport.module.css";
import type { AnalysisReportData, ReportArtifact } from "./types";

export function ReportHeader({
  report,
  runId,
  featuredArtifact,
  onOpenArtifact,
}: {
  report: AnalysisReportData;
  runId: string;
  featuredArtifact?: ReportArtifact;
  onOpenArtifact?: (artifact: ReportArtifact) => void | Promise<void>;
}) {
  return (
    <>
      <header className={styles.hero}>
        <StatusChip className={styles.completionLine} tone="success">
          Analysis completed
        </StatusChip>
        <h2 id="analysis-report-heading">{report.title}</h2>
        <p className={styles.description}>{report.description}</p>
        <p className={styles.metadata}>
          <span>{report.completedAt}</span>
          {report.duration ? (
            <>
              <i aria-hidden="true" /> <span>{report.duration}</span>
            </>
          ) : null}
          <i aria-hidden="true" />
          <code>{runId}</code>
        </p>
        {featuredArtifact && onOpenArtifact ? (
          <button
            className={`${ui.button} ${ui.buttonPrimary} ${styles.heroAction}`}
            onClick={() => onOpenArtifact(featuredArtifact)}
            type="button"
          >
            Open {featuredArtifact.title}
          </button>
        ) : null}
      </header>

      <section className={styles.metricGrid} aria-label="Analysis metrics">
        {report.metrics.map((metric) => (
          <div
            className={styles.metric}
            data-tone={metric.tone ?? "neutral"}
            key={metric.label}
          >
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            {metric.detail ? <small>{metric.detail}</small> : null}
          </div>
        ))}
      </section>
    </>
  );
}
