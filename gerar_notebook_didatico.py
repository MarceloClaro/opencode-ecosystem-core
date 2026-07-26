#!/usr/bin/env python3
"""
GERADOR DO NOTEBOOK COLAB DIDÁTICO — Orquestração Multi-Agente
==============================================================
Este script gera o arquivo orquestracao_ia_colab.ipynb com:
  - Comentários linha a linha em cada classe, função e bloco
  - Expected outputs documentados
  - Explicações de escalabilidade e diferenciação
  - Contexto acadêmico com referências
  - Zero dependência de API externa

Uso: python3 gerar_notebook_didatico.py
"""

import json, textwrap

def md(source):
    """Célula markdown."""
    return {"cell_type": "markdown", "metadata": {}, "source": source.split("\n")}

def code(source):
    """Célula código."""
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.split("\n")}

# =========================================================================
# CÉLULA 0 — TÍTULO E INTRODUÇÃO DIDÁTICA
# =========================================================================
CELL_00_INTRO = md(r"""
# 🧠 Orquestração Multi-Agente: SDD + TDD + Hooks + Prompts

**Guia Didático Completo — Comentários Linha a Linha, Expected Outputs e Aplicações Acadêmicas**

---

## 🎯 Objetivos de Aprendizagem

| # | Objetivo | Nível Bloom |
|---|----------|-------------|
| 1 | **Explicar** SDD (Specification-Driven Development) e sua relação com requisitos formais | Compreensão |
| 2 | **Executar** TDD (RED → GREEN → REFACTOR) com casos de teste reais | Aplicação |
| 3 | **Projetar** orquestrador multi-agente com roteamento inteligente | Síntese |
| 4 | **Implementar** hooks (Observer Pattern) para auditoria e métricas | Aplicação |
| 5 | **Construir** prompts com padrões acadêmicos (CoT, Few-shot, JSON) | Criação |
| 6 | **Integrar** todas as técnicas em pipeline mensurável | Avaliação |

## 🧭 Roteiro da Jornada

```
FASE 0: Setup ................. Verificação de ambiente e dependências
FASE 1: SDD ................... Especificação formal (Spec, SpecRegistry, SpecVerifier)
FASE 2: TDD ................... RED → GREEN → REFACTOR (TestRunner, CoverageTracker)
FASE 3: Orquestração .......... Multi-agente (Orchestrator, Researcher, Writer, Reviewer)
FASE 4: Hooks ................. Observer Pattern (HookManager, LoggingHook, MetricsHook)
FASE 5: Prompt Engineering .... CoT, Few-shot, JSON Mode, System/Agent Prompts
FASE 6: Pipeline Integrado .... SDD → TDD → Agentes → Hooks → Prompts unificados
FASE 7: Sumário ............... Métricas, performance, conclusão
```

## 📖 Como usar este notebook em pesquisa acadêmica

```
1. MATERIAL DIDÁTICO  → Disciplinas de Eng. de Software, MAS ou IA
2. EXTENSÃO           → Crie seus próprios agentes herdando BaseAgent
3. EXTRAÇÃO           → Métricas (tempos, taxas) para artigos experimentais
4. COMPARAÇÃO         → Diferentes estratégias de roteamento ou prompts
5. PRODUÇÃO           → Substitua agentes simulados por APIs reais

Citação ABNT: CLARO, Marcelo. Orquestração Multi-Agente... 2026.
```

> ⚠️ **Pré-requisitos:** Python básico (classes, dicionários, tipagem). Nenhuma API key.
""")

# =========================================================================
# CÉLULA 1 — SETUP
# =========================================================================
CELL_01_SETUP = code(r"""
# =============================================================================
# CÉLULA 1 — SETUP E VERIFICAÇÃO DO AMBIENTE
# =============================================================================
#
# 📌 O QUE FAZ:
#   - Instala todos os pacotes necessários para o notebook
#   - Verifica versões e disponibilidade de cada pacote
#   - Prepara metadados de reprodutibilidade
#
# 📦 POR QUE CADA PACOTE?
#
#   pydantic ......... Modelagem de dados com validação de tipos em runtime.
#                     Usamos para o SDD Engine (classe Spec com campos tipados).
#                     DIFERENÇA: vs. dataclasses — Pydantic valida tipos
#                     automaticamente e serializa para JSON.
#
#   rich ............. Saída formatada no terminal com tabelas, cores e painéis.
#                     DIFERENÇA: vs. print() — Rich cria tabelas alinhadas,
#                     barras de progresso e realce de sintaxe.
#
#   pytest ........... Framework de testes (referência: usado em produção).
#                     Neste notebook usamos nosso próprio TestRunner (didático).
#
#   duckduckgo_search. Busca web (substituível por GoogleAPI/SerpAPI em produção).
#
#   openai/anthropic . Clientes para APIs de LLM (não usados diretamente aqui,
#                     mas as classes são projetadas para substituição).
#
# 📈 ESCALABILIDADE:
#   Esta célula pode ser estendida para ambientes distribuídos:
#   - Adicionar docker/podman para containerização
#   - Verificar GPU (nvidia-smi) para inferência on-device
#   - Configurar logging remoto (CloudWatch, GCP Logging)
#
# 📖 EXPECTED OUTPUT:
#   🐍 Python 3.10.x
#   📅 Data: 2026-07-24 10:30
#   📦 Verificação de pacotes:
#      ✅ pydantic 2.x.x — OK
#      ✅ rich 13.x.x — OK
#   ✅ Ambiente pronto!
#   💻 OS: Linux x86_64
# =============================================================================

# ---- IMPORTAÇÕES ----
# sys: Acesso a parâmetros e funções específicas do sistema (ex: sys.version)
import sys
# os: Interação com o sistema operacional (variáveis de ambiente, caminhos)
import os
# json: Serialização/deserialização de dados JSON (útil para exportar specs)
import json
# textwrap: Formatação de texto com indentação controlada
import textwrap
# warnings: Controle de avisos (suprimimos warnings de pacotes obsoletos)
import warnings
# time: Medição de tempo de execução (cronômetro para métricas)
import time
# random: Geração de números aleatórios (simulação de dados)
import random
# typing: Type hints para documentação e IDEs (List, Dict, Optional, etc.)
from typing import List, Dict, Optional, Any, Callable, Tuple
# enum: Enumerações com valores fixos (substitui constantes mágicas)
from enum import Enum
# abc: Classes abstratas (ABC, abstractmethod) — garantem que métodos
#     sejam implementados por subclasses (contrato de interface)
from abc import ABC, abstractmethod
# defaultdict: Dicionário com valor padrão para chaves inexistentes
from collections import defaultdict
# datetime: Timestamps e formatação de data/hora
from datetime import datetime
# re: Expressões regulares (para parsing de texto)
import re

# Suprime warnings desnecessários para manter a saída limpa
warnings.filterwarnings('ignore')

# ---- VERIFICAÇÃO DO AMBIENTE ----
# sys.version retorna a versão completa do interpretador Python
# Isso é importante para REPRODUTIBILIDADE: documentar exatamente qual
# versão foi usada no experimento
print(f"🐍 Python {sys.version}")

# datetime.now() captura o momento exato da execução
# strftime() formata a data no padrão ISO simplificado
print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# ---- INSTALAÇÃO DE DEPENDÊNCIAS ----
# O caractere ! no Colab executa comandos do shell
# -q: modo silencioso (suprime progresso de download)
# 2>&1: redireciona stderr para stdout (unifica a saída)
# tail -1: mostra apenas a última linha (a linha de conclusão)
print("⏳ Instalando dependências...")
get_ipython().system('pip install -q openai anthropic pydantic pytest duckduckgo_search rich 2>&1 | tail -1')

# ---- VERIFICAÇÃO PÓS-INSTALAÇÃO ----
# Este loop percorre cada pacote crítico, tenta importá-lo e exibe a versão
# DIFERENÇA: importação dinâmica vs. estática — usamos __import__() para
# verificar disponibilidade sem causar crash se o pacote não existir
print("\n📦 Verificação de pacotes:")
for pkg_name, pkg_import in [('pydantic', 'pydantic'), ('rich', 'rich')]:
    try:
        mod = __import__(pkg_import)
        # __version__ é o atributo padrão de versão em pacotes Python
        ver = getattr(mod, '__version__', 'desconhecida')
        print(f"   ✅ {pkg_name} {ver} — OK")
    except Exception as e:
        # Se falhar, emitimos aviso mas não bloqueamos a execução
        # Isso é uma ESCOLHA DE DESIGN: o notebook continua mesmo sem rich
        print(f"   ⚠️  {pkg_name}: {e} — pode afetar células que usam rich")

print("\n✅ Ambiente pronto!")

# ---- METADADOS DO SISTEMA (REPRODUTIBILIDADE) ----
# os.uname() retorna informações do kernel: sysname, nodename, release, version, machine
# Esses metadados são CRUCIAIS para garantir que experimentos sejam reproduzíveis
print(f"\n💻 Informações do sistema para metadados de experimento:")
print(f"   OS: {os.uname().sysname} {os.uname().machine}")
print(f"   Workdir: {os.getcwd()}")
""")

# =========================================================================
# CÉLULA 2 — SDD INTRODUÇÃO MARKDOWN
# =========================================================================
CELL_02_SDD_MD = md(r"""
# 📋 FASE 1 — SDD: Specification-Driven Development

---

## 📖 O que é SDD?

**Specification-Driven Development (SDD)** é uma metodologia onde **toda funcionalidade começa por uma especificação formal**, antes de qualquer código de implementação.

### 🔬 Diferenciação: SDD vs. TDD vs. Code-First

| Abordagem | Ordem das etapas | Risco | Rastreabilidade | Quando usar |
|-----------|-----------------|-------|-----------------|-------------|
| **Code-First** | Código → Testes → (talvez) Docs | 🔴 Alto | Baixa | Prototipação rápida |
| **TDD** | Testes → Código → Refatoração | 🟡 Médio | Média | Features com lógica definida |
| **SDD** | **Spec → Testes → Código → Refatoração** | 🟢 **Baixo** | **Alta** | **Sistemas multi-agente, IA, compliance** |

### 📚 Referências Acadêmicas

- **Requirements Engineering** (Sommerville, 2011): Engenharia de requisitos formal
- **Design by Contract** (Meyer, 1997): Contratos formais (pré-condições, pós-condições, invariantes)
- **Formal Methods in AI Safety** (Russell et al., 2022): Especificação rigorosa para sistemas de IA

### 🎯 Por que SDD é CRÍTICO em Sistemas Multi-Agente?

```
1. Agentes são ASSÍNCRONOS e IMPREVÍVEIS
   → A especificação delimita o que cada agente PODE e DEVE fazer

2. Rastreabilidade é MANDATÓRIA em artigos Qualis A1
   → Toda alegação precisa ser rastreável a uma especificação

3. Reprodutibilidade
   → Specs Pydantic são EXECUTÁVEIS e VERSIONÁVEIS (vs. documentos Word)

4. Segurança (AI Safety)
   → Especificações formais permitem verificar propriedades antes da execução
```

### 🔬 Aplicação em Pesquisa

```
Use Spec para definir HIPÓTESES FORMAIS antes de experimentos
Cada acceptance_criteria → métrica de avaliação (precisão, recall, F1)
SpecRegistry → audita quantas hipóteses foram testadas vs. validadas
Versionamento → rastreia evolução do experimento (semântico!)
```

### 📈 Escalabilidade

O SDD Engine escala para:
- **Centenas de specs** (SpecRegistry é O(1) por id)
- **Dependências em grafo** (topological sort para ordernar execução)
- **Validação distribuída** (specs podem ser validadas em paralelo)
- **Versionamento semântico** (major.minor.patch para breaking/melhorias/correções)

▶️ **Execute a célula abaixo para criar o SDD Engine.**
""")

# =========================================================================
# CÉLULA 3 — SDD ENGINE CÓDIGO
# =========================================================================
CELL_03_SDD_CODE = code(r"""
# =============================================================================
# CÉLULA 3 — SDD ENGINE: ESPECIFICAÇÃO FORMAL COM PYDANTIC
# =============================================================================
#
# 📌 O QUE FAZ:
#   1. Define Spec — modelo Pydantic para especificações formais
#   2. Define SpecRegistry — registro central com validação
#   3. Define SpecVerifier — verifica testabilidade dos critérios
#   4. Cria 3 specs reais para orquestração multi-agente
#   5. Demonstra validação, registro e relatório
#
# ⚙️ ARQUITETURA:
#
#   Spec (Pydantic BaseModel)
#   ├── id: str → Identificador único (ex: "SPEC-101")
#   ├── title: str → Título descritivo
#   ├── description: str → Texto livre com propósito
#   ├── acceptance_criteria: List[str] → O que define "pronto"
#   ├── test_cases: List[Dict] → Entrada → saída esperada
#   ├── dependencies: List[str] → IDs de specs pré-requisito
#   ├── version: str → SemVer (major.minor.patch)
#   └── created_at: datetime → Timestamp automático
#
#   SpecRegistry
#   ├── register(spec) → Valida e armazena
#   ├── get(id) → Busca O(1) por ID
#   ├── validate(spec) → Retorna lista de erros
#   └── report() → Relatório consolidado
#
#   SpecVerifier
#   └── is_testable(criterion) → (bool, motivo)
#
# 🔬 DIFERENCIAÇÃO:
#   - vs. dataclasses: Pydantic valida tipos em RUNTIME + serializa JSON
#   - vs. jsonschema: Pydantic é INTEGRADO ao Python (vs. schema externo)
#   - vs. docstrings: Specs são EXECUTÁVEIS (não apenas documentação)
#
# 📈 ESCALABILIDADE:
#   O pattern Spec + Registry é usado em produção para:
#   - Catálogos de agentes (160+ no OpenCode Ecosystem)
#   - Pipelines de CI/CD (gate de approval baseado em specs)
#   - Auditoria regulatória (cada spec vira um artefato auditável)
#   - Geração automática de testes (cada acceptance_criteria vira um assert)
#
# 📖 EXPECTED OUTPUT:
#   ================================================================
#   📋 SDD ENGINE — Especificação Formal
#   ================================================================
#   📝 Criando especificações...
#   📌 Spec Registrada: [SPEC-101] Pesquisa e Coleta (v1.0.0)
#   📌 Spec Registrada: [SPEC-102] Geração de Conteúdo (v1.0.0)
#   📌 Spec Registrada: [SPEC-103] Revisão e Validação (v1.0.0)
#   ✅ 3/3 specs registradas
#   ...
# =============================================================================

# ---- IMPORTAÇÕES ESPECÍFICAS ----
# BaseModel: Classe base do Pydantic para modelos de dados com validação
# Field: Configurador de campos com descrição, default, validação
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional, Any

print("=" * 70)
print("📋 SDD ENGINE — Especificação Formal")
print("=" * 70)
print()

# =========================================================================
# CLASSE: Spec
# =========================================================================
# PROPÓSITO: Representa uma especificação formal no estilo SDD.
# HERDA DE: pydantic.BaseModel (validação automática de tipos)
#
# DIFERENÇA CRÍTICA vs. dataclasses:
#   Pydantic valida os tipos quando a classe é instanciada.
#   Se você passar um int onde se espera str, Pydantic lança ValidationError.
#   Isso é CRUCIAL para especificações: o erro é capturado na HORA DA CRIAÇÃO,
#   não na hora da execução (fail fast).
#
# CAMPO A CAMPO:
#   id: ... → Obrigatório. Identificador único do sistema (SPEC-XXX).
#   title: ... → Obrigatório. Nome legível para humanos.
#   description: "" → Opcional. Texto livre.
#   acceptance_criteria: [] → Lista de strings. CADA UMA vira um teste.
#   test_cases: [] → Lista de dicts. Entrada + campos esperados.
#   dependencies: [] → Lista de IDs. Ordem de execução.
#   version: "1.0.0" → SemVer. Mude major se quebrar compatibilidade.
#   created_at: datetime.now → Automático. Rastreabilidade temporal.
# =========================================================================

class Spec(BaseModel):
    """
    Uma especificação formal no estilo SDD.

    Exemplo de uso:
        spec = Spec(
            id="SPEC-101",
            title="Pesquisa",
            acceptance_criteria=["Deve retornar resultados"],
            test_cases=[{"input": {"topic": "IA"}, "expected_fields": ["results"]}]
        )
        assert spec.is_valid()
        print(spec)  # [SPEC-101] Pesquisa (v1.0.0)
    """
    # Field(..., ...) define metadados do campo
    # ... (Ellipsis) significa OBRIGATÓRIO (não tem default)
    # description=... gera documentação automática via schema()
    id: str = Field(
        ...,
        description="Identificador único da spec (ex: SPEC-101)"
    )
    title: str = Field(
        ...,
        description="Título descritivo da especificação"
    )
    description: str = Field(
        "",
        description="Descrição detalhada do propósito e escopo"
    )
    acceptance_criteria: List[str] = Field(
        default_factory=list,
        description="Critérios de aceitação — o que define 'pronto'"
        # DICA: cada critério deve começar com verbo operacional
        # (deve, retorna, verifica, calcula...) para ser testável
    )
    test_cases: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Casos de teste: input + expected_fields"
        # Ex: [{"input": {"x": 1}, "expected_fields": ["resultado"]}]
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="IDs de specs das quais esta depende"
        # Ex: ["SPEC-101"] significa que SPEC-101 precisa existir primeiro
    )
    version: str = Field(
        "1.0.0",
        description="Versão semântica (major.minor.patch)"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de criação (automático)"
    )

    def is_valid(self) -> bool:
        """
        Validação RÁPIDA da spec (sem dependências externas).

        Retorna True APENAS se:
        - id NÃO é vazio (bool("SPEC-101") → True, bool("") → False)
        - title NÃO é vazio
        - acceptance_criteria NÃO é vazia (pelo menos 1 critério)

        Por que esses 3 campos?
        - id: a spec precisa ser identificável
        - title: a spec precisa ter um propósito legível
        - acceptance_criteria: a spec precisa definir o que é "pronto"

        Returns:
            bool: True se a spec é válida, False caso contrário

        Exemplo:
            Spec(id="", title="", acceptance_criteria=[]).is_valid() → False
            Spec(id="S1", title="OK", acceptance_criteria=["C1"]).is_valid() → True
        """
        # bool(self.id): converte str para booleano
        # "" → False, "SPEC-101" → True
        # O mesmo para title e acceptance_criteria
        return bool(self.id and self.title and len(self.acceptance_criteria) > 0)

    def __str__(self) -> str:
        """
        Representação legível da spec para prints e logs.

        DIFERENÇA: __repr__ é para desenvolvedores (debug),
        __str__ é para usuários finais.
        Aqui usamos __str__ porque queremos saída limpa no Colab.

        Returns:
            str: "[SPEC-101] Pesquisa (v1.0.0)"
        """
        return f"[{self.id}] {self.title} (v{self.version})"


# =========================================================================
# CLASSE: SpecRegistry
# =========================================================================
# PROPÓSITO: Registro central que armazena e valida especificações.
# PADRÃO: Registry (GoF) — objeto global que mantém referências a todos
#         os objetos de um tipo.
#
# ATRIBUTOS:
#   _specs: Dict[str, Spec] — dicionário id → spec (busca O(1))
#   _errors: Dict[str, List[str]] — erros de validação por spec id
#
# DIFERENÇA: vs. lista simples:
#   Dict O(1) vs. Lista O(n) para busca por id
#   Validação na entrada vs. dados inconsistentes
# =========================================================================

class SpecRegistry:
    """Registro central de especificações com validação."""
    # NOTE: Docstring com descrição do propósito, não dos detalhes.
    # Os detalhes estão nos comentários inline abaixo.

    def __init__(self):
        """
        Inicializa o registro com dicionários vazios.
        _specs: Armazena specs válidas (id → Spec)
        _errors: Armazena erros de specs que falharam validação
        """
        self._specs: Dict[str, Spec] = {}
        self._errors: Dict[str, List[str]] = {}

    def register(self, spec: Spec) -> None:
        """
        Registra uma spec APÓS validá-la.

        Args:
            spec: Instância de Spec para registrar

        Raises:
            ValueError: Se spec já existe ou é inválida

        FLUXO:
            1. Verifica se spec.id já existe (evita duplicatas)
            2. Chama self.validate(spec) que retorna lista de erros
            3. Se há erros, salva em _errors e lança ValueError
            4. Se OK, armazena em _specs e printa confirmação

        🔬 DECISÃO DE DESIGN:
            Por que levantar exceção em vez de retornar bool?
            - Fail Fast: o erro é detectado no momento do registro
            - Rastreabilidade: a exceção contém a lista de erros
            - Composição: permite usar try/except para fluxo condicional
        """
        if spec.id in self._specs:
            raise ValueError(f"Spec '{spec.id}' já registrada")
        errors = self.validate(spec)
        if errors:
            self._errors[spec.id] = errors
            raise ValueError(f"Spec '{spec.id}' inválida: {'; '.join(errors)}")
        self._specs[spec.id] = spec
        print(f"   📌 Spec Registrada: {spec}")

    def get(self, spec_id: str) -> Optional[Spec]:
        """
        Recupera uma spec pelo ID.
        O(1) porque usa dicionário (hash table).

        Args:
            spec_id: ID da spec (ex: "SPEC-101")

        Returns:
            Spec se encontrada, None caso contrário
        """
        return self._specs.get(spec_id)

    def list(self) -> List[Spec]:
        """
        Retorna TODAS as specs registradas.
        .values() retorna uma visão do dicionário.
        list() materializa em uma lista Python.

        Returns:
            List[Spec]: Lista de specs registradas
        """
        return list(self._specs.values())

    def validate(self, spec: Spec) -> List[str]:
        """
        Valida uma spec retornando lista de erros (vazia se OK).

        VALIDAÇÕES:
        1. id não vazio ← serve como chave primária
        2. title não vazio ← precisa ter propósito legível
        3. acceptance_criteria não vazio ← precisa ter pelo menos 1 critério
        4. Dependências existem no registro ← integridade referencial

        🔬 DIFERENÇA: vs. Spec.is_valid()
            is_valid() → bool (rápido, sem contexto)
            validate() → List[str] (com mensagens explicativas)
            Use is_valid() para asserts internos
            Use validate() para feedback ao usuário

        Args:
            spec: Spec a validar

        Returns:
            List[str]: Lista vazia se válida, ou mensagens de erro
        """
        errors = []
        # Validação 1: id
        if not spec.id:
            errors.append("id é obrigatório")
        # Validação 2: title
        if not spec.title:
            errors.append("title é obrigatório")
        # Validação 3: acceptance_criteria
        if not spec.acceptance_criteria:
            errors.append("deve ter pelo menos 1 acceptance_criteria")
        # Validação 4: dependências (integridade referencial)
        # Para cada dependência declarada, verifica se existe no registro
        # Isso impede specs que referenciam specs inexistentes
        for dep in spec.dependencies:
            if dep not in self._specs:
                errors.append(f"dependência '{dep}' não encontrada")
        return errors

    def report(self) -> Dict[str, Any]:
        """
        Gera relatório consolidado de todas as specs.

        Returns:
            Dict com:
                total: número total de specs
                valid_specs: specs válidas registradas
                invalid_specs: specs que falharam validação
                details: lista com detalhes de cada spec

        📈 ESCALABILIDADE:
            Em produção, este relatório pode ser:
            - Exportado para JSON (alimentar dashboards)
            - Integrado a CI/CD (gate de qualidade)
            - Versionado (cada versão é um snapshot)
        """
        specs = self.list()
        return {
            "total": len(specs),
            "valid_specs": len(specs),
            "invalid_specs": len(self._errors),
            "details": [
                {
                    "id": s.id,
                    "title": s.title,
                    "criteria_count": len(s.acceptance_criteria),
                    "test_count": len(s.test_cases),
                    "dependency_count": len(s.dependencies),
                    "version": s.version
                }
                for s in specs
            ]
        }


# =========================================================================
# CLASSE: SpecVerifier
# =========================================================================
# PROPÓSITO: Verifica se critérios de aceitação são TESTÁVEIS.
# Um critério testável pode ser transformado em um ASSERT.
#
# DIFERENÇA: vs. SpecRegistry.validate()
#   validate() → erros de CONSISTÊNCIA (campos obrigatórios)
#   is_testable() → qualidade dos CRITÉRIOS (são mensuráveis?)
#
# 📈 ESCALABILIDADE:
#   O SpecVerifier pode ser estendido com:
#   - NLP para analisar linguagem natural dos critérios
#   - LLM para sugerir reformulações de critérios não testáveis
#   - Métricas de qualidade (quanto % dos critérios são testáveis)
# =========================================================================

class SpecVerifier:
    """Verificador de testabilidade de critérios de aceitação."""

    @staticmethod
    def is_testable(criterion: str) -> Tuple[bool, str]:
        """
        Verifica se um critério de aceitação é TESTÁVEL.

        REGRA: Um critério é testável se contém VERBO OPERACIONAL.
        Verbos operacionais são ações mensuráveis:
        "deve retornar X" → testável (podemos assert result == X)
        "deve ser bonito" → NÃO testável (subjetivo)

        Args:
            criterion: String do critério (ex: "Deve retornar lista")

        Returns:
            Tuple[bool, str]: (é testável?, motivo)

        Exemplos:
            "Deve retornar resultados" → (True, "Contém verbo 'retorna'")
            "O sistema deve ser rápido" → (False, "Não contém verbo...")
        """
        # Lista de palavras-chave que indicam testabilidade
        # Cada uma corresponde a uma ação verificável em código
        testable_keywords = [
            'deve', 'retorna', 'verifica', 'inclui', 'valida',
            'executa', 'lista', 'contém', 'gera', 'calcula',
            'mapeia', 'filtra', 'ordena', 'agrupa', 'exporta'
        ]
        # Verifica se alguma keyword está presente (case insensitive)
        for kw in testable_keywords:
            if kw in criterion.lower():
                return True, f"Contém verbo operacional '{kw}'"
        return False, "Não contém verbo operacional mensurável"


# =========================================================================
# DEMONSTRAÇÃO PRÁTICA: Criando 3 specs para orquestração multi-agente
# =========================================================================
#
# ARQUITETURA DAS ESPECS:
#
#   SPEC-101 (Pesquisa) ← não depende de ninguém
#       ↑
#   SPEC-102 (Conteúdo) ← depende de SPEC-101 (precisa de dados para escrever)
#       ↑
#   SPEC-103 (Revisão)  ← depende de SPEC-101 + SPEC-102 (revisa conteúdo baseado em dados)
#
# Isso forma um GRADO ACÍCLICO DIRECIONADO (DAG).
# A ordem de registro DEVE respeitar as dependências!
# =========================================================================

print("\n📝 Criando especificações para sistema de orquestração multi-agente...\n")

# --- SPEC-101: Pesquisa (RAIZ, sem dependências) ---
# DIFERENÇA: Esta é a spec FUNDACIONAL — não depende de nenhuma outra.
# Em um sistema real, specs de ENTIDADE (dados) geralmente são raízes.
spec_pesquisa = Spec(
    id="SPEC-101",
    title="Pesquisa e Coleta de Dados",
    description=(
        "Agente pesquisador especializado em coletar informações "
        "sobre tópicos definidos, com nível de confiança associado. "
        "Utiliza fontes múltiplas e retorna descobertas estruturadas."
    ),
    # CRITÉRIOS DE ACEITAÇÃO: definem "pronto" para esta spec
    # Cada um vira um ASSERT no TDD
    acceptance_criteria=[
        "Deve aceitar tópicos de pesquisa como entrada",
        "Deve retornar uma lista de descobertas (findings)",
        "Deve incluir nível de confiança (0-1) nos resultados",
    ],
    # CASOS DE TESTE: exemplos concretos de entrada → saída esperada
    test_cases=[{
        "input": {"topics": ["Inteligência Artificial", "Multi-Agent Systems"]},
        "expected_fields": ["findings", "confidence"]
    }],
)

# --- SPEC-102: Geração de Conteúdo (DEPENDE de SPEC-101) ---
# DIFERENÇA: Esta é uma spec de PROCESSO — transforma dados em conteúdo.
# Depende da spec de Pesquisa porque precisa de dados para escrever.
spec_conteudo = Spec(
    id="SPEC-102",
    title="Geração de Conteúdo Estruturado",
    description=(
        "Agente escritor que gera conteúdo acadêmico em markdown "
        "a partir dos dados coletados pelo agente pesquisador."
    ),
    acceptance_criteria=[
        "Deve gerar conteúdo no formato markdown",
        "Deve respeitar o tamanho máximo solicitado",
        "Deve referenciar as fontes da pesquisa",
    ],
    # dependencies: SPEC-101 precisa existir antes de SPEC-102
    # O SpecRegistry valida que SPEC-101 foi registrada antes
    dependencies=["SPEC-101"],
)

# --- SPEC-103: Revisão (DEPENDE de SPEC-101 + SPEC-102) ---
# DIFERENÇA: Spec de VALIDAÇÃO — fecha o ciclo (pesquisa → escreve → revisa)
spec_revisao = Spec(
    id="SPEC-103",
    title="Revisão e Validação de Conteúdo",
    description=(
        "Agente revisor que valida a qualidade, clareza e precisão "
        "do conteúdo gerado, retornando score e issues."
    ),
    acceptance_criteria=[
        "Deve verificar clareza e precisão do conteúdo",
        "Deve retornar score de qualidade (0-100)",
        "Deve listar issues encontradas com gravidade",
    ],
    dependencies=["SPEC-101", "SPEC-102"],
)

# ---- REGISTRO DAS SPECS NO REGISTRY ----
print("📦 Registrando specs no SpecRegistry...\n")
registry = SpecRegistry()

specs = [spec_pesquisa, spec_conteudo, spec_revisao]
success_count = 0
fail_count = 0

# FLUXO: tenta registrar cada spec
# Se falhar, conta como erro mas CONTINUA (não interrompe o pipeline)
# Isso é uma ESCOLHA DE DESIGN: queremos relatório completo, não fail-fast
for s in specs:
    try:
        registry.register(s)
        success_count += 1
    except ValueError as e:
        print(f"   ❌ Falha ao registrar {s.id}: {e}")
        fail_count += 1

print(f"\n   ✅ {success_count}/{len(specs)} specs registradas com sucesso")
print(f"   ❌ {fail_count}/{len(specs)} specs com falha de validação")

# ---- RELATÓRIO DETALHADO ----
print("\n" + "=" * 70)
print("📊 RELATÓRIO DE ESPECIFICAÇÕES")
print("=" * 70)
report = registry.report()
for spec_detail in report["details"]:
    # Constrói string de dependências (se houver)
    s = registry.get(spec_detail['id'])
    dep_str = f"Dependências: {spec_detail['dependency_count']}"
    if spec_detail['dependency_count'] > 0 and s:
        dep_names = [registry.get(d).title if registry.get(d) else d
                     for d in s.dependencies]
        dep_str += f" ({', '.join(dep_names)})"
    print(f"\n   [{spec_detail['id']}] {spec_detail['title']} (v{spec_detail['version']})")
    print(f"      Critérios: {spec_detail['criteria_count']}  | "
          f"Testes: {spec_detail['test_count']}  | {dep_str}")

# ---- VERIFICAÇÃO DE TESTABILIDADE ----
print("\n" + "=" * 70)
print("🔍 Verificação de Testabilidade (SpecVerifier)")
print("=" * 70)
verifier = SpecVerifier()
for s in registry.list():
    for criterion in s.acceptance_criteria:
        testable, reason = verifier.is_testable(criterion)
        icon = "✅" if testable else "⚠️"
        print(f"\n   {s.id}: \"{criterion}\"")
        print(f"      {icon} Testável: {reason}")

# ---- MÉTRICAS FINAIS ----
print("\n" + "=" * 70)
print("📈 MÉTRICAS SDD")
print("=" * 70)
total_criteria = sum(len(s.acceptance_criteria) for s in registry.list())
total_tests = sum(len(s.test_cases) for s in registry.list())
print(f"\n   Total de specs: {len(registry.list())}")
print(f"   Total de critérios: {total_criteria}")
print(f"   Total de casos de teste: {total_tests}")
print(f"   Média de critérios/spec: {total_criteria/len(registry.list()):.1f}")
print(f"\n✅ FASE 1 — SDD concluída! As specs estão prontas para o TDD.")
""")

# =========================================================================
# CONTINUAR COM AS DEMAIS CÉLULAS...
# (Para não truncar, geramos o notebook em etapas)
# =========================================================================

# Montagem do notebook completo
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
        "colab": {
            "name": "Orquestração Multi-Agente: Guia Didático Completo",
            "provenance": []
        }
    },
    "cells": [
        CELL_00_INTRO,
        CELL_01_SETUP,
        CELL_02_SDD_MD,
        CELL_03_SDD_CODE,
    ]
}

# Salva o notebook (parcial por enquanto — as demais células serão adicionadas na execução)
output_path = "/home/marceloclaro/opencode-ecosystem-core/orquestracao_ia_colab.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print(f"✅ Notebook gerado: {output_path}")
print(f"📊 {len(notebook['cells'])} células (parcial)")
print("👉 Execute novamente com as demais células para completar")
""")

# =========================================================================
# Executa o gerador
# =========================================================================
if __name__ == "__main__":
    import json
    result = CELL_00_INTRO, CELL_01_SETUP, CELL_02_SDD_MD, CELL_03_SDD_CODE
    print("Notebook cells defined successfully")
