export type ReportTone = "neutral" | "success" | "warning" | "danger";

export interface ReportMetric {
  label: string;
  value: string;
  detail?: string;
  tone?: ReportTone;
}

export interface ReportArtifact {
  id: string;
  title: string;
  path?: string;
  openUrl?: string;
  kind: string;
  status: "created" | "not_available" | "blocked";
  description: string;
  size?: string;
}

export interface AnalysisReportData {
  title: string;
  description: string;
  summary: string;
  completedAt: string;
  duration?: string;
  runDirectory: string;
  artifactCount: number;
  artifactCountTruncated?: boolean;
  metrics: ReportMetric[];
  warnings: string[];
  entries: ReportArtifact[];
  notes: string[];
  provenance: Array<{ label: string; value: string }>;
  sources: ReportSource[];
}

export interface ReportSource {
  label: string;
  path: string;
}
