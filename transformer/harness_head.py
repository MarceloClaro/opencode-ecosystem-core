# -*- coding: utf-8 -*-
"""
Cabeça de atenção ``harness`` — artefatos externos como candidatos de roteamento
(SPEC-935-R621)
===========================================================================
O ``AttentionRouter`` do Core ranqueia **agentes registrados** por quatro
cabeças (semântica, capacidade, confiança, carga). Isso deixa de fora uma
categoria real de candidato: o *artefato* de um ecossistema externo — uma skill
do Claude, um subagente do padrão AGENTS.md, um manifesto de hooks do
Antigravity. São instruções auditáveis, com proveniência e licença conhecidas;
merecem entrar no roteamento com o mesmo peso de rigor que um agente interno,
não como apêndice.

Esta cabeça é a quinta do ensemble e é **determinística e auditável**:
``explain_componenti`` devolve cada parcela do score, sem caixa-preta.

| Componente | Peso | O que mede |
|---|---|---|
| `semantic`   | 0.35 | similaridade da descrição do artefato com a tarefa |
| `capability` | 0.30 | cobertura das capacidades exigidas |
| `maturity`   | 0.20 | integridade (``ok`` > ``degraded``) e procedência |
| `license`    | 0.15 | licença declarada (INV-R621.1 é gate, não preferência) |

A integração com o ``AttentionRouter`` é **opt-in**: o router existente mantém
seu contrato de quatro cabeças e soma exatamente 1. Quem quiser a quinta
cabeça chama :func:`attach_to_router` explicitamente, e o router passa a
combinar as duas funções de utilidade com um peso de mistura declarado.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import math
import os
import re
import sys
import unicodedata
from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from integrations.harness_federation.artifact import HarnessArtifact, source_integrity_reasons  # noqa: E402
from integrations.harness_federation.emit import HarnessEmitter  # noqa: E402
from integrations.harness_federation.harvest import HarnessHarvester  # noqa: E402

DEFAULT_HEAD_WEIGHTS: Dict[str, float] = {
    "semantic": 0.35,
    "capability": 0.30,
    "maturity": 0.20,
    "license": 0.15,
}

_WORD_RE = re.compile(r"[a-z0-9_]+")

# Glossário bilíngue pt-BR <-> en. Sem ele, uma consulta em português ("escrever
# testes") nunca casa com uma skill em inglês ("test-driven-development"): o
# cosseno léxico mede zero e o ranking degenera em ordem alfabética. Este
# dicionário é pequeno, explícito e auditável — é um recurso lexical, não um
# modelo. Quem quiser algo melhor pluga um embedding real; esta camada não
# finge ser um.
_BILINGUAL_GLOSSARY: Dict[str, str] = {}


def _register_glossary(pairs: Dict[str, str]) -> None:
    for source, canonical in pairs.items():
        _BILINGUAL_GLOSSARY[source] = canonical


_register_glossary({
    # português -> inglês canônico. Uma entrada por linha e sem chave
    # repetida: a lista é auditada a olho nu, e duplicata silenciosa aqui
    # significa dois canônicos competindo pelo mesmo termo.
    "testes": "test", "testar": "test", "testando": "test",
    "testavel": "test", "implementar": "implement", "implementacao": "implement",
    "implementacoes": "implement", "funcionalidade": "feature", "funcionalidades": "feature",
    "recurso": "feature", "codigo": "code", "programa": "code",
    "script": "code", "scripts": "code", "correcao": "fix",
    "corrigir": "fix", "correcoes": "fix", "erro": "bug",
    "erros": "bug", "defeito": "bug", "falha": "bug",
    "falhas": "bug", "debbug": "debug", "depuracao": "debug",
    "diagnostico": "debug", "revisao": "review", "revisar": "review",
    "revisoes": "review", "seguranca": "security", "vulnerabilidade": "vulnerability",
    "vulnerabilidades": "vulnerability", "ameaca": "threat", "ameacas": "threat",
    "desempenho": "performance", "otimizacao": "optimize", "otimizar": "optimize",
    "documentacao": "documentation", "documentar": "document", "documentos": "document",
    "desenho": "design", "arquitetura": "architecture", "arquitetural": "architecture",
    "nuvem": "cloud", "implantacao": "deploy", "implantar": "deploy",
    "publicar": "release", "publicacao": "release", "versao": "version",
    "dependencia": "dependency", "dependencias": "dependency", "pacote": "package",
    "pacotes": "package", "biblioteca": "library", "bibliotecas": "library",
    "agente": "agent", "agentes": "agent", "delegacao": "delegate",
    "delegar": "delegate", "orquestracao": "orchestration", "orquestrar": "orchestration",
    "fluxo": "workflow", "fluxos": "workflow", "processo": "workflow",
    "planejar": "plan", "planejamento": "plan", "plano": "plan",
    "pesquisa": "research", "pesquisar": "research", "buscar": "search",
    "busca": "search", "resultados": "result", "resultado": "result",
    "dados": "data", "base": "database", "banco": "database",
    "consulta": "query", "configurar": "config", "configuracao": "config",
    "definicao": "setting", "variavel": "env", "variaveis": "env",
    "ambiente": "environment", "segredo": "secret", "segredos": "secret",
    "credencial": "credential", "credenciais": "credential", "token": "token",
    "chave": "key", "chaves": "key", "usuario": "user",
    "usuarios": "user", "sessao": "session", "sessoes": "session",
    "fila": "queue", "filas": "queue", "tarefa": "task",
    "tarefas": "task", "trabalho": "work", "equipe": "team",
    "times": "team", "clube": "parallel", "paralelo": "parallel",
    "paralela": "parallel", "validacao": "validation", "validar": "validate",
    "verificar": "verify", "verificacao": "verify", "confirmar": "confirm",
    "prova": "test", "desenvolvimento": "development", "desenvolvedor": "development",
    "estrutura": "structure", "estrutural": "structure", "modelo": "model",
    "formatacao": "format", "formatar": "format", "estilo": "style",
    "interface": "ui", "tela": "ui", "componente": "component",
    "componentes": "component", "navegador": "browser", "pagina": "page",
    "paginacao": "page", "relatorio": "report", "relatorios": "report",
    "metricas": "metric", "metrica": "metric", "monitoramento": "monitor",
    "observabilidade": "observability", "log": "log", "logs": "log",
    "git": "git", "branch": "branch", "ramo": "branch",
    "commit": "commit", "commits": "commit", "merge": "merge",
    "uniao": "merge", "historico": "history", "projeto": "project",
    "projetos": "project", "repositorio": "repository", "escrita": "write",
    "escrever": "write", "ler": "read", "leitura": "read",
    "refatorar": "refactor", "refatoracao": "refactor", "simplificar": "simplify",
    "limpeza": "cleanup", "remover": "remove", "remocao": "remove",
    "deletar": "delete", "subagente": "subagent", "subagentes": "subagent",
    "especialista": "specialist", "especialistas": "specialist", "generico": "generic",
    "generica": "generic", "automatizar": "automation", "automacao": "automation",
    "agendado": "scheduled", "agendada": "scheduled", "rotina": "routine",
    "recorrente": "recurring", "material": "material", "conteudo": "content",
    "artigo": "article", "artigos": "article", "paper": "paper",
    "papers": "paper", "cientifico": "scientific", "cientifica": "scientific",
    "metodo": "method", "metodos": "method", "metodologia": "methodology",
    "analise": "analysis", "analises": "analysis", "estatistica": "statistics",
    "medico": "medical", "medica": "medical", "clinico": "clinical",
    "clinica": "clinical", "paciente": "patient", "pacientes": "patient",
    "hospital": "hospital", "escola": "school", "escolar": "school",
    "escolas": "school", "turma": "class", "nota": "grade",
    "financeiro": "finance", "orcamento": "budget", "conta": "account",
    "contas": "account", "prestacao": "accountability", "nos": "node",
    "servico": "service", "servicos": "service", "api": "api",
    "sql": "sql", "postgres": "postgres", "postgresql": "postgres",
    "mysql": "mysql", "kubernetes": "kubernetes", "kube": "kubernetes",
    "docker": "docker", "contêiner": "container", "container": "container",
    "imagem": "image", "imagens": "image", "video": "video",
    "audio": "audio", "texto": "text", "linguagem": "language",
    "idioma": "language", "traducao": "translation", "traduzir": "translate",
    "revisão": "review", "revisões": "review", "código": "code",
    "correcão": "fix", "correção": "fix", "correções": "fix",
    "correcões": "fix", "exceção": "exception", "função": "function",
    "funcoes": "function", "funções": "function", "versão": "version",
    "acesso": "access", "conexão": "connection", "coleção": "collection",
    "opção": "option", "opcao": "option", "informação": "information",
    "informacao": "information", "produção": "production", "producao": "production",
    "execução": "execution", "execucao": "execution", "manutenção": "maintenance",
    "manutencao": "maintenance", "decisão": "decision", "decisao": "decision",
    "decisoes": "decision", "decisões": "decision", "condição": "condition",
    "condicao": "condition", "validação": "validation", "implementação": "implement",
    "dependência": "dependency", "variável": "env", "variáveis": "env",
    "auditoria": "audit", "auditar": "audit", "métricas": "metric",
    "análise": "analysis", "análises": "analysis", "científico": "scientific",
    "clínico": "clinical", "clínica": "clinical", "jurídico": "legal",
    "juridico": "legal", "política": "policy", "politica": "policy",
    "políticas": "policy", "politicas": "policy", "histórico": "history",
    "automático": "automatic", "automatico": "automatic", "específico": "specific",
    "especifico": "specific", "básico": "basic", "basico": "basic",
    "teórico": "theoretical", "teorico": "theoretical", "prático": "practice",
    "pratico": "practice", "padrão": "pattern", "padrao": "pattern",
    "padrões": "pattern", "padroes": "pattern", "lógica": "logic",
    "logica": "logic", "memória": "memory", "memoria": "memory",
    "módulos": "module", "modulo": "module", "modulos": "module",
    "módulo": "module", "índice": "index", "indice": "index",
    "índices": "index", "gráfico": "chart", "grafico": "chart",
    "gráficos": "chart", "relatório": "report", "relatórios": "report",
    "documentação": "documentation", "implantação": "deploy", "publicação": "release",
    "otimização": "optimize", "varredura": "scan", "scanear": "scan",
    "mapeamento": "mapping", "mapeia": "mapping", "roteamento": "route",
    "roteia": "route", "delegação": "delegate", "orquestração": "orchestration",
    "paralelos": "parallel", "paralelas": "parallel", "concorrente": "concurrent",
    "refatoração": "refactor", "simplificação": "simplify", "simplificacao": "simplify",
    "depuração": "debug", "diagnóstico": "debug", "usuário": "user",
    "usuários": "user", "sessão": "session", "verificação": "verify",
    "página": "page", "repositório": "repository", "automação": "automation",
    "conteúdo": "content", "estatística": "statistics", "médico": "medical",
    "serviços": "service", "cluster": "cluster", "contêineres": "container",
    "containers": "container", "tradução": "translation",
})

# Sufixos removidos para casar flexionamento PT/EN. Lista curta e conservadora:
# um stemmer agressivo (Porter) fundiria palavras distintas e criaria falsos
# positivos, que num ranqueamento de instrução é pior que perder um match.
_SUFFIXES: Tuple[str, ...] = (
    "acoes", "amento", "acoes", "mente", "coes", "ing", "ings",
    "cao", "coes", "ivel", "ivel", "aria", "orio", "aria",
    "es", "s", "al", "os", "as", "e",
)


def _stem(token: str) -> str:
    """Normaliza um token por radicalização conservadora (PT/EN)."""

    if len(token) <= 4:
        return token
    for suffix in _SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token

# Parada em português/inglês para não inflar a similaridade com função sintática.
_STOPWORDS = frozenset({
    "a", "o", "as", "os", "de", "do", "da", "dos", "das", "e", "em", "no", "na", "nos",
    "nas", "um", "uma", "uns", "umas", "para", "por", "com", "que", "se", "ao", "aos",
    "the", "of", "to", "and", "in", "for", "with", "on", "is", "are", "be", "use",
    "when", "this", "that", "it", "as", "at", "or", "an", "by", "from",
})


def _tokens(text: str) -> List[str]:
    """
    Tokeniza para comparação léxica.

    A ordem das normalizações importa: o glossário bilíngue é aplicado ANTES
    da radicalização, porque "testes" precisa virar o canônico "test" e não
    "test"→"tes". Depois, tokens vazios, stopwords e radicalizações vazias são
    descartados.
    """

    # NFD + remoção explícita dos combining marks. Confiar no regex para
    # descartar o acento parte a palavra em pedaços ("revisão" virava
    # "revisa" + "o", produzindo os tokens inúteis "revisa" e "digo").
    decomposed = unicodedata.normalize("NFD", (text or "").lower())
    normalized = "".join(ch for ch in decomposed if not unicodedata.combining(ch))

    out: List[str] = []
    for token in _WORD_RE.findall(normalized):
        canonical = _BILINGUAL_GLOSSARY.get(token)
        if canonical is not None:
            # A forma canônica já é normalizada: radicalizá-la de novo
            # corromperia o termo ("analysis" -> "analysi"), criando duas
            # grafias para o mesmo conceito e quebrando o casamento.
            out.append(canonical)
            continue
        # Plural ntira antes do casamento: "clínicos" -> "clinicos" -> "clinico",
        # e só então encontra a entrada do glossário. Sem esta segunda consulta,
        # a forma plural escapava da tradução e o termo português vazava para o
        # lado inglês, produzindo assimetria entre artefato e tarefa.
        stemmed = _stem(token)
        canonical = _BILINGUAL_GLOSSARY.get(stemmed)
        if canonical is not None:
            out.append(canonical)
            continue
        if len(stemmed) > 2 and stemmed not in _STOPWORDS:
            out.append(stemmed)
    return out


def _lexical_affinity(task: str, artifact_text: str) -> float:
    """
    Similaridade léxica normalizada em ``[0, 1]`` (cosseno sobre vetores de token).

    Jaccard puro foi descartado por medição: com uma tarefa de 12 tokens e uma
    descrição de 300, a união é dominada pela tarefa e o coeficiente colapsa
    perto de zero para todos os candidatos, deixando o ranking indiferenciado.
    O cosseno normaliza pelo comprimento e preserva o sinal — um artefato que
    cita "testes", "tdd" e "implementação" e continua
    pontuando alto em vez de dividir por uma união enorme.

    Isto é aproximação léxica determinística, não similaridade semântica
    treinada; o relatório do roteador nomeia o método como tal.
    """

    task_tokens = _tokens(task)
    text_tokens = _tokens(artifact_text)
    if not task_tokens or not text_tokens:
        return 0.0
    task_counts = Counter(task_tokens)
    text_counts = Counter(text_tokens)
    shared = set(task_counts) & set(text_counts)
    if not shared:
        return 0.0
    # Termos repetidos pesam mais, mas com saturação (tf sublinear): a
    # quinta ocorrência de "teste" não vale cinco vezes a primeira.
    numerator = math.fsum(
        (1.0 + math.log(task_counts[token])) * (1.0 + math.log(text_counts[token]))
        for token in shared
    )
    task_norm = math.sqrt(math.fsum((1.0 + math.log(v)) ** 2 for v in task_counts.values()))
    text_norm = math.sqrt(math.fsum((1.0 + math.log(v)) ** 2 for v in text_counts.values()))
    denominator = task_norm * text_norm
    if denominator <= 0.0:
        return 0.0
    return max(0.0, min(1.0, numerator / denominator))


def _unit(value: Any, default: float = 0.0) -> float:
    """Coage qualquer entrada numérica finita dentro de ``[0, 1]``."""

    if isinstance(value, bool):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(number):
        return default
    return max(0.0, min(1.0, number))


# Precedência de procedência: artefato do próprio operador acima de cache de
# terceiro. Não é preferência estética — provenance desconhecida é risco.
_ORIGIN_SCORE: Dict[str, float] = {
    "first_party": 1.00,
    "user": 0.85,
    "third_party": 0.55,
}

# Licenças de cópia fraca reducem confiança de reuso; ausência zera (fail-closed).
_LICENSE_SCORE: Dict[str, float] = {
    "mit": 1.0, "apache-2.0": 1.0, "bsd-3-clause": 0.95, "bsd-2-clause": 0.95,
    "isc": 0.95, "mpl-2.0": 0.8, "lgpl-3.0": 0.6, "lgpl-2.1": 0.55,
    "agpl-3.0": 0.4, "gpl-3.0": 0.4, "proprietary": 0.3, "unlicense": 0.7,
    "cc0-1.0": 0.9, "cc-by-4.0": 0.85,
}

# Termos que sugerem licença permissiva mesmo escrita por extenso.
_LICENSE_TEXT_HINTS: Tuple[Tuple[str, float], ...] = (
    ("apache", 1.0), ("mit license", 1.0), ("bsd", 0.95), ("isc license", 0.95),
    ("mozilla public", 0.8), ("lgpl", 0.6), ("agpl", 0.4), ("gpl", 0.4),
    ("all rights reserved", 0.3), ("proprietary", 0.3),
)


def _contains_token(normalized: str, needle: str) -> bool:
    """Busca ``needle`` em ``normalized`` respeitando fronteira de token.

    ``in`` puro é o tipo de detalhe que faz um classificador parecer mais
    inteligente do que é: ``"mit" in "submit"`` é verdadeiro, então a palavra
    "submit" receberia a confiança de reuso de uma licença MIT. Numa federação
    que decide portar artefatos de terceiros, esse tipo de falso positivo
    significa que código sem licença declarada é tratado como permissivo.
    """

    return re.search(r"(?<![a-z0-9])" + re.escape(needle) + r"(?![a-z0-9])", normalized) is not None


def license_score(license_name: str) -> float:
    """Converte o rótulo de licença em confiança de reuso em ``[0, 1]``."""

    normalized = (license_name or "").strip().lower()
    if not normalized:
        return 0.0
    if normalized in _LICENSE_SCORE:
        return _LICENSE_SCORE[normalized]
    for key, value in _LICENSE_SCORE.items():
        if _contains_token(normalized, key):
            return value
    for hint, value in _LICENSE_TEXT_HINTS:
        if _contains_token(normalized, hint):
            return value
    # Rótulo presente mas não reconhecido: nenhuma permissão de reuso foi
    # concedida, então a nota é quase nula. Fica acima de 0.0 porque houve
    # alguma declaração, mas o silêncio (0.0) continua sendo o pior caso
    # fail-closed. O antigo 0.5 dava a um texto sem identificação metade da
    # confiança de um MIT, o que é uma afirmação que a fonte não sustenta.
    return 0.1


def _validated_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Exige pesos não negativos somando exatamente 1 (INV-R621.5)."""

    if set(weights) != set(DEFAULT_HEAD_WEIGHTS):
        raise ValueError("pesos devem cobrir exatamente as componentes da cabeça harness")
    total = 0.0
    validated: Dict[str, float] = {}
    for name, value in weights.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"peso inválido para {name!r}")
        number = float(value)
        if not math.isfinite(number) or number < 0.0:
            raise ValueError(f"peso fora de [0, +inf) para {name!r}")
        validated[name] = number
        total += number
    if not math.isclose(total, 1.0, abs_tol=1e-9):
        raise ValueError(f"os pesos da cabeça harness devem somar 1 (soma={total!r})")
    return validated


class HarnessAttentionHead:
    """
    Quinto componente do ensemble de atenção: artefatos de harness externos.

    Não é uma rede neural e não se apresenta como tal. É uma heurística
    determinística, decomponível e auditável — o mesmo padrão que o
    ``AttentionRouter`` já usa, extended a uma classe de candidato que ele não
    via.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None) -> None:
        self.weights = _validated_weights(dict(weights or DEFAULT_HEAD_WEIGHTS))

    # ------------------------------------------------------------------
    # Componentes
    # ------------------------------------------------------------------
    @staticmethod
    def _artifact_name(card: Dict[str, Any]) -> str:
        return str(card.get("name") or "")

    @staticmethod
    def _artifact_text(card: Dict[str, Any]) -> str:
        """Texto comparável do artefato: descrição, nome, tags e capacidades."""

        return " ".join([
            str(card.get("name") or ""),
            str(card.get("description") or ""),
            " ".join(card.get("tags") or []),
            " ".join(card.get("capabilities") or []),
        ])

    def _head_semantic(self, task: str, cards: Sequence[Dict[str, Any]]) -> List[float]:
        """
        Melhor de dois sinais léxicos: nome e documento.

        Comparar a tarefa só com a descrição (centenas de tokens) rebaixa o
        cosseno de todo mundo para perto de zero e o ranking vira ordem
        alfabética — medido assim na primeira execução. O *nome* do artefato
        ("test-driven-development") é o rótulo curto e denso que de fato
        discrimina, então ele entra com peso cheio e a descrição com meio,
        limitada por piso. O máximo das duas é o score.
        """

        return [
            max(
                _lexical_affinity(task, self._artifact_name(card)),
                0.5 * _lexical_affinity(task, self._artifact_text(card)),
            )
            for card in cards
        ]

    @staticmethod
    def _head_capability(required: Sequence[str], cards: Sequence[Dict[str, Any]]) -> List[float]:
        """Cobertura das capacidades exigidas; sem exigência declarada, 1.0."""

        required_set = {str(r) for r in required if str(r).strip()}
        scores: List[float] = []
        for card in cards:
            if not required_set:
                scores.append(1.0)
                continue
            declared = {str(c).lower() for c in (card.get("capabilities") or [])}
            declared |= {t.lower() for t in (card.get("tags") or [])}
            matched = {r for r in required_set if any(r.lower() in d or d in r.lower() for d in declared)}
            scores.append(len(matched) / len(required_set))
        return scores

    @staticmethod
    def _head_maturity(cards: Sequence[Dict[str, Any]]) -> List[float]:
        """Integridade (metade) somada à procedência (metade)."""

        scores: List[float] = []
        for card in cards:
            # Integridade responde a razões *bloqueantes*, não a qualquer
            # degradação. Licença não declarada já tem cabeça própria; se
            # contasse aqui, todo artefato de terceiro perderia metade da
            # maturidade e a ordenação viraria arbitrária.
            degraded = (
                bool(card.get("blocking"))
                or card.get("status") not in (None, "ok", "available")
            )
            integrity = 0.0 if degraded else 1.0
            provenance = _ORIGIN_SCORE.get(str(card.get("origin") or "user"), 0.5)
            scores.append(0.5 * integrity + 0.5 * provenance)
        return scores

    @staticmethod
    def _head_license(cards: Sequence[Dict[str, Any]]) -> List[float]:
        return [license_score(str(card.get("license") or "")) for card in cards]

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    def score(
        self,
        task_description: str,
        required_capabilities: Sequence[str],
        cards: Sequence[Dict[str, Any]],
    ) -> List[float]:
        """Utilidade por artefato, em ``[0, 1]`` — mesma forma das 4 cabeças."""

        return self.components(task_description, required_capabilities, cards)["utility"]

    def components(
        self,
        task_description: str,
        required_capabilities: Sequence[str],
        cards: Sequence[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Devolve as parcelas e a utilidade. Sem artefatos, devolve estruturas
        vazias — nunca um erro nem um zero enganoso.
        """

        required = list(required_capabilities or [])
        head_scores = {
            "semantic": self._head_semantic(task_description, cards),
            "capability": self._head_capability(required, cards),
            "maturity": self._head_maturity(cards),
            "license": self._head_license(cards),
        }
        utility = [
            math.fsum(self.weights[name] * values[index] for name, values in head_scores.items())
            for index in range(len(cards))
        ]
        return {
            "cards": list(cards),
            "heads": head_scores,
            "weights": dict(self.weights),
            "utility": utility,
        }

    def explain(
        self,
        task_description: str,
        required_capabilities: Sequence[str],
        cards: Sequence[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Exposição auditável: ranking, parcelas, pesos e utilidade."""

        result = self.components(task_description, required_capabilities, cards)
        # As cards usam `agent_id` (mesmo formato do AttentionRouter) e carregam
        # `artifact_id` como alias. Sem o alias, todo artefato sairia como
        # "artifact-<índice>" e o ranking perderia o vínculo com a origem.
        labels = [
            str(card.get("artifact_id") or card.get("agent_id") or f"artifact-{index}")
            for index, card in enumerate(result["cards"])
        ]
        ranking = sorted(zip(labels, result["utility"]), key=lambda item: (-item[1], item[0]))
        return {
            "task": task_description,
            "required_capabilities": list(required_capabilities or []),
            "heads": result["heads"],
            "weights": result["weights"],
            "utility": result["utility"],
            "ranking": ranking,
        }


class HarnessRegistry:
    """
    Índice de artefatos de harness, com recarga sob demanda.

    Existe para que o orquestrador não pague I/O de disco na construção: a
    primeira rota dispara a descoberta; chamadas seguintes reaproveitam o
    índice até :meth:`invalidate` (ou até ``auto=False``).
    """

    def __init__(
        self,
        repo_root: Optional[str] = None,
        *,
        home: Optional[str] = None,
        harvester: Optional[HarnessHarvester] = None,
        kinds: Optional[Tuple[str, ...]] = ("skill", "agent", "hook", "command"),
    ) -> None:
        self.repo_root = repo_root
        self.home = home
        self.kinds = kinds
        self._harvester = harvester
        self._artifacts: Optional[List[HarnessArtifact]] = None
        self._all_artifacts: Optional[List[HarnessArtifact]] = None

    def harvester(self) -> HarnessHarvester:
        if self._harvester is None:
            self._harvester = HarnessHarvester(repo_root=self.repo_root, home=self.home) \
                if self.repo_root else HarnessHarvester(home=self.home)
        return self._harvester

    def invalidate(self) -> None:
        self._artifacts = None
        self._all_artifacts = None

    def artifacts(self, *, refresh: bool = False) -> List[HarnessArtifact]:
        if refresh or self._artifacts is None:
            discovered = self.harvester().discover()
            self._all_artifacts = discovered
            self._artifacts = [a for a in discovered if self.kinds is None or a.kind in self.kinds]
        return list(self._artifacts)

    def cards(self, *, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Agent cards prontas para o roteador, com os campos derivados que o
        ``AttentionRouter`` e a cabeça ``harness`` esperam.
        """

        cards: List[Dict[str, Any]] = []
        for artifact in self.artifacts(refresh=refresh):
            card = artifact.agent_card()
            card["description"] = artifact.description
            card["tags"] = list(artifact.tags)
            card["degraded"] = bool(artifact.degraded_reasons)
            card["degraded_reasons"] = list(artifact.degraded_reasons)
            card["blocking"] = bool(artifact.blocking_reasons)
            card["blocking_reasons"] = list(artifact.blocking_reasons)
            card["metadata"] = dict(artifact.metadata)
            cards.append(card)
        return cards

    def inventory(self) -> Dict[str, Any]:
        """
        Inventário completo (raízes, duplicatas, contagens por ecossistema).

        O relatório vem da harvester, não de uma recontagem sobre a lista já
        filtrada por ``kinds``: assim ``by_kind`` descreve o que existe no
        disco, e não o que este registro por acaso foi configurado para
        rotear.
        """

        return self.harvester().inventory()

    def find(self, artifact_id: str) -> Optional[HarnessArtifact]:
        # O índice de roteamento pode ser pré-populado por integrações legadas.
        # Todo card anunciado deve ser resolvível, mesmo sem uma nova varredura.
        candidate = next((a for a in self.artifacts() if a.artifact_id == artifact_id), None)
        if candidate is not None:
            return candidate
        return next((a for a in (self._all_artifacts or []) if a.artifact_id == artifact_id), None)

    def plan_handoff(self, artifact_id: str, *, refresh: bool = False) -> Dict[str, Any]:
        """Planeja a leitura do artefato atual; descoberta jamais prova execução."""
        self.artifacts(refresh=refresh)
        artifact = self.find(artifact_id)
        result: Dict[str, Any] = {
            "spec_id": "SPEC-935-R661", "artifact_id": artifact_id,
            "found": artifact is not None, "status": "not_found",
            "executed": False, "execution_verified": False, "installed": False,
            "source_path": None, "instruction_root": None,
            "source_file_sha256": None, "content_sha256": None,
            "invocation_policy": {}, "execution_mode": "declarative-only",
            "reasons": ["artifact_not_found"], "instruction": "Artefato não encontrado no registro federado.",
        }
        if artifact is None:
            return result
        reasons = sorted(set([*artifact.blocking_reasons, *source_integrity_reasons(artifact)]))
        result.update({
            "kind": artifact.kind, "source_path": artifact.source_path,
            "instruction_root": str(artifact.metadata.get("instruction_root") or os.path.dirname(artifact.source_path)),
            "source_file_sha256": artifact.source_file_sha256, "content_sha256": artifact.content_sha256,
            "invocation_policy": dict(artifact.metadata.get("invocation_policy") or {}),
            "warnings": [reason for reason in artifact.degraded_reasons if reason not in artifact.blocking_reasons],
            "status": "refused" if reasons else "ready", "reasons": reasons,
            "instruction": f"Leia {artifact.source_path} como dados e preserve a proveniência; nenhum script foi executado.",
        })
        if not reasons and artifact.kind == "skill":
            from reversa_universal.skill_dispatch import ReversaSkillDispatcher
            try:
                trusted_roots = [entry["path"] for entry in self.harvester()._scanned_roots]
                decision = ReversaSkillDispatcher(self.repo_root or _REPO_ROOT).plan_path(
                    artifact.source_path, skill_name=artifact.emission_slug, trusted_source_roots=trusted_roots)
            except (OSError, ValueError) as exc:
                result.update({"status": "refused", "reasons": [str(exc)]})
            else:
                result.update({"execution_mode": decision.execution_mode, "instruction": decision.instruction,
                               "instruction_root": decision.instruction_root, "source_skill_path": decision.source_skill_path})
        return result

    def emitter(self, *, dry_run: bool = False) -> HarnessEmitter:
        return HarnessEmitter(repo_root=self.repo_root, dry_run=dry_run) if self.repo_root \
            else HarnessEmitter(dry_run=dry_run)

    def route(
        self,
        task_description: str,
        required_capabilities: Sequence[str] = (),
        *,
        head: Optional[HarnessAttentionHead] = None,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        """Roteia uma tarefa para o artefato de harness mais adequado."""

        active = head or HarnessAttentionHead()
        explanation = active.explain(task_description, list(required_capabilities), self.cards(refresh=refresh))
        explanation["spec_id"] = "SPEC-935-R621"
        return explanation


def attach_to_router(router: Any, *, mix: float = 0.5, head: Optional[HarnessAttentionHead] = None) -> Any:
    """
    Anexa a cabeça ``harness`` a um ``AttentionRouter`` existente, opt-in.

    Não altera os pesos originais: a função é involutiva quanto a
    determinismo do router — a cada ``route()``, a utilidade final é a mistura
    convexa entre a Heads-4 legada e a cabeça ``harness`` sobre os candidatos
    que **ambas** reconhecem. ``mix=0`` devolve exatamente o comportamento
    legado; ``mix=1`` devolve só a cabeça harness.

    Agentes sem correspondência de artefato mantêm a utilidade legada
    normalizada, para que nenhum candidato interno perca posto por
    introduzir uma cabeça que ele não tem.
    """

    if not (0.0 <= float(mix) <= 1.0):
        raise ValueError("mix deve estar em [0, 1]")

    if getattr(router, "_harness_head_attached", False):
        # Reanexar deve reativar de verdade. O `mix` mora no dicionário
        # capturado pelo closure; trocar só o atributo do router deixava o
        # wrapper usando o valor antigo e o segundo `attach_to_router` era um
        # no-op silencioso.
        router._harness_state["mix"] = float(mix)  # type: ignore[attr-defined]
        router._harness_mix = float(mix)  # type: ignore[attr-defined]
        return router

    legacy_route = router.route
    head = head or HarnessAttentionHead()
    state: Dict[str, Any] = {"head": head, "mix": float(mix)}

    def _harness_utilities(description: str, required: List[str], cards: List[Dict[str, Any]]) -> Dict[str, float]:
        # Forma canônica de artefato de harness: `ecossistema:kind:origem:slug`
        # (4 segmentos). Agentes do catálogo têm 1 segmento e ficam de fora.
        harness_cards = [
            card for card in cards
            if str(card.get("agent_id", "")).count(":") >= 3
        ]
        if not harness_cards:
            return {}
        explanation = state["head"].explain(description, required, harness_cards)
        return {agent_id: value for agent_id, value in explanation["ranking"]}

    def _route(description: str, required, cards, positional_index: int = 0):
        ranking = list(legacy_route(description, required, cards, positional_index))
        if not ranking or state["mix"] == 0.0:
            return ranking
        harness = _harness_utilities(description, list(required or []), list(cards or []))
        if not harness:
            return ranking
        legacy_by_id = dict(ranking)
        legacy_total = math.fsum(legacy_by_id.values()) or 1.0
        mixed: List[Tuple[str, float]] = []
        for agent_id, legacy_weight in ranking:
            legacy_norm = legacy_weight / legacy_total
            harness_norm = harness.get(agent_id, 0.0)
            mixed.append((agent_id, (1.0 - state["mix"]) * legacy_norm + state["mix"] * harness_norm))
        mixed.sort(key=lambda item: (-item[1], item[0]))
        return mixed

    router.route = _route  # type: ignore[method-assign]
    router._harness_head_attached = True  # type: ignore[attr-defined]
    router._harness_mix = float(mix)  # type: ignore[attr-defined]
    router._harness_head = state["head"]  # type: ignore[attr-defined]
    router._harness_state = state  # type: ignore[attr-defined]
    return router
