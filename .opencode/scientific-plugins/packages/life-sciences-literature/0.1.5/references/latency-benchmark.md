# Life Sciences Literature latency benchmark

Measured on August 6, 2026 against the three actual independently packaged literature skills and their live documented public endpoints. Each workflow received two fresh-process cold samples and 20 same-interpreter warm samples; only substantive, evidence-bearing successful responses were counted.

The PubMed Central full-text lookup for `PMC3257301` improved from **529 ms to 360 ms at p50 (-31.9%)**, and from **558 ms to 374 ms at p95**. The workflow still performs its two required S3 requests but now reuses one scoped HTTP session for identifier resolution, version discovery, and article metadata.

The session is closed on success, missing records, malformed responses, and network failures. NCBI API keys remain limited to their own request parameters; PubMed Central record ordering, canonical citation URLs, exact raw response bytes, and deterministic multi-page sidecars are unchanged.

The bioRxiv/medRxiv and PubMed Entrez skills were independently validated in the same run. Their stable direct-record requests already make one upstream HTTP request, so no speculative connection-sharing change was necessary.
