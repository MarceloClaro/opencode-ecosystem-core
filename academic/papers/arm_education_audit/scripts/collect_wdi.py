# -*- coding: utf-8 -*-
"""Coletor WDI com cache imutável — SPEC-935-R408.

Baixa indicadores oficiais do World Bank (api.worldbank.org/v2), preserva a
resposta bruta em data/raw com URL, timestamp UTC, status HTTP e SHA-256, e
permite reconstrução offline do painel processado a partir do cache.

Uso:
    python3 scripts/collect_wdi.py            # coleta (ou reutiliza cache)
    python3 scripts/collect_wdi.py --offline  # força operação offline
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pandas as pd

AUDIT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = AUDIT_DIR / "data" / "raw"
PROC_DIR = AUDIT_DIR / "data" / "processed"
MANIFEST_PATH = RAW_DIR / "manifest.json"

BASE_URL = "https://api.worldbank.org/v2/"

COUNTRIES = ["ARG", "BRA", "CHL", "CHN", "KOR", "SGP", "VNM"]
YEARS_START, YEARS_END = 1960, 2023

INDICATORS = {
    "NY.GDP.PCAP.KD": "PIB per capita (US$ constantes)",
    "NY.GDP.PCAP.KD.ZG": "Crescimento anual do PIB per capita (%)",
    "SE.TER.ENRR": "Matrícula bruta no ensino terciário (%)",
    "SE.XPD.TOTL.GD.ZS": "Gasto público em educação (% do PIB)",
    "GB.XPD.RSDV.GD.ZS": "Pesquisa e desenvolvimento (% do PIB)",
    "SI.POV.GINI": "Índice de Gini",
    "SP.DYN.LE00.IN": "Expectativa de vida ao nascer (anos)",
    "SP.URB.TOTL.IN.ZS": "População urbana (% do total)",
    "NV.IND.MANF.ZS": "Manufatura (% do PIB)",
    "BX.KLT.DINV.WD.GD.ZS": "IED líquido (% do PIB)",
    "TX.VAL.TECH.MF.ZS": "Exportações de alta tecnologia (% das manufaturadas)",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_official_world_bank_source(url: str) -> bool:
    return url.startswith(BASE_URL)


def _indicator_url(indicator: str) -> str:
    params = urlencode(
        {"date": f"{YEARS_START}:{YEARS_END}", "format": "json", "per_page": 1000}
    )
    return f"{BASE_URL}country/{';'.join(COUNTRIES)}/indicator/{indicator}?{params}"


def fetch_indicator(indicator: str, session: Any) -> dict:
    """Baixa um indicador e devolve registro de cache com resposta bruta."""
    url = _indicator_url(indicator)
    resp = session.get(url, timeout=60)
    raw = resp.content
    record = {
        "indicator": indicator,
        "url": url,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status_http": resp.status_code,
        "sha256": sha256_bytes(raw),
        "cache_file": f"wdi_{indicator}.json",
        "bytes": len(raw),
    }
    (RAW_DIR / record["cache_file"]).write_bytes(raw)
    return record


def load_cached_raw() -> dict:
    """Carrega manifest + respostas brutas do cache (offline)."""
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"cache ausente: {MANIFEST_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    payload = {}
    for req in manifest["requests"]:
        cache_path = RAW_DIR / req["cache_file"]
        if not cache_path.exists():
            raise FileNotFoundError(f"cache ausente: {cache_path}")
        data = cache_path.read_bytes()
        assert sha256_bytes(data) == req["sha256"], f"hash divergente: {req['cache_file']}"
        payload[req["indicator"]] = json.loads(data.decode("utf-8"))
    return manifest, payload


def parse_wdi_payload(payload: list) -> pd.DataFrame:
    """Converte resposta JSON da API em DataFrame país-ano-valor."""
    rows = []
    if not isinstance(payload, list) or len(payload) < 2:
        return pd.DataFrame(columns=["iso3", "year", "indicator", "value"])
    for item in payload[1]:
        rows.append(
            {
                "iso3": item.get("countryiso3code"),
                "year": int(item.get("date")),
                "indicator": item.get("indicator", {}).get("id"),
                "value": item.get("value"),
            }
        )
    return pd.DataFrame(rows)


def load_cached_panel() -> pd.DataFrame:
    """Reconstrói o painel processado a partir do cache (offline)."""
    proc_csv = PROC_DIR / "panel_wdi_1960_2023.csv"
    if proc_csv.exists():
        return pd.read_csv(proc_csv)
    manifest, payload = load_cached_raw()
    frames = [parse_wdi_payload(payload[ind]) for ind in payload]
    return pd.concat(frames, ignore_index=True)


def build_panel() -> pd.DataFrame:
    """Monta grade 7×64 com uma linha por país-ano e valores observados."""
    manifest, payload = load_cached_raw()
    frames = [parse_wdi_payload(payload[ind]) for ind in payload]
    long = pd.concat(frames, ignore_index=True)

    idx = pd.MultiIndex.from_product([COUNTRIES, range(YEARS_START, YEARS_END + 1)],
                                     names=["iso3", "year"])
    panel = pd.DataFrame(index=idx).reset_index()
    wide = long.pivot_table(index=["iso3", "year"], columns="indicator",
                            values="value", aggfunc="first").reset_index()
    panel = panel.merge(wide, on=["iso3", "year"], how="left")
    # ausência permanece ausente (NaN) — nunca vira 0
    return panel


def variable_counts(panel: pd.DataFrame) -> dict:
    cols = [c for c in panel.columns if c not in {"iso3", "year"}]
    return {
        "columns": cols,
        "n_observed": {c: int(panel[c].notna().sum()) for c in cols},
        "n_missing": {c: int(panel[c].isna().sum()) for c in cols},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Coleta WDI com cache")
    parser.add_argument("--offline", action="store_true", help="usa apenas o cache")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROC_DIR.mkdir(parents=True, exist_ok=True)

    if args.offline:
        manifest, _ = load_cached_raw()
    else:
        # A reconstrução offline não deve exigir a biblioteca HTTP nem rede;
        # a dependência é carregada somente no caminho de coleta online.
        import requests

        session = requests.Session()
        existing = {}
        if MANIFEST_PATH.exists():
            existing = {r["indicator"]: r for r in
                        json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["requests"]}
        records = []
        for ind in INDICATORS:
            if ind in existing:
                records.append(existing[ind])
                print(f"[cache] {ind}")
                continue
            record = fetch_indicator(ind, session)
            records.append(record)
            print(f"[fetch] {ind} ({record['bytes']} bytes, {record['status_http']})")
        manifest = {
            "source": BASE_URL,
            "countries": COUNTRIES,
            "period": [YEARS_START, YEARS_END],
            "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "requests": records,
        }
        MANIFEST_PATH.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    panel = build_panel()
    panel.to_csv(PROC_DIR / "panel_wdi_1960_2023.csv", index=False)
    counts = variable_counts(panel)
    (PROC_DIR / "variable_counts.json").write_text(
        json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"painel: {len(panel)} linhas ({len(COUNTRIES)}×{YEARS_END-YEARS_START+1})")
    for col in counts["columns"]:
        print(f"  {col}: n={counts['n_observed'][col]}")


if __name__ == "__main__":
    main()
