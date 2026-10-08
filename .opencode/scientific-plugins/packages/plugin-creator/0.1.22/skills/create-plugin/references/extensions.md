# MCP Apps and Extensions

Use the workflow table in [Create a plugin](../SKILL.md#extensions) to choose
Extensions, then follow the relevant SDK and example implementation.

## Read the relevant implementation docs

Read the relevant sections of the
[protocol spec](https://github.com/openai/mcp-extensions/blob/main/docs/spec.md)
and the SDK guide for the app's stack:
[Python](https://github.com/openai/mcp-extensions/blob/main/python/README.md) or
[TypeScript](https://github.com/openai/mcp-extensions/blob/main/typescript/README.md).
Keep a Python MCP server in Python; its browser UI can use the TypeScript app
SDK without changing the server's language.
Use the installed release tag or source commit for SDK APIs instead of `main`;
for a new project, choose a supported [release](https://github.com/openai/mcp-extensions/releases).
Use the current support table when available; do not copy a fixed platform matrix
into the plugin. If remote docs are unavailable or omit a capability, use installed
types, bundled docs, and host capabilities, and flag support you cannot verify.
Keep protocol mechanics in those docs.

## Learn from Bits & Bolts

Use [Bits & Bolts](https://github.com/openai/mcp-extensions/tree/main/plugins/bits-and-bolts)
as a guiding reference for Extension integration patterns:

- Its Parts Library opens from global navigation, while the Parts Tray stays
  beside a conversation. A project tracker can use the same pattern for a
  project browser and the current conversation's selected tasks.
- Its settings view persists measurement units and grid preferences. A charting
  app can expose its own display preferences through a settings entrypoint.
- Its file viewer reads a host-managed CAD file, attaches a selected surface
  as model context, and saves edits with version checks. A CSV editor can adapt
  that pattern for a selected row and an edited file.

Follow the relevant server metadata and UI bridge usage; adapt the patterns to
the app's language and workflow rather than copying the example's full stack.

## Implement in the app's server and UI

New apps default to a cloud plugin hosted by [Sites MCP](sites-mcp.md).
Add Extensions to that same Site's MCP server and UI, and use the Sites MCP
publishing and connection workflow. For an existing app or an explicitly local
workflow, preserve its source, hosting, runtime, and authentication.

For a catalog browser like Bits & Bolts, register the HTML view as an MCP
resource and associate an opener tool through the installed MCP Apps SDK's
metadata. Connect the view with the SDK's host bridge so the UI and chat tools
work with the same persisted catalog. Add a global entrypoint if users should
open it from navigation; keep catalog search usable without opening the view.
A website URL or JSON tool result alone does not register an app view.

For **every widget**, explicitly choose its supported display modes and preferred
mode using the installed SDK and [display-preference specification](https://github.com/openai/mcp-extensions/blob/main/docs/spec.md#preferred-model-display-mode).
Use that version's metadata fields and placement; do not mix API versions.

Default to fullscreen only; in a Codex conversation this is the side panel.
Include inline only when the interaction belongs in the conversation,
such as a confirmation card, a one-time action, or a simple, ephemeral visual.
Supporting a compact layout alone is not a reason to enable inline. Declare
both modes only when each offers a useful experience; prefer inline for an
inline-only widget. Verify actual placement rather than relying on the preference.

For file access, use the host's resource bridge and granted write capability.
Sending a filesystem path to a remote server does not grant it local access.
Preserve unsaved changes and version checks when saving. For context and
mentions, resolve the selected record under its access rules and attach only
the relevant data. Attaching context does not send a message or authorize an
action on that data.

## Open and verify

Once connected, invoke the app's opener in the intended host. Use its launch
result instead of calling the opener again from the UI for the same data.
Check the requested controls, placement, and data changes; a JSON result alone
does not prove the view rendered. Report unverified host behavior separately.

Display-mode preferences are hints. If fullscreen was intended but the host
starts inline, check host context after `app.connect()` and request fullscreen
once only when the host advertises it. Use the installed SDK's API and accept
the returned mode. Do not expand a widget intentionally designed for inline use.

Retry tool discovery briefly after installation before reporting it pending.
If the host requires a fresh task, offer one with the existing plugin; create
it only when authorized. Obtain the exact plugin reference through discovery
and include `[@Plugin name](plugin://<name>@<marketplace>)` in the task prompt;
a plain-text name does not preselect the plugin. Include the user's request,
source location, Site ID when applicable, current state, and remaining work.
Verify tool availability there before claiming success. Do not create a
replacement plugin or repeatedly create tasks to refresh tools.
