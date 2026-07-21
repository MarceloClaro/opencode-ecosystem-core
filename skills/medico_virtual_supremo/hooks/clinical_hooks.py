# -*- coding: utf-8 -*-
"""
Sistema de Hooks Clínicos — Implementação
============================================
Gerencia hooks de pré e pós-processamento para cada etapa do pipeline.
Permite extensão por plugins sem modificar o pipeline principal.

Etapas com hooks:
  - pre_normalize / post_normalize   (Etapa 1)
  - pre_hypothesis / post_hypothesis (Etapa 3)
  - pre_plan / post_plan             (Etapa 5)
  - pre_verify / post_verify         (Etapa 6)
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional

# MetaBus opcional (falha graceful)
try:
    from skills.medico_virtual_supremo.metabus_integration import cross_validation_executed
    _METABUS_HOOKS = True
except ImportError:
    _METABUS_HOOKS = False

logger = logging.getLogger(__name__)


class ClinicalHook:
    """
    Um hook clínico individual.

    Attributes:
        name: Nome do hook (único por etapa).
        stage: Etapa do pipeline (ex: 'pre_normalize', 'post_hypothesis').
        fn: Função callback (contexto -> contexto).
        priority: Ordem de execução (menor = primeiro).
        description: Descrição do propósito do hook.
    """

    def __init__(
        self,
        name: str,
        stage: str,
        fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        priority: int = 100,
        description: str = "",
    ):
        self.name = name
        self.stage = stage
        self.fn = fn
        self.priority = priority
        self.description = description
        self.execution_time: float = 0.0
        self.execution_count: int = 0

    def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa o hook com medição de tempo."""
        start = time.perf_counter()
        try:
            result = self.fn(context)
            self.execution_time += time.perf_counter() - start
            self.execution_count += 1
            return result
        except Exception as e:
            logger.warning(f"Hook '{self.name}' na etapa '{self.stage}' falhou: {e}")
            # Hook falha graciosamente — retorna contexto original
            return context

    def __repr__(self) -> str:
        return f"<ClinicalHook '{self.name}' stage='{self.stage}' pri={self.priority}>"


# ──────────────────────────────────────────────────────────────────────────────
# Gerenciador de Hooks
# ──────────────────────────────────────────────────────────────────────────────

# Etapas válidas para hooks
STAGES = {
    "pre_normalize",
    "post_normalize",
    "pre_hypothesis",
    "post_hypothesis",
    "pre_plan",
    "post_plan",
    "pre_verify",
    "post_verify",
}


class ClinicalHookManager:
    """
    Gerencia o ciclo de vida de hooks clínicos.

    Uso:
        manager = ClinicalHookManager()

        @manager.register("pre_normalize", priority=10)
        def sanitizar_dados(ctx):
            ctx["dados_sanitizados"] = True
            return ctx

        # Executar todos os hooks de uma etapa
        contexto = manager.execute("pre_normalize", {"paciente": ...})
    """

    def __init__(self):
        self._hooks: Dict[str, List[ClinicalHook]] = {stage: [] for stage in STAGES}

    def register(
        self,
        stage: str,
        name: Optional[str] = None,
        priority: int = 100,
        description: str = "",
    ) -> Callable:
        """
        Decorator para registrar um hook.

        Args:
            stage: Etapa do hook (ex: 'pre_normalize').
            name: Nome do hook (auto se None).
            priority: Prioridade (menor = execução mais cedo).
            description: Descrição do hook.
        """
        if stage not in STAGES:
            raise ValueError(
                f"Etapa inválida '{stage}'. Válidas: {', '.join(sorted(STAGES))}"
            )

        def decorator(fn: Callable) -> Callable:
            hook_name = name or fn.__name__
            hook = ClinicalHook(
                name=hook_name,
                stage=stage,
                fn=fn,
                priority=priority,
                description=description,
            )
            self._hooks[stage].append(hook)
            self._hooks[stage].sort(key=lambda h: h.priority)
            return fn

        return decorator

    def add(self, hook: ClinicalHook) -> None:
        """Adiciona um hook já instanciado."""
        if hook.stage not in STAGES:
            raise ValueError(f"Etapa inválida '{hook.stage}'")
        self._hooks[hook.stage].append(hook)
        self._hooks[hook.stage].sort(key=lambda h: h.priority)

    def execute(
        self, stage: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa todos os hooks registrados para uma etapa.

        Args:
            stage: Nome da etapa.
            context: Contexto atual do pipeline.

        Returns:
            Contexto modificado pelos hooks.
        """
        if stage not in STAGES:
            raise ValueError(f"Etapa inválida '{stage}'")

        hooks = self._hooks.get(stage, [])
        for hook in hooks:
            context = hook(context)
        return context

    def get_hooks(self, stage: Optional[str] = None) -> List[ClinicalHook]:
        """Retorna hooks registrados, opcionalmente filtrados por etapa."""
        if stage:
            if stage not in STAGES:
                raise ValueError(f"Etapa inválida '{stage}'")
            return self._hooks.get(stage, [])
        result = []
        for s in sorted(STAGES):
            result.extend(self._hooks[s])
        return result

    def summary(self) -> Dict[str, Any]:
        """Resumo dos hooks registrados."""
        return {
            "total_hooks": sum(len(h) for h in self._hooks.values()),
            "por_etapa": {
                stage: [
                    {"name": h.name, "priority": h.priority, "calls": h.execution_count}
                    for h in hooks
                ]
                for stage, hooks in self._hooks.items()
                if hooks
            },
        }

    def clear(self) -> None:
        """Remove todos os hooks."""
        for stage in STAGES:
            self._hooks[stage] = []


# ──────────────────────────────────────────────────────────────────────────────
# Hooks Padrão
# ──────────────────────────────────────────────────────────────────────────────

def criar_hook_manager_padrao() -> ClinicalHookManager:
    """
    Cria um ClinicalHookManager com hooks padrão pré-registrados.

    Estes hooks implementam as funcionalidades base:
    - Sanitização de dados sensíveis (pre_normalize)
    - Detecção de dados duplicados (post_normalize)
    - Ranqueamento de hipóteses por gravidade (post_hypothesis)
    - Adaptação de linguagem ao público (post_plan)
    """
    manager = ClinicalHookManager()

    @manager.register("pre_normalize", priority=10, description="Sanitizar dados sensíveis (RG, CPF, nome completo)")
    def hook_sanitizar_dados(ctx):
        # Garante que o rastro de hooks existe
        ctx.setdefault("hooks", [])
        ctx.setdefault("alertas", [])
        dados = ctx.get("clinical_data", {})
        # Remove campos potencialmente identificáveis
        campos_sensiveis = ["cpf", "rg", "nome_completo", "endereco", "telefone", "email"]
        for campo in campos_sensiveis:
            dados.pop(campo, None)
        ctx["clinical_data"] = dados
        ctx["hooks"].append("sanitizar_dados: OK")
        return ctx

    @manager.register("pre_normalize", priority=20, description="Validar faixa etária")
    def hook_validar_idade(ctx):
        paciente = ctx.get("patient", {})
        idade = paciente.get("age_years")
        if idade is not None and (idade < 0 or idade > 130):
            ctx["alertas"].append(f"Idade inválida: {idade}")
            paciente["age_years"] = None
        ctx["patient"] = paciente
        ctx["hooks"].append("validar_idade: OK")
        return ctx

    @manager.register("post_normalize", priority=10, description="Detectar valores críticos em exames")
    def hook_detectar_criticos(ctx):
        dados = ctx.get("clinical_data", {})
        sinais = dados.get("vital_signs", {})
        criticos = []

        # Sinais vitais críticos
        if sinais.get("temp") and sinais["temp"] > 41:
            criticos.append("Hiperpirexia (>41°C)")
        if sinais.get("spo2") and sinais["spo2"] < 90:
            criticos.append("Hipoxemia (SpO2 <90%)")
        if sinais.get("fc") and sinais["fc"] > 140:
            criticos.append("Taquicardia grave (FC >140 bpm)")
        if sinais.get("fr") and sinais["fr"] > 35:
            criticos.append("Taquipneia grave (FR >35 irpm)")

        if criticos:
            ctx.setdefault("alertas", []).extend(criticos)
        ctx["hooks"].append(f"detectar_criticos: {len(criticos)} críticos encontrados")
        return ctx

    @manager.register("post_hypothesis", priority=10, description="Ranquear hipóteses por gravidade")
    def hook_ranquear_hipoteses(ctx):
        hipoteses = ctx.get("hipoteses", [])
        ordem_status = {"grave_não_perder": 0, "provável": 1, "iatrogênica": 2, "alternativa": 3}
        hipoteses.sort(key=lambda h: ordem_status.get(h.get("status", "alternativa"), 99))
        ctx["hipoteses"] = hipoteses
        ctx["hooks"].append("ranquear_hipoteses: OK")
        return ctx

    @manager.register("post_plan", priority=10, description="Adaptar linguagem ao público-alvo")
    def hook_adaptar_linguagem(ctx):
        modo = ctx.get("modo", "professional_cds")
        if modo == "patient_education":
            plano = ctx.get("plano", {})
            # Simplificar termos técnicos no plano
            if "red_flags" in plano:
                plano["red_flags_orientacao"] = [
                    f"⚠️ {flag}" for flag in plano.get("red_flags", [])
                ]
            ctx["plano"] = plano
            ctx["hooks"].append("adaptar_linguagem: modo paciente")
        return ctx

    @manager.register("pre_verify", priority=10, description="Carregar checklist baseado no modo")
    def hook_checklist_por_modo(ctx):
        modo = ctx.get("modo", "professional_cds")
        checklists = {
            "professional_cds": [
                "diagnóstico sem sustentação?",
                "dose sem parâmetros?",
                "sinal de alarme omitido?",
            ],
            "patient_education": [
                "linguagem acessível?",
                "prescrição evitada?",
                "orientação de busca de atendimento?",
            ],
            "research": ["fonte citada?", "viés declarado?", "conflito de interesse?"],
            "simulation": ["caso marcado como fictício?", "sem recomendações reais?"],
        }
        ctx["checklist_personalizado"] = checklists.get(modo, checklists["professional_cds"])
        ctx["hooks"].append(f"checklist_por_modo: {modo}")
        return ctx

    @manager.register("post_verify", priority=10, description="Registrar auditoria no contexto e publicar no MetaBus")
    def hook_registrar_auditoria(ctx):
        ctx.setdefault("hooks", [])
        auditoria = ctx.get("auditoria", {})
        checks_passaram = auditoria.get("checks_passed", [])
        checks_falharam = auditoria.get("checks_failed", [])
        ctx["hooks"].append(
            f"auditoria: {len(checks_passaram)} checks OK, {len(checks_falharam)} falhas"
        )

        # 🧠 MetaBus: publica resultado da auditoria como validação cruzada
        if _METABUS_HOOKS:
            try:
                run_id = ctx.get("run_id", "N/A") or "N/A"
                cross_validation_executed(
                    run_id=run_id,
                    especialistas_consultados=1,
                    consenso=len(checks_falharam) == 0,
                    conflitos=len(checks_falharam),
                )
            except Exception:
                pass

        return ctx

    return manager
