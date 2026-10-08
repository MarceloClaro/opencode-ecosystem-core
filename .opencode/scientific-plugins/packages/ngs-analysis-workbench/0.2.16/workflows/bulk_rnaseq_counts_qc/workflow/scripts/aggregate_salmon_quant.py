#!/usr/bin/env python3
"""Aggregate Salmon quant.sf files into transcript- and gene-level matrices."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path

MIN_TX2GENE_COVERAGE = 0.95


def parse_gtf_attributes(raw: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for chunk in raw.strip().split(";"):
        part = chunk.strip()
        if not part or " " not in part:
            continue
        key, value = part.split(" ", 1)
        values[key] = value.strip().strip('"')
    return values


def tx2gene_from_gtf(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    mapping: dict[str, dict[str, str]] = {}
    opener = gzip.open if path.name.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9 or fields[2] not in {"transcript", "exon"}:
                continue
            attrs = parse_gtf_attributes(fields[8])
            transcript_id = attrs.get("transcript_id")
            gene_id = attrs.get("gene_id")
            if not transcript_id or not gene_id:
                continue
            gene_name = attrs.get("gene_name")
            if transcript_id not in mapping or gene_name is not None:
                mapping[transcript_id] = {
                    "gene_id": gene_id,
                    "gene_name": gene_name or gene_id,
                }
    return mapping


def canonical_transcript_id(transcript_id: str) -> str:
    """Return the stable transcript identifier used to join Salmon and GTF records."""
    primary_id = transcript_id.strip().split("|", 1)[0]
    unversioned_id, separator, version = primary_id.rpartition(".")
    if separator and unversioned_id and version.isdigit():
        return unversioned_id
    return primary_id


def resolve_tx2gene(
    transcript_ids: list[str], tx2gene: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """Resolve quant transcript IDs exactly, then by an unambiguous canonical ID."""
    canonical_lookup: dict[str, dict[str, str]] = {}
    ambiguous_ids: set[str] = set()
    for transcript_id, gene_record in tx2gene.items():
        canonical_id = canonical_transcript_id(transcript_id)
        existing_record = canonical_lookup.get(canonical_id)
        if existing_record and existing_record["gene_id"] != gene_record["gene_id"]:
            ambiguous_ids.add(canonical_id)
            canonical_lookup.pop(canonical_id, None)
        elif canonical_id not in ambiguous_ids:
            canonical_lookup[canonical_id] = gene_record

    resolved: dict[str, dict[str, str]] = {}
    for transcript_id in transcript_ids:
        gene_record = tx2gene.get(transcript_id)
        if gene_record is None:
            gene_record = canonical_lookup.get(canonical_transcript_id(transcript_id))
        if gene_record is not None:
            resolved[transcript_id] = gene_record
    return resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--quant", action="append", default=[], help="sample=/path/to/quant.sf")
    return parser.parse_args()


def read_quant_sf(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return {row["Name"]: row for row in reader}


def write_matrix(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    sample_to_quant: dict[str, Path] = {}
    for item in args.quant:
        sample, raw_path = item.split("=", 1)
        sample_to_quant[sample] = Path(raw_path)

    sample_names = sorted(sample_to_quant)
    per_sample = {sample: read_quant_sf(path) for sample, path in sample_to_quant.items()}
    transcript_ids = sorted({tx for table in per_sample.values() for tx in table})
    gtf_path = (
        Path(config["references"]["annotation_gtf"])
        if config.get("references", {}).get("annotation_gtf")
        else None
    )
    tx2gene = tx2gene_from_gtf(gtf_path)
    resolved_tx2gene = resolve_tx2gene(transcript_ids, tx2gene)

    tpm_rows: list[list[str]] = []
    num_reads_rows: list[list[str]] = []
    effective_length_rows: list[list[str]] = []
    for transcript_id in transcript_ids:
        tpm_row = [transcript_id]
        num_reads_row = [transcript_id]
        effective_length_row = [transcript_id]
        for sample in sample_names:
            record = per_sample[sample].get(transcript_id)
            tpm_row.append(record["TPM"] if record else "")
            num_reads_row.append(record["NumReads"] if record else "")
            effective_length_row.append(record["EffectiveLength"] if record else "")
        tpm_rows.append(tpm_row)
        num_reads_rows.append(num_reads_row)
        effective_length_rows.append(effective_length_row)

    write_matrix(outdir / "tpm.tsv", ["transcript_id", *sample_names], tpm_rows)
    write_matrix(outdir / "num_reads.tsv", ["transcript_id", *sample_names], num_reads_rows)
    write_matrix(
        outdir / "effective_length.tsv", ["transcript_id", *sample_names], effective_length_rows
    )

    mapped_transcripts = [
        transcript_id for transcript_id in transcript_ids if transcript_id in resolved_tx2gene
    ]
    unmapped_transcripts = [
        transcript_id for transcript_id in transcript_ids if transcript_id not in resolved_tx2gene
    ]
    transcript_coverage = len(mapped_transcripts) / len(transcript_ids) if transcript_ids else 0.0
    per_sample_read_coverage: dict[str, float | None] = {}
    for sample in sample_names:
        total_reads = sum(float(record["NumReads"]) for record in per_sample[sample].values())
        mapped_reads = sum(
            float(per_sample[sample][transcript_id]["NumReads"])
            for transcript_id in mapped_transcripts
            if transcript_id in per_sample[sample]
        )
        per_sample_read_coverage[sample] = mapped_reads / total_reads if total_reads > 0 else None
    available_read_coverage = [
        coverage for coverage in per_sample_read_coverage.values() if coverage is not None
    ]
    minimum_read_coverage = min(available_read_coverage, default=None)
    gene_outputs_eligible = bool(tx2gene) and (
        transcript_coverage >= MIN_TX2GENE_COVERAGE
        and (minimum_read_coverage is None or minimum_read_coverage >= MIN_TX2GENE_COVERAGE)
    )
    coverage = {
        "threshold": MIN_TX2GENE_COVERAGE,
        "total_transcripts": len(transcript_ids),
        "mapped_transcripts": len(mapped_transcripts),
        "unmapped_transcripts": len(unmapped_transcripts),
        "transcript_coverage_fraction": transcript_coverage,
        "per_sample_num_reads_coverage_fraction": per_sample_read_coverage,
        "minimum_num_reads_coverage_fraction": minimum_read_coverage,
        "gene_level_artifacts_created": gene_outputs_eligible,
        "unmapped_transcript_preview": unmapped_transcripts[:50],
    }
    (outdir / "tx2gene_coverage.json").write_text(
        json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not gene_outputs_eligible:
        for filename in ("tx2gene.tsv", "gene_num_reads.tsv", "gene_tpm.tsv"):
            (outdir / filename).unlink(missing_ok=True)

    tx2gene_rows: list[list[str]] = []
    gene_num_reads: dict[str, list[float]] = {}
    gene_tpm: dict[str, list[float]] = {}
    for transcript_id in mapped_transcripts:
        gene_record = resolved_tx2gene[transcript_id]
        gene_id = gene_record["gene_id"]
        gene_name = gene_record["gene_name"]
        tx2gene_rows.append([transcript_id, gene_id, gene_name])
        gene_num_reads.setdefault(gene_id, [0.0] * len(sample_names))
        gene_tpm.setdefault(gene_id, [0.0] * len(sample_names))
        for idx, sample in enumerate(sample_names):
            record = per_sample[sample].get(transcript_id)
            if not record:
                continue
            gene_num_reads[gene_id][idx] += float(record["NumReads"])
            gene_tpm[gene_id][idx] += float(record["TPM"])

    if gene_outputs_eligible:
        write_matrix(
            outdir / "tx2gene.tsv", ["transcript_id", "gene_id", "gene_name"], tx2gene_rows
        )
        write_matrix(
            outdir / "gene_num_reads.tsv",
            ["gene_id", *sample_names],
            [
                [gene_id, *[f"{value:.6f}" for value in gene_num_reads[gene_id]]]
                for gene_id in sorted(gene_num_reads)
            ],
        )
        write_matrix(
            outdir / "gene_tpm.tsv",
            ["gene_id", *sample_names],
            [
                [gene_id, *[f"{value:.6f}" for value in gene_tpm[gene_id]]]
                for gene_id in sorted(gene_tpm)
            ],
        )

    configured_samples = config.get("rnaseq_salmon_samples") or config.get("samples", {})
    sample_rows = []
    for sample in sample_names:
        info = configured_samples[sample]
        r1 = info.get("r1", [])
        r2 = info.get("r2", [])
        r1 = [r1] if isinstance(r1, str) else r1
        r2 = [r2] if isinstance(r2, str) else r2
        sample_rows.append(
            [
                sample,
                info.get("layout", "PE" if r2 else "SE"),
                info.get("strandedness", "unknown"),
                info.get("salmon_libtype", ""),
                info.get("salmon_libtype_source", ""),
                ",".join(str(index) for index in info.get("row_indices", [])),
                str(len(r1)),
                str(len(r2)),
            ]
        )
    write_matrix(
        outdir / "samples.tsv",
        [
            "sample",
            "layout",
            "strandedness",
            "salmon_libtype",
            "salmon_libtype_source",
            "technical_replicate_rows",
            "fastq_1_files",
            "fastq_2_files",
        ],
        sample_rows,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
