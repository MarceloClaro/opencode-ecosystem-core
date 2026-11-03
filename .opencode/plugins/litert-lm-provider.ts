/**
 * LiteRT-LM Provider Plugin for OpenCode V2 (SPEC-935-R210 / SPEC-935-R1004)
 * =========================================================================
 * Registra o provider "litert-lm" (OpenAI-compatível, on-device) e dispara o
 * bootstrap do supervisor local.
 *
 * API V2: o host exige `export default { id, setup }` e registra providers por
 * `ctx.provider.transform`. O mapa `provider` da V1 nunca é executado pela V2.
 *
 * O registro é IDEMPOTENTE: se `opencode.json` já declarar `provider.litert-lm`
 * (com modelos), o transform apenas garante `activation: "enabled"` e não
 * duplica provider nem modelos.
 *
 * Modelos obtidos do servidor real via GET /v1/models (2026-07-22, porta 9379).
 * Modelos >2B podem levar >60s na primeira inferência (carregamento sob demanda).
 *
 * @packageDocumentation
 * @module litert-lm-provider
 */

import { Model, Plugin, Provider } from "@opencode/plugin";
import { spawn } from "node:child_process";
import { join } from "node:path";

const SUPERVISOR_RELATIVE_PATH = "integrations/litert_lm_supervisor.py";
const PROVIDER_ID = "litert-lm";
const BASE_URL = "http://localhost:9379/v1";
const MODEL_LIMIT = { context: 20480, output: 2048 };

/** Solicita o bootstrap canônico sem aguardar cold start ou readiness. */
function requestLiteRTBootstrap(workspace: string): void {
  const supervisorPath = join(workspace, SUPERVISOR_RELATIVE_PATH);
  try {
    const request = spawn(
      "python3",
      [supervisorPath, "ensure", "--non-blocking"],
      {
        cwd: workspace,
        detached: true,
        stdio: "ignore",
      },
    );
    request.once("error", () => undefined);
    request.unref();
  } catch {
    // O provider continua carregável; o MCP repetirá a solicitação como fallback.
  }
}

/**
 * Modelos disponíveis (validação empírica):
 *   gemma-4-E4B (4B expert), gemma-4-12B (12B),
 *   gemma-4-E2B (2B expert — responde), Qwen3-0.6B (0.6b).
 */
const MODEL_NAMES: ReadonlyArray<readonly [string, string]> = [
  ["litert-community/gemma-4-E4B-it-litert-lm", "Gemma 4 4B Expert (LiteRT-LM on-device)"],
  ["litert-community/gemma-4-12B-it-litert-lm", "Gemma 4 12B (LiteRT-LM on-device)"],
  ["litert-community/gemma-4-E2B-it-litert-lm", "Gemma 4 2B Expert (LiteRT-LM on-device)"],
  ["litert-community/Qwen3-0.6B", "Qwen3 0.6B (LiteRT-LM on-device)"],
];

function defineModel(id: string, name: string): Model.Info {
  return {
    ...Model.Info.default(PROVIDER_ID as Provider.ID, id as Model.ID),
    name,
    capabilities: { tools: false, input: ["text"], output: ["text"] },
    limit: { context: MODEL_LIMIT.context, output: MODEL_LIMIT.output },
    cost: [],
    status: "active",
    enabled: true,
  };
}

const MODELS: Model.Info[] = MODEL_NAMES.map(([id, name]) => defineModel(id, name));

export default Plugin.define({
  id: "litert-lm",
  async setup(ctx) {
    const workspace = ctx.location.project.canonical ?? ctx.location.directory;
    requestLiteRTBootstrap(workspace);

    await ctx.provider.transform((editor) => {
      const record = editor.get(PROVIDER_ID);

      if (!record) {
        editor.add({
          info: {
            ...Provider.Info.empty(PROVIDER_ID as Provider.ID),
            name: "LiteRT-LM (on-device)",
            activation: "enabled",
            package: "@opencode/ai/providers/openai-compatible",
            settings: { baseURL: BASE_URL, apiKey: "sk-no-key-required" },
          },
          models: MODELS,
        });
        return;
      }

      // Provider já declarado em opencode.json: não duplicar inventário.
      if (record.models.size === 0) {
        editor.models.set(PROVIDER_ID, MODELS);
      }
      editor.update(PROVIDER_ID, (provider) => {
        provider.activation = "enabled";
      });
    });
  },
});
