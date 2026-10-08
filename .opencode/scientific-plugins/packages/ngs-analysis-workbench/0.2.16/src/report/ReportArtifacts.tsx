import { Chip } from "../design-system/Chip";
import styles from "./AnalysisReport.module.css";
import { ReportArtifactRow } from "./ReportArtifactRow";
import type { ReportArtifact } from "./types";

export function ReportArtifacts({
  reviewArtifacts,
  outputArtifacts,
  runDirectory,
  onOpenArtifact,
}: {
  reviewArtifacts: ReportArtifact[];
  outputArtifacts: ReportArtifact[];
  runDirectory: string;
  onOpenArtifact?: (artifact: ReportArtifact) => void | Promise<void>;
}) {
  return (
    <>
      {reviewArtifacts.length ? (
        <section
          className={styles.section}
          aria-labelledby="report-review-heading"
        >
          <div className={styles.sectionHeading}>
            <div>
              <h3 id="report-review-heading">Review</h3>
            </div>
          </div>
          <div className={styles.reviewList}>
            {reviewArtifacts.map((artifact) => (
              <ReportArtifactRow
                artifact={artifact}
                key={artifact.id}
                onOpen={onOpenArtifact}
                runDirectory={runDirectory}
              />
            ))}
          </div>
        </section>
      ) : null}

      <section
        className={styles.section}
        aria-labelledby="report-outputs-heading"
      >
        <div className={styles.sectionHeading}>
          <div>
            <h3 id="report-outputs-heading">Key outputs</h3>
          </div>
          <Chip>{outputArtifacts.length}</Chip>
        </div>
        <div className={styles.artifactList}>
          {outputArtifacts.map((artifact) => (
            <ReportArtifactRow
              artifact={artifact}
              key={artifact.id}
              onOpen={onOpenArtifact}
              runDirectory={runDirectory}
            />
          ))}
        </div>
      </section>
    </>
  );
}
