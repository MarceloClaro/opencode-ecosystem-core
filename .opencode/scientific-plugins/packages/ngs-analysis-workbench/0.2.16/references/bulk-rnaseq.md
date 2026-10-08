# Bulk RNA-seq guidance

Use this guidance for bulk RNA-seq requests starting from FASTQs, aligned reads,
transcript estimates, or a count matrix. Determine whether the user wants read
processing, quantification, differential expression, or a combination. Read the
basic FASTQ QC reference separately when raw-read interpretation or trimming is
part of the request.

## What to inspect

- organism, genome build, annotation release, and gene identifier convention
- FASTQ or aligned-read layout and paired-versus-single status
- strandedness or whether it must be inferred
- sample metadata, biological condition, replicates, batch, pairing, and covariates
- desired quantification level: genes, transcripts, or both
- requested contrasts, baselines, and downstream deliverables

Do not make the user restate values that can be recovered from an existing
sample sheet, count matrix, metadata table, or workflow output.

## Read processing and quantification

- Keep genome FASTA, annotation, transcriptome, and indexes from compatible
  releases and record their provenance.
- Infer unknown strandedness before final counting and flag disagreement between
  configured and observed library orientation.
- Treat alignment, pseudoalignment, and existing lab protocols as distinct
  method choices rather than interchangeable implementations.
- Review workflow-produced evidence such as mapping or assignment rate,
  duplication, insert size, rRNA or mitochondrial signal, gene-body bias, and
  sample outliers when available.
- Preserve integer raw counts or Salmon's potentially fractional estimated `NumReads` separately from normalized expression; never label estimated counts as raw integer observations.
- Before interpreting bundled Salmon gene-level outputs, inspect `tx2gene_coverage.json` and `gene_level_artifacts_created`; transcript outputs do not establish valid transcript-to-gene coverage or guarantee gene-level matrices.
- Carry sample metadata forward without silently rewriting sample identity.

Do not begin differential expression merely because a workflow produced a
matrix. First confirm that the count representation, metadata, replication,
design, and requested contrasts support the comparison.

When counts and metadata are separate objects, require unique sample identifiers
and an exact one-to-one match between the selected count-matrix columns and
metadata rows. Report duplicate, missing, and extra identifiers explicitly.
Reorder metadata only by identifier after validating that mapping; never rely on
positional order or silently guess an identifier transformation.

## Differential expression

- Start directly from verified existing counts or expression matrices when
  they already satisfy the requested endpoint; do not rerun FASTQ processing.
- Identify whether values are raw integer counts, normalized expression, or
  log-transformed values before choosing a statistical method. Do not apply
  count-based normalization or models to already transformed measurements.
- Require one biological sample per aligned count-matrix column and metadata
  row; preserve excluded samples and keep technical replicates distinct.
- State the design formula, coefficient or contrast, baseline, and relevant
  covariates explicitly.
- Model donor or subject for paired and repeated-measures studies.
- Keep adjustment for batch in the statistical model distinct from removing
  batch effects for visualization.
- Do not filter genes using post-hoc knowledge of the desired result.
- Select DESeq2, edgeR, limma-voom, or a lab-standard method according to the
  data representation and study design; do not force a universal framework.
- Report effect size, uncertainty, adjusted significance, and filtering status,
  not only a ranked list of significant genes.
- Confirm the tested feature universe and multiple-testing correction; a
  nominal p-value, enrichment plot, or PCA separation is not a validated
  differential-expression result.
- Leave a requested comparison untested when replication or identifiability is
  inadequate, and explain the blocker rather than manufacturing a result.

## Evidence to carry forward

For quantification, preserve the sample sheet, reference provenance, observed count or estimated-count representation, transcript-to-gene mapping and its coverage when used, sample metadata, QC evidence, method, and important failures. For differential expression, preserve the exact design and contrasts, exclusions, package and method provenance, QC plots, complete result tables, and limitations caused by sample size, confounding, or failed libraries.
