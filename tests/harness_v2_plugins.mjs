/**
 * Harness de verificação do contrato de plugins do OpenCode V2 (SPEC-935-R1004).
 *
 * Importa o plugin REAL e:
 *  - `contract`: valida o schema do carregador V2 (`{id, setup|effect}`).
 *  - `acesso`  : executa a ferramenta registrada via `ctx.tool.transform`.
 *  - `deploy`  : executa o hook `ctx.tool.hook("execute.before")`.
 *  - `litert`  : executa `ctx.provider.transform` em dois cenários.
 *
 * Saída: uma linha JSON. Erros de import/setup viram `{ok:false,error}`.
 *
 * Uso: node --experimental-strip-types harness_v2_plugins.mjs <plugin> <mode>
 */
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";

const PLUGIN = process.argv[2];
const MODE = process.argv[3];

function emit(obj) {
  console.log(JSON.stringify(obj));
}

function shapeOf(def) {
  return {
    isObject: typeof def === "object" && def !== null,
    isFunction: typeof def === "function",
    id: def?.id ?? null,
    hasSetup: typeof def?.setup === "function",
    hasEffect: typeof def?.effect === "function",
  };
}

/** Editor de tools mínimo, suficiente para um plugin que só registra definições. */
function makeToolEditor(sink) {
  return {
    list: () => sink.slice(),
    get: () => undefined,
    namespace: () => {},
    add: (tool) => sink.push(tool),
    update: () => {},
    remove: () => {},
  };
}

/** Editor de provider mínimo, com registro das operações para asserção. */
function makeProviderEditor(record, log) {
  return {
    list: () => (record ? [record] : []),
    get: (id) => (record && record.provider.id === id ? record : undefined),
    add: (entry) => {
      log.push({ op: "add", providerID: entry.info.id, models: entry.models.length });
    },
    update: (id, fn) => {
      log.push({ op: "update", providerID: id });
      if (record && record.provider.id === id) fn(record.provider);
    },
    remove: () => {},
    models: {
      set: (id, models) => log.push({ op: "models.set", providerID: id, models: models.length }),
      update: () => {},
      remove: () => {},
    },
  };
}

async function runAcesso(def) {
  const registered = [];
  const ctx = {
    tool: {
      transform: async (cb) => {
        cb(makeToolEditor(registered));
        return { dispose: async () => {} };
      },
    },
  };
  await def.setup(ctx);

  const tool = registered.find((t) => /acesso/.test(t.name));
  if (!tool) return { ok: false, error: "tool_not_registered", registered: registered.map((t) => t.name) };

  const cases = [];
  async function run(label, input, expectThrow) {
    let threw = false;
    let message = "";
    let parsed = null;
    try {
      const result = await tool.execute(input, {});
      const text = typeof result?.content === "string" ? result.content : null;
      parsed = text ? JSON.parse(text) : null;
    } catch (err) {
      threw = true;
      message = String(err?.message ?? err);
    }
    cases.push({ label, threw, expectThrow, message, parsed, pass: threw === expectThrow });
  }

  await run("doi simples", { doi: "10.1371/journal.pone.0024352" }, false);
  await run("doi com prefixo doi.org", { doi: "https://doi.org/10.1038/NATURE12373" }, false);
  await run("doi invalido", { doi: "nao-e-doi" }, true);
  await run("sci-hub bloqueado", { doi: "10.1371/x", pdfUrl: "https://sci-hub.se/paper.pdf" }, true);
  await run("esquema nao http", { doi: "10.1371/x", pdfUrl: "ftp://example.org/a.pdf" }, true);
  await run("url http candidata", { doi: "10.1371/x", pdfUrl: "https://example.org/a.pdf" }, false);

  return {
    ok: cases.every((c) => c.pass),
    tool: { name: tool.name, hasInputSchema: tool.input?.type === "object", required: tool.input?.required },
    cases,
  };
}

async function runDeploy(def) {
  const hooks = new Map();
  const ctx = {
    tool: {
      hook: async (name, cb) => {
        hooks.set(name, cb);
        return { dispose: async () => {} };
      },
    },
  };
  await def.setup(ctx);

  const before = hooks.get("execute.before");
  if (!before) return { ok: false, error: "hook_not_registered", hooks: [...hooks.keys()] };

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "deploy-guards-"));
  const clean = `<!doctype html><html><body><div class="card num">x</div>
<script>var el=document.querySelector('.num');el.textContent='ok';</script></body></html>`;
  const buggy = `<!doctype html><html><body><div class="card num">x</div>
<script>var el=document.querySelector('num');el.textContent='ok';</script></body></html>`;

  const cases = [];
  async function run(label, event, expectThrow) {
    let threw = false;
    let message = "";
    try {
      await before(event);
    } catch (err) {
      threw = true;
      message = String(err?.message ?? err);
    }
    cases.push({ label, threw, expectThrow, message: message.split("\n")[0], pass: threw === expectThrow });
  }

  await run(
    "write V2 (path) html limpo",
    { tool: "write", input: { path: path.join(tmp, "novo-limpo.html"), content: clean } },
    false,
  );
  await run(
    "write V2 (path) bug R580",
    { tool: "write", input: { path: path.join(tmp, "novo-bug.html"), content: buggy } },
    true,
  );

  const alvo = path.join(tmp, "alvo.html");
  fs.writeFileSync(alvo, buggy, "utf8");
  await run(
    "edit V2 corrige o disco",
    { tool: "edit", input: { path: alvo, oldString: "querySelector('num')", newString: "querySelector('.num')" } },
    false,
  );
  await run(
    "edit V2 introduz o bug",
    { tool: "edit", input: { path: alvo, oldString: "querySelector('.num')", newString: "querySelector('num')" } },
    true,
  );

  await run("write sem content (indeterminavel)", { tool: "write", input: { path: path.join(tmp, "x.html") } }, false);
  await run(
    "compat V1 (filePath) bug R580",
    { tool: "write", input: { filePath: path.join(tmp, "v1-bug.html"), content: buggy } },
    true,
  );
  await run("tool irrelevante", { tool: "read", input: { path: "/etc/hostname" } }, false);
  await run("shell sem git", { tool: "shell", input: { command: "echo ok" } }, false);

  return { ok: cases.every((c) => c.pass), cases };
}

async function runLitert(def) {
  const scenario = async (record) => {
    const log = [];
    const ctx = {
      app: { version: "test" },
      location: {
        directory: "/tmp/opencode/harness-litert",
        project: { id: "proj", directory: "/tmp/opencode/harness-litert", canonical: "/tmp/opencode/harness-litert" },
      },
      provider: {
        transform: async (cb) => {
          cb(makeProviderEditor(record, log));
          return { dispose: async () => {} };
        },
      },
    };
    await def.setup(ctx);
    return log;
  };

  const empty = await scenario(null);
  const existing = await scenario({
    provider: { id: "litert-lm", name: "LiteRT-LM", activation: "auto", package: "aisdk:@ai-sdk/openai-compatible" },
    models: new Map(),
  });

  const addEmpty = empty.find((e) => e.op === "add");
  const addExisting = existing.find((e) => e.op === "add");
  const modelsExisting = existing.find((e) => e.op === "models.set");

  return {
    ok:
      Boolean(addEmpty) &&
      addEmpty.models === 4 &&
      !addExisting &&
      Boolean(modelsExisting) &&
      modelsExisting.models === 4,
    empty,
    existing,
  };
}

try {
  const mod = await import(PLUGIN);
  const def = mod.default;

  if (MODE === "contract") {
    const shape = shapeOf(def);
    emit({ ok: shape.isObject && !!shape.id && (shape.hasSetup || shape.hasEffect), shape });
  } else if (!shapeOf(def).isObject) {
    emit({ ok: false, error: "default_is_not_object", shape: shapeOf(def) });
  } else if (MODE === "acesso") {
    emit(await runAcesso(def));
  } else if (MODE === "deploy") {
    emit(await runDeploy(def));
  } else if (MODE === "litert") {
    emit(await runLitert(def));
  } else {
    emit({ ok: false, error: `unknown_mode:${MODE}` });
  }
} catch (err) {
  emit({ ok: false, error: String(err?.stack ?? err) });
}
