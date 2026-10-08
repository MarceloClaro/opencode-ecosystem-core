# Configuration

The package includes `config.json`, a runnable public single-cell example. URL
reads and references are downloaded only when the workflow requires them. Local
paths bypass downloading. No input data is included in the package.

The Workbench uses this JSON config by default; supply an explicit JSON config to
override it. Native Snakemake may also accept
YAML, but the current MCP resolver reports non-JSON configs as `unknown` rather
than guessing. The config contains:

- `samples`: sample names mapped to barcode and cDNA FASTQ paths.
- `threads`: default threads per rule.
- `references`: genome FASTA, annotation GTF, and barcode whitelist paths.
- `chemistry`: STARsolo barcode, UMI, filtering, and feature settings.
- `chemistry.genome_sa_index_nbases`: STAR index sizing; the packaged
  chromosome-19 example uses 11, while configurations that omit the setting use
  STAR's whole-genome default of 14.
- `chemistry.features_mode`: one supported gene-counting mode; raw matrices
  and, when cell filtering is enabled, filtered matrices use that same mode.
- `execution.star_image`: the reviewed STAR image used when Snakemake deploys
  rules through Apptainer; Conda execution does not require an image.

From the workflow package root, pass the packaged configuration explicitly:

```bash
snakemake --snakefile workflow/Snakefile --configfile config/config.json --cores 4
```

The workflow does not select a software deployment method automatically. The
runtime may select the pinned `workflow/envs/star.yaml` environment for both
STAR rules when Conda is available. Use the packaged container profile or an
explicit deployment flag to select Apptainer instead:

```bash
snakemake --snakefile workflow/Snakefile --configfile config/config.json --cores 4 --workflow-profile container
snakemake --snakefile workflow/Snakefile --configfile config/config.json --cores 4 --sdm apptainer
```

When running Snakemake directly, pass the desired configuration explicitly. Input paths
should be absolute when launched from a workbench run directory. The container
image uses the standard `docker://` image format but runs through Apptainer, not
a custom Docker invocation. The Workbench does not select Conda implicitly; the
container profile can be selected when running Snakemake directly.
