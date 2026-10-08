# Configuration

The package includes `config.json`, a runnable public bulk RNA-seq example. URL
reads and references are downloaded only when the workflow requires them. Local
paths bypass downloading. No input data is included in the package.

The Workbench uses this JSON config by default; supply an explicit JSON config to
override it. Native Snakemake may also accept
YAML, but the current MCP resolver reports non-JSON configs as `unknown` rather
than guessing. The config contains:

- `samples`: sample names mapped to `r1`, optional `r2`, `strandedness`, and
  `salmon_libtype`. Read paths may be strings or lists of technical replicates.
- `references.transcriptome_fasta`: transcript FASTA used to build the Salmon
  index.
- `references.annotation_gtf`: optional plain or gzip-compressed GTF used for
  transcript-to-gene aggregation; configured annotations must exist. Gene-level
  matrices are emitted only when the reported coverage threshold is met.
- `threads`: default threads per rule.
- `salmon.kmer`: optional Salmon index k-mer size; defaults to 31.
- `salmon.decoys`: optional decoy-name list for an already decoy-aware
  transcriptome FASTA.
- `commands`: optional absolute executable overrides for `fastqc`, `multiqc`,
  `salmon`, and `python`. The MCP binding, not this config, selects Snakemake.

From the workflow package root, pass the packaged configuration explicitly:

```bash
snakemake --snakefile workflow/Snakefile --configfile config/config.json --cores 4
```

When running Snakemake directly, pass the desired configuration explicitly.
Input and executable paths should be absolute when launched from a workbench run
directory. Use Salmon library type `A` when the workflow should infer the
format, or supply an explicit type such as `ISR` only after the library design
has been reviewed.

The workflow does not select a software deployment method automatically. The
runtime may select the pinned FastQC, MultiQC, Salmon, and Python environment in
`workflow/envs/salmon.yaml` when Conda is available. Otherwise, executable rules
use the commands available in the selected execution environment.
