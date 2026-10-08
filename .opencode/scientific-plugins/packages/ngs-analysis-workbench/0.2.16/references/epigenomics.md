# Epigenomics guidance

Classify observed material as ATAC accessibility or antibody-targeted ChIP,
CUT&RUN, or CUT&Tag before choosing a method. Read processing, signal tracks,
peak calling, consensus peaks, and differential testing are distinct endpoints.

## Shared design and evidence

- Establish sample identity, biological replicates, organism, reference build,
  alignment state, assay protocol, requested endpoint, and any target regions.
- Verify actual mapped reads, duplicate handling, fragment distributions,
  blacklist compatibility, available controls, and replicate concordance.
- Keep peak coordinates, signal tracks, count matrices, thresholds, reference
  provenance, and software versions attached to the observed workflow output.
- Never treat reads, fragments, lanes, or technical partitions as biological
  replicates; missing controls or reference mismatches remain limitations.

## ATAC-seq accessibility

- Confirm transposition protocol, Tn5 shifting assumptions, mitochondrial
  fraction, nucleosomal fragment pattern, and transcription-start-site signal.
- Inspect observed TSS enrichment, FRiP, library complexity, blacklist
  overlap, and accessible-peak reproducibility when those metrics exist.
- Specify whether the endpoint is accessibility QC, peak identification,
  consensus accessibility, motif analysis, or differential accessibility.
- Peak presence is evidence of detected signal, not differential
  accessibility; comparisons require suitable replicate-level counts and an
  identified statistical contrast.

## ChIP-seq, CUT&RUN, and CUT&Tag

- Establish target protein or histone mark, antibody, control/input/IgG
  pairing, replicate model, spike-ins, and broad-versus-narrow peak biology.
- Preserve assay-specific normalization and background assumptions; do not
  borrow ATAC transposition or accessibility thresholds for antibody assays.
- Inspect actual target enrichment, control background, FRiP or equivalent
  signal, peak reproducibility, spike-in evidence, and signal tracks.
- Separate individual peak calling, consensus binding, and differential
  binding. Binding differences require observed replicate-aware comparisons.

A peak file, browser track, or successful controller process does not prove
target specificity, differential biology, or a validated treatment effect.
