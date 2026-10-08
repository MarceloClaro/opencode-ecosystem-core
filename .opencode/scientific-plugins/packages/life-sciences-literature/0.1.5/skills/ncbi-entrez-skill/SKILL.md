---
name: ncbi-entrez-skill
description: Submit compact NCBI Entrez E-Utilities requests for PubMed publication search, summaries, fetches, and links; save raw JSON or XML only on request.
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Add claim-adjacent links only for substantive claims supported by returned `sources`; never cite empty, metadata-only, or failed lookups.
- Preserve `checked_sources`, use only supported `canonical_url` mappings, and leave requested raw or machine-readable output unchanged.
- Use the `ncbi-entrez-skill` entry in `../../references/source-links.json` and follow `../../references/source-presentation.md`.

## Operating rules
- Use `scripts/ncbi_entrez.py` for all Entrez calls in this package.
- Set `params.db=pubmed` on every request; if `params.dbfrom` is provided, it must also be `pubmed`.
- If `params.linkname` is provided, use only `pubmed_pubmed` or a `pubmed_pubmed_*` link.
- Use explicit `endpoint` values such as `esearch`, `esummary`, `efetch`, `elink`, or `einfo`.
- Search-style Entrez calls are better with `retmax=10` and `max_items=10`.
- Route PubMed Central Open Access and full-text requests to `ncbi-pmc-skill`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script output by default.
- Return raw JSON or XML only if the user explicitly asks for machine-readable output.
- Prefer targeted endpoint calls instead of broad unfiltered dumps.
- If the user needs the full raw response, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Required fields: `endpoint` and `params.db=pubmed`.
- Optional fields: `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`.
- Common PubMed patterns:
  - `{"endpoint":"esearch","params":{"db":"pubmed","term":"KRAS AND colorectal cancer","retmode":"json","retmax":10},"max_items":10}`
  - `{"endpoint":"esummary","params":{"db":"pubmed","id":"22966082","retmode":"json"},"max_items":10}`
  - `{"endpoint":"efetch","params":{"db":"pubmed","id":"22966082","retmode":"xml"},"response_format":"xml","max_items":10}`
  - `{"endpoint":"elink","params":{"dbfrom":"pubmed","db":"pubmed","id":"22966082","retmode":"json"},"max_items":10}`

## Output
- Success returns `ok`, `source`, endpoint metadata, and either compact `records`, a compact `summary`, or `text_head`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"endpoint":"esearch","params":{"db":"pubmed","term":"TP53 AND cancer","retmode":"json","retmax":10},"max_items":10}' | python scripts/ncbi_entrez.py
```
