"""Roteador JSON dos laboratórios reais — SPEC-935-R900 FR-002..FR-012.

Contrato: ``handle_get``/``handle_post`` devolvem ``Response`` para rotas
``/api/*``; ``None`` significa "não é minha rota" (o servidor segue para o
backend simulado da SPEC-935-R899). Toda exceção vira JSON de erro — o servidor
nunca cai por causa de uma requisição.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from . import ca_lab, datasets, labs
from .jobs import manager as job_manager
from .paths import DatasetPathError, ensure_import_path

ensure_import_path()

MOCK_SHAPE_ROUTES = {"/api/health", "/api/datasets", "/api/models", "/api/validation"}


@dataclass
class Response:
    status: int
    ctype: str
    body: bytes
    headers: dict[str, str] = field(default_factory=dict)


def json_response(obj: Any, status: int = 200) -> Response:
    return Response(
        status=status,
        ctype="application/json; charset=utf-8",
        body=json.dumps(obj, ensure_ascii=False, default=str).encode(),
    )


def error_response(detail: str, status: int = 400) -> Response:
    return json_response({"detail": detail, "real": True}, status=status)


def _q(query: Mapping[str, Sequence[str]] | None, key: str, default: str | None = None) -> str | None:
    if not query:
        return default
    values = query.get(key)
    if not values:
        return default
    return values[0]


def _q_int(query, key: str, default: int, lo: int, hi: int) -> int:
    raw = _q(query, key)
    if raw is None:
        return default
    try:
        return max(lo, min(int(float(raw)), hi))
    except (TypeError, ValueError):
        return default


def _has_module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


# --------------------------------------------------------------------------- GET
def _health() -> Response:
    return json_response(
        {
            "real": True,
            "mock": False,
            "mode": "local-real+laboratorios",
            "python": sys.version.split()[0],
            "capabilities": {
                "odontoca": _has_module("odontoca"),
                "sklearn": _has_module("sklearn"),
                "pandas": _has_module("pandas"),
                "numpy": _has_module("numpy"),
                "openpyxl": _has_module("openpyxl"),
                "pil": _has_module("PIL"),
            },
            "datasets": len(datasets.inventory()),
            "laboratories": len(labs.model_reports()),
            "ca_states": ["H", "C", "F", "M"],
            "claim_levels": {
                "ml": labs.CLAIM_LEVEL,
                "ca": ca_lab.CLAIM_LEVEL,
            },
            "disclaimer": (
                "Laboratórios locais reais (dataset/treino/CA). Sem inferência "
                "hospedada; comparação empírica e simulação descritiva — revisão "
                "humana obrigatória."
            ),
        }
    )


def _datasets_index() -> Response:
    items = datasets.inventory()
    return json_response(
        {
            "real": True,
            "mock": False,
            "count": len(items),
            "allowlist": sorted(datasets.names()),
            "datasets": items,
        }
    )


def _dataset_sample(query) -> Response:
    name = _q(query, "name")
    if not name:
        return error_response("parâmetro 'name' é obrigatório", 400)
    n = _q_int(query, "n", 5, 1, 50)
    sheet = _q(query, "sheet")
    try:
        return json_response(datasets.sample(name, n=n, sheet=sheet))
    except KeyError:
        return error_response(f"dataset fora do inventário: {name}", 404)
    except DatasetPathError as exc:
        return error_response(str(exc), 400)
    except Exception as exc:
        return error_response(f"{type(exc).__name__}: {exc}", 500)


def _models() -> Response:
    labs_list = labs.model_reports()
    return json_response(
        {
            "real": True,
            "mock": False,
            "count": len(labs_list),
            "claim_level": labs.CLAIM_LEVEL,
            "disclaimer": labs.DISCLAIMER,
            "laboratories": labs_list,
        }
    )


def _jobs_index() -> Response:
    return json_response(
        {"real": True, "jobs": [job.payload() for job in job_manager.list()]}
    )


def _job_status(query) -> Response:
    job_id = _q(query, "id")
    if job_id:
        job = job_manager.get(job_id)
        if job is None:
            return error_response(f"job inexistente: {job_id}", 404)
    else:
        job = job_manager.latest()
    if job is None:
        return json_response({"real": True, "job": None, "detail": "nenhum job iniciado"})
    payload = job.payload(with_report=True)
    if job.state == "error":
        payload["detail"] = job.error
    return json_response(payload)


def _ca_demo(query) -> Response:
    steps = _q_int(query, "steps", 3, 1, 20)
    seed = _q_int(query, "seed", 7, 0, 10**6)
    n_teeth = _q_int(query, "n_teeth", 32, 1, 32)
    return json_response(ca_lab.simulate(steps=steps, seed=seed, n_teeth=n_teeth, rule="prior"))


def _validation() -> Response:
    return json_response(labs.validation())


_GET_ROUTES = {
    "/api/health": lambda q: _health(),
    "/api/datasets": lambda q: _datasets_index(),
    "/api/datasets/sample": _dataset_sample,
    "/api/models": lambda q: _models(),
    "/api/train/jobs": lambda q: _jobs_index(),
    "/api/train/status": _job_status,
    "/api/ca/demo": _ca_demo,
    "/api/validation": lambda q: _validation(),
}


def handle_get(path: str, query: Mapping[str, Sequence[str]] | None = None) -> Response | None:
    handler = _GET_ROUTES.get(path)
    if handler is None:
        return None
    try:
        return handler(query or {})
    except Exception as exc:
        return error_response(f"{type(exc).__name__}: {exc}", 500)


# --------------------------------------------------------------------------- POST
def _read_json(body: bytes, ctype: str) -> dict[str, Any]:
    if not body:
        return {}
    if "json" not in (ctype or ""):
        raise ValueError("Content-Type deve ser application/json")
    data = json.loads(body.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("corpo JSON deve ser um objeto")
    return data


def _start_training(body: bytes, ctype: str) -> Response:
    try:
        payload = _read_json(body, ctype)
    except Exception as exc:
        return error_response(f"JSON inválido: {exc}", 400)
    dataset = payload.get("dataset") or "Table_S1.xlsx"
    task = str(payload.get("task") or ("onset" if dataset == "Table_S1.xlsx" else "default"))
    try:
        job = job_manager.start(
            str(dataset),
            task=task,
            folds=int(payload.get("folds") or 5),
            seed=int(payload.get("seed") or 0),
            target=(str(payload["target"]) if payload.get("target") else None),
            sample_rows=(int(payload["sample_rows"]) if payload.get("sample_rows") else None),
        )
    except (ValueError, DatasetPathError) as exc:
        return error_response(str(exc), 400)
    except Exception as exc:
        return error_response(f"{type(exc).__name__}: {exc}", 500)
    return json_response({"real": True, "accepted": True, "job": job.payload()}, 202)


def _ca_simulate(body: bytes, ctype: str) -> Response:
    try:
        payload = _read_json(body, ctype)
    except Exception as exc:
        return error_response(f"JSON inválido: {exc}", 400)
    try:
        result = ca_lab.simulate(
            steps=int(payload.get("steps") or 3),
            seed=int(payload.get("seed") or 0),
            n_teeth=int(payload.get("n_teeth") or 32),
            rule=str(payload.get("rule") or "prior"),
        )
    except Exception as exc:
        return error_response(f"{type(exc).__name__}: {exc}", 500)
    return json_response(result)


_POST_ROUTES = {
    "/api/train": _start_training,
    "/api/ca/simulate": _ca_simulate,
}


def handle_post(
    path: str,
    query: Mapping[str, Sequence[str]] | None = None,
    body: bytes = b"",
    content_type: str = "",
) -> Response | None:
    handler = _POST_ROUTES.get(path)
    if handler is None:
        return None
    try:
        return handler(body, content_type)
    except Exception as exc:
        return error_response(f"{type(exc).__name__}: {exc}", 500)
