import type { Preview } from "@storybook/react-vite";
import type { CSSProperties } from "react";

import { CODEX_MCP_DEV_THEME_PRESETS } from "./host-theme-fixtures";

import "../src/styles/theme.css";
import "../src/styles/base.css";
import "./storybook.css";

const preview: Preview = {
  decorators: [
    (Story, context) => {
      const hostTheme =
        context.globals.hostTheme === "story"
          ? context.parameters.hostTheme
          : context.globals.hostTheme;
      const theme =
        hostTheme?.endsWith("dark") ||
        (!hostTheme && context.parameters.theme === "dark")
          ? "dark"
          : "light";
      const hostVariables = hostTheme?.startsWith("codex-")
        ? CODEX_MCP_DEV_THEME_PRESETS[theme].variables
        : {};
      return (
        <div
          className="ngs-theme ngs-storybook-shell"
          data-host-display-mode={
            context.parameters.hostDisplayMode === "fullscreen"
              ? "fullscreen"
              : "inline"
          }
          data-story-theme={theme}
          data-host-theme={hostTheme}
          style={
            {
              ...hostVariables,
              ...context.parameters.hostVariables,
              colorScheme: theme,
            } as CSSProperties
          }
        >
          <div
            className="ngs-storybook-stage"
            style={{ maxWidth: context.parameters.storyWidth ?? 960 }}
          >
            <Story />
          </div>
        </div>
      );
    },
  ],
  initialGlobals: { hostTheme: "story" },
  globalTypes: {
    hostTheme: {
      description: "MCP host theme contract",
      toolbar: {
        title: "Host theme",
        icon: "circlehollow",
        dynamicTitle: true,
        items: [
          { value: "story", title: "Story theme" },
          { value: "codex-light", title: "Codex light" },
          { value: "codex-dark", title: "Codex dark" },
          { value: "fallback-light", title: "Fallback light" },
          { value: "fallback-dark", title: "Fallback dark" },
        ],
      },
    },
  },
  parameters: {
    layout: "fullscreen",
  },
};

export default preview;
