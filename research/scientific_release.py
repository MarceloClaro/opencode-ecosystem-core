"""R891: aceite computacional local; nunca executa programas do pacote recebido."""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .provenance_pipeline import (
    _REPRODUCER,
    _article,
    _https_url,
    _json,
    _retrieve_metadata,
    _validate_reference,
)
from .statistical_methods import MAX_CSV_BYTES, validate_configuration

_FILES = {"dataset": "dataset.csv", "configuration": "configuration.json", "analysis": "analysis.json",
          "methods_code": "statistical_methods.py", "reproduce_code": "reproduce.py",
          "references": "references.json", "reproduction": "reproduction.json",
          "computational_review": "computational-review.json", "rag_corpus": "rag-corpus.json",
          "rag_retrieval": "rag-query.json", "article": "article.md"}
_MAX_BYTES = 5_000_000
_MAX_TOTAL = 30_000_000
_REPLAY_RTOL = 1e-12
_REPLAY_ATOL = 1e-12
_WORKER = r'''import importlib.util, json, platform, resource, sys
from pathlib import Path
root = Path(sys.argv[1])
seconds = int(sys.argv[2])
resource.setrlimit(resource.RLIMIT_CPU, (seconds, seconds))
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
resource.setrlimit(resource.RLIMIT_FSIZE, (1000000, 1000000))
resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
try:
    specification = importlib.util.spec_from_file_location("trusted_core_methods", root / "trusted_methods.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    configuration = json.loads((root / "configuration.json").read_text())
    result = module.execute_analysis(root / "dataset.csv", configuration["method"], configuration["variables"])
    import scipy
    print(json.dumps({"status": "completed", "analysis": result,
          "runtime": {"python": platform.python_version(), "scipy": scipy.__version__}},
          allow_nan=False, sort_keys=True))
except Exception as exc:
    print(json.dumps({"status": "blocked", "error_type": type(exc).__name__}))
    sys.exit(2)
'''


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _equal(left: Any, right: Any) -> bool:
    return _json(left) == _json(right)


def _compare_replayed_analysis(actual: Any, expected: Any) -> tuple[bool, float]:
    """Tolera arredondamento só no replay; estrutura e parâmetros são exatos."""
    maximum_difference = 0.0

    def compare(left: Any, right: Any, path: tuple = ()) -> bool:
        nonlocal maximum_difference
        if type(left) is not type(right):
            return False
        if isinstance(left, dict):
            if left.keys() != right.keys():
                return False
            return all([compare(left[key], right[key], path + (key,)) for key in left])
        if isinstance(left, list):
            if len(left) != len(right):
                return False
            return all([compare(a, b, path + (index,)) for index, (a, b) in enumerate(zip(left, right))])
        if type(left) is float:
            if not math.isfinite(left) or not math.isfinite(right):
                return False
            maximum_difference = max(maximum_difference, abs(left - right))
            if path and path[-1] == "alpha":
                return left == right  # Prespecificação, não estatística calculada.
            if path and path[-1] == "p_value" and not (0 <= left <= 1 and 0 <= right <= 1):
                return False
            return math.isclose(left, right, rel_tol=_REPLAY_RTOL, abs_tol=_REPLAY_ATOL)
        return left == right  # Inclui booleanos, inteiros/contagens/seeds e texto.

    matched = compare(actual, expected)
    return matched, maximum_difference


def _load(raw: bytes) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, "duplicate_json_key")
            result[key] = value
        return result

    def invalid(_value):
        raise ValueError("nonfinite_json_number")

    result = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    # Re-encoding also rejects overflow such as 1e999, not only NaN tokens.
    _json(result)
    return result


def validate_verify_config(config: dict) -> dict:
    """Valida a configuração, sem acessar ou executar o pacote."""
    _require(isinstance(config, dict) and set(config) <= {"package_dir", "timeout_seconds"}, "invalid_verify_config")
    directory = config.get("package_dir")
    timeout = config.get("timeout_seconds", 45)
    _require(isinstance(directory, str) and 0 < len(directory.strip()) <= 4096 and "\x00" not in directory,
             "invalid_package_dir")
    _require(type(timeout) is int and 1 <= timeout <= 60, "timeout_seconds_must_be_integer_1_to_60")
    return {"package_dir": directory, "timeout_seconds": timeout}


def _root_fd(directory: str) -> int:
    """Abre todos os componentes sem seguir links, inclusive ancestrais."""
    path = Path(os.path.abspath(directory))
    descriptor = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:]:
            following = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _read(descriptor: int, name: str, limit: int = _MAX_BYTES) -> bytes:
    handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
    try:
        before = os.fstat(handle)
        _require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= limit, "invalid_artifact_size_or_type")
        with os.fdopen(handle, "rb", closefd=False) as stream:
            raw = stream.read(limit + 1)
        after = os.fstat(handle)
        _require(len(raw) == before.st_size and before.st_mtime_ns == after.st_mtime_ns
                 and before.st_ctime_ns == after.st_ctime_ns, "artifact_changed_during_snapshot")
        return raw
    finally:
        os.close(handle)


def _artifact_name(declared: Any, expected: str) -> str:
    _require(isinstance(declared, str) and 0 < len(declared) <= 4096 and "\x00" not in declared,
             "invalid_artifact_path")
    posix, windows = PurePosixPath(declared), PureWindowsPath(declared)
    _require(".." not in posix.parts and ".." not in windows.parts, "artifact_path_traversal")
    absolute = posix.is_absolute() or windows.is_absolute()
    _require(absolute or declared == expected, "artifact_path_not_internal")
    name = windows.name if "\\" in declared else posix.name
    _require(name == expected, "ambiguous_or_wrong_artifact_basename")
    return expected  # Nunca abre o caminho original, mesmo quando ele é absoluto.


def _no_synthetic(value: Any, depth: int = 0) -> None:
    _require(depth <= 16, "metadata_nesting_limit")
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "synthetic":
                _require(item is False, "synthetic_or_invalid_evidence_flag")
            if key == "evidence_kind":
                _require(isinstance(item, str) and item.casefold() not in {"synthetic", "simulation", "demonstration"},
                         "ineligible_evidence_kind")
            if key == "evidence_eligible":
                _require(item is True, "ineligible_evidence_flag")
            _no_synthetic(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _no_synthetic(item, depth + 1)


def _flags(value: dict, expected: dict) -> None:
    _require(isinstance(value, dict), "invalid_receipt_schema")
    for key, flag in expected.items():
        _require(value.get(key) is flag, "invalid_execution_flag:" + key)


def _validate_documents(manifest: dict, documents: dict, raw: dict, trusted: bytes) -> dict:
    _require(manifest.get("status") == "completed" and manifest.get("evidence_kind") == "executed_local_analysis",
             "package_not_completed_local_analysis")
    _flags(manifest, {"experiment_executed": True, "external_validation": False, "model_inference_executed": False})
    _no_synthetic(manifest)
    for document in documents.values():
        _no_synthetic(document)
    config, analysis = documents["configuration"], documents["analysis"]
    _require(isinstance(config, dict) and set(config) == {"method", "variables", "dataset_sha256", "methods_sha256"},
             "invalid_analysis_configuration")
    validate_configuration(config["method"], config["variables"])
    _require(config["dataset_sha256"] == _digest(raw["dataset"]), "configuration_dataset_hash_mismatch")
    _require(config["methods_sha256"] == _digest(raw["methods_code"]) == _digest(trusted), "method_version_mismatch")
    _require(raw["reproduce_code"] == _REPRODUCER.encode(), "untrusted_exported_reproducer")
    _require(isinstance(analysis, dict) and _equal(analysis, manifest.get("analysis")), "manifest_analysis_mismatch")
    _flags(analysis, {"experiment_executed": True, "causal_inference": False})
    _require(analysis.get("method") == config["method"] and _equal(analysis.get("variables"), config["variables"]),
             "analysis_configuration_mismatch")
    reproduction, review = documents["reproduction"], documents["computational_review"]
    _flags(reproduction, {"process_executed": True, "matched": True})
    _require(type(reproduction.get("exit_code")) is int and reproduction["exit_code"] == 0,
             "reproduction_exit_not_zero")
    _require(reproduction.get("dataset_sha256") == config["dataset_sha256"]
             and reproduction.get("analysis_sha256") == _digest(_json(analysis).encode()), "reproduction_hash_mismatch")
    _flags(review, {"human_peer_review": False, "external_validation": False, "reproduction_matched": True,
                   "source_authenticity_independently_validated": False, "single_prespecified_method": True,
                   "finite_numeric_output": True, "causal_inference": False, "passed": True})
    _require(review.get("kind") == "computational_review" and _equal(review, manifest.get("computational_review"))
             and _equal(reproduction, manifest.get("reproduction")), "manifest_receipt_mismatch")
    provenance = manifest.get("provenance")
    _require(isinstance(provenance, dict), "missing_provenance")
    dataset = provenance.get("dataset")
    _require(isinstance(dataset, dict) and dataset.get("evidence_kind") == "real_observations"
             and dataset.get("source_authenticity") == "user_declared", "invalid_dataset_provenance")
    _https_url(dataset.get("source_url"), "dataset.source_url")
    _require(isinstance(dataset.get("title"), str) and 0 < len(dataset["title"].strip()) <= 2000,
             "invalid_dataset_title")
    _require(dataset.get("sha256") == config["dataset_sha256"] and type(dataset.get("snapshot_bytes")) is int
             and dataset["snapshot_bytes"] == len(raw["dataset"]), "dataset_provenance_hash_mismatch")
    sources = provenance.get("references")
    _require(isinstance(sources, list) and 1 <= len(sources) <= 5, "invalid_reference_provenance")
    online = [source for source in sources if isinstance(source, dict) and source.get("status") == "online"]
    source_keys = sorted(key for key in documents if key.startswith("reference_source_"))
    _require(len(online) == len(source_keys) > 0, "reference_snapshot_count_mismatch")
    records = {}
    for key, source in zip(source_keys, online):
        _https_url(source.get("source_url"), "reference.source_url")
        _require(source.get("sha256") == _digest(raw[key]) and source.get("evidence_kind") == "retrieved_http_metadata"
                 and source.get("source_mode") in {"provided_snapshot", "live_http"}
                 and source.get("source_authenticity") in {"user_declared", "captured_by_pipeline"}, "invalid_reference_source")
        snapshot = documents[key]
        _require(isinstance(snapshot, dict) and snapshot.get("status") == "online"
                 and snapshot.get("evidence_kind") == "retrieved_http_metadata", "invalid_reference_snapshot")
        items = snapshot.get("records")
        _require(isinstance(items, list) and 1 <= len(items) <= 20, "invalid_reference_records")
        for item in items:
            normalized = _validate_reference(item)
            records.setdefault(normalized.get("doi") or normalized["url"], normalized)
    references = list(records.values())[:20]
    _require(_equal(documents["references"], references), "references_snapshot_mismatch")
    corpus = [{"doc_id": f"reference-{index}", "title": item["title"], "source": item["url"],
               "text": item["title"] + "\n" + item["abstract"], "evidence_scope": "bibliographic_metadata",
               "year": item.get("year"), "sha256": _digest((item["title"] + "\n" + item["abstract"]).encode())}
              for index, item in enumerate(references, 1)]
    question = manifest.get("question")
    _require(isinstance(question, str) and 0 < len(question.strip()) <= 4000, "invalid_question")
    retrieval = _retrieve_metadata(question, corpus)
    _require(_equal(documents["rag_corpus"], corpus) and _equal(documents["rag_retrieval"], retrieval)
             and _equal(manifest.get("rag"), retrieval), "bibliographic_retrieval_mismatch")
    # R663 imprime as variáveis na ordem recebida, mas exporta JSON com chaves
    # ordenadas. A apresentação pode diferir nessa única linha após recarga.
    article_lines = raw["article"].decode("utf-8").splitlines(keepends=True)
    for index, line in enumerate(article_lines):
        if line.startswith("Colunas/grupos: "):
            displayed = _load(line.removeprefix("Colunas/grupos: ").rstrip().removesuffix(".").encode())
            _require(_equal(displayed, config["variables"]), "article_variables_mismatch")
            article_lines[index] = "Colunas/grupos: " + json.dumps(analysis["variables"], ensure_ascii=False) + ".\n"
    _require("".join(article_lines) == _article(question, dataset, analysis, references, reproduction),
             "article_template_or_content_mismatch")
    runtime = manifest.get("runtime")
    _require(isinstance(runtime, dict) and all(isinstance(runtime.get(key), str) and 0 < len(runtime[key]) < 100
                                             for key in ("python", "scipy")), "invalid_original_runtime")
    return config


def _replay(raw: dict, config: dict, trusted: bytes, seconds: float, receipt: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="core-r891-") as temporary:
        root = Path(temporary)
        (root / "dataset.csv").write_bytes(raw["dataset"])
        (root / "configuration.json").write_text(_json(config))
        (root / "trusted_methods.py").write_bytes(trusted)
        environment = {"PATH": os.defpath, "LANG": "C.UTF-8", "OPENBLAS_NUM_THREADS": "1",
                       "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}
        with (root / "stdout.json").open("wb") as output, (root / "stderr.log").open("wb") as errors:
            try:
                process = subprocess.run([sys.executable, "-I", "-c", _WORKER, temporary, str(max(1, int(seconds)))],
                    cwd=temporary, env=environment, stdin=subprocess.DEVNULL, stdout=output, stderr=errors,
                    timeout=seconds, check=False, start_new_session=True)
            except subprocess.TimeoutExpired:
                # subprocess.run só espera o prazo após criar o processo.
                receipt["process_executed"] = True
                raise
            receipt["process_executed"] = True
        _require(process.returncode == 0, "trusted_replay_process_failed")
        _require((root / "stdout.json").stat().st_size <= 1_000_000, "replay_output_limit")
        result = _load((root / "stdout.json").read_bytes())
        _require(isinstance(result, dict) and result.get("status") == "completed", "trusted_replay_failed")
        return result


def verify_scientific_package(*, package_dir: str, timeout_seconds: int = 45) -> dict:
    """Revalida bytes e cálculo; a origem científica permanece uma declaração."""
    started = time.monotonic()
    report = {"status": "blocked", "success": False, "local_computational_acceptance": False,
              "human_submission_acceptance": False, "human_review_status": "pending",
              "external_validation": False, "confidence_promoted": False,
              "evidence_scope": "local_package_bytes_and_trusted_core_replay",
              "verified_artifacts": {}, "replay": {"process_executed": False, "matched": False},
              "limitations": ["Hashes identificam conteúdo; não certificam origem ou verdade dos dados e referências.",
                              "Não avalia sustentação de citações, originalidade, causalidade ou revisão por pares.",
                              "Aceite humano para submissão e validação externa permanecem pendentes."]}
    descriptor = None
    try:
        config_input = validate_verify_config({"package_dir": package_dir, "timeout_seconds": timeout_seconds})
        descriptor = _root_fd(config_input["package_dir"])
        manifest_raw = _read(descriptor, "manifest.json", 2_000_000)
        manifest = _load(manifest_raw)
        _require(isinstance(manifest, dict), "invalid_manifest_schema")
        entries = manifest.get("artifacts")
        _require(isinstance(entries, dict) and 12 <= len(entries) <= 16, "invalid_artifact_manifest")
        expected = dict(_FILES)
        for key in entries:
            if re.fullmatch(r"reference_source_[1-5]", key):
                expected[key] = "reference-source-" + key.rsplit("_", 1)[1] + ".json"
        _require(set(entries) == set(expected), "missing_or_unknown_artifact_role")
        source_indexes = sorted(int(key.rsplit("_", 1)[1]) for key in entries if key.startswith("reference_source_"))
        _require(source_indexes == list(range(1, len(source_indexes) + 1)), "noncontiguous_reference_snapshots")
        raw, documents, total = {}, {}, len(manifest_raw)
        for role, name in expected.items():
            entry = entries[role]
            _require(isinstance(entry, dict) and set(entry) == {"path", "sha256", "bytes"}, "invalid_artifact_entry")
            _artifact_name(entry["path"], name)
            _require(isinstance(entry["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is not None,
                     "invalid_artifact_sha256")
            _require(type(entry["bytes"]) is int and 0 < entry["bytes"] <= _MAX_BYTES, "invalid_declared_artifact_bytes")
            data = _read(descriptor, name, MAX_CSV_BYTES if role == "dataset" else _MAX_BYTES)
            _require(_digest(data) == entry["sha256"] and len(data) == entry["bytes"], "artifact_hash_or_size_mismatch:" + role)
            total += len(data)
            _require(total <= _MAX_TOTAL, "package_size_limit")
            raw[role] = data
            if name.endswith(".json"):
                documents[role] = _load(data)
            report["verified_artifacts"][role] = {"name": name, "sha256": entry["sha256"], "bytes": len(data)}
        trusted = Path(__file__).with_name("statistical_methods.py").read_bytes()
        config = _validate_documents(manifest, documents, raw, trusted)
        remaining = timeout_seconds - (time.monotonic() - started)
        _require(remaining > 0, "verification_time_budget_exceeded")
        replayed = _replay(raw, config, trusted, remaining, report["replay"])
        matched, difference = _compare_replayed_analysis(replayed.get("analysis"), documents["analysis"])
        report["replay"].update(runtime=replayed.get("runtime"),
            max_abs_difference=difference if math.isfinite(difference) else None,
            numeric_difference_overflow=not math.isfinite(difference),
            numeric_tolerance={"rtol": _REPLAY_RTOL, "atol": _REPLAY_ATOL})
        _require(matched, "trusted_replay_analysis_mismatch")
        _require(_read(descriptor, "manifest.json", 2_000_000) == manifest_raw
                 and all(_read(descriptor, expected[role]) == data for role, data in raw.items()), "package_changed_during_verification")
        _require(time.monotonic() - started <= timeout_seconds, "verification_time_budget_exceeded")
        report["replay"].update(matched=True, method=config["method"], runtime=replayed.get("runtime"),
            analysis_sha256=_digest(_json(replayed["analysis"]).encode()), trusted_methods_sha256=_digest(trusted),
            package_code_executed=False, isolated_python=True, cpu_seconds_limit=max(1, int(remaining)),
            address_space_bytes_limit=2 * 1024**3)
        report.update(status="locally_verified", success=True, local_computational_acceptance=True,
                      manifest_sha256=_digest(manifest_raw), original_runtime=manifest["runtime"])
    except subprocess.TimeoutExpired:
        report["reason"] = "replay_timeout"
    except (ValueError, TypeError, OSError, OverflowError, KeyError, AttributeError, RecursionError) as exc:
        report["reason"] = str(exc)[:300] if isinstance(exc, ValueError) else type(exc).__name__
    finally:
        if descriptor is not None:
            os.close(descriptor)
    report["verification_runtime"] = {"python": platform.python_version()}
    report["report_sha256"] = _digest(_json(report).encode())
    return report
