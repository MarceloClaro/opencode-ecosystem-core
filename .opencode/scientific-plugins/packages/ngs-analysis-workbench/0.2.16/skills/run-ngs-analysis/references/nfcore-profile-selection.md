# nf-core profile selection guidance

Use this reference after live workflow discovery selects a Nextflow workflow
from the nf-core collection.
The agent owns profile selection. MCP reports runtime observations, checks the
standard task environment named by the request, and preserves the supplied
profile in the reviewed plan.

Profiles are compositional Nextflow configuration, not assay stages. Do not
encode a fixed profile for FASTQ QC, bulk RNA-seq, single-cell RNA-seq, or a
particular nf-core pipeline in this guidance.

## Inspect before selecting

For the exact selected pipeline revision, inspect:

1. the pipeline's usage documentation and `nextflow.config` profile block
2. any configuration files included by candidate profiles
3. the input source, especially whether it is workflow-owned test data or user data
4. `get_runtime_environment`, including the container daemon's reported
   platform rather than only the host CPU

Do not assume a profile exists or retains the same effects across pipelines or
revisions. If its definition cannot be inspected, keep its effect unresolved
and explain that limitation before approval.

## Compose from independent concerns

Select components supported by the inspected pipeline revision:

- **Input fixture:** use `test` only when the run intentionally uses that
  profile's bundled data. Omit test-data profiles for user inputs.
- **Task software environment:** normally choose one applicable environment, such as `docker`, `podman`, `apptainer`, `singularity`, or `conda`, after the corresponding selected-target runtime is observed ready. Do not combine competing environments without inspecting their effective merged configuration.
- **Platform or portability:** consider components such as `arm64`,
  `emulate_amd64`, `wave`, or `gpu` only when the exact revision declares them
  and the observed runtime and intended execution require them. Inspect any
  included configuration, use the container daemon platform rather than only
  the host CPU, and disclose network resolution, emulation, or other material
  side effects.
- **Site or executor configuration:** use institutional or executor profiles
  only for a selected compute target whose configuration is available. A local
  runtime observation does not establish remote readiness.

Preserve the complete ordered profile string because component order can affect
the merged Nextflow configuration. Show the selected revision, profile,
supporting runtime facts, upstream source provenance, and material side effects
before asking for execution approval.

A readiness warning for an uninterpreted additional component means the agent
must expose the upstream definition and rationale. It is not permission to
silently add, remove, or rewrite the component.
