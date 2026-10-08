import {
  App,
  applyDocumentTheme,
  applyHostFonts,
  applyHostStyleVariables,
} from "@modelcontextprotocol/ext-apps/app-with-deps";

export type ToolArguments = Record<string, unknown>;
export type ToolPayload = Record<string, unknown>;

export interface InlineSnapshot {
  input?: ToolArguments;
  payload?: ToolPayload;
  error?: string;
  cancelled?: string;
}

type SnapshotListener = (snapshot: InlineSnapshot) => void;

export class InlineMcpClient {
  private readonly app = new App(
    { name: "NGS Run Review", version: "0.1.0" },
    {},
    { autoResize: true },
  );

  private connectPromise?: Promise<void>;
  private snapshot: InlineSnapshot = {};
  private readonly listeners = new Set<SnapshotListener>();

  constructor() {
    this.app.ontoolinput = ({ arguments: input }) => {
      this.update({ input: input ?? {} });
    };
    this.app.ontoolresult = (result) => {
      if (result.isError) {
        this.update({ error: toolErrorMessage(result), payload: undefined });
        return;
      }
      if (!isRecord(result.structuredContent)) {
        this.update({ error: "The tool did not return structured content.", payload: undefined });
        return;
      }
      this.update({ payload: result.structuredContent, error: undefined });
    };
    this.app.ontoolcancelled = ({ reason }) => {
      this.update({ cancelled: reason ?? "The tool call was cancelled." });
    };
    this.app.onhostcontextchanged = (context) => applyHostContext(context);
  }

  connect() {
    if (!this.connectPromise) {
      this.connectPromise = this.app.connect().then(() => {
        applyHostContext(this.app.getHostContext());
      });
    }
    return this.connectPromise;
  }

  subscribe(listener: SnapshotListener) {
    this.listeners.add(listener);
    listener(this.snapshot);
    return () => {
      this.listeners.delete(listener);
    };
  }

  async call(name: string, arguments_: ToolArguments): Promise<ToolPayload> {
    await this.connect();
    const result = await this.app.callServerTool({ name, arguments: arguments_ });
    if (result.isError) throw new Error(toolErrorMessage(result));
    if (!isRecord(result.structuredContent)) {
      throw new Error(`${name} did not return structured content.`);
    }
    return result.structuredContent;
  }

  private update(update: Partial<InlineSnapshot>) {
    this.snapshot = { ...this.snapshot, ...update };
    for (const listener of this.listeners) listener(this.snapshot);
  }
}

function applyHostContext(context: ReturnType<App["getHostContext"]>) {
  if (!context) return;
  if (context.theme) applyDocumentTheme(context.theme);
  if (context.styles?.variables) applyHostStyleVariables(context.styles.variables);
  if (context.styles?.css?.fonts) applyHostFonts(context.styles.css.fonts);
}

function toolErrorMessage(result: { content?: unknown }) {
  if (!Array.isArray(result.content)) return "MCP tool call failed.";
  const text = result.content.find(
    (item) => isRecord(item) && item.type === "text" && typeof item.text === "string",
  );
  return isRecord(text) && typeof text.text === "string" ? text.text : "MCP tool call failed.";
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}
