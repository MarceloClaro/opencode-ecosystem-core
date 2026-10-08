import type { AnalysisReportData, ReportArtifact } from "./types";
import { ReportArtifacts } from "./ReportArtifacts";
import { ReportDetails } from "./ReportDetails";
import { ReportHeader } from "./ReportHeader";
import { ReportNarrative } from "./ReportNarrative";
import styles from "./AnalysisReport.module.css";

interface AnalysisReportProps {
  report: AnalysisReportData;
  runId: string;
  registryRunId: string;
  onOpenArtifact?: (artifact: ReportArtifact) => void | Promise<void>;
}

const REVIEW_KINDS = new Set(["html_report", "localhost_app", "notebook"]);

export function AnalysisReport({
  report,
  runId,
  registryRunId,
  onOpenArtifact,
}: AnalysisReportProps) {
  const reviewArtifacts = report.entries.filter(
    (entry) => entry.status === "created" && REVIEW_KINDS.has(entry.kind),
  );
  const outputArtifacts = report.entries.filter(
    (entry) => entry.status === "created" && !REVIEW_KINDS.has(entry.kind),
  );
  return (
    <article className={styles.results} aria-labelledby="analysis-report-heading">
      <ReportHeader
        featuredArtifact={reviewArtifacts.find((entry) => entry.openUrl)}
        onOpenArtifact={onOpenArtifact}
        report={report}
        runId={runId}
      />

      <div className={styles.contentGrid}>
        <div className={styles.mainColumn}>
          <ReportNarrative report={report} registryRunId={registryRunId} />
          <ReportArtifacts
            onOpenArtifact={onOpenArtifact}
            outputArtifacts={outputArtifacts}
            reviewArtifacts={reviewArtifacts}
            runDirectory={report.runDirectory}
          />
        </div>

        <ReportDetails report={report} />
      </div>
    </article>
  );
}
