export const HISTORY_SUMMARY_CHARACTER_LIMIT = 125;

export function plainTextAnalysisSummary(value: string): string {
  return value
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/(?<!\w)_{1,2}([^_]+)_{1,2}(?!\w)/g, "$1")
    .replace(/[`*~]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function analysisSummaryMessage(
  summary: string | undefined,
  reportLoading: boolean,
  reportError?: string,
): string | undefined {
  if (summary) return plainTextAnalysisSummary(summary);
  if (reportLoading) return "Run information is ready; loading the completed report.";
  return reportError;
}

export function runHistorySummary(value: string): string {
  const summary = plainTextAnalysisSummary(value)
    .split(/(?<=[.!?])\s+(?=[A-Z0-9])/, 1)[0]
    .replace(/(?:…|\.{3})+$/, "")
    .replace(/[,;:]\s*$/, "")
    .trim();
  if (!summary) return "";
  if (
    summary.length <= HISTORY_SUMMARY_CHARACTER_LIMIT &&
    /[.!?]$/.test(summary)
  ) {
    return summary;
  }

  let sentence = summary.replace(/[.!?]+$/, "");
  const limit = HISTORY_SUMMARY_CHARACTER_LIMIT - 1;
  if (sentence.length > limit) {
    let bounded = sentence.slice(0, limit).trimEnd();
    if (!/\s/.test(sentence[limit])) {
      const boundary = bounded.lastIndexOf(" ");
      if (boundary > 0) bounded = bounded.slice(0, boundary);
    }
    sentence = bounded.replace(/[,;:-]\s*$/, "");
  }
  return `${sentence}.`;
}
