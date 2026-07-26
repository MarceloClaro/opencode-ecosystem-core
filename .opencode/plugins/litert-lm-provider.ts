/**
 * LiteRT-LM Provider Plugin for OpenCode
 * ========================================
 * Registers "litert-lm" as a native LLM provider via the plugin hook `provider`.
 *
 * Makes `opencode run --model "litert-lm/litert-community/gemma-4-E2B-it-litert-lm" ...`
 * work by telling OpenCode that "litert-lm" is a valid provider prefix and declaring
 * which models are available under it.
 *
 * @packageDocumentation
 * @module litert-lm-provider
 */

import type { Plugin } from "@opencode-ai/plugin";
import { spawn } from "node:child_process";
import { join } from "node:path";

const SUPERVISOR_RELATIVE_PATH = "integrations/litert_lm_supervisor.py";

/** Solicita o bootstrap canônico sem aguardar cold start ou readiness. */
function requestLiteRTBootstrap(worktree: string, directory: string): void {
  const workspace = worktree || directory;
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
 * LiteRT-LM Provider Plugin
 *
 * Hooks into OpenCode's provider system to register the "litert-lm" provider
 * with its supported on-device GGUF models (Gemma 4, Gemma 3, Llama 4, Phi-4, Qwen 2.5).
 *
 * The connection details (baseURL, apiKey) come from opencode.json:
 * ```json
 * {
 *   "provider": {
 *     "litert-lm": {
 *       "options": {
 *         "apiKey": "sk-no-key-required",
 *         "baseURL": "http://localhost:9379/v1"
 *       }
 *     }
 *   }
 * }
 * ```
 *
 * The provider is OpenAI-compatible, so OpenCode routes requests to
 * `{baseURL}/chat/completions` using the `@ai-sdk/openai-compatible` adapter.
 */
export const LiteRTProvider: Plugin = async ({ directory, worktree }) => {
  requestLiteRTBootstrap(worktree, directory);
  return {
    provider: {
      id: "litert-lm",

      /**
       * Declares all models available under the litert-lm provider.
       *
       * The `provider` parameter contains the merged provider configuration
       * from opencode.json (including options.baseURL and options.apiKey).
       *
       * @param provider - Provider configuration from opencode.json
       * @param ctx - Context with optional auth info
       * @returns Record of model ID → Model definition
       */
      /**
       * Model definitions obtidas do servidor real via GET /v1/models.
       * Atualizado em 2026-07-22 conforme servidor rodando em :9379.
       *
       * Modelos disponíveis (validação empírica):
       *   ✅ litert-community/gemma-4-E4B-it-litert-lm  (4B expert)
       *   ✅ litert-community/gemma-4-12B-it-litert-lm  (12B)
       *   ✅ litert-community/gemma-4-E2B-it-litert-lm  (2B expert — testado: responde "FUNCIONOU")
       *   ✅ litert-community/Qwen3-0.6B                (0.6B)
       *
       * Nota: modelos >2B podem levar >60s para primeira inferência
       * (carregamento sob demanda do LiteRT Runtime).
       */
      models: async (_provider, _ctx) => ({
        "litert-community/gemma-4-E4B-it-litert-lm": {
          id: "litert-community/gemma-4-E4B-it-litert-lm",
          providerID: "litert-lm",
          api: { id: "litert-lm", url: "", npm: "@ai-sdk/openai-compatible" },
          name: "Gemma 4 4B Expert (LiteRT-LM on-device)",
          capabilities: {
            temperature: true, reasoning: false, attachment: false, toolcall: false,
            input: { text: true, audio: false, image: false, video: false, pdf: false },
            output: { text: true, audio: false, image: false, video: false, pdf: false },
            interleaved: false,
          },
          cost: { input: 0, output: 0, cache: { read: 0, write: 0 } },
          limit: { context: 20480, output: 2048 },
          status: "active", options: {}, headers: {}, release_date: "",
        },

        "litert-community/gemma-4-12B-it-litert-lm": {
          id: "litert-community/gemma-4-12B-it-litert-lm",
          providerID: "litert-lm",
          api: { id: "litert-lm", url: "", npm: "@ai-sdk/openai-compatible" },
          name: "Gemma 4 12B (LiteRT-LM on-device)",
          capabilities: {
            temperature: true, reasoning: false, attachment: false, toolcall: false,
            input: { text: true, audio: false, image: false, video: false, pdf: false },
            output: { text: true, audio: false, image: false, video: false, pdf: false },
            interleaved: false,
          },
          cost: { input: 0, output: 0, cache: { read: 0, write: 0 } },
          limit: { context: 20480, output: 2048 },
          status: "active", options: {}, headers: {}, release_date: "",
        },

        "litert-community/gemma-4-E2B-it-litert-lm": {
          id: "litert-community/gemma-4-E2B-it-litert-lm",
          providerID: "litert-lm",
          api: { id: "litert-lm", url: "", npm: "@ai-sdk/openai-compatible" },
          name: "Gemma 4 2B Expert (LiteRT-LM on-device)",
          capabilities: {
            temperature: true, reasoning: false, attachment: false, toolcall: false,
            input: { text: true, audio: false, image: false, video: false, pdf: false },
            output: { text: true, audio: false, image: false, video: false, pdf: false },
            interleaved: false,
          },
          cost: { input: 0, output: 0, cache: { read: 0, write: 0 } },
          limit: { context: 20480, output: 2048 },
          status: "active", options: {}, headers: {}, release_date: "",
        },

        "litert-community/Qwen3-0.6B": {
          id: "litert-community/Qwen3-0.6B",
          providerID: "litert-lm",
          api: { id: "litert-lm", url: "", npm: "@ai-sdk/openai-compatible" },
          name: "Qwen3 0.6B (LiteRT-LM on-device)",
          capabilities: {
            temperature: true, reasoning: false, attachment: false, toolcall: false,
            input: { text: true, audio: false, image: false, video: false, pdf: false },
            output: { text: true, audio: false, image: false, video: false, pdf: false },
            interleaved: false,
          },
          cost: { input: 0, output: 0, cache: { read: 0, write: 0 } },
          limit: { context: 20480, output: 2048 },
          status: "active", options: {}, headers: {}, release_date: "",
        },
      }),
    },
  };
};

// Default export also supported (OpenCode auto-discovers both)
export default LiteRTProvider;
