"""R1069: cliente imagegen OpenAI-compatible, testado com servidor local falso."""
from __future__ import annotations

import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import threading

import pytest

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl2nXQAAAAASUVORK5CYII="
)
SCRIPT = Path(__file__).resolve().parents[1] / "skills/imagegen/scripts/image_gen.py"
spec = importlib.util.spec_from_file_location("core_image_gen", SCRIPT)
image_gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(image_gen)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        if not self.path.endswith("/images/generations"):
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps({"data": [{"b64_json": base64.b64encode(PNG).decode()}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def fake_api(monkeypatch):
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    monkeypatch.setenv("OPENAI_BASE_URL", f"http://127.0.0.1:{port}/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    yield
    server.shutdown()
    thread.join(timeout=5)


def test_generate_writes_image(tmp_path, fake_api):
    target = tmp_path / "one.png"
    result = image_gen.generate("teste", target, size="16x16")
    assert result["status"] == "ok"
    assert target.is_file()
    assert target.read_bytes() == PNG


def test_generate_batch_writes_outputs(tmp_path, fake_api):
    prompts = tmp_path / "prompts.jsonl"
    prompts.write_text(
        "\n".join([
            json.dumps({"id": "a", "prompt": "primeira", "output": "sheets/a.png", "size": "16x16"}),
            json.dumps({"id": "b", "prompt": "segunda", "output": "sheets/b.png", "size": "16x16"}),
        ]) + "\n",
        encoding="utf-8",
    )
    result = image_gen.generate_batch(prompts, tmp_path / "out", concurrency=2)
    assert result["status"] == "completed"
    assert result["succeeded"] == 2 and result["failed"] == 0
    assert (tmp_path / "out/sheets/a.png").is_file()
    assert (tmp_path / "out/sheets/b.png").is_file()


def test_batch_rejects_path_traversal(tmp_path, fake_api):
    prompts = tmp_path / "prompts.jsonl"
    prompts.write_text(json.dumps({"id": "x", "prompt": "x", "output": "../escape.png"}) + "\n")
    with pytest.raises(ValueError):
        image_gen.generate_batch(prompts, tmp_path / "out")


def test_missing_key_is_blocked(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        image_gen.generate("x", tmp_path / "x.png")


def test_non_loopback_http_is_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_BASE_URL", "http://example.com/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    with pytest.raises(ValueError, match="loopback"):
        image_gen.generate("x", tmp_path / "x.png")
