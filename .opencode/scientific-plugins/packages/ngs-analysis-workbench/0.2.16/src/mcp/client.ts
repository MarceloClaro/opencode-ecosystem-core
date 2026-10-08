import {
  App,
  applyDocumentTheme,
  applyHostFonts,
  applyHostStyleVariables,
} from "@modelcontextprotocol/ext-apps/app-with-deps";

type ToolArguments = Record<string, unknown>;
export type HostContext = ReturnType<App["getHostContext"]>;
type HostContextListener = (context: NonNullable<HostContext>) => void;

export interface McpToolCaller {
  call<T>(name: string, arguments_: ToolArguments): Promise<T>;
}

export interface NgsWorkbenchClient extends McpToolCaller {
  connect(): Promise<void>;
  getHostContext(): HostContext;
  onHostContextChanged(listener: HostContextListener): () => void;
  openLink(url: string): Promise<{ isError?: boolean }>;
}

export class NgsMcpClient implements NgsWorkbenchClient {
  private readonly app = new App(
    { name: "NGS Analysis Workbench", version: "0.1.0" },
    { availableDisplayModes: ["inline", "fullscreen"] },
    { autoResize: true },
  );

  connect() {
    return this.app.connect();
  }

  getHostContext() {
    return this.app.getHostContext();
  }

  onHostContextChanged(listener: HostContextListener) {
    const handler = (context: NonNullable<HostContext>) => listener(context);
    this.app.addEventListener("hostcontextchanged", handler);
    return () => this.app.removeEventListener("hostcontextchanged", handler);
  }

  async call<T>(name: string, arguments_: ToolArguments): Promise<T> {
    const result = await this.app.callServerTool({ name, arguments: arguments_ });
    if (isRecord(result) && result.isError === true) {
      throw new Error(toolErrorMessage(result));
    }
    if (!isRecord(result) || !isRecord(result.structuredContent)) {
      throw new Error(`${name} did not return structured content.`);
    }
    return result.structuredContent as T;
  }

  openLink(url: string) {
    return this.app.openLink({ url });
  }
}

export function applyHostContext(context: HostContext) {
  if (!context) return;
  if (context.theme) applyDocumentTheme(context.theme);
  if (context.styles?.variables) applyHostStyleVariables(context.styles.variables);
  if (context.styles?.css?.fonts) applyHostFonts(context.styles.css.fonts);
}

function toolErrorMessage(result: Record<string, unknown>) {
  const content = result.content;
  if (!Array.isArray(content)) return "MCP tool call failed.";
  const text = content.find(
    (item) => isRecord(item) && item.type === "text" && typeof item.text === "string",
  );
  return isRecord(text) && typeof text.text === "string" ? text.text : "MCP tool call failed.";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}
