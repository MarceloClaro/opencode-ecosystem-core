"""Manifesto e CLI do laboratório; não executa LLM, rede ou experimento."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import uuid
from datetime import datetime, timezone

from .budget import Budget, BudgetExceeded

SCHEMA = "r1049.research-lab.v1"
VERDICTS = {"partial", "rejected", "supported"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(data) -> str:
    text = json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode()).hexdigest()


def _write(directory: Path, name: str, data) -> None:
    path = directory / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def load_run(directory: Path | str) -> dict:
    path = Path(directory) / "manifest.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != SCHEMA:
        raise ValueError("manifesto de research lab inválido")
    return data


def create_run(objective: str, out_dir: Path | str, *, dry_run: bool = True,
               budget: Budget | None = None) -> dict:
    if not isinstance(objective, str) or not 10 <= len(objective.strip()) <= 2000:
        raise ValueError("objetivo deve ter entre 10 e 2000 caracteres")
    budget = budget or Budget()
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    run_id = "run-" + uuid.uuid4().hex[:12]
    directory = root / run_id
    directory.mkdir()
    manifest = {
        "schema_version": SCHEMA,
        "run_id": run_id,
        "created_utc": _now(),
        "objective": objective.strip(),
        "status": "planned" if dry_run else "awaiting_execution",
        "dry_run": bool(dry_run),
        "execution_performed": False,
        "human_review_required": True,
        "external_validation": False,
        "budget": budget.snapshot(),
        "steps": [],
        "limitations": [
            "O laboratório não chama LLM, rede ou experimento.",
            "Não há descoberta científica sem revisão e validação externas.",
            "Artefatos são file-first; a retomada lê manifest.json.",
        ],
    }
    manifest["manifest_sha256"] = _hash(manifest)
    _write(directory, "manifest.json", manifest)
    _write(directory, "budget.json", budget.snapshot())
    plan = (
        f"# Plano — {run_id}\n\n"
        f"## Objetivo\n\n{manifest['objective']}\n\n"
        "## Etapas previstas\n\n"
        "1. Delimitar pergunta e critério de refutação.\n"
        "2. Registrar fontes e hipóteses rivais.\n"
        "3. Definir evidência, análise e limites.\n"
        "4. Revisar com humano; não executar rede/LLM.\n\n"
        "## Status\n\n"
        f"- dry_run: `{manifest['dry_run']}`\n"
        "- execução: **não realizada**\n"
        "- revisão humana: **obrigatória**\n"
    )
    (directory / "plan.md").write_text(plan, encoding="utf-8")
    return manifest


def _refresh(directory: Path, manifest: dict) -> dict:
    manifest["manifest_sha256"] = _hash({k: v for k, v in manifest.items()
                                         if k != "manifest_sha256"})
    _write(directory, "manifest.json", manifest)
    _write(directory, "budget.json", manifest["budget"])
    return manifest


def record_step(directory: Path | str, name: str, notes: str, *,
                step_seconds: float = 0.0, cost_usd: float = 0.0,
                external_calls: int = 0) -> dict:
    directory = Path(directory)
    manifest = load_run(directory)
    if manifest["status"] not in {"planned", "in_progress", "awaiting_execution"}:
        raise ValueError("run não aceita novos passos")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("nome do passo obrigatório")
    if not isinstance(notes, str) or not notes.strip():
        raise ValueError("notas do passo obrigatórias")
    budget = Budget.from_dict(manifest["budget"])
    budget.consume(step_seconds=step_seconds, cost_usd=cost_usd,
                   external_calls=external_calls)
    manifest["budget"] = budget.snapshot()
    manifest["steps"].append({
        "index": len(manifest["steps"]) + 1,
        "name": name.strip(),
        "notes": notes.strip(),
        "step_seconds": step_seconds,
        "cost_usd": cost_usd,
        "external_calls": external_calls,
        "recorded_utc": _now(),
    })
    manifest["status"] = "in_progress"
    return _refresh(directory, manifest)


def finalize_run(directory: Path | str, *, reviewer: str, verdict: str,
                 notes: str = "") -> dict:
    directory = Path(directory)
    manifest = load_run(directory)
    if manifest["status"] not in {"planned", "in_progress", "awaiting_execution"}:
        raise ValueError("run já finalizado")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("revisor humano obrigatório")
    if verdict not in VERDICTS:
        raise ValueError(f"veredito inválido: {verdict}")
    review = {
        "run_id": manifest["run_id"],
        "reviewer": reviewer.strip(),
        "verdict": verdict,
        "notes": notes.strip(),
        "reviewed_utc": _now(),
        "human_review": True,
        "external_validation": False,
        "scope": "revisão local; não é validação externa",
    }
    _write(directory, "review.json", review)
    manifest["status"] = "completed_pending_external_validation"
    manifest["human_review"] = review
    manifest["execution_performed"] = False
    return _refresh(directory, manifest)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--max-seconds", type=float, default=60.0)
    parser.add_argument("--max-cost", type=float, default=0.0)
    parser.add_argument("--max-external-calls", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        budget = Budget(max_steps=args.max_steps, max_seconds=args.max_seconds,
                        max_cost_usd=args.max_cost, max_external_calls=args.max_external_calls)
        run = create_run(args.objective, args.out, dry_run=args.dry_run,
                         budget=budget)
    except (ValueError, BudgetExceeded) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)},
                         ensure_ascii=False))
        return 2
    print(json.dumps({"status": run["status"], "run_id": run["run_id"],
                      "directory": str(args.out / run["run_id"]),
                      "execution_performed": run["execution_performed"],
                      "human_review_required": run["human_review_required"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
