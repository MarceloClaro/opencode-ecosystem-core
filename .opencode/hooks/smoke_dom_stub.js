#!/usr/bin/env node
/**
 * smoke_dom_stub.js — Smoke test de JS inline com stub de DOM em Node.
 * ---------------------------------------------------------------------
 * Extrai blocos <script> (sem src) de um arquivo .html e os executa num
 * contexto com um DOM mínimo INSTRUMENTADO que espelha o HTML real:
 *   - ids, classes e tags presentes no arquivo são resolvíveis;
 *   - seletores que NÃO existem no DOM retornam null (como no browser);
 *   - elementos <audio> têm superfície de API (paused/play/pause/...).
 *
 * Detecta a classe de bug observada no ciclo R580: `'num'` (sem ponto) em
 * vez de `'.num'` — seletor inexistente → null → TypeError em runtime que
 * `node --check` NÃO captura.
 *
 * Uso:
 *   node smoke_dom_stub.js arquivo.html [--assert-count N] [--selector .card]
 *
 * Exit: 0 = ok; 1 = exceção de runtime ou contagem divergente.
 */
const fs = require("fs");
const vm = require("vm");

const file = process.argv[2];
if (!file) { console.error("uso: node smoke_dom_stub.js arquivo.html [--assert-count N]"); process.exit(2); }

const html = fs.readFileSync(file, "utf8");
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)]
  .map((m) => m[1])
  .filter((s) => s.trim().length > 0);

if (scripts.length === 0) {
  console.error("SMOKE_FAIL: nenhum script inline encontrado");
  process.exit(1);
}

// --- índice do DOM real (tags, classes, ids presentes no HTML) -------------
const tagRe = /<([a-zA-Z][a-zA-Z0-9-]*)(?=[\s>])/g;
const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map((m) => m[1]));
const classes = new Set();
for (const m of html.matchAll(/class="([^"]+)"/g)) for (const c of m[1].split(/\s+/)) classes.add(c);
const tags = new Set();
for (const m of html.matchAll(tagRe)) tags.add(m[1].toLowerCase());
const { innerHTML: _unused, ..._ } = {};

function parseFragment(frag) {
  const cls = new Set(), tgs = new Set();
  for (const m of frag.matchAll(/class="([^"]*)"/g)) for (const c of m[1].split(/\s+/)) if (c) cls.add(c);
  for (const m of frag.matchAll(/<([a-zA-Z][a-zA-Z0-9-]*)(?=[\s>])/g)) tgs.add(m[1].toLowerCase());
  return { cls, tgs };
}

function classifySel(sel) {
  sel = String(sel || "").trim();
  if (sel.startsWith(".")) return { kind: "class", value: sel.slice(1) };
  if (sel.startsWith("#")) return { kind: "id", value: sel.slice(1) };
  return { kind: "tag", value: sel.toLowerCase() };
}

function makeEl(tag) {
  const el = {
    tagName: String(tag).toUpperCase(),
    children: [],
    style: {},
    dataset: {},
    classList: { add() {}, remove() {}, toggle() {} },
    setAttribute() {}, removeAttribute() {},
    addEventListener() {},
    appendChild(c) { el.children.push(c); appendCalls += 1; return c; },
    querySelector(sel) {
      const { kind, value } = classifySel(sel);
      const known =
        kind === "class" ? el._classes.has(value) || classes.has(value)
        : kind === "id"   ? el._ids.has(value) || ids.has(value)
        :                   el._tags.has(value) || tags.has(value);
      return known ? makeEl("div") : null;
    },
    querySelectorAll(sel) {
      const { kind, value } = classifySel(sel);
      const known =
        kind === "class" ? el._classes.has(value) || classes.has(value)
        : kind === "id"   ? el._ids.has(value) || ids.has(value)
        :                   el._tags.has(value) || tags.has(value);
      return known ? [makeEl("div")] : [];
    },
    // superfície <audio>/<video>
    paused: true, muted: false, volume: 1, duration: 1, currentTime: 0,
    play() { return Promise.resolve(); }, pause() {}, load() {},
    // texto e fragmento
    get textContent() { return el._text; }, set textContent(v) { el._text = String(v); },
    get innerHTML() { return el._html; },
    set innerHTML(v) {
      el._html = String(v);
      const { cls, tgs } = parseFragment(el._html);
      el._classes = new Set([...el._classes, ...cls]);
      el._tags = new Set([...el._tags, ...tgs]);
    },
    focus() {}, click() {},
    closest() { return makeEl("div"); },
  };
  el._text = "";
  el._html = "";
  el._classes = new Set();
  el._tags = new Set();
  el._ids = new Set();
  return el;
}

let appendCalls = 0;
const doc = {
  body: makeEl("body"),
  createElement: (tag) => makeEl(tag),
  querySelector: (sel) => {
    const { kind, value } = classifySel(sel);
    const known =
      kind === "class" ? classes.has(value)
      : kind === "id"   ? ids.has(value)
      :                   tags.has(value);
    return known ? makeEl("div") : null;
  },
  querySelectorAll: (sel) => {
    const { kind, value } = classifySel(sel);
    const known =
      kind === "class" ? classes.has(value)
      : kind === "id"   ? ids.has(value)
      :                   tags.has(value);
    return known ? [makeEl("div")] : [];
  },
  getElementById: (id) => (ids.has(id) ? makeEl("div") : null),
  getElementsByTagName: (t) => (tags.has(String(t).toLowerCase()) ? [makeEl(t)] : []),
  addEventListener() {},
  documentElement: makeEl("html"),
};

const sandbox = {
  document: doc,
  window: { document: doc, addEventListener() {}, location: { href: file, replace() {}, assign() {}, reload() {} }, scrollTo() {}, matchMedia: () => ({ matches: false }) },
location: { href: file, replace() {}, assign() {}, reload() {} },
  console: { log() {}, error(...a) { console.error(...a); } },
  Math, Date, JSON, Object, Array, String, Number, Boolean, Promise, RegExp,
  setTimeout, clearTimeout, setInterval, clearInterval,
  fetch: () => Promise.resolve({ ok: false, status: 599, text: () => Promise.resolve("") }),
  alert() {}, confirm() {}, prompt() {},
};
sandbox.globalThis = sandbox;
sandbox.window.window = sandbox.window;
sandbox.window.mermaid = undefined;

let failed = false;
for (const [i, src] of scripts.entries()) {
  try {
    vm.runInNewContext(src, sandbox, { filename: `${file}#script${i + 1}`, timeout: 3000 });
  } catch (err) {
    failed = true;
    console.error(`SMOKE_FAIL: script #${i + 1} → ${err.message}`);
    if (process.env.SMOKE_DEBUG) console.error(err.stack);
  }
}

const assertCount = (() => {
  const i = process.argv.indexOf("--assert-count");
  return i >= 0 ? Number(process.argv[i + 1]) : null;
})();
if (assertCount !== null && appendCalls < assertCount) {
  failed = true;
  console.error(`SMOKE_FAIL: esperado >= ${assertCount} appendChild (grid vazio?) — viu ${appendCalls}`);
}

if (failed) { console.error("SMOKE_FAIL"); process.exit(1); }
console.log(`SMOKE_OK: ${scripts.length} scripts inline, ${appendCalls} appendChild, DOM stub sem runtime errors`);
process.exit(0);