---
name: understand-ngs-data
description: Understand an NGS starting point from raw reads, matrices, metadata, references, prior plans, runs, or results. Use when the user asks what data exists, how files and samples relate, whether inputs are usable, what is missing, or which analyses they could support.
---

# Understand NGS Data

Read [AnalysisContext](../../references/analysis-context.md). Inspect and relate
available material without choosing a workflow, installing software,
transforming inputs, or creating an execution plan.

## Inspect

Inventory relevant:

- FASTQs and their raw or derived state
- BCL run folders, sample sheets, index reads, lanes, and demultiplexing outputs
- DNA alignments, VCF/gVCF files, target intervals, and tumor/normal relationships
- chromatin alignments, peak sets, signal tracks, targets, and control libraries
- marker-gene or shotgun inputs, feature/taxonomy tables, and reference databases
- bulk counts, transcript estimates, matrices, and sample metadata
- single-cell matrices or objects (`matrix.mtx`, `*.h5`, `*.h5ad`, `*.rds`)
- library, chemistry, genome, annotation, index, and sample-sheet metadata
- immutable plans, durable run IDs, result projections, and primary artifacts

Record identity, role, provenance, observed state, and sample or artifact
relationships. Prefer parsers, manifests, and workflow-owned metadata over
filenames. Use durable get tools to establish run lifecycle; do not interpret a
nonterminal run.

Load only the applicable scientific reference:

- [Basic FASTQ QC](../../references/fastq-qc.md)
- [Bulk RNA-seq](../../references/bulk-rnaseq.md)
- [Single-cell RNA-seq](../../references/single-cell-rnaseq.md)
- [Detailed single-cell guidance](../../references/single-cell-qc-annotation-umap-heuristics.md), only for existing cell-level QC, annotation, or embedding decisions
- [Demultiplexing](../../references/bcl-demultiplexing.md), for BCLs, index reads, and sample assignment
- [DNA variants](../../references/dna-variants.md), for germline, somatic, or UMI-panel material
- [Epigenomics](../../references/epigenomics.md), for ATAC, ChIP, or CUT&RUN material
- [Microbiome](../../references/microbiome.md), for amplicon or shotgun metagenomic material

Let assay-specific guidance override generic FASTQ advice for protocol-specific
read roles. State supportable tasks in scientific terms, not engine names. Ask
only for missing information that changes sample identity, assay
interpretation, method, or endpoint.

## Output: StartingPointAssessment

Add a `starting_point_assessment` artifact with:

1. known objective
2. material inventory and relationships
3. evidence and provenance
4. supportable tasks and their conditions
5. missing, conflicting, or unusable inputs
6. open questions and at most one pending user decision
7. justified handoff to design, run, or results
