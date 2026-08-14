#!/usr/bin/env python3
"""Download expandido (R412) — WDI + WGI para todos os países com cache imutável.

- Baixa indicadores via API oficial do Banco Mundial (`country/all`).
- Salva JSON bruto em data/raw_expandido/wdi_<IND>.json.
- Mantém manifest_expandido.json com URL, timestamp UTC, status HTTP, SHA-256.
- Não altera os arquivos do R408 (data/raw/), preservando auditoria histórica.
- Se o cache já existe e o hash confere, reutiliza (execução offline).
"""

import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent
RAW_EXP = AUDIT / "data" / "raw_expandido"
MANIFEST = RAW_EXP / "manifest_expandido.json"
PER_PAGE = 20000
DATE_RANGE = "1960:2023"

INDICADORES_BASE = [
    "NY.GDP.PCAP.KD",        # PIB per capita (US$ constantes)
    "NY.GDP.PCAP.KD.ZG",     # crescimento PIB per capita
    "SE.TER.ENRR",           # matrícula terciária (% bruto)
    "SE.XPD.TOTL.GD.ZS",     # gasto público educacional (% PIB)
    "GB.XPD.RSDV.GD.ZS",     # P&D (% PIB)
    "SI.POV.GINI",           # Gini
    "SP.DYN.LE00.IN",        # expectativa de vida
    "SP.URB.TOTL.IN.ZS",     # urbanização
    "NV.IND.MANF.ZS",        # manufatura (% PIB)
    "BX.KLT.DINV.WD.GD.ZS",  # investimento direto estrangeiro (% PIB)
    "TX.VAL.TECH.MF.ZS",     # exportação alta tecnologia (% exportações)
]

INDICADORES_WGI = [
    "CC.EST",  # controle da corrupção
    "GE.EST",  # efetividade governamental
    "PV.EST",  # estabilidade política
    "RQ.EST",  # qualidade regulatória
    "RL.EST",  # estado de direito
    "VA.EST",  # voz e prestação de contas
]

# O WGI vive no source 3 da API v2 (não no banco WDI principal); os IDs usam o
# prefixo GOV_WGI_ e o endpoint responde em country/all/indicator sem `date`
# (cobertura 1996-2024 implícita).
WGI_PREFIX = "GOV_WGI_"

URL_TEMPLATE = (
    "https://api.worldbank.org/v2/country/all/indicator/{ind}?"
    "date={date}&format=json&per_page={per_page}"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {
        "source": "https://api.worldbank.org/v2 (WDI + WGI)",
        "scope": "all countries (agregados mantidos no bruto; filtrados no painel)",
        "period": DATE_RANGE,
        "collected_at": None,
        "requests": [],
    }


def save_manifest(manifest: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def fetch_with_cache(indicator: str) -> tuple[str, dict]:
    """Baixa o indicador ou reutiliza cache. Retorna (cache_file, request_meta)."""
    if indicator in INDICADORES_WGI:
        url = URL_TEMPLATE.format(
            ind=WGI_PREFIX + indicator, date="1996:2023", per_page=PER_PAGE
        )
    else:
        url = URL_TEMPLATE.format(ind=indicator, date=DATE_RANGE, per_page=PER_PAGE)
    cache_file = f"wdi_{indicator}.json"
    path = RAW_EXP / cache_file

    if path.exists():
        return cache_file, {
            "indicator": indicator,
            "url": url,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "status_http": 200,
            "sha256": sha256_file(path),
            "cache_file": cache_file,
            "bytes": path.stat().st_size,
            "cache_reused": True,
        }

    RAW_EXP.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "opencode-ecosystem/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        status = resp.status
        body = resp.read()
        time.sleep(0.3)  # cortesia à API

    if status != 200:
        raise RuntimeError(f"HTTP {status} para {indicator}")

    path.write_bytes(body)
    return cache_file, {
        "indicator": indicator,
        "url": url,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status_http": status,
        "sha256": sha256_file(path),
        "cache_file": cache_file,
        "bytes": path.stat().st_size,
        "cache_reused": False,
    }


def main() -> int:
    manifest = load_manifest()
    indicadores = INDICADORES_BASE + INDICADORES_WGI
    existentes = {r["indicator"] for r in manifest["requests"]}
    for ind in indicadores:
        if ind in existentes:
            print(f"[cache] {ind}")
            continue
        try:
            cache_file, meta = fetch_with_cache(ind)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERRO] {ind}: {exc}", file=sys.stderr)
            return 1
        # remove entrada antiga se houver e anexa a nova
        manifest["requests"] = [r for r in manifest["requests"] if r["indicator"] != ind]
        manifest["requests"].append(meta)
        print(f"[ok] {ind} ({meta['bytes']} bytes, sha256={meta['sha256'][:12]}…)")
        save_manifest(manifest)

    manifest["collected_at"] = datetime.now(timezone.utc).isoformat()
    manifest["n_indicadores"] = len(manifest["requests"])
    save_manifest(manifest)
    print(f"\nManifest expandido: {len(manifest['requests'])} indicadores")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
