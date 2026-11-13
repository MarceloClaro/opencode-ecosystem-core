# civilization-atlas-skill integration (SPEC-935-R1118)

import json
import os
from pathlib import Path

# Base directory - the civilization-atlas-skill repo
BASE_DIR = Path(__file__).parent

# SKILL metadata
SKILL = {
    "name": "civilization-atlas",
    "description": "Skill de pesquisa histórica e sistemas complexos: comparacao de sociedades, mecanismos, condicoes de transferencia, base rates e decisoes.",
    "version": "1.0.0",
    "license": "MIT",
    "references": "WDI (World Development Indicators, CC BY 4.0); Seshat (global history databank, MIT); NASA GISTEMP (citation required); COW (licença restrita, não redistribuído)",
}

# Base rates - vendorized subset
_BASE_RATES_PATH = BASE_DIR / "base_rates.json"


def base_rates():
    """Retorna base rates vendorizadas do civilization-atlas-skill."""
    if _BASE_RATES_PATH.is_file():
        with open(_BASE_RATES_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


# Query script - simplified version
def query(**kwargs):
    """Executa query reproduzivel com base rates e conhecimento local."""
    rates = base_rates()
    # Retorna estrutura basica para compatibilidade
    return {
        "rates": rates,
        "query": kwargs,
        "source": "civilization-atlas-skill",
    }


# ATTRIBUTION - registered sources with hashes
_ATTRIBUTION_PATH = BASE_DIR / "ATTRIBUTION.md"


def attribution():
    """Retorna registro de atribuicao por fonte."""
    if _ATTRIBUTION_PATH.is_file():
        with open(_ATTRIBUTION_PATH, encoding="utf-8") as f:
            content = f.read()
        # Basico: retorna dict com info de fontes
        return {"content": content, "path": str(_ATTRIBUTION_PATH)}
    return {"content": "", "path": str(_ATTRIBUTION_PATH), "note": "ATTRIBUTION.md nao encontrado"}


# ATTRIBUTION - module level export
ATTRIBUTION = attribution()
