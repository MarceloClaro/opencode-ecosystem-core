/**
 * Acesso Aberto Auditoria Plugin for OpenCode
 * ===========================================
 * Superfície de orientação SPEC-979: valida uma entrada e indica a pasta
 * do fluxo SPEC-977/978. Não cria arquivos, consulta rede ou executa pipeline.
 *
 * @packageDocumentation
 * @module acesso-aberto-auditoria
 */

import { tool, type Plugin } from "@opencode-ai/plugin";

const BLOCKED = ["sci-hub", "scihub"];

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

const argumentShape = {
  doi: tool.schema.string().max(2048)
    .refine((value) => /^10\.\d{4,9}\/\S+$/.test(normalizeDoi(value)), "DOI inválido antes de rede")
    .describe("Um DOI a orientar; aceita DOI:, doi.org ou identificador simples."),
  pdfUrl: tool.schema.string().max(4096).trim().min(1)
    .refine((value) => !isBlockedSource(value), "blocked: unauthorized_source")
    .refine(isHttpUrl, "URL candidata deve usar HTTP ou HTTPS")
    .optional().describe("URL candidata; não confirma acesso aberto nem autoriza download."),
};
const inputSchema = tool.schema.object(argumentShape).strict();

export const AcessoAbertoAuditoriaPlugin: Plugin = async () => {
  return {
    tool: {
      "acesso-aberto-auditoria": tool({
        description:
          "Orienta a auditoria por DOI: valida a entrada, bloqueia fontes Sci-Hub e sugere a pasta SPEC-977/978. Sem rede, criação de arquivos ou execução de pipeline. Revisão humana obrigatória.",
        args: argumentShape,
        async execute(args) {
          // tool() fornece o contrato ao host, mas não valida execute direta.
          // A operação inteira também é admitida por schema nessa fronteira.
          const admitted = inputSchema.parse(args);
          const doi = normalizeDoi(admitted.doi);
          const { pdfUrl } = admitted;
          const slug = doi.replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 120);
          return JSON.stringify({
            doi,
            pdfUrl: pdfUrl ?? null,
            pasta: `auditoria_fichamentos/${slug}`,
            guidance_only: true,
            file_creation: false,
            pipeline_executed: false,
            network_performed: false,
            evidence_eligible: false,
            proximo: "Solicite ao orquestrador marceloclaro o fluxo criar_pasta_auditoria + adicionar_recorte + auditar_pasta em research/auditoria_fichamento.py; esta ferramenta apenas orienta.",
            revisaoHumanaObrigatoria: true,
          });
        },
      }),
    },
  };
};

export default AcessoAbertoAuditoriaPlugin;
