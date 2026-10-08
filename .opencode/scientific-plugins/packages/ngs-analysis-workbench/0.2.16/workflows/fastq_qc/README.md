# Local FASTQ QC workflow

This workflow uses the Snakemake standardized repository layout. Its entrypoint
is `workflow/Snakefile`, its editable default configuration is
`config/config.json`, and its pinned software environment is
`workflow/envs/fastq_qc.yaml`. The packaged default downloads a small public
paired-read dataset when no project-specific configuration is supplied:

```bash
snakemake --snakefile workflow/Snakefile --configfile config/config.json --cores 4
```

The workflow does not select a software deployment method automatically. The
runtime is responsible for selecting one that is available in the execution
environment. Supply another `--configfile` to use project-specific inputs
without modifying the package. The NGS Analysis Workbench automatically selects
the packaged default configuration unless an override is supplied. See
`config/README.md` for available options.
