# -*- coding: utf-8 -*-
"""
DatajudClient — Cliente para API Pública Datajud do CNJ
=========================================================
Acesso a dados processuais dos 27 Tribunais de Justiça estaduais brasileiros.

Base URL: https://api-publica.datajud.cnj.jus.br
Formato: OpenAPI 3.0 / JSON

Resolução CNJ n. 331/2020 — Base Nacional de Dados do Poder Judiciário
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, date
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

logger = logging.getLogger("datajud")

# ── Tribunais disponíveis na API Datajud ────────────────────────────────

TRIBUNAIS: Dict[str, str] = {
    "tjac": "Acre",
    "tjal": "Alagoas",
    "tjam": "Amazonas",
    "tjap": "Amapá",
    "tjba": "Bahia",
    "tjce": "Ceará",
    "tjdf": "Distrito Federal e Territórios",
    "tjes": "Espírito Santo",
    "tjgo": "Goiás",
    "tjma": "Maranhão",
    "tjmg": "Minas Gerais",
    "tjms": "Mato Grosso do Sul",
    "tjmt": "Mato Grosso",
    "tjpa": "Pará",
    "tjpb": "Paraíba",
    "tjpe": "Pernambuco",
    "tjpi": "Piauí",
    "tjpr": "Paraná",
    "tjrj": "Rio de Janeiro",
    "tjrn": "Rio Grande do Norte",
    "tjro": "Rondônia",
    "tjrr": "Roraima",
    "tjrs": "Rio Grande do Sul",
    "tjsc": "Santa Catarina",
    "tjse": "Sergipe",
    "tjsp": "São Paulo",
    "tjto": "Tocantins",
}

# ── Dados mockados para modo offline ────────────────────────────────────

MOCK_PROCESSOS: Dict[str, List[Dict[str, Any]]] = {
    "tjsp": [
        {
            "id": "mock-tjsp-001",
            "tribunal": "tjsp",
            "numeroProcesso": "1000001-12.2020.8.26.0001",
            "dataAjuizamento": "2020-01-15T10:00:00Z",
            "grau": "primeiro",
            "nivelSigilo": 0,
            "classe": {"codigo": 7, "nome": "Procedimento Comum Cível"},
            "assuntos": [
                {"codigo": 1234, "nome": "Obrigação de Fazer / Não Fazer"},
                {"codigo": 5678, "nome": "Contratos Bancários"},
            ],
            "orgaoJulgador": {"codigo": 1, "nome": "1ª Vara Cível"},
            "movimentos": [
                {"codigo": 1, "nome": "Distribuição", "dataHora": "2020-01-15T10:00:00Z"},
                {"codigo": 3, "nome": "Despacho", "dataHora": "2020-02-01T14:00:00Z"},
                {"codigo": 51, "nome": "Sentença", "dataHora": "2020-06-10T09:00:00Z",
                 "complementosTabelados": [{"codigo": 1, "descricao": "Procedente", "valor": 1, "nome": "Resultado"}]},
            ],
            "dataHoraUltimaAtualizacao": "2020-06-10T09:00:00Z",
        }
    ],
    "tjrj": [
        {
            "id": "mock-tjrj-001",
            "tribunal": "tjrj",
            "numeroProcesso": "0000001-12.2021.8.19.0001",
            "dataAjuizamento": "2021-03-20T08:30:00Z",
            "grau": "segundo",
            "nivelSigilo": 0,
            "classe": {"codigo": 198, "nome": "Apelação Cível"},
            "assuntos": [
                {"codigo": 7890, "nome": "Responsabilidade Civil do Estado"},
            ],
            "orgaoJulgador": {"codigo": 10, "nome": "2ª Câmara Cível"},
            "movimentos": [
                {"codigo": 1, "nome": "Distribuição", "dataHora": "2021-03-20T08:30:00Z"},
                {"codigo": 26, "nome": "Inclusão em Pauta", "dataHora": "2021-05-01T10:00:00Z"},
                {"codigo": 131, "nome": "Julgamento", "dataHora": "2021-05-15T14:00:00Z",
                 "complementosTabelados": [{"codigo": 4, "descricao": "Provimento Parcial", "valor": 4, "nome": "Resultado"}]},
            ],
            "dataHoraUltimaAtualizacao": "2021-05-15T14:00:00Z",
        }
    ],
}


@dataclass
class DatajudProcess:
    """Representação de um processo judicial da API Datajud."""
    id: str
    tribunal: str
    numero_processo: str
    data_ajuizamento: Optional[datetime] = None
    grau: str = ""
    nivel_sigilo: int = 0
    classe: Optional[Dict[str, Any]] = None
    assuntos: List[Dict[str, Any]] = field(default_factory=list)
    orgao_julgador: Optional[Dict[str, Any]] = None
    movimentos: List[Dict[str, Any]] = field(default_factory=list)
    data_ultima_atualizacao: Optional[datetime] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "DatajudProcess":
        """Constrói a partir do JSON da API Datajud."""
        def _parse_dt(val: Optional[str]) -> Optional[datetime]:
            if val:
                try:
                    return datetime.fromisoformat(val.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    return None
            return None

        return cls(
            id=data.get("id", ""),
            tribunal=(data.get("tribunal") or "").lower() if data.get("tribunal") else "",
            numero_processo=data.get("numeroProcesso", ""),
            data_ajuizamento=_parse_dt(data.get("dataAjuizamento")),
            grau=data.get("grau", ""),
            nivel_sigilo=data.get("nivelSigilo", 0),
            classe=data.get("classe"),
            assuntos=data.get("assuntos", []),
            orgao_julgador=data.get("orgaoJulgador"),
            movimentos=data.get("movimentos", []),
            data_ultima_atualizacao=_parse_dt(data.get("dataHoraUltimaAtualizacao")),
        )

    @property
    def tribunal_nome(self) -> str:
        return TRIBUNAIS.get(self.tribunal, self.tribunal.upper())

    @property
    def assunto_principal(self) -> Optional[str]:
        if self.assuntos:
            return self.assuntos[0].get("nome")
        return None

    @property
    def classe_nome(self) -> Optional[str]:
        if self.classe:
            return self.classe.get("nome")
        return None

    @property
    def resultado(self) -> Optional[str]:
        """Extrai o resultado da decisão a partir do último movimento relevante."""
        for mov in reversed(self.movimentos):
            complementos = mov.get("complementosTabelados", [])
            for comp in complementos:
                desc = comp.get("descricao", "")
                if desc.lower() in ("procedente", "improcedente", "provimento",
                                    "provimento parcial", "denegado", "parcialmente procedente"):
                    return desc
        return None

    @property
    def ementa_texto(self) -> str:
        """Gera uma ementa sintética a partir dos dados do processo."""
        partes = [
            f"Processo {self.numero_processo} ({self.tribunal_nome})",
        ]
        if self.classe_nome:
            partes.append(f"Classe: {self.classe_nome}")
        if self.assunto_principal:
            partes.append(f"Assunto: {self.assunto_principal}")
        if self.resultado:
            partes.append(f"Resultado: {self.resultado}")
        return " — ".join(partes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tribunal": self.tribunal,
            "numero_processo": self.numero_processo,
            "grau": self.grau,
            "classe": self.classe,
            "assuntos": self.assuntos,
            "resultado": self.resultado,
            "ementa": self.ementa_texto,
        }


class DatajudClient:
    """Cliente para API pública Datajud do CNJ.

    Modos de operação:
      - online: faz requisições HTTP reais à API Datajud
      - offline (mock): usa dados mockados internos (útil para testes e demo)

    Args:
        api_key: Chave de autenticação (Authorization header).
        base_url: URL base da API.
        offline: Se True, usa dados mockados em vez de requisições reais.
        cache_size: Tamanho máximo do cache LRU.
    """

    BASE_URL = "https://api-publica.datajud.cnj.us.br"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        offline: bool = False,
        cache_size: int = 128,
    ):
        self.api_key = api_key or os.environ.get("DATAJUD_API_KEY", "")
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.offline = offline
        self._cache: Dict[str, Tuple[float, List[DatajudProcess]]] = {}
        self._cache_max = cache_size
        self._session = None

    # ── Cache ────────────────────────────────────────────────────────────

    def _cache_get(self, key: str) -> Optional[List[DatajudProcess]]:
        entry = self._cache.get(key)
        if entry:
            ts, data = entry
            if time.time() - ts < 300:  # 5 min TTL
                return data
            del self._cache[key]
        return None

    def _cache_set(self, key: str, data: List[DatajudProcess]) -> None:
        if len(self._cache) >= self._cache_max:
            # LRU simplificado: limpa metade
            keys = list(self._cache.keys())
            for k in keys[: len(keys) // 2]:
                del self._cache[k]
        self._cache[key] = (time.time(), data)

    # ── Requisição HTTP ──────────────────────────────────────────────────

    def _request(self, tribunal: str, query: str) -> List[Dict[str, Any]]:
        """Faz requisição à API Datajud (ou retorna mock)."""
        if self.offline:
            return self._mock_search(tribunal, query)

        if not self.api_key:
            logger.warning("DATAJUD_API_KEY não configurada — usando modo offline")
            return self._mock_search(tribunal, query)

        import urllib.request
        import urllib.error

        endpoint = f"/api_publica_{tribunal}/_search"
        url = f"{self.base_url}{endpoint}?query={quote(query)}"

        req = urllib.request.Request(
            url,
            headers={"Authorization": self.api_key, "Accept": "application/json"},
            method="GET",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("data", data.get("hits", data.get("results", [])))
        except urllib.error.HTTPError as e:
            if e.code == 401:
                logger.error("Datajud: credencial inválida (401)")
                raise PermissionError("Credencial Datajud inválida — verifique DATAJUD_API_KEY")
            elif e.code == 429:
                logger.warning("Datajud: rate limit excedido (429)")
                raise RuntimeError("Rate limit excedido — aguarde antes de novas requisições")
            elif e.code == 404:
                logger.warning(f"Datajud: tribunal {tribunal} não encontrado (404)")
                return []
            else:
                logger.error(f"Datajud: erro HTTP {e.code} — {e.reason}")
                raise
        except urllib.error.URLError as e:
            logger.warning(f"Datajud: falha de conexão — {e.reason}. Usando fallback offline")
            return self._mock_search(tribunal, query)

    # ── Dados Mockados ───────────────────────────────────────────────────

    def _mock_search(self, tribunal: str, query: str) -> List[Dict[str, Any]]:
        """Retorna dados mockados simulando resposta da API."""
        processos = MOCK_PROCESSOS.get(tribunal, [])
        if not query:
            return processos
        # Filtro textual simples
        query_lower = query.lower()
        resultados = []
        for proc in processos:
            texto = json.dumps(proc).lower()
            if query_lower in texto:
                resultados.append(proc)
        return resultados

    # ── Métodos públicos ─────────────────────────────────────────────────

    def search(self, tribunal: str, query: str = "") -> List[DatajudProcess]:
        """Pesquisa processos em um tribunal específico.

        Args:
            tribunal: Sigla do tribunal (ex.: 'tjsp', 'tjrj', 'tjmg').
            query: Termo de pesquisa.

        Returns:
            Lista de DatajudProcess encontrados.
        """
        tribunal = tribunal.lower().strip()
        if tribunal not in TRIBUNAIS:
            raise ValueError(
                f"Tribunal '{tribunal}' não reconhecido. "
                f"Use uma sigla válida: {', '.join(sorted(TRIBUNAIS.keys()))}"
            )

        cache_key = f"{tribunal}:{query}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        raw_data = self._request(tribunal, query)
        results = [DatajudProcess.from_api(item) for item in raw_data]
        self._cache_set(cache_key, results)
        return results

    def search_all(self, query: str = "", tribunais: Optional[List[str]] = None) -> Dict[str, List[DatajudProcess]]:
        """Pesquisa processos em múltiplos tribunais.

        Args:
            query: Termo de pesquisa.
            tribunais: Lista de tribunais a consultar (None = todos).

        Returns:
            Dict {tribunal: [DatajudProcess, ...]}.
        """
        tribunais = tribunais or list(TRIBUNAIS.keys())
        resultados: Dict[str, List[DatajudProcess]] = {}
        for sigla in tribunais:
            try:
                resultados[sigla] = self.search(sigla, query)
            except (PermissionError, RuntimeError) as e:
                logger.error(f"Erro ao consultar {sigla}: {e}")
                resultados[sigla] = []
            except Exception as e:
                logger.warning(f"Falha inesperada ao consultar {sigla}: {e}")
                resultados[sigla] = []
        return resultados

    def get_process(self, numero_processo: str, tribunal: str) -> Optional[DatajudProcess]:
        """Busca um processo específico por número.

        Args:
            numero_processo: Número do processo (formato CNJ).
            tribunal: Sigla do tribunal.

        Returns:
            DatajudProcess ou None se não encontrado.
        """
        results = self.search(tribunal, numero_processo)
        for proc in results:
            if proc.numero_processo == numero_processo:
                return proc
        return None

    def list_tribunals(self) -> List[Dict[str, str]]:
        """Lista todos os tribunais disponíveis."""
        return [
            {"sigla": sigla, "nome": nome}
            for sigla, nome in sorted(TRIBUNAIS.items())
        ]

    def get_available_tribunals(self) -> List[str]:
        """Retorna lista de siglas de tribunais disponíveis."""
        return sorted(TRIBUNAIS.keys())
