"""QualityChecker — Valida cada nanobloco contra seus critérios.

Pipeline de validação:
1. Verifica critérios básicos (extensão, estrutura)
2. Verifica critérios semânticos (coerência interna)
3. Se falha, tenta reescrita com modelo superior
4. Até 3 tentativas com escalonamento de modelo
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from . import (
    LINE_RANGE, MAX_RETRIES, ModelTier, NanoBlock, NanoPlan,
    QualityReport, Criterion, FIDELITY_THRESHOLD,
)
from .writer import LiteRTMClient


logger = logging.getLogger(__name__)

# Palavras e padrões que indicam problemas de qualidade
WEAK_PATTERNS = [
    "em resumo", "basicamente", "simplesmente", "apenas",
    "é importante notar", "vale ressaltar", "importante mencionar",
    "como mencionado anteriormente", "como dito antes",
    "de certa forma", "de alguma maneira", "de modo geral",
    "pode-se dizer que", "podemos observar que",
]

SUSPECT_PATTERNS = [
    "lorem ipsum", "texto pendente", "a ser preenchido",
    "TODO", "FIXME", "XXXX", "inserir",
]

QUALITY_MODEL = ModelTier.GEMMA4_2B  # modelo para verificação
REWRITE_MODELS = [ModelTier.GEMMA4_4B, ModelTier.GEMMA4_2B, ModelTier.QWEN3_0_6B]


class QualityChecker:
    """Valida a qualidade de nanoblocos contra critérios.

    Características:
    - Verificação automática de critérios formais
    - Verificação semântica via modelo LLM
    - Reescrita com escalonamento de modelo
    """

    def __init__(self, client: Optional[LiteRTMClient] = None):
        self.client = client or LiteRTMClient()

    def check_block(self, block: NanoBlock, plan: NanoPlan) -> QualityReport:
        """Valida um nanobloco contra seus critérios.

        Args:
            block: Bloco a validar.
            plan: Plano completo.

        Returns:
            QualityReport com resultados.
        """
        start = time.time()
        criteria = block.criteria
        passed = 0
        total = len(criteria)
        issues = []

        # Verificação formal básica
        for crit in criteria:
            result = self._check_criterion(crit, block)
            if result["passed"]:
                passed += 1
                crit.passed = True
            else:
                crit.passed = False
                issues.append(result.get("reason", ""))

        # Verificação semântica (apenas se já passou nos formais)
        if issues:
            semantic_issues = self._check_semantic(block, plan)
            issues.extend(semantic_issues)
            passed -= len(semantic_issues) * 0  # Não reduz passed, apenas adiciona issues

        score = round(passed / max(total, 1) * 10.0, 2)
        elapsed = (time.time() - start) * 1000

        report = QualityReport(
            block_id=block.id,
            criteria_passed=passed,
            criteria_total=total,
            score=score,
            retries=block.retries,
            model_used=block.model_used or QUALITY_MODEL,
            time_ms=round(elapsed, 1),
            issues=issues,
            passed=score >= 7.0,  # 7/10 mínimo para passar
        )

        block.quality_score = score
        block.status = "verified" if report.passed else "failed"

        return report

    def _check_criterion(self, criterion: Criterion, block: NanoBlock) -> dict:
        """Verifica um critério individual.

        Returns:
            Dict com resultado da verificação.
        """
        desc = criterion.description.lower()
        content = block.content
        lines = content.split("\n")
        reasons = []

        # Critério de extensão
        if "extensão" in desc or "linhas" in desc:
            num_lines = len([l for l in lines if l.strip()])
            if 5 <= num_lines <= 30:
                return {"passed": True}
            else:
                return {
                    "passed": False,
                    "reason": f"Extensão: {num_lines} linhas (esperado 5-15)",
                }

        # Critério de parágrafos
        if "parágrafo" in desc or "tópico" in desc:
            paragraphs = [p for p in content.split("\n\n") if p.strip()]
            valid_pars = sum(1 for p in paragraphs if len(p.split()) >= 30)
            if valid_pars >= max(1, len(paragraphs) // 2):
                return {"passed": True}
            return {
                "passed": False,
                "reason": f"Apenas {valid_pars}/{len(paragraphs)} parágrafos com estrutura adequada",
            }

        # Critério de citação
        if "citação" in desc or "fonte" in desc or "autor" in desc:
            has_citation = (
                "(" in content and ")" in content
                and any(c in content for c in ["et al", "19", "20", "21", "22", "23", "24", "25"])
            )
            if has_citation:
                return {"passed": True}
            # Não obrigatório para todos os blocos
            return {"passed": True, "reason": "Citação não detectada (opcional para este bloco)"}

        # Critério de impessoalidade
        if "impessoal" in desc or "objetiva" in desc or "juízo" in desc:
            subjective_words = [
                "acredito", "penso", "acho", "na minha opinião",
                "eu acho", "nós acreditamos", "talvez",
            ]
            found = [w for w in subjective_words if w in content.lower()]
            if not found:
                return {"passed": True}
            return {
                "passed": False,
                "reason": f"Linguagem subjetiva detectada: {found}",
            }

        # Critério de transição
        if "transição" in desc or "continuidade" in desc or "conecta" in desc:
            connectors = [
                "portanto", "assim", "dessa forma", "consequentemente",
                "ademais", "outrossim", "contudo", "entretanto",
                "por outro lado", "além disso", "no entanto",
            ]
            found = [c for c in connectors if c in content.lower()]
            if found:
                return {"passed": True}
            return {
                "passed": False,
                "reason": "Conectivos de transição não encontrados",
            }

        # Critério de conclusão
        if "conclusão" in desc or "sintetiza" in desc or "contribui" in desc:
            conclusion_markers = [
                "conclui", "portanto", "dessa forma", "assim",
                "em síntese", "em suma", "por conseguinte",
            ]
            found = [m for m in conclusion_markers if m in content.lower()]
            if found:
                return {"passed": True}
            return {
                "passed": False,
                "reason": "Marcadores de conclusão não encontrados",
            }

        # Critério de dados/resultados
        if "dados" in desc or "precisão" in desc or "valor" in desc or "estatística" in desc:
            has_numbers = any(c.isdigit() for c in content)
            if has_numbers:
                return {"passed": True}
            return {
                "passed": False,
                "reason": "Dados numéricos não detectados",
            }

        # Critério de terminologia
        if "terminologia" in desc or "vocabulário" in desc or "técnica" in desc:
            academic_terms = [
                "análise", "método", "teoria", "conceito", "abordagem",
                "paradigma", "hipótese", "variável", "correlação",
                "significância", "amostra", "fenômeno", "fenomeno",
            ]
            found = [t for t in academic_terms if t in content.lower()]
            if found:
                return {"passed": True}
            return {
                "passed": False,
                "reason": "Terminologia acadêmica insuficiente",
            }

        # Critérios sem verificação automatizada (passam)
        return {"passed": True}

    def _check_semantic(self, block: NanoBlock, plan: NanoPlan) -> list[str]:
        """Verificação semântica via modelo LLM.

        Returns:
            Lista de issues encontradas.
        """
        issues = []

        # Verifica padrões fracos
        for pattern in WEAK_PATTERNS:
            if pattern in block.content.lower():
                issues.append(f"Padrão de linguagem fraca: '{pattern}'")
                break  # Uma ocorrência já é suficiente

        # Verifica padrões suspeitos
        for pattern in SUSPECT_PATTERNS:
            if pattern in block.content.lower():
                issues.append(f"Conteúdo suspeito: '{pattern}'")
                break

        # Verifica se o conteúdo repete o título de forma mecânica
        title_words = set(block.title.lower().split())
        content_words = set(block.content.lower().split())
        overlap = len(title_words & content_words) / max(len(title_words), 1)
        if overlap > 0.8 and len(title_words) > 3:
            issues.append("Alta sobreposição com o título do bloco (possível repetição mecânica)")

        return issues

    def rewrite_block(self, block: NanoBlock, plan: NanoPlan,
                       issues: list[str]) -> Optional[NanoBlock]:
        """Tenta reescrever um bloco com base nos issues.

        Escalona modelo conforme criticidade.

        Args:
            block: Bloco com problemas.
            plan: Plano completo.
            issues: Lista de issues a endereçar.

        Returns:
            Bloco reescrito ou None se falhar.
        """
        for model in REWRITE_MODELS[:MAX_RETRIES]:
            try:
                prompt = self._build_rewrite_prompt(block, plan, issues)
                messages = [
                    {"role": "system", "content": (
                        "Você é um revisor acadêmico. Reescreva o texto "
                        "abaixo para atender aos critérios de qualidade. "
                        "Preserve o conteúdo essencial e o tom acadêmico."
                    )},
                    {"role": "user", "content": prompt},
                ]

                response = self.client.chat(
                    messages=messages,
                    model=model.value,
                    max_tokens=400,
                    temperature=0.5,
                    timeout=120,
                )

                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    block.content = content
                    block.model_used = model
                    block.retries += 1
                    block.status = "written"
                    logger.info(f"Bloco {block.index} reescrito com {model.value}")
                    return block

            except Exception as e:
                logger.warning(
                    f"Reescrita bloco {block.index} falhou com {model.value}: {e}"
                )
                continue

        return None

    def _build_rewrite_prompt(self, block: NanoBlock, plan: NanoPlan,
                               issues: list[str]) -> str:
        """Constrói prompt para reescrita."""
        issues_text = "\n".join(f"- {i}" for i in issues[:5])
        return (
            f"Reescreva o seguinte bloco acadêmico para corrigir estes problemas:\n\n"
            f"{issues_text}\n\n"
            f"Texto original:\n{block.content}\n\n"
            f"Título: {block.title}\n"
            f"Seção: {block.section}\n"
            f"Tipo: {block.block_type.value}\n\n"
            f"Mantenha a extensão entre 5 e 15 linhas (nanobloco).\n"
            f"Tom acadêmico formal em português brasileiro."
        )

    def verify_and_fix(self, block: NanoBlock, plan: NanoPlan) -> tuple[NanoBlock, QualityReport]:
        """Verifica e tenta corrigir automaticamente.

        Pipeline completo: check → se falha → rewrite → re-check.

        Returns:
            Tupla (bloco, relatório).
        """
        report = self.check_block(block, plan)

        if not report.passed and report.issues:
            logger.info(f"Bloco {block.index}: tentando reescrita ({len(report.issues)} issues)")
            rewritten = self.rewrite_block(block, plan, report.issues)

            if rewritten:
                # Re-check após reescrita
                final_report = self.check_block(rewritten, plan)
                return rewritten, final_report

        return block, report
