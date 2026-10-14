"""ODONTOCA - Prof. Marcelo Claro — reprodução funcional do contrato observado (SPEC-935-R853).

Este backend NÃO contém os modelos de IA do alvo original (indisponíveis). Ele
reproduz o CONTRATO HTTP observado (OpenAPI 0.1.0) e o comportamento de I/O que
o front-end exercita, com um "motor" determinístico explícito (stub) que gera
caixas/pranchas a partir do tamanho da imagem enviada. Nada aqui é apresentado
como equivalente clínico ao original.

Contrato reproduzido (fonte: /openapi.json do alvo):
  GET  /health
  POST /predict                 (JSON: detecções)
  POST /predict/image           (PNG anotado)
  POST /predict/images          (ZIP_STORED: 3 PNGs + panoramica-impressao.json)
  POST /segment/sam             (contorno a partir de uma caixa)
  POST /feedback                (salvar revisão)  + GET /feedback/{image_id}
  GET  /feedback/export
  GET/POST /admin/api/...       (sessão + revisão do banco; stub autenticado)
  GET  /validacao/api/modelos   (stub autenticado)
  GET  /docs, /openapi.json     (FastAPI)

Cabeçalhos de resposta de /predict/images (observados no front-end):
  X-Model-Scope, X-Additional-Status, X-Additional-Count, X-Anatomy-Count,
  X-Teeth-Count, X-Findings-Count

Rodar:  uvicorn app:app --app-dir repro/backend --port 8799
"""

from __future__ import annotations

import io
import json
import os
import secrets
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Body, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

# Registro de motores (Opções 1/2/3) — carregado por caminho para funcionar tanto
# via `uvicorn --app-dir` quanto por import direto em testes.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engines as engines_mod  # noqa: E402
import store as store_mod  # noqa: E402,F401

# --- 31 classes Dental31 (observadas em /health do alvo) ----------------------
ADDITIONAL_CLASSES = [
    "caries", "crown", "filling", "implant", "malaligned", "mandibular_canal",
    "missing_teeth", "periapical_lesion", "retained_root", "root_canal_treatment",
    "root_piece", "impacted_tooth", "maxillary_sinus", "bone_loss", "fracture_teeth",
    "permanent_teeth", "supra_eruption", "tad", "abutment", "attrition",
    "bone_defect", "gingival_former", "metal_band", "orthodontic_brackets",
    "permanent_retainer", "post_core", "plating", "wire", "cyst",
    "root_resorption", "primary_teeth",
]

FDI_PERMANENT = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28,
                 38, 37, 36, 35, 34, 33, 32, 31, 41, 42, 43, 44, 45, 46, 47, 48]

app = FastAPI(title="ODONTOCA - Prof. Marcelo Claro", version="0.1.0")

# Motor de inferência ativo (Opções 1/2/3). Default: RX_ENGINE ou "stub".
_ACTIVE_ENGINE: str = engines_mod.resolve(None)

# Sessões, feedback, imagens, jobs e validação persistem em SQLite (SPEC-935-R874).
store = store_mod


def _active_engine() -> str:
    return _ACTIVE_ENGINE


def _guard(engine_id: str, capability: str):
    """Fail-closed: converte indisponibilidade do motor em HTTP 409 explícito."""
    try:
        return engines_mod.require_available(engine_id, capability)
    except ValueError as exc:  # motor ausente/indisponível/sem capability
        raise HTTPException(status_code=409, detail=f"motor de inferência indisponível — {exc}") from exc


def _service_engine(capability: str) -> str:
    """Motor que serve `capability` (composição por capacidade, SPEC-935-R876).

    Usa o motor ATIVO quando ele cobre a capacidade; senão recorre ao melhor
    provedor DISPONÍVEL (pesos reais antes do stub). Fail-closed: 409 somente
    quando NENHUM motor disponível cobre a capacidade.
    """
    eng = engines_mod.resolve_capability(capability, _active_engine())
    if eng is None:
        raise HTTPException(
            status_code=409,
            detail=f"motor de inferência indisponível — nenhum motor disponível cobre '{capability}'",
        )
    return eng


def _weights_detect(img: Image.Image) -> list[dict]:
    """Inferência REAL com pesos do operador (.pt) via Ultralytics. Só roda se disponível."""
    import numpy as np  # noqa: PLC0415
    from ultralytics import YOLO  # noqa: PLC0415
    weights = engines_mod.find_weights(os.environ.get("RX_WEIGHTS_DIR", ""))
    model = YOLO(weights[0])
    results = model.predict(np.array(img.convert("RGB")), verbose=False)
    boxes: list[dict] = []
    for res in results:
        names = getattr(res, "names", {}) or {}
        for b in getattr(res, "boxes", []) or []:
            cls = int(b.cls[0])
            boxes.append({
                "class_id": cls,
                "class_name": names.get(cls, str(cls)),
                "score": round(float(b.conf[0]), 4),
                "box": [float(v) for v in b.xyxy[0].tolist()],
            })
    return boxes


def _medsam_segment(img: Image.Image, box: list[float]) -> list[list[float]]:
    """Segmentação REAL via MedSAM. Só roda se disponível."""
    import numpy as np  # noqa: PLC0415
    import cv2  # noqa: PLC0415
    from segment_anything import SamPredictor, sam_model_registry  # noqa: PLC0415
    ckpt = os.environ["RX_MEDSAM_CKPT"]
    sam = _load_sam(ckpt, sam_model_registry)
    predictor = SamPredictor(sam)
    predictor.set_image(np.array(img.convert("RGB")))
    masks, _, _ = predictor.predict(box=np.array(box, dtype=float), multimask_output=False)
    contours, _ = cv2.findContours(masks[0].astype("uint8"), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return []
    contour = max(contours, key=cv2.contourArea)
    return [[float(p[0][0]), float(p[0][1])] for p in contour]


_SAM_CACHE: dict[str, "object"] = {}


def _load_sam(ckpt: str, registry):
    """Carrega o checkpoint SAM/MedSAM **mapeando para CPU**.

    O checkpoint oficial `medsam_vit_b.pth` guarda storages ancorados em CUDA;
    `sam_model_registry['vit_b'](checkpoint=...)` internamente usa
    `torch.load(f)` **sem** `map_location` e falha em host CPU-only. Aqui o
    `state_dict` é lido com `map_location='cpu'` e injetado em `strict=True`,
    o que garante correspondência exata de arquitetura (MedSAM ViT-B).
    """
    import torch  # noqa: PLC0415
    key = os.path.abspath(os.path.expanduser(ckpt))
    cached = _SAM_CACHE.get(key)
    if cached is not None:
        return cached
    state_dict = torch.load(key, map_location="cpu")
    sam = registry["vit_b"](checkpoint=None)
    sam.load_state_dict(state_dict, strict=True)
    sam.eval()
    _SAM_CACHE[key] = sam
    return sam


def _detect(img: Image.Image) -> tuple[list[dict], str]:
    """Detecção por capacidade: motor ativo se puder, senão o melhor disponível.

    Devolve (caixas, motor_efetivo). Fail-closed: 409 quando nenhum motor
    disponível cobre 'detection'.
    """
    eng = _service_engine("detection")
    if eng == "stub":
        return _stub_engine(img.width, img.height, 16), eng
    if eng == "weights":
        return _weights_detect(img), eng
    raise HTTPException(status_code=409, detail=f"motor '{eng}' não fornece detecção")


def _stub_engine(width: int, height: int, count: int) -> list[dict]:
    """Motor determinístico: distribui `count` caixas em grade sobre a imagem.

    Substitui os modelos reais. Score decrescente e classes rotativas apenas
    para exercitar os caminhos do front-end. NÃO é detecção clínica.
    """
    cols = 4
    rows = max(1, (count + cols - 1) // cols)
    bw = max(1, width // cols)
    bh = max(1, height // rows)
    boxes = []
    for i in range(count):
        r, c = divmod(i, cols)
        x = c * bw + bw // 8
        y = r * bh + bh // 4
        w = bw * 3 // 4
        h = bh // 2
        boxes.append({
            "class_id": i % len(ADDITIONAL_CLASSES),
            "class_name": ADDITIONAL_CLASSES[i % len(ADDITIONAL_CLASSES)],
            "score": round(0.9 - 0.02 * i, 4),
            "box": [x, y, x + w, y + h],
        })
    return boxes


def _annotated_png(img: Image.Image, boxes: list[dict], color=(45, 212, 191)) -> bytes:
    canvas = img.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    for b in boxes:
        x0, y0, x1, y1 = b["box"]
        draw.rectangle([x0, y0, x1, y1], outline=color, width=3)
        draw.text((x0 + 3, y0 + 3), f"{b['score']:.2f}", fill=color)
    out = io.BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def _anatomy_png(img: Image.Image) -> bytes:
    canvas = img.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    w, h = canvas.size
    draw.ellipse([w // 8, h // 5, w // 2 - w // 10, h // 2], outline=(96, 165, 250), width=4)
    draw.ellipse([w // 2 + w // 10, h // 5, w - w // 8, h // 2], outline=(96, 165, 250), width=4)
    draw.line([w // 6, h * 3 // 4, w * 5 // 6, h * 3 // 4], fill=(244, 114, 182), width=4)
    out = io.BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def _teeth_plate(img: Image.Image, n: int, cell=(220, 150)) -> tuple[bytes, int, int, list[dict]]:
    """Prancha de dentes: mosaico 4 colunas; devolve (png, w, h, cards).

    Os cards usam coordenadas absolutas dentro da prancha — exatamente o que o
    front-end (readImageBundle/buildPrintPreview) espera no layout de impressão.
    """
    cw, ch = cell
    cols = 4
    rows = max(1, (n + cols - 1) // cols)
    plate_w, plate_h = cols * cw, rows * ch
    plate = Image.new("RGB", (plate_w, plate_h), (3, 7, 18))
    src = img.convert("RGB")
    cards = []
    for i in range(n):
        r, c = divmod(i, cols)
        crop = src.resize((cw, ch))
        plate.paste(crop, (c * cw, r * ch))
        cards.append({
            "title": f"Dente {i + 1}",
            "x": c * cw,
            "y": r * ch,
            "width": cw,
            "height": ch,
        })
    out = io.BytesIO()
    plate.save(out, format="PNG")
    return out.getvalue(), plate_w, plate_h, cards


def _diagnostics(classes_count: int, confidence: float) -> dict:
    return {
        "confidence_floor": confidence,
        "candidate_limit_reached": False,
        "classes": [
            {
                "class_id": i,
                "class_name": ADDITIONAL_CLASSES[i] if i < len(ADDITIONAL_CLASSES) else f"class_{i}",
                "candidates": 1 if i % 5 else 0,
                "max_score": round(0.6 - 0.01 * i, 4) if i % 5 else None,
                "threshold": confidence,
                "accepted": 1 if i % 5 else 0,
                "status": "detected" if i % 5 else "no_candidate",
            }
            for i in range(classes_count)
        ],
    }


# --- páginas -----------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((FRONTEND / "index.html").read_text(encoding="utf-8"))


@app.get("/editor.js")
def editor_js() -> Response:
    return FileResponse(FRONTEND / "editor.js", media_type="application/javascript")


@app.get("/review", response_class=HTMLResponse)
def review_page() -> HTMLResponse:
    return HTMLResponse((FRONTEND / "review.html").read_text(encoding="utf-8"))


@app.get("/validacao", response_class=HTMLResponse)
def validacao_page() -> HTMLResponse:
    return HTMLResponse((FRONTEND / "validacao.html").read_text(encoding="utf-8"))


# --- seletor de motores (Opções 1/2/3) ---------------------------------------

def _opcoes_html() -> str:
    rows = []
    for e in engines_mod.engine_statuses():
        badge = "PRONTO" if e.available else "indisponível"
        color = "#22c55e" if e.available else "#94a3b8"
        kind = "inferência" if e.kind == "inference" else "treino (host com GPU)"
        req = ", ".join(e.requires) or "—"
        envs = "".join(
            f"<div><code>{k}={v}</code></div>" for k, v in (e.env_vars or {}).items()
        ) or "<span style='color:#64748b'>—</span>"
        rows.append(f"""
        <div class="card">
          <div class="hd"><b>Opção {e.option}</b> · {e.title}
            <span class="badge" style="background:{color}">{badge}</span></div>
          <div class="meta">tipo: {kind} · capabilities: {', '.join(e.capabilities) or '—'}</div>
          <div class="meta">requer: {req}</div>
          <div class="env">{envs}</div>
          <div class="det">{e.detail}</div>
          <div class="how">{e.how_to_enable}</div>
        </div>""")
    options = "".join(f'<option value="{e.id}">{e.id}</option>' for e in engines_mod.engine_statuses())
    serving = " · ".join(
        f"<b>{cap}</b>→{eng or '<span style=\"color:#f87171\">409</span>'}"
        for cap, eng in engines_mod.serving_map(_active_engine()).items()
    )
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>ODONTOCA - Prof. Marcelo Claro — seleção de motor</title>
<style>
 body{{font:15px/1.5 system-ui,Segoe UI,sans-serif;background:#0b1220;color:#e2e8f0;margin:0;padding:24px}}
 h1{{font-size:20px}} .cur{{background:#111a2e;padding:12px 16px;border-radius:10px;margin:12px 0}}
 .card{{background:#111a2e;border:1px solid #1e293b;border-radius:10px;padding:14px 16px;margin:10px 0}}
 .hd{{font-size:16px}} .badge{{color:#04121f;font-weight:700;border-radius:999px;padding:2px 10px;font-size:12px;margin-left:6px}}
 .meta{{color:#94a3b8;font-size:13px}} .env code{{background:#0b1220;padding:2px 6px;border-radius:6px}}
 .det,.how{{font-size:13px;color:#cbd5e1}} .how{{color:#7dd3fc}}
 form{{margin:16px 0}} select,button{{font:inherit;padding:8px 12px;border-radius:8px;border:1px solid #334155;background:#0b1220;color:#e2e8f0}}
 button{{background:#22d3ee;color:#04121f;font-weight:700;cursor:pointer}}
 a{{color:#7dd3fc}}
</style></head><body>
<h1>ODONTOCA - Prof. Marcelo Claro — opções de motor</h1>
<div class="cur">Motor ativo: <b>{_active_engine()}</b> · <a href="/">visualizador</a> · <a href="/docs">/docs</a> · <a href="/health">/health</a></div>
<div class="cur">Servindo por capacidade: {serving}</div>
<form method="post" action="/opcoes">
  <label>Escolher motor:
    <select name="engine">{options}</select>
  </label>
  <button type="submit">Aplicar</button>
</form>
{''.join(rows)}
<p style="color:#64748b">Composição por capacidade: o motor ativo serve o que ele cobre; o que ele NÃO cobre é servido pelo melhor motor <b>disponível</b> (pesos reais antes do stub). Fail-closed: quando nenhum motor disponível cobre a capacidade, a requisição retorna 409 com o motivo.</p>
</body></html>"""


@app.get("/opcoes", response_class=HTMLResponse)
def opcoes_page() -> HTMLResponse:
    return HTMLResponse(_opcoes_html())


@app.post("/opcoes")
def set_engine(engine: str = Form(...)) -> RedirectResponse:
    global _ACTIVE_ENGINE
    if engines_mod.by_id(engine) is None:
        raise HTTPException(status_code=422, detail=f"motor desconhecido: {engine}")
    _ACTIVE_ENGINE = engine
    return RedirectResponse("/opcoes", status_code=303)


@app.get("/opcoes.json")
def opcoes_json() -> dict:
    return {"active": _active_engine(), "serving": engines_mod.serving_map(_active_engine()),
            "engines": engines_mod.as_dicts(),
            "environment": engines_mod.environment()}


# --- health ------------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {
        "status": "ready",
        "device": "0",
        "models": {
            "age_weights_sha256": "stub",
            "fdi_weights_sha256": "stub",
            "teeth_weights_sha256": "stub",
            "finding_weights_sha256": "stub",
            "additional_weights_sha256": "stub",
        },
        "model_versions": {
            "age": {"version": "stub", "sha256": "stub", "registered": True},
            "fdi": {"version": "stub", "sha256": "stub", "registered": True},
            "teeth": {"version": "stub", "sha256": "stub", "registered": True},
            "findings": {"version": "stub", "sha256": "stub", "registered": True},
            "additional": {"version": "stub", "sha256": "stub", "registered": False},
        },
        "sam": {"status": "ready", "model": "stub-sam", "device": "cpu"},
        "additional_model": {
            "status": "ready",
            "source_id": "stub",
            "source_url": "https://www.kaggle.com/datasets/lokisilvres/dental-disease-panoramic-detection-dataset",
            "classes": ADDITIONAL_CLASSES,
            "role": "additional_information",
            "requires_review": True,
            "device": "0",
        },
        "engine": {
            "active": _active_engine(),
            "serving": engines_mod.serving_map(_active_engine()),
            "options": engines_mod.as_dicts(),
            "environment": engines_mod.environment(),
        },
    }


# --- predição ----------------------------------------------------------------

def _read_upload(file: UploadFile) -> Image.Image:
    try:
        return Image.open(io.BytesIO(file.file.read()))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Imagem inválida.") from exc


@app.post("/predict")
def predict(
    file: UploadFile = File(...),
    confidence: float = 0.25,
    fdi_confidence: float = 0.40,
    anatomy_confidence: float | None = None,
    imgsz: int = 640,
    min_iou: float = 0.5,
    include_additional: bool = True,
    model_scope: str = "combined",
    diagnose: bool = False,
) -> dict:
    img = _read_upload(file)
    boxes, eng = _detect(img)  # fail-closed: 409 se nenhum motor puder detectar
    teeth = [{"fdi": FDI_PERMANENT[i % len(FDI_PERMANENT)], "score": b["score"],
              "box": b["box"]} for i, b in enumerate(boxes)]
    findings = [b for b in boxes if b["class_name"] in ("caries", "periapical_lesion", "impacted_tooth")]
    return {
        "teeth": teeth,
        "findings": findings,
        "additional": [b for b in boxes] if include_additional else [],
        "model_scope": model_scope,
        "engine": eng,
        "diagnostics": _diagnostics(31, confidence) if diagnose else None,
    }


@app.post("/predict/image")
def predict_image(file: UploadFile = File(...), confidence: float = 0.25) -> Response:
    img = _read_upload(file)
    boxes, _ = _detect(img)
    return Response(content=_annotated_png(img, boxes), media_type="image/png")


@app.post("/predict/images")
def predict_images(
    file: UploadFile = File(...),
    confidence: float = 0.25,
    fdi_confidence: float = 0.40,
    anatomy_confidence: float | None = None,
    imgsz: int = 640,
    min_iou: float = 0.5,
    include_additional: bool = True,
    model_scope: str = "combined",
    diagnose: bool = False,
) -> Response:
    img = _read_upload(file)
    solo = model_scope == "dental31"
    n_teeth = 0 if solo else 16
    boxes, eng = _detect(img)  # fail-closed: 409 se nenhum motor puder detectar

    teeth_png, plate_w, plate_h, cards = _teeth_plate(img, max(1, n_teeth))
    layout = {
        "width": plate_w,
        "height": plate_h,
        "cards": cards if not solo else [],
        "dental31_diagnostics": _diagnostics(31, confidence) if diagnose else None,
    }

    # ZIP_STORED (sem compressão) — como o front-end readImageBundle exige.
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("panoramica-anotada.png", _annotated_png(img, boxes))
        zf.writestr("panoramica-anatomia.png", _anatomy_png(img))
        zf.writestr("panoramica-dentes.png", teeth_png)
        zf.writestr("panoramica-impressao.json", json.dumps(layout))

    additional_status = "completed" if include_additional else "disabled"
    headers = {
        "X-Model-Scope": "dental31" if solo else "combined",
        "X-Additional-Status": additional_status,
        "X-Additional-Count": str(len(boxes) if include_additional else 0),
        "X-Anatomy-Count": "3" if include_additional else "0",
        "X-Teeth-Count": str(n_teeth),
        "X-Findings-Count": "0" if solo else "3",
        "X-Engine": eng,
    }
    return Response(content=buf.getvalue(), media_type="application/zip", headers=headers)


# --- SAM ---------------------------------------------------------------------

@app.post("/segment/sam")
def segment_sam(
    file: UploadFile = File(...),
    box: str = Form(...),
    target: str = Form("generic"),
    fdi: str | None = Form(None),
) -> dict:
    img = _read_upload(file)
    try:
        x0, y0, x1, y1 = json.loads(box)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail="box inválido") from exc
    eng = _service_engine("sam")  # ativo se cobrir 'sam'; senão melhor disponível
    if eng == "stub":
        # contorno = retângulo da caixa (stub; o alvo usa MedSAM)
        contour = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    elif eng == "open_base":
        contour = _medsam_segment(img, [x0, y0, x1, y1])
    else:
        raise HTTPException(status_code=409, detail=f"motor '{eng}' não fornece segmentação SAM")
    return {"contour": contour, "target": target, "fdi": fdi,
            "engine": eng, "image_size": [img.width, img.height]}


# --- feedback (persistência SQLite, SPEC-935-R874) ---------------------------

@app.post("/feedback")
async def save_feedback(
    file: UploadFile = File(...),
    document: str = Form(...),
    baseline: str = Form("{}"),
    revision: int = Form(0),
) -> dict:
    image_id = secrets.token_hex(8)
    store.save_feedback(image_id, revision,
                        json.loads(document) if document else {},
                        json.loads(baseline) if baseline else {})
    return {"image_id": image_id, "revision": revision, "saved": True}


@app.get("/feedback/export")
def export_feedback(group: str, task: str) -> Response:
    payload = store.all_feedback()
    body = json.dumps({"group": group, "task": task, "items": payload}, ensure_ascii=False)
    return Response(content=body, media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="feedback-{group}-{task}.json"'})


# rota dinâmica declarada DEPOIS de /feedback/export para não sombrear a estática
@app.get("/feedback/{image_id}")
def read_feedback(image_id: str) -> dict:
    fb = store.get_feedback(image_id)
    if fb is None:
        raise HTTPException(status_code=404, detail="Revisão não encontrada.")
    return fb


# --- admin (sessão persistente; stub autenticado) ----------------------------

def _session(request: Request) -> dict:
    sess = store.get_session(request.cookies.get("admin_session"))
    if sess is None:
        raise HTTPException(status_code=401, detail="Sessão administrativa inválida ou expirada.")
    return sess


@app.post("/admin/api/login")
def admin_login(request: Request, payload: dict | None = Body(default=None)) -> Response:
    payload = payload or {}
    username = payload.get("username") or payload.get("user") or "admin"
    sess = store.create_session(username, payload.get("role"))
    resp = JSONResponse({
        "authenticated": True, "user": sess["username"], "username": sess["username"],
        "role": sess["role"], "is_admin": sess["is_admin"], "csrf": sess["csrf"],
    })
    resp.set_cookie("admin_session", sess["sid"], httponly=True, samesite="strict")
    return resp


@app.get("/admin/api/session")
def admin_session(request: Request) -> dict:
    sess = _session(request)
    return {"authenticated": True, "user": sess["username"], "username": sess["username"],
            "role": sess["role"], "is_admin": sess["is_admin"], "csrf": sess["csrf"]}


@app.post("/admin/api/logout")
def admin_logout(request: Request) -> Response:
    store.delete_session(request.cookies.get("admin_session"))
    resp = JSONResponse({"authenticated": False})
    resp.delete_cookie("admin_session")
    return resp


@app.get("/admin/api/reviews")
def admin_reviews(request: Request, page: int = 1, status: str = "all",
                  age_group: str | None = None, source_group: str | None = None,
                  class_group: str | None = None, class_label: str | None = None,
                  probability_order: str | None = None) -> dict:
    _session(request)
    return store.list_reviews(page, status, age_group, source_group, class_group,
                              class_label, probability_order)


@app.get("/admin/api/statistics")
def admin_statistics(request: Request) -> dict:
    _session(request)
    return store.statistics()


@app.get("/admin/api/images/{image_id}")
def admin_image(request: Request, image_id: str) -> dict:
    _session(request)
    item = store.get_image(image_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return item


@app.get("/admin/api/images/{image_id}/thumbnail")
def admin_image_thumbnail(request: Request, image_id: str) -> Response:
    _session(request)
    item = store.get_image(image_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return Response(content=store.synth_thumbnail(image_id, item["width"], item["height"]),
                    media_type="image/png")


@app.get("/admin/api/images/{image_id}/image")
def admin_image_full(request: Request, image_id: str) -> Response:
    _session(request)
    item = store.get_image(image_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return Response(content=store.synth_panoramic(image_id, item["width"], item["height"]),
                    media_type="image/png")


@app.put("/admin/api/images/{image_id}/age")
def admin_image_age(request: Request, image_id: str, payload: dict = Body(...)) -> dict:
    sess = _session(request)
    label = (payload or {}).get("label")
    if label not in ("child", "adult", "uncertain"):
        raise HTTPException(status_code=422, detail="label inválido")
    if not store.set_age(image_id, label, sess["username"]):
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return {"image_id": image_id, "label": label, "reviewed": True}


@app.post("/admin/api/images/{image_id}/edit-lock")
def admin_edit_lock(request: Request, image_id: str) -> dict:
    sess = _session(request)
    store.set_edit_lock(image_id, sess["username"])
    return {"image_id": image_id, "editing_by": sess["username"]}


@app.delete("/admin/api/images/{image_id}/edit-lock")
def admin_edit_unlock(request: Request, image_id: str) -> dict:
    _session(request)
    store.clear_edit_lock(image_id)
    return {"image_id": image_id, "editing_by": None}


@app.post("/admin/api/images/{image_id}/segment")
def admin_segment(request: Request, image_id: str, replace_teeth: bool = False) -> dict:
    _session(request)
    job = store.create_segment_job(image_id, replace_teeth)
    if job is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return job


@app.get("/admin/api/jobs/{job_id}")
def admin_job(request: Request, job_id: str) -> dict:
    _session(request)
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return job


@app.get("/admin/api/batch")
def admin_batch_get(request: Request) -> dict:
    _session(request)
    return store.get_current_batch()


@app.post("/admin/api/batch")
def admin_batch_post(request: Request, replace_ai_annotations: bool = False) -> dict:
    _session(request)
    return store.create_batch()


@app.delete("/admin/api/batch/{batch_id}")
def admin_batch_delete(request: Request, batch_id: str) -> dict:
    _session(request)
    batch = store.cancel_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")
    return batch


@app.get("/admin/api/export")
def admin_export(request: Request, group: str = "all", task: str = "detect") -> Response:
    _session(request)
    body = store.export_zip(group, task)
    return Response(content=body, media_type="application/zip",
                    headers={"Content-Disposition": f'attachment; filename="export-{group}-{task}.zip"'})


# --- validação ---------------------------------------------------------------

@app.get("/validacao/api/modelos")
def validacao_modelos(request: Request) -> dict:
    _session(request)
    models = store.list_models()
    # `modelos` mantém compatibilidade com a SPEC-935-R853; `models` alimenta o front.
    return {"models": models,
            "modelos": [{"slug": m["slug"], "name": m["name"]} for m in models]}


@app.get("/validacao/api/modelos/{slug}")
def validacao_modelo(request: Request, slug: str, page: int = 1, page_size: int = 10) -> dict:
    _session(request)
    model = store.get_model(slug, page, page_size)
    if model is None:
        raise HTTPException(status_code=404, detail="Modelo não encontrado.")
    return model


@app.post("/validacao/api/modelos/{slug}/imagens/{image_id}/revisao")
def validacao_revisao(request: Request, slug: str, image_id: str) -> dict:
    _session(request)
    return {"review_url": f"/?review={image_id}", "slug": slug, "image_id": image_id}


@app.get("/validacao/media/{slug}/{index}.png")
def validacao_media(request: Request, slug: str, index: int) -> Response:
    _session(request)
    return Response(content=store.synth_plot(slug, index), media_type="image/png")


@app.get("/validacao/annotations/{slug}/{image_id}.json")
def validacao_annotations(request: Request, slug: str, image_id: str) -> dict:
    _session(request)
    return store.model_annotations(slug, image_id)


# rota HTML do detalhe (serve a SPA; o JS lê o slug da própria URL)
@app.get("/validacao/{slug}", response_class=HTMLResponse)
def validacao_detail_page(slug: str) -> HTMLResponse:
    return HTMLResponse((FRONTEND / "validacao.html").read_text(encoding="utf-8"))


if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8799)
