"""NanoWriter Pool — Pool de agentes escritores LiteRT-LM.

Gerencia:
- Roteamento inteligente: cada tipo de bloco → modelo ideal
- Pool paralelo: até N workers simultâneos
- Fallback: se modelo superior falha, escala para modelo mais leve
- Retry: até 3 tentativas com backoff exponencial
"""

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Callable

from . import (
    MODEL_TIER_BY_BLOCK_TYPE, TIMEOUT_BY_BLOCK_TYPE,
    ModelTier, NanoBlock, NanoPlan,
    MAX_RETRIES, PARALLEL_WORKERS_DEFAULT,
)
from .context_window import ContextWindowManager


logger = logging.getLogger(__name__)


class LiteRTMClient:
    """Cliente mínimo para API OpenAI-compatível do LiteRT-LM.

    Implementa chamada síncrona com timeout.
    """

    def __init__(self, base_url: str = "http://localhost:9379/v1",
                 api_key: str = "not-needed"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = None  # será lazy-init

    def _ensure_session(self):
        """Garante que a sessão HTTP existe."""
        import requests
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })

    def chat(self, messages: list[dict], model: str,
             max_tokens: int = 400, temperature: float = 0.7,
             timeout: int = 120) -> dict:
        """Chamada síncrona ao modelo.

        Args:
            messages: Lista de mensagens no formato chat.
            model: ID do modelo.
            max_tokens: Máximo de tokens na resposta.
            temperature: Temperatura de amostragem.
            timeout: Timeout em segundos.

        Returns:
            Dict com a resposta.
        """
        self._ensure_session()

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        resp = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def is_available(self) -> bool:
        """Verifica se o servidor está respondendo."""
        import requests
        try:
            resp = requests.get(f"{self.base_url.replace('/v1', '')}/health",
                                timeout=5)
            return resp.status_code == 200
        except Exception:
            try:
                resp = requests.get(f"{self.base_url}/models", timeout=5)
                return resp.status_code == 200
            except Exception:
                return False


class PoolConfig:
    """Configuração do pool de escritores."""
    def __init__(self, max_workers: int = PARALLEL_WORKERS_DEFAULT,
                 max_retries: int = MAX_RETRIES,
                 timeout_per_block: int = 120,
                 temperature: float = 0.7,
                 fallback_enabled: bool = True,
                 dry_run: bool = False):
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.timeout_per_block = timeout_per_block
        self.temperature = temperature
        self.fallback_enabled = fallback_enabled
        self.dry_run = dry_run


class NanoWriterPool:
    """Pool de agentes escritores com roteamento inteligente.

    Características:
    - Roteia bloco para modelo ideal baseado no tipo
    - Executa em paralelo via ThreadPoolExecutor
    - Fallback automático para modelo mais leve
    - Retry com backoff exponencial
    """

    MODEL_FALLBACK_CHAIN = {
        ModelTier.GEMMA4_4B: [ModelTier.GEMMA4_2B, ModelTier.QWEN3_0_6B],
        ModelTier.GEMMA4_2B: [ModelTier.QWEN3_0_6B],
        ModelTier.QWEN3_0_6B: [],
    }

    def __init__(self, client: Optional[LiteRTMClient] = None,
                 config: Optional[PoolConfig] = None):
        self.client = client or LiteRTMClient()
        self.config = config or PoolConfig()
        self.context_manager = ContextWindowManager()
        self.results: dict[str, dict] = {}
        self._stats = {
            "total_calls": 0,
            "successful": 0,
            "failed": 0,
            "fallbacks_used": 0,
            "total_time_ms": 0,
        }

    def _select_model(self, block: NanoBlock) -> ModelTier:
        """Seleciona o modelo ideal baseado no tipo do bloco."""
        return MODEL_TIER_BY_BLOCK_TYPE.get(
            block.block_type, ModelTier.QWEN3_0_6B
        )

    def _build_messages(self, block: NanoBlock, plan: NanoPlan) -> list[dict]:
        """Constrói as mensagens para o modelo."""
        context = self.context_manager.build_context(block, plan, mode="write")

        system_prompt = (
            "Você é um escritor acadêmico especializado em português brasileiro. "
            "Produza texto formal, preciso e coeso, adequado para publicação "
            "acadêmica Qualis A1. Siga exatamente os critérios de qualidade "
            "fornecidos e respeite a extensão solicitada."
        )

        user_prompt = (
            f"Escreva o bloco {block.index + 1}/{plan.total_blocks} do manuscrito "
            f"\"{plan.title}\".\n\n"
            f"Seção: {block.section}\n"
            f"Título do bloco: {block.title}\n"
            f"Tipo: {block.block_type.value}\n\n"
            f"Contexto de vizinhança:\n"
        )

        if context["neighbors"].get("previous"):
            prev = context["neighbors"]["previous"]
            user_prompt += (
                f"Bloco anterior ({prev['index'] + 1}): {prev['title']}\n"
                f"Conteúdo anterior (início): {prev['content_snippet'][:200] if prev['content_snippet'] else '[a ser escrito]'}\n\n"
            )

        if context["neighbors"].get("next"):
            nxt = context["neighbors"]["next"]
            user_prompt += (
                f"Próximo bloco ({nxt['index'] + 1}): {nxt['title']}\n\n"
            )

        user_prompt += (
            f"Critérios de qualidade:\n"
            + "\n".join(f"- {c.description} [peso {c.weight}/5]"
                       for c in block.criteria) +
            f"\n\nExtensão: entre 5 e 15 linhas (nanobloco acadêmico).\n"
            f"Tom: acadêmico formal em português brasileiro."
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _extract_content(self, response: dict) -> str:
        """Extrai o texto da resposta da API."""
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return ""

    def write_block(self, block: NanoBlock, plan: NanoPlan) -> NanoBlock:
        """Escreve um nanobloco.

        Tenta com o modelo ideal, fallback em caso de falha.

        Args:
            block: O nanobloco a escrever.
            plan: Plano completo.

        Returns:
            NanoBlock com conteúdo preenchido.
        """
        if self.config.dry_run:
            block.content = (
                f"[DRY RUN - Simulated content for block {block.index}: {block.title}]\n"
                + "\n".join(f"Parágrafo simulado {i+1} para atingir ~100 linhas."
                          for i in range(25))
            )
            block.actual_tokens = len(block.content) // 4
            block.status = "written"
            block.model_used = self._select_model(block)
            block.quality_score = 8.0  # score médio para dry run
            return block

        model = self._select_model(block)
        messages = self._build_messages(block, plan)
        timeout = TIMEOUT_BY_BLOCK_TYPE.get(block.block_type, 60)

        last_error = ""
        attempted_models = []

        for attempt in range(self.config.max_retries):
            try:
                self._stats["total_calls"] += 1

                response = self.client.chat(
                    messages=messages,
                    model=model.value,
                    max_tokens=400,
                    temperature=self.config.temperature,
                    timeout=timeout,
                )

                content = self._extract_content(response)
                if not content:
                    raise ValueError("Resposta vazia do modelo")

                block.content = content
                block.actual_tokens = len(content) // 4
                block.status = "written"
                block.model_used = model
                block.retries = attempt
                self._stats["successful"] += 1

                logger.info(
                    f"Bloco {block.index} escrito com {model.value} "
                    f"(tentativa {attempt + 1})"
                )
                return block

            except Exception as e:
                last_error = str(e)
                attempted_models.append(model.value)
                self._stats["failed"] += 1

                logger.warning(
                    f"Falha bloco {block.index} com {model.value}: {e}"
                )

                # Tenta fallback
                if self.config.fallback_enabled:
                    fallback_chain = self.MODEL_FALLBACK_CHAIN.get(model, [])
                    if fallback_chain:
                        model = fallback_chain[0]
                        self._stats["fallbacks_used"] += 1
                        logger.info(
                            f"Fallback bloco {block.index} para {model.value}"
                        )
                        continue

                # Backoff exponencial antes de retentar
                if attempt < self.config.max_retries - 1:
                    wait = 2 ** attempt
                    logger.info(f"Aguardando {wait}s antes de retentar...")
                    time.sleep(wait)

        # Se chegou aqui, todas as tentativas falharam
        block.status = "failed"
        block.error = last_error[:500]
        logger.error(
            f"Bloco {block.index} falhou após {self.config.max_retries} tentativas: "
            f"{last_error}"
        )
        return block

    def write_blocks_batch(self, blocks: list[NanoBlock], plan: NanoPlan,
                            max_workers: Optional[int] = None) -> list[NanoBlock]:
        """Escreve múltiplos blocos em paralelo.

        Args:
            blocks: Lista de blocos a escrever.
            plan: Plano completo.
            max_workers: Workers simultâneos (default: config).

        Returns:
            Lista de blocos escritos.
        """
        workers = max_workers or self.config.max_workers
        results: list[NanoBlock] = []
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self.write_block, block, plan): block.index
                for block in blocks
            }

            for future in as_completed(futures):
                block_idx = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.results[result.id] = {
                        "status": result.status,
                        "tokens": result.actual_tokens,
                        "model": result.model_used.value if result.model_used else None,
                    }
                except Exception as e:
                    # Recupera o bloco original
                    original = next(b for b in blocks if b.index == block_idx)
                    original.status = "failed"
                    original.error = str(e)[:500]
                    results.append(original)
                    logger.error(f"Bloco {block_idx}: exceção no pool: {e}")

        # Ordena por índice
        results.sort(key=lambda b: b.index)
        elapsed = time.time() - start_time
        self._stats["total_time_ms"] = int(elapsed * 1000)

        return results

    def get_stats(self) -> dict:
        """Retorna estatísticas do pool."""
        return dict(self._stats)

    def reset_stats(self):
        """Reseta estatísticas."""
        self._stats = {
            "total_calls": 0,
            "successful": 0,
            "failed": 0,
            "fallbacks_used": 0,
            "total_time_ms": 0,
        }
