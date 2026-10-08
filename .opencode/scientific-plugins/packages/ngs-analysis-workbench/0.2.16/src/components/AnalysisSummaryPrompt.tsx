import { DisclosureSummary } from "../design-system/DisclosureSummary";
import { CopyButton } from "./CopyButton";
import ui from "../styles/ui.module.css";

export function AnalysisSummaryPrompt({
  registryRunId,
}: {
  registryRunId: string;
}) {
  const prompt = [
    `Analyze NGS run registry_run_id=${JSON.stringify(
      registryRunId,
    )} using the understand-ngs-results skill.`,
    "First call get_ngs_run for this ID to read its durable lifecycle, target, run_dir, and plan checksum.",
    "If still active, use run-ngs-analysis and observe_ngs_run to monitor this same run until terminal.",
    "Follow the skill to verify the target and inspect relevant outputs under <run_dir>/results, using SSH for a remote target.",
    "Write an evidence-grounded report to a local Markdown file, then call update_ngs_run_analysis_summary with this registry_run_id and the file's absolute summary_path.",
    "Return the analysis or the precise blocker in conversation. Do not start a replacement run.",
  ].join(" ");

  return (
    <details className={ui.disclosure}>
      <DisclosureSummary>Ask Codex to analyze this run</DisclosureSummary>
      <p>{prompt}</p>
      <CopyButton
        value={prompt}
        label="Copy analysis prompt"
        failureLabel="Select the prompt above to copy"
        variant="secondary"
      />
    </details>
  );
}
