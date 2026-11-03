/**
 * Acesso Aberto Auditoria Plugin for OpenCode V2 (SPEC-979 / SPEC-935-R1004)
 * ==========================================================================
 * Superfície de orientação SPEC-979: valida uma entrada e indica a pasta
 * do fluxo SPEC-977/978. Não cria arquivos, consulta rede ou executa pipeline.
 *
 * API V2: o host exige `export default { id, setup }` e registra ferramentas
 * por `ctx.tool.transform`. O mapa `tool` da V1 não é executado pela V2.
 *
 * @packageDocumentation
 * @module acesso-aberto-auditoria
 */

import { Plugin } from "@opencode/plugin";

const BLOCKED = ["sci-hub", "scihub"];
const DOI_SHAPE = /^10\.\d{4,9}\/\S+$/;

function isBlockedSource(url: string): boolean {
  const s = url.toLowerCase();
  return BLOCKED.some((b) => s.includes(b)) || s.startsWith("scihub-mcp://");
}

function normalizeDoi(doi: string): string {
  return doi.trim().toLowerCase()
    .replace(/^https?:\/\/(dx\.)?doi\.org\//, "")
    .replace(/^doi:\s*/, "");
}

function isHttpUrl(value: string): boolean {
  try {
    const parsed = new URL(value);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

/**
 * JSON Schema não expressa `refine` (DOI normalizado, bloqueio de fonte).
 * O schema garante a forma; a semântica é aplicada em `execute` antes de
 * qualquer efeito, mantendo a recusa total de entrada inválida.
 */
const input = {
  type: "object",
  properties: {
    doi: {
      type: "string",
      maxLength: 2048,
      // Aceita as mesmas formas que `normalizeDoi` trata (DOI:, doi.org, dx.doi.org),
      // inclusive com espaços nas bordas; rejeita vazio e múltiplos DOIs.
      pattern:
        "^\\s*(?:[Hh][Tt][Tt][Pp][Ss]?://(?:[Dd][Xx]\\.)?[Dd][Oo][Ii]\\.[Oo][Rr][Gg]/|[Dd][Oo][Ii]:\\s*)?10\\.[0-9]{4,9}/\\S+\\s*$",
      description: "Um DOI a orientar; aceita DOI:, doi.org ou identificador simples.",
    },
    pdfUrl: {
      type: "string",
      maxLength: 4096,
      minLength: 1,
      pattern: "^[Hh][Tt][Tt][Pp][Ss]?://",
      description: "URL candidata; não confirma acesso aberto nem autoriza download.",
    },
  },
  required: ["doi"],
  additionalProperties: false,
} as const;

export default Plugin.define({
  id: "acesso-aberto-auditoria",
  async setup(ctx) {
    await ctx.tool.transform((editor) => {
      editor.add({
        name: "acesso-aberto-auditoria",
        description:
          "Orienta a auditoria por DOI: valida a entrada, bloqueia fontes Sci-Hub e sugere a pasta SPEC-977/978. Sem rede, criação de arquivos ou execução de pipeline. Revisão humana obrigatória.",
        input,
        async execute(raw) {
          // O host valida `input` antes de chamar execute; esta checagem
          // preserva a recusa de entrada inválida quando a tool é invocada
          // diretamente (harness, testes, reuso interno).
          if (raw === null || typeof raw !== "object" || Array.isArray(raw)) {
            throw new Error("entrada inválida: objeto esperado");
          }
          const args = raw as { doi?: unknown; pdfUrl?: unknown };
          for (const key of Object.keys(args)) {
            if (key !== "doi" && key !== "pdfUrl") {
              throw new Error(`entrada inválida: campo não suportado (${key})`);
            }
          }
          if (typeof args.doi !== "string") {
            throw new Error("entrada inválida: doi deve ser string");
          }
          if (args.pdfUrl !== undefined && typeof args.pdfUrl !== "string") {
            throw new Error("entrada inválida: pdfUrl deve ser string");
          }
          const doi = normalizeDoi(args.doi);
          if (!DOI_SHAPE.test(doi)) {
            throw new Error("DOI inválido antes de rede");
          }
          if (args.pdfUrl !== undefined) {
            if (isBlockedSource(args.pdfUrl)) {
              throw new Error("blocked: unauthorized_source");
            }
            if (!isHttpUrl(args.pdfUrl)) {
              throw new Error("URL candidata deve usar HTTP ou HTTPS");
            }
          }
          const pdfUrl = args.pdfUrl;
          const slug = doi.replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 120);
          return {
            content: JSON.stringify({
              doi,
              pdfUrl: pdfUrl ?? null,
              pasta: `auditoria_fichamentos/${slug}`,
              guidance_only: true,
              file_creation: false,
              pipeline_executed: false,
              network_performed: false,
              evidence_eligible: false,
              proximo:
                "Solicite ao orquestrador marceloclaro o fluxo criar_pasta_auditoria + adicionar_recorte + auditar_pasta em research/auditoria_fichamento.py; esta ferramenta apenas orienta.",
              revisaoHumanaObrigatoria: true,
            }),
          };
        },
      });
    });
  },
});
