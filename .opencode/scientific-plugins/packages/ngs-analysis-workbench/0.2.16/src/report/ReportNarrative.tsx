import { Icon } from "../design-system/Icon";
import styles from "./AnalysisReport.module.css";
import type { AnalysisReportData } from "./types";
import { AnalysisSummaryPrompt } from "../components/AnalysisSummaryPrompt";
import { plainTextAnalysisSummary } from "../analysisSummary";

export function ReportNarrative({
  report,
  registryRunId,
}: {
  report: AnalysisReportData;
  registryRunId: string;
}) {
  return (
    <>
      <section
        className={styles.section}
        aria-labelledby="report-summary-heading"
      >
        <h3 id="report-summary-heading">Analysis summary</h3>
        {report.summary ? (
          <p className={styles.summary}>
            {plainTextAnalysisSummary(report.summary)}
          </p>
        ) : (
          <AnalysisSummaryPrompt registryRunId={registryRunId} />
        )}
      </section>

      {report.warnings.length ? (
        <section
          className={styles.warning}
          aria-labelledby="report-warning-heading"
        >
          <Icon className={styles.warningIcon} name="info-sm" size={20} />
          <div>
            <h3 id="report-warning-heading">Review recommended</h3>
            <ul>
              {report.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          </div>
        </section>
      ) : null}
    </>
  );
}
