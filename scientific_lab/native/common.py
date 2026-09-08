from __future__ import annotations
import datetime as dt, hashlib, json, re, uuid
from pathlib import Path
from typing import Any

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')

def uid(prefix: str, n: int = 10) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:n]}"

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def slug(text: str, n: int = 90) -> str:
    x = re.sub(r'[^\w\s.-]', '', text or '', flags=re.UNICODE).strip().lower()
    x = re.sub(r'[\s/]+', '-', x)
    return x[:n].strip('-.') or 'item'

def dump(path: Path, obj: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path

def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))
