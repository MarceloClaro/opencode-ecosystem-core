#!/usr/bin/env python3
"""Cliente de geração de imagens OpenAI-compatible, sem shell e sem vazar chave.

Interface compatível com o skill hbg:
  image_gen.py generate --model MODEL --prompt TEXT --size 1536x1024 --out FILE
  image_gen.py generate-batch --input prompts.jsonl --out-dir DIR --concurrency 5

A chave vem apenas de OPENAI_API_KEY; o endpoint de OPENAI_BASE_URL. Aceita
http://127.0.0.1|localhost ou https://. Não imprime a chave nem grava em disco.
"""

from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MAX_TIMEOUT = 300
MAX_CONCURRENCY = 10
DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1536x1024"


def _endpoint() -> tuple[str, str]:
    base = (os.environ.get("OPENAI_BASE_URL") or "http://127.0.0.1:8317/v1").rstrip("/")
    parsed = urlparse(base)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("OPENAI_BASE_URL deve usar http(s)")
    if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("http sem TLS só é aceito em loopback")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY ausente; configure o proxy local ou um endpoint compatível")
    return base, key


def _post(url: str, key: str, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    request = Request(
        url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:600]
        raise ValueError(f"HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise ValueError(f"conexão falhou: {exc.reason}") from exc
    try:
        return json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("resposta não é JSON") from exc


def _image_bytes(body: Dict[str, Any], key: str, timeout: int) -> bytes:
    data = body.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ValueError("resposta sem data[0]")
    item = data[0]
    encoded = item.get("b64_json")
    if isinstance(encoded, str) and encoded:
        try:
            return base64.b64decode(encoded)
        except (ValueError, TypeError) as exc:
            raise ValueError("b64_json inválido") from exc
    url = item.get("url")
    if isinstance(url, str) and url.startswith(("http://", "https://")):
        request = Request(url, headers={"User-Agent": "core-imagegen/1"})
        with urlopen(request, timeout=timeout) as response:
            return response.read()
    raise ValueError("resposta sem b64_json ou url")


def _safe_output(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError("output vazio")
    target = (root / relative).resolve()
    if not str(target).startswith(str(root.resolve()) + os.sep) and target != root.resolve():
        raise ValueError("output fora do diretório permitido")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _generate_one(prompt: str, model: str, size: str, out: Path,
                  timeout: int) -> Dict[str, Any]:
    base, key = _endpoint()
    payload = {"model": model, "prompt": prompt, "n": 1, "size": size,
               "response_format": "b64_json"}
    started = time.monotonic()
    try:
        body = _post(base + "/images/generations", key, payload, timeout)
        content = _image_bytes(body, key, timeout)
        out.write_bytes(content)
        return {"status": "ok", "path": str(out), "bytes": len(content),
                "elapsed_seconds": round(time.monotonic() - started, 3)}
    except (ValueError, OSError) as exc:
        return {"status": "failed", "path": str(out), "error": str(exc)[:600],
                "elapsed_seconds": round(time.monotonic() - started, 3)}


def generate(prompt: str, out: Path, *, model: str = DEFAULT_MODEL,
             size: str = DEFAULT_SIZE, timeout: int = 180) -> Dict[str, Any]:
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt obrigatório")
    if not re.fullmatch(r"\d{2,5}x\d{2,5}|auto", size):
        raise ValueError("size deve ser LARGURAxALTURA ou auto")
    if out.is_dir():
        out = out / f"image-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    return _generate_one(prompt.strip(), model, size, out, timeout)


def generate_batch(input_path: Path, out_dir: Path, *, concurrency: int = 5,
                    timeout: int = 180) -> Dict[str, Any]:
    if not input_path.is_file():
        raise ValueError("JSONL de prompts inexistente")
    if type(concurrency) is not int or not 1 <= concurrency <= MAX_CONCURRENCY:
        raise ValueError(f"concurrency deve estar entre 1 e {MAX_CONCURRENCY}")
    jobs: List[Dict[str, Any]] = []
    for line_number, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            job = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"linha {line_number} não é JSON") from exc
        if not isinstance(job, dict) or not isinstance(job.get("prompt"), str):
            raise ValueError(f"linha {line_number} sem prompt")
        jobs.append(job)
    if not jobs:
        raise ValueError("JSONL sem jobs")
    out_dir.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    prepared = []
    for index, job in enumerate(jobs, 1):
        relative = job.get("output") or job.get("id") or f"job-{index:03d}"
        if not isinstance(relative, str):
            relative = f"job-{index:03d}"
        if not relative.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            relative += ".png"
        target = _safe_output(out_dir, relative)
        if str(target) in seen:
            raise ValueError(f"output duplicado: {relative}")
        seen.add(str(target))
        prepared.append((job, target))

    results = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {}
        for job, target in prepared:
            model = job.get("model") or os.environ.get("HBG_IMAGE_MODEL") or DEFAULT_MODEL
            size = job.get("size") or DEFAULT_SIZE
            futures[executor.submit(_generate_one, job["prompt"], model, size,
                                    target, timeout)] = target
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item.get("path", ""))
    succeeded = sum(1 for item in results if item["status"] == "ok")
    failed = len(results) - succeeded
    return {
        "status": "completed" if failed == 0 else ("partial" if succeeded else "failed"),
        "requested": len(results), "succeeded": succeeded, "failed": failed,
        "outputs": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--model", default=os.environ.get("HBG_IMAGE_MODEL", DEFAULT_MODEL))
    gen.add_argument("--prompt", required=True)
    gen.add_argument("--size", default=DEFAULT_SIZE)
    gen.add_argument("--out", required=True)
    gen.add_argument("--timeout", type=int, default=180)
    gen.add_argument("--no-augment", action="store_true")
    batch = sub.add_parser("generate-batch")
    batch.add_argument("--input", required=True)
    batch.add_argument("--out-dir", required=True)
    batch.add_argument("--concurrency", type=int, default=5)
    batch.add_argument("--timeout", type=int, default=180)
    batch.add_argument("--no-augment", action="store_true")
    args = parser.parse_args(argv)
    try:
        if getattr(args, "timeout", 180) < 10 or getattr(args, "timeout", 180) > MAX_TIMEOUT:
            raise ValueError(f"timeout deve estar entre 10 e {MAX_TIMEOUT}")
        if args.command == "generate":
            result = generate(args.prompt, Path(args.out).expanduser(), model=args.model,
                              size=args.size, timeout=args.timeout)
            payload = {"status": result["status"], **result}
        else:
            payload = generate_batch(Path(args.input).expanduser(),
                                      Path(args.out_dir).expanduser(),
                                      concurrency=args.concurrency,
                                      timeout=args.timeout)
    except (ValueError, OSError) as exc:
        payload = {"status": "blocked", "error": str(exc)}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "completed" or payload.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
