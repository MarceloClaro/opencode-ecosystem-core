# -*- coding: utf-8 -*-
"""
Governança de custo de tokens multi-superfície — SPEC-981
================================================================
O Core executa em seis superfícies de inferência com semânticas de custo
heterogêneas:

  * ``local_compute`` — Ollama, LiteRT-LM (on-device), Colibri: custo de
    token zero, mas a máquina do operador paga energia/VRAM;
  * ``free_tier`` — Gemini CLI e a faixa gratuita do provedor: cota, não
    token cobrado;
  * ``metered_api`` — OpenCode Zen/Go, NVIDIA NIM, Gemini API, OpenAI API:
    tarifa por token, declarada por provider;
  * ``subscription`` — Codex CLI, Antigravity CLI, Claude CLI: crédito ou
    cota de assinatura, **não** preço por token.

Antes desta spec o Core não tinha registro de tarifas nem contabilidade de
dinheiro: o comando ``economy`` mede *stakes* da token economy
(``economy/token_economy.py``), que é garantia de comportamento, não gasto.

Regras invioláveis deste módulo:

  1. **Tarifa desconhecida não é tarifa zero.** ``estimate_cost`` devolve
     ``usd=None`` com ``basis="tariff_unknown"``. Nunca se presume barato o
     que não se sabe precificar.
  2. **Preço de API não é preço de assinatura.** Superfícies de assinatura
     e free tier devolvem ``usd=None`` com a base correta e ressalvas.
  3. **Nada aqui é cobrança observada.** Toda estimativa sai marcada como
     estimativa, com fonte e data de consulta do catálogo consultado.
  4. **Falha fechada.** Registro malformado levanta ``CostRegistryError``; o
     orçamento bloqueia quando o custo não é verificável.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT, "integrations", "cost_registry.json")

# ── Semânticas de cobrança ───────────────────────────────────────────────────
KIND_LOCAL = "local_compute"
KIND_FREE_TIER = "free_tier"
KIND_METERED = "metered_api"
KIND_SUBSCRIPTION = "subscription"
VALID_KINDS: Tuple[str, ...] = (KIND_LOCAL, KIND_FREE_TIER, KIND_METERED, KIND_SUBSCRIPTION)

# ── Níveis de complexidade ───────────────────────────────────────────────────
COMPLEXITIES: Tuple[str, ...] = ("trivial", "simples", "media", "complexa", "critica")

# ── Provider do opencode.json → superfície do registro ────────────────────────
# ``opencode`` e ``opencode-zen`` apontam o mesmo endpoint (Zen v1) com chaves
# de ambiente diferentes; a economia é a mesma.
PROVIDER_SURFACE: Dict[str, str] = {
    "opencode": "opencode-zen",
    "opencode-zen": "opencode-zen",
    "opencode-go": "opencode-go",
    "openai": "openai-api",
    "litert-lm": "local-litert-lm",
    "ollama-local": "local-ollama",
    "colibri": "local-colibri",
}

# ── Cadeias por complexidade (provider/model) ────────────────────────────────
# A ordem é a preferência; o último item é sempre um modelo capaz, porque a
# cadeia precisa terminar em um modelo que resolve a tarefa crítica.
#
# Justificativa medida no Core (não é opinião):
#   * R499 (curadoria free, tarefa IMO com scaffold MASWOS): modelos free
#     acertam 100% em matemática/acadêmico, com mimo-v2.5-free em 23,8 s;
#   * R506 (benchmark de código): mimo-v2.5-free 1/9, big-pickle 0/9 e
#     nemotron-3-ultra-free 2/9 corretos — por isso free NÃO é a cabeça da
#     cadeia de implementação, apenas a cauda.
CHAIN_TEMPLATES: Dict[str, Tuple[str, ...]] = {
    "trivial": (
        "litert-lm/litert-community/gemma-4-E2B-it-litert-lm",
        "colibri/olmoe-1b-7b",
        "opencode-zen/mimo-v2.6-flash-free",
    ),
    "simples": (
        "opencode-zen/mimo-v2.6-flash-free",
        "opencode-go/mimo-v2.6-flash",
        "opencode-go/deepseek-v4.1-flash",
    ),
    "media": (
        "opencode-go/mimo-v2.6-flash",
        "opencode-go/deepseek-v4.1-flash",
        "opencode-go/minimax-m3.1-flash",
    ),
    "complexa": (
        "opencode-go/deepseek-v4.1-flash",
        "opencode-go/mimo-v2.6-flash",
        "opencode-go/deepseek-v4-pro",
        "opencode-go/kimi-k2.7-code",
    ),
    "critica": (
        "opencode-go/deepseek-v4-pro",
        "opencode-go/kimi-k2.7-code",
        "opencode-zen/deepseek-v4-pro",
    ),
}

# Teto de custo por complexidade: a cadeia nunca o ultrapassa.
CEILINGS: Dict[str, str] = {
    "trivial": "free",
    "simples": "economico",
    "media": "economico",
    "complexa": "capaz",
    "critica": "capaz",
}

# ── Classificação de complexidade a partir do cartão do agente ───────────────
# Regras determinísticas e auditáveis: a primeira que casa vence.
#
# Cada chave pode declarar exclusões. Sem elas, ``literature_review`` casaria
# com ``review`` e mandaria o ``researcher`` para a faixa crítica — erro
# observado em RED: revisão de literatura é atividade de pesquisa, não gate.
_COMPLEXITY_RULES: Tuple[Tuple[str, Tuple[Tuple[str, Tuple[str, ...]], ...]], ...] = (
    (
        "critica",
        (
            ("audit", ()),
            ("review", ("literature", "code")),
            ("reviewer", ()),
            ("qa", ()),
            ("verific", ()),
            ("security", ()),
            ("proof", ()),
            ("lean", ()),
            ("blind", ()),
            ("preflight", ()),
            ("conformidade", ()),
            ("compliance", ()),
            ("forense", ()),
            ("red_history", ()),
            ("gate", ()),
        ),
    ),
    (
        "complexa",
        (
            ("research", ()),
            ("literature_review", ()),
            ("methodolog", ()),
            ("reproduc", ()),
            ("analysis", ()),
            ("formal", ()),
            ("statistic", ()),
            ("causal", ()),
            ("benchmark", ()),
            ("orchestrat", ()),
            ("quantum", ()),
            ("arquitetura", ()),
            ("architecture", ()),
        ),
    ),
    (
        "media",
        (
            ("engineering", ()),
            ("implement", ()),
            ("code", ()),
            ("refactor", ()),
            ("debug", ()),
            ("tdd", ()),
            ("test", ()),
            ("python", ()),
            ("devops", ()),
            ("coding", ()),
        ),
    ),
    (
        "simples",
        (
            ("writing", ()),
            ("escrita", ()),
            ("redact", ()),
            ("abnt", ()),
            ("formatting", ()),
            ("formatacao", ()),
            ("translat", ()),
            ("summar", ()),
            ("extract", ()),
            ("classif", ()),
            ("textual", ()),
            ("editorial", ()),
            ("publishing", ()),
            ("literary", ()),
            ("copy", ()),
            ("document", ()),
        ),
    ),
)


class CostRegistryError(RuntimeError):
    """Registro de tarifas ausente, malformado ou sem procedência."""


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Usage:
    """Consumo de tokens de uma execução (estimativa ou medido pelo provider)."""

    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0
    reasoning_tokens: int = 0

    @property
    def billable_input(self) -> int:
        """Entrada que NÃO veio do cache (a cache é cobrada à parte)."""
        return max(0, self.input_tokens - self.cached_input_tokens)

    def as_dict(self) -> Dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "reasoning_tokens": self.reasoning_tokens,
        }


@dataclass(frozen=True)
class CostEstimate:
    """Estimativa de custo de uma execução.

    ``usd is None`` significa **custo não verificável** — nunca "grátis".
    """

    surface_id: str
    model_id: str
    usd: Optional[float]
    basis: str
    is_estimate: bool
    source: Optional[str] = None
    source_date: Optional[str] = None
    caveats: Tuple[str, ...] = ()
    tokens: Dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "model_id": self.model_id,
            "usd": self.usd,
            "basis": self.basis,
            "is_estimate": self.is_estimate,
            "source": self.source,
            "source_date": self.source_date,
            "caveats": list(self.caveats),
            "tokens": dict(self.tokens),
        }


@dataclass(frozen=True)
class PlanStep:
    """Um degrau do plano de execução por superfície."""

    surface_id: str
    model_id: str
    provider: str
    complexity: str
    free: bool


@dataclass(frozen=True)
class BudgetDecision:
    """Decisão do orçamento — fechada por padrão."""

    allowed: bool
    reason: str
    surface_id: str
    projected_usd: Optional[float]
    ceiling_usd: float
    alternative: Optional[str] = None


# ── Registro ─────────────────────────────────────────────────────────────────

def _validate_registry(data: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, Mapping):
        raise CostRegistryError("registro de tarifas não é um mapeamento")
    for chave in ("surfaces", "tariffs", "provenance"):
        if chave not in data:
            raise CostRegistryError(f"registro sem a seção '{chave}'")
    if not isinstance(data["surfaces"], Mapping) or not data["surfaces"]:
        raise CostRegistryError("registro sem superfícies declaradas")
    if not isinstance(data["tariffs"], Mapping):
        raise CostRegistryError("registro sem tarifas declaradas")
    if not data["provenance"].get("primary", {}).get("url"):
        raise CostRegistryError("registro sem procedência declarada")

    for sid, meta in data["surfaces"].items():
        if not isinstance(meta, Mapping):
            raise CostRegistryError(f"superfície '{sid}' malformada")
        if meta.get("kind") not in VALID_KINDS:
            raise CostRegistryError(
                f"superfície '{sid}' com tipo de cobrança desconhecido: {meta.get('kind')!r}"
            )
        if not isinstance(meta.get("billable"), bool):
            raise CostRegistryError(f"superfície '{sid}' sem 'billable' booleano")

    for chave, tarifa in data["tariffs"].items():
        if not isinstance(tarifa, Mapping):
            raise CostRegistryError(f"tarifa '{chave}' malformada")
        if not tarifa.get("source"):
            raise CostRegistryError(f"tarifa '{chave}' sem fonte declarada")
        if not tarifa.get("source_date"):
            raise CostRegistryError(f"tarifa '{chave}' sem data de consulta")
        for campo in ("input", "output", "cache_read", "cache_write"):
            valor = tarifa.get(campo)
            if valor is None:
                continue
            if not isinstance(valor, (int, float)) or valor < 0:
                raise CostRegistryError(f"tarifa '{chave}' com '{campo}' inválido: {valor!r}")
    return dict(data)


def load_registry(path: Optional[str] = None) -> Dict[str, Any]:
    """Carrega e valida o registro de tarifas (falha fechada)."""
    caminho = path or REGISTRY_PATH
    try:
        with open(caminho, "r", encoding="utf-8") as fonte:
            data = json.load(fonte)
    except FileNotFoundError as exc:
        raise CostRegistryError(f"registro de tarifas ausente: {caminho}") from exc
    except json.JSONDecodeError as exc:
        raise CostRegistryError(f"registro de tarifas ilegível: {caminho}") from exc
    return _validate_registry(data)


def list_surfaces() -> List[Dict[str, Any]]:
    """Todas as superfícies declaradas, com seus metadados de cobrança."""
    registro = load_registry()
    saida = []
    for sid, meta in sorted(registro["surfaces"].items()):
        item = dict(meta)
        item["surface_id"] = sid
        item["n_models"] = sum(1 for k in registro["tariffs"] if k.startswith(f"{sid}::"))
        item["n_free"] = sum(
            1
            for k, t in registro["tariffs"].items()
            if k.startswith(f"{sid}::") and t.get("input") == 0 and t.get("output") == 0
        )
        saida.append(item)
    return saida


def surface_ids() -> List[str]:
    """Identificadores das superfícies declaradas."""
    return sorted(load_registry()["surfaces"])


def get_surface(surface_id: str) -> Dict[str, Any]:
    registro = load_registry()
    try:
        return registro["surfaces"][surface_id]
    except KeyError as exc:
        raise CostRegistryError(f"superfície desconhecida: {surface_id}") from exc


def get_tariff(surface_id: str, model_id: str) -> Optional[Dict[str, Any]]:
    """Tarifa declarada de um modelo numa superfície (``None`` se não houver)."""
    registro = load_registry()
    return registro["tariffs"].get(f"{surface_id}::{model_id}")


def is_free_model(surface_id: str, model_id: str) -> bool:
    """O modelo custa zero token nesta superfície?

    Verdadeiro apenas para: superfície local (o operador paga o compute) ou
    modelo com tarifa publicada 0/0. Desconhecido **não** é gratuito.
    """
    meta = get_surface(surface_id)
    if meta["kind"] == KIND_LOCAL:
        return True
    tarifa = get_tariff(surface_id, model_id)
    if tarifa is None:
        return False
    return tarifa.get("input") == 0 and tarifa.get("output") == 0


# ── Estimativa ───────────────────────────────────────────────────────────────

def _blended_usd(tarifa: Mapping[str, Any], uso: Usage) -> float:
    """Custo ponderado da execução (tarifa por milhão de tokens)."""
    cache_read = tarifa.get("cache_read")
    if cache_read is None:
        cache_read = tarifa.get("input", 0.0)
    custo = (
        uso.billable_input * float(tarifa.get("input") or 0.0)
        + uso.cached_input_tokens * float(cache_read)
        + uso.output_tokens * float(tarifa.get("output") or 0.0)
    ) / 1_000_000.0
    return round(custo, 10)


def estimate_cost(
    surface_id: str,
    model_id: str,
    uso: Optional[Usage] = None,
) -> CostEstimate:
    """Estima o custo de uma execução.

    Devolve ``usd=None`` quando o custo **não é verificável por token**
    (assinatura, free tier por cota) ou quando a tarifa é desconhecida.
    """
    uso = uso or Usage()
    meta = get_surface(surface_id)
    tarifa = get_tariff(surface_id, model_id)
    tokens = uso.as_dict()

    if meta["kind"] == KIND_LOCAL:
        return CostEstimate(
            surface_id=surface_id,
            model_id=model_id,
            usd=0.0,
            basis="local_compute",
            is_estimate=False,
            source=tarifa.get("source") if tarifa else None,
            source_date=tarifa.get("source_date") if tarifa else None,
            caveats=(
                "Custo de token zero: a energia e a VRAM ficam com o operador.",
                "A janela real do contexto vem do runtime, não do cliente.",
            ),
            tokens=tokens,
        )

    if meta["kind"] == KIND_SUBSCRIPTION:
        return CostEstimate(
            surface_id=surface_id,
            model_id=model_id,
            usd=None,
            basis="subscription_quota",
            is_estimate=False,
            source=tarifa.get("source") if tarifa else None,
            source_date=tarifa.get("source_date") if tarifa else None,
            caveats=(
                "Superfície por assinatura/cota: a tarifa por token não descreve este consumo.",
                "O consumo real é medido em créditos ou na cota do plano.",
            ),
            tokens=tokens,
        )

    if meta["kind"] == KIND_FREE_TIER:
        return CostEstimate(
            surface_id=surface_id,
            model_id=model_id,
            usd=None,
            basis="free_tier_quota",
            is_estimate=False,
            source=tarifa.get("source") if tarifa else None,
            source_date=tarifa.get("source_date") if tarifa else None,
            caveats=(
                "Camada gratuita sujeita a cota, limite de modelo e política de dados própria.",
                "Gratuito não é ilimitado: o excesso ou o 429 exige escalonamento declarado.",
            ),
            tokens=tokens,
        )

    if tarifa is None:
        return CostEstimate(
            surface_id=surface_id,
            model_id=model_id,
            usd=None,
            basis="tariff_unknown",
            is_estimate=False,
            caveats=(
                "Tarifa não declarada para este modelo nesta superfície.",
                "Custo desconhecido não é custo zero: o orçamento bloqueia por default.",
            ),
            tokens=tokens,
        )

    return CostEstimate(
        surface_id=surface_id,
        model_id=model_id,
        usd=_blended_usd(tarifa, uso),
        basis="tariff_declared",
        is_estimate=True,
        source=tarifa.get("source"),
        source_date=tarifa.get("source_date"),
        caveats=(
            "Estimativa a partir da tarifa declarada: não é cobrança observada em conta.",
            "Tributação de cache, tiers de contexto e escrevimento de cache variam por provider.",
        ),
        tokens=tokens,
    )


def rank_models(
    surface_id: str,
    uso: Optional[Usage] = None,
) -> List[Tuple[float, str]]:
    """Modelos da superfície ordenados por custo estimado (menor primeiro).

    Modelos sem tarifa declarada ficam de fora — não são comparáveis.
    """
    uso = uso or Usage()
    registro = load_registry()
    prefixo = f"{surface_id}::"
    ranked: List[Tuple[float, str]] = []
    for chave, tarifa in registro["tariffs"].items():
        if not chave.startswith(prefixo):
            continue
        model_id = chave[len(prefixo):]
        ranked.append((_blended_usd(tarifa, uso), model_id))
    return sorted(ranked)


# ── Complexidade e cadeias ───────────────────────────────────────────────────

def _tokens_de_meta(meta: Mapping[str, Any]) -> List[str]:
    """Tokens textuais determinísticos a partir dos campos estruturados."""
    valores: List[str] = []

    def _adiciona(valor: Any) -> None:
        if valor is None:
            return
        if isinstance(valor, (list, tuple, set)):
            for item in valor:
                _adiciona(item)
            return
        if isinstance(valor, Mapping):
            for chave, item in valor.items():
                _adiciona(chave)
                _adiciona(item)
            return
        texto = str(valor).strip().lower()
        if not texto:
            return
        texto = re.sub(r"[\[\]{}<>()\"']", " ", texto)
        for parte in re.split(r"[\s,;/|]+", texto):
            if parte:
                valores.append(parte)

    for campo in ("id", "agent_id", "name", "category", "type", "episteme"):
        _adiciona(meta.get(campo))
    for campo in ("tags", "capabilities"):
        _adiciona(meta.get(campo))
    # Skills A2A são dicionários com prosa longa (description/examples). A
    # classificação de complexidade usa APENAS as tags declaradas: texto
    # livre não pode decidir o modelo de um agente.
    skills = meta.get("skills")
    if isinstance(skills, (list, tuple)):
        for skill in skills:
            if isinstance(skill, Mapping):
                _adiciona(skill.get("tags"))
            else:
                _adiciona(skill)
    return valores


def complexity_for_agent(meta: Optional[Mapping[str, Any]]) -> str:
    """Classifica a complexidade declarada de um agente.

    Duas passagens, nesta ordem:

      1. **Campos declarados** do cartão (id, categoria, tipo, tags) — o que o
         autor do agente escreveu.
      2. **Campos derivados** (capabilities, skills) — heurística do loader.

    A separação importa: as capabilities derivadas trazem rótulos amplos
    (``code_review``, ``architecture``, ``research``) que, se pesassem como
    declaração, jogariam o ``coder`` na faixa crítica. O cartão declarado
    sempre manda.
    """
    if not meta:
        return "media"

    declarado = _tokens_de_meta(
        {
            "id": meta.get("id"),
            "agent_id": meta.get("agent_id"),
            "name": meta.get("name"),
            "category": meta.get("category"),
            "type": meta.get("type"),
            "tags": meta.get("tags"),
        }
    )
    nivel = _classificar_tokens(declarado)
    if nivel:
        return nivel

    derivado = _tokens_de_meta(
        {"capabilities": meta.get("capabilities"), "skills": meta.get("skills")}
    )
    nivel = _classificar_tokens(derivado)
    return nivel or "media"


def _classificar_tokens(tokens: Sequence[str]) -> Optional[str]:
    """Primeira regra que casa com os tokens; ``None`` se nenhuma casa."""
    if not tokens:
        return None
    conjunto = set(tokens)
    for nivel, chaves in _COMPLEXITY_RULES:
        for chave, exclusoes in chaves:
            for token in conjunto:
                if chave not in token:
                    continue
                if any(exclusao in token for exclusao in exclusoes):
                    continue
                return nivel
    return None


def agent_chain(complexity: str) -> List[str]:
    """Cadeia ordenada de fallback (``provider/model``) para a complexidade."""
    if complexity not in CHAIN_TEMPLATES:
        raise CostRegistryError(f"complexidade desconhecida: {complexity!r}")
    return list(CHAIN_TEMPLATES[complexity])


def head_model_for(
    meta: Optional[Mapping[str, Any]],
    cadeia: Sequence[str],
    policy: Optional[Mapping[str, Any]] = None,
) -> Optional[str]:
    """Modelo da cabeça, quando a política autoriza a fixação.

    A fixação é suprimida em três casos, todos declarados:

    1. ``policy.apply_head_model`` desligado — a cadeia continua publicada,
       mas cada agente conserva o modelo global da sessão;
    2. cadeia vazia — nada a fixar;
    3. categoria em ``policy.no_fix_model_categories`` ou id com prefixo em
       ``policy.no_fix_model_prefixes`` — o cartão deliberadamente não fixa
       modelo porque o fallback do runtime é o caminho válido (SPEC-935-R276:
       agentes literários sem ``model`` explícito para evitar retorno vazio).

    A supressão é explícita e auditável: ela remove apenas a fixação, nunca a
    cadeia de fallback declarada em ``options.model_fallbacks``.
    """
    politica = dict(policy or {})
    if not politica.get("apply_head_model", True):
        return None
    if not cadeia:
        return None
    meta = meta or {}
    agent_id = str(meta.get("id") or "")
    categoria = str(meta.get("category") or "")
    if categoria and categoria in (politica.get("no_fix_model_categories") or []):
        return None
    for prefixo in politica.get("no_fix_model_prefixes") or []:
        if prefixo and agent_id.startswith(str(prefixo)):
            return None
    return str(cadeia[0])


def resolve_plan(complexity: str) -> List[PlanStep]:
    """Plano de execução por superfície, na ordem de preferência."""
    passos: List[PlanStep] = []
    for ref in agent_chain(complexity):
        provider, model_id = ref.split("/", 1)
        surface_id = PROVIDER_SURFACE.get(provider)
        if surface_id is None:
            continue
        passos.append(
            PlanStep(
                surface_id=surface_id,
                model_id=model_id,
                provider=provider,
                complexity=complexity,
                free=is_free_model(surface_id, model_id),
            )
        )
    return passos


# ── Orçamento ────────────────────────────────────────────────────────────────

class BudgetLedger:
    """Registro de custo estimado por superfície, com tetos fail-closed.

    O ledger guarda **estimativas** derived de tarifas declaradas. Ele não
    substitui a fatura do provedor: serve para decidir, não para_atestar.
    """

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or os.path.join(ROOT, ".mci_state", "cost_ledger.jsonl")

    # -- escrita ----------------------------------------------------------
    def record(self, estimativa: CostEstimate) -> None:
        registro = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "surface_id": estimativa.surface_id,
            "model_id": estimativa.model_id,
            "usd": estimativa.usd,
            "basis": estimativa.basis,
            "is_estimate": estimativa.is_estimate,
            "tokens": estimativa.tokens,
        }
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as destino:
            destino.write(json.dumps(registro, ensure_ascii=False) + "\n")

    # -- leitura ----------------------------------------------------------
    def entries(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        entradas = []
        with open(self.path, "r", encoding="utf-8") as fonte:
            for linha in fonte:
                linha = linha.strip()
                if not linha:
                    continue
                try:
                    entradas.append(json.loads(linha))
                except json.JSONDecodeError:
                    continue
        return entradas

    def usage_usd(self, surface_id: str) -> float:
        """Soma estimada da superfície (custos desconhecidos NÃO contam como 0)."""
        total = 0.0
        for entrada in self.entries():
            if entrada.get("surface_id") != surface_id:
                continue
            valor = entrada.get("usd")
            if isinstance(valor, (int, float)):
                total += float(valor)
        return round(total, 10)

    def unknown_count(self, surface_id: str) -> int:
        """Quantas execuções ficaram sem custo verificável na superfície."""
        return sum(
            1
            for entrada in self.entries()
            if entrada.get("surface_id") == surface_id and entrada.get("usd") is None
        )

    # -- decisão ----------------------------------------------------------
    def check(
        self,
        surface_id: str,
        ceiling_usd: float,
        pending: Optional[CostEstimate] = None,
    ) -> BudgetDecision:
        """Decide se a próxima execução cabe no teto (falha fechada)."""
        meta = get_surface(surface_id)
        if meta["kind"] == KIND_LOCAL:
            return BudgetDecision(
                allowed=True,
                reason="custo de token local: o teto monetário não se aplica",
                surface_id=surface_id,
                projected_usd=0.0,
                ceiling_usd=ceiling_usd,
            )
        if pending is not None and pending.usd is None:
            return BudgetDecision(
                allowed=False,
                reason=(
                    f"custo não verificável: tarifa desconhecida para '{pending.model_id}' "
                    f"em '{surface_id}' — não se presume barato o que não se sabe precificar"
                ),
                surface_id=surface_id,
                projected_usd=None,
                ceiling_usd=ceiling_usd,
                alternative="superfície local ou modelo com tarifa declarada",
            )
        adicional = pending.usd if pending is not None and pending.usd is not None else 0.0
        projetado = round(self.usage_usd(surface_id) + adicional, 10)
        if projetado > ceiling_usd:
            return BudgetDecision(
                allowed=False,
                reason=(
                    f"teto excedido: projetado US$ {projetado:.4f} > teto US$ {ceiling_usd:.4f} "
                    f"em '{surface_id}'"
                ),
                surface_id=surface_id,
                projected_usd=projetado,
                ceiling_usd=ceiling_usd,
                alternative="modelo mais barato da mesma superfície ou superfície gratuita",
            )
        return BudgetDecision(
            allowed=True,
            reason=f"projetado US$ {projetado:.4f} dentro do teto US$ {ceiling_usd:.4f}",
            surface_id=surface_id,
            projected_usd=projetado,
            ceiling_usd=ceiling_usd,
        )


# ── Relatório ────────────────────────────────────────────────────────────────

def _mais_economico(surface_id: str) -> Optional[Dict[str, Any]]:
    ranked = rank_models(
        surface_id,
        Usage(input_tokens=1_000_000, output_tokens=100_000, cached_input_tokens=800_000),
    )
    pagos = [(custo, modelo) for custo, modelo in ranked if custo > 0]
    if not pagos:
        return None
    custo, modelo = pagos[0]
    return {"model_id": modelo, "usd_por_1M_entrada_80pct_cache_100k_saida": custo}


def report(ledger: Optional[BudgetLedger] = None) -> Dict[str, Any]:
    """Relatório de governança de custo (dinheiro), separado da token economy."""
    registro = load_registry()
    ledger = ledger or BudgetLedger()
    superficies = []
    for meta in list_surfaces():
        item = dict(meta)
        item["mais_economico_pago"] = _mais_economico(meta["surface_id"])
        item["gasto_estimado_usd"] = ledger.usage_usd(meta["surface_id"])
        item["execucoes_sem_custo_verificavel"] = ledger.unknown_count(meta["surface_id"])
        superficies.append(item)
    return {
        "provenance": registro["provenance"],
        "policy": registro.get("policy", {}),
        "surfaces": superficies,
        "chains": {nivel: agent_chain(nivel) for nivel in COMPLEXITIES},
        "separation_note": (
            "Este relatório mede custo monetário estimado. A token economy "
            "(economy/token_economy.py) mede stakes e slashing de comportamento: "
            "são grandezas diferentes e não devem ser somadas."
        ),
        "limitations": [
            "Tarifas são declaradas por catálogo consultado; não são cobrança observada.",
            "Superfícies de assinatura e free tier não têm preço por token.",
            "0/0 significa custo publicado zero: pode ser gratuito ou sem preço publicado.",
        ],
    }


def suggested_provider_blocks() -> Dict[str, Any]:
    """Blocos de provider prontos para aplicação EXPLÍCITA pelo operador.

    A governança não habilita provider nenhum por conta própria: uma
    superfície sem chave não pode virar erro silencioso na inicialização.
    """
    return {
        "nvidia-nim": {
            "options": {
                "apiKey": "{env:NVIDIA_API_KEY}",
                "baseURL": "https://integrate.api.nvidia.com/v1",
            },
            "models": {
                model_id: {"name": model_id, "cost": {"input": 0.0, "output": 0.0}}
                for model_id in sorted(
                    chave.split("::", 1)[1]
                    for chave in load_registry()["tariffs"]
                    if chave.startswith("nvidia-nim::")
                )
            },
        }
    }
