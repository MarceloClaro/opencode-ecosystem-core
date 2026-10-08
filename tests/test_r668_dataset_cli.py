"""R668: transporte CLI artificial testa contratos; o probe real é separado."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

import pytest

from integrations.dataset_cli import DatasetCliIntegration


CSV = "Id,SepalLengthCm,SepalWidthCm,PetalLengthCm,PetalWidthCm,Species\n" + "".join(
    f"{i},{4+i/10},3.0,{1+i/10},0.2,Iris-{['setosa','versicolor','virginica'][(i-1)//10]}\n"
    for i in range(1, 31)
)
REVISION = "a" * 40


@pytest.fixture
def cli(tmp_path, monkeypatch):
    calls = []
    def runner(argv, **kwargs):
        calls.append((argv, kwargs))
        assert kwargs.get("shell", False) is False
        assert isinstance(kwargs["timeout"], (int, float))
        if argv[1:3] == ["datasets", "info"]:
            stdout = json.dumps({"id": "scikit-learn/iris", "sha": REVISION,
                                 "tags": ["license:cc0-1.0"], "private": False, "gated": False})
        elif argv[1:3] == ["datasets", "ls"]:
            stdout = json.dumps([{"path": "Iris.csv", "size": len(CSV.encode())}])
        elif argv[1] == "download":
            destination = Path(argv[argv.index("--local-dir") + 1])
            destination.mkdir(exist_ok=True)
            (destination / "Iris.csv").write_text(CSV)
            stdout = str(destination / "Iris.csv")
        else:
            stdout = "test cli"
        return subprocess.CompletedProcess(argv, 0, stdout, "")
    integration = DatasetCliIntegration(root=tmp_path, runner=runner)
    monkeypatch.setattr(integration, "_executable", lambda provider: Path("/trusted/hf" if provider == "huggingface" else "/trusted/kaggle"))
    integration._test_calls = calls
    return integration


def downloaded(cli, tmp_path, directory="download"):
    return cli.download(provider="huggingface", dataset_id="scikit-learn/iris", filenames=["Iris.csv"],
                        output_dir=str(tmp_path / directory))


def test_hf_download_pins_revision_and_hashes_actual_files(cli, tmp_path):
    result = downloaded(cli, tmp_path)
    assert result["status"] == "completed"
    assert result["download_executed"] is True
    assert result["revision"] == REVISION
    assert result["license"] == "cc0-1.0"
    assert result["files"][0]["sha256"] == hashlib.sha256(CSV.encode()).hexdigest()
    argv = [call[0] for call in cli._test_calls if call[0][1] == "download"][0]
    assert argv[argv.index("--revision") + 1] == REVISION
    assert "--repo-type" in argv and "dataset" in argv


@pytest.mark.parametrize("change", ["escape", "traversal", "shell", "provider", "size", "existing"])
def test_invalid_download_blocks_before_cli(cli, tmp_path, change):
    kwargs = dict(provider="huggingface", dataset_id="scikit-learn/iris", filenames=["Iris.csv"], output_dir=str(tmp_path / "download"))
    if change == "escape":
        kwargs["output_dir"] = str(tmp_path.parent / "outside-r668")
    elif change == "traversal":
        kwargs["filenames"] = ["../escape.csv"]
    elif change == "shell":
        kwargs["dataset_id"] = "scikit-learn/iris; secret"
    elif change == "provider":
        kwargs["provider"] = "bash"
    elif change == "size":
        kwargs["max_bytes"] = True
    else:
        Path(kwargs["output_dir"]).mkdir()
    result = cli.download(**kwargs)
    assert result["status"] == "blocked"
    assert not cli._test_calls


def test_preflight_size_limit_prevents_download(cli, tmp_path):
    result = cli.download(provider="huggingface", dataset_id="scikit-learn/iris", filenames=["Iris.csv"],
                          output_dir=str(tmp_path / "download"), max_bytes=10)
    assert result["status"] == "blocked"
    assert not any(call[0][1] == "download" for call in cli._test_calls)


def test_cli_auth_failure_does_not_expose_token(tmp_path, monkeypatch):
    def runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, "", "Unauthorized HF_TOKEN=highly-secret-value")
    cli = DatasetCliIntegration(root=tmp_path, runner=runner)
    monkeypatch.setattr(cli, "_executable", lambda _provider: Path("/trusted/kaggle"))
    result = cli.download(provider="kaggle", dataset_id="uciml/iris", filenames=["Iris.csv"], output_dir=str(tmp_path / "download"))
    assert result["status"] == "blocked"
    assert result["reason"] == "authentication_required"
    assert "highly-secret-value" not in json.dumps(result)


def test_cli_success_without_file_is_not_download(tmp_path, monkeypatch):
    def runner(argv, **kwargs):
        if argv[1:3] == ["datasets", "info"]:
            stdout = json.dumps({"id": "scikit-learn/iris", "sha": REVISION, "tags": ["license:cc0-1.0"]})
        elif argv[1:3] == ["datasets", "ls"]:
            stdout = json.dumps([{"path": "Iris.csv", "size": len(CSV)}])
        else:
            stdout = "claimed success without a file"
        return subprocess.CompletedProcess(argv, 0, stdout, "")
    cli = DatasetCliIntegration(root=tmp_path, runner=runner)
    monkeypatch.setattr(cli, "_executable", lambda _provider: Path("/trusted/hf"))
    result = downloaded(cli, tmp_path)
    assert result["status"] == "blocked"
    assert result["download_executed"] is False


def test_custom_dataset_retains_sources_and_prevents_group_leakage(cli, tmp_path):
    source = downloaded(cli, tmp_path)
    result = cli.build_custom(source_manifests=[source["manifest_path"]], output_dir=str(tmp_path / "custom"))
    assert result["status"] == "completed"
    assert result["rows"] == 30
    assert result["domain"] == "botanical_measurements"
    assert result["license"] == "cc0-1.0"
    assert result["training_executed"] is False
    assert result["split_integrity"]["overlap_groups"] == 0
    assert sum(result["splits"].values()) == 30
    assert set(result["splits"]) == {"train", "validation", "test"}
    observations = json.loads(Path(result["artifacts"]["lineage"]["path"]).read_text())
    assert all(row["source_row_id"] and row["sources"] for row in observations)


def test_mirrors_are_deduplicated_and_splits_reproducible(cli, tmp_path):
    one = downloaded(cli, tmp_path, "one")
    two = downloaded(cli, tmp_path, "two")
    combined = cli.build_custom(source_manifests=[one["manifest_path"], two["manifest_path"]], output_dir=str(tmp_path / "combined"))
    again = cli.build_custom(source_manifests=[one["manifest_path"]], output_dir=str(tmp_path / "again"))
    assert combined["rows"] == again["rows"] == 30
    assert combined["mirrored_rows_merged"] == 30
    for split in combined["splits"]:
        assert combined["artifacts"][split]["sha256"] == again["artifacts"][split]["sha256"]


def test_custom_rejects_modified_source(cli, tmp_path):
    source = downloaded(cli, tmp_path)
    Path(source["files"][0]["path"]).write_text(CSV.replace("4.1", "9.9"))
    result = cli.build_custom(source_manifests=[source["manifest_path"]], output_dir=str(tmp_path / "custom"))
    assert result["status"] == "blocked"
    assert not (tmp_path / "custom").exists()


def test_custom_rejects_unknown_semantics(cli, tmp_path):
    source = downloaded(cli, tmp_path)
    result = cli.build_custom(source_manifests=[source["manifest_path"]], output_dir=str(tmp_path / "custom"), domain="clinical_outcomes")
    assert result["status"] == "blocked"
    assert not (tmp_path / "custom").exists()


@pytest.mark.parametrize("oversized", [False, True])
def test_versioned_kaggle_uses_bounded_archive_not_broken_file_endpoint(tmp_path, monkeypatch, oversized):
    calls = []
    def runner(argv, **kwargs):
        calls.append(argv)
        stdout = ""
        if argv[1:3] == ["datasets", "metadata"]:
            folder = Path(argv[argv.index("--path") + 1])
            (folder / "dataset-metadata.json").write_text(json.dumps({"licenses": [{"name": "CC0-1.0"}]}))
        elif argv[1:3] == ["datasets", "files"]:
            stdout = json.dumps([{"name": "Iris.csv", "size": len(CSV.encode())},
                                 {"name": "other.csv", "size": 21_000_000 if oversized else 4}])
        elif "--file" in argv:
            return subprocess.CompletedProcess(argv, 1, "", "404 Not Found")
        else:
            folder = Path(argv[argv.index("--path") + 1])
            with zipfile.ZipFile(folder / "iris.zip", "w") as archive:
                archive.writestr("Iris.csv", CSV)
                archive.writestr("other.csv", "a,b\n")
        return subprocess.CompletedProcess(argv, 0, stdout, "")
    integration = DatasetCliIntegration(root=tmp_path, runner=runner)
    monkeypatch.setattr(integration, "_executable", lambda _provider: Path("/trusted/kaggle"))
    result = integration.download(provider="kaggle", dataset_id="uciml/iris", revision="1",
                                  filenames=["Iris.csv"], output_dir=str(tmp_path / "download"))
    downloads = [argv for argv in calls if argv[1:3] == ["datasets", "download"]]
    if oversized:
        assert result["reason"] == "versioned_archive_preflight_exceeds_limit"
        assert not downloads
    else:
        assert result["status"] == "completed"
        assert downloads[0][3] == "uciml/iris/1" and "--file" not in downloads[0]
        assert result["revision"] == "1" and result["version_pinned"] is True
        assert result["files"][0]["sha256"] == hashlib.sha256(CSV.encode()).hexdigest()
