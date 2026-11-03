"""Carregamento de dados com proveniência fail-closed — SPEC-935-R898 FR-001/FR-012."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# SHA-256 fixado no manuscrito OdontoCA (notebook v1.4.0, cell SOURCE_SHA256).
SOURCE_SHA256 = "b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa"

TARGET_CANDIDATES = (
    "caries", "carie", "caries_binary", "target", "label", "y",
    "class", "outcome", "progression_event",
)

CLAIM_LEVEL = "comparacao_empirica"


class SourceHashError(RuntimeError):
    """SHA-256 do arquivo difere do valor fixado (fail-closed)."""


class ConsentError(RuntimeError):
    """Operação externa sem consentimento explícito do operador."""


class TargetNotFoundError(LookupError):
    """Nenhuma coluna-alvo detectável e nenhum override fornecido."""


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_table_s1(path: str | Path, *, sheet: str = "all_metadata") -> pd.DataFrame:
    """Carrega a fonte primária validando o SHA-256 fixado (FR-001)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    digest = sha256_file(p)
    if digest != SOURCE_SHA256:
        raise SourceHashError(
            f"SHA-256 difere do fixado no manuscrito: {digest} != {SOURCE_SHA256}"
        )
    return pd.read_excel(p, sheet_name=sheet)


def detect_target(df: pd.DataFrame, target: str | None = None) -> str:
    """Detecta a coluna-alvo por convenção; override manual respeitado."""
    if target is not None:
        if target not in df.columns:
            raise TargetNotFoundError(f"coluna-alvo '{target}' ausente")
        return target
    lowered = {c.lower(): c for c in df.columns}
    for cand in TARGET_CANDIDATES:
        if cand in lowered:
            return lowered[cand]
    raise TargetNotFoundError(
        f"nenhum alvo em {TARGET_CANDIDATES}; use --target. colunas={list(df.columns)}"
    )


@dataclass
class LoadedCSV:
    df: pd.DataFrame
    target: str


def load_csv(path: str | Path, target: str | None = None) -> LoadedCSV:
    p = Path(path)
    if p.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(p)
    else:
        try:
            df = pd.read_csv(p)
        except UnicodeDecodeError:
            df = pd.read_csv(p, encoding="latin-1")
    tgt = detect_target(df, target)
    return LoadedCSV(df=df, target=tgt)


def download_kaggle(
    ref: str,
    dest: str | Path,
    *,
    consent: bool = False,
    timeout: int = 600,
) -> Path:
    """Baixa dataset Kaggle — exige consentimento explícito (FR-012).

    Consentimento = keyword ``consent=True`` vindo da CLI ``--i-know-kaggle``.
    Registra proveniência (ref, hash do zip) em ``dest/provenance.json``.
    """
    if not consent:
        raise ConsentError(
            "download Kaggle requer consentimento explícito (--i-know-kaggle)"
        )
    if shutil.which("kaggle") is None:
        raise ConsentError("kaggle CLI não encontrada no PATH")
    dest_p = Path(dest)
    dest_p.mkdir(parents=True, exist_ok=True)
    cmd = ["kaggle", "datasets", "download", "-d", ref, "-p", str(dest_p), "--unzip"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"kaggle falhou ({proc.returncode}): {proc.stderr[-800:]}")
    files = sorted(
        f for f in dest_p.rglob("*")
        if f.is_file() and f.name != "provenance.json"
    )
    prov = {
        "source": "kaggle",
        "ref": ref,
        "files": [
            {"path": str(f.relative_to(dest_p)), "sha256": sha256_file(f), "bytes": f.stat().st_size}
            for f in files
        ],
        "claim_level": CLAIM_LEVEL,
    }
    (dest_p / "provenance.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=2)
    )
    return dest_p
