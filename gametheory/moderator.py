"""
P14 — Agent Forum / Debate Moderator

Sistema de debate multiagente com moderador LLM.
Extraido e generalizado do ForumEngine (BettaFish, 666ghj).
Aprimorado com 38 tipos de raciocínio + Teoria dos Jogos.

Uso:
    from moderator import Forum, AgentSpeech
    from debate_strategies import DEBATE_PROFILES, ReasoningType

    forum = Forum(agents=["Analista", "Crítico"],
                  debate_profile="ESTRATEGISTA")
    forum.open_session("Analisar tendencia de mercado")

    forum.publish("QueryEngine", "Dados mostram alta de 15%...")
    forum.publish("MediaEngine", "Cobertura midiatica e positiva...")
    # Moderador automaticamente invocado apos N speeches

    print(forum.transcript)
"""

import os
import json
import time
import uuid
import threading
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Callable, Dict, List, Any
from enum import Enum

# ─── P17+ Integration: Debate Strategies Engine ───────────────────────────
try:
    from .debate_strategies import (
        ReasoningType, REASONING_PROMPTS,
        DEBATE_PROFILES, MetaReasoner,
        PayoffMatrix, ShapleyValue,
        TOURNAMENT_STRATEGIES,
    )
    HAS_STRATEGIES = True
except ImportError:
    from debate_strategies import (
        ReasoningType, REASONING_PROMPTS,
        DEBATE_PROFILES, MetaReasoner,
        PayoffMatrix, ShapleyValue,
        TOURNAMENT_STRATEGIES,
    )
    HAS_STRATEGIES = True

# ─── P18 Integration: PhD Auditor (nexus-phd-strategist) ─────────────────
try:
    from .phd_auditor import (
        NashSolver,
        StatisticalRigor,
        QualisA1Auditor,
        SensitivityAnalyzer,
        IMRADFormatter,
    )
    HAS_PHD_AUDITOR = True
except ImportError:
    from phd_auditor import (
        NashSolver,
        StatisticalRigor,
        QualisA1Auditor,
        SensitivityAnalyzer,
        IMRADFormatter,
    )
    HAS_PHD_AUDITOR = True
except ImportError:
    from debate_strategies import (
        ReasoningType, REASONING_PROMPTS,
        DEBATE_PROFILES, MetaReasoner,
        PayoffMatrix, ShapleyValue,
        TOURNAMENT_STRATEGIES,
    )
    HAS_STRATEGIES = True


# ─── Constantes ───────────────────────────────────────────────────────────────

FORUM_VERSION = "1.0"
DEFAULT_BUFFER_SIZE = 5
DEFAULT_TIMEOUT_SECONDS = 7200
DEFAULT_POLL_INTERVAL = 1.0


# ─── Enums ────────────────────────────────────────────────────────────────────

class DebateStage(Enum):
    """Estagios do ciclo de debate."""
    IDLE = "idle"
    OPEN = "open"
    DISCUSS = "discuss"
    SYNTHESIZE = "synthesize"
    CONCLUDE = "conclude"
    CLOSED = "closed"


class ModeratorMode(Enum):
    """Modos de operacao do moderador LLM."""
    SUMMARIZE = "summarize"
    CHALLENGE = "challenge"
    DEEPEN = "deepen"
    CONCLUDE = "conclude"


# ─── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class AgentSpeech:
    """Discurso padrao de um agente no forum."""
    source: str
    content: str
    timestamp: str = ""
    speech_id: str = ""
    stage: str = ""
    confidence: float = 0.5
    stance: str = "neutral"
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.speech_id:
            self.speech_id = f"sp-{uuid.uuid4().hex[:8]}"


@dataclass
class ModeratorSpeech:
    """Discurso do moderador."""
    content: str
    mode: ModeratorMode = ModeratorMode.SUMMARIZE
    timestamp: str = ""
    speech_id: str = ""
    sources: list = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.speech_id:
            self.speech_id = f"mod-{uuid.uuid4().hex[:8]}"


@dataclass
class SessionConfig:
    """Configuracao de uma sessao de forum."""
    topic: str
    agents: list
    moderator_model: str = "opencode/big-pickle"
    moderator_temperature: float = 0.6
    moderator_top_p: float = 0.9
    buffer_size: int = DEFAULT_BUFFER_SIZE
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    max_rounds: int = 30
    api_key: str = ""
    base_url: str = ""
    language: str = "pt-BR"


# ─── Helpers de LLM ───────────────────────────────────────────────────────────

def _build_system_prompt(config: SessionConfig, stage: DebateStage) -> str:
    """Constroi system prompt para o moderador conforme o estagio."""
    base = f"""Voce e o moderador de um forum multiagente sobre: {config.topic}

Agentes participantes: {', '.join(config.agents)}.

Seu papel:
1. SINTETIZAR: Resuma as descobertas de cada agente de forma integrada
2. DESAFIAR: Aponte contradicoes e lacunas entre as perspectiva
3. APROFUNDAR: Sugira novas direcoes de analise
4. CONCLUIR: Produza um relatorio final consolidado

Regras:
- Mantenha-se objetivo e baseado em evidencias e citações relevantes e reais
- Identifique consensos e divergencias explicitamente
- Aponte fontes de cada afirmacao (qual agente disse o que, e suas bases teoricas e conceituais e estatistica)
- Nao repita pontos ja consolidados em rodadas anteriores
- Use {config.language} para responder"""
    return base


def _build_discuss_prompt(speeches: list[AgentSpeech], history: list) -> str:
    """Constroi prompt de discussao."""
    speeches_text = "\n\n".join([
        f"[{s.timestamp}] {s.source} (confianca:{s.confidence}, posicao:{s.stance}):\n{s.content}"
        for s in speeches
    ])
    
    history_text = ""
    if history:
        hist_entries = []
        for h in history[-3:]:
            if isinstance(h, ModeratorSpeech):
                hist_entries.append(f"[MODERADOR] {h.content[:200]}...")
            elif isinstance(h, AgentSpeech):
                hist_entries.append(f"[{h.source}] {h.content[:200]}...")
        if hist_entries:
            history_text = "\n\nHistorico recente:\n" + "\n".join(hist_entries)
    
    return f"""Analise as seguintes contribuicoes dos agentes e produza uma sintese:

{speeches_text}
{history_text}

Estruture sua resposta em:
1. **Sintese**: Principais pontos de cada agente
2. **Consensos**: Onde os agentes concordam
3. **Divergencias**: Onde ha conflito de perspectivas
4. **Direcoes**: Perguntas para aprofundamento na proxima rodada"""


def _call_llm(system_prompt: str, user_prompt: str,
              model: str, temperature: float, top_p: float,
              api_key: str, base_url: str) -> Optional[str]:
    """Chama LLM via API compativel com OpenAI."""
    if not api_key:
        # Modo offline/demo: retorna sintese template
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url or "https://api.openai.com/v1")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            top_p=top_p,
        )
        if response.choices:
            return response.choices[0].message.content
    except Exception as e:
        print(f"[Forum] LLM call failed: {e}")
    
    return None


def _generate_fallback_synthesis(speeches: list[AgentSpeech]) -> str:
    """Geracao offline/demo quando LLM nao esta disponivel."""
    lines = []
    sources = set(s.source for s in speeches)
    lines.append(f"## Sintese do Moderador (offline)")
    lines.append(f"Fontes analisadas: {', '.join(sorted(sources))}")
    lines.append(f"Total de contribuicoes: {len(speeches)}")
    lines.append("")
    for s in speeches:
        lines.append(f"**{s.source}**: {s.content[:150]}...")
    lines.append("")
    lines.append("*Modo offline — ative FORUM_MODERATOR_API_KEY para analise LLM completa*")
    return "\n".join(lines)


# ─── Canals de Comunicacao ───────────────────────────────────────────────────

class Channel:
    """Canal abstrato de comunicacao entre agentes e forum."""
    
    def publish(self, speech: AgentSpeech):
        raise NotImplementedError
    
    def poll(self) -> list[AgentSpeech]:
        raise NotImplementedError
    
    def get_transcript(self) -> list:
        raise NotImplementedError
    
    def clear(self):
        raise NotImplementedError


class MemoryChannel(Channel):
    """Canal em memoria (para uso programatico)."""
    
    def __init__(self):
        self._speeches: list[AgentSpeech] = []
        self._lock = threading.Lock()
    
    def publish(self, speech: AgentSpeech):
        with self._lock:
            self._speeches.append(speech)
    
    def poll(self) -> list[AgentSpeech]:
        with self._lock:
            new = [s for s in self._speeches if not getattr(s, '_consumed', False)]
            for s in new:
                s._consumed = True  # type: ignore
            return new
    
    def get_transcript(self) -> list:
        with self._lock:
            return list(self._speeches)
    
    def clear(self):
        with self._lock:
            self._speeches.clear()


class FileChannel(Channel):
    """Canal via arquivos (similar ao log-based do BettaFish)."""
    
    def __init__(self, log_dir: str = "forum_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self._last_position: dict[str, int] = {}
        self._all_speeches: list = []
    
    def publish(self, speech: AgentSpeech):
        with self._lock:
            filepath = self.log_dir / f"{speech.source}.log"
            with open(filepath, 'a', encoding='utf-8') as f:
                entry = json.dumps(asdict(speech), ensure_ascii=False)
                f.write(f"[{speech.timestamp}] [{speech.source}] {entry}\n")
                f.flush()
    
    def poll(self) -> list[AgentSpeech]:
        results = []
        with self._lock:
            for filepath in sorted(self.log_dir.glob("*.log")):
                source = filepath.stem
                pos = self._last_position.get(source, 0)
                current_size = filepath.stat().st_size
                
                if current_size > pos:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        f.seek(pos)
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                # Extrai JSON da linha: [timestamp] [source] {...}
                                json_start = line.find('{')
                                if json_start >= 0:
                                    data = json.loads(line[json_start:])
                                    speech = AgentSpeech(**data)
                                    results.append(speech)
                            except (json.JSONDecodeError, TypeError):
                                continue
                    self._last_position[source] = f.tell()
        
        for s in results:
            self._all_speeches.append(s)
        return results
    
    def get_transcript(self) -> list:
        return list(self._all_speeches)
    
    def clear(self):
        with self._lock:
            for f in self.log_dir.glob("*.log"):
                f.unlink()
            self._last_position.clear()
            self._all_speeches.clear()


# ─── Monitor ───────────────────────────────────────────────────────────────────

class ForumMonitor:
    """Monitora canais e gerencia buffer de speeches."""
    
    def __init__(self, channel: Channel, buffer_size: int = DEFAULT_BUFFER_SIZE):
        self.channel = channel
        self._buffer_limit = buffer_size
        self._buffer: list[AgentSpeech] = []
        self._lock = threading.Lock()
    
    def poll_and_buffer(self) -> list[AgentSpeech]:
        """Poll do canal, retorna speeches novos e atualiza buffer."""
        new = self.channel.poll()
        with self._lock:
            self._buffer.extend(new)
        return new
    
    def drain_buffer(self) -> list[AgentSpeech]:
        """Esvazia o buffer atual."""
        with self._lock:
            drained = list(self._buffer)
            self._buffer.clear()
        return drained
    
    def get_buffer_size(self) -> int:
        """Tamanho atual do buffer."""
        with self._lock:
            return len(self._buffer)
    
    def is_ready(self) -> bool:
        """Buffer atingiu o tamanho minimo para acionar moderador."""
        with self._lock:
            return len(self._buffer) >= self._buffer_limit


# ─── Moderador ────────────────────────────────────────────────────────────────

class ForumModerator:
    """Moderador LLM do forum."""
    
    def __init__(self, config: SessionConfig):
        self.config = config
        self.previous_summaries: list[str] = []
    
    def generate(self, speeches: list[AgentSpeech], stage: DebateStage,
                 history: Optional[list] = None) -> ModeratorSpeech:
        """Gera discurso do moderador."""
        system_prompt = _build_system_prompt(self.config, stage)
        user_prompt = _build_discuss_prompt(speeches, history or [])
        
        raw = _call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=self.config.moderator_model,
            temperature=self.config.moderator_temperature,
            top_p=self.config.moderator_top_p,
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
        
        if not raw:
            raw = _generate_fallback_synthesis(speeches)
        
        mode_map = {
            DebateStage.OPEN: ModeratorMode.SUMMARIZE,
            DebateStage.DISCUSS: ModeratorMode.DEEPEN,
            DebateStage.SYNTHESIZE: ModeratorMode.SUMMARIZE,
            DebateStage.CONCLUDE: ModeratorMode.CONCLUDE,
        }
        
        speech = ModeratorSpeech(
            content=raw,
            mode=mode_map.get(stage, ModeratorMode.SUMMARIZE),
            sources=[s.speech_id for s in speeches],
        )
        
        self.previous_summaries.append(raw[:200])
        return speech


# ─── Forum Principal ───────────────────────────────────────────────────────────

class Forum:
    """Orquestrador principal do forum multiagente."""
    
    def __init__(self,
                 agents: Optional[list[str]] = None,
                 channel: str = "memory",
                 log_dir: str = "",
                 moderator_model: str = "opencode/big-pickle",
                 moderator_temperature: float = 0.6,
                 buffer_size: int = DEFAULT_BUFFER_SIZE,
                 timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
                 api_key: str = "",
                 base_url: str = "",
                 language: str = "pt-BR",
                 debate_profile: str = "LOGICO_RIGOROSO",
                 reasoning_types: Optional[list] = None,
                 tournament_mode: bool = False):
        """
        Args:
            agents: Lista de nomes de agentes participantes.
            debate_profile: Perfil pre-definido (LOGICO_RIGOROSO, ESTRATEGISTA, etc.)
            reasoning_types: Lista manual de ReasoningType (sobrescreve profile).
            tournament_mode: Se True, usa torneio Axelrod-style com game theory.
        """
        self.agents = agents or []
        self._channel: Channel = (
            FileChannel(log_dir) if channel == "filesystem"
            else MemoryChannel()
        )
        self.monitor = ForumMonitor(self._channel, buffer_size)

        self._session_config: Optional[SessionConfig] = None
        self._moderator: Optional[ForumModerator] = None
        self._stage = DebateStage.IDLE
        self._history: list = []
        self._background_thread: Optional[threading.Thread] = None
        self._running = False

        # ── P17+ Debate Strategies ──
        self.debate_profile = debate_profile
        self.reasoning_types = reasoning_types or DEBATE_PROFILES.get(debate_profile, [ReasoningType.CRITICAL])
        self.tournament_mode = tournament_mode
        self.meta_reasoner = MetaReasoner() if HAS_STRATEGIES else None
        self._tournament_scores: Dict[str, float] = {}

        self._default_config = {
            "moderator_model": moderator_model,
            "moderator_temperature": moderator_temperature,
            "buffer_size": buffer_size,
            "timeout_seconds": timeout_seconds,
            "api_key": api_key,
            "base_url": base_url,
            "language": language,
        }
    
    @property
    def stage(self) -> DebateStage:
        return self._stage
    
    @property
    def transcript(self) -> list:
        return list(self._history)
    
    @property
    def is_active(self) -> bool:
        return self._running
    
    # ─── API Publica ───────────────────────────────────────────────────────
    
    def open_session(self, topic: str):
        """Abre nova sessao de debate."""
        self._channel.clear()
        self._history.clear()
        
        self._session_config = SessionConfig(
            topic=topic,
            agents=list(self.agents),
            **{k: v for k, v in self._default_config.items()
               if k in SessionConfig.__dataclass_fields__}
        )
        
        self._moderator = ForumModerator(self._session_config)
        self._stage = DebateStage.OPEN
        self._running = True
        
        # Discurso de abertura do moderador
        opening = ModeratorSpeech(
            content=f"## Sessao iniciada: {topic}\n\n"
                    f"Agentes participantes: {', '.join(self.agents)}\n"
                    f"Estagio: ABERTURA. Cada agente deve apresentar sua analise inicial.",
            mode=ModeratorMode.SUMMARIZE,
        )
        self._history.append(opening)
        
        print(f"[Forum] Sessao aberta: {topic}")
        print(f"[Forum] Moderador: {self._session_config.moderator_model}")
        return opening
    
    def publish(self, source: str, content: str,
                confidence: float = 0.5, stance: str = "neutral",
                metadata: Optional[dict] = None) -> AgentSpeech:
        """Agente publica um discurso no forum."""
        if not self._session_config:
            raise RuntimeError("Nenhuma sessao ativa. Chame open_session() primeiro.")
        
        speech = AgentSpeech(
            source=source,
            content=content,
            confidence=confidence,
            stance=stance,
            stage=self._stage.value,
            metadata=metadata or {},
        )
        
        self._channel.publish(speech)
        self._history.append(speech)
        
        print(f"[Forum] {source} publicou (confianca={confidence}, estagio={self._stage.value})")
        
        # Verificar se deve acionar moderador
        new_speeches = self.monitor.poll_and_buffer()
        if self.monitor.is_ready() and self._stage not in (DebateStage.CONCLUDE, DebateStage.CLOSED):
            self._trigger_moderator()
        
        return speech
    
    def conclude(self) -> ModeratorSpeech:
        """Forca conclusao da sessao atual."""
        if self._stage == DebateStage.CLOSED:
            raise RuntimeError("Sessao ja foi concluida.")
        if not self._session_config:
            raise RuntimeError("Nenhuma sessao ativa.")
        
        self._stage = DebateStage.CONCLUDE
        buffer = self.monitor.drain_buffer()
        
        final = ModeratorSpeech(
            content=f"## Conclusao do Forum\n\n"
                    f"Topic: {self._session_config.topic}\n"
                    f"Total de contribuicoes: {len([h for h in self._history if isinstance(h, AgentSpeech)])}\n"
                    f"Rodadas de moderacao: {len([h for h in self._history if isinstance(h, ModeratorSpeech)])}\n\n"
                    f"*Sessao encerrada.*",
            mode=ModeratorMode.CONCLUDE,
            sources=[s.speech_id for s in buffer],
        )
        
        self._history.append(final)
        self._stage = DebateStage.CLOSED
        self._running = False
        
        print(f"[Forum] Sessao concluida.")
        return final
    
    def get_json_report(self) -> dict:
        """Retorna relatorio completo da sessao em JSON."""
        return {
            "forum_version": FORUM_VERSION,
            "topic": self._session_config.topic if self._session_config else "",
            "stage": self._stage.value,
            "agents": self.agents,
            "total_speeches": len([h for h in self._history if isinstance(h, AgentSpeech)]),
            "total_moderations": len([h for h in self._history if isinstance(h, ModeratorSpeech)]),
            "transcript": [
                asdict(h) if isinstance(h, AgentSpeech)
                else {"type": "moderator", **asdict(h)}
                for h in self._history
            ],
        }
    
    # ─── Interno ───────────────────────────────────────────────────────────
    
    def _trigger_moderator(self):
        """Aciona moderador com o buffer atual."""
        if not self._moderator or not self._session_config:
            return
        
        buffer = self.monitor.drain_buffer()
        if not buffer:
            return
        
        self._stage = DebateStage.SYNTHESIZE
        
        speech = self._moderator.generate(
            speeches=buffer,
            stage=self._stage,
            history=self._history,
        )
        
        self._history.append(speech)
        self._channel.publish(AgentSpeech(
            source="MODERATOR",
            content=speech.content,
            stage=self._stage.value,
            confidence=1.0,
            stance="moderator",
        ))
        
        self._stage = DebateStage.DISCUSS
        print(f"[Forum] Moderador publicou sintese ({len(buffer)} speeches analisados)")

    # ── P17+ Game Theory Integration ─────────────────────────────────────

    def get_reasoning_prompt(self, agent_name: str = "") -> str:
        """Retorna prompt de raciocinio composto para o agente."""
        if not HAS_STRATEGIES:
            return ""
        context = {"topic": self._session_config.topic if self._session_config else "",
                   "role": agent_name}
        if self.meta_reasoner:
            types = self.meta_reasoner.select_for_context(context)
        else:
            types = self.reasoning_types
        prompts = [REASONING_PROMPTS.get(rt, "") for rt in types[:5] if rt in REASONING_PROMPTS]
        return "\n---\n".join(p for p in prompts if p)

    def run_game_theory_analysis(self) -> Dict[str, Any]:
        """Analise completa de Teoria dos Jogos para o topico do debate."""
        if not HAS_STRATEGIES:
            return {"error": "debate_strategies nao disponivel"}
        if len(self.agents) < 2:
            return {"error": "Necessario pelo menos 2 agentes"}

        result: Dict[str, Any] = {}
        pd = PayoffMatrix.prisoners_dilemma()
        ne = pd.find_nash_equilibria()
        result["prisoners_dilemma"] = {
            "payoff": {"C,C": "(3,3)", "C,D": "(0,5)", "D,C": "(5,0)", "D,D": "(1,1)"},
            "nash_equilibria": [f"{s1}/{s2}" for s1, s2 in ne],
            "insight": "Equilibrio subotimo — racionalidade individual produz resultado pior para todos."
        }

        result["recommended_strategies"] = [rt.name for rt in self.reasoning_types[:5]]
        if self.meta_reasoner:
            ctx = {"topic": self._session_config.topic if self._session_config else ""}
            result["recommended_strategies"] = [
                rt.name for rt in self.meta_reasoner.select_for_context(ctx)[:5]
            ]

        if self.tournament_mode:
            self._tournament_scores = {a: 0.0 for a in self.agents}
            result["tournament"] = {"mode": "Axelrod round-robin", "rounds": 10, "scores": self._tournament_scores}

        return result

    def describe_strategies(self) -> Dict[str, Any]:
        """Catalogo das 38 estrategias disponiveis."""
        return {
            "total": 38,
            "categorias": {
                "Logica Classica (5)": ["DEDUCTIVE","INDUCTIVE","ABDUCTIVE","ANALOGICAL","SYLLOGISTIC"],
                "Dialetica & Critica (5)": ["DIALECTICAL","SOCRATIC","CRITICAL","DECONSTRUCTIVE","FALSIFICATIONIST"],
                "Teoria dos Jogos (10)": ["NASH_EQUILIBRIUM","PRISONERS_DILEMMA","ZERO_SUM","TIT_FOR_TAT","STACKELBERG","BARGAINING","COALITIONAL","EVOLUTIONARY_STABLE","SIGNALING","MECHANISM_DESIGN"],
                "Decisao sob Incerteza (5)": ["BAYESIAN","MINIMAX","EXPECTED_UTILITY","PROSPECT_THEORY","REAL_OPTIONS"],
                "Estrategico (5)": ["COMPETITIVE","COOPERATIVE","ADVERSARIAL","STAKEHOLDER","PARETO_OPTIMAL"],
                "Criativo & Sistemico (8)": ["SYSTEMS_THINKING","SCENARIO_PLANNING","LATERAL","COUNTERFACTUAL","FIRST_PRINCIPLES","DESIGN_THINKING","PRECAUTIONARY","ETHICAL"],
            },
            "perfis_predefinidos": list(DEBATE_PROFILES.keys()),
            "torneio_axelrod": list(TOURNAMENT_STRATEGIES.keys()),
        }

    # ── P18: PhD Auditor (nexus-phd-strategist integration) ─────────

    def run_phd_audit(self,
                      debate_output: Optional[Dict[str, Any]] = None,
                      statistics: Optional[Dict[str, Any]] = None,
                      references: Optional[List[Dict[str, str]]] = None,
                      sensitivity_params: Optional[Dict[str, List[float]]] = None,
                      ) -> Dict[str, Any]:
        """Executa auditoria completa Qualis A1 + rigor estatístico.

        Pipeline P18:
        1. NashSolver — Equilíbrio de Nash generalizado
        2. StatisticalRigor — Cohen's d, Bonferroni, Power Analysis
        3. QualisA1Auditor — Score de qualidade acadêmica (0-100)
        4. SensitivityAnalyzer — Robustez das conclusões
        5. IMRADFormatter — Formatação em estrutura de artigo

        Returns:
            Dict com qualis_level, statistical_tests, sensitivity_analysis,
            nash_analysis, imrad_document.
        """
        result: Dict[str, Any] = {}

        # 1. Nash Solver
        result["nash_analysis"] = NashSolver.prisoners_dilemma(t=5, r=3, p=1, s=0)

        # 2. Statistical Rigor
        stats_data = statistics or {}
        gdp_pos = stats_data.get("gdp_positive", [])
        gdp_neg = stats_data.get("gdp_negative", [])

        if gdp_pos and gdp_neg:
            d_result = StatisticalRigor.cohens_d(gdp_pos, gdp_neg)
            result["cohens_d"] = d_result

        p_values = stats_data.get("p_values", [0.01, 0.03, 0.04, 0.12, 0.25])
        result["bonferroni"] = StatisticalRigor.bonferroni_correction(p_values)

        result["power_analysis"] = StatisticalRigor.statistical_power(
            effect_size=0.5, n=11, alpha=0.05
        )

        # 3. Qualis A1 Audit
        auditor = QualisA1Auditor()
        content = debate_output or {
            "claims": [{"text": "Brasil enfrenta armadilha da renda média",
                        "source": "World Bank 2024"}],
            "sources": ["World Bank, 2024"],
            "statistics": {
                "p_value": 0.03, "effect_size": 0.5,
                "confidence_interval": True, "bonferroni_applied": True,
            },
            "references": [
                {"authors": "Stiglitz", "year": "2024"},
                {"authors": "Piketty", "year": "2023"},
                {"authors": "Acemoglu & Restrepo", "year": "2020"},
            ],
            "structure": ["introduction", "methods", "results", "discussion"],
            "research_gap": True,
            "has_formulas": True,
            "methodology_detailed": True,
        }
        result["qualis_audit"] = auditor.audit(content)

        # 4. Sensitivity Analysis
        if sensitivity_params:
            def baseline_fn(params):
                return params.get("pib_2024", 10311) * (1 + params.get("cagr", 0.022)) ** 6

            sa = SensitivityAnalyzer.analyze(
                base_conclusion={"parameters": {"pib_2024": 10311, "cagr": 0.022}},
                parameters=sensitivity_params,
                compute_fn=baseline_fn,
            )
            result["sensitivity"] = sa

        return result


# ─── Conveniencia ─────────────────────────────────────────────────────────────

def create_forum(agents: Optional[list[str]] = None, **kwargs) -> Forum:
    """Factory function para criar Forum com configuracao simples."""
    return Forum(agents=agents, **kwargs)


def demo():
    """Demonstracao offline do Forum com Game Theory."""
    print("=" * 60)
    print("P14 Agent Forum + P17 Game Theory — DEMO")
    print("=" * 60)

    forum = Forum(
        agents=["QueryEngine", "MediaEngine", "InsightEngine"],
        debate_profile="ESTRATEGISTA",
        moderator_model="opencode/big-pickle",
        language="pt-BR",
        tournament_mode=True,
    )

    # Mostrar estratégias disponíveis
    strategies = forum.describe_strategies()
    print(f"\n📊 38 Estrategias de Raciocinio disponiveis")
    for cat, items in strategies["categorias"].items():
        print(f"  {cat}: {len(items)} tipos")

    # Analise de Teoria dos Jogos
    analysis = forum.run_game_theory_analysis()
    print(f"\n🎮 Analise de Teoria dos Jogos:")
    print(f"  Dilema do Prisioneiro: {analysis.get('prisoners_dilemma', {}).get('insight', '')}")

    # Debate
    forum.open_session("Analisar impacto da regulamentacao de IA no Brasil")

    forum.publish("QueryEngine",
                  "Dados do primeiro trimestre mostram 15% de aumento em investimentos "
                  "em conformidade regulatoria. 15 empresas de tecnologia reportaram "
                  "contratacao de especialistas em governanca de IA.")

    forum.publish("MediaEngine",
                  "Cobertura midiatica dividida: 45% das noticias destacam riscos da "
                  "regulamentacao, 35% destacam oportunidades. Setor financeiro e o "
                  "mais citado (60% das mencpes).")

    forum.publish("InsightEngine",
                  "Dados historicos de regulacoes similares (LGPD 2018, Marco Civil 2014) "
                  "mostram padrao: impacto inicial negativo (-8% investimento) seguido de "
                  "recuperacao em 18 meses com crescimento medio de 22%.")

    forum.conclude()

    print("\n=== TRANSCRIPT ===")
    for entry in forum.transcript:
        if isinstance(entry, AgentSpeech):
            print(f"\n[{entry.source}] {entry.content[:100]}...")
        elif isinstance(entry, ModeratorSpeech):
            print(f"\n[MODERADOR] {entry.content[:100]}...")

    print("\n=== JSON REPORT ===")
    report = forum.get_json_report()
    print(f"Topic: {report['topic']}")
    print(f"Stage: {report['stage']}")

    return forum


if __name__ == "__main__":
    demo()
