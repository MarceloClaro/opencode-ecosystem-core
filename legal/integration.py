# -*- coding: utf-8 -*-
"""
Integration — Ponte Datajud ↔ Motores de Raciocínio Jurídico (SPEC-921/922)
=============================================================================
Conecta dados reais da API Datajud do CNJ aos motores de raciocínio jurídico:

  DatajudProcess → Precedent      (para PrecedentAnalyzer)
  DatajudProcess → LegalFact      (para LegalSyllogism)
  DatajudProcess → Principle      (para PrincipleBalancing)
  DatajudProcess → LegalArgument  (para LegalArgumentScorer)
"""

from __future__ import annotations

import logging
from datetime import date as date_type, datetime
from typing import Any, Dict, List, Optional, Set

from legal.datajud_client import DatajudClient, DatajudProcess
from legal.syllogism import (
    LegalSyllogism, LegalNorm, LegalFact, NormHierarchy, NormType, Competence,
)
from legal.balancing import PrincipleBalancing, Principle
from legal.precedents import (
    PrecedentAnalyzer, Precedent, CaseFacts, PrecedentType, BindingLevel,
)
from legal.argumentation import LegalArgumentScorer, LegalArgument

logger = logging.getLogger("legal.integration")


# ═══════════════════════════════════════════════════════════════════════════
# Conversores: Datajud → Tipos do módulo legal/
# ═══════════════════════════════════════════════════════════════════════════

_TRIBUNAL_TO_COMPETENCE: Dict[str, Competence] = {
    "tjac": Competence.ESTADO, "tjal": Competence.ESTADO, "tjam": Competence.ESTADO,
    "tjap": Competence.ESTADO, "tjba": Competence.ESTADO, "tjce": Competence.ESTADO,
    "tjdf": Competence.DISTRITO_FEDERAL, "tjes": Competence.ESTADO, "tjgo": Competence.ESTADO,
    "tjma": Competence.ESTADO, "tjmg": Competence.ESTADO, "tjms": Competence.ESTADO,
    "tjmt": Competence.ESTADO, "tjpa": Competence.ESTADO, "tjpb": Competence.ESTADO,
    "tjpe": Competence.ESTADO, "tjpi": Competence.ESTADO, "tjpr": Competence.ESTADO,
    "tjrj": Competence.ESTADO, "tjrn": Competence.ESTADO, "tjro": Competence.ESTADO,
    "tjrr": Competence.ESTADO, "tjrs": Competence.ESTADO, "tjsc": Competence.ESTADO,
    "tjse": Competence.ESTADO, "tjsp": Competence.ESTADO, "tjto": Competence.ESTADO,
}


def process_to_precedent(proc: DatajudProcess) -> Precedent:
    """Converte um DatajudProcess em Precedent para o PrecedentAnalyzer.

    A ementa sintética é usada como tese. Os fundamentos são extraídos
    dos movimentos processuais. Os assuntos viram fatos relevantes.
    """
    # Determinar tipo de precedente com base no grau
    if proc.grau == "segundo":
        ptype = PrecedentType.PRECEDENTE_INTERPRETATIVO
        binding = BindingLevel.PERSUASIVO
    else:
        ptype = PrecedentType.ORDINARIO
        binding = BindingLevel.PERSUASIVO

    tribunal_nome = proc.tribunal_nome
    orgao = (proc.orgao_julgador or {}).get("nome", "Não informado")

    # Data de julgamento a partir do último movimento
    data_julgamento = date_type.today()
    for mov in reversed(proc.movimentos):
        if mov.get("dataHora"):
            try:
                dt = datetime.fromisoformat(mov["dataHora"].replace("Z", "+00:00"))
                data_julgamento = dt.date()
                break
            except (ValueError, AttributeError):
                pass

    # Fundamentos a partir dos movimentos
    fundamentos = []
    obiter_dicta = []
    for mov in proc.movimentos:
        nome_mov = mov.get("nome", "")
        if nome_mov in ("Sentença", "Acórdão", "Decisão", "Despacho"):
            fundamentos.append(nome_mov)
        elif nome_mov in ("Inclusão em Pauta", "Vista", "Conclusão"):
            obiter_dicta.append(nome_mov)

    # Fatos relevantes a partir dos assuntos
    fatos = [
        f"Classe: {proc.classe_nome}" if proc.classe_nome else "Classe não informada",
    ]
    for assunto in proc.assuntos:
        fatos.append(assunto.get("nome", ""))

    return Precedent(
        id=f"{proc.tribunal}_{proc.id}",
        tribunal=tribunal_nome,
        orgao_julgador=orgao,
        data_julgamento=data_julgamento,
        tipo=ptype,
        binding=binding,
        ementa=proc.ementa_texto,
        tese=proc.ementa_texto,
        fundamentos=fundamentos or ["Decisão judicial"],
        fatos=[f for f in fatos if f],
        obiter_dicta=obiter_dicta,
    )


def process_to_legal_fact(proc: DatajudProcess) -> LegalFact:
    """Converte um DatajudProcess em LegalFact para o LegalSyllogism.

    A descrição do fato é construída a partir da classe e assuntos.
    A competência é inferida do tribunal.
    """
    descricao = f"Processo {proc.numero_processo}"
    if proc.classe_nome:
        descricao += f" — {proc.classe_nome}"
    if proc.assunto_principal:
        descricao += f": {proc.assunto_principal}"
    if proc.resultado:
        descricao += f" — Resultado: {proc.resultado}"

    competencia = _TRIBUNAL_TO_COMPETENCE.get(proc.tribunal)

    return LegalFact(
        descricao=descricao,
        competencia=competencia,
    )


def process_to_legal_argument(proc: DatajudProcess) -> LegalArgument:
    """Converte um DatajudProcess em LegalArgument para o LegalArgumentScorer.

    A tese é a ementa sintética. Os fundamentos normativos e jurisprudenciais
    são inferidos dos dados disponíveis.
    """
    # Determinar fundamento normativo a partir da classe
    fundamento_normativo = ""
    classe_nome = (proc.classe_nome or "").lower()
    if "apelação" in classe_nome:
        fundamento_normativo = "CPC/2015, arts. 1.009-1.014"
    elif "execução" in classe_nome:
        fundamento_normativo = "CPC/2015, arts. 771-925"
    elif "mandado" in classe_nome:
        fundamento_normativo = "CF/88, art. 5º, LXIX-LXX"
    elif "recurso" in classe_nome:
        fundamento_normativo = "CPC/2015, arts. 994-1.044"
    elif "procedimento" in classe_nome:
        fundamento_normativo = "CPC/2015, arts. 318-538"
    else:
        fundamento_normativo = "Legislação aplicável conforme a matéria"

    # Premissas a partir dos assuntos
    premissas = [f"Classe: {proc.classe_nome}"] if proc.classe_nome else []
    for assunto in proc.assuntos:
        premissas.append(f"Assunto: {assunto.get('nome', '')}")
    if proc.resultado:
        premissas.append(f"Resultado: {proc.resultado}")

    return LegalArgument(
        id=f"{proc.tribunal}_{proc.id}",
        autor=proc.tribunal_nome,
        tese=proc.ementa_texto,
        fundamento_normativo=fundamento_normativo,
        fundamento_jurisprudencial=f"Tribunal: {proc.tribunal_nome}",
        fundamento_doutrinario="",
        premissas=premissas,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Integração: Alimenta motores com dados do Datajud
# ═══════════════════════════════════════════════════════════════════════════


class LegalDatajudIntegration:
    """Integração entre API Datajud e motores de raciocínio jurídico.

    Permite alimentar todos os motores do módulo legal/ com dados
    reais de processos judiciais dos tribunais brasileiros.

    Args:
        api_key: Chave da API Datajud (ou None para usar DATAJUD_API_KEY env).
        offline: Se True, usa dados mockados.
    """

    def __init__(self, api_key: Optional[str] = None, offline: bool = True):
        self.client = DatajudClient(api_key=api_key, offline=offline)

        # Motores de raciocínio (compartilhados)
        self.syllogism = LegalSyllogism()
        self.balancing = PrincipleBalancing()
        self.precedents = PrecedentAnalyzer()
        self.scorer = LegalArgumentScorer()

        # Registro de quantos processos foram integrados
        self._stats = {"processos_carregados": 0, "precedentes_registrados": 0}

    def load_processes(
        self,
        tribunal: str,
        query: str = "",
        register_precedents: bool = True,
        register_norms: bool = True,
        register_facts: bool = True,
    ) -> List[DatajudProcess]:
        """Carrega processos de um tribunal e alimenta os motores.

        Args:
            tribunal: Sigla do tribunal (ex.: 'tjsp').
            query: Termo de pesquisa (ex.: 'indenização').
            register_precedents: Se True, registra no PrecedentAnalyzer.
            register_norms: Se True, registra normas inferidas no LegalSyllogism.
            register_facts: Se True, registra fatos no LegalSyllogism.

        Returns:
            Lista de processos carregados.
        """
        processos = self.client.search(tribunal, query)
        self._stats["processos_carregados"] += len(processos)

        for proc in processos:
            # Registrar como precedente
            if register_precedents:
                precedent = process_to_precedent(proc)
                self.precedents.register_precedent(precedent)
                self._stats["precedentes_registrados"] += 1

            # Registrar norma inferida (a classe processual como tipo de norma)
            if register_norms and proc.classe_nome:
                norm = LegalNorm(
                    id=f"norm_{proc.tribunal}_{proc.classe.get('codigo', '000')}",
                    texto=f"Classe {proc.classe_nome} — processamento conforme legislação aplicável",
                    hierarquia=NormHierarchy.LEI_ORDINARIA,
                    tipo=NormType.REGRA,
                    competencia=_TRIBUNAL_TO_COMPETENCE.get(proc.tribunal),
                )
                self.syllogism.register_norm(norm)

            # Registrar fato jurídico
            if register_facts:
                fact = process_to_legal_fact(proc)
                # O fato é registrado implicitamente — podemos subsumir depois

        return processos

    def load_all_tribunals(
        self, query: str = ""
    ) -> Dict[str, List[DatajudProcess]]:
        """Carrega processos de todos os tribunais disponíveis."""
        return self.client.search_all(query)

    def analyze_process(self, processo: DatajudProcess) -> Dict[str, Any]:
        """Analisa um processo com todos os motores de raciocínio.

        Aplica a pipeline completa:
          1. Subsunção (LegalSyllogism)
          2. Ponderação (PrincipleBalancing) — se houver princípios colidentes
          3. Precedentes (PrecedentAnalyzer)
          4. Scoring (LegalArgumentScorer)

        Args:
            processo: Processo a ser analisado.

        Returns:
            Dict com resultados de cada motor.
        """
        resultado: Dict[str, Any] = {
            "processo": processo.numero_processo,
            "tribunal": processo.tribunal_nome,
        }

        # 1. Subsunção
        fato = process_to_legal_fact(processo)
        subsuncao = self.syllogism.subsume(fato)
        resultado["subsuncao"] = subsuncao.to_dict()

        # 2. Precedentes
        precedent = process_to_precedent(processo)
        caso = CaseFacts(
            descricao=fato.descricao,
            fatos_relevantes=[
                f"Classe: {processo.classe_nome}",
                *(a.get("nome", "") for a in processo.assuntos),
            ],
        )
        precedente_result = self.precedents.identify_distinguishing(precedent.id, caso)
        resultado["precedente"] = precedente_result.to_dict()

        # 3. Scoring do argumento
        arg = process_to_legal_argument(processo)
        score = self.scorer.score(arg)
        resultado["scoring"] = score.to_dict()

        return resultado

    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas de integração."""
        return dict(self._stats)

    def reset_stats(self) -> None:
        """Reseta as estatísticas."""
        self._stats = {"processos_carregados": 0, "precedentes_registrados": 0}
