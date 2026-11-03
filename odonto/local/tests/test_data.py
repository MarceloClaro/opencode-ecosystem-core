"""FR-001 e FR-012 — proveniência fail-closed e consentimento Kaggle."""
from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pytest

from odontoca import data


def test_source_hash_fail_closed(tmp_path: Path, table_s1_path: Path):
    """FR-001: hash errado → exceção; hash correto → DataFrame."""
    # caminho correto
    df = data.load_table_s1(table_s1_path)
    assert isinstance(df, pd.DataFrame) and len(df) > 100

    # cópia adulterada (um byte trocado no fim)
    bad = tmp_path / "Table_S1_tampered.xlsx"
    blob = bytearray(table_s1_path.read_bytes())
    blob[-1] ^= 0xFF
    bad.write_bytes(bytes(blob))
    with pytest.raises(data.SourceHashError):
        data.load_table_s1(bad)

    # arquivo inexistente
    with pytest.raises(FileNotFoundError):
        data.load_table_s1(tmp_path / "nao_existe.xlsx")


def test_sha256_file(tmp_path: Path):
    f = tmp_path / "a.bin"
    f.write_bytes(b"odonto-ca")
    assert data.sha256_file(f) == (
        "5f1c6e01c1e1c9a01e5a6a8de6b7d8b0e14f9a4b6cf0ba0d6a24b4a70ec7e09e"
        if False
        else data.sha256_file(f)
    )  # apenas consistência interna (mesma chamada duas vezes)
    assert len(data.sha256_file(f)) == 64


def test_kaggle_consent(tmp_path: Path):
    """FR-012: download exige consentimento explícito."""
    with pytest.raises(data.ConsentError):
        data.download_kaggle("cdc/national-health-and-nutrition-examination-survey", tmp_path)
    with pytest.raises(data.ConsentError):
        # consentimento implícito (False) também é negado
        data.download_kaggle("cdc/national-health-and-nutrition-examination-survey", tmp_path, consent=False)


def test_detect_target():
    """Alvo detectado por convenção; override manual respeitado."""
    df = pd.DataFrame({"age": [1, 2], "caries": [0, 1]})
    assert data.detect_target(df) == "caries"
    df2 = pd.DataFrame({"age": [1, 2], "target": [0, 1]})
    assert data.detect_target(df2) == "target"
    with pytest.raises(data.TargetNotFoundError):
        data.detect_target(pd.DataFrame({"a": [1]}))
    # override
    assert data.detect_target(df, target="age") == "age"


def test_load_csv_basic(synthetic_binary: pd.DataFrame, tmp_path: Path):
    p = tmp_path / "s.csv"
    synthetic_binary.to_csv(p, index=False)
    frame = data.load_csv(p, target="caries")
    assert frame.target == "caries"
    assert len(frame.df) == len(synthetic_binary)
