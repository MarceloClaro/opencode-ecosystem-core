"""Panoramica AI — reprodução funcional do contrato observado (SPEC-935-R853).

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
import secrets
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Body, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

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

app = FastAPI(title="Panoramica AI", version="0.1.0")

# Sessões admin em memória (stub; o alvo usa cookie de sessão)
_SESSIONS: dict[str, dict] = {}
# Revisões salvas em memória
_FEEDBACK: dict[str, dict] = {}


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
    n = 16
    boxes = _stub_engine(img.width, img.height, n)
    teeth = [{"fdi": FDI_PERMANENT[i % len(FDI_PERMANENT)], "score": round(0.9 - 0.02 * i, 4),
              "box": b["box"]} for i, b in enumerate(boxes)]
    findings = [b for b in boxes if b["class_name"] in ("caries", "periapical_lesion", "impacted_tooth")]
    return {
        "teeth": teeth,
        "findings": findings,
        "additional": [b for b in boxes] if include_additional else [],
        "model_scope": model_scope,
        "diagnostics": _diagnostics(31, confidence) if diagnose else None,
    }


@app.post("/predict/image")
def predict_image(file: UploadFile = File(...), confidence: float = 0.25) -> Response:
    img = _read_upload(file)
    boxes = _stub_engine(img.width, img.height, 16)
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
    boxes = _stub_engine(img.width, img.height, 16)

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
    # contorno = retângulo da caixa (stub; o alvo usa MedSAM)
    contour = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    return {"contour": contour, "target": target, "fdi": fdi,
            "image_size": [img.width, img.height]}


# --- feedback ----------------------------------------------------------------

@app.post("/feedback")
async def save_feedback(
    file: UploadFile = File(...),
    document: str = Form(...),
    baseline: str = Form("{}"),
    revision: int = Form(0),
) -> dict:
    image_id = secrets.token_hex(8)
    _FEEDBACK[image_id] = {
        "image_id": image_id,
        "revision": revision,
        "document": json.loads(document) if document else {},
        "baseline": json.loads(baseline) if baseline else {},
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"image_id": image_id, "revision": revision, "saved": True}


@app.get("/feedback/export")
def export_feedback(group: str, task: str) -> Response:
    payload = [v for v in _FEEDBACK.values()]
    body = json.dumps({"group": group, "task": task, "items": payload}, ensure_ascii=False)
    return Response(content=body, media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="feedback-{group}-{task}.json"'})


# rota dinâmica declarada DEPOIS de /feedback/export para não sombrear a estática
@app.get("/feedback/{image_id}")
def read_feedback(image_id: str) -> dict:
    if image_id not in _FEEDBACK:
        raise HTTPException(status_code=404, detail="Revisão não encontrada.")
    return _FEEDBACK[image_id]


# --- admin (stub autenticado) ------------------------------------------------

def _require_session(request: Request) -> None:
    sid = request.cookies.get("admin_session")
    if not sid or sid not in _SESSIONS:
        raise HTTPException(status_code=401, detail="Sessão administrativa inválida ou expirada.")


@app.post("/admin/api/login")
def admin_login(request: Request, payload: dict | None = Body(default=None)) -> Response:
    sid = secrets.token_hex(16)
    _SESSIONS[sid] = {"user": (payload or {}).get("user", "admin")}
    resp = JSONResponse({"authenticated": True})
    resp.set_cookie("admin_session", sid, httponly=True, samesite="strict")
    return resp


@app.get("/admin/api/session")
def admin_session(request: Request) -> dict:
    _require_session(request)
    return {"authenticated": True, "user": _SESSIONS[request.cookies["admin_session"]]["user"]}


@app.post("/admin/api/logout")
def admin_logout(request: Request) -> Response:
    sid = request.cookies.get("admin_session")
    _SESSIONS.pop(sid, None)
    resp = JSONResponse({"authenticated": False})
    resp.delete_cookie("admin_session")
    return resp


@app.get("/admin/api/reviews")
def admin_reviews(request: Request, page: int = 1, status: str = "all") -> dict:
    _require_session(request)
    return {"page": page, "status": status, "total": len(_FEEDBACK),
            "items": list(_FEEDBACK.values())}


@app.get("/admin/api/statistics")
def admin_statistics(request: Request) -> dict:
    _require_session(request)
    return {"total_images": len(_FEEDBACK), "reviewed": len(_FEEDBACK), "by_group": {}}


@app.get("/validacao/api/modelos")
def validacao_modelos(request: Request) -> dict:
    _require_session(request)
    return {"modelos": [
        {"slug": "dental31", "name": "Dental31 (adicional)"},
        {"slug": "fdi", "name": "FDI / numeração"},
        {"slug": "teeth", "name": "Segmentação dentária"},
        {"slug": "findings", "name": "Achados (DENTEX)"},
    ]}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8799)
