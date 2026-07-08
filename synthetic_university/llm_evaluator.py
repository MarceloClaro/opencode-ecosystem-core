"""
LLM Evaluator — Avaliacao de teses por LLM real via OpenCode CLI, Antigravity e Ollama.

Pipeline de fallback:
  1. Antigravity Bridge (delegate analysis)
  2. OpenCode CLI (opencode run --model)
  3. Ollama CLI (ollama run, se modelo generativo disponivel)
  4. Template estatico (fallback garantido)

SPEC-935-R88 — R88 do OpenCode Ecosystem Core.
"""

import json
import logging
import os
import subprocess
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Templates de fallback multilíngue
FEEDBACK_TEMPLATES = {
    "strong": {
        "pt": "A tese apresenta uma contribuicao original e bem fundamentada. "
              "A argumentacao e robusta e as evidencias suportam claramente a hipotese. "
              "Recomendo a publicacao com pequenas revisoes.",
        "en": "The thesis presents an original and well-founded contribution. "
              "The argumentation is robust and the evidence clearly supports the hypothesis. "
              "I recommend publication with minor revisions.",
    },
    "moderate": {
        "pt": "A tese tem meritos, mas precisa de refinamentos na metodologia "
              "e na revisao de literatura. As evidencias sao promissoras, "
              "mas insuficientes para conclusoes definitivas.",
        "en": "The thesis has merits but needs refinements in methodology "
              "and literature review. The evidence is promising but insufficient "
              "for definitive conclusions.",
    },
    "weak": {
        "pt": "A tese aborda um tema relevante, mas a argumentacao precisa "
              "ser fortalecida e as evidencias sao limitadas. "
              "Sugiro uma revisao aprofundada antes de prosseguir.",
        "en": "The thesis addresses a relevant topic, but the argumentation "
              "needs strengthening and the evidence is limited. "
              "I suggest an in-depth review before proceeding.",
    },
}


class LLMEvaluator:
    """Avaliador de teses usando LLMs reais com fallback em cascata.

    Args:
        lang: Idioma dos prompts e templates ('pt' ou 'en').
        model: Modelo OpenCode CLI (ex: 'opencode/north-mini-code-free').
        cache_size: Tamanho maximo do cache LRU (0 = sem cache).
        timeout: Timeout em segundos para chamadas externas.
    """

    def __init__(
        self,
        lang: str = "pt",
        model: str = "opencode/north-mini-code-free",
        cache_size: int = 500,
        timeout: int = 30,
    ):
        self.lang = lang
        self.model = model
        self.cache_size = cache_size
        self._cache: dict = {}  # instancia-local, nao global
        self.timeout = timeout
        self.stats = {
            "antigravity_calls": 0,
            "antigravity_ok": 0,
            "opencode_calls": 0,
            "opencode_ok": 0,
            "ollama_calls": 0,
            "ollama_ok": 0,
            "template_fallbacks": 0,
            "total_calls": 0,
        }

    def generate(
        self, professor, thesis_dict: dict, endorsement: str
    ) -> Tuple[str, str, float]:
        """Gera feedback para um professor sobre uma tese.

        Returns:
            (feedback_text, source, time_taken_seconds)
            source: 'antigravity' | 'opencode' | 'ollama' | 'template'
        """
        cache_key = self._cache_key(professor, thesis_dict, endorsement)
        if cache_key in self._cache:
            logger.debug("R88 Cache hit: %s", cache_key)
            return self._cache[cache_key]

        self.stats["total_calls"] += 1
        start = time.time()
        feedback, source = self._try_all(professor, thesis_dict, endorsement)
        elapsed = time.time() - start

        result = (feedback, source, elapsed)
        if self.cache_size > 0:
            if len(self._cache) >= self.cache_size:
                # LRU simples: remove o primeiro
                self._cache.pop(next(iter(self._cache)))
            self._cache[cache_key] = result

        logger.info("R88 Feedback via %s em %.3fs", source, elapsed)
        return result

    def _try_all(
        self, professor, thesis_dict: dict, endorsement: str
    ) -> Tuple[str, str]:
        """Tenta cada fonte em ordem, retorna (feedback, source)."""
        # 1. Antigravity
        try:
            result = self._try_antigravity(professor, thesis_dict, endorsement)
            if result:
                return result, "antigravity"
        except Exception as e:
            logger.warning("R88 Antigravity falhou: %s", e)

        # 2. OpenCode CLI
        try:
            result = self._try_opencode_cli(professor, thesis_dict, endorsement)
            if result:
                return result, "opencode"
        except Exception as e:
            logger.warning("R88 OpenCode CLI falhou: %s", e)

        # 3. Ollama CLI
        try:
            result = self._try_ollama_cli(professor, thesis_dict, endorsement)
            if result:
                return result, "ollama"
        except Exception as e:
            logger.warning("R88 Ollama CLI falhou: %s", e)

        # 4. Template fallback
        self.stats["template_fallbacks"] += 1
        return self._template_feedback(professor, thesis_dict, endorsement), "template"

    def _try_antigravity(self, professor, thesis_dict, endorsement) -> Optional[str]:
        """Tenta usar o Antigravity Bridge via subprocess ou HTTP.

        O Antigravity esta disponivel como ferramenta MCP no ambiente OpenCode.
        Tentamos chama-lo via opencode run se ele estiver registrado.
        """
        self.stats["antigravity_calls"] += 1
        prompt = self._build_ag_prompt(professor, thesis_dict, endorsement)

        # Tenta via OpenCode com um modelo disponivel
        try:
            cmd = [
                "opencode", "run",
                "--model", self.model,
                "--format", "json",
                prompt,
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode == 0 and result.stdout.strip():
                # Extrai texto do JSON de eventos
                feedback = self._extract_opencode_json(result.stdout)
                if feedback and len(feedback) > 15:
                    self.stats["antigravity_ok"] += 1
                    return feedback
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug("R88 Antigravity subprocess: %s", e)

        return None

    def _try_opencode_cli(self, professor, thesis_dict, endorsement) -> Optional[str]:
        """Usa opencode run --model para gerar feedback."""
        self.stats["opencode_calls"] += 1
        prompt = self._build_prompt(professor, thesis_dict, endorsement)

        try:
            cmd = [
                "opencode", "run",
                "--model", self.model,
                prompt,
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode == 0:
                feedback = result.stdout.strip()
                # Remove cabecalhos comuns do opencode
                feedback = self._clean_opencode_output(feedback)
                if feedback and len(feedback) > 15:
                    self.stats["opencode_ok"] += 1
                    logger.info(
                        "R88 OpenCode OK (%.1fs): %s...",
                        getattr(result, 'timeout', 0),
                        feedback[:80],
                    )
                    return feedback
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug("R88 OpenCode CLI: %s", e)

        return None

    def _try_ollama_cli(self, professor, thesis_dict, endorsement) -> Optional[str]:
        """Usa ollama run para gerar feedback (se modelo generativo existir)."""
        self.stats["ollama_calls"] += 1
        prompt = self._build_prompt(professor, thesis_dict, endorsement)

        # Lista de modelos generativos para tentar
        models_to_try = ["tinyllama", "llama3.2", "phi", "gemma:2b"]
        for model in models_to_try:
            try:
                cmd = [
                    "ollama", "run",
                    model,
                    prompt,
                ]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=min(self.timeout, 60),
                )
                if result.returncode == 0:
                    feedback = result.stdout.strip()
                    if feedback and len(feedback) > 10:
                        self.stats["ollama_ok"] += 1
                        return feedback
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                logger.debug("R88 Ollama %s: %s", model, e)

        return None

    def _build_prompt(
        self, professor, thesis_dict: dict, endorsement: str
    ) -> str:
        """Constroi prompt em portugues ou ingles para o LLM."""
        is_pt = self.lang == "pt"

        if is_pt:
            prompt = (
                f"Voce e {professor.nome}, professor(a) de {professor.faculty_id} "
                f"com especializacao em {', '.join(professor.specialties[:3])}. "
                f"Seu indice h e {professor.h_index}.\n\n"
                f"Analise a seguinte tese:\n"
                f"Titulo: {thesis_dict.get('title', 'Sem titulo')}\n"
                f"Hipotese: {thesis_dict.get('hypothesis', 'Sem hipotese')}\n"
                f"Score composto: {thesis_dict.get('composite_score', 0):.2f}\n\n"
                f"Seu endosso previsto: {endorsement.upper()}\n\n"
                f"Forneca feedback academico critico e construtivo em 1-2 paragrafos. "
                f"Seja especifico sobre pontos fortes e fracos. "
                f"Responda APENAS com o feedback, sem introducao."
            )
        else:
            prompt = (
                f"You are {professor.nome}, a professor in {professor.faculty_id} "
                f"specializing in {', '.join(professor.specialties[:3])}. "
                f"Your h-index is {professor.h_index}.\n\n"
                f"Analyze the following thesis:\n"
                f"Title: {thesis_dict.get('title', 'No title')}\n"
                f"Hypothesis: {thesis_dict.get('hypothesis', 'No hypothesis')}\n"
                f"Composite score: {thesis_dict.get('composite_score', 0):.2f}\n\n"
                f"Your predicted endorsement: {endorsement.upper()}\n\n"
                f"Provide critical and constructive academic feedback in 1-2 paragraphs. "
                f"Be specific about strengths and weaknesses. "
                f"Reply ONLY with the feedback, no introduction."
            )
        return prompt

    def _build_ag_prompt(
        self, professor, thesis_dict: dict, endorsement: str
    ) -> str:
        """Prompt especifico para o Antigravity Bridge."""
        is_pt = self.lang == "pt"
        if is_pt:
            return (
                f"[ANALISE ACADEMICA]\n"
                f"Professor: {professor.nome} ({professor.faculty_id})\n"
                f"Especialidades: {', '.join(professor.specialties[:3])}\n"
                f"Tese: {thesis_dict.get('title', 'Sem titulo')}\n"
                f"Endosso: {endorsement}\n\n"
                f"Forneca feedback academico detalhado em 2-3 paragrafos. "
                f"Avalie: originalidade, metodologia, evidencias, contribuicao."
            )
        else:
            return (
                f"[ACADEMIC ANALYSIS]\n"
                f"Professor: {professor.nome} ({professor.faculty_id})\n"
                f"Specialties: {', '.join(professor.specialties[:3])}\n"
                f"Thesis: {thesis_dict.get('title', 'No title')}\n"
                f"Endorsement: {endorsement}\n\n"
                f"Provide detailed academic feedback in 2-3 paragraphs. "
                f"Evaluate: originality, methodology, evidence, contribution."
            )

    def _template_feedback(
        self, professor, thesis_dict: dict, endorsement: str
    ) -> str:
        """Retorna feedback template no idioma configurado."""
        template = FEEDBACK_TEMPLATES.get(
            endorsement, FEEDBACK_TEMPLATES["moderate"]
        )
        feedback = template.get(self.lang, template["en"])
        return (
            f"Prof. {professor.nome} ({professor.faculty_id}): {feedback}"
        )

    def _cache_key(self, professor, thesis_dict, endorsement) -> str:
        pid = getattr(professor, "professor_id", str(id(professor)))
        tid = thesis_dict.get("thesis_id", thesis_dict.get("title", "unknown"))
        return f"{pid}:{tid}:{endorsement}"

    @staticmethod
    def _extract_opencode_json(stdout: str) -> Optional[str]:
        """Extrai texto do formato JSON de eventos do OpenCode."""
        texts = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "text":
                    texts.append(data.get("content", ""))
            except json.JSONDecodeError:
                continue
        full = " ".join(texts).strip()
        return full if len(full) > 15 else None

    @staticmethod
    def _clean_opencode_output(output: str) -> str:
        """Remove cabecalhos gerados pelo opencode CLI."""
        lines = output.splitlines()
        # Remove linhas de arte ASCII / logo
        cleaned = [
            l for l in lines
            if not any(skip in l for skip in [
                "▄", "█", "▀", "opencode", "━━━", "───",
                "model:", "provider:", "time:", "tokens:",
                "Tools used", "Assistant",
            ])
        ]
        return " ".join(c.strip() for c in cleaned if c.strip()).strip()

    def get_stats(self) -> dict:
        """Retorna estatisticas de uso."""
        return {**self.stats}

    def clear_cache(self):
        """Limpa o cache de feedbacks."""
        self._cache.clear()
