#!/usr/bin/env python3
"""
FinancialDataSource — Dados Financeiros (yfinance, BCB, FRED, World Bank)
===========================================================================
Busca cotações, séries macroeconômicas, indicadores financeiros.

Fontes:
    - yfinance: ações, ETFs, índices, câmbio (gratuito)
    - BCB/SGS: 2.000+ séries — SELIC, IPCA, PIB, câmbio (gratuito)
    - FRED: 800K+ séries macroeconômicas (chave gratuita)
    - World Bank: indicadores globais PIB, população, educação (gratuito)
    - Alpha Vantage: ações, câmbio, cripto (chave gratuita)

Uso:
    from skills.tooling.data_knowledge_hub.financial import FinancialDataSource
    fds = FinancialDataSource()
    result = fds.search("PETR4", source="yfinance")
    result = fds.search("IPCA", source="bcb")
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from .base import DataSource


# ─── Dados Mockados (modo offline) ─────────────────────────

MOCK_DATA = {
    "yfinance": [
        {"symbol": "PETR4.SA", "name": "Petrobras PN", "price": 38.52,
         "change_pct": 1.25, "currency": "BRL", "market": "B3"},
        {"symbol": "VALE3.SA", "name": "Vale ON", "price": 68.90,
         "change_pct": -0.45, "currency": "BRL", "market": "B3"},
        {"symbol": "ITUB4.SA", "name": "Itaú Unibanco PN", "price": 32.15,
         "change_pct": 0.80, "currency": "BRL", "market": "B3"},
    ],
    "bcb": [
        {"serie": "IPCA", "codigo": 433, "valor": 0.38, "unidade": "%",
         "periodo": "Jun/2024", "descricao": "IPCA - Variação mensal"},
        {"serie": "SELIC", "codigo": 4390, "valor": 10.50, "unidade": "% a.a.",
         "periodo": "Jul/2024", "descricao": "Taxa Selic anual"},
        {"serie": "PIB", "codigo": 1207, "valor": 2892.0, "unidade": "R$ bilhões",
         "periodo": "2024", "descricao": "PIB a preços de mercado"},
    ],
    "fred": [
        {"series_id": "GDP", "name": "Real Gross Domestic Product",
         "value": 22997.5, "unit": "Billions USD", "period": "2024 Q2"},
        {"series_id": "UNRATE", "name": "Unemployment Rate",
         "value": 4.1, "unit": "%", "period": "Jun/2024"},
        {"series_id": "CPIAUCSL", "name": "CPI All Urban Consumers",
         "value": 314.5, "unit": "Index", "period": "Jun/2024"},
    ],
    "world_bank": [
        {"indicator": "NY.GDP.MKTP.CD", "name": "GDP (current US$)",
         "country": "Brazil", "value": 2175.0, "year": 2023, "unit": "Bilhões USD"},
        {"indicator": "SP.POP.TOTL", "name": "Population, total",
         "country": "Brazil", "value": 216.0, "year": 2023, "unit": "Milhões"},
        {"indicator": "NY.GDP.PCAP.CD", "name": "GDP per capita",
         "country": "Brazil", "value": 10050.0, "year": 2023, "unit": "USD"},
    ],
    "alpha_vantage": [
        {"symbol": "PETR4.SA", "name": "Petrobras PN",
         "price": 38.52, "change": 0.48, "change_pct": 1.26},
    ],
}

SOURCE_NAMES = {
    "yfinance": "Yahoo Finance",
    "bcb": "Banco Central do Brasil (SGS)",
    "fred": "Federal Reserve Economic Data (FRED)",
    "world_bank": "World Bank Open Data",
    "alpha_vantage": "Alpha Vantage",
}


class FinancialDataSource(DataSource):
    """
    Fonte de dados financeiros: yfinance, BCB/SGS, FRED, World Bank.
    """

    name = "financial"

    def __init__(self):
        super().__init__()
        self._fred_api_key = os.environ.get("FRED_API_KEY", "")
        self._alpha_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
        self._sources = {
            "yfinance": self._search_yfinance,
            "bcb": self._search_bcb,
            "fred": self._search_fred,
            "world_bank": self._search_world_bank,
            "alpha_vantage": self._search_alpha_vantage,
        }

    def search(
        self, query: str, source: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        start = time.time()

        if source and source in self._sources:
            return self._sources[source](query, start)

        # Roteamento automático por palavras-chave
        ql = query.lower()
        if any(w in ql for w in ["ação", "ação", "stock", "share", "petr", "vale",
                                  "itub", "bbas", "b3sa", "^bvsp"]):
            return self._search_yfinance(query, start)
        elif any(w in ql for w in ["ipca", "selic", "inflação", "juros",
                                    "cambio", "câmbio", "bcb", "bacen"]):
            return self._search_bcb(query, start)
        elif any(w in ql for w in ["gdp", "unemployment", "cpi", "fed",
                                    "treasury", "fred"]):
            return self._search_fred(query, start)
        elif any(w in ql for w in ["world bank", "pib", "gdp per capita",
                                    "population", "indicador global"]):
            return self._search_world_bank(query, start)
        elif any(w in ql for w in ["alpha", "vantage", "technical"]):
            return self._search_alpha_vantage(query, start)
        else:
            # Fallback: yfinance
            return self._search_yfinance(query, start)

    # ─── yfinance ───────────────────────────────────────────

    def _search_yfinance(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            import yfinance as yf

            # Tenta como ticker
            ticker_str = query.strip().upper()
            # Remove sufixo .SA se não tiver
            if len(ticker_str) <= 5 and not ticker_str.endswith(".SA"):
                ticker_str += ".SA"

            ticker = yf.Ticker(ticker_str)
            info = ticker.info or {}

            results = []
            if info and "regularMarketPrice" in info:
                results.append({
                    "symbol": info.get("symbol", ticker_str),
                    "name": info.get("longName", info.get("shortName", ticker_str)),
                    "price": info.get("regularMarketPrice", 0),
                    "change": info.get("regularMarketChange", 0),
                    "change_pct": info.get("regularMarketChangePercent", 0),
                    "currency": info.get("currency", "BRL"),
                    "market": info.get("exchange", "B3"),
                    "source": "yfinance",
                })

            if not results:
                # Busca geral
                try:
                    search_results = yf.Search(ticker_str)
                    for s in getattr(search_results, "quotes", []):
                        results.append({
                            "symbol": s.get("symbol", ""),
                            "name": s.get("longname", s.get("shortname", "")),
                            "exchange": s.get("exchange", ""),
                            "type": s.get("quoteType", ""),
                            "source": "yfinance",
                        })
                except Exception:
                    pass

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "yfinance", results,
                                     "online" if success else "offline", elapsed)

        except ImportError:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "yfinance", MOCK_DATA["yfinance"],
                                     "offline", elapsed)
        except Exception as exc:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "yfinance", MOCK_DATA["yfinance"],
                                     "offline", elapsed)

    # ─── BCB/SGS ────────────────────────────────────────────

    def _search_bcb(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            # Mapear termos para séries BCB
            series_map = {
                "ipca": 433,
                "selic": 4390,
                "pib": 1207,
                "cambio": 1,
                "câmbio": 1,
                "dolar": 1,
                "dólar": 1,
            }

            ql = query.lower()
            serie_cod = None
            for term, cod in series_map.items():
                if term in ql:
                    serie_cod = cod
                    break

            if not serie_cod:
                serie_cod = 433  # IPCA default

            url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie_cod}/dados/ultimos/5"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for item in data:
                results.append({
                    "serie": query,
                    "codigo": serie_cod,
                    "valor": float(item.get("valor", 0)),
                    "data": item.get("data", ""),
                    "fonte": "BCB/SGS",
                })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "bcb", results,
                                     "online" if success else "offline", elapsed)

        except Exception as exc:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "bcb", MOCK_DATA["bcb"],
                                     "offline", elapsed)

    # ─── FRED ────────────────────────────────────────────────

    def _search_fred(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            series_map = {
                "gdp": "GDP",
                "unemployment": "UNRATE",
                "cpi": "CPIAUCSL",
                "fed rate": "FEDFUNDS",
                "treasury": "DGS10",
            }

            ql = query.lower()
            series_id = None
            for term, sid in series_map.items():
                if term in ql:
                    series_id = sid
                    break

            if not series_id:
                series_id = "GDP"

            api_key = self._fred_api_key or "YOUR_FRED_API_KEY"
            url = (
                f"https://api.stlouisfed.org/fred/series/observations"
                f"?series_id={series_id}&api_key={api_key}"
                f"&file_type=json&sort_order=desc&limit=5"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for obs in data.get("observations", []):
                val = obs.get("value", ".")
                if val != ".":
                    results.append({
                        "series_id": series_id,
                        "date": obs.get("date", ""),
                        "value": float(val),
                        "source": "FRED",
                    })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "fred", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "fred", MOCK_DATA["fred"],
                                     "offline", elapsed)

    # ─── World Bank ──────────────────────────────────────────

    def _search_world_bank(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            indicators = {
                "gdp": "NY.GDP.MKTP.CD",
                "population": "SP.POP.TOTL",
                "gdp per capita": "NY.GDP.PCAP.CD",
                "inflation": "FP.CPI.TOTL.ZG",
            }

            ql = query.lower()
            indicator = None
            for term, ind in indicators.items():
                if term in ql:
                    indicator = ind
                    break

            if not indicator:
                indicator = "NY.GDP.MKTP.CD"

            # Buscar Brasil
            url = f"https://api.worldbank.org/v2/country/BR/indicator/{indicator}?format=json&per_page=5"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            if len(data) > 1:
                for item in data[1]:
                    if item.get("value"):
                        results.append({
                            "indicator": indicator,
                            "country": "Brazil",
                            "value": float(item["value"]),
                            "year": item.get("date", ""),
                            "source": "World Bank",
                        })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "world_bank", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "world_bank", MOCK_DATA["world_bank"],
                                     "offline", elapsed)

    # ─── Alpha Vantage ───────────────────────────────────────

    def _search_alpha_vantage(
        self, query: str, start_time: float
    ) -> Dict[str, Any]:
        try:
            api_key = self._alpha_key or "demo"
            symbol = query.strip().upper()
            if not symbol.endswith(".SA"):
                symbol += ".SA"

            url = (
                f"https://www.alphavantage.co/query"
                f"?function=GLOBAL_QUOTE"
                f"&symbol={symbol}&apikey={api_key}"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            quote = data.get("Global Quote", {})
            if quote:
                results.append({
                    "symbol": quote.get("01. symbol", symbol),
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_pct": float(quote.get("10. change percent", "0%").replace("%", "")),
                    "volume": quote.get("06. volume", 0),
                    "source": "Alpha Vantage",
                })

            elapsed = (time.time() - start_time) * 1000
            success = len(results) > 0
            self._record_query(elapsed, success)
            return self._make_result(query, "alpha_vantage", results,
                                     "online" if success else "offline", elapsed)

        except Exception:
            elapsed = (time.time() - start_time) * 1000
            self._record_query(elapsed, False, offline=True)
            return self._make_result(query, "alpha_vantage", MOCK_DATA["alpha_vantage"],
                                     "offline", elapsed)
