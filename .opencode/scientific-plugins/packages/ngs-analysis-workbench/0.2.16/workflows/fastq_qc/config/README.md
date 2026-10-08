# Configuration

The package includes `config.json`, a runnable paired-read public example. URL
inputs are downloaded only when their Snakemake rules require them. Local sample
paths bypass those rules. No input data is included in the package.

The Workbench uses this JSON config by default; supply an explicit JSON config to
override it. Native Snakemake may also accept
YAML, but the current MCP resolver reports non-JSON configs as `unknown` rather
than guessing. The config contains:

- `samples`: sample names mapped to `r1` and optional `r2` FASTQ paths.
- `threads`: default threads per rule.
- `trim_mode`: `none`, `fastp`, or `cutadapt`.
- `adapter_r1`: required when Cutadapt is selected.
- `adapter_r2`: additionally required for paired-end Cutadapt samples.
- `commands`: optional executable overrides for FastQC, MultiQC, fastp, and
  Cutadapt.

From the workflow package root, pass the packaged configuration explicitly:

```bash
snakemake --snakefile workflow/Snakefile --configfile config/config.json --cores 4
```

When running Snakemake directly, pass the desired configuration explicitly.
Input and executable paths should be absolute when launched from a workbench run
directory.

The workflow does not select a software deployment method automatically. The
runtime may select the pinned FastQC, MultiQC, fastp, and Cutadapt environment
in `workflow/envs/fastq_qc.yaml` when Conda is available. Otherwise, executable
rules use the commands available in the selected execution environment.
