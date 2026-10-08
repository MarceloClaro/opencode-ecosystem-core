# Single-cell RNA-seq guidance

Use this guidance for single-cell or single-nucleus RNA-seq starting from FASTQs,
count matrices, Cell Ranger-style output, AnnData, Seurat, or related objects.
Determine whether the endpoint is count generation, post-count QC, clustering,
annotation, visualization, or downstream statistical comparison.

Read the basic FASTQ QC reference when raw-read quality interpretation is needed,
but let this reference control barcode, UMI, chemistry, and read-role decisions.

## What to inspect

- input type and whether raw counts and sample provenance are preserved
- single-cell versus single-nucleus assay
- chemistry or explicit barcode, UMI, cDNA, index, and whitelist layout
- organism, tissue, reference, and expected cells when known
- sample, donor, batch, capture channel, and multiplexing metadata
- desired endpoint and whether a compatible annotation reference exists

Do not infer chemistry from filenames. Do not alter protocol-specific read
segments through generic trimming without confirming their biological role.

## FASTQ to count matrix

- Choose a counting method compatible with the observed chemistry, read layout,
  whitelist, organism, and desired output rather than selecting by engine alone.
- Treat vendor-standard output as an explicit user choice with its associated
  terms and constraints, not as the universal default.
- Preserve sample and capture identity through barcode and feature matrices.
- Record the reference, chemistry, whitelist, cell-calling assumptions, and
  workflow-generated QC evidence.

Counting and post-count interpretation are separate scientific decisions. A
successfully generated matrix is not evidence that cell calling, doublets,
ambient RNA, sample quality, or annotation are acceptable.

## Post-count QC and annotation

- Preserve raw counts and per-sample or per-channel provenance. Make any loss of
  raw counts or sample identity explicit before continuing.
- Choose cell-level thresholds from observed distributions and expected biology,
  reviewing detected genes, total counts, mitochondrial fraction, and relevant
  nuisance signals overall and by technical partition.
- Treat nonstandard metrics primarily as review signals. Do not turn them into
  hard filters without dataset-specific evidence and user agreement.
- Assess doublets within realistic capture partitions and retain scores and calls.
- Assess ambient RNA when supported by the dataset and method.
- Prefer a passes-QC annotation over irreversible deletion when auditability matters.
- Choose conventional PCA or a learned latent representation according to scale,
  batch structure, integration needs, and the analytical question.
- Match annotation references by species, tissue, assay, chemistry, and biological
  state. Use conservative hierarchical labels and retain uncertainty.
- Keep visualization decisions separate from filtering and preserve legible global
  and per-group views.
- Keep matrices sparse, avoid whole-object copies, and checkpoint major stages for
  large datasets.

Use the detailed single-cell heuristics before choosing
specific thresholds, a doublet method, latent-space integration, annotation
backend, or UMAP feature panel.

## Replicate-aware downstream comparisons

- Treat the biological sample or donor as the experimental unit. Cells and
  capture channels are not independent biological replicates.
- Before differential expression or abundance testing, confirm unique sample
  and donor identifiers, group assignments, pairing, batch and covariate
  structure, sufficient biological replication, and an identifiable design.
  Leave a comparison untested when replication is inadequate or the requested
  effect is confounded.
- For expression comparisons within a cell type or state, preserve raw counts
  and construct sample- or donor-level pseudobulk counts when that matches the
  method assumptions. Define the aggregation, inclusion rules, design, baseline,
  and contrasts explicitly. Do not run an ordinary cell-level test that treats
  cells from the same sample as independent observations.
- Use a replicate-aware cell-level mixed model only when it is deliberately
  selected for the study design and its assumptions are reviewed and recorded.
- For differential abundance, use a replicate-aware method and state the
  population denominator and sampling assumptions; do not test cell counts as
  independent events.
- Keep post-count QC and annotation, label or state selection, and downstream
  statistical comparisons as separate reviewed stages. Record which cells,
  labels, samples, and covariates enter each comparison.

## Evidence to carry forward

Preserve the raw-count object, sample metadata, chemistry and reference provenance,
cell-calling assumptions, thresholds and justification plots, cells flagged at
each decision, doublet and ambient-RNA evidence, latent-space choice, annotation
backend and confidence, visualization outputs, biological-replicate identifiers,
pseudobulk or mixed-model construction, exact designs and contrasts, package
versions, and unresolved biological limitations.
