import type {
  AnalysisReportData,
  ReportArtifact,
  ReportMetric,
  ReportSource,
  ReportTone,
} from "./types";

const TONES = new Set<ReportTone>(["neutral", "success", "warning", "danger"]);
const STATUSES = new Set<ReportArtifact["status"]>([
  "created",
  "not_available",
  "blocked",
]);

export function parseAnalysisReport(
  value: unknown,
): AnalysisReportData | undefined {
  if (!isRecord(value) || value.schema_version !== 1) return undefined;
  const title = stringValue(value.title);
  const description = stringValue(value.description);
  const summary = stringValue(value.summary);
  const runDirectory = stringValue(value.run_directory);
  const artifactCount = nonnegativeInteger(value.artifact_count);
  if (
    !title ||
    !description ||
    !runDirectory ||
    artifactCount === undefined
  ) {
    return undefined;
  }

  return {
    title,
    description,
    summary,
    completedAt: formatCompletedAt(value.completed_at_ms),
    duration: formatDuration(value.duration_ms),
    runDirectory,
    artifactCount,
    artifactCountTruncated: value.artifact_count_truncated === true,
    metrics: arrayValue(value.metrics).map(parseMetric).filter(isDefined),
    warnings: stringArray(value.warnings),
    entries: arrayValue(value.entries).map(parseArtifact).filter(isDefined),
    notes: stringArray(value.notes),
    provenance: arrayValue(value.provenance)
      .map(parseLabelValue)
      .filter(isDefined),
    sources: arrayValue(value.sources).map(parseSource).filter(isDefined),
  };
}

function parseMetric(value: unknown): ReportMetric | undefined {
  if (!isRecord(value)) return undefined;
  const label = stringValue(value.label);
  const metricValue = stringValue(value.value);
  if (!label || !metricValue) return undefined;
  const tone = stringValue(value.tone);
  return {
    label,
    value: metricValue,
    detail: optionalString(value.detail),
    tone: TONES.has(tone as ReportTone) ? (tone as ReportTone) : undefined,
  };
}

function parseArtifact(value: unknown): ReportArtifact | undefined {
  if (!isRecord(value)) return undefined;
  const id = stringValue(value.id);
  const title = stringValue(value.title);
  const kind = stringValue(value.kind);
  const status = stringValue(value.status);
  const description = stringValue(value.description);
  if (
    !id ||
    !title ||
    !kind ||
    !STATUSES.has(status as ReportArtifact["status"]) ||
    !description
  ) {
    return undefined;
  }
  return {
    id,
    title,
    path: optionalString(value.path),
    openUrl: optionalString(value.open_url),
    kind,
    status: status as ReportArtifact["status"],
    description,
    size: formatBytes(nonnegativeInteger(value.size_bytes)),
  };
}

function parseLabelValue(
  value: unknown,
): { label: string; value: string } | undefined {
  if (!isRecord(value)) return undefined;
  const label = stringValue(value.label);
  const itemValue = stringValue(value.value);
  return label && itemValue ? { label, value: itemValue } : undefined;
}

function parseSource(value: unknown): ReportSource | undefined {
  if (!isRecord(value)) return undefined;
  const label = stringValue(value.label);
  const path = stringValue(value.path);
  return label && path ? { label, path } : undefined;
}

function formatCompletedAt(value: unknown) {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
    return "Completion time unavailable";
  }
  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(new Date(value));
}

function formatDuration(value: unknown) {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0)
    return undefined;
  const seconds = Math.round(value / 1_000);
  const hours = Math.floor(seconds / 3_600);
  const minutes = Math.floor((seconds % 3_600) / 60);
  const remainder = seconds % 60;
  if (hours) return `${hours} hr ${minutes} min`;
  if (minutes) return `${minutes} min ${remainder} sec`;
  return `${remainder} sec`;
}

function formatBytes(value: number | undefined) {
  if (value === undefined) return undefined;
  if (value < 1_024) return `${value} B`;
  if (value < 1_024 ** 2) return `${(value / 1_024).toFixed(1)} KB`;
  if (value < 1_024 ** 3) return `${(value / 1_024 ** 2).toFixed(1)} MB`;
  return `${(value / 1_024 ** 3).toFixed(1)} GB`;
}

function nonnegativeInteger(value: unknown) {
  return typeof value === "number" && Number.isInteger(value) && value >= 0
    ? value
    : undefined;
}

function stringArray(value: unknown) {
  return arrayValue(value).filter(
    (item): item is string => typeof item === "string",
  );
}

function arrayValue(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function stringValue(value: unknown) {
  return typeof value === "string" ? value : "";
}

function optionalString(value: unknown) {
  const string = stringValue(value);
  return string || undefined;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function isDefined<T>(value: T | undefined): value is T {
  return value !== undefined;
}
