# -*- coding: utf-8 -*-
"""
Evolution Cycles — Registro de Ciclos Evolutivos (R1..R46+)
===========================================================
Porta a disciplina de ciclos evolutivos documentados do OpenCode_Ecosystem
(evolution/evo-*.md, com scores por round) para um registro programático.

Cada ciclo (round) registra: objetivo, mudanças, score de qualidade (0-10),
lições aprendidas. O registro persiste em evolution/cycles.json e alimenta a
memória metacognitiva do ecossistema (lições viram reflexões no MetaBus).
"""

from __future__ import annotations

import glob
import copy
import math
import tempfile
from contextlib import contextmanager
from functools import wraps
from threading import RLock
import hashlib
import hmac
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from evolution.audit_gate import EvolutionAuditGate, git_head_commit

logger = logging.getLogger("evolution.cycles")

EVOLUTION_DIR = os.path.dirname(os.path.abspath(__file__))
# Isolamento de teste: respeita EVOLUTION_STATE_PATH se definida,
# senao usa o state_path real (evolution/cycles.json).
STATE_PATH = os.environ.get(
    "EVOLUTION_STATE_PATH",
    os.path.join(EVOLUTION_DIR, "cycles.json"),
)
# R611: a sequência de round_id NÃO pode colidir com specs já existentes.
# specs vive em <raiz>/specs (SPEC-935-R<id>-*.md); EVOLUTION_SPECS_PATH
# permite isolar o teste sem tocar o repo real.
SPECS_PATH = os.environ.get(
    "EVOLUTION_SPECS_PATH",
    os.path.join(os.path.dirname(EVOLUTION_DIR), "specs"),
)


@dataclass
class EvolutionCycle:
    round_id: str                 # ex.: "R47"
    objective: str
    changes: List[str] = field(default_factory=list)
    score: Optional[float] = None  # 0-10
    lessons: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    # --- Cadeia de custódia auditável (SPEC-935-R462) ---
    artifact_hashes: Dict[str, str] = field(default_factory=dict)  # sha256 por artefato
    external_verdict: Optional[Dict[str, Any]] = None  # quem auditou + passou/reprovou
    verifier_identity: str = ""  # identificador do auditor (≠ gerador)
    evidence_trail: List[str] = field(default_factory=list)  # specs/testes/scans
    audited: bool = False  # True se passou pelo gate externo
    legacy: bool = False  # True se ciclo pré-R462 sem auditoria formal
    # --- Âncoras externas de imutabilidade (endurecimento R462) ---
    merkle_root: str = ""  # hash agregado dos artefatos do ciclo
    origin_commit: str = ""  # commit git HEAD no momento do registro
    state_merkle_root: str = ""  # hash do cycles.json no momento do registro
    # --- Audit chain entre ciclos (R488, lição Bernstein RFC 2104) ---
    prev_state_merkle_root: str = ""  # state_merkle_root do ciclo ANTERIOR ancorado


def chain_state_merkle(prev_hex: str, state_bytes: bytes) -> str:
    """HMAC-SHA256 (RFC 2104) encadeando um estado ao hash do ciclo anterior.

    chain(prev, state) = HMAC-SHA256(key=prev, msg=state_bytes).

    Uso: cada ciclo âncora registra `prev_state_merkle_root` = state_merkle_root
    do ciclo anterior, e `state_merkle_root` = sha256 do cycles.json APÓS sua
    inserção. Rearranjar/remover/injetar ciclos quebra a cadeia verificável por
    `EvolutionRegistry.verify_state_chain()`.
    """
    return hmac.new(
        prev_hex.encode("utf-8"), state_bytes, digestmod=hashlib.sha256
    ).hexdigest()


def _synchronized(method):
    """Protege também a alocação do ID e a leitura das âncoras do ciclo."""
    @wraps(method)
    def locked(self, *args, **kwargs):
        with self._write_lock:
            return method(self, *args, **kwargs)
    return locked


class EvolutionRegistry:
    """Registro persistente de ciclos evolutivos do ecossistema."""

    def __init__(self, state_path: str | None = None):
        # R611: leitura reativa ao ambiente permite isolamento em teste sem
        # tocar o cycles.json real (EVOLUTION_STATE_PATH).
        self.state_path = os.fspath(state_path or os.environ.get(
            "EVOLUTION_STATE_PATH", STATE_PATH,
        ))
        self.cycles: List[EvolutionCycle] = []
        self._total_score: float = 0.0
        self._scored_count: int = 0
        self._write_lock = RLock()
        self._load()

    def _load(self) -> None:
        self._source_bytes = None
        self._raw_document = {"cycles": []}
        self._origins = {}
        self._unmodeled_reasons: Dict[int, str] = {}
        self._pending_migrations: Dict[int, Dict[str, Any]] = {}
        self.load_error = None
        self.cycles = []
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "rb") as f:
                    self._source_bytes = f.read()
                def reject_constant(value):
                    raise ValueError(f"Número JSON não finito: {value}")
                data = json.loads(self._source_bytes, parse_constant=reject_constant)
                if not isinstance(data, dict) or not isinstance(data.get("cycles"), list):
                    raise ValueError("Registro deve ser objeto com lista cycles")
                self._raw_document = data
                allowed = {"round_id", "objective", "changes", "score", "lessons",
                           "timestamp", "artifact_hashes", "external_verdict",
                           "verifier_identity", "evidence_trail", "audited", "legacy",
                           "merkle_root", "origin_commit", "state_merkle_root",
                           "prev_state_merkle_root"}
                raw_cycles = data.get("cycles", [])
            except (OSError, TypeError, ValueError) as exc:
                self.load_error = f"Registro ilegível ou inválido: {type(exc).__name__}"
                logger.warning(self.load_error)
                raw_cycles = []
            # Tolerância por entrada (lição R581): UMA entrada malformada ou em
            # formato antigo (id/titulo) não pode derrubar o registro inteiro —
            # antes, TypeError aqui zerava o histórico e o próximo record() o
            # sobrescrevia silenciosamente.
            self.cycles = []
            self._unmodeled_reasons = {}
            dropped = 0
            for index, cycle in enumerate(raw_cycles):
                if not isinstance(cycle, dict):
                    dropped += 1
                    self._unmodeled_reasons[index] = "entry_not_object"
                    continue
                try:
                    model = EvolutionCycle(
                            **{key: value for key, value in cycle.items()
                               if key in allowed}
                        )
                    self._validate_cycle(model)
                    self.cycles.append(model)
                    self._origins[id(model)] = (index, asdict(model))
                except (TypeError, ValueError) as exc:
                    dropped += 1
                    self._unmodeled_reasons[index] = self._cycle_error_code(exc)
            if dropped:
                logger.warning(
                    "EvolutionRegistry: %d entrada(s) ignorada(s) (formato antigo ou inválida); %d carregadas",
                    dropped, len(self.cycles),
                )
        else:
            self.cycles = []
        self._recompute_stats()

    @staticmethod
    def _cycle_error_code(error: Exception) -> str:
        """Classifica a falha estrutural sem copiar valores do registro."""
        message = str(error)
        if "Identidade ou objetivo" in message:
            return "invalid_identity_or_objective"
        if "Score inválido" in message:
            return "invalid_score"
        if "Timestamp inválido" in message:
            return "invalid_timestamp"
        if "Listas do ciclo" in message:
            return "invalid_list_fields"
        if "Metadados de custódia" in message:
            return "invalid_custody_fields"
        return "invalid_cycle_shape"

    @staticmethod
    def _validate_cycle(cycle: EvolutionCycle) -> None:
        if not isinstance(cycle.round_id, str) or not cycle.round_id or not isinstance(cycle.objective, str):
            raise ValueError("Identidade ou objetivo inválido")
        try:
            score_valid = cycle.score is None or type(cycle.score) in (int, float) and math.isfinite(cycle.score)
        except OverflowError:
            score_valid = False
        if not score_valid:
            raise ValueError("Score inválido")
        try:
            timestamp_valid = type(cycle.timestamp) in (int, float) and math.isfinite(cycle.timestamp)
        except OverflowError:
            timestamp_valid = False
        if not timestamp_valid:
            raise ValueError("Timestamp inválido")
        for value in (cycle.changes, cycle.lessons, cycle.evidence_trail):
            if not isinstance(value, list):
                raise ValueError("Listas do ciclo inválidas")
        if (not isinstance(cycle.artifact_hashes, dict)
                or cycle.external_verdict is not None and not isinstance(cycle.external_verdict, dict)
                or type(cycle.audited) is not bool or type(cycle.legacy) is not bool):
            raise ValueError("Metadados de custódia inválidos")

    def _recompute_stats(self) -> None:
        scored = [c.score for c in self.cycles if c.score is not None]
        self._total_score = sum(scored)
        self._scored_count = len(scored)

    @staticmethod
    def _canonical_legacy_json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)

    @staticmethod
    def _valid_finite_number(value: Any) -> bool:
        if type(value) not in (int, float):
            return False
        try:
            return math.isfinite(value)
        except OverflowError:
            return False

    @staticmethod
    def _legacy_text_list(value: Any, field_name: str, reasons: set[str]) -> List[str]:
        """Projection text-only determinística; o objeto original nunca some."""
        if isinstance(value, list):
            result = []
            for item in value:
                if isinstance(item, str):
                    result.append(item)
                else:
                    result.append(EvolutionRegistry._canonical_legacy_json(item))
                    reasons.add(f"{field_name}_item_serialized")
            return result
        if value is None:
            reasons.add(f"{field_name}_missing")
            return []
        if field_name == "changes" and isinstance(value, dict) and isinstance(value.get("changes"), list):
            reasons.add("changes_not_list")
            return EvolutionRegistry._legacy_text_list(value["changes"], field_name, reasons)
        if isinstance(value, str):
            reasons.add(f"{field_name}_scalar_wrapped")
            return [value]
        reasons.add(f"{field_name}_serialized")
        return [EvolutionRegistry._canonical_legacy_json(value)]

    @staticmethod
    def _legacy_timestamp(value: Any, reasons: set[str]) -> float:
        if EvolutionRegistry._valid_finite_number(value):
            return float(value)
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                reasons.add("timestamp_iso8601_normalized")
                return parsed.timestamp()
            except (ValueError, OverflowError, OSError):
                reasons.add("timestamp_invalid")
                return 0.0
        reasons.add("timestamp_missing" if value is None else "timestamp_invalid")
        return 0.0

    def _project_legacy_entry(self, raw: Dict[str, Any], index: int,
                              used_round_ids: set[str]) -> tuple[EvolutionCycle, List[str], str]:
        """Constrói projeção tipada; preserva o payload integral na extensão R983."""
        reasons = {self._unmodeled_reasons.get(index, "legacy_shape_migrated")}
        nested = raw.get("changes") if isinstance(raw.get("changes"), dict) else {}

        round_id = raw.get("round_id")
        if not isinstance(round_id, str) or not round_id.strip():
            old_id = raw.get("id")
            if isinstance(old_id, str) and old_id.strip():
                round_id = old_id.strip()
                reasons.add("legacy_identity_mapped")
            else:
                digest = hashlib.sha256(self._canonical_legacy_json(raw).encode("utf-8")).hexdigest()
                round_id = f"legacy-entry-{index}-{digest[:12]}"
                reasons.add("synthetic_identity")
        if round_id in used_round_ids:
            digest = hashlib.sha256(self._canonical_legacy_json(raw).encode("utf-8")).hexdigest()
            stem = f"legacy-entry-{index}-{digest[:12]}"
            round_id = stem
            suffix = 1
            while round_id in used_round_ids:
                round_id = f"{stem}-{suffix}"
                suffix += 1
            reasons.add("synthetic_identity")
        used_round_ids.add(round_id)

        objective = raw.get("objective")
        if not isinstance(objective, str) or not objective.strip():
            title = raw.get("title", raw.get("titulo", nested.get("title")))
            if isinstance(title, str) and title.strip():
                objective = title.strip()
                reasons.add("legacy_objective_mapped")
            else:
                objective = f"Legacy record {round_id}"
                reasons.add("synthetic_objective")

        changes = self._legacy_text_list(raw.get("changes"), "changes", reasons)
        lessons = self._legacy_text_list(raw.get("lessons"), "lessons", reasons)
        evidence = self._legacy_text_list(raw.get("evidence_trail"), "evidence_trail", reasons)

        score = raw.get("score", nested.get("score"))
        if score is not None and not self._valid_finite_number(score):
            score = None
            reasons.add("score_invalid")

        timestamp = self._legacy_timestamp(raw.get("timestamp", nested.get("timestamp")), reasons)
        artifact_hashes = raw.get("artifact_hashes")
        if not isinstance(artifact_hashes, dict):
            artifact_hashes = {}
            if raw.get("artifact_hashes") is not None:
                reasons.add("artifact_hashes_invalid")
        external_verdict = raw.get("external_verdict")
        if external_verdict is not None and not isinstance(external_verdict, dict):
            external_verdict = None
            reasons.add("external_verdict_invalid")
        verifier = raw.get("verifier_identity", "")
        if not isinstance(verifier, str):
            verifier = ""
            reasons.add("verifier_identity_invalid")
        audited = raw.get("audited", False)
        if type(audited) is not bool:
            audited = False
            reasons.add("audited_invalid")
        legacy = raw.get("legacy", True)
        if type(legacy) is not bool:
            legacy = True
            reasons.add("legacy_flag_invalid")

        string_fields = {}
        for name in ("merkle_root", "origin_commit", "state_merkle_root", "prev_state_merkle_root"):
            value = raw.get(name, "")
            if not isinstance(value, str):
                value = ""
                reasons.add(f"{name}_invalid")
            string_fields[name] = value

        model = EvolutionCycle(
            round_id=round_id,
            objective=objective,
            changes=changes,
            score=score,
            lessons=lessons,
            timestamp=timestamp,
            artifact_hashes=artifact_hashes,
            external_verdict=external_verdict,
            verifier_identity=verifier,
            evidence_trail=evidence,
            audited=audited,
            legacy=legacy,
            **string_fields,
        )
        self._validate_cycle(model)
        canonical_hash = hashlib.sha256(
            self._canonical_legacy_json(raw).encode("utf-8")
        ).hexdigest()
        return model, sorted(reasons), canonical_hash

    def preview_legacy_migration(self) -> Dict[str, Any]:
        """Relatório somente leitura da projeção R983; não grava nem altera memória."""
        used_ids = {cycle.round_id for cycle in self.cycles}
        entries = []
        migratable = 0
        unmigratable = 0
        for index in sorted(self._unmodeled_reasons):
            raw = self._raw_document.get("cycles", [])[index]
            if not isinstance(raw, dict):
                entries.append({"source_index": index,
                                "reason_codes": ["entry_not_object"],
                                "migratable": False})
                unmigratable += 1
                continue
            model, reasons, source_hash = self._project_legacy_entry(raw, index, used_ids)
            entries.append({
                "source_index": index,
                "round_id": model.round_id,
                "reason_codes": reasons,
                "source_sha256": source_hash,
                "migratable": True,
            })
            migratable += 1
        return {
            "status": "preview",
            "modelled_count": len(self.cycles),
            "unmodelled_count": len(self._unmodeled_reasons),
            "migratable_count": migratable,
            "unmigratable_count": unmigratable,
            "entries": entries,
            "source_sha256": hashlib.sha256(self._source_bytes or b"").hexdigest(),
            "writes_performed": False,
        }

    @staticmethod
    def _create_legacy_backup(path: str, source_path: str,
                              source_bytes: bytes) -> tuple[str, bool]:
        """Cria backup exclusivo byte-a-byte; conflito de backup bloqueia."""
        backup = os.path.abspath(path)
        source = os.path.abspath(source_path)
        if (os.path.islink(backup) or os.path.islink(source)
                or backup == source):
            raise ValueError("caminho de backup inválido")
        parent = os.path.dirname(backup)
        if not os.path.isdir(parent) or os.path.islink(parent):
            raise ValueError("diretório de backup ausente ou symlink")
        parent_path = Path(parent)
        if any(part.is_symlink() for part in (parent_path, *parent_path.parents)):
            raise ValueError("componente symlink no caminho de backup")
        digest = hashlib.sha256(source_bytes).hexdigest()
        try:
            fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        except FileExistsError:
            with open(backup, "rb") as stream:
                existing = stream.read()
            if existing != source_bytes:
                raise FileExistsError("backup existente diverge dos bytes de origem")
            return digest, False
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(source_bytes)
                stream.flush()
                os.fsync(stream.fileno())
        except Exception:
            try:
                os.unlink(backup)
            except FileNotFoundError:
                pass
            raise
        return digest, True

    def migrate_legacy_entries(self, backup_path: str | os.PathLike | None = None) -> Dict[str, Any]:
        """Migra explicitamente objetos históricos, com backup e proveniência R983.

        O construtor e o doctor nunca chamam este método. Publicação e controle
        de concorrência reutilizam ``save()``; qualquer erro restaura a memória
        da instância, enquanto o backup byte-a-byte permanece como evidência.
        """
        preview = self.preview_legacy_migration()
        if preview["migratable_count"] == 0:
            return {
                **preview,
                "status": "already_migrated" if preview["unmodelled_count"] == 0 else "no_migratable_entries",
                "migrated_count": 0,
                "remaining_unmodelled_count": preview["unmodelled_count"],
            }
        if self.load_error or self._source_bytes is None:
            raise ValueError((self.load_error or "fonte de histórico ausente") + "; migração recusada")

        with open(self.state_path, "rb") as source:
            current_source = source.read()
        if current_source != self._source_bytes:
            raise RuntimeError("Registro mudou concorrentemente; recarregue antes de migrar")

        target_backup = os.fspath(backup_path or (self.state_path + ".pre-r983"))
        backup_hash, backup_created = self._create_legacy_backup(
            target_backup, self.state_path, self._source_bytes
        )
        backup_reference = os.path.relpath(
            os.path.abspath(target_backup), os.path.dirname(os.path.abspath(self.state_path))
        ).replace(os.sep, "/")

        used_ids = {cycle.round_id for cycle in self.cycles}
        candidates = []
        for index in sorted(self._unmodeled_reasons):
            raw = self._raw_document.get("cycles", [])[index]
            if isinstance(raw, dict):
                model, reasons, source_hash = self._project_legacy_entry(raw, index, used_ids)
                candidates.append((index, raw, model, reasons, source_hash))

        previous_cycles = list(self.cycles)
        previous_origins = dict(self._origins)
        previous_pending = dict(self._pending_migrations)
        previous_unmodeled = dict(self._unmodeled_reasons)
        try:
            for index, raw, model, reasons, source_hash in candidates:
                self.cycles.append(model)
                self._origins[id(model)] = (index, asdict(model))
                self._pending_migrations[index] = {
                    "migration_id": "R983-v1",
                    "source_index": index,
                    "round_id": model.round_id,
                    "backup_path": backup_reference,
                    "backup_sha256": backup_hash,
                    "source_sha256": source_hash,
                    "reason_codes": reasons,
                }
            self.save()
        except Exception:
            self.cycles = previous_cycles
            self._origins = previous_origins
            self._pending_migrations = previous_pending
            self._unmodeled_reasons = previous_unmodeled
            self._recompute_stats()
            raise

        return {
            "status": "migrated",
            "migrated_count": len(candidates),
            "remaining_unmodelled_count": len(self._unmodeled_reasons),
            "backup_path": os.path.abspath(target_backup),
            "backup_sha256": backup_hash,
            "backup_created": backup_created,
            "source_sha256": preview["source_sha256"],
            "entry_summaries": [
                {"source_index": index, "round_id": model.round_id,
                 "reason_codes": reasons, "source_sha256": source_hash}
                for index, _raw, model, reasons, source_hash in candidates
            ],
            "writes_performed": True,
        }

    @contextmanager
    def _locked_file(self):
        # Advisory writer lock; every writer still checks the exact loaded bytes.
        with open(self.state_path + ".lock", "a+b") as lock:
            if os.name == "nt":
                import msvcrt
                lock.seek(0)
                if not lock.read(1):
                    lock.write(b"0"); lock.flush()
                lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
                try: yield
                finally:
                    lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock, fcntl.LOCK_EX)
                try: yield
                finally: fcntl.flock(lock, fcntl.LOCK_UN)

    def save(self) -> None:
        with self._write_lock:
            if self.load_error:
                raise ValueError(self.load_error + "; gravação recusada")
            by_index = {self._origins[id(c)][0]: c for c in self.cycles if id(c) in self._origins}
            loaded_indices = {index for index, _ in self._origins.values()}
            migration_indices = set(self._pending_migrations)
            document = copy.deepcopy(self._raw_document)
            rows, origins = [], {}
            migration_records = []
            def append(model, raw, source_index=None):
                self._validate_cycle(model)
                current = asdict(model)
                migration = self._pending_migrations.get(source_index)
                # Migrated cycle rows return to the canonical field set. The
                # old payload is preserved in the top-level migration ledger.
                row = dict(current) if migration is not None else dict(raw)
                previous = self._origins.get(id(model), (None, None))[1]
                if migration is None and previous != current:
                    row.update(current)
                if migration is not None:
                    migration_records.append(copy.deepcopy(migration))
                origins[id(model)] = (len(rows), current)
                rows.append(row)
            for index, raw in enumerate(document["cycles"]):
                if index in by_index:
                    append(by_index[index], raw, index)
                elif index not in loaded_indices:
                    rows.append(raw)  # Preserve unmodeled historical entries.
            for cycle in self.cycles:
                if id(cycle) not in self._origins:
                    append(cycle, {})
            if migration_records:
                existing_migrations = document.get("legacy_migrations", [])
                if not isinstance(existing_migrations, list):
                    raise ValueError("legacy_migrations existente não é uma lista; gravação recusada")
                document["legacy_migrations"] = existing_migrations + migration_records
            document["cycles"] = rows
            payload = (json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
            with self._locked_file():
                current = None
                if os.path.exists(self.state_path):
                    with open(self.state_path, "rb") as stream:
                        current = stream.read()
                if current != self._source_bytes:
                    raise RuntimeError("Registro mudou concorrentemente; recarregue antes de gravar")
                parent = os.path.dirname(os.path.abspath(self.state_path))
                fd, temporary = tempfile.mkstemp(dir=parent, prefix=".cycles-", suffix=".tmp")
                try:
                    with os.fdopen(fd, "wb") as stream:
                        if current is not None:
                            os.chmod(temporary, os.stat(self.state_path).st_mode & 0o777)
                        stream.write(payload); stream.flush(); os.fsync(stream.fileno())
                    os.replace(temporary, self.state_path)
                finally:
                    if os.path.exists(temporary): os.unlink(temporary)
            self._source_bytes, self._raw_document, self._origins = payload, document, origins
            self._unmodeled_reasons = {
                index: reason for index, reason in self._unmodeled_reasons.items()
                if index not in migration_indices
            }
            self._pending_migrations = {}
            self._recompute_stats()

    def _append_cycle(self, cycle: EvolutionCycle) -> EvolutionCycle:
        with self._write_lock:
            self._validate_cycle(cycle)
            self.cycles.append(cycle)
            try:
                self.save()
            except Exception:
                self.cycles.pop()
                self._recompute_stats()
                raise
            return cycle

    def next_round_id(self) -> str:
        max_n = 46  # R1..R46 documentados no ecossistema original
        identifiers = [c.round_id for c in self.cycles]
        # Preservar um registro histórico também reserva sua identidade, mesmo
        # quando os demais campos não satisfazem o modelo atual.
        identifiers.extend(row.get("round_id", row.get("id", ""))
                           for row in self._raw_document["cycles"] if isinstance(row, dict))
        for identifier in identifiers:
            m = re.match(r"R(\d+)", identifier) if isinstance(identifier, str) else None
            if m:
                max_n = max(max_n, int(m.group(1)))
        # R611: specs/ também reserva numerais — scannear o diretório evita
        # colidir com uma spec existente (bug observado: ciclo virou R607
        # quando specs/SPEC-935-R607.md já existia).
        specs_dir = os.environ.get("EVOLUTION_SPECS_PATH", SPECS_PATH)
        spec_dir = glob.glob(os.path.join(specs_dir, "SPEC-935-R*.md"))
        for path in spec_dir:
            m = re.search(r"R(\d+)", os.path.basename(path))
            if m:
                max_n = max(max_n, int(m.group(1)))
        return f"R{max_n + 1}"

    @_synchronized
    def record(self, objective: str, changes: List[str],
               score: Optional[float] = None,
               lessons: Optional[List[str]] = None,
               round_id: Optional[str] = None) -> EvolutionCycle:
        cycle = EvolutionCycle(
            round_id=round_id or self.next_round_id(),
            objective=objective, changes=changes,
            score=score, lessons=lessons or [],
            legacy=True,  # sem auditoria externa formal => ciclo legado (R462)
        )
        return self._append_cycle(cycle)

    def _anchor(self, artifact_hashes: Dict[str, str],
                state_merkle_root: Optional[str] = None) -> Dict[str, str]:
        """Constrói âncoras externas de imutabilidade do ciclo.

        Retorna {commit, merkle, state} — commit git HEAD atual, merkle_root
        dos artefatos registrados e (opcional) hash do estado do cycles.json
        no momento do registro. Ancorar o estado prova em que 'fotografia' do
        registro o ciclo foi inserido (imutabilidade do estado).
        """
        gate = EvolutionAuditGate()
        return {
            "commit": git_head_commit(),
            "merkle": gate.merkle_root(artifact_hashes),
            "state": state_merkle_root or "",
        }

    @_synchronized
    def record_audited(self, objective: str, changes: List[str],
                       artifact_hashes: Dict[str, str],
                       external_verdict: Dict[str, Any],
                       verifier_identity: str,
                       generator_identity: str,
                       evidence_trail: Optional[List[str]] = None,
                       round_id: Optional[str] = None,
                       score: Optional[float] = None,
                       lessons: Optional[List[str]] = None,
                       anchor_state: bool = True) -> EvolutionCycle:
        """Registra um ciclo que JÁ passou pelo EvolutionAuditGate (auditado).

        Fail-closed: exige external_verdict.passed=True e verifier distinto do
        gerador (Pelo contrario, ver `record_rejected`). Endurecido: ancora
        automaticamente o commit git HEAD, o merkle_root dos artefatos e o hash
        do estado do cycles.json (imutabilidade composita) se `anchor_state`.
        """
        passed = bool(external_verdict and external_verdict.get("passed") is True)
        verified_by_other = bool(verifier_identity
                                 and verifier_identity != generator_identity)
        if not passed or not verified_by_other:
            raise PermissionError(
                "Ciclo recusado: exige external_verdict.passed=True e "
                "verifier_identity distinto do gerador. Use record_rejected() "
                "para persistir um rastro de rejeicao. (SPEC-935-R462 gate)"
            )

        anchors = self._anchor(artifact_hashes)
        state_hash = ""
        if anchor_state and self.state_path:
            try:
                with open(self.state_path, "rb") as f:
                    state_hash = EvolutionAuditGate().hash_state(f.read())
            except OSError:
                state_hash = ""

        cycle = EvolutionCycle(
            round_id=round_id or self.next_round_id(),
            objective=objective, changes=changes,
            score=score, lessons=lessons or [],
            artifact_hashes=dict(artifact_hashes),
            external_verdict=dict(external_verdict),
            verifier_identity=verifier_identity,
            evidence_trail=list(evidence_trail or []),
            audited=True,
            legacy=False,
            merkle_root=anchors["merkle"] or state_hash,
            origin_commit=anchors["commit"],
            state_merkle_root=state_hash,
        )
        return self._append_cycle(cycle)

    @_synchronized
    def record_rejected(self, objective: str, changes: List[str],
                        reason: str,
                        verifier_identity: str,
                        generator_identity: str,
                        round_id: Optional[str] = None) -> EvolutionCycle:
        """Persiste um veredito REPROVADO como rastro auditável (reject trail).

        Diferente de `record_audited`, que levanta PermissionError, este metodo
        REGISTRA o ciclo com external_verdict.passed=False — mantendo a
        evidenci a de que uma tentativa ocorreu e foi reprovada pelo gate. E
        auditabilidade da falha, nao apenas acerto. (SPEC-935-R462)
        """
        cycle = EvolutionCycle(
            round_id=round_id or self.next_round_id(),
            objective=objective, changes=changes,
            external_verdict={"passed": False, "reason": reason,
                              "verifier": verifier_identity},
            verifier_identity=verifier_identity,
            audited=False,
            legacy=False,
        )
        return self._append_cycle(cycle)

    def custody_metric(self) -> Dict[str, Any]:
        """Métrica de Custódia Auditável (SPEC-935-R462 / gate de aceitação).

        Custódia(%) = (ciclos com artifact_hashes ∧ external_verdict ∧
                       verifier_identity ≠ '') / total × 100.
        Baseline medido: 0,0%. Alvo pós-R462: ≥ 90%.
        """
        total = len(self.cycles)
        if total == 0:
            return {"audited": 0, "total": 0, "pct": 0.0, "rejected": 0,
                    "tampered": 0, "legacy": 0, "anchored": 0}
        audited = sum(1 for c in self.cycles
                      if c.audited
                      and c.artifact_hashes
                      and c.external_verdict
                      and c.verifier_identity
                      and c.external_verdict.get("passed") is True)
        # 'anchored' = auditado E com merkle_root (imutabilidade composita)
        anchored = sum(1 for c in self.cycles
                       if c.audited and c.merkle_root
                       and c.external_verdict
                       and c.external_verdict.get("passed") is True)
        legacy = sum(1 for c in self.cycles if c.legacy)
        tampered = sum(1 for c in self.cycles
                       if c.external_verdict
                       and c.external_verdict.get("tampered") is True)
        rejected_trail = sum(1 for c in self.cycles
                             if c.external_verdict
                             and c.external_verdict.get("passed") is False)
        return {
            "audited": audited,
            "total": total,
            "pct": round(100.0 * audited / total, 1),
            "anchored": anchored,
            "rejected": rejected_trail,
            "tampered": tampered,
            "legacy": legacy,
        }

    def custody_recent(self, since_round: str = "R462") -> Dict[str, Any]:
        """Custódia sobre ciclos NOVOS (a partir de `since_round`). Mede a
        fração dos ciclos gerados sob o regime auditado que realmente passaram
        pelo gate externo. É a medida honesta da melhoria estrutural (R462)."""
        recent = [c for c in self.cycles
                  if self._round_num(c.round_id) >= self._round_num(since_round)]
        total = len(recent)
        if total == 0:
            return {"audited": 0, "total": 0, "pct": 0.0}
        audited = sum(1 for c in recent
                      if c.audited and c.artifact_hashes and c.external_verdict
                      and c.verifier_identity
                      and c.external_verdict.get("passed") is True)
        return {
            "audited": audited,
            "total": total,
            "pct": round(100.0 * audited / total, 1),
        }

    def _round_num(self, round_id: str) -> int:
        m = re.match(r"R(\d+)", round_id or "")
        return int(m.group(1)) if m else -1

    def verify_state_chain(self) -> Dict[str, Any]:
        """Verifica a cadeia de audit entre ciclos (R488, lição Bernstein).

        Percorre os ciclos EM ORDEM; para cada ciclo com âncora
        (`prev_state_merkle_root` ou `state_merkle_root` preenchidos):
        - primeiro nó âncora: `prev` deve ser "" (raiz da cadeia);
        - nós seguintes: `prev` deve ser igual ao `state_merkle_root` do último
          nó âncora visto;
        - nós cegos (sem âncoras) são tolerados e não quebram a cadeia.

        Retorna {"ok", "size", "anchored", "broken"} onde `broken` lista os
        round_ids com referências inconsistentes. Isto não recalcula o conteúdo
        histórico nem autentica os campos do ciclo. Remover a última âncora ou
        alterar conteúdo sem mudar referências pode não ser detectado; `ok`
        significa somente consistência dos elos declarados.
        """
        last_state = ""
        broken: List[Dict[str, Any]] = []
        in_chain = 0
        anchored = 0
        for cycle in self.cycles:
            prev = cycle.prev_state_merkle_root or ""
            state = cycle.state_merkle_root or ""
            if state:
                anchored += 1
            if not (prev or state):
                continue  # nó cego
            in_chain += 1
            if prev and last_state == "" and prev != "":
                broken.append({"round_id": cycle.round_id, "reason": "prev sem âncora anterior"})
            elif prev and prev != last_state:
                broken.append({"round_id": cycle.round_id, "reason": "prev != state do ciclo anterior"})
            if state:
                last_state = state
        return {
            "ok": not broken,
            "size": in_chain,
            "anchored": anchored,
            "broken": broken,
        }


    def history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return [asdict(c) for c in self.cycles[-limit:]]

    def average_score(self) -> Optional[float]:
        """Média móvel dos scores dos ciclos com score (G5 — R438).

        Esta média **não é gate de qualidade**. O gate real é
        `SpecVerifier` + `GradingHead` + `confidence_calibrator` (verificado
        por `SpecRegistry` e `loop_spec_registry`), não a média histórica.
        A média serve apenas como indicador de tendência evolutiva.
        """
        if self._scored_count > 0:
            return round(self._total_score / self._scored_count, 2)
        return None

    def load_documented_cycles(self) -> List[Dict[str, str]]:
        """Indexa os ciclos documentados em evolution/evo-*.md (portados do original)."""
        docs = []
        for path in sorted(glob.glob(os.path.join(EVOLUTION_DIR, "evo-*.md"))):
            name = os.path.basename(path)
            title = ""
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("#"):
                            title = line.lstrip("# ").strip()
                            break
            except OSError:
                pass
            docs.append({"file": name, "title": title})
        return docs


# Singleton
evolution_registry = EvolutionRegistry()
