# Microbiome and metagenomics guidance

Distinguish marker-gene amplicon analysis from untargeted shotgun sequencing.
Read QC, denoising, taxonomy, diversity, functional profiling, and differential
abundance require different observed inputs, methods, references, and outputs.

## Amplicon microbiome

- Establish the marker and region, primer sequences/orientation, read layout,
  sample identity, technical partitions, negative controls, and extraction blanks.
- Inspect read-quality evidence before selecting truncation, merging, primer
  removal, chimera filtering, or denoising assumptions.
- Verify an actual ASV/feature table before claiming denoised features; require
  an observed taxonomy table and identified database/version for assignments.
- Alpha/beta diversity requires appropriate sample-linked feature data,
  normalization choices, and study metadata; FASTQ QC alone proves neither.
- Keep contaminants, low-depth samples, primer bias, unclassified features,
  database limits, and control behavior visible.

## Shotgun metagenomics

- Establish host organism, required host depletion, paired-read layout,
  controls, sample metadata, reference databases, and the requested endpoint.
- Bind taxonomy and functional database identities separately; a taxonomy
  database does not establish pathway or gene-family annotation.
- Require observed taxonomic tables/reports for organism claims and distinct
  verified functional tables for pathway or gene-family claims.
- Interpret host depletion, contamination, classification uncertainty,
  database coverage, compositional effects, and sequencing depth in context.
- Do not download large reference databases or remove host reads implicitly;
  resource acquisition and transformations require their proper authorization.

## Differential abundance and claim boundaries

- Require sample- or donor-level biological replication, a specified contrast,
  and identifiable group, batch, and covariate effects before testing.
- Choose a method that addresses compositionality, zeros, sequencing depth,
  normalization, and multiple-testing correction for the observed data.
- Relative abundance does not establish absolute microbial load; diversity
  plots, clustered samples, and raw count differences do not establish
  statistically supported differential abundance.

For either assay, preserve marker/protocol, controls, database versions,
sample-linked tables, normalization, workflow provenance, and actual QC
outputs. A completed workflow or attractive plot cannot substitute for missing
ASV, taxonomy, functional, or statistically supported abundance evidence.
