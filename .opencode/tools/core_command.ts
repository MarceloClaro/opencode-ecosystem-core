import { tool } from "@opencode-ai/plugin";
import { spawn } from "node:child_process";

// R816: texto só atravessa stdin JSON. O parser textual do OpenCode é upstream.
const commands = ["diagnose", "maswos", "reason", "economy", "models", "route", "sdd", "tdd", "pypi", "efficiency", "goose", "gemini", "plandex", "reasonix", "colab", "colab-mcp", "minizinc", "claude-sdk", "opencode-sdk", "kaggle", "agy"] as const;
const deadlineMs = 180_000;
const maxOutputBytes = 8 * 1024 * 1024;

export default tool({
  description: "Operações autorizadas do Core pelo primário marceloclaro. Argumentos são dados JSON; CLIs recebem argv explícito. Resultados locais não atestam inferência externa.",
  args: {
    command: tool.schema.enum(commands),
    arguments: tool.schema.string().optional().describe("Texto literal, consulta, tópico ou caminho; nunca código shell."),
    argv: tool.schema.array(tool.schema.string()).optional().describe("Para CLIs: argumentos e opções como lista explícita, sem shell."),
  },
  async execute(args, context) {
    if (context.agent !== "marceloclaro") {
      return JSON.stringify({ success: false, status: "failed", error: "primary_agent_required" });
    }
    if (context.abort.aborted) {
      return JSON.stringify({ success: false, status: "failed", error: "cancelled" });
    }
    return await new Promise<string>((resolve) => {
      let settled = false;
      let stopping = false;
      let stdout = "";
      let stderr = "";
      let bytes = 0;
      let forced: ReturnType<typeof setTimeout> | undefined;
      const child = spawn("python3", ["-m", "integrations.opencode_commands"], {
        cwd: context.worktree, shell: false, detached: process.platform !== "win32",
        stdio: ["pipe", "pipe", "pipe"],
      });
      const finish = (result: object) => {
        if (settled) return;
        settled = true;
        clearTimeout(deadline);
        if (forced) clearTimeout(forced);
        context.abort.removeEventListener("abort", onAbort);
        resolve(JSON.stringify(result));
      };
      const kill = (signal: NodeJS.Signals) => {
        try {
          if (process.platform !== "win32" && child.pid) process.kill(-child.pid, signal);
          else child.kill(signal);
        } catch { /* O processo pode ter encerrado entre o evento e o sinal. */ }
      };
      const stop = (error: string) => {
        if (stopping || settled) return;
        stopping = true;
        kill("SIGTERM");
        forced = setTimeout(() => { kill("SIGKILL"); finish({ success: false, status: "failed", error }); }, 2_000);
      };
      const onAbort = () => stop("cancelled");
      const deadline = setTimeout(() => stop("timeout"), deadlineMs);
      context.abort.addEventListener("abort", onAbort, { once: true });
      child.on("error", (error) => finish({ success: false, status: "failed", error: "process_error", message: error.message }));
      child.stdin.on("error", () => stop("stdin_error"));
      for (const [stream, collect] of [[child.stdout, (text: string) => { stdout += text; }], [child.stderr, (text: string) => { stderr += text; }]] as const) {
        stream.setEncoding("utf8");
        stream.on("data", (text: string) => {
          bytes += Buffer.byteLength(text);
          if (bytes > maxOutputBytes) stop("output_limit");
          else collect(text);
        });
      }
      child.on("close", (code, signal) => {
        if (stopping) return; // A limpeza forçada conclui o envelope de falha.
        // Também encerra descendentes que sobreviveram ao helper e soltaram
        // seus pipes. O grupo pertence exclusivamente a esta chamada.
        kill("SIGKILL");
        try {
          const report = JSON.parse(stdout);
          if (!report || typeof report !== "object" || typeof report.success !== "boolean" ||
              report.coordinator !== "marceloclaro" ||
              report.status !== (report.success ? "completed" : "failed") ||
              (code === 0) !== (report.success === true) ||
              (report.success && (report.command !== args.command || !report.result || typeof report.result !== "object"))) {
            throw new Error("resultado incompatível com saída do processo");
          }
          finish({ ...report, process: { returncode: code, signal, stderr } });
        } catch {
          finish({ success: false, status: "failed", error: "invalid_process_result", process: { returncode: code, signal, stderr } });
        }
      });
      child.stdin.end(JSON.stringify(args));
    });
  },
});
