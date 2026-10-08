"""Instala somente o binário oficial fixado, verificando checksums publicados."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile

import requests

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.43.0"
BASE = f"https://github.com/boltz-bio/boltz-api-cli/releases/download/v{VERSION}/"
ARCHIVE = f"boltz-api_{VERSION}_linux_amd64.tar.gz"
EXPECTED = "d074a681c027c2456438a9af324f554d8e56a274092060e86a522109e09fd866"
CHECKSUMS = f"boltz-api_{VERSION}_checksums.txt"
CHECKSUMS_SHA = "8763d42f0ab2d6fe8ef4f511c1fbe4429da2e2f943dacc506e8377d17f4ba73c"


def fetch(name, expected, limit):
    result = requests.get(BASE + name, timeout=(15, 60), stream=True)
    result.raise_for_status()
    chunks = []
    size = 0
    for chunk in result.iter_content(65536):
        size += len(chunk)
        if size > limit:
            raise ValueError("Artefato excedeu o limite de bytes")
        chunks.append(chunk)
    raw = b"".join(chunks)
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("Checksum oficial divergente")
    return raw


def main():
    checksums = fetch(CHECKSUMS, CHECKSUMS_SHA, 200000)
    if f"{EXPECTED}  {ARCHIVE}" not in checksums.decode():
        raise ValueError("Arquivo ausente do manifesto oficial de checksums")
    raw = fetch(ARCHIVE, EXPECTED, 64000000)
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        candidates = [m for m in archive.getmembers() if m.name == "boltz-api" and m.isfile()]
        if len(candidates) != 1 or candidates[0].size > 128000000:
            raise ValueError("Binário regular delimitado não encontrado")
        binary = archive.extractfile(candidates[0]).read()
    target = ROOT / ".venv/bin/boltz-api"
    sha = hashlib.sha256(binary).hexdigest()
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != sha:
        raise ValueError("Binário existente diferente; preservado")
    target.write_bytes(binary)
    target.chmod(0o755)
    env = {**os.environ, "BOLTZ_API_NO_UPDATE_CHECK": "1"}
    version = subprocess.run([str(target), "--version"], capture_output=True, text=True,
                             timeout=20, env=env)
    auth = subprocess.run([str(target), "auth", "status", "--format", "json"],
                          capture_output=True, text=True, timeout=20, env=env)
    report = {"version": version.stdout.strip(), "version_exit_code": version.returncode,
              "source_url": BASE + ARCHIVE, "archive_sha256": EXPECTED,
              "checksums_url": BASE + CHECKSUMS, "checksums_sha256": CHECKSUMS_SHA,
              "binary_path": str(target), "binary_sha256": sha,
              "auth_status_exit_code": auth.returncode,
              "inference_executed": False, "authentication_payload_persisted": False}
    (ROOT / "docs/evidence/R670_BOLTZ_INSTALL.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
