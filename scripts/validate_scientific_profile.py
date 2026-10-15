#!/usr/bin/env python3
"""Executa somente o perfil científico enumerado, em processos seriais delimitados.

O recibo prova a execução local dos testes selecionados. Não mede a suíte global,
escala científica, autenticidade externa de dados ou mérito de manuscritos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import signal
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath

import psutil

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
# Execução direta da CLI exige o bootstrap da raiz antes do import interno.
from scripts.quality_report import load_junit_results  # noqa: E402

DEFAULT_GROUP_TIMEOUT = 180
DEFAULT_MAX_RSS_BYTES = 1536 * 1024 * 1024
PROFILE_GROUPS = (
    ("provenance_release", (
        "tests/test_r663_scientific_provenance.py",
        "tests/test_r891_scientific_release.py",
        "tests/test_r891_scientific_orchestration.py",
        "tests/test_r891_scientific_profile.py",
        "tests/test_r892_scientific_fail_closed.py",
    )),
    ("manuscripts", (
        "tests/test_r108_marceloclaro_scientific_fusion.py",
        "tests/test_r109_loop_engineering.py",
        "tests/test_r103_peer_review.py",
        "tests/test_r104d_agentic_revision.py",
        "tests/test_r105_paper_composer.py",
        "tests/test_r381_manuscript_rigor_gate_integration.py",
        "tests/test_scientific_lab_v41_core_integration.py",
        "tests/test_scientific_lab_v42_native.py",
        "tests/test_r706_manuscript_scale.py::test_config_valida_gera_slug_e_modulos",
        "tests/test_r706_manuscript_scale.py::test_config_rejeita_tipo_invalido",
        "tests/test_r706_manuscript_scale.py::test_config_rejeita_titulo_e_autores_vazios",
        "tests/test_r706_manuscript_scale.py::test_tipos_cobrem_cinco_modalidades",
        "tests/test_r706_manuscript_scale.py::test_scaffold_cria_workspace_isolado",
        "tests/test_r706_manuscript_scale.py::test_scaffold_nega_sobrescrita_sem_force",
        "tests/test_r706_manuscript_scale.py::test_parse_tabular_cabecalho_linhas_regras",
        "tests/test_r706_manuscript_scale.py::test_parse_bbl_duas_referencias_com_negrito",
        "tests/test_r706_manuscript_scale.py::test_citacoes_expandem_autor_data",
        "tests/test_r706_manuscript_scale.py::test_iter_blocos_reconhece_tipos",
        "tests/test_r706_manuscript_scale.py::test_gates_citacoes_indefinidas",
        "tests/test_r706_manuscript_scale.py::test_gates_diretorio_inexistente",
        "tests/test_r706_manuscript_scale.py::test_gates_forca_alegacao_sinaliza",
        "tests/test_r706_manuscript_scale.py::test_produzir_lote_isola_falhas",
        "tests/test_r706_manuscript_scale.py::test_docx_builder_generico",
    )),
    ("workflow_memory", (
        "tests/test_r644_workflow.py", "tests/test_r644_workflow_store.py",
        "tests/test_r825_execution_cancellation.py",
        "tests/test_r827_remaining_mcp_cancellation.py",
        "tests/test_r886_memory_reasoning.py", "tests/test_r886_metacognitive_loop.py",
        "tests/test_r893_whoosh_persistence.py",
    )),
    ("reasoning_integrity", (
        "tests/test_r818_restricted_math_engine.py", "tests/test_r821_z3_fail_closed.py",
        "tests/test_r888_imobench_integrity.py", "tests/test_r890_quantum_provenance.py",
        "tests/test_r815_scientific_lexical_screening.py",
    )),
    ("delivery_contracts", (
        "tests/test_r137_opencode_config_reproducible.py", "tests/test_r839_tdd_history.py",
        "tests/test_r839_red_delivery.py", "tests/test_r839_verifier_delivery.py",
    )),
)
PROFILE_EXCLUSIONS = {
    "tests/test_r706_manuscript_scale.py::test_pptx_theme_falha_fechada_sem_dependencia":
        "Guarda condicional faz skip quando python-pptx está instalado; não pertence ao perfil.",
    "other_tests": "Demais testes não enumerados, compiladores, GPU e cargas externas não executados.",
}
_EXCLUDED_COMPONENTS = frozenset({
    "docs", "reports", "report", "output", "outputs", "artigos", "vendor", "third_party",
    "third-party", "node_modules", ".venv", "venv", "__pycache__", ".git", ".backups",
    ".pytest_cache", ".ruff_cache", "build", "dist", ".mci_state", ".mci_cache",
})
_EXCLUDED_ROOTS = frozenset({
    "LiteRT-LM-main", "colibri", "biblioteca ai", "cache", "checkpoints", "data", "assets",
    "illustrations", "notebooks", "packages", "tmp", "sandbox", "publications",
    "producao_cientifica", "pesquisa-artigo-qualis-a1", "manuscrito_porescrito799_R522",
    "opencode-ecosystem-core", "odonto", "Medicina", "Nova pasta", "PLUGIN NOTA10", "PROJETO 1",
    "prestacao_contas_nota_dez", "contas-escolares-airam-veras", "auditoria_fichamentos",
    "regimento e ppp airam veras", "resultados_quantum_ia (1)", "implementar ideias",
    "llm-agent-quantization", "opencode_whoosh",
})
_SOURCE_SUFFIXES = frozenset({
    ".py", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".json", ".txt", ".md",
    ".sh", ".ps1", ".js", ".ts", ".tsx", ".jsx", ".sql", ".lean",
})
_THREAD_KEYS = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
# O recorder grava antes do teardown, enquanto testes podem substituir os.replace.
# Preservar a primitiva original isola o registro sem suprimir falhas reais de I/O.
_ATOMIC_REPLACE = os.replace


def _write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                         encoding="utf-8")
    _ATOMIC_REPLACE(temporary, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_source(name: str) -> bool:
    p = PurePosixPath(name)
    if not p.parts or p.is_absolute() or ".." in p.parts:
        return False
    if any(part in _EXCLUDED_COMPONENTS for part in p.parts):
        return False
    if p.parts[0] in _EXCLUDED_ROOTS or p.parts[0].startswith(("livro-", "opencode-ecosystem-core-pesquisador-")):
        return False
    # Arquivos privados não são abertos, nem mesmo para calcular hashes.
    if any(part.lower().startswith((".env", "secret", "credential")) for part in p.parts):
        return False
    if p.name.lower() in {"auth.json", "token.json", "tokens.json", "oauth.json", "settings.local.json"}:
        return False
    if len(p.parts) == 1 and p.suffix.lower() == ".md":
        return False
    return p.suffix.lower() in _SOURCE_SUFFIXES


def source_snapshot(root: Path) -> dict:
    """Hash do estado de trabalho, incluindo fontes novas ainda fora do índice."""
    root = Path(root).resolve()
    process = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                             cwd=root, capture_output=True, check=True, timeout=30)
    files = {}
    for name in sorted({os.fsdecode(item) for item in process.stdout.split(b"\0") if item}):
        if not _is_source(name):
            continue
        path = root / name
        # Não seguir symlinks de fonte, diretórios redirecionados ou arquivos privados.
        path.resolve().relative_to(root)
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != root):
            raise ValueError(f"Fonte contém symlink: {name}")
        if not path.exists():
            files[name] = {"state": "deleted"}
        elif path.is_file():
            if path.stat().st_size > 64 * 1024 * 1024:
                raise ValueError(f"Fonte excede 64 MiB: {name}")
            files[name] = {"sha256": _sha256(path), "bytes": path.stat().st_size}
        else:
            raise ValueError(f"Fonte não é arquivo regular: {name}")
    if not files:
        raise ValueError("Snapshot não contém fontes reconhecidas")
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return {"digest": hashlib.sha256(canonical).hexdigest(), "files": files,
            "policy": "git_worktree_sources_v1", "includes_untracked": True,
            "excluded_components": sorted(_EXCLUDED_COMPONENTS),
            "excluded_roots": sorted(_EXCLUDED_ROOTS), "source_suffixes": sorted(_SOURCE_SUFFIXES)}


class _Recorder:
    """Plugin local: coleta e fases reais, sem inferir execução de texto do log."""

    def __init__(self, path: Path, run_id: str):
        self.path = path
        self.record = {"run_id": run_id, "session_complete": False,
                       "selected_nodeids": [], "reports": [], "collection_errors": []}

    def _save(self):
        self.record["written_ns"] = time.time_ns()
        _write_json(self.path, self.record)

    def pytest_collection_modifyitems(self, items):
        self.record["selected_nodeids"] = [item.nodeid for item in items]
        for item in items:
            item.user_properties.append(("scientific_profile_nodeid", item.nodeid))
        self._save()

    def pytest_collectreport(self, report):
        if report.failed:
            self.record["collection_errors"].append(report.nodeid)
            self._save()

    def pytest_runtest_logreport(self, report):
        self.record["reports"].append({"nodeid": report.nodeid, "when": report.when,
                                        "outcome": report.outcome})
        self._save()

    def pytest_sessionfinish(self, session, exitstatus):
        self.record["session_complete"] = True
        self.record["exit_code"] = int(exitstatus)
        self._save()


def validate_group_receipts(folder: Path, run_id: str, started_ns: int,
                            ended_ns: int, exit_code: int | None) -> dict:
    """Falha fechada sobre recibos novos de uma execução do grupo."""
    folder = Path(folder)
    junit, ledger_path = folder / "junit.xml", folder / "execution.json"
    result = {"status": "blocked", "problems": [], "selected_nodeids": [],
              "executed_nodeids": [], "junit_path": str(junit), "ledger_path": str(ledger_path)}
    problems = result["problems"]
    if exit_code != 0:
        problems.append(f"pytest_exit:{exit_code}")
    try:
        if ledger_path.is_symlink() or junit.is_symlink():
            raise ValueError("Recibo não pode ser symlink")
        for path in (ledger_path, junit):
            if not started_ns <= path.stat().st_mtime_ns <= ended_ns + 1_000_000_000:
                raise ValueError("Recibo antigo ou futuro")
        if ledger_path.stat().st_size > 32 * 1024 * 1024:
            raise ValueError("Ledger excede limite")
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        if not isinstance(ledger, dict):
            raise TypeError("Ledger deve ser objeto JSON")
        if (ledger.get("run_id") != run_id or ledger.get("session_complete") is not True
                or type(ledger.get("exit_code")) is not int
                or ledger.get("exit_code") != exit_code
                or not started_ns <= ledger.get("written_ns", 0) <= ended_ns + 1_000_000_000):
            raise ValueError("Ledger incompleto ou pertence a outra execução")
        selected, reports = ledger["selected_nodeids"], ledger["reports"]
        if (not isinstance(selected, list) or not all(isinstance(n, str) for n in selected)
                or len(selected) != len(set(selected)) or not isinstance(reports, list)):
            raise ValueError("Seleção inválida")
        if any(not isinstance(item, dict)
               or not all(isinstance(item.get(key), str) for key in ("nodeid", "when", "outcome"))
               for item in reports):
            raise ValueError("Fases de execução inválidas")
        result["selected_nodeids"] = selected
        result["executed_nodeids"] = list(dict.fromkeys(
            item["nodeid"] for item in reports if item["when"] == "call"))
        if not selected:
            problems.append("zero_tests")
        if ledger.get("collection_errors"):
            problems.append("collection_errors")
        counts = load_junit_results(junit)
        result["counts"] = {key: counts[key] for key in ("total", "passed", "failed", "errors", "skipped")}
        result["junit_sha256"] = counts["junit_sha256"]
        result["ledger_sha256"] = _sha256(ledger_path)
        for key in ("failed", "errors", "skipped", "unrepresented_tests"):
            if counts[key]:
                problems.append(key)
        if counts["total"] != len(selected) or counts["passed"] != len(selected):
            problems.append("incomplete_junit")
        cases = list(ET.fromstring(junit.read_bytes()).iter("testcase"))
        identities = [case.findall("./properties/property[@name='scientific_profile_nodeid']") for case in cases]
        if (any(len(props) != 1 for props in identities)
                or sorted(props[0].get("value", "") for props in identities) != sorted(selected)):
            problems.append("junit_selection_mismatch")
        for nodeid in selected:
            phases = [(r["when"], r["outcome"]) for r in reports if r["nodeid"] == nodeid]
            if phases != [("setup", "passed"), ("call", "passed"), ("teardown", "passed")]:
                problems.append(f"incomplete_execution:{nodeid}")
        if any(r["nodeid"] not in selected for r in reports):
            problems.append("unexpected_execution")
    except (OSError, ValueError, TypeError, KeyError, ET.ParseError) as exc:
        problems.append(f"invalid_receipt:{type(exc).__name__}:{exc}")
        if not result["selected_nodeids"] and "zero_tests" not in problems:
            problems.append("zero_tests")
    if not problems:
        result["status"] = "passed"
    return result


def _environment(folder: Path) -> dict:
    env = os.environ.copy()
    for key in ("PYTEST_ADDOPTS", "PYTHONPATH", "PYTEST_PLUGINS", "PYTEST_CURRENT_TEST"):
        env.pop(key, None)
    for key in _THREAD_KEYS:
        env[key] = "1"
    env["PYTHONHASHSEED"] = "0"
    env["MCI_STATE_DIR"] = str(folder / "mci-state")
    env["HARNESS_HEALTH_PATH"] = str(folder / "harness-health.sqlite3")
    return env


def _stop_owned_processes(process: subprocess.Popen, observed: dict) -> list[int]:
    """Encerra a árvore que iniciou, sem procurar processos alheios pelo nome."""
    try:
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            observed[(child.pid, child.create_time())] = child
    except psutil.NoSuchProcess:
        pass
    owned = []
    for (_, created), child in observed.items():
        try:
            if child.create_time() == created and child.is_running():
                owned.append(child)
                child.terminate()
        except psutil.NoSuchProcess:
            pass
    # POSIX: a sessão criada exclusivamente pelo runner também contém filhos
    # muito rápidos para o primeiro snapshot psutil. O PGID é o PID deste filho.
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        process.terminate()
    _, alive = psutil.wait_procs(owned, timeout=0.3)
    for child in alive:
        try:
            child.kill()
        except psutil.NoSuchProcess:
            pass
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        process.kill()
    process.wait(timeout=5)
    survivors = []
    for child in owned:
        try:
            if child.is_running() and child.status() != psutil.STATUS_ZOMBIE:
                survivors.append(child.pid)
        except psutil.NoSuchProcess:
            pass
    return survivors


def _run_group(root: Path, folder: Path, name: str, targets: tuple, run_id: str,
               timeout: float, max_rss_bytes: int) -> dict:
    folder.mkdir()
    started_ns, start = time.time_ns(), time.monotonic()
    log_path = folder / "pytest.log"
    command = [sys.executable, str(Path(__file__).resolve()), "--_worker", run_id,
               "--_ledger", str(folder / "execution.json"), "--",
               "-q", "-o", "addopts=", "-o", "junit_family=xunit2",
               "--junitxml", str(folder / "junit.xml"), *targets]
    _write_json(folder / "selection.json", {"run_id": run_id, "group": name,
                "targets": list(targets), "command": command, "started_ns": started_ns})
    peak, observed, stop_reason, cleanup_problems = 0, {}, None, []
    with log_path.open("w", encoding="utf-8") as log:
        try:
            process = subprocess.Popen(command, cwd=root, stdout=log, stderr=subprocess.STDOUT,
                                       env=_environment(folder), start_new_session=os.name == "posix")
            try:
                parent = psutil.Process(process.pid)
                while process.poll() is None:
                    rss = 0
                    try:
                        tree = [parent, *parent.children(recursive=True)]
                    except psutil.NoSuchProcess:
                        tree = []
                    for child in tree:
                        try:
                            observed[(child.pid, child.create_time())] = child
                            rss += child.memory_info().rss
                        except psutil.NoSuchProcess:
                            pass
                    peak = max(peak, rss)
                    if rss > max_rss_bytes:
                        stop_reason = "memory_limit"
                        break
                    if time.monotonic() - start >= timeout:
                        stop_reason = "timeout"
                        break
                    time.sleep(0.025)
            finally:
                # Limpa descendentes mesmo quando pytest conclui normalmente.
                survivors = _stop_owned_processes(process, observed)
                if survivors:
                    cleanup_problems.append(f"cleanup_incomplete:{survivors}")
            exit_code = process.returncode
        except (OSError, psutil.Error, subprocess.TimeoutExpired) as exc:
            exit_code = None
            cleanup_problems.append(f"process_error:{type(exc).__name__}:{exc}")
    ended_ns = time.time_ns()
    result = validate_group_receipts(folder, run_id, started_ns, ended_ns, exit_code)
    result.update(name=name, targets=list(targets), started_ns=started_ns, ended_ns=ended_ns,
                  duration_seconds=round(time.monotonic() - start, 3), exit_code=exit_code,
                  peak_rss_bytes=peak, max_rss_bytes=max_rss_bytes, timeout_seconds=timeout,
                  log_path=str(log_path), log_sha256=_sha256(log_path),
                  selection_path=str(folder / "selection.json"),
                  selection_sha256=_sha256(folder / "selection.json"))
    if stop_reason:
        result["problems"].append(stop_reason)
    result["problems"].extend(cleanup_problems)
    result["status"] = "blocked" if result["problems"] else "passed"
    _write_json(folder / "result.json", result)
    return result


def _validate_options(groups, group_timeout, max_rss_bytes):
    if (isinstance(group_timeout, bool) or not isinstance(group_timeout, (int, float))
            or not math.isfinite(group_timeout) or not 0 < group_timeout <= DEFAULT_GROUP_TIMEOUT):
        raise ValueError("Prazo deve ser positivo e no máximo 180 segundos por grupo")
    if (type(max_rss_bytes) is not int or not 0 < max_rss_bytes <= DEFAULT_MAX_RSS_BYTES):
        raise ValueError("RSS deve ser inteiro positivo e no máximo 1536 MiB por grupo")
    if not groups or not isinstance(groups, (tuple, list)):
        raise ValueError("Perfil vazio ou inválido")
    seen_names, seen_targets = set(), set()
    for name, targets in groups:
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name) or name in seen_names:
            raise ValueError("Nome de grupo inválido ou duplicado")
        seen_names.add(name)
        if not isinstance(targets, (tuple, list)) or not targets:
            raise ValueError("Grupo sem seleção explícita")
        for target in targets:
            path = PurePosixPath(target.split("::", 1)[0]) if isinstance(target, str) else None
            if (path is None or not target.startswith("tests/test_") or path.suffix != ".py"
                    or ".." in path.parts or "*" in target or target in seen_targets):
                raise ValueError("Seleção deve conter somente testes internos enumerados e únicos")
            seen_targets.add(target)


def run_profile(root: Path, output: Path, *, groups=PROFILE_GROUPS,
                group_timeout=DEFAULT_GROUP_TIMEOUT,
                max_rss_bytes=DEFAULT_MAX_RSS_BYTES) -> dict:
    """API interna aceita perfil de fixture; a CLI utiliza sempre PROFILE_GROUPS."""
    _validate_options(groups, group_timeout, max_rss_bytes)
    root, output = Path(root).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex
    folder = output / run_id
    folder.mkdir(exist_ok=False)
    report = {"schema_version": "1.0", "status": "blocked", "run_id": run_id,
        "run_dir": str(folder), "report_path": str(folder / "summary.json"),
        "scope": "enumerated_scientific_regression_profile", "global_suite_executed": False,
        "external_scientific_validation": False, "scientific_scale_validated": False,
        "root": str(root), "python_version": sys.version, "platform": sys.platform,
        "started_ns": time.time_ns(), "groups": [], "problems": [],
        "profile_selection": [{"name": name, "targets": list(targets)} for name, targets in groups],
        "profile_exclusions": PROFILE_EXCLUSIONS,
        "limits": {"group_timeout_seconds": group_timeout, "max_rss_bytes": max_rss_bytes,
                   "rss_scope": "pytest_process_and_descendants_sampled_every_25ms",
                   "thread_environment": {key: "1" for key in _THREAD_KEYS}},
        "totals": dict.fromkeys(("total", "passed", "failed", "errors", "skipped"), 0),
        "not_executed_groups": [name for name, _ in groups], "changed_sources": [],
        "limitations": ["Perfil local enumerado; não representa a suíte global.",
                        "RSS amostrado; não constitui isolamento por cgroup ou limite instantâneo.",
                        "Hashes antes/depois não detectam alteração transitória revertida durante execução.",
                        "Nenhuma validação externa de dados, referências, mérito ou escala científica."]}
    report["dependency_versions"] = {}
    for package in ("pytest", "pytest-timeout", "numpy", "scipy", "psutil"):
        try:
            report["dependency_versions"][package] = version(package)
        except PackageNotFoundError:
            report["dependency_versions"][package] = None
    try:
        report["source_before"] = source_snapshot(root)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report["problems"].append("source_snapshot_failed")
        report["snapshot_error"] = f"{type(exc).__name__}:{exc}"
    else:
        for index, (name, targets) in enumerate(groups, 1):
            print(f"[{index}/{len(groups)}] {name}: executando seleção enumerada", flush=True)
            result = _run_group(root, folder / f"{index:02d}-{name}", name, targets,
                                run_id, group_timeout, max_rss_bytes)
            report["groups"].append(result)
            report["not_executed_groups"].remove(name)
            for key, value in result.get("counts", {}).items():
                report["totals"][key] += value
            print(f"[{index}/{len(groups)}] {name}: {result['status']}", flush=True)
            if result["status"] != "passed":
                report["problems"].append(f"group_blocked:{name}")
                break
        try:
            report["source_after"] = source_snapshot(root)
            before, after = report["source_before"]["files"], report["source_after"]["files"]
            report["changed_sources"] = sorted(name for name in before.keys() | after.keys()
                                                if before.get(name) != after.get(name))
            if report["changed_sources"]:
                report["problems"].append("source_changed")
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            report["problems"].append("source_snapshot_after_failed")
            report["snapshot_error"] = f"{type(exc).__name__}:{exc}"
    if report["not_executed_groups"]:
        report["problems"].append("unexecuted_groups")
    if not report["totals"]["total"]:
        report["problems"].append("zero_tests")
    if not report["problems"]:
        report["status"] = "passed"
    report["ended_ns"] = time.time_ns()
    _write_json(folder / "summary.json", report)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "reports/scientific-profile")
    parser.add_argument("--_worker", help=argparse.SUPPRESS)
    parser.add_argument("--_ledger", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    options = parser.parse_args(argv)
    if options._worker:
        import pytest
        arguments = options.pytest_args
        if arguments and arguments[0] == "--":
            arguments = arguments[1:]
        return int(pytest.main(arguments, plugins=[_Recorder(options._ledger, options._worker)]))
    if options.pytest_args:
        parser.error("A CLI aceita somente o perfil fechado; seleções adicionais não são permitidas")
    report = run_profile(REPO_ROOT, options.output)
    print(json.dumps({"status": report["status"], "totals": report["totals"],
                      "report_path": report["report_path"], "problems": report["problems"]},
                     ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
