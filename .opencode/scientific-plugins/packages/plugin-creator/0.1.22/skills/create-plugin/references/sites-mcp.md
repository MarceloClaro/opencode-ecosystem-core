# Host a plugin with Sites MCP

Sites MCP is the default hosting path for a new cloud plugin. Read the
available Sites plugin's `sites-mcp` skill and follow its setup,
authentication, publishing, and connection workflow. Use `sites-building` and
`sites-hosting` as directed there. If the skill or backend is unavailable,
explain the gap and continue independent source work without promising a
working connection or substituting another host.

## Build the requested surface

Reuse an existing Site's source and project identity. Let `sites-mcp` own the
server implementation; choose the user-facing surface from the request:

- **Tools used in chat:** build the MCP endpoint and required storage. Keep the
  website page minimal: the app's purpose and useful connection/status information.
- **Interactive views:** add an MCP App when a view helps the workflow. Choose
  useful [Extensions](extensions.md) and follow that guide's implementation and
  verification steps. A published website URL is not an MCP App view.
- **A website people will use:** follow `sites-building` and `sites-hosting`.
  Add MCP to the same application when the request also needs tools in chat;
  a standalone website does not require a plugin or MCP server.

## Publish and connect

Sites publishing provisions the App and its canonical private plugin. Follow
the Sites skill's readiness and connection steps, then verify the requested
tools and any in-chat view. Do not use `create_plugin` to create a duplicate,
including while provisioning is pending. Reuse the existing App/plugin on updates
and preserve Site sharing and plugin access separately. Honor source-only requests without deploying.

The account archive editor rejects canonical App plugins. To add skills to a
Site-generated plugin, first verify an editor supports it and preserves those
files on later Site publishes; otherwise report the limitation.
