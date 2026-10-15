"""Jobs de treinamento REAIS em thread — SPEC-935-R900 FR-006/FR-007.

O treino local (`scikit-learn`) pode levar dezenas de segundos; por isso roda
em thread com progresso por estágio (``load → prepare → train → report``) e
*artefatos reais* em ``odonto/local/outputs/_jobs/<id>``. O progresso é
**honesto**: conta estágios concluídos, não folds (não instrumentamos o CV).
"""
from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from .paths import OUTPUTS, ensure_import_path
from . import datasets as datasets_mod

ensure_import_path()

STAGES = ("load", "prepare", "train", "report")
JOBS_DIR = OUTPUTS / "_jobs"
CLAIM_LEVEL = "comparacao_empirica"


@dataclass
class TrainJob:
    id: str
    dataset: str
    task: str = "default"
    folds: int = 5
    seed: int = 0
    target: str | None = None
    sample_rows: int | None = None
    state: str = "queued"          # queued | running | done | error
    stage: str = "queued"
    completed: int = 0
    total: int = len(STAGES)
    n_rows: int | None = None
    n_events: int | None = None
    subsampled: bool = False
    report: dict[str, Any] | None = None
    out_dir: str | None = None
    error: str | None = None
    started_at: float | None = None
    finished_at: float | None = None
    real: bool = True
    mock: bool = False
    claim_level: str = CLAIM_LEVEL
    stages: list[str] = field(default_factory=lambda: list(STAGES))

    @property
    def percentage(self) -> float:
        return round(100.0 * self.completed / max(1, self.total), 1)

    def payload(self, with_report: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "state": self.state,
            "stage": self.stage,
            "dataset": self.dataset,
            "task": self.task,
            "folds": self.folds,
            "seed": self.seed,
            "progress": {
                "completed": self.completed,
                "total": self.total,
                "percentage": self.percentage,
                "basis": "stage",
                "stages": self.stages,
            },
            "n_rows": self.n_rows,
            "n_events": self.n_events,
            "subsampled": self.subsampled,
            "real": True,
            "mock": False,
            "claim_level": self.claim_level,
            "out_dir": self.out_dir,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }
        if with_report:
            data["report"] = self.report
        return data


class TrainJobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, TrainJob] = {}
        self._lock = threading.Lock()

    def get(self, job_id: str) -> TrainJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list(self) -> list[TrainJob]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda j: j.started_at or 0, reverse=True)

    def latest(self) -> TrainJob | None:
        jobs = self.list()
        return jobs[0] if jobs else None

    def start(
        self,
        dataset: str,
        *,
        task: str = "default",
        folds: int = 5,
        seed: int = 0,
        target: str | None = None,
        sample_rows: int | None = None,
    ) -> TrainJob:
        """Inicia um job real. Recusa dataset fora da allowlist (FR-012)."""
        from .paths import resolve_dataset, resolve_table_s1

        allowed = datasets_mod.names()
        if dataset not in allowed:
            raise ValueError(
                f"dataset fora da allowlist: {dataset!r}; use um de {sorted(allowed)}"
            )
        if task not in {"default", "onset"}:
            raise ValueError(f"task inválida: {task}")
        if task == "onset" and dataset != "Table_S1.xlsx":
            raise ValueError("task=onset exige Table_S1.xlsx (fonte primária)")

        path = resolve_table_s1() if dataset == "Table_S1.xlsx" else resolve_dataset(dataset)
        job = TrainJob(
            id=uuid.uuid4().hex[:12],
            dataset=dataset,
            task=task,
            folds=max(2, min(int(folds), 10)),
            seed=int(seed),
            target=target,
            sample_rows=(max(40, int(sample_rows)) if sample_rows else None),
            out_dir=str(JOBS_DIR / "pending"),
            state="running",
            stage="load",
            started_at=time.time(),
        )
        with self._lock:
            self._jobs[job.id] = job
        job.out_dir = str(JOBS_DIR / job.id)
        thread = threading.Thread(target=self._run, args=(job, path), daemon=True)
        thread.start()
        return job

    def _run(self, job: TrainJob, path) -> None:
        try:
            from odontoca import train as train_mod

            job.stage = "load"
            frame, resolved_target = train_mod.load_frame_from_args(str(path), None, job.target)
            job.target = resolved_target
            if job.sample_rows and len(frame) > job.sample_rows:
                frame = frame.sample(n=job.sample_rows, random_state=job.seed).reset_index(drop=True)
                job.subsampled = True
            job.completed = 1

            job.stage = "prepare"
            group = None
            if job.task == "onset":
                frame, job.target = train_mod.prepare_onset_s1(frame)
                group = "HostID"
            job.n_rows = int(len(frame))
            job.completed = 2

            job.stage = "train"
            report = train_mod.run_training(
                frame,
                target=job.target,
                group=group,
                out_dir=job.out_dir,
                n_folds=job.folds,
                seed=job.seed,
            )
            job.n_rows = int(report.get("n_rows", job.n_rows or 0))
            job.n_events = int(report.get("events", 0))
            job.completed = 3

            job.stage = "report"
            job.report = report
            job.claim_level = str(report.get("claim_level", CLAIM_LEVEL))
            job.completed = len(STAGES)
            job.state = "done"
            job.finished_at = time.time()
        except Exception as exc:  # fail-closed: erro explícito, sem resultado falso
            job.state = "error"
            job.stage = "error"
            job.error = f"{type(exc).__name__}: {exc}"
            job.finished_at = time.time()


manager = TrainJobManager()
