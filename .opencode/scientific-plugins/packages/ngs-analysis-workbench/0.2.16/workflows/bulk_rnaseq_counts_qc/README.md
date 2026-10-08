# Local bulk RNA-seq workflow

This Salmon workflow uses the Snakemake standardized repository layout. Its
entrypoint is `workflow/Snakefile`, its editable default configuration is
`config/config.json`, and its pinned software environment is
`workflow/envs/salmon.yaml`. The packaged default downloads a small public
sample and its compact references:

```bash
snakemake --snakefile workflow/Snakefile --configfile config/config.json --cores 4
```

The workflow does not select a software deployment method automatically. The
runtime is responsible for selecting one that is available in the execution
environment. Supply another `--configfile` to use project-specific inputs
without modifying the package. The NGS Analysis Workbench automatically selects
the packaged default configuration unless an override is supplied. See
`config/README.md` for sample, library, and reference options.

The workflow produces raw-read FastQC/MultiQC reports, per-sample Salmon
quantification, transcript matrices, and gene matrices when transcript-to-gene
coverage from the supplied GTF is sufficient. It is an intentionally compact
local execution option, not a parameter-for-parameter replacement for
`nf-core/rnaseq`.
