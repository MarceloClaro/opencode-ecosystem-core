"""Percurso científico delimitado: proveniência, cálculo e reprodução (R663)."""
from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .statistical_methods import MAX_CSV_BYTES, METHODS, execute_analysis, validate_configuration

MAX_REFERENCE_BYTES = 1_000_000
MAX_REFERENCES = 20
MAX_PROVENANCE_BYTES = 128_000


def _validate_provenance_metadata(value: Any, depth: int = 0) -> None:
    if depth > 8:
        raise ValueError("provenance metadata nesting exceeds its limit")
    if isinstance(value, dict):
        if len(value) > 100:
            raise ValueError("provenance object exceeds its field limit")
        for key, item in value.items():
            if not isinstance(key, str) or not key or len(key) > 128:
                raise ValueError("invalid provenance metadata key")
            _validate_provenance_metadata(item, depth + 1)
    elif isinstance(value, list):
        if len(value) > 1000:
            raise ValueError("provenance metadata list exceeds its limit")
        for item in value:
            _validate_provenance_metadata(item, depth + 1)
    elif isinstance(value, str):
        if len(value) > 8192 or any(ord(character) < 32 and character not in "\n\r\t" for character in value):
            raise ValueError("invalid provenance metadata text")
    elif value is not None and not isinstance(value, (bool, int, float)):
        raise ValueError("provenance metadata must be JSON data")


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)


def _https_url(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) > 2048:
        raise ValueError(f"{field} requires an HTTPS URL")
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.fragment:
        raise ValueError(f"{field} requires an HTTPS URL without credentials or fragment")
    return value


def _snapshot(path: Any, maximum: int, expected_hash: Any = None) -> tuple[bytes, str]:
    if not isinstance(path, (str, Path)):
        raise ValueError("snapshot path must be a filesystem path")
    candidate = Path(path)
    if not candidate.is_file() or not 0 < candidate.stat().st_size <= maximum:
        raise ValueError("snapshot missing, empty or exceeds its size limit")
    with candidate.open("rb") as stream:
        raw = stream.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("snapshot exceeds its size limit")
    digest = _hash(raw)
    if expected_hash is not None and expected_hash != digest:
        raise ValueError("snapshot_hash_mismatch")
    return raw, digest


def _validate_reference(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict) or record.get("synthetic") or record.get("evidence_kind") in {"synthetic", "demonstration", "simulation"}:
        raise ValueError("reference must contain actual bibliographic metadata")
    title = record.get("title")
    if not isinstance(title, str) or not title.strip() or len(title) > 2000:
        raise ValueError("reference requires a title")
    doi = record.get("doi")
    url = record.get("url") or (f"https://doi.org/{doi}" if doi else None)
    if isinstance(url, str) and url.startswith("http://doi.org/"):
        url = url.replace("http://", "https://", 1)
    _https_url(url, "reference.url")
    abstract = record.get("abstract", "") or ""
    if not isinstance(abstract, str) or len(abstract) > 100_000:
        raise ValueError("reference abstract exceeds its limit")
    return {**record, "title": title.strip(), "url": url, "abstract": abstract}


def _collect_references(question: str, sources: list[dict[str, Any]] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[bytes]]:
    records: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    snapshots: list[bytes] = []
    if sources is not None:
        if not isinstance(sources, list) or not 1 <= len(sources) <= 5:
            raise ValueError("reference_sources must contain one to five source snapshots")
        for source in sources:
            if not isinstance(source, dict):
                raise ValueError("reference source must be an object")
            source_url = _https_url(source.get("source_url"), "reference source_url")
            raw, digest = _snapshot(source.get("path"), MAX_REFERENCE_BYTES, source.get("sha256"))
            document = json.loads(raw)
            if not isinstance(document, dict) or document.get("status") != "online" or document.get("synthetic") or document.get("evidence_eligible") is False or document.get("evidence_kind") != "retrieved_http_metadata":
                raise ValueError("reference snapshot must declare retrieved HTTP metadata; offline or demonstration data are ineligible")
            items = document.get("records")
            if not isinstance(items, list) or not 1 <= len(items) <= MAX_REFERENCES:
                raise ValueError("reference snapshot requires one to twenty records")
            records.extend(_validate_reference(item) for item in items)
            provenance.append({"source_url": source_url, "sha256": digest,
                               "source_mode": "provided_snapshot", "source_authenticity": "user_declared",
                               "evidence_kind": "retrieved_http_metadata", "status": "online",
                               "retrieved_at": document.get("retrieved_at")})
            snapshots.append(raw)
    else:
        from .searchers import CrossrefSearcher, OpenAlexSearcher
        for searcher, source_url in ((CrossrefSearcher(), "https://api.crossref.org/works"),
                                     (OpenAlexSearcher(), "https://api.openalex.org/works")):
            try:
                items = searcher._search(question, 3)
                validated = [_validate_reference(item.to_dict()) for item in items]
            except Exception as exc:
                provenance.append({"source_url": source_url, "source_mode": "live_http",
                                   "status": "unavailable", "evidence_kind": "failed_http_request",
                                   "error_type": type(exc).__name__})
                continue
            if validated:
                document = {"status": "online", "evidence_kind": "retrieved_http_metadata",
                            "retrieved_at": datetime.now(timezone.utc).isoformat(), "records": validated}
                raw = _json(document).encode("utf-8")
                records.extend(validated)
                provenance.append({"source_url": source_url, "sha256": _hash(raw),
                                   "source_mode": "live_http", "source_authenticity": "captured_by_pipeline",
                                   "evidence_kind": "retrieved_http_metadata", "status": "online",
                                   "retrieved_at": document["retrieved_at"]})
                snapshots.append(raw)
                break
            provenance.append({"source_url": source_url, "source_mode": "live_http", "status": "empty"})
    unique = {}
    for record in records:
        key = record.get("doi") or record["url"]
        unique.setdefault(key, record)
    if not unique:
        raise ValueError("no_eligible_reference_sources")
    return list(unique.values())[:MAX_REFERENCES], provenance, snapshots


_REPRODUCER = '''"""Reprodução R663: executa somente métodos internos copiados com o estudo."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
configuration = json.loads((root / "configuration.json").read_text(encoding="utf-8"))
dataset = root / "dataset.csv"
digest = hashlib.sha256(dataset.read_bytes()).hexdigest()
code_digest = hashlib.sha256((root / "statistical_methods.py").read_bytes()).hexdigest()
if digest != configuration["dataset_sha256"] or code_digest != configuration["methods_sha256"]:
    print(json.dumps({"status": "blocked", "error": "dataset_hash_mismatch" if digest != configuration["dataset_sha256"] else "methods_hash_mismatch"}))
    sys.exit(2)
try:
    from statistical_methods import execute_analysis
    result = execute_analysis(dataset, configuration["method"], configuration["variables"])
    print(json.dumps({"status": "completed", "dataset_sha256": digest, "analysis": result}, sort_keys=True, allow_nan=False))
except Exception as exc:
    print(json.dumps({"status": "blocked", "error_type": type(exc).__name__}))
    sys.exit(2)
'''


def _article(question: str, dataset: dict[str, Any], analysis: dict[str, Any], references: list[dict[str, Any]], reproduction: dict[str, Any]) -> str:
    reference_lines = []
    for index, reference in enumerate(references, 1):
        title = re.sub(r"[\r\n]+", " ", reference["title"])
        reference_lines.append(f"{index}. {title}. {reference.get('year') or 's.d.'}. {reference['url']}")
    inferential = (f"Estimativa: {analysis['estimate']:.8g}. p-valor bilateral: {analysis['p_value']:.8g}. "
                   f"Intervalo de 95%: {analysis['confidence_interval_95']}." if analysis.get("p_value") is not None
                   else "Análise descritiva; não foi realizado teste de hipótese.")
    assumptions = "\n".join(f"- {item}" for item in analysis["assumptions"])
    limitations = "\n".join(f"- {item}" for item in analysis["limitations"])
    return f"""# Relatório científico computacional

## Pergunta

{question}

## Dados e proveniência

Dataset: {dataset['title']}. Origem informada: {dataset['source_url']}.
SHA-256 do CSV analisado: {dataset['sha256']}.
A origem de arquivos fornecidos é uma declaração do responsável; o hash identifica
o conteúdo e não certifica sua autenticidade. Evidência externa independente: ausente.

Metadados de proveniência informados, incluindo transformação e limitações:

```json
{_json(dataset)}
```

## Método prespecificado

Método: {analysis['method']}. Observações: {analysis['n']}.
Colunas/grupos: {json.dumps(analysis['variables'], ensure_ascii=False)}.
Valores ausentes e não finitos são rejeitados. Um único método foi executado.
Hipótese nula: {analysis['null_hypothesis'] or 'não aplicável'}.

{assumptions}

## Resultados executados

{inferential}

```json
{_json(analysis)}
```

## Reprodução e revisão computacional

Reexecução em processo separado: {reproduction['process_executed']}.
Concordância com o cálculo original: {reproduction['matched']}.
A revisão computacional verificou integridade dos snapshots, consistência numérica
e reprodução; não ocorreu revisão humana por pares.

## Limitações

{limitations}
- As referências abaixo documentam metadados bibliográficos; não foram inferidos
  resultados dos artigos nem realizado julgamento humano de sua adequação.
- Este relatório não prova originalidade científica nem validade em outros domínios.

## Referências coletadas ou fornecidas como snapshots identificados

{chr(10).join(reference_lines)}
"""


def _retrieve_metadata(question: str, corpus: list[dict[str, Any]]) -> dict[str, Any]:
    """Recuperação lexical delimitada; metadados não sustentam claims do artigo."""
    query_tokens = set(re.findall(r"\w+", question.casefold()))
    evidence = []
    for document in corpus:
        terms = set(re.findall(r"\w+", document["text"].casefold()))
        overlap = sorted(query_tokens & terms)
        if overlap:
            evidence.append({"doc_id": document["doc_id"], "title": document["title"],
                             "source": document["source"], "sha256": document["sha256"],
                             "lexical_score": len(overlap) / max(1, len(query_tokens)),
                             "matched_terms": overlap, "evidence_scope": "bibliographic_metadata"})
    evidence.sort(key=lambda item: (-item["lexical_score"], item["doc_id"]))
    return {"query": question, "retrieval_executed": True, "method": "lexical_overlap",
            "evidence": evidence[:5], "abstained": not bool(evidence),
            "model_inference_executed": False, "scientific_claim_support": False,
            "limitation": "A recuperação usa título/resumo; não demonstra leitura integral ou sustentação dos resultados."}


class ScientificProvenancePipeline:
    """API de execução local delimitada; não recebe programas ou comandos."""

    def describe(self) -> dict[str, Any]:
        return {"methods": list(METHODS), "dataset_format": "CSV UTF-8",
                "requires": ["question", "dataset_csv", "dataset_provenance", "method", "variables", "output_dir"],
                "reference_modes": ["live_http_open_science", "provided_hashed_snapshot"],
                "human_peer_review": False, "external_validation": False,
                "arbitrary_code_execution": False, "max_csv_bytes": MAX_CSV_BYTES}

    def run(self, *, question: str, dataset_csv: str, dataset_provenance: dict[str, Any],
            method: str, variables: dict[str, Any], output_dir: str,
            reference_sources: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        try:
            if not isinstance(question, str) or not question.strip() or len(question) > 4000:
                raise ValueError("question must contain one to four thousand characters")
            validate_configuration(method, variables)
            if not isinstance(dataset_provenance, dict) or dataset_provenance.get("evidence_kind") != "real_observations" or dataset_provenance.get("synthetic") or dataset_provenance.get("evidence_eligible") is False:
                raise ValueError("dataset requires an explicit real_observations declaration; demonstration data are ineligible")
            _validate_provenance_metadata(dataset_provenance)
            if len(_json(dataset_provenance).encode()) > MAX_PROVENANCE_BYTES:
                raise ValueError("dataset provenance exceeds the 128 KB limit")
            title = dataset_provenance.get("title")
            if not isinstance(title, str) or not title.strip() or len(title) > 2000:
                raise ValueError("dataset requires a title")
            source_url = _https_url(dataset_provenance.get("source_url"), "dataset.source_url")
            if not isinstance(output_dir, str) or not output_dir.strip():
                raise ValueError("output_dir must name a new directory")
            output = Path(output_dir).resolve()
            if output.exists():
                raise ValueError("output_dir must not already exist")
            raw, digest = _snapshot(dataset_csv, MAX_CSV_BYTES, dataset_provenance.get("sha256"))
            references, reference_provenance, snapshots = _collect_references(question, reference_sources)
            _json(references)
            # Analisa o snapshot em memória para impedir drift entre leitura e análise:
            # um arquivo temporário privado contém exatamente os bytes que serão exportados.
            import tempfile
            with tempfile.TemporaryDirectory(prefix="r663-analysis-") as temporary:
                snapshot_path = Path(temporary) / "dataset.csv"
                snapshot_path.write_bytes(raw)
                analysis = execute_analysis(snapshot_path, method, variables)
                _json(analysis)  # bloqueia NaN/Infinity antes da criação dos artefatos.
        except (ValueError, TypeError, OSError, OverflowError, ImportError) as exc:
            return {"status": "blocked", "reason": str(exc)[:1000], "error_type": type(exc).__name__,
                    "experiment_executed": False, "artifacts": {}, "external_validation": False}

        dataset = {**dataset_provenance, "title": title, "source_url": source_url, "sha256": digest,
                   "evidence_kind": "real_observations", "source_authenticity": "user_declared",
                   "original_path": str(Path(dataset_csv).resolve()), "snapshot_bytes": len(raw)}
        methods_raw = Path(__file__).with_name("statistical_methods.py").read_bytes()
        configuration = {"method": method, "variables": variables, "dataset_sha256": digest,
                         "methods_sha256": _hash(methods_raw)}
        artifacts: dict[str, dict[str, Any]] = {}

        def write(name: str, filename: str, data: bytes) -> None:
            target = output / filename
            target.write_bytes(data)
            artifacts[name] = {"path": str(target), "sha256": _hash(data), "bytes": len(data)}

        try:
            output.mkdir(parents=True, exist_ok=False)
            write("dataset", "dataset.csv", raw)
            write("configuration", "configuration.json", _json(configuration).encode())
            write("analysis", "analysis.json", _json(analysis).encode())
            write("methods_code", "statistical_methods.py", methods_raw)
            write("reproduce_code", "reproduce.py", _REPRODUCER.encode())
            write("references", "references.json", _json(references).encode())
            for index, snapshot in enumerate(snapshots, 1):
                write(f"reference_source_{index}", f"reference-source-{index}.json", snapshot)
            process = subprocess.run([sys.executable, str(output / "reproduce.py")], cwd=output,
                                     capture_output=True, text=True, timeout=45, check=False)
            reproduced = json.loads(process.stdout) if process.returncode == 0 else {}
            matched = (process.returncode == 0 and reproduced.get("dataset_sha256") == digest
                       and _json(reproduced.get("analysis")) == _json(analysis))
            reproduction = {"process_executed": True, "exit_code": process.returncode,
                            "matched": matched, "dataset_sha256": reproduced.get("dataset_sha256"),
                            "analysis_sha256": _hash(_json(reproduced.get("analysis")).encode()) if reproduced else None}
            write("reproduction", "reproduction.json", _json(reproduction).encode())
            review = {"kind": "computational_review", "human_peer_review": False,
                      "external_validation": False, "reproduction_matched": matched,
                      "source_authenticity_independently_validated": False,
                      "single_prespecified_method": True, "finite_numeric_output": True,
                      "causal_inference": False, "passed": matched}
            write("computational_review", "computational-review.json", _json(review).encode())
            # Corpus RAG rastreável de metadados; sem alegar leitura integral dos artigos.
            rag_corpus = [{"doc_id": f"reference-{index}", "title": item["title"],
                           "source": item["url"], "text": item["title"] + "\n" + item["abstract"],
                           "evidence_scope": "bibliographic_metadata", "year": item.get("year"),
                           "sha256": _hash((item["title"] + "\n" + item["abstract"]).encode())}
                          for index, item in enumerate(references, 1)]
            write("rag_corpus", "rag-corpus.json", _json(rag_corpus).encode())
            retrieval = _retrieve_metadata(question, rag_corpus)
            write("rag_retrieval", "rag-query.json", _json(retrieval).encode())
            write("article", "article.md", _article(question, dataset, analysis, references, reproduction).encode())
            import scipy
            report = {"status": "completed" if matched else "blocked", "question": question,
                      "evidence_kind": "executed_local_analysis", "experiment_executed": True,
                      "external_validation": False, "model_inference_executed": False,
                      "provenance": {"dataset": dataset, "references": reference_provenance},
                      "analysis": analysis, "reproduction": reproduction,
                      "rag": retrieval,
                      "computational_review": review, "artifacts": artifacts.copy(),
                      "runtime": {"python": platform.python_version(), "scipy": scipy.__version__},
                      "generated_at": datetime.now(timezone.utc).isoformat()}
            if not matched:
                report["reason"] = "independent_reproduction_failed"
            write("manifest", "manifest.json", _json(report).encode())
            report["artifacts"] = artifacts
            return report
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            return {"status": "blocked", "reason": f"artifact_or_reproduction_failure: {type(exc).__name__}",
                    "experiment_executed": True, "artifacts": artifacts, "external_validation": False}
