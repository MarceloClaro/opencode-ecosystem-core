#!/usr/bin/env python3
"""Gera uma prancha via Gemini image model, sem gravar a chave.

Uso:
  GEMINI_API_KEY=... python3 gemini_image.py \
    --prompt "..." --out plate.png --aspect 4:3 --size 2K
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", default="gemini-3-pro-image")
    parser.add_argument("--aspect", default="3:4")
    parser.add_argument("--size", default="2K")
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print(json.dumps({"status": "blocked", "error": "GEMINI_API_KEY ausente"}))
        return 2
    payload = {
        "contents": [{"parts": [{"text": args.prompt.strip()}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": args.aspect, "imageSize": args.size},
        },
    }
    request = urllib.request.Request(
        ENDPOINT.format(model=args.model),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            body = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:800]
        print(json.dumps({"status": "failed", "http": exc.code, "error": detail}))
        return 1
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)[:800]}))
        return 1

    parts = (
        body.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    image = None
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and str(inline.get("mimeType", "")).startswith("image/"):
            image = inline
            break
    if image is None:
        text = " ".join(part.get("text", "") for part in parts if part.get("text"))
        print(json.dumps({"status": "failed", "error": "sem imagem", "text": text[:800]}))
        return 1

    content = base64.b64decode(image["data"])
    target = args.out.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    print(json.dumps({
        "status": "ok",
        "path": str(target),
        "bytes": len(content),
        "mime": image.get("mimeType"),
        "sha256": hashlib.sha256(content).hexdigest(),
        "model": args.model,
        "aspect": args.aspect,
        "size": args.size,
        "prompt_sha256": hashlib.sha256(args.prompt.encode("utf-8")).hexdigest(),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
