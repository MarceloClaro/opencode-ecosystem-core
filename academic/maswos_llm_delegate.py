# -*- coding: utf-8 -*-
"""
MASWOS LLM Delegate — Delegação real dos 16 agentes MASWOS via OpenCode
======================================================================
Conecta o MaswosPipeline ao OpenCode CLI para execução real dos 16 estágios,
substituindo o dry-run por conteúdo gerado por LLM.

Modelos disponíveis (free): mimo-v2.5-free, nemotron-3-ultra-free, etc.
Modelos premium: claude-sonnet-4-5, gpt-5.5, gemini-3.5-flash, etc.

Anti-overclaim: gera conteúdo auxiliar, NÃO constitui validação científica.
"""

import json
import logging
import subprocess
import sys
from typing import Optional

logger = logging.getLogger("academic.maswos_llm_delegate")

# Modelo padrão (free tier para demo; trocar para premium em produção)
DEFAULT_MODEL = "opencode/mimo-v2.5-free"


def _call_opencode(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 800) -> str:
    """Chama OpenCode CLI para gerar conteúdo."""
    try:
        result = subprocess.run(
            ["opencode", "run", prompt, "-m", model],
            capture_output=True, text=True, timeout=120,
            env={**dict(__import__('os').environ), "OPENCODE_PURE": "1"},
        )
        output = result.stdout.strip()
        # Remove ANSI codes
        import re
        output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        # Remove lines starting with > (build info)
        lines = [l for l in output.split('\n') if not l.strip().startswith('>')]
        return '\n'.join(lines).strip()
    except subprocess.TimeoutExpired:
        logger.error("OpenCode timeout for model %s", model)
        return "[TIMEOUT: LLM não respondeu em 120s]"
    except Exception as e:
        logger.error("OpenCode call failed: %s", e)
        return f"[ERRO: LLM delegate falhou — {e}]"


# Prompts especializados por agente MASWOS
AGENT_PROMPTS = {
    "01_agente_diagnostico_escopo": (
        "You are a scientific research scope diagnostician. "
        "Given the topic below, produce a structured diagnosis with: "
        "(1) Research problem statement, (2) Scope delimitation, "
        "(3) Key variables, (4) Target population of studies, "
        "(5) Preliminary research questions. "
        "Write in academic English, 300-500 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "02_agente_busca_curadoria": (
        "You are a scientific literature search specialist. "
        "Given the topic and context, produce a detailed search strategy with: "
        "(1) Boolean query strings for each database (OpenAlex, PubMed, Scopus, WoS), "
        "(2) Inclusion/exclusion criteria, (3) Date range justification, "
        "(4) Language restrictions, (5) Expected yield estimate. "
        "Write in academic English, 300-500 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "03_agente_evidencias_citacoes": (
        "You are a citation and evidence analyst. "
        "Given the topic and context, produce: "
        "(1) Key seminal works to cite, (2) Evidence hierarchy assessment, "
        "(3) Citation density targets per section, (4) DOI verification strategy, "
        "(5) Reference management recommendations. "
        "Write in academic English, 300-500 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "04_agente_estrutura_argumentativa": (
        "You are an academic argumentation architect. "
        "Given the topic and context, produce a detailed argumentative structure with: "
        "(1) Thesis statement, (2) Supporting arguments (3-5), "
        "(3) Counter-arguments and rebuttals, (4) Logical flow diagram, "
        "(5) Section-by-section argument mapping. "
        "Write in academic English, 300-500 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "05_agente_revisao_literatura_teoria": (
        "You are a theoretical literature review specialist. "
        "Given the topic and context, produce: "
        "(1) Theoretical framework identification, (2) Key theories and models, "
        "(3) Evolution of the field over time, (4) Gaps in existing reviews, "
        "(5) Novel synthesis approach. "
        "Write in academic English, 300-500 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "06_agente_metodologia_reprodutibilidade": (
        "You are a research methodology and reproducibility expert. "
        "Given the topic and context, produce a detailed methodology section with: "
        "(1) Study design (systematic review/PRISMA 2020), "
        "(2) Search protocol, (3) Data extraction form, "
        "(4) Quality assessment tool (RoB 2 / NOS), "
        "(5) Synthesis strategy (narrative/meta-analysis), "
        "(6) Reproducibility checklist. "
        "Write in academic English, 400-600 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "07_agente_estatistica_analise": (
        "You are a statistical analysis expert. "
        "Given the topic and context, produce: "
        "(1) Statistical methods appropriate for the study type, "
        "(2) Effect size measures, (3) Heterogeneity assessment (I², Q test), "
        "(4) Publication bias tests (funnel plot, Egger's test), "
        "(5) Sensitivity analysis plan. "
        "Write in academic English, 300-500 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "08_agente_visualizacao_evidencia_grafica": (
        "You are a scientific visualization expert. "
        "Given the topic and context, produce: "
        "(1) PRISMA flow diagram specification, (2) Forest plot requirements, "
        "(3) Funnel plot specification, (4) Table specs (characteristics of studies), "
        "(5) Figure legends. "
        "Write in academic English, 300-400 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "09_agente_resultados": (
        "You are a scientific results section writer. "
        "Given the topic, context, and methodology, produce a complete Results section with: "
        "(1) Study selection results (PRISMA flow), "
        "(2) Study characteristics table description, "
        "(3) Quality assessment results, "
        "(4) Synthesis of findings by outcome, "
        "(5) Subgroup analysis if applicable. "
        "Write in academic English, 500-800 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "10_agente_discussao_contribuicao": (
        "You are a scientific discussion and contribution analyst. "
        "Given the topic, context, and results, produce a Discussion section with: "
        "(1) Summary of main findings, (2) Comparison with existing literature, "
        "(3) Implications for theory and practice, "
        "(4) Limitations and threats to validity, "
        "(5) Novel contributions to the field. "
        "Write in academic English, 500-800 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "11_agente_conclusao_coerencia_final": (
        "You are a scientific conclusion writer. "
        "Given the topic, context, and full manuscript, produce a Conclusion section with: "
        "(1) Restatement of objective, (2) Key findings summary, "
        "(3) Implications, (4) Future research directions, "
        "(5) Final closing statement. "
        "Write in academic English, 300-500 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "12_agente_auditoria_bibliografica_abnt": (
        "You are a bibliographic standards auditor (ABNT NBR 6023/10520, Vancouver, APA 7). "
        "Given the topic and context, produce: "
        "(1) Citation format compliance check, (2) Reference list format verification, "
        "(3) DOI/URL completeness, (4) Author name standardization, "
        "(5) Year accuracy check. "
        "Write in academic English, 200-400 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "13_agente_qa_qualis_a1": (
        "You are a Qualis A1 quality assurance reviewer. "
        "Given the manuscript context, produce a quality assessment with: "
        "(1) Score per criterion (0-10) for: rigor, citation density, ABNT compliance, "
        "originality, methodology, statistical analysis, coherence, visual quality, "
        "internationalization, self-containment. "
        "(2) Overall score (0-100), (3) Specific improvement recommendations per criterion, "
        "(4) Pass/fail determination (≥95 = Qualis A1). "
        "Write in academic English, 400-600 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "14_agente_consistencia_interna": (
        "You are an internal consistency verifier. "
        "Given the manuscript context, produce: "
        "(1) Cross-reference verification (intro↔conclusion alignment), "
        "(2) Methodology↔results consistency, (3) Citation↔reference matching, "
        "(4) Figure/table references in text, (5) Terminology consistency. "
        "Write in academic English, 200-400 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "15_agente_resumo_abstract_palavras_chave": (
        "You are an abstract and keywords specialist. "
        "Given the manuscript context, produce: "
        "(1) Structured abstract (Background, Methods, Results, Conclusion) 250-300 words, "
        "(2) 4-6 keywords following MeSH/DeCS guidelines, "
        "(3) Portuguese resumo (if applicable), (4) Title optimization suggestions. "
        "Write in academic English, 300-400 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
    "16_agente_integracao_editorial_docx": (
        "You are an editorial integration specialist. "
        "Given the manuscript context, produce: "
        "(1) DOCX formatting checklist, (2) Figure placement verification, "
        "(3) Table formatting compliance, (4) Header/footer configuration, "
        "(5) Metadata (title, authors, affiliations, correspondence). "
        "Write in academic English, 200-300 words.\n\nTOPIC: {topic}\nCONTEXT: {context}"
    ),
}


def create_maswos_delegate(topic: str, model: str = DEFAULT_MODEL):
    """Cria uma delegate_fn para o MaswosPipeline usando OpenCode."""

    def delegate_fn(agent_id: str, capability: str, description: str) -> str:
        prompt_template = AGENT_PROMPTS.get(agent_id)
        if not prompt_template:
            prompt_template = (
                f"You are a scientific research expert ({capability}). "
                f"Given the topic and context below, produce a comprehensive "
                f"academic section of 300-500 words.\n\n"
                f"TOPIC: {topic}\nCONTEXT: {description}"
            )

        prompt = prompt_template.format(topic=topic, context=description[:1500])
        logger.info("Delegando a %s (%s) via %s", agent_id, capability, model)

        output = _call_opencode(prompt, model=model, max_tokens=800)
        logger.info("Resposta de %s: %d chars", agent_id, len(output))
        return output

    return delegate_fn
