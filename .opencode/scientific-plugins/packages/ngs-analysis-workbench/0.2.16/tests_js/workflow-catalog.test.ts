import assert from "node:assert/strict";
import { after, before, test } from "node:test";

import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer, type ViteDevServer } from "vite";

let server: ViteDevServer;
let listPipelines: (client: {
  call: (name: string, parameters: Record<string, unknown>) => Promise<unknown>;
}) => Promise<Array<Record<string, unknown>>>;
let listComputeTargets: (client: {
  call: (name: string, parameters: Record<string, unknown>) => Promise<unknown>;
}) => Promise<Array<Record<string, unknown>>>;
let PipelineCatalog: (properties: Record<string, unknown>) => unknown;
let ComputeTargetCatalog: (properties: Record<string, unknown>) => unknown;
let NgsWorkbenchSurface: (properties: Record<string, unknown>) => unknown;
let useNgsWorkbench: typeof import("../src/hooks/useNgsWorkbench.ts").useNgsWorkbench;
let groupRunLineages: (runs: Array<Record<string, unknown>>) => Array<{
  id: string;
  latest: Record<string, unknown>;
  runs: Array<Record<string, unknown>>;
}>;

const payload = {
  workflows: [
    {
      workflow_id: "rnaseq",
      name: "Included Nextflow RNA-seq",
      engine: "nextflow",
      description: "Curated RNA-seq alignment and quantification.",
      catalog: "bundled",
      collection: "nf-core",
      source: { kind: "remote", workflow: "nf-core/rnaseq", revision: "3.26.0" },
    },
    {
      workflow_id: "oai_bulk_rnaseq_counts_qc",
      name: "Included Snakemake RNA-seq",
      engine: "snakemake",
      description: "Bundled RNA-seq quantification.",
      catalog: "bundled",
      source: {
        kind: "local",
        root: "/private/plugin/workflows/rnaseq",
        entrypoint: "workflow/Snakefile",
        source_sha256: `sha256:${"c".repeat(64)}`,
      },
    },
    {
      workflow_id: "lab_rna_quant",
      name: "Saved laboratory RNA-seq",
      engine: "snakemake",
      description: null,
      catalog: "user",
      source: {
        kind: "local",
        root: "/Users/private/workflows/lab_rna_quant",
        entrypoint: "Snakefile",
        source_sha256: `sha256:${"a".repeat(64)}`,
      },
    },
  ],
};

const targetPayload = {
  count: 2,
  targets: [
    {
      target_id: "local",
      title: "This computer",
      provider: "ngs-analysis-workbench",
      controller_transport: "local_process",
      executor: "local_process",
      workspace_access: "local_filesystem",
      description: "Run the workflow controller on this computer.",
    },
    {
      target_id: "research-slurm",
      title: "Research Slurm",
      provider: "ngs-compute",
      controller_transport: "ssh",
      executor: "slurm",
      workspace_access: "remote_filesystem",
      description: "Run a workflow controller through SSH.",
      workspace_root: "/shared/rosalind",
      executor_configuration: { partition: "genomics" },
    },
  ],
};

before(async () => {
  server = await createServer({
    appType: "custom",
    configFile: false,
    logLevel: "silent",
    server: { middlewareMode: true },
  });
  ({ listComputeTargets, listPipelines } = await server.ssrLoadModule("/src/mcp/ngs.ts"));
  ({ PipelineCatalog } = await server.ssrLoadModule("/src/components/PipelineCatalog.tsx"));
  ({ ComputeTargetCatalog } = await server.ssrLoadModule("/src/components/ComputeTargetCatalog.tsx"));
  ({ NgsWorkbenchSurface } = await server.ssrLoadModule("/src/App.tsx"));
  ({ useNgsWorkbench } = await server.ssrLoadModule("/src/hooks/useNgsWorkbench.ts"));
  ({ groupRunLineages } = await server.ssrLoadModule("/src/components/RunHistory.tsx"));
});

after(async () => {
  await server?.close();
});

async function workflows() {
  return listPipelines({
    async call(name, parameters) {
      assert.equal(name, "list_workflows");
      assert.deepEqual(parameters, {});
      return payload;
    },
  });
}

async function computeTargets() {
  return listComputeTargets({
    async call(name, parameters) {
      assert.equal(name, "list_compute_target_summaries");
      assert.deepEqual(parameters, {});
      return targetPayload;
    },
  });
}

test("maps public workflow identity and nested source only at the UI boundary", async () => {
  const entries = await workflows();
  const saved = entries.find((workflow) => workflow.id === "lab_rna_quant");

  assert.equal(saved?.catalog, "saved");
  assert.equal(saved?.sourceKind, "local");
  assert.equal(saved?.description, "");
  assert.equal(saved?.entrypoint, "Snakefile");
  assert.equal(saved?.workflow, "/Users/private/workflows/lab_rna_quant");
  assert.equal(saved?.sourceSha256, payload.workflows[2].source.source_sha256);
  assert.equal(entries[0]?.revision, "3.26.0");
});

test("groups executions by first run and selects the greatest workflow attempt", () => {
  const runs = [
    {
      registry_run_id: "latest", run_id: "run-b", first_run_id: "run-a",
      attempt_number: 2, binding: "nextflow", created_at_ms: 20,
      updated_at_ms: 30,
    },
    {
      registry_run_id: "older", run_id: "run-a", first_run_id: "run-a",
      attempt_number: 1, binding: "nextflow", created_at_ms: 10,
      updated_at_ms: 100,
    },
    { registry_run_id: "unlinked", run_id: "run-c", first_run_id: "run-c",
      attempt_number: 1, binding: "nextflow", created_at_ms: 15, updated_at_ms: 40 },
  ];

  const grouped = groupRunLineages(runs);

  assert.equal(grouped.length, 2);
  assert.deepEqual(grouped[0].runs.map((run) => run.registry_run_id), ["older", "latest"]);
  assert.equal(grouped[0].latest.registry_run_id, "latest");
  assert.equal(grouped[1].id, "run-c");
});

test("loads drawer history using only the first run ID", async () => {
  const attempts = [{ registry_run_id: "first" }, { registry_run_id: "latest" }];
  const client = {
    async call(name: string, parameters: Record<string, unknown>) {
      assert.equal(name, "list_ngs_runs");
      assert.deepEqual(parameters, { first_run_id: "run-a", limit: 200 });
      return { ok: true, runs: attempts };
    },
  } as Parameters<typeof useNgsWorkbench>[0];
  let loadRunLineage: ReturnType<typeof useNgsWorkbench>["loadRunLineage"];
  function Harness() {
    ({ loadRunLineage } = useNgsWorkbench(client));
    return null;
  }
  renderToStaticMarkup(createElement(Harness));
  const selected = {
    registry_run_id: "latest", run_id: "run-b", first_run_id: "run-a", binding: "nextflow",
  } as Parameters<typeof loadRunLineage>[0];
  assert.deepEqual(await loadRunLineage!(selected), attempts);
});

test("shows user workflows first and keeps engine metadata reviewable", async () => {
  const html = renderToStaticMarkup(createElement(PipelineCatalog, {
    pipelines: await workflows(),
    loading: false,
  }));

  assert.ok(html.indexOf("Saved laboratory RNA-seq") < html.indexOf("Included Nextflow RNA-seq"));
  assert.ok(html.includes("Included Nextflow RNA-seq"));
  assert.ok(html.includes("Included Snakemake RNA-seq"));
  assert.ok(!html.includes("/private/plugin"));
  assert.ok(!html.includes("/Users/private"));
});

test("distinguishes the loading catalog from an actually empty catalog", () => {
  const loading = renderToStaticMarkup(createElement(PipelineCatalog, {
    pipelines: [],
    loading: true,
  }));
  const empty = renderToStaticMarkup(createElement(PipelineCatalog, {
    pipelines: [],
    loading: false,
  }));

  assert.ok(loading.includes('role="status"'));
  assert.ok(loading.includes("Loading pipelines"));
  assert.ok(!loading.includes("No pipelines are available"));
  assert.ok(empty.includes("No pipelines are available"));
  assert.ok(!empty.includes('role="status"'));
});

test("makes Pipelines a primary page while keeping the Runs page available", async () => {
  const workbench = {
    connected: true,
    displayMode: "inline",
    catalogLoading: false,
    pipelines: await workflows(),
    loadCatalog: async () => undefined,
    dismissError: () => undefined,
  };
  const html = renderToStaticMarkup(createElement(NgsWorkbenchSurface, {
    initialPage: "workflows",
    workbench,
  }));

  assert.match(html, /<button[^>]*>Runs<\/button>/);
  assert.match(html, /<button[^>]*aria-current="page"[^>]*>Pipelines<\/button>/);
  assert.ok(html.includes("Saved laboratory RNA-seq"));
  assert.ok(html.includes("Included Nextflow RNA-seq"));
});

test("makes Compute a primary page and lists configuration without readiness claims", async () => {
  const targets = await computeTargets();
  const html = renderToStaticMarkup(createElement(NgsWorkbenchSurface, {
    initialPage: "compute",
    workbench: {
      connected: true,
      displayMode: "inline",
      computeTargets: targets,
      targetsError: undefined,
      targetsLoading: false,
      loadComputeTargets: async () => undefined,
      dismissError: () => undefined,
    },
  }));

  assert.match(html, /<button[^>]*>Runs<\/button>/);
  assert.match(html, /<button[^>]*>Pipelines<\/button>/);
  assert.match(html, /<button[^>]*aria-current="page"[^>]*>Compute<\/button>/);
  assert.ok(html.includes("This computer"));
  assert.ok(html.includes("Research Slurm"));
  assert.ok(html.includes("Configured does not mean workflow-ready"));
  assert.ok(html.includes('aria-haspopup="dialog"'));
  assert.ok(!html.includes("Ready"));
});

test("does not present an unavailable target inventory as empty", () => {
  const html = renderToStaticMarkup(createElement(ComputeTargetCatalog, {
    targets: undefined,
    loading: false,
    error: "Could not load compute targets.",
  }));

  assert.ok(html.includes('role="alert"'));
  assert.ok(html.includes("Could not load compute targets."));
  assert.ok(!html.includes("No compute targets are available"));
});

test("keeps target details configuration-only", async () => {
  const html = renderToStaticMarkup(createElement(ComputeTargetCatalog, {
    targets: await computeTargets(),
    loading: false,
  }));

  assert.ok(html.includes("Local process"));
  assert.equal(html.match(/Local process/g)?.length, 1);
  assert.ok(html.includes("Slurm"));
  assert.ok(!html.includes("config_hash"));
  assert.ok(!html.includes("host_access"));
});

test("does not present a disconnected catalog as an empty pipeline library", () => {
  const html = renderToStaticMarkup(createElement(NgsWorkbenchSurface, {
    initialPage: "workflows",
    workbench: {
      connected: false,
      displayMode: "inline",
      catalogLoading: false,
      pipelines: [],
      error: "The MCP host is unavailable.",
      loadCatalog: async () => undefined,
      dismissError: () => undefined,
    },
  }));

  assert.ok(html.includes("pipeline library is unavailable"));
  assert.ok(!html.includes("No pipelines are available"));
});
