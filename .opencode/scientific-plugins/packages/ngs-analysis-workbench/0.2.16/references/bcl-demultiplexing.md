# BCL demultiplexing guidance

Use this reference when the actual input is a sequencing run folder or the
requested endpoint is sample assignment and BCL-to-FASTQ conversion. Existing
demultiplexed FASTQs should enter the appropriate downstream assay instead.

## Establish the run and sample model

- Inspect `RunInfo.xml`, available run parameters, base-call directories, and
  the exact sample-sheet format without modifying them.
- Establish instrument, flow cell, cycles, lane structure, samples, and whether
  lane outputs should remain separate or be combined.
- Verify index lengths, single-versus-dual indexing, i5 orientation, allowed
  mismatches, and collision risk for the actual instrument and library.
- Preserve inline barcodes, UMIs, read roles, masking, and any explicitly
  requested adapter handling; do not infer index orientation from filenames.
- Identify the existing converter, its version, resource needs, and relevant
  licensing. Never install or obtain proprietary software implicitly.

An absent sample sheet, ambiguous index orientation, duplicate sample/index
assignments, missing read structure, or insufficient output space remains an
explicit blocker rather than a guessed demultiplexing policy.

## Interpret only actual conversion evidence

- Confirm verified per-sample FASTQs, read pairing, read counts, and sample
  identity against the approved sample sheet.
- Review available yield, clusters passing filter, lane-level assignment,
  undetermined reads, unexpected index sequences, and contamination or hopping.
- Keep raw run-folder identity, sample-sheet provenance, converter version,
  settings, lane policy, and output layout attached to the result.
- Treat severe assignment anomalies as unresolved even when conversion exits
  successfully; do not start downstream processing merely because files exist.

Demultiplexing evidence does not establish read-quality acceptance, expression,
variant calls, taxonomy, or any downstream biological conclusion.
