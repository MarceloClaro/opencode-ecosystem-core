"""Downloads e composição de datasets por CLIs oficiais, sem shell (R668)."""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Callable
import zipfile

MAX_BYTES = 20_000_000
MAX_METADATA_BYTES = 2_000_000
MAX_ROWS = 50_000
PROVIDERS = {"huggingface": "hf", "kaggle": "kaggle"}
IRIS_REPOSITORIES = {("huggingface", "scikit-learn/iris"), ("kaggle", "uciml/iris")}
IRIS_SCHEMA = {
    "Id": "observation_id", "SepalLengthCm": "sepal_length_cm",
    "SepalWidthCm": "sepal_width_cm", "PetalLengthCm": "petal_length_cm",
    "PetalWidthCm": "petal_width_cm", "Species": "species",
}
FIELDNAMES = list(IRIS_SCHEMA.values())


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)


def _within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _filename(name: Any) -> str:
    if not isinstance(name, str) or not 1 <= len(name) <= 240 or not re.fullmatch(r"[A-Za-z0-9_. /-]+", name):
        raise ValueError("invalid_dataset_filename")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} or part.startswith("-") for part in path.parts) or name.startswith(("-", ".", "/")) or "\\" in name:
        raise ValueError("invalid_dataset_filename")
    if path.suffix.lower() not in {".csv", ".json", ".jsonl", ".tsv", ".txt", ".md", ".parquet"}:
        raise ValueError("unsupported_dataset_file_type")
    return name


def _csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


class _CliFailure(RuntimeError):
    pass


class DatasetCliIntegration:
    """Adaptador delimitado de dataset; não faz login, upload ou treino."""

    def __init__(self, root: str | Path | None = None, runner: Callable[..., Any] | None = None):
        self.root = Path(root or Path(__file__).resolve().parents[1]).resolve()
        self.runner = runner or subprocess.run

    def _executable(self, provider: str) -> Path | None:
        name = PROVIDERS[provider]
        candidates = [Path(sys.executable).parent / name, self.root / ".venv" / "bin" / name]
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
        return next((path.resolve() for path in candidates if path.is_file()), None)

    def status(self) -> dict[str, Any]:
        result = {}
        for provider, package in (("huggingface", "huggingface_hub"), ("kaggle", "kaggle")):
            executable = self._executable(provider)
            try:
                version = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                version = None
            credential_file = Path(os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface"))) / "token" if provider == "huggingface" else Path(os.environ.get("KAGGLE_CONFIG_DIR", str(Path.home() / ".kaggle"))) / "kaggle.json"
            configured = credential_file.is_file() or bool(os.environ.get("HF_TOKEN")) if provider == "huggingface" else credential_file.is_file() or bool(os.environ.get("KAGGLE_API_TOKEN")) or bool(os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"))
            result[provider] = {"installed": executable is not None, "executable": str(executable) if executable else None,
                                "version": version, "credentials_configured": configured,
                                "authentication_validated": False, "download_executed": False}
        return {"status": "ready" if all(item["installed"] for item in result.values()) else "degraded",
                "providers": result, "custom_domains": ["botanical_measurements"],
                "upload_supported": False, "training_executed": False}

    def _target(self, output_dir: str) -> Path:
        if not isinstance(output_dir, str) or not output_dir.strip():
            raise ValueError("output_dir_required")
        candidate = Path(output_dir)
        target = (candidate if candidate.is_absolute() else self.root / candidate).resolve()
        if not _within(target, self.root) or target == self.root:
            raise ValueError("output_outside_workspace")
        if target.exists():
            raise ValueError("output_directory_already_exists")
        return target

    def _run(self, argv: list[str], commands: list[dict[str, Any]]) -> str:
        try:
            process = self.runner(argv, capture_output=True, text=True, timeout=60, check=False, shell=False)
        except subprocess.TimeoutExpired as exc:
            commands.append({"argv": argv, "status": "timeout", "timeout_seconds": 60})
            raise _CliFailure("cli_timeout") from exc
        stdout, stderr = process.stdout or "", process.stderr or ""
        commands.append({"argv": argv, "exit_code": process.returncode,
                         "stdout_sha256": _digest(stdout.encode()), "stderr_sha256": _digest(stderr.encode())})
        if process.returncode != 0:
            diagnostic = (stdout + stderr).casefold()
            reason = "authentication_required" if any(term in diagnostic for term in ("unauthorized", "authenticate", "credentials", "token", "login", "401", "403")) else "cli_failed"
            raise _CliFailure(reason)
        if len(stdout.encode()) > MAX_METADATA_BYTES:
            raise _CliFailure("cli_output_exceeds_limit")
        return stdout

    @staticmethod
    def _read_file(path: Path, root: Path, limit: int = MAX_BYTES) -> bytes:
        resolved = path.resolve()
        if not _within(resolved, root.resolve()) or path.is_symlink() or not path.is_file():
            raise ValueError("source_file_missing_or_outside_root")
        with path.open("rb") as stream:
            raw = stream.read(limit + 1)
        if not raw or len(raw) > limit:
            raise ValueError("source_file_empty_or_exceeds_limit")
        return raw

    @staticmethod
    def _extract_requested(data_dir: Path, filename: str, max_bytes: int) -> None:
        target = data_dir / filename
        if target.exists():
            return
        for archive_path in data_dir.rglob("*.zip"):
            if archive_path.is_symlink() or not _within(archive_path.resolve(), data_dir.resolve()) or archive_path.stat().st_size > max_bytes:
                raise ValueError("unsafe_archive")
            with zipfile.ZipFile(archive_path) as archive:
                infos = archive.infolist()
                if len(infos) > 10 or sum(item.file_size for item in infos) > max_bytes:
                    raise ValueError("archive_exceeds_limit")
                for item in infos:
                    destination = (data_dir / item.filename).resolve()
                    if not _within(destination, data_dir.resolve()) or item.filename.startswith(("/", "\\")) or "\\" in item.filename or (item.external_attr >> 16) & 0o170000 == 0o120000:
                        raise ValueError("unsafe_archive_member")
                matches = [item for item in infos if item.filename == filename and not item.is_dir()]
                if matches:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(matches[0]) as stream:
                        raw = stream.read(max_bytes + 1)
                    if len(raw) > max_bytes:
                        raise ValueError("archive_member_exceeds_limit")
                    target.write_bytes(raw)
                    return

    def download(self, *, provider: str, dataset_id: str, filenames: list[str], output_dir: str,
                 revision: str | None = None, max_bytes: int = MAX_BYTES) -> dict[str, Any]:
        commands: list[dict[str, Any]] = []
        try:
            if provider not in PROVIDERS:
                raise ValueError("unsupported_dataset_provider")
            if not isinstance(dataset_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}/[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", dataset_id):
                raise ValueError("invalid_dataset_id")
            if not isinstance(filenames, list) or not 1 <= len(filenames) <= 5 or len(set(filenames)) != len(filenames):
                raise ValueError("one_to_five_unique_filenames_required")
            filenames = [_filename(filename) for filename in filenames]
            if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or not 1 <= max_bytes <= MAX_BYTES:
                raise ValueError("invalid_max_bytes")
            if revision is not None and (not isinstance(revision, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}", revision) or ".." in revision):
                raise ValueError("invalid_revision")
            if provider == "kaggle" and revision is not None and not re.fullmatch(r"[1-9][0-9]{0,8}", revision):
                raise ValueError("kaggle_revision_must_be_positive_version_number")
            output = self._target(output_dir)
            executable = self._executable(provider)
            if executable is None:
                raise _CliFailure("cli_not_installed")
            prefix = str(executable)
            output.mkdir(parents=True, exist_ok=False)
            metadata_dir, data_dir = output / "metadata", output / "data"
            metadata_dir.mkdir()
            data_dir.mkdir()
            if provider == "huggingface":
                info_args = [prefix, "datasets", "info", dataset_id, "--format", "json"]
                if revision:
                    info_args += ["--revision", revision]
                metadata = json.loads(self._run(info_args, commands))
                resolved_revision = metadata.get("sha")
                if not isinstance(resolved_revision, str) or not re.fullmatch(r"[a-f0-9]{40}", resolved_revision):
                    raise ValueError("hf_commit_revision_unresolved")
                listing = json.loads(self._run([prefix, "datasets", "ls", dataset_id, "-R", "--revision", resolved_revision, "--format", "json"], commands))
                licenses = [tag.removeprefix("license:") for tag in metadata.get("tags", []) if isinstance(tag, str) and tag.startswith("license:")]
                license_name = licenses[0] if len(licenses) == 1 else "unknown"
                source_url = f"https://huggingface.co/datasets/{dataset_id}/tree/{resolved_revision}"
                size_map = {item.get("path"): item.get("size") for item in listing if isinstance(item, dict)}
            else:
                identifier = dataset_id + (f"/{revision}" if revision else "")
                self._run([prefix, "datasets", "metadata", dataset_id, "--path", str(metadata_dir)], commands)
                metadata = json.loads(self._read_file(metadata_dir / "dataset-metadata.json", metadata_dir, MAX_METADATA_BYTES))
                details = metadata.get("info", metadata)
                listing = json.loads(self._run([prefix, "datasets", "files", identifier, "--format", "json", "--page-size", "200"], commands))
                licenses = [item.get("name") for item in details.get("licenses", []) if isinstance(item, dict)]
                license_name = licenses[0].casefold() if len(licenses) == 1 and isinstance(licenses[0], str) else "unknown"
                resolved_revision = revision or "unversioned_latest"
                source_url = f"https://www.kaggle.com/datasets/{dataset_id}" + (f"/versions/{revision}" if revision else "")
                size_map = {item.get("name"): item.get("size") for item in listing if isinstance(item, dict)}
            expected_sizes = {}
            for filename in filenames:
                size = size_map.get(filename)
                if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
                    raise ValueError("requested_file_missing_or_size_unknown")
                expected_sizes[filename] = size
            if sum(expected_sizes.values()) > max_bytes:
                raise ValueError("preflight_download_exceeds_limit")
            if provider == "kaggle" and revision:
                # O endpoint de arquivo da CLI 2.2.4 retorna 404 para Iris v1;
                # o ZIP versionado oficial preserva a versão. Nunca baixa o ZIP
                # inteiro sem limitar também todos os arquivos não solicitados.
                archive_sizes = list(size_map.values())
                if not 1 <= len(listing) <= 10 or len(size_map) != len(listing) or any(
                    isinstance(size, bool) or not isinstance(size, int) or size <= 0
                    for size in archive_sizes
                ) or sum(archive_sizes) > max_bytes:
                    raise ValueError("versioned_archive_preflight_exceeds_limit")
            (metadata_dir / "source-info.json").write_text(_json(metadata), encoding="utf-8")
            (metadata_dir / "source-files.json").write_text(_json(listing), encoding="utf-8")
            if provider == "huggingface":
                self._run([prefix, "download", dataset_id, *filenames, "--repo-type", "dataset", "--revision", resolved_revision,
                           "--local-dir", str(data_dir), "--max-workers", "1", "--force-download"], commands)
            elif revision:
                self._run([prefix, "datasets", "download", identifier, "--path", str(data_dir), "--quiet", "--force"], commands)
                for filename in filenames:
                    self._extract_requested(data_dir, filename, max_bytes)
            else:
                for filename in filenames:
                    self._run([prefix, "datasets", "download", identifier, "--file", filename, "--path", str(data_dir), "--quiet", "--force"], commands)
                    self._extract_requested(data_dir, filename, max_bytes)
            files = []
            for filename in filenames:
                path = data_dir / filename
                raw = self._read_file(path, data_dir, max_bytes)
                if len(raw) != expected_sizes[filename]:
                    raise ValueError("downloaded_file_size_mismatch")
                files.append({"name": filename, "path": str(path), "bytes": len(raw), "sha256": _digest(raw),
                              "source_url": source_url, "revision": resolved_revision, "license": license_name})
            manifest = {"status": "completed", "evidence_kind": "actual_cli_dataset_download", "download_executed": True,
                        "provider": provider, "dataset_id": dataset_id, "revision": resolved_revision,
                        "version_pinned": resolved_revision != "unversioned_latest", "license": license_name,
                        "source_url": source_url, "files": files, "commands": commands,
                        "metadata_sha256": _digest(_json(metadata).encode()),
                        "metadata_path": str(metadata_dir / "source-info.json"),
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "limitations": ["A licença é declarada nos metadados da plataforma; metadados Kaggle descrevem a licença corrente.",
                                        "O download e os hashes não são certificação independente da autenticidade da coleta original."],
                        "training_executed": False, "upload_executed": False}
            manifest_path = output / "download-manifest.json"
            manifest_path.write_text(_json(manifest), encoding="utf-8")
            return {**manifest, "manifest_path": str(manifest_path), "manifest_sha256": _digest(manifest_path.read_bytes())}
        except (ValueError, TypeError, OSError, _CliFailure, zipfile.BadZipFile) as exc:
            return {"status": "blocked", "reason": str(exc) if isinstance(exc, (ValueError, _CliFailure)) else type(exc).__name__,
                    "download_executed": False, "provider": provider, "commands": commands,
                    "training_executed": False, "upload_executed": False}

    def build_custom(self, *, source_manifests: list[str], output_dir: str,
                     name: str = "iris-core-personalizado", domain: str = "botanical_measurements", seed: int = 668) -> dict[str, Any]:
        try:
            if domain != "botanical_measurements":
                raise ValueError("unsupported_custom_domain_no_implicit_semantic_merge")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", name):
                raise ValueError("invalid_dataset_name")
            if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed <= 2**32 - 1:
                raise ValueError("invalid_split_seed")
            if not isinstance(source_manifests, list) or not 1 <= len(source_manifests) <= 5:
                raise ValueError("one_to_five_source_manifests_required")
            output = self._target(output_dir)
            sources, observations = [], {}
            mirrored = 0
            for manifest_name in source_manifests:
                if not isinstance(manifest_name, str):
                    raise ValueError("invalid_source_manifest_path")
                manifest_path = Path(manifest_name)
                if not manifest_path.is_absolute():
                    manifest_path = self.root / manifest_path
                manifest_raw = self._read_file(manifest_path, self.root, MAX_METADATA_BYTES)
                manifest = json.loads(manifest_raw)
                if manifest.get("status") != "completed" or manifest.get("download_executed") is not True or manifest.get("evidence_kind") != "actual_cli_dataset_download":
                    raise ValueError("source_manifest_does_not_document_completed_download")
                if (manifest.get("provider"), manifest.get("dataset_id")) not in IRIS_REPOSITORIES:
                    raise ValueError("unknown_source_semantics_iris_adapter_only")
                if manifest.get("license", "").casefold() != "cc0-1.0":
                    raise ValueError("license_not_supported_for_this_composition")
                source = {"provider": manifest["provider"], "dataset_id": manifest["dataset_id"],
                          "revision": manifest["revision"], "source_url": manifest["source_url"],
                          "license": manifest["license"], "manifest_sha256": _digest(manifest_raw)}
                sources.append(source)
                csv_files = [item for item in manifest.get("files", []) if item.get("name") == "Iris.csv"]
                if len(csv_files) != 1:
                    raise ValueError("iris_csv_required")
                original = csv_files[0]
                raw = self._read_file(Path(original["path"]), manifest_path.parent, MAX_BYTES)
                if _digest(raw) != original["sha256"]:
                    raise ValueError("source_dataset_hash_mismatch")
                reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
                if reader.fieldnames != list(IRIS_SCHEMA):
                    raise ValueError("iris_schema_or_units_do_not_match")
                for row in reader:
                    if None in row or any(value is None for value in row.values()):
                        raise ValueError("invalid_iris_csv_row")
                    identifier = row["Id"]
                    if not re.fullmatch(r"[1-9][0-9]{0,8}", identifier):
                        raise ValueError("invalid_iris_observation_id")
                    normalized = {"observation_id": identifier}
                    for column, target in IRIS_SCHEMA.items():
                        if column in {"Id", "Species"}:
                            continue
                        value = float(row[column])
                        if not math.isfinite(value) or not 0 < value <= 100:
                            raise ValueError("invalid_iris_measurement_cm")
                        normalized[target] = format(value, ".12g")
                    species = row["Species"].removeprefix("Iris-")
                    if species not in {"setosa", "versicolor", "virginica"}:
                        raise ValueError("unknown_iris_species")
                    normalized["species"] = species
                    fingerprint = _digest(_json({key: value for key, value in normalized.items() if key != "observation_id"}).encode())
                    lineage = {**source, "source_file_sha256": original["sha256"], "source_row_id": identifier}
                    if identifier in observations:
                        if observations[identifier]["row"] != normalized:
                            raise ValueError("conflicting_mirror_observation_values")
                        observations[identifier]["sources"].append(lineage)
                        mirrored += 1
                    else:
                        observations[identifier] = {"row": normalized, "group_hash": fingerprint, "sources": [lineage]}
                    if len(observations) > MAX_ROWS:
                        raise ValueError("custom_dataset_exceeds_row_limit")
            if len(observations) < 10:
                raise ValueError("insufficient_observations_for_three_splits")
            groups = {}
            for identifier, observation in observations.items():
                groups.setdefault(observation["group_hash"], []).append(identifier)
            # Estratifica por espécie, preservando grupos idênticos no mesmo conjunto.
            assignments = {}
            for species in ("setosa", "versicolor", "virginica"):
                selected = [group for group, identifiers in groups.items() if observations[identifiers[0]]["row"]["species"] == species]
                selected.sort(key=lambda group: _digest(f"{seed}:{group}".encode()))
                if len(selected) < 3:
                    raise ValueError("each_species_requires_three_distinct_observation_groups")
                train_end = min(len(selected) - 2, max(1, round(len(selected) * 0.70)))
                validation_end = min(len(selected) - 1, max(train_end + 1, round(len(selected) * 0.85)))
                for index, group in enumerate(selected):
                    split = "train" if index < train_end else "validation" if index < validation_end else "test"
                    assignments[group] = split
            split_rows = {split: [] for split in ("train", "validation", "test")}
            lineage_records = []
            all_rows = []
            for identifier, observation in sorted(observations.items(), key=lambda item: int(item[0])):
                split = assignments[observation["group_hash"]]
                all_rows.append(observation["row"])
                split_rows[split].append(observation["row"])
                lineage_records.append({"observation_id": identifier, "source_row_id": identifier,
                                        "group_hash": observation["group_hash"], "split": split, "sources": observation["sources"]})
            output.mkdir(parents=True, exist_ok=False)
            artifacts = {}
            for label, filename, raw in [("dataset", "dataset.csv", _csv_bytes(all_rows)),
                                          *[(split, f"{split}.csv", _csv_bytes(rows)) for split, rows in split_rows.items()],
                                          ("lineage", "lineage.json", _json(lineage_records).encode())]:
                path = output / filename
                path.write_bytes(raw)
                artifacts[label] = {"path": str(path), "sha256": _digest(raw), "bytes": len(raw)}
            card = f"""# {name}

Dataset local de medidas botânicas Iris em centímetros e três espécies.
Licença informada nas fontes: CC0-1.0. Observações: {len(all_rows)}.
Fontes baixadas por CLI: {len(sources)}; linhas de espelhos reunidas: {mirrored}.
Não adiciona observações sintéticas e não combina populações de domínios distintos.
Normalização: nomes de colunas e rótulos; nenhuma alteração numérica das medidas.
Splits estratificados por espécie, com grupos de medidas idênticas preservados.
Semente: {seed}. As proporções aproximadas são 70/15/15, com contagens reais no manifesto.
Limitações: dataset histórico pequeno; espécies/populações influenciam associações
agregadas; não sustenta inferência causal, aplicação clínica ou generalização universal.
Não houve publicação, upload, treino nem revisão humana por pares.
"""
            card_path = output / "README.md"
            card_path.write_text(card, encoding="utf-8")
            artifacts["card"] = {"path": str(card_path), "sha256": _digest(card.encode()), "bytes": len(card.encode())}
            manifest = {"status": "completed", "name": name, "domain": domain, "rows": len(all_rows),
                        "evidence_kind": "derived_real_observations", "synthetic": False,
                        "license": "cc0-1.0", "sources": sources, "schema": FIELDNAMES,
                        "units": {column: "cm" for column in FIELDNAMES if column.endswith("_cm")},
                        "seed": seed, "splits": {split: len(rows) for split, rows in split_rows.items()},
                        "split_integrity": {"overlap_groups": 0, "overlap_observation_ids": 0,
                                            "assignment": "stratified_by_species_and_grouped_by_identical_measurements"},
                        "mirrored_rows_merged": mirrored, "artifacts": artifacts,
                        "transformations": ["rename_iris_columns_with_centimeter_units", "normalize_species_labels",
                                            "align_mirrors_by_original_id_and_reject_conflicts", "preserve_duplicate_measurement_groups_in_same_split"],
                        "training_executed": False, "upload_executed": False, "external_validation": False,
                        "generated_at": datetime.now(timezone.utc).isoformat()}
            manifest_path = output / "custom-manifest.json"
            manifest_path.write_text(_json(manifest), encoding="utf-8")
            return {**manifest, "manifest_path": str(manifest_path), "manifest_sha256": _digest(manifest_path.read_bytes())}
        except (ValueError, TypeError, KeyError, OSError, UnicodeError) as exc:
            return {"status": "blocked", "reason": str(exc) if isinstance(exc, ValueError) else type(exc).__name__,
                    "training_executed": False, "upload_executed": False}
