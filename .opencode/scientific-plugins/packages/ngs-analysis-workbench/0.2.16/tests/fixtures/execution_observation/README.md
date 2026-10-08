# Recorded execution-observation fixtures

These fixtures were captured from completed Workbench runs on 2026-08-07 and
are retained as real parser inputs rather than constructed unit-test rows.

- `nextflow/workflow/trace.txt` came from
  `nfcore-fastq-qc-20260808-010703-d888c7ed`. Its original SHA-256 was
  `1b949485a35a825f55d904fdf1c624ec4233d325d8336c451d546ce2d3197e20`; the
  recorded file is byte-for-byte identical.
- `snakemake/results/.snakemake/log/2026-08-07T180851.803407.snakemake.log` came from
  `snakemake-fastq-qc-20260808-010555-1ce65ac4`. Its original SHA-256 was
  `25dbedfc5534623c898027c658ab813425afb64b9d6c446f2ec6a46941591df1`.
  Hostname, username, temporary-directory, environment, and workspace path
  prefixes were normalized; timestamps, workflow identifiers, rule records,
  job identifiers, wildcards, progress, and tool output are unchanged.
  The normalized fixture SHA-256 is
  `d95c965a54ab3de78e32ea86f60204db9095068dd27a587bb7b2192c7e157b71`.

The sibling `goldens/` files contain the complete engine-neutral observations
expected from these inputs. Tests normalize only the fixture-root portion of
`evidence.path` before comparing the full payload.
