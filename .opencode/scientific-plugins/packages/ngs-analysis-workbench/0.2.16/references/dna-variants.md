# DNA variant analysis guidance

Select a germline, somatic, or UMI-panel policy from observed material, sample
relationships, molecular protocol, and requested endpoint. FASTQs, aligned
BAM/CRAM files, gVCFs, and final VCFs represent different starting states;
avoid rerunning upstream stages when verified downstream inputs already exist.

## Shared prerequisites

- Establish WGS, exome, or targeted-panel design; specimen identity; read or
  alignment state; and biological sample relationships.
- Verify reference build, contig naming, FASTA/index identity, annotation,
  target or bait intervals, and caller-specific supporting resources.
- Inspect actual coverage, alignment, duplication, contamination, allele
  support, filter state, and relevant reference/resource provenance.
- Keep low coverage, target gaps, sample swaps, incompatible builds, or absent
  controls visible; VCF existence alone is not a validated variant call.

## Germline and inherited analyses

- Distinguish singleton, cohort, family, duo, and trio designs; preserve
  pedigree, sex/ploidy, relatedness, and sample-identification assumptions.
- Specify per-sample VCF, gVCF generation, joint genotyping, or annotation as
  separate endpoints. Joint-called cohort results require actual joint evidence.
- Use recalibration or known-sites resources only when independently verified
  against the same reference and capture design.
- Inspect genotype, depth, allele balance, quality/filter fields, and available
  Mendelian or concordance checks before describing observed inherited calls.

## Somatic and tumor analyses

- Establish exact tumor/normal pairing, tumor-only status, assay intervals,
  purity, contamination, panel-of-normals, and germline-resource compatibility.
- Inspect actual caller/filter evidence, allele fractions, normal support,
  orientation artifacts, and coverage before describing candidate variants.
- Tumor-only calls are candidate findings with unresolved germline origin;
  never present them as confirmed somatic without independent supporting data.

## UMI and duplex-panel analyses

- Verify barcode layout, extraction, molecular-family formation, target
  intervals, consensus method, duplex requirements, and error model.
- Distinguish raw reads, unique molecules, consensus reads, duplex-supported
  molecules, and callable molecular depth; they are not interchangeable.
- Low-frequency claims require actual molecular support and appropriate
  filtering, not only high raw coverage or a nominal allele fraction.

Research calls are not clinical diagnoses, pathogenicity classifications, or
treatment recommendations without a separately validated clinical workflow.
