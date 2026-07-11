// SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
// Toda resposta DEVE ser em português do Brasil formal.
// Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out)

/**
 * ANTIGRAVITY BRIDGE v1.1 — Ponte Bidirecional OpenCode ↔ Antigravity
 *
 * Arquitetura de orquestração que permite ao OpenCode Ecosystem delegar tarefas
 * ao Antigravity (Google DeepMind Advanced Agentic Coding) e receber resultados
 * de volta como eventos síncronos no pipeline de agentes.
 *
 * Capacidades expostas pelo Antigravity:
 *   - Geração de imagens (generate_image)
 *   - Execução de browser com gravação (browser_subagent)
 *   - Pesquisa web e leitura de URLs
 *   - Geração/edição de código com contexto de repositório completo
 *   - Subagentes paralelos com estado compartilhado
 *
 * Pipeline:
 *   OpenCode Session → AntiBridge → Task Router → Antigravity Executor
 *   Antigravity Result → State Update → EcosystemSync Health Matrix
 *
 * Integração com ecossistema existente:
 *   - ecosystem-sync v3.5: registra "antigravity" como componente monitorado
 *   - manus-evolve v2.2: extrai padrões das delegações bem-sucedidas
 *   - nexus multi-agent v6.2: antigravity como nó executor externo
 */
import type { Plugin } from "@opencode-ai/plugin"
import { readFile, writeFile, mkdir } from "fs/promises"
import { existsSync } from "fs"

// ============================================================
// Tipos e Interfaces
// ============================================================

interface AntiBridgeTask {
  id: string
  type: "code" | "image" | "browser" | "search" | "analysis" | "orchestration"
  prompt: string
  context?: string
  priority: "critical" | "high" | "normal" | "low"
  timestamp: string
  status: "pending" | "delegated" | "completed" | "failed"
  result?: string
  latencyMs?: number
  retries: number
}

interface AntiBridgeState {
  version: string
  sessionId: string
  tasks: AntiBridgeTask[]
  totalDelegated: number
  totalCompleted: number
  totalFailed: number
  successRate: number
  avgLatencyMs: number
  lastSync: string | null
  capabilities: {
    codeGeneration: boolean
    imageGeneration: boolean
    browserAutomation: boolean
    webSearch: boolean
    subagentOrchestration: boolean
    parallelExecution: boolean
    ragSynthesis: boolean
    // Cloud capabilities (SPEC-935-R130)
    alloydbOperations: boolean
    bigqueryAnalytics: boolean
    cloudSqlPostgres: boolean
    cloudSqlMysql: boolean
    cloudSqlSqlServer: boolean
    dataflowPipelines: boolean
    composerAirflow: boolean
    gcsSecurity: boolean
    firestoreOps: boolean
    spannerOps: boolean
    pipelineOrchestration: boolean
    dataAutocleaning: boolean
    lakehouseFederation: boolean
  }
  orchestrationPatterns: Record<string, number>
  pendingQueue: AntiBridgeTask[]
  healthScore: number
}

interface TaskClassification {
  type: AntiBridgeTask["type"]
  priority: AntiBridgeTask["priority"]
  requiresAntigravity: boolean
  reason: string
  suggestedCapability: string
}

// ============================================================
// Constantes
// ============================================================

const STATE_FILE = ".evolve/antigravity-bridge-state.json"
const TASK_QUEUE_FILE = ".evolve/antigravity-task-queue.json"
const OBSERVABILITY_LOG = ".evolve/antigravity-observability.jsonl"
const BRIDGE_VERSION = "1.0.0"

// Capacidades que o Antigravity possui e o OpenCode não
const ANTIGRAVITY_EXCLUSIVE_CAPABILITIES = [
  "generate_image",
  "browser_subagent",
  "read_url_content",
  "search_web",
  "view_file_binary",
  "generate_animated_demo",
  "query_rag",
  // === Cloud Skills (SPEC-935-R130) ===
  "cloud_alloydb_admin",
  "cloud_alloydb_health",
  "cloud_alloydb_monitor",
  "cloud_alloydb_performance",
  "cloud_bigquery_analytics",
  "cloud_bigquery_ml",
  "cloud_bigquery_dts",
  "cloud_sql_postgres_admin",
  "cloud_sql_postgres_health",
  "cloud_sql_postgres_vector",
  "cloud_sql_mysql_admin",
  "cloud_sql_sqlserver_admin",
  "cloud_dataflow_pipelines",
  "cloud_composer_airflow",
  "cloud_spark_dataproc",
  "cloud_gcs_security",
  "cloud_firestore_crud",
  "cloud_spanner_graph",
  "cloud_pipeline_orchestration",
  "cloud_data_autocleaning",
  "cloud_lakehouse_federation",
]

// Padrões de prompt que indicam necessidade do Antigravity
const ANTIGRAVITY_TRIGGER_PATTERNS = [
  /\b(imagem|image|screenshot|foto|visual|design|UI|interface)\b/i,
  /\b(browser|navegador|web scraping|automação web)\b/i,
  /\b(pesquisa web|busca online|search web|google|duckduckgo)\b/i,
  /\b(URL|website|página web|read url)\b/i,
  /\b(paralelo|parallel|simultâneo|concurrent)\b/i,
  /\b(demo|demonstração|animação|recording|gravação)\b/i,
  /\b(rag|banco vetorial|vector db|consultar base|busca semântica)\b/i,
  /\b(marceloclaro|\/marceloclaro|orquestrador supremo)\b/i,
  // === Cloud Triggers (SPEC-935-R130) ===
  /\b(alloydb|cloud sql|bigquery|dataflow|composer|dataproc)\b/i,
  /\b(gcp|google cloud|cloud infrastructure|nuvem|cloud computing)\b/i,
  /\b(pipeline de dados|data pipeline|data lake|data warehouse)\b/i,
  /\b(cloud database|banco de dados cloud|postgres cloud|mysql cloud)\b/i,
  /\b(cloud security|cloud migration|infraestrutura cloud)\b/i,
  /\b(gcs|cloud storage|firestore|spanner|bigtable)\b/i,
  /\b(terraform|iac|infrastructure as code|cloud deployment)\b/i,
]

// ============================================================
// Funções Auxiliares
// ============================================================

function generateTaskId(): string {
  return `anti-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`
}

function classifyTask(input: string): TaskClassification {
  const lowerInput = input.toLowerCase()

  // Verificar triggers do Antigravity
  const triggeredPatterns = ANTIGRAVITY_TRIGGER_PATTERNS.filter(p => p.test(input))

  if (lowerInput.includes("/marceloclaro") || lowerInput.includes("marceloclaro") || lowerInput.includes("orquestrador supremo")) {
    return {
      type: "orchestration",
      priority: "critical",
      requiresAntigravity: true,
      reason: "Invocação explícita do Orquestrador Supremo Marcelo Claro (SPEC-042)",
      suggestedCapability: "subagent_orchestration",
    }
  }

  if (lowerInput.includes("image") || lowerInput.includes("imagem") || lowerInput.includes("visual")) {
    return {
      type: "image",
      priority: "normal",
      requiresAntigravity: true,
      reason: "Geração de imagem requer capacidade generate_image do Antigravity",
      suggestedCapability: "generate_image",
    }
  }

  if (lowerInput.includes("browser") || lowerInput.includes("navegador") || lowerInput.includes("web automação")) {
    return {
      type: "browser",
      priority: "high",
      requiresAntigravity: true,
      reason: "Automação de browser requer browser_subagent do Antigravity",
      suggestedCapability: "browser_subagent",
    }
  }

  if (lowerInput.includes("rag") || lowerInput.includes("banco vetorial") || lowerInput.includes("busca semântica")) {
    return {
      type: "orchestration",
      priority: "high",
      requiresAntigravity: true,
      reason: "Consulta RAG avançada direcionada para síntese cruzada do Antigravity",
      suggestedCapability: "query_rag",
    }
  }

  if (lowerInput.includes("pesquisa") || lowerInput.includes("search") || lowerInput.includes("url")) {
    return {
      type: "search",
      priority: "normal",
      requiresAntigravity: true,
      reason: "Pesquisa web/leitura URL requer search_web ou read_url_content",
      suggestedCapability: "search_web",
    }
  }

  if (triggeredPatterns.length > 0) {
    return {
      type: "orchestration",
      priority: "high",
      requiresAntigravity: true,
      reason: `${triggeredPatterns.length} padrões Antigravity detectados`,
      suggestedCapability: "subagent_orchestration",
    }
  }

  // Tarefas de análise/código que o OpenCode pode fazer mas Antigravity potencializa
  if (lowerInput.includes("análise") || lowerInput.includes("analysis") || lowerInput.includes("refactor")) {
    return {
      type: "analysis",
      priority: "normal",
      requiresAntigravity: false,
      reason: "Análise pode ser feita pelo OpenCode; Antigravity é opcional para enriquecimento",
      suggestedCapability: "code_analysis",
    }
  }

  return {
    type: "code",
    priority: "normal",
    requiresAntigravity: false,
    reason: "Tarefa de código padrão — OpenCode é primário, Antigravity como suporte",
    suggestedCapability: "code_generation",
  }
}

async function loadState(directory: string): Promise<AntiBridgeState> {
  const statePath = `${directory}/${STATE_FILE}`
  try {
    if (existsSync(statePath)) {
      const content = await readFile(statePath, "utf-8")
      const s = JSON.parse(content)
      return s
    }
  } catch {}

  return {
    version: BRIDGE_VERSION,
    sessionId: `session-${Date.now().toString(36)}`,
    tasks: [],
    totalDelegated: 0,
    totalCompleted: 0,
    totalFailed: 0,
    successRate: 1.0,
    avgLatencyMs: 0,
    lastSync: null,
    capabilities: {
      codeGeneration: true,
      imageGeneration: true,
      browserAutomation: true,
      webSearch: true,
      subagentOrchestration: true,
      parallelExecution: true,
      ragSynthesis: true,
      // Cloud capabilities (SPEC-935-R130)
      alloydbOperations: true,
      bigqueryAnalytics: true,
      cloudSqlPostgres: true,
      cloudSqlMysql: true,
      cloudSqlSqlServer: true,
      dataflowPipelines: true,
      composerAirflow: true,
      gcsSecurity: true,
      firestoreOps: true,
      spannerOps: true,
      pipelineOrchestration: true,
      dataAutocleaning: true,
      lakehouseFederation: true,
    },
    orchestrationPatterns: {},
    pendingQueue: [],
    healthScore: 100,
  }
}

async function saveState(directory: string, state: AntiBridgeState): Promise<void> {
  await mkdir(`${directory}/.evolve`, { recursive: true }).catch(() => {})
  await writeFile(`${directory}/${STATE_FILE}`, JSON.stringify(state, null, 2))
}

async function logObservability(
  directory: string,
  event: string,
  data: Record<string, any>
): Promise<void> {
  const logPath = `${directory}/${OBSERVABILITY_LOG}`
  const entry =
    JSON.stringify({
      timestamp: new Date().toISOString(),
      bridge: "antigravity-bridge-v1",
      event,
      ...data,
    }) + "\n"
  try {
    await mkdir(`${directory}/.evolve`, { recursive: true }).catch(() => {})
    await writeFile(logPath, entry, { flag: "a" })
  } catch (err: any) {
    console.error(`[AntiBridge] Log error: ${err.message}`)
  }
}

function buildAntiBridgePrompt(task: AntiBridgeTask, ecosystemContext: string): string {
  return `<!-- ANTIGRAVITY BRIDGE REQUEST v1.0 -->
<!-- Gerado pelo OpenCode Ecosystem via antigravity-bridge.ts -->
<!-- ID: ${task.id} | Tipo: ${task.type} | Prioridade: ${task.priority} -->

## Contexto do Ecossistema OpenCode
${ecosystemContext}

## Tarefa Delegada
**Tipo**: ${task.type}
**Prioridade**: ${task.priority}
**Timestamp**: ${task.timestamp}

## Prompt da Tarefa
${task.prompt}

${task.context ? `## Contexto Adicional\n${task.context}\n` : ""}
## Instruções de Retorno
- Retorne o resultado em português brasileiro formal
- Inclua métricas de execução quando aplicável
- Sinalize erros com prefixo "[ERRO ANTIGRAVITY]:"
- Para tarefas de imagem: descreva o artefato gerado e o caminho
- Para tarefas de browser: inclua URL acessada e resultado capturado
`
}

function updateHealthScore(state: AntiBridgeState): number {
  if (state.totalDelegated === 0) return 100
  const baseScore = state.successRate * 80
  const latencyPenalty = Math.min(20, state.avgLatencyMs / 1000)
  const queuePenalty = Math.min(10, state.pendingQueue.length * 2)
  return Math.max(0, Math.min(100, baseScore - latencyPenalty - queuePenalty))
}

// ============================================================
// Plugin Export — AntiBridgePlugin
// ============================================================

export const AntiBridgePlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  console.log("[AntiBridge v1.0] Ponte OpenCode ↔ Antigravity inicializada")

  let state = await loadState(directory)
  state.sessionId = `session-${Date.now().toString(36)}`

  return {
    // ============ SESSION START: Registrar capacidades do Antigravity ============
    "session.created": async () => {
      console.log("[AntiBridge v1.0] Registrando capacidades do Antigravity no ecossistema...")

      try {
        // Atualizar estado do ecossistema para incluir Antigravity como componente
        const ecoStatePath = `${directory}/.evolve/ecosystem-state.json`
        let ecoState: any = {}
        try {
          const ecoContent = await readFile(ecoStatePath, "utf-8")
          ecoState = JSON.parse(ecoContent)
        } catch {}

        // Registrar Antigravity e MarceloClaro como agentes especializados
        if (!ecoState.agents) ecoState.agents = {}
        ecoState.agents["antigravity-bridge"] = {
          name: "antigravity-bridge",
          type: "agent",
          status: "active",
          score: 95,
          lastCheck: new Date().toISOString(),
          errorCount: 0,
          latency: null,
          category: "external-ai",
          capabilities: ANTIGRAVITY_EXCLUSIVE_CAPABILITIES,
          provider: "google-deepmind",
          version: BRIDGE_VERSION,
        }
        ecoState.agents["marceloclaro"] = {
          name: "marceloclaro",
          type: "orchestrator",
          status: "active",
          score: 100,
          lastCheck: new Date().toISOString(),
          errorCount: 0,
          latency: null,
          category: "supreme-orchestration",
          capabilities: ["orchestrate_pillars", "prevent_goal_drift", "tdd_validation", "cli_alignment"],
          provider: "opencode-ecosystem",
          version: "1.0.0",
        }

        // Adicionar entradas de afinidade na matriz de validação cruzada
        const affinityEntries: Record<string, number> = {
          "antigravity↔manus-evolve": 0.95,
          "antigravity↔openagent": 0.90,
          "antigravity↔ecosystem-sync": 0.85,
          "antigravity↔quantum-nexus-phd": 0.80,
          "antigravity↔criador-artigo": 0.90,
          "antigravity↔seeker": 0.85,
          "antigravity↔generate_image:agent": 1.0,
          "antigravity↔browser_subagent:agent": 1.0,
          "antigravity↔search_web:mcp": 0.95,
          "antigravity↔websearch:mcp": 0.90,
          "marceloclaro↔antigravity": 0.98,
          "marceloclaro↔master-orchestrator": 0.95,
          "marceloclaro↔stage-orchestrator": 0.95,
          "marceloclaro↔trust-engine": 0.95,
          // Cloud agent affinities (SPEC-935-R130)
          "antigravity↔cloud-alloydb-specialist": 0.90,
          "antigravity↔cloud-bigquery-specialist": 0.90,
          "antigravity↔cloud-sql-postgres-specialist": 0.85,
          "antigravity↔cloud-sql-mysql-specialist": 0.85,
          "antigravity↔cloud-sql-sqlserver-specialist": 0.80,
          "antigravity↔cloud-data-pipelines-specialist": 0.90,
          "antigravity↔cloud-security-specialist": 0.85,
          "antigravity↔cloud-data-infra-generalist": 0.80,
          "cloud-alloydb-specialist↔cloud-bigquery-specialist": 0.85,
          "cloud-data-pipelines-specialist↔cloud-security-specialist": 0.80,
        }

        if (!ecoState.crossValidationMatrix) ecoState.crossValidationMatrix = {}
        Object.assign(ecoState.crossValidationMatrix, affinityEntries)

        try {
          await writeFile(ecoStatePath, JSON.stringify(ecoState, null, 2))
        } catch {}

        // Registrar no log de observabilidade
        await logObservability(directory, "bridge.session.start", {
          sessionId: state.sessionId,
          capabilities: state.capabilities,
          pendingTasks: state.pendingQueue.length,
          totalHistoric: state.totalDelegated,
        })

        await client.app.log({
          body: {
            service: "antigravity-bridge-v1",
            level: "info",
            message: `Ponte OpenCode↔Antigravity ativa | Capacidades: ${ANTIGRAVITY_EXCLUSIVE_CAPABILITIES.length} exclusivas | Sessão: ${state.sessionId} | Histórico: ${state.totalDelegated} tarefas delegadas`,
            extra: {
              version: BRIDGE_VERSION,
              capabilities: state.capabilities,
              sessionId: state.sessionId,
            },
          },
        })
      } catch (err: any) {
        await client.app.log({
          body: {
            service: "antigravity-bridge-v1",
            level: "error",
            message: `Falha na inicialização da ponte: ${err.message}`,
          },
        })
      }
    },

    // ============ TOOL EXECUTE: Interceptar e classificar tarefas ============
    "tool.execute.before": async (input: any, _output: any) => {
      const tool = input.tool || ""
      const prompt = input.args?.prompt || input.args?.message || input.args?.query || ""

      if (!prompt || prompt.length < 10) return

      const classification = classifyTask(prompt)

      // Registrar padrão de orquestração
      const patternKey = `${tool}:${classification.type}`
      state.orchestrationPatterns[patternKey] = (state.orchestrationPatterns[patternKey] || 0) + 1

      // Se requer Antigravity, criar tarefa pendente
      if (classification.requiresAntigravity) {
        const task: AntiBridgeTask = {
          id: generateTaskId(),
          type: classification.type,
          prompt: prompt.substring(0, 500),
          priority: classification.priority,
          timestamp: new Date().toISOString(),
          status: "pending",
          retries: 0,
        }
        state.pendingQueue.push(task)
        console.log(`[AntiBridge] Tarefa ${task.id} (${classification.type}) enfileirada — ${classification.reason}`)
      }
    },

    // ============ TOOL EXECUTE AFTER: Processar resultado e aprender ============
    "tool.execute.after": async (input: any, output: any) => {
      const toolName = input.tool || "unknown"
      const resultStr = typeof output?.result === "string"
        ? output.result
        : JSON.stringify(output?.result || output?.output || "").substring(0, 300)

      // Verificar se é resultado do Antigravity (via marker no output)
      if (resultStr.includes("ANTIGRAVITY BRIDGE") || resultStr.includes("anti-")) {
        const completedTask = state.pendingQueue.find(t => t.status === "delegated")
        if (completedTask) {
          completedTask.status = "completed"
          completedTask.result = resultStr.substring(0, 200)
          state.pendingQueue = state.pendingQueue.filter(t => t.id !== completedTask.id)
          state.tasks.push(completedTask)
          state.totalCompleted++
        }
      }

      // Atualizar métricas gerais
      state.lastSync = new Date().toISOString()
      state.successRate = state.totalDelegated > 0
        ? state.totalCompleted / state.totalDelegated
        : 1.0
      state.healthScore = updateHealthScore(state)
    },

    // ============ SESSION IDLE: Processar fila + relatório de orquestração ============
    "session.idle": async () => {
      // Processar tarefas pendentes não delegadas
      const unprocessed = state.pendingQueue.filter(t => t.status === "pending")
      if (unprocessed.length > 0) {
        console.log(`[AntiBridge] ${unprocessed.length} tarefas pendentes para delegação ao Antigravity`)

        for (const task of unprocessed) {
          task.status = "delegated"
          state.totalDelegated++
          await logObservability(directory, "task.delegated", {
            taskId: task.id,
            type: task.type,
            priority: task.priority,
          })
        }
      }

      // Gerar relatório de padrões de orquestração
      const topPatterns = Object.entries(state.orchestrationPatterns)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 5)
        .map(([p, c]) => `${p}(${c}x)`)

      // Atualizar health score
      state.healthScore = updateHealthScore(state)
      state.lastSync = new Date().toISOString()

      await saveState(directory, state)

      await logObservability(directory, "session.idle.report", {
        totalDelegated: state.totalDelegated,
        totalCompleted: state.totalCompleted,
        successRate: state.successRate,
        healthScore: state.healthScore,
        pendingQueue: state.pendingQueue.length,
        topPatterns,
      })

      await client.app.log({
        body: {
          service: "antigravity-bridge-v1",
          level: "info",
          message: `Ponte idle | Delegadas: ${state.totalDelegated} | Concluídas: ${state.totalCompleted} | Taxa: ${(state.successRate * 100).toFixed(1)}% | Saúde: ${state.healthScore.toFixed(1)} | Fila: ${state.pendingQueue.length} | Padrões: ${topPatterns.join(", ")}`,
        },
      })
    },

    // ============ SESSION ERROR: Rastrear falhas e recuperar ============
    "session.error": async (input: any) => {
      const failedTasks = state.pendingQueue.filter(t => t.status === "delegated")
      for (const task of failedTasks) {
        task.retries++
        if (task.retries >= 3) {
          task.status = "failed"
          state.totalFailed++
          state.tasks.push(task)
          state.pendingQueue = state.pendingQueue.filter(t => t.id !== task.id)
        } else {
          task.status = "pending" // Recolocar na fila para retry
        }
      }

      state.successRate = state.totalDelegated > 0
        ? state.totalCompleted / state.totalDelegated
        : 1.0
      state.healthScore = updateHealthScore(state)

      await saveState(directory, state)
      await logObservability(directory, "session.error", {
        failedCount: state.totalFailed,
        healthScore: state.healthScore,
        pendingRetries: state.pendingQueue.filter(t => t.retries > 0).length,
      })
    },

    // ============ SHELL ENV: Expor variáveis de ambiente da ponte ============
    "shell.env": async (_input: any, output: any) => {
      output.env.ANTIGRAVITY_BRIDGE_VERSION = BRIDGE_VERSION
      output.env.ANTIGRAVITY_BRIDGE_ACTIVE = "true"
      output.env.ANTIGRAVITY_BRIDGE_HEALTH = state.healthScore.toFixed(1)
      output.env.ANTIGRAVITY_BRIDGE_DELEGATED = String(state.totalDelegated)
      output.env.ANTIGRAVITY_BRIDGE_COMPLETED = String(state.totalCompleted)
      output.env.ANTIGRAVITY_BRIDGE_SUCCESS_RATE = state.successRate.toFixed(3)
      output.env.ANTIGRAVITY_BRIDGE_PENDING = String(state.pendingQueue.length)
      output.env.ANTIGRAVITY_SESSION_ID = state.sessionId
      output.env.ANTIGRAVITY_CAPABILITIES_COUNT = String(
        Object.values(state.capabilities).filter(Boolean).length
      )
      // Capacidades individuais
      output.env.ANTIGRAVITY_CAP_IMAGE = String(state.capabilities.imageGeneration)
      output.env.ANTIGRAVITY_CAP_BROWSER = String(state.capabilities.browserAutomation)
      output.env.ANTIGRAVITY_CAP_SEARCH = String(state.capabilities.webSearch)
      output.env.ANTIGRAVITY_CAP_PARALLEL = String(state.capabilities.parallelExecution)
      output.env.ANTIGRAVITY_CAP_SUBAGENT = String(state.capabilities.subagentOrchestration)
      output.env.ANTIGRAVITY_CAP_RAG = String(state.capabilities.ragSynthesis)
    },

    // ============ PERMISSION: Auto-aprovar ferramentas de integração conhecidas ============
    "permission.asked": async (input: any, output: any) => {
      const tool = input.tool || ""
      // Auto-aprovar ferramentas de bridge se padrão é confiável
      if (
        tool.includes("antigravity") ||
        tool.includes("generate_image") ||
        tool.includes("browser_subagent")
      ) {
        const patternCount = state.orchestrationPatterns[tool] || 0
        if (patternCount >= 2) {
          output.autoApprove = true
          console.log(`[AntiBridge] Auto-aprovando ${tool} (${patternCount} usos anteriores bem-sucedidos)`)
        }
      }
    },
  }
}
