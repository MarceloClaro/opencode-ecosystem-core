# Basic FASTQ QC guidance

Use this guidance for general raw-read quality assessment, FastQC or MultiQC
interpretation, pairing problems, and trimming decisions. When the reads come
from bulk or single-cell RNA-seq, combine it with the corresponding assay
reference rather than repeating assay-specific guidance here.

## What to inspect

- FASTQ paths, sample identity, pairing convention, and read roles
- whether reads are raw, demultiplexed, previously trimmed, or archive-derived
- whether the requested endpoint is interpretation, QC reports, or transformed reads
- known adapters or primers and any expected inline barcodes or UMIs
- downstream sensitivity to read length, clipping, pairing, and read-role changes

Use a standard FASTQ parser or workflow-native validation for record counts,
compression integrity, and read-name pairing. Filenames alone are not evidence
that mates or sample assignments are correct.

## Scientific guidance

Inspect raw-read QC before recommending transformation. Do not trim by default.

- A terminal quality drop may justify quality trimming, but preserve enough
  sequence for the downstream method.
- Adapter or primer signal requires identifying what the sequence represents
  before removal; use an explicit method when exact sequences matter.
- Treat poly-G, tile-specific failures, and severe quality shifts as possible
  run or platform issues rather than ordinary adapter contamination.
- Classify overrepresented sequences as adapters, primers, rRNA, PhiX, host
  contamination, or plausible biology before filtering them.
- Interpret duplication in assay context; high duplication may be expected for
  amplicons, targeted libraries, or low-input material.
- Do not trim or rewrite barcode, UMI, index, or protocol-specific read segments
  without applying the relevant assay guidance.

Never overwrite raw FASTQs. Preserve raw QC evidence even when producing a
derived FASTQ set.

## Evidence to carry forward

Carry forward the inspected sample/read inventory, raw-versus-derived state,
pairing evidence, important QC findings, any transformation and its rationale,
failed or questionable libraries, and downstream caveats. Ground conclusions
in generated reports rather than expected filenames alone.
