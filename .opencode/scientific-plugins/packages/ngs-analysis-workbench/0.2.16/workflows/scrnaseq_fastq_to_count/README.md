# Local single-cell RNA-seq workflow

This STARsolo workflow uses the Snakemake standardized repository layout. Its
entrypoint is `workflow/Snakefile`, its editable default configuration is
`config/config.json`, and its pinned software environment is
`workflow/envs/star.yaml`. The packaged default downloads a public
10x sample, chromosome-19 references, and its barcode whitelist:

```bash
snakemake --snakefile workflow/Snakefile --configfile config/config.json --cores 4
```

The workflow does not select a software deployment method automatically. The
runtime is responsible for selecting one that is available in the execution
environment. Supply another `--configfile` to override the package defaults, or
use `--sdm apptainer` to select the reviewed STAR container image. Snakemake
executes Docker-format images through Apptainer; it does not invoke the Docker
daemon directly. The NGS Analysis Workbench automatically selects the packaged
default configuration unless an override is supplied. See `config/README.md`
for chemistry, reference, and deployment options.
