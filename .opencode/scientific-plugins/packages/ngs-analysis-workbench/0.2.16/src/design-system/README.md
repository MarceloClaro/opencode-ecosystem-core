# NGS visual foundation

The spacing, type, shape, control and motion foundations come from Product
Design's **OpenAI Design System**, `0.1.53-internal.19`, with `codex-desktop`.
`tokens.css` and `motion.css` preserve the source values. `../styles/theme.css`
adapts them to the existing MCP Apps host contract. Host variables supply the palette, fonts and theme changes. Shape follows the explicit product direction
below. Control text removes surface-token alpha and
light-theme semantic text mixes toward primary text for readable contrast.

Aliases resolve at each `.ngs-theme` boundary, not only `:root`, because
Storybook and embedded consumers may supply their theme below the root.
Light/dark fallbacks use the Codex desktop foundation and its MCP host fixtures.

`Icon` is the supplied masked-image primitive ported to TypeScript. Its SVGs
are unmodified approved `public/icons/` assets from the template's verified
shared bundle, except the explicitly user-selected Codex `check-md.svg` and
`regenerate.svg` from
`codex/codex-apps/webview/src/icons/`. Assets are stored alongside the primitive
and imported with `?inline` so both single-file MCP resources remain
self-contained. `icons/provenance.json` records exact hashes and overrides.
Do not add another icon library, text glyphs,
emoji, CSS drawings or custom SVG paths as interface icons. The existing helix
remains the branded app icon. Scientific identifiers retain their source case;
human-facing labels use sentence case.

Motion uses foundation durations and easing. Native dialog semantics, Escape
dismissal, focus restoration, hidden sidebar semantics and reduced motion must
remain intact. Loading motion never implies invented progress.

Host contract references:

- `codex/palett/src/host-adapters/mcp/widget-host-theme.ts`
- `codex/palett/src/dev-host/codex-mcp-theme-fixtures.ts`
- `@modelcontextprotocol/ext-apps` host style and document theme helpers
- `codex/codex-apps/webview/src/local-conversation/items/mcp-app-host-styles.ts` (native desktop mapping)

## Shape and icon guidance

Use 12 px for controls, 16 px for panels/callouts, and 20 px for large surfaces
such as dialogs. This explicit product direction overrides host radius values;
host colors and typography still apply. Keep full radius for pills or circular
status marks. Flat sections and dividers do not need a rounded container.

Use the Codex `check-md` at 16 px in compact status chips, attempt tabs and
copy feedback, following Codex's `icon-xs` copy/menu usage. The SVG's
17 px viewBox is not a mandate for its rendered size. Keep the idle copy icon
at the same 16 px size as its confirmation. The larger process rail's 24 px
status circles use a 20 px check. In run-history attempt traces, render every
status glyph and spinner at 14 px inside its 20 px circle. Elsewhere, other
status glyphs remain at 20 px; use
`close-medium` for failure marks and dialog dismissal.
`close-small` has a more inset drawing in its 24 px source canvas; shrinking it
to a 12–14 px box made it optically undersized beside the check icon. Keep the
source assets unchanged and adjust the primitive size instead of editing paths.

Use adjacent keyboard-operable disclosures for source files, provenance and
execution evidence. Keep scientific warnings, failures and result summaries
visible. Do not put essential information exclusively in hover tooltips.

Use the shared `CopyButton` for file paths, the run folder and analysis prompts.
It pairs the approved copy icon with a text label, then shows a check and
"Copied" after success. Preserve contextual accessible names and live feedback.

## Chips

Use `Chip` for neutral engine, catalog, compute, and count labels. Use
`StatusChip` for workflow, attempt, process, and inline status labels. Both
share a 24 px minimum height, 12 px host-aware medium text, 8 px horizontal
padding, full pill radius, and a subtle opaque fill. Status chips add the
approved 16 px check or 20 px other status glyph and semantic text color.
Only active work spins; blocked,
queued, cached, and completed retain their own labels and existing meaning.
The report's Analysis completed label uses the same success StatusChip; it
describes execution completion, not a passing scientific QC verdict.

Do not use chip styling for interactive attempt selectors, navigation controls,
or compact timeline markers. Static chips have no independent hover state;
their opaque fill stays consistent inside a hovered row.

## Workbench layout

Keep Runs, Pipelines, and Compute at the app level. Inside a run, the main pane
holds the scientific result or current execution; Run history is the inspector
of that run's workflow attempts, not another global history page. Selecting an
older attempt must preserve the analysis in the main pane.

Fullscreen Storybook stories use `storyWidth: "none"` so the app chrome fills the
preview viewport. Keep explicit widths for narrow fixtures and embedded stories;
the report's own reading-width constraints are separate from the app shell.

Use compact persistent app and context bars. In fullscreen, analysis and attempt
details scroll independently. The inspector extends to the run context bar;
its header is the single Run history open/close control, with no additional X.
Tabs labeled Attempt 1, Attempt 2, and so on stay visible below it. Use
tabs only when more than one attempt is available; a single attempt renders
directly as a named details region without a tab bar or tabpanel semantics. Use
[`@base-ui/react` Tabs](https://base-ui.com/react/components/tabs), pinned to
1.5.0 to match the Codex Palett dependency, for selection, roving keyboard focus,
tab/panel accessibility relationships, and panel transition lifecycle. The
headless primitive receives the OpenAI host-aware styles here. Left/Right/Home/End
move focus; Enter or Space activates because loading an older attempt may take
time. Keep tabs on one line with native horizontal overflow, hide the scrollbar,
and reveal the selected tab after selection, reopening, or resizing. Do not scroll
the report.
Fade 24 px of the tab strip only at edges with hidden content, updating on scroll
and resize. Reveal focused/selected tabs beyond the fade so their labels and
focus rings remain legible. Keep the tab strip's bottom divider outside the
mask, but omit the divider under the Run history heading. Retain the sidebar's
vertical pane boundary.
Use 14 px host-aware semibold text for both the Run history pane heading and
Attempt status heading; keep the collapsed pane toggle at its standard medium weight.
Use the regular underline tab bar: 36 px tab height, 12 px text, and 8 px
padding. The 2 px shared underline moves over 220 ms and panels fade over
140 ms; inactive
panels become inert during exit and unmount afterward. Disable both transitions
for reduced motion.
Show the same approved status icon in each attempt tab as in its status chip;
only active execution spins. Keep the selected workflow status under Attempt
status, with Refresh status beside that heading. Surface the recorded start or
finish time and relevant progress; omit the latest-task row after successful completion.
Warnings and recorded failures stay prominent. Keep technical evidence below
in uniform 44 px disclosure rows, regardless of whether a row has a count chip.
Omit the empty execution-activity placeholder in compact terminal attempts.
Keep actual evidence-unavailable reasons and recorded failure details. Outside
the inspector, missing terminal evidence uses a neutral statement, not Waiting.
Sidebar disclosure labels align with the content margin and put chevrons at
the trailing edge. Sticky bars, inspectors, and modal surfaces retain the host
background hue but remove alpha so underlying content cannot bleed through.
The compact Refresh status control is a 32 px icon button with the unmodified
20 px Codex `regenerate` asset, as used by the Codex review toolbar. Use
Base UI Tooltip for hover and keyboard focus, with its portal inside the
current theme boundary or native dialog. Escape dismisses an open tooltip
before the drawer. Keep the accessible name, disabled busy state and spinner.
Visible summary label/value pairs use the same body text size; shared status
chips retain their standard small text. Warning callouts use the info icon's
own circle without a second filled disc.
At narrow container widths, default the inspector closed
and open it as a native modal drawer with Escape, focus restoration, and the
same selected attempt. Do not stack the inspector below a long report.

Separate ordinary sections with spacing and heading hierarchy. Give each report
title the host's medium heading size (24 px fallback) and semibold weight,
with its matching line height, above the 14 px section headings. Place the report
action beside the completion chip; let the title, description and metadata span
the header below them, retaining the text reading-width limits. Metadata uses
the full header width, and the run ID is capped only by available space. Below
760 px, place the action after the metadata. Give each report
metric its own 16 px-radius card. Use light dividers between artifact and task
list rows, as well as app chrome, pane boundaries, and table structure. Keep summaries and
scientific warnings visible; collapse detailed task attempts and execution
evidence by default, except for failed task attempts. Resource labels stay on
one line and their label/value pairs wrap together when space is limited.
