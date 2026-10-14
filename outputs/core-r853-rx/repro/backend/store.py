"""store.py — persistência SQLite da reprodução ODONTOCA - Prof. Marcelo Claro (SPEC-935-R874).

Persiste sessões, imagens, anotações, jobs, lotes, locks de edição, feedback e os
relatórios de validação. Os dados semeados são de **DEMONSTRAÇÃO SINTÉTICA**
(gerados proceduralmente), destinados apenas a exercitar a interface — NÃO são
dados clínicos reais nem o banco do alvo original.

Banco: `RX_ADMIN_DB` (default `~/.cache/rx-admin/admin.db`). A conexão é por
thread (thread-local) e o caminho é relido a cada chamada, de modo que o teste
possa apontar para um arquivo temporário e a persistência sobreviva a reabertura.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import secrets
import sqlite3
import threading
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw

_DEFAULT = Path.home() / ".cache" / "rx-admin" / "admin.db"
_local = threading.local()

SOURCES = ["dental_dataset", "dental31", "dentex", "teeth_segmentation", "other"]
QUADRANTS = ["Q1", "Q2", "Q3", "Q4"]
FDI = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28,
       38, 37, 36, 35, 34, 33, 32, 31, 41, 42, 43, 44, 45, 46, 47, 48]
FINDINGS = ["caries", "periapical_lesion", "impacted_tooth"]
ADDITIONAL = [
    "caries", "crown", "filling", "implant", "malaligned", "mandibular_canal",
    "missing_teeth", "periapical_lesion", "retained_root", "root_canal_treatment",
    "root_piece", "impacted_tooth", "maxillary_sinus", "bone_loss", "fracture_teeth",
    "permanent_teeth", "supra_eruption", "tad", "abutment", "attrition",
    "bone_defect", "gingival_former", "metal_band", "orthodontic_brackets",
    "permanent_retainer", "post_core", "plating", "wire", "cyst",
    "root_resorption", "primary_teeth",
]
PAGE_SIZE = 10


def _db_path() -> Path:
    return Path(os.environ.get("RX_ADMIN_DB") or _DEFAULT)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def conn() -> sqlite3.Connection:
    path = _db_path()
    current = getattr(_local, "conn", None)
    if current is None or getattr(_local, "path", None) != str(path):
        if current is not None:
            try:
                current.close()
            except Exception:  # noqa: BLE001
                pass
        path.parent.mkdir(parents=True, exist_ok=True)
        new = sqlite3.connect(str(path), check_same_thread=False)
        new.row_factory = sqlite3.Row
        new.execute("PRAGMA journal_mode=WAL")
        _local.conn, _local.path = new, str(path)
        _init(new)
        _seed(new)
    return _local.conn


def reset() -> None:
    """Fecha a conexão da thread; a próxima chamada reabre o MESMO arquivo."""
    current = getattr(_local, "conn", None)
    if current is not None:
        try:
            current.close()
        except Exception:  # noqa: BLE001
            pass
    _local.conn, _local.path = None, None


# --- schema ------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS sessions(sid TEXT PRIMARY KEY, username TEXT, role TEXT,
    is_admin INT, csrf TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS images(image_id TEXT PRIMARY KEY, source_database TEXT,
    width INT, height INT, revision INT, created_at TEXT, reviewed INT, reviewer TEXT,
    age_label TEXT, age_confidence REAL, age_reviewed INT, age_reviewed_by TEXT);
CREATE TABLE IF NOT EXISTS annotations(id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id TEXT, grp TEXT, label TEXT, segmented INT, source TEXT);
CREATE TABLE IF NOT EXISTS jobs(job_id TEXT PRIMARY KEY, kind TEXT, status TEXT,
    current INT, total INT, message TEXT, image_id TEXT, batch_id TEXT,
    created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS batches(batch_id TEXT PRIMARY KEY, status TEXT,
    current INT, total INT, succeeded INT, skipped INT, failed INT, message TEXT,
    created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS edit_locks(image_id TEXT PRIMARY KEY, editing_by TEXT,
    updated_at TEXT);
CREATE TABLE IF NOT EXISTS feedback(image_id TEXT PRIMARY KEY, revision INT,
    document TEXT, baseline TEXT, saved_at TEXT);
CREATE TABLE IF NOT EXISTS models(slug TEXT PRIMARY KEY, data TEXT);
CREATE TABLE IF NOT EXISTS class_deltas(grp TEXT, label TEXT, pending_delta INT,
    review_delta INT, PRIMARY KEY(grp, label));
"""


def _init(c: sqlite3.Connection) -> None:
    c.executescript(_SCHEMA)
    c.commit()


# --- seed (dados de demonstração explícitos) ---------------------------------

def _seed(c: sqlite3.Connection) -> None:
    if c.execute("SELECT value FROM meta WHERE key='seeded'").fetchone():
        return
    base_ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(12):
        image_id = f"rx-{i + 1:04d}"
        width, height = 1200 + 20 * i, 600
        reviewed = 1 if i < 7 else 0
        age_labels = ["child", "adult", "uncertain"]
        age_label = age_labels[i % 3]
        age_conf = round(0.62 + 0.03 * (i % 9), 3)
        created = (base_ts + timedelta(hours=i)).isoformat()
        c.execute(
            "INSERT INTO images(image_id,source_database,width,height,revision,created_at,"
            "reviewed,reviewer,age_label,age_confidence,age_reviewed,age_reviewed_by) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (image_id, SOURCES[i % len(SOURCES)], width, height, i, created,
             reviewed, (f"revisor{i % 3 + 1}" if reviewed else None),
             age_label, age_conf, reviewed, (f"revisor{i % 3 + 1}" if reviewed else None)),
        )
        seg_teeth = 1 if reviewed else (1 if i % 2 == 0 else 0)
        rows: list[tuple[str, str, int, str]] = []
        for q in QUADRANTS:
            rows.append(("quadrants", q, seg_teeth, "human" if reviewed else "ai"))
        for fdi in FDI[:16]:
            rows.append(("teeth", str(fdi), seg_teeth, "human" if reviewed else "ai"))
        if i % 2 == 0:
            rows.append(("findings", "caries", seg_teeth, "ai"))
        if i % 3 == 0:
            rows.append(("findings", "periapical_lesion", seg_teeth, "ai"))
        if i % 4 == 0:
            rows.append(("additional", "crown", 0, "ai"))
        if i % 5 == 0:
            rows.append(("additional", "implant", 0, "ai"))
        for grp, label, seg, src in rows:
            c.execute("INSERT INTO annotations(image_id,grp,label,segmented,source) "
                      "VALUES(?,?,?,?,?)", (image_id, grp, label, seg, src))
    c.executemany("INSERT INTO class_deltas(grp,label,pending_delta,review_delta) VALUES(?,?,?,?)", [
        ("findings", "caries", 2, 1), ("additional", "crown", 1, 0),
        ("teeth", "18", 0, 1), ("quadrants", "Q1", 0, 2),
    ])
    for slug, data in _model_seed().items():
        c.execute("INSERT INTO models(slug,data) VALUES(?,?)",
                  (slug, json.dumps(data, ensure_ascii=False)))
    c.execute("INSERT INTO meta(key,value) VALUES('seeded','1')")
    c.commit()


def _model_seed() -> dict:
    def plots(slug, names):
        return [{"name": n, "url": f"/validacao/media/{slug}/{k}.png"}
                for k, n in enumerate(names)]

    def examples(slug, ids):
        return [{"id": i,
                 "original": f"/admin/api/images/{i}/image",
                 "annotations": f"/validacao/annotations/{slug}/{i}.json",
                 "review_url": f"/?review={i}"} for i in ids]

    teeth_classes = [
        {"class": "tooth", "support": 96, "precision": 0.91, "recall_sensitivity": 0.89,
         "ap50": 0.93, "pixel_iou_jaccard": 0.86, "pixel_dice": 0.92, "boundary_f1": 0.81},
        {"class": "impacted_tooth", "support": 12, "precision": 0.84, "recall_sensitivity": 0.8,
         "ap50": 0.88, "pixel_iou_jaccard": 0.79, "pixel_dice": 0.87, "boundary_f1": 0.72},
    ]
    det_classes = [
        {"class": "caries", "support": 40, "precision": 0.78, "recall_sensitivity": 0.74,
         "f1": 0.76, "ap50": 0.82, "map50_95": 0.58, "roc_auc_image_presence": 0.9},
        {"class": "periapical_lesion", "support": 22, "precision": 0.7, "recall_sensitivity": 0.68,
         "f1": 0.69, "ap50": 0.75, "map50_95": 0.49, "roc_auc_image_presence": 0.86},
        {"class": "impacted_tooth", "support": 12, "precision": 0.83, "recall_sensitivity": 0.79,
         "f1": 0.81, "ap50": 0.86, "map50_95": 0.61, "roc_auc_image_presence": 0.93},
    ]
    add_classes = [
        {"class": "crown", "support": 30, "precision": 0.8, "recall_sensitivity": 0.77,
         "f1": 0.78, "ap50": 0.83, "map50_95": 0.55, "roc_auc_image_presence": 0.9},
        {"class": "implant", "support": 14, "precision": 0.86, "recall_sensitivity": 0.82,
         "f1": 0.84, "ap50": 0.89, "map50_95": 0.63, "roc_auc_image_presence": 0.94},
    ]
    ex_ids = ["rx-0001", "rx-0002", "rx-0003"]
    return {
        "teeth": {
            "slug": "teeth", "name": "Segmentação dentária", "eyebrow": "Segmentação",
            "kind": "segment", "accent": "teal",
            "description": "Contorno de cada dente para localização e impressão.",
            "progress": {"processed": 180, "total": 180, "status": "complete"},
            "training_validation": {"epoch": 87, "epochs_completed": 100, "images": 1200,
                                    "metrics": {"map50": 0.8778, "map50_95": 0.612,
                                                "precision": 0.83, "recall_sensitivity": 0.81}},
            "summary": {"task": "segment", "images": 180, "ground_truth_instances": 2880,
                        "metrics": {"map50": 0.87, "map50_95": 0.61,
                                    "macro_pixel_dice": 0.91, "macro_pixel_iou_jaccard": 0.84}},
            "per_class": teeth_classes,
            "plots": plots("teeth", ["Matriz de confusão", "Curva precisão-recall"]),
            "examples_all": examples("teeth", ex_ids),
        },
        "fdi": {
            "slug": "fdi", "name": "FDI / numeração", "eyebrow": "Numeração",
            "kind": "detection", "accent": "blue",
            "description": "Identificação do dente pela notação FDI 11–48.",
            "progress": {"processed": 200, "total": 200, "status": "complete"},
            "training_validation": {"epoch": 64, "epochs_completed": 80, "images": 900,
                                    "metrics": {"map50": 0.81, "map50_95": 0.57,
                                                "precision": 0.79, "recall_sensitivity": 0.77}},
            "summary": {"task": "detect", "images": 200, "ground_truth_instances": 3200,
                        "metrics": {"map50": 0.81, "map50_95": 0.57,
                                    "precision": 0.79, "recall_sensitivity": 0.77}},
            "per_class": det_classes,
            "plots": plots("fdi", ["Matriz de confusão"]),
            "examples_all": examples("fdi", ex_ids),
        },
        "findings": {
            "slug": "findings", "name": "Achados (DENTEX)", "eyebrow": "Achados clínicos",
            "kind": "detection", "accent": "orange",
            "description": "Cárie, lesão periapical e dente impactado (DENTEX).",
            "progress": {"processed": 150, "total": 150, "status": "complete"},
            "training_validation": {"epoch": 72, "epochs_completed": 100, "images": 705,
                                    "metrics": {"map50": 0.76, "map50_95": 0.5,
                                                "precision": 0.72, "recall_sensitivity": 0.7}},
            "summary": {"task": "detect", "images": 150, "ground_truth_instances": 74,
                        "metrics": {"map50": 0.76, "map50_95": 0.5,
                                    "precision": 0.72, "recall_sensitivity": 0.7}},
            "per_class": det_classes,
            "plots": plots("findings", ["Matriz de confusão", "Curva precisão-recall"]),
            "examples_all": examples("findings", ex_ids),
        },
        "dental31": {
            "slug": "dental31", "name": "Dental31 (adicional)", "eyebrow": "Informação adicional",
            "kind": "detection", "accent": "purple",
            "description": "31 classes adicionais (Dental31) — requer revisão humana.",
            "progress": {"processed": 90, "total": 120, "status": "processing"},
            "training_validation": {"epoch": 40, "epochs_completed": 80, "images": 1400,
                                    "metrics": {"map50": 0.7, "map50_95": 0.46,
                                                "precision": 0.68, "recall_sensitivity": 0.65}},
            "summary": {"task": "detect", "images": 90, "ground_truth_instances": 44,
                        "metrics": {"map50": 0.7, "map50_95": 0.46,
                                    "precision": 0.68, "recall_sensitivity": 0.65},
                        "operational_coverage": 0.9},
            "per_class": add_classes,
            "plots": plots("dental31", ["Matriz percentual"]),
            "examples_all": examples("dental31", ex_ids),
        },
        "age": {
            "slug": "age", "name": "Estimativa de faixa etária", "eyebrow": "Faixa etária",
            "kind": "age", "accent": "amber",
            "description": "Classificação criança / adulto para triagem operacional.",
            "progress": {"processed": 220, "total": 220, "status": "complete"},
            "training_validation": {"epoch": 55, "epochs_completed": 60, "images": 3000,
                                    "metrics": {"accuracy": 0.9, "recall_child_sensitivity": 0.88,
                                                "roc_auc": 0.95}},
            "summary": {"task": "classify", "images": 220, "ground_truth_instances": 220,
                        "metrics": {"accuracy": 0.9, "recall_child_sensitivity": 0.88,
                                    "specificity_adult": 0.91, "roc_auc": 0.95},
                        "operational_coverage": 0.88},
            "per_class": [],
            "plots": plots("age", ["Curva ROC"]),
            "examples_all": examples("age", ex_ids),
        },
    }


# --- sessões -----------------------------------------------------------------

def create_session(username: str = "admin", role: str | None = None) -> dict:
    c = conn()
    username = username or "admin"
    if role is None:
        role = "student" if str(username).lower().startswith(("aluno", "student")) else "reviewer"
    is_admin = 0 if role == "student" else 1
    sid, csrf = secrets.token_hex(16), secrets.token_hex(16)
    c.execute("INSERT INTO sessions(sid,username,role,is_admin,csrf,created_at) VALUES(?,?,?,?,?,?)",
              (sid, username, role, is_admin, csrf, _now()))
    c.commit()
    return {"sid": sid, "username": username, "role": role,
            "is_admin": bool(is_admin), "csrf": csrf}


def get_session(sid: str | None) -> dict | None:
    if not sid:
        return None
    row = conn().execute("SELECT * FROM sessions WHERE sid=?", (sid,)).fetchone()
    if not row:
        return None
    return {"sid": row["sid"], "username": row["username"], "role": row["role"],
            "is_admin": bool(row["is_admin"]), "csrf": row["csrf"]}


def delete_session(sid: str | None) -> None:
    c = conn()
    c.execute("DELETE FROM sessions WHERE sid=?", (sid,))
    c.commit()


# --- imagens -----------------------------------------------------------------

def _image_item(row: sqlite3.Row, anns: list[sqlite3.Row],
                locks: dict, jobs_by_image: dict) -> dict:
    group_counts: dict[str, int] = {}
    complete: list[str] = []
    by_group: dict[str, list[int]] = {}
    for a in anns:
        by_group.setdefault(a["grp"], []).append(a["segmented"])
    for grp, segs in by_group.items():
        group_counts[grp] = len(segs)
        if all(segs):
            complete.append(grp)
    annotation_count = len(anns)
    segmented_count = sum(1 for a in anns if a["segmented"])
    return {
        "image_id": row["image_id"], "reviewed": bool(row["reviewed"]),
        "reviewer": row["reviewer"], "revision": row["revision"],
        "created_at": row["created_at"], "source_database": row["source_database"],
        "width": row["width"], "height": row["height"],
        "annotation_count": annotation_count, "segmented_count": segmented_count,
        "complete_groups": complete, "group_counts": group_counts,
        "age_classification": {
            "label": row["age_label"], "confidence": row["age_confidence"],
            "reviewed": bool(row["age_reviewed"]), "reviewed_by": row["age_reviewed_by"],
        },
        "sort_probability": row["age_confidence"],
        "probability_basis": "class",
    }


def _locks() -> dict:
    return {r["image_id"]: {"editing_by": r["editing_by"]} for r in
            conn().execute("SELECT * FROM edit_locks")}


def _active_jobs() -> dict:
    rows = conn().execute("SELECT * FROM jobs WHERE status IN ('queued','processing')").fetchall()
    return {r["image_id"]: _job_dict(r) for r in rows if r["image_id"]}


def list_reviews(page: int = 1, status: str = "all", age_group: str | None = None,
                 source_group: str | None = None, class_group: str | None = None,
                 class_label: str | None = None, probability_order: str | None = None) -> dict:
    c = conn()
    where, params = [], []
    if status == "reviewed":
        where.append("reviewed=1")
    elif status == "pending":
        where.append("reviewed=0")
    if age_group:
        where.append("age_label=?")
        params.append(age_group)
    if source_group:
        where.append("source_database=?")
        params.append(source_group)
    if class_group and class_label:
        where.append("image_id IN (SELECT image_id FROM annotations WHERE grp=? AND label=?)")
        params += [class_group, class_label]
    sql = "SELECT * FROM images"
    if where:
        sql += " WHERE " + " AND ".join(where)
    if probability_order in ("asc", "desc"):
        sql += f" ORDER BY age_confidence {probability_order.upper()}, created_at"
    else:
        sql += " ORDER BY created_at"
    rows = c.execute(sql, params).fetchall()
    total = len(rows)
    pages = max(1, math.ceil(total / PAGE_SIZE))
    page = max(1, min(page, pages))
    window = rows[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]
    locks, jobs_by_image = _locks(), _active_jobs()
    items = []
    for row in window:
        anns = c.execute("SELECT * FROM annotations WHERE image_id=?", (row["image_id"],)).fetchall()
        items.append(_image_item(row, anns, locks, jobs_by_image))
    return {"page": page, "pages": pages, "total": total, "items": items,
            "active_jobs": jobs_by_image, "edit_locks": locks}


def get_image(image_id: str) -> dict | None:
    c = conn()
    row = c.execute("SELECT * FROM images WHERE image_id=?", (image_id,)).fetchone()
    if not row:
        return None
    anns = c.execute("SELECT * FROM annotations WHERE image_id=?", (image_id,)).fetchall()
    return _image_item(row, anns, _locks(), _active_jobs())


def delete_image(image_id: str) -> bool:
    c = conn()
    exists = c.execute("SELECT 1 FROM images WHERE image_id=?", (image_id,)).fetchone()
    if not exists:
        return False
    c.execute("DELETE FROM annotations WHERE image_id=?", (image_id,))
    c.execute("DELETE FROM images WHERE image_id=?", (image_id,))
    c.execute("DELETE FROM edit_locks WHERE image_id=?", (image_id,))
    c.commit()
    return True


def set_age(image_id: str, label: str, username: str) -> bool:
    c = conn()
    if not c.execute("SELECT 1 FROM images WHERE image_id=?", (image_id,)).fetchone():
        return False
    c.execute("UPDATE images SET age_label=?, age_reviewed=1, age_reviewed_by=? WHERE image_id=?",
              (label, username, image_id))
    c.commit()
    return True


def set_edit_lock(image_id: str, editing_by: str) -> None:
    c = conn()
    c.execute("INSERT INTO edit_locks(image_id,editing_by,updated_at) VALUES(?,?,?) "
              "ON CONFLICT(image_id) DO UPDATE SET editing_by=excluded.editing_by,"
              "updated_at=excluded.updated_at", (image_id, editing_by, _now()))
    c.commit()


def clear_edit_lock(image_id: str) -> None:
    c = conn()
    c.execute("DELETE FROM edit_locks WHERE image_id=?", (image_id,))
    c.commit()


# --- jobs / batch ------------------------------------------------------------

def _job_dict(row: sqlite3.Row) -> dict:
    return {"job_id": row["job_id"], "status": row["status"], "current": row["current"],
            "total": row["total"], "message": row["message"], "kind": row["kind"]}


def get_job(job_id: str) -> dict | None:
    row = conn().execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    return _job_dict(row) if row else None


def create_segment_job(image_id: str, replace_teeth: bool = False) -> dict | None:
    c = conn()
    if not c.execute("SELECT 1 FROM images WHERE image_id=?", (image_id,)).fetchone():
        return None
    total = c.execute("SELECT COUNT(*) FROM annotations WHERE image_id=?", (image_id,)).fetchone()[0]
    job_id = secrets.token_hex(8)
    # Stub determinístico: marca as anotações como segmentadas (substitui MedSAM real).
    c.execute("UPDATE annotations SET segmented=1 WHERE image_id=?", (image_id,))
    c.execute("INSERT INTO jobs(job_id,kind,status,current,total,message,image_id,batch_id,"
              "created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (job_id, "segment", "completed", total, total,
               "Processamento concluído (motor stub).", image_id, None, _now(), _now()))
    c.commit()
    return get_job(job_id)


def create_batch() -> dict:
    c = conn()
    pending = c.execute("SELECT image_id FROM images WHERE reviewed=0").fetchall()
    batch_id = secrets.token_hex(8)
    total = len(pending)
    c.execute("INSERT INTO batches(batch_id,status,current,total,succeeded,skipped,failed,"
              "message,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (batch_id, "completed", total, total, total, 0, 0,
               "Lote concluído (motor stub).", _now(), _now()))
    c.execute("UPDATE annotations SET segmented=1 WHERE image_id IN "
              "(SELECT image_id FROM images WHERE reviewed=0)")
    c.commit()
    return _batch_dict(c.execute("SELECT * FROM batches WHERE batch_id=?", (batch_id,)).fetchone())


def _batch_dict(row: sqlite3.Row) -> dict:
    return {"batch_id": row["batch_id"], "status": row["status"], "current": row["current"],
            "total": row["total"], "succeeded": row["succeeded"], "skipped": row["skipped"],
            "failed": row["failed"], "message": row["message"]}


def get_current_batch() -> dict:
    row = conn().execute("SELECT * FROM batches ORDER BY created_at DESC LIMIT 1").fetchone()
    if not row:
        return {"batch_id": None, "status": "idle", "current": 0, "total": 0,
                "succeeded": 0, "skipped": 0, "failed": 0, "message": ""}
    return _batch_dict(row)


def cancel_batch(batch_id: str) -> dict | None:
    c = conn()
    row = c.execute("SELECT * FROM batches WHERE batch_id=?", (batch_id,)).fetchone()
    if not row:
        return None
    c.execute("UPDATE batches SET status='cancelled', updated_at=? WHERE batch_id=?",
              (_now(), batch_id))
    c.commit()
    return _batch_dict(c.execute("SELECT * FROM batches WHERE batch_id=?", (batch_id,)).fetchone())


# --- export ------------------------------------------------------------------

def export_zip(group: str, task: str) -> bytes:
    c = conn()
    rows = c.execute("SELECT * FROM images ORDER BY created_at").fetchall()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest = {"group": group, "task": task, "synthetic": True, "images": []}
        for row in rows:
            anns = c.execute("SELECT grp,label,segmented,source FROM annotations WHERE image_id=?",
                             (row["image_id"],)).fetchall()
            if group != "all":
                anns = [a for a in anns if a["grp"] == group]
                if not anns:
                    continue
            zf.writestr(f"images/{row['image_id']}.png",
                        synth_panoramic(row["image_id"], row["width"], row["height"]))
            payload = {"image_id": row["image_id"], "source_database": row["source_database"],
                       "width": row["width"], "height": row["height"],
                       "annotations": [dict(a) for a in anns]}
            zf.writestr(f"annotations/{row['image_id']}.json",
                        json.dumps(payload, ensure_ascii=False, indent=2))
            manifest["images"].append(row["image_id"])
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return buf.getvalue()


# --- feedback ----------------------------------------------------------------

def save_feedback(image_id: str, revision: int, document: dict, baseline: dict) -> None:
    c = conn()
    c.execute("INSERT INTO feedback(image_id,revision,document,baseline,saved_at) "
              "VALUES(?,?,?,?,?) ON CONFLICT(image_id) DO UPDATE SET revision=excluded.revision,"
              "document=excluded.document, baseline=excluded.baseline, saved_at=excluded.saved_at",
              (image_id, revision, json.dumps(document, ensure_ascii=False),
               json.dumps(baseline, ensure_ascii=False), _now()))
    c.commit()


def get_feedback(image_id: str) -> dict | None:
    row = conn().execute("SELECT * FROM feedback WHERE image_id=?", (image_id,)).fetchone()
    if not row:
        return None
    return {"image_id": row["image_id"], "revision": row["revision"],
            "document": json.loads(row["document"]), "baseline": json.loads(row["baseline"]),
            "saved_at": row["saved_at"]}


def all_feedback() -> list[dict]:
    return [get_feedback(r["image_id"]) for r in conn().execute("SELECT image_id FROM feedback")]


# --- estatísticas ------------------------------------------------------------

def statistics() -> dict:
    c = conn()
    images = c.execute("SELECT COUNT(*) FROM images").fetchone()[0]
    reviewed = c.execute("SELECT COUNT(*) FROM images WHERE reviewed=1").fetchone()[0]
    deltas = {(r["grp"], r["label"]): r for r in c.execute("SELECT * FROM class_deltas")}
    rows = c.execute(
        "SELECT grp, label, COUNT(DISTINCT image_id) AS imgs, COUNT(*) AS anns, "
        "SUM(segmented) AS seg FROM annotations GROUP BY grp, label ORDER BY grp, label").fetchall()
    classes = []
    for r in rows:
        d = deltas.get((r["grp"], r["label"]))
        classes.append({"group": r["grp"], "label": r["label"], "images": r["imgs"],
                        "annotations": r["anns"], "segmented": int(r["seg"] or 0),
                        "pending_delta": int(d["pending_delta"]) if d else 0,
                        "review_delta": int(d["review_delta"]) if d else 0})
    classes_increased = sum(1 for row in classes if row["review_delta"] > 0)
    return {"images": images, "reviewed_images": reviewed,
            "classes_increased": classes_increased, "classes": classes,
            "average_review_seconds": 138.0 if reviewed else None,
            "measured_reviews": reviewed}


# --- validação ---------------------------------------------------------------

def list_models() -> list[dict]:
    rows = conn().execute("SELECT data FROM models ORDER BY slug").fetchall()
    models = []
    for r in rows:
        m = json.loads(r["data"])
        models.append({k: m[k] for k in ("slug", "name", "eyebrow", "description",
                                         "kind", "accent", "progress", "summary",
                                         "training_validation")})
    return models


def get_model(slug: str, page: int = 1, page_size: int = PAGE_SIZE) -> dict | None:
    row = conn().execute("SELECT data FROM models WHERE slug=?", (slug,)).fetchone()
    if not row:
        return None
    m = json.loads(row["data"])
    all_examples = m.pop("examples_all", [])
    total = len(all_examples)
    pages = max(1, math.ceil(total / page_size))
    page = max(1, min(page, pages))
    m["examples"] = all_examples[(page - 1) * page_size: page * page_size]
    m["pagination"] = {"page": page, "pages": pages, "total": total, "page_size": page_size}
    return m


def model_annotations(slug: str, image_id: str) -> dict:
    c = conn()
    row = c.execute("SELECT * FROM images WHERE image_id=?", (image_id,)).fetchone()
    if not row:
        return {"classes": [], "fixed_confidence": 0.25, "predictions": [], "ground_truth": []}
    anns = c.execute("SELECT * FROM annotations WHERE image_id=?", (image_id,)).fetchall()
    width, height = row["width"], row["height"]
    labels = [a["label"] for a in anns] or ["tooth"]
    classes = sorted(set(labels))
    predictions, ground_truth = [], []
    n = max(1, len(anns))
    cw = width / n
    for i, a in enumerate(anns):
        x = i * cw
        bbox = [round(x + 4, 1), round(height * 0.3, 1), round(x + cw - 4, 1), round(height * 0.7, 1)]
        polygon = [[round(x + 4, 1), round(height * 0.3, 1)], [round(x + cw - 4, 1), round(height * 0.3, 1)],
                   [round(x + cw - 4, 1), round(height * 0.7, 1)], [round(x + 4, 1), round(height * 0.7, 1)]]
        arrow = {"label": a["label"], "bbox_xyxy": bbox,
                 "polygon_xy": polygon if slug == "teeth" else []}
        ground_truth.append(dict(arrow))
        predictions.append({**arrow, "confidence": round(0.6 + 0.03 * (i % 12), 3)})
    return {"classes": classes, "fixed_confidence": 0.25,
            "predictions": predictions, "ground_truth": ground_truth}


# --- imagens sintéticas (demonstração) ---------------------------------------

def synth_panoramic(image_id: str, width: int, height: int) -> bytes:
    seed = int(hashlib.sha256(image_id.encode()).hexdigest(), 16)
    base = Image.new("RGB", (width, height), (8, 12, 20))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        v = int(20 + 40 * y / height)
        draw.line([(0, y), (width, y)], fill=(v // 2, v, v // 3))
    n = 16
    cw = width // n
    for k in range(n):
        x = k * cw
        jitter = (seed >> (k % 8)) & 7
        draw.ellipse([x + 4, height // 2 - 40 + jitter, x + cw - 4, height // 2 + 60 + jitter],
                     fill=(230, 225, 205), outline=(180, 170, 150))
    draw.text((10, 10), f"DEMO {image_id} (sintetico)", fill=(200, 220, 255))
    out = io.BytesIO()
    base.save(out, format="PNG")
    return out.getvalue()


def synth_thumbnail(image_id: str, width: int, height: int) -> bytes:
    full = Image.open(io.BytesIO(synth_panoramic(image_id, width, height)))
    full.thumbnail((240, 120))
    out = io.BytesIO()
    full.save(out, format="PNG")
    return out.getvalue()


def synth_plot(slug: str, index: int) -> bytes:
    img = Image.new("RGB", (480, 320), (11, 18, 32))
    draw = ImageDraw.Draw(img)
    for gx in range(0, 481, 40):
        draw.line([(gx, 0), (gx, 320)], fill=(24, 34, 54))
    for gy in range(0, 321, 40):
        draw.line([(0, gy), (480, gy)], fill=(24, 34, 54))
    seed = int(hashlib.sha256(f"{slug}:{index}".encode()).hexdigest(), 16)
    points = []
    for i in range(12):
        v = 300 - ((seed >> (i % 16)) & 0xFF) - 40 * (i % 3)
        points.append((20 + i * 38, max(20, v)))
    draw.line(points, fill=(45, 212, 191), width=3)
    draw.text((14, 8), f"DEMO plot {slug} #{index}", fill=(226, 232, 240))
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()
