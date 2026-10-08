import { Icon, type IconName } from "../design-system/Icon";
import { useState } from "react";
import { CopyButton } from "../components/CopyButton";

import ui from "../styles/ui.module.css";
import styles from "./AnalysisReport.module.css";
import { humanize, joinRunPath } from "./format";
import type { ReportArtifact } from "./types";

export function ReportArtifactRow({
  artifact,
  onOpen,
  runDirectory,
}: {
  artifact: ReportArtifact;
  onOpen?: (artifact: ReportArtifact) => void | Promise<void>;
  runDirectory: string;
}) {
  const [opening, setOpening] = useState(false);
  const canOpen = Boolean(onOpen && artifact.openUrl);
  const canCopy = Boolean(artifact.path && !canOpen);
  const openLabel = "Open";

  return (
    <div className={styles.artifactRow}>
      <KindMark kind={artifact.kind} />
      <div className={styles.artifactCopy}>
        <strong>{artifact.title}</strong>
        <p>{artifact.description}</p>
        <small>
          {humanize(artifact.kind)}
          {artifact.size ? ` · ${artifact.size}` : ""}
        </small>
      </div>
      {canOpen ? (
        <button
          aria-label={`${openLabel} ${artifact.title}`}
          className={`${ui.button} ${ui.buttonQuiet}`}
          disabled={opening}
          onClick={() => {
            setOpening(true);
            void Promise.resolve(onOpen?.(artifact)).finally(() =>
              setOpening(false),
            );
          }}
          type="button"
        >
          {opening ? "Opening…" : openLabel}
        </button>
      ) : canCopy && artifact.path ? (
        <CopyButton
          value={joinRunPath(runDirectory, artifact.path)}
          accessibleLabel={`Copy path for ${artifact.title}`}
        />
      ) : null}
    </div>
  );
}

function KindMark({ kind }: { kind: string }) {
  const name: IconName =
    kind === "html_report" || kind === "localhost_app"
      ? "bar-chart"
      : kind === "table"
      ? "square-grid"
      : "upload-documents";
  return (
    <span className={styles.kindMark}>
      <Icon name={name} size={20} />
    </span>
  );
}
