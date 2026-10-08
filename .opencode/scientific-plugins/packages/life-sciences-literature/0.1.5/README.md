# Life Sciences Literature

Life Sciences Literature is a focused Codex plugin for biomedical publication discovery. It covers peer-reviewed records, open-access article availability, and bioRxiv or medRxiv preprints without requiring the broader Life Science: Research plugin.

## Included skills

- `biorxiv-skill` for bioRxiv and medRxiv metadata and publication linkage
- `ncbi-entrez-skill` for PubMed publication search, summary, fetch, and link workflows
- `ncbi-pmc-skill` for PMC Open Access availability metadata

## Standalone ownership

All three skills, the plugin-local `scripts/literature_source_contract.py` runtime helper, and the source registry and presentation contract under `references/` are owned under `chatgpt/oai-maintained-plugins/plugins/life-sciences-literature/`. The plugin has no runtime, build, or distribution dependency on another life-science plugin and remains usable when those plugins are removed.

The initial copies preserve the implementations present on `origin/master` at `c1cb315bdb09128189f7d40f5034c7cc00645a1d`. From this point forward, this plugin owns its copies independently; changes in the original plugin do not propagate automatically.

## Evidence and source contract

Each retrieval skill emits structured evidence-bearing `sources` only for responses that support a scientific or record-specific claim. Connectivity checks, metadata-only responses, and empty results instead appear under `checked_sources`. DOI, PMID, and PMCID links are constructed only from validated registry mappings; search terms, API keys, tokens, sessions, and private values are redacted from provenance URLs. Explicitly requested raw JSON, XML, FASTA, and text artifacts preserve their upstream bytes exactly.

Validate all three skills and their standalone source registry with `python scripts/validate_source_contract.py`, and run `python -m pytest tests skills/ncbi-entrez-skill/scripts/test_ncbi_entrez.py skills/ncbi-pmc-skill/scripts/test_ncbi_pmc.py`.

## Example prompts

- Find recent PubMed papers and bioRxiv preprints about TREM2 in microglia.
- Check whether a PMID or DOI has an open-access article package in PMC.
- Compare a preprint record with its linked published article.
