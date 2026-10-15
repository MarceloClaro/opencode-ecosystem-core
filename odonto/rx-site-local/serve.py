#!/usr/bin/env python3
"""Servidor local da "Panoramica AI" — interface + LABORATÓRIOS REAIS locais.

Duas camadas coexistem:

1. **Interface (mock)** — SPEC-935-R899. O front-end faz `fetch(...).then(r =>
   r.json())`; sem backend, cada endpoint devolvia HTML 404 e o navegador
   falhava com ``Unexpected token '<'``. Aqui os endpoints devolvem JSON/ZIP
   válidos. ``/predict/images`` NÃO é inferência de IA: devolve a radiografia
   com selo "MOCK" e zero detecções por padrão.

2. **Laboratórios reais (SPEC-935-R900)** — rotas ``/api/*`` e as páginas
   ``/review``, ``/validacao``, ``/cadastro``, ``/docs`` executam compute REAL
   neste servidor sobre dados locais: inventário de datasets (com SHA-256),
   treino scikit-learn em thread, autômatos celulares (``odontoca.ca``) e o
   *gate* fail-closed da coorte travada (996/83/81). Nível de alegação:
   ``comparacao_empirica`` (ML) e ``descritivo_nao_causal`` (CA).

Uso:
    python3 serve.py [--port 8791] [--simulate 0] [--dir .]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from PIL import Image, ImageDraw

from backend import api as backend_api
from backend import labs as backend_labs

MOCK_BANNER = (
    '<div id="mock-notice" style="position:fixed;bottom:0;left:0;right:0;z-index:2147483647;'
    'pointer-events:none;padding:6px 14px;background:rgba(124,45,18,.95);color:#fff;'
    'font:650 12px/1.3 system-ui,sans-serif;text-align:center">'
    'MODO LOCAL — BACKEND SIMULADO (MOCK). Nenhum resultado exibido é inferência de IA. '
    'Demonstração de interface.</div>'
)

LAB_BANNER = (
    '<div id="lab-notice" style="position:fixed;bottom:0;left:0;right:0;z-index:2147483647;'
    'pointer-events:none;padding:6px 14px;background:rgba(19,78,74,.95);color:#e6fffb;'
    'font:650 12px/1.3 system-ui,sans-serif;text-align:center">'
    'LABORATÓRIO LOCAL (SPEC-935-R900) — compute REAL neste servidor sobre dados locais. '
    'Comparação empírica e simulação descritiva; NÃO é validação clínica nem inferência '
    'hospedada. Revisão humana obrigatória.</div>'
)


FDI_TEETH = (
    [f"1{n}" for n in range(1, 9)] + [f"2{n}" for n in range(1, 9)]
    + [f"3{n}" for n in range(1, 9)] + [f"4{n}" for n in range(1, 9)]
    + ["51", "52", "53", "54", "55", "61", "62", "63", "64", "65",
       "71", "72", "73", "74", "75", "81", "82", "83", "84", "85"]
)

ANNOTATION_CLASSES = {
    "teeth": FDI_TEETH,
    "findings": ["Impacted", "Caries", "Periapical lesion", "Deep caries"],
    "additional": {
        "maxillary_sinus": "Maxillary sinus",
        "mandibular_canal": "Mandibular canal",
        "dental31": "Dental31 / additional information",
    },
}

PLACEHOLDER_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d4944415478da63fcffff3f030005fe02fea72d5e8c0000000049454e44ae426082"
)

ROUTE_STUBS = {"/desejos"}

# páginas de laboratório REAIS (SPEC-935-R900) servidas de pages/<nome>.html
LAB_PAGES = {"review", "validacao", "cadastro", "docs"}

PLATE_W, PLATE_H = 1024, 384


def png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def watermark(image: Image.Image, text: str) -> Image.Image:
    out = image.copy()
    draw = ImageDraw.Draw(out)
    w, h = out.size
    draw.rectangle([0, 0, max(0, w - 1), max(0, h - 1)], outline=(255, 80, 80), width=3)
    draw.text((8, 8), f"MOCK — {text}", fill=(255, 80, 80))
    return out


def boundary_of(content_type: str) -> bytes | None:
    match = re.search(r'boundary="?([^";]+)"?', content_type or "")
    return match.group(1).encode() if match else None


def first_file_bytes(body: bytes, content_type: str) -> bytes | None:
    """Bytes do primeiro campo com filename de um corpo multipart/form-data."""
    boundary = boundary_of(content_type)
    if not boundary:
        return None
    for chunk in body.split(b"--" + boundary):
        if b"filename=" not in chunk or b"\r\n\r\n" not in chunk:
            continue
        head, _, payload = chunk.partition(b"\r\n\r\n")
        if b"filename=" not in head:
            continue
        return payload.rstrip(b"\r\n-")
    return None


def fit(image: Image.Image, max_side: int = 1400) -> Image.Image:
    out = image.copy()
    out.thumbnail((max_side, max_side))
    return out


def build_mock_bundle(raw: bytes | None, simulate: int = 0) -> tuple[bytes, dict, dict]:
    """Monta o bundle ZIP (STORED) lido por ``readImageBundle``.

    Retorna (zip_bytes, headers_extra, layout).
    """
    original = Image.new("RGB", (1024, 512), (12, 18, 26))
    if raw:
        try:
            original = fit(Image.open(io.BytesIO(raw)).convert("RGB"))
        except Exception:  # upload inválido: degrada sem quebrar a UI
            pass

    annotated = watermark(original, "imagem anotada (sem detecções)")
    anatomy = watermark(original, "anatomia (sem detecções)")

    plate = Image.new("RGB", (PLATE_W, PLATE_H), (18, 24, 32))
    draw = ImageDraw.Draw(plate)
    draw.text((12, 10), "MOCK — prancha de dentes (dados fictícios de demonstração)",
              fill=(255, 80, 80))

    report: dict = {"teeth": [], "findings": [], "additional_information": [],
                    "age_classification": {"label": "uncertain"}}
    cards: list[dict] = []

    if simulate > 0:
        cell_w, cell_h = PLATE_W // 4, 96
        for index in range(min(simulate, 12)):
            col, row = index % 4, index // 4
            x, y = col * cell_w + 4, 40 + row * cell_h
            if y + cell_h > PLATE_H:
                break
            label = f"DEMO-FDI {FDI_TEETH[index]}"
            draw.rectangle([x, y, x + cell_w - 8, y + cell_h - 8], outline=(255, 80, 80))
            draw.text((x + 6, y + 6), label, fill=(255, 80, 80))
            cards.append({"title": label, "x": x, "y": y,
                          "width": cell_w - 8, "height": cell_h - 8})
            report["teeth"].append({
                "bbox_xyxy": [float(x), float(y), float(x + cell_w - 8), float(y + cell_h - 8)],
                "fdi_candidate": FDI_TEETH[index],
                "mock": True,
            })

    layout = {
        "width": PLATE_W,
        "height": PLATE_H,
        "cards": cards,
        "image_id": hashlib.sha256(raw or b"mock").hexdigest()[:32],
        "annotation_classes": ANNOTATION_CLASSES,
        "report": report,
        "dental31_diagnostics": None,
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr("panoramica-anotada.png", png_bytes(annotated))
        zf.writestr("panoramica-anatomia.png", png_bytes(anatomy))
        zf.writestr("panoramica-dentes.png", png_bytes(plate))
        zf.writestr("panoramica-impressao.json", json.dumps(layout))
    headers = {
        "X-Teeth-Count": str(len(report["teeth"])),
        "X-Findings-Count": "0",
        "X-Additional-Status": "completed",
        "X-Additional-Count": "0",
        "X-Anatomy-Count": "0",
    }
    return buf.getvalue(), headers, layout


class MockHandler(BaseHTTPRequestHandler):
    site_dir = Path(__file__).resolve().parent
    simulate = 0

    def respond(self, data: bytes, ctype: str, status: int = 200, extra: dict | None = None):
        try:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(data)
        except BrokenPipeError:
            pass

    def json_out(self, obj, status: int = 200):
        self.respond(json.dumps(obj).encode(), "application/json; charset=utf-8", status)

    def json_error(self, detail: str, status: int = 404):
        self.json_out({"detail": detail}, status)

    def serve_file(self, rel: str) -> None:
        target = (self.site_dir / rel).resolve()
        root = self.site_dir.resolve()
        if not (target == root or root in target.parents) or not target.is_file():
            return self.json_error(f"arquivo ausente: {rel}", 404)
        data = target.read_bytes()
        if target.name == "index.html":
            data = data.replace(b"<body", b'<body data-mock="1"', 1)
            # rodapé + pointer-events:none: avisa sem interceptar cliques da navegação
            data = data.replace(b"</body>", MOCK_BANNER.encode() + b"</body>", 1)
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".mp4": "video/mp4",
        }.get(target.suffix.lower(), "application/octet-stream")
        return self.respond(data, ctype)

    def serve_lab_page(self, name: str) -> None:
        """Serve uma página de laboratório real, injetando o selo LAB não bloqueante."""
        target = (self.site_dir / "pages" / f"{name}.html").resolve()
        root = (self.site_dir / "pages").resolve()
        if root not in target.parents or not target.is_file():
            return self.json_error(f"página de laboratório ausente: {name}", 404)
        data = target.read_bytes().replace(b"</body>", LAB_BANNER.encode() + b"</body>", 1)
        return self.respond(data, "text/html; charset=utf-8")

    def route_stub(self, path: str) -> bytes:
        return (
            "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>"
            f"<title>{path} — cópia local</title>"
            "<style>body{margin:0;background:#0a1119;color:#e2e8f0;"
            "font:16px/1.5 system-ui,sans-serif}main{max-width:720px;margin:auto;padding:32px}"
            "h1{font-size:20px}a{color:#5eead4}p{color:#9fb1c5}</style></head><body>"
            + MOCK_BANNER
            + f"<main><h1>{path} — fora da cópia local</h1><p>Esta rota não estava entre os "
            "arquivos capturados na auditoria REA (index.html, editor.js, navigation.js/css). "
            "A análise em <a href='/'>/</a> continua funcional.</p></main></body></html>"
        ).encode()

    # ---------- GET ----------
    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        query = parse_qs(parsed.query)
        if path in ("/", "/index.html"):
            return self.serve_file("index.html")
        if path in ("/editor.js", "/navigation.js", "/navigation.css"):
            return self.serve_file(path.lstrip("/"))
        stripped = path.strip("/")
        if stripped in LAB_PAGES and path == f"/{stripped}":
            return self.serve_lab_page(stripped)
        if path.startswith("/colaboradores/") or path in ("/favicon.ico", "/og-image.png"):
            return self.respond(PLACEHOLDER_PNG, "image/png")

        # laboratórios reais (SPEC-935-R900)
        lab = backend_api.handle_get(path, query)
        if lab is not None:
            return self.respond(lab.body, lab.ctype, lab.status, lab.headers)

        if path == "/health":
            progress = backend_labs.training_progress()
            return self.json_out({"status": "ok", "mock": True, "labs": True,
                                  "additional_model": {"status": "ready"},
                                  "laboratories": len(backend_labs.model_reports()),
                                  "training": {"completed": progress["completed"],
                                               "target": progress["target"],
                                               "source": progress["source"]}})
        if path == "/reviewer-ranking":
            return self.json_out({"counts": [0] * 8, "mock": True})
        if path == "/reviewer-profiles":
            return self.json_out({"profiles": [], "mock": True})
        if path == "/administrator-statistics":
            return self.json_out({"adult": 0, "child": 0, "mock": True})
        if path == "/training-progress":
            return self.json_out(backend_labs.training_progress())
        if path == "/admin/api/session":
            return self.json_out({"username": "demo-local", "csrf": "mock-csrf",
                                  "is_admin": False, "mock": True})
        if path.startswith("/admin/api/images/") or path.startswith("/feedback/"):
            return self.json_error("revisão administrativa indisponível no modo local", 404)
        if path == "/feedback/export":
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("LEIA-ME.txt", "Export MOCK: nenhuma revisão real registrada.\n")
            return self.respond(buffer.getvalue(), "application/zip")
        if path in ROUTE_STUBS:
            return self.respond(self.route_stub(path), "text/html; charset=utf-8")
        return self.json_error(f"rota não encontrada no modo local: {path}", 404)

    # ---------- POST ----------
    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""

        # laboratórios reais (SPEC-935-R900): treino e CA
        lab = backend_api.handle_post(path, parse_qs(parsed.query), body,
                                      self.headers.get("Content-Type", ""))
        if lab is not None:
            return self.respond(lab.body, lab.ctype, lab.status, lab.headers)

        if path == "/predict/images":
            raw = first_file_bytes(body, self.headers.get("Content-Type", ""))
            bundle, extra, _ = build_mock_bundle(raw, simulate=self.simulate)
            extra["X-Model-Scope"] = parse_qs(parsed.query).get("model_scope", ["combined"])[0]
            return self.respond(bundle, "application/zip", 200, extra)
        if path == "/segment/sam":
            return self.json_out({"bbox_xyxy": [8.0, 8.0, 72.0, 72.0],
                                  "polygon_xy": [[8, 8], [72, 8], [72, 72], [8, 72]],
                                  "model": "mock"})
        if path == "/feedback":
            return self.json_out({"revision": 1, "reviewer": "demo-local", "mock": True})
        if path == "/admin/api/wishes":
            return self.json_out({"id": "mock-wish-1", "mock": True})
        if path == "/admin/api/logout":
            return self.json_out({"status": "ok", "mock": True})
        if path.startswith("/admin/api/images/") and path.endswith("/edit-lock"):
            return self.json_out({"status": "locked", "mock": True})
        return self.json_error(f"rota não encontrada no modo local: {path}", 404)

    # ---------- DELETE ----------
    def do_DELETE(self):  # noqa: N802
        if urlparse(self.path).path.endswith("/edit-lock"):
            return self.json_out({"status": "released", "mock": True})
        return self.json_error("rota não encontrada no modo local", 404)

    def log_message(self, fmt, *args):
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Servidor local MOCK da Panoramica AI")
    parser.add_argument("--port", type=int, default=8791)
    parser.add_argument("--dir", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--simulate", type=int, default=0,
                        help="caixas DEMO fictícias (0 = nenhuma detecção)")
    args = parser.parse_args()

    MockHandler.site_dir = Path(args.dir).resolve()
    MockHandler.simulate = max(0, args.simulate)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), MockHandler)
    print(f"Panoramica AI (MOCK) -> http://127.0.0.1:{args.port}/ | dir={MockHandler.site_dir} "
          f"| simulate={MockHandler.simulate}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
