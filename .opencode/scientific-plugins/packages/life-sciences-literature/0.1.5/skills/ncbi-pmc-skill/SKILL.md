---
name: ncbi-pmc-skill
description: Retrieve compact PMC Article Dataset metadata for PMCID, PMID, or DOI lookups. Use when a user wants open-access status, license, retraction status, or current article file URLs; save raw JSON only on request.
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Add claim-adjacent links only for substantive claims supported by returned `sources`; never cite empty, metadata-only, or failed lookups.
- Preserve `checked_sources`, use only supported `canonical_url` mappings, and leave requested raw or machine-readable output unchanged.
- Use the `ncbi-pmc-skill` entry in `../../references/source-links.json` and follow `../../references/source-presentation.md`.

## Operating rules
- Use `scripts/ncbi_pmc.py` for all PMC Article Dataset metadata calls in this package.
- This skill is intentionally narrow: it resolves one PMCID, PMID, DOI, or text identifier through PMC ESearch when needed and reads versioned metadata from the current public PMC Cloud dataset.
- Pass the identifier under `params.id`; use `params.retmax` only when a non-PMCID lookup may resolve to multiple PMC records.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script output by default.
- Report the returned open-access, manuscript, retraction, license, and HTTPS file URL fields directly rather than inferring availability.
- Return raw JSON metadata only if the user explicitly asks for machine-readable output.
- Prefer targeted endpoint calls instead of broad unfiltered dumps.
- If the user needs the full raw response, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Required field: `params.id`
- Optional fields: `params.retmax`, `max_items`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common PMC Article Dataset patterns:
  - `{"params":{"id":"PMC3257301"},"max_items":10}`
  - `{"params":{"id":"22966082"},"max_items":10}`
  - `{"params":{"id":"10.1093/nar/gkr1184"},"max_items":10}`

## Output
- Success returns `ok`, `source`, resolved `pmcids`, record counts, `truncated`, and compact versioned `records` containing license, retraction, and file URL metadata.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"params":{"id":"PMC3257301"},"max_items":10}' | python scripts/ncbi_pmc.py
```
