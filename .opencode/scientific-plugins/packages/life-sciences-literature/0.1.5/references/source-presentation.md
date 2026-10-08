# Evidence and source presentation

Every externally sourced scientific claim needs a response that actually supports it; successful retrieval alone is not evidence.

- Add claim-adjacent Markdown links only for substantive external claims supported by the response, using a deterministic authoritative record URL whenever one exists.
- Keep successful connectivity, schema, service-metadata, identifier-resolution, empty-result, and checked-but-empty lookups exclusively in `checked_sources`. Failed lookups do not provide citations.
- Evidence-bearing `sources` entries must include `supports_claim=true` and `kind=evidence`. Orchestration and synthesis must propagate only downstream entries carrying both properties.
- Use explicit, validated DOI, PMID, and PMCID mappings from `source-links.json`; never invent a deep link for an unsupported source or identifier.
- Redact credentials, tokens, API keys, email, session identifiers, private search or patient terms, request-body values, URL userinfo, and fragments from all provenance URLs.
- Raw JSON, XML, FASTA, or text responses must remain byte-for-byte identical to the upstream payload. Save structured sources separately; never inject Markdown or source metadata into raw output.
