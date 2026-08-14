# -*- coding: utf-8 -*-
"""Validações de proveniência — SPEC-935-R408.

Funções de gate para o manifesto de fontes: fonte oficial, hash presente,
duplicatas país-ano, valores fabricados (fora de faixa plausível declarada)
e leakage por país em validação cruzada.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_URL = "https://api.worldbank.org/v2/"

# Faixas plausíveis declaradas por indicador (limites generosos para capturar
# valores fabricados sem gerar falso positivo em séries oficiais).
PLAUSIBLE_RANGES = {
    "NY.GDP.PCAP.KD": (50.0, 200_000.0),
    "NY.GDP.PCAP.KD.ZG": (-50.0, 50.0),
    "SE.TER.ENRR": (0.0, 300.0),
    "SE.XPD.TOTL.GD.ZS": (0.0, 30.0),
    "GB.XPD.RSDV.GD.ZS": (0.0, 10.0),
    "SI.POV.GINI": (0.0, 100.0),
    "SP.DYN.LE00.IN": (20.0, 100.0),
    "SP.URB.TOTL.IN.ZS": (0.0, 100.0),
    "NV.IND.MANF.ZS": (0.0, 100.0),
    "BX.KLT.DINV.WD.GD.ZS": (-50.0, 100.0),
    "TX.VAL.TECH.MF.ZS": (0.0, 100.0),
}


def is_official_world_bank_source(url: str) -> bool:
    """Somente a API oficial é aceita como fonte primária."""
    return url.startswith(BASE_URL)


def validate_hash(manifest_path: Path) -> list[str]:
    """Retorna lista de erros de hash no manifesto (vazia se íntegro)."""
    import json

    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    errors = []
    for req in manifest.get("requests", []):
        cache_path = Path(manifest_path).parent / req["cache_file"]
        if not cache_path.exists():
            errors.append(f"cache ausente: {req['cache_file']}")
            continue
        import hashlib

        digest = hashlib.sha256(cache_path.read_bytes()).hexdigest()
        if digest != req["sha256"]:
            errors.append(f"hash divergente: {req['cache_file']}")
    return errors


def find_duplicated_country_year(panel: pd.DataFrame) -> int:
    return int(panel.duplicated(subset=["iso3", "year"]).sum())


def find_fabricated_values(panel: pd.DataFrame) -> pd.DataFrame:
    """Retorna linhas com valores fora das faixas plausíveis declaradas."""
    out = []
    for col, (lo, hi) in PLAUSIBLE_RANGES.items():
        if col not in panel.columns:
            continue
        mask = panel[col].notna() & ~panel[col].between(lo, hi)
        if mask.any():
            bad = panel.loc[mask, ["iso3", "year", col]]
            bad = bad.rename(columns={col: "value"})
            bad["indicator"] = col
            bad["plausible_range"] = f"({lo}, {hi})"
            out.append(bad)
    if not out:
        return pd.DataFrame(columns=["iso3", "year", "value", "indicator", "plausible_range"])
    return pd.concat(out, ignore_index=True)


def country_leakage_train_test(train: pd.DataFrame, test: pd.DataFrame) -> set[str]:
    """Países presentes simultaneamente em treino e teste = leakage."""
    return set(train["iso3"]).intersection(set(test["iso3"]))
