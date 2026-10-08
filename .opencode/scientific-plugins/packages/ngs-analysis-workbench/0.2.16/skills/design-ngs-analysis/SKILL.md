---
name: design-ngs-analysis
description: Translate a biological question or scientific outcome into a defensible NGS analysis plan. Use to define experimental units, groups, covariates, contrasts, endpoints, references, validity gates, evidence needs, methods, or supportable claims before choosing an executable workflow.
---

# Design NGS Analysis

Read [AnalysisContext](../../references/analysis-context.md). Design backward
from the scientific decision, not forward from a pipeline. If material identity
or relationships are insufficient, follow
[understand-ngs-data](../understand-ngs-data/SKILL.md) first. This skill is
read-only and does not register or execute a workflow.

## Resolve the scientific model

Establish or leave explicitly unknown:

- scientific question, decision, assay, and current data state
- biological experimental unit versus technical partitions
- groups, pairing, repeated measures, batches, covariates, and confounding
- contrasts, baselines, endpoints, and quantification level
- organism, genome build, reference, annotation, and identifiers
- evidence required for the claim, failure conditions, and unsupported claims

Do not treat cells, reads, lanes, or capture channels as biological replicates.
Leave unidentifiable comparisons untested. Keep model-based batch adjustment
distinct from visualization-oriented batch removal.

Load only the applicable scientific reference:

- [Basic FASTQ QC](../../references/fastq-qc.md)
- [Bulk RNA-seq](../../references/bulk-rnaseq.md)
- [Single-cell RNA-seq](../../references/single-cell-rnaseq.md)
- [Detailed single-cell guidance](../../references/single-cell-qc-annotation-umap-heuristics.md), before choosing cell thresholds, correction, annotation, or embedding policy
- [Demultiplexing](../../references/bcl-demultiplexing.md), for run-folder and sample-assignment endpoints
- [DNA variants](../../references/dna-variants.md), for germline, somatic, or UMI-panel endpoints
- [Epigenomics](../../references/epigenomics.md), for accessibility or antibody-targeted endpoints
- [Microbiome](../../references/microbiome.md), for amplicon or shotgun taxonomy/function endpoints

For differential expression, apply the bulk or single-cell reference to the
actual matrix state, donor-level replication, design, and requested contrast.
Do not restart read processing when suitable counts and metadata already exist.

For each endpoint define validated inputs, method assumptions, validity gates,
measurements and denominators, comparison structure, required QC/provenance,
and criteria for supported, unsupported, or inconclusive claims. Catalogs may
establish feasibility, but installed software does not choose the scientific
method.

## Output: AnalysisPlan

Add an `analysis_plan` artifact with:

1. objective and decision
2. evidence-backed starting point
3. scientific model and reference assumptions
4. endpoints, comparisons, methods, and rationale
5. evidence contract and validity gates
6. limitations, unknowns, and unresolved choices
7. supported, unsupported, and conditional claims
8. implementation requirements without readiness or approval claims

If results change the question, supersede the prior plan and preserve why.
