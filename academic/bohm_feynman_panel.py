# -*- coding: utf-8 -*-
"""Painel determinístico de 13 revisores, incluindo personas Bohm/Feynman.

Não é impersonação, não é parecer humano e não produz respostas. As personas
são lentes de revisão inspiradas em obras públicas; não falam em nome das
pessoas reais nem substituem revisão por pares.
"""
from __future__ import annotations

from typing import Any

REVIEWERS_13 = [
    {
        "id": "bohm",
        "name": "David Bohm (persona de revisão)",
        "role": "totalidade, diálogo e suspensão de suposições",
        "question": "O texto trata o todo e as partes sem apagar nenhum dos dois?",
        "limit": "Persona inspirada na obra pública; não é o Bohm histórico e não endossa o texto.",
    },
    {
        "id": "feynman",
        "name": "Richard Feynman (persona de revisão)",
        "role": "clareza, estimativa e limite do que se sabe",
        "question": "A explicação sobrevive a uma estimativa de ordem de grandeza e a um contraexemplo simples?",
        "limit": "Persona inspirada na obra pública; não é o Feynman histórico e não endossa o texto.",
    },
    {
        "id": "methodologist",
        "name": "Metodólogo",
        "role": "desenho, unidade de análise e inferência",
        "question": "O desenho distingue demonstração, replicação e generalização?",
        "limit": "Revisão local baseada em regras; não é parecer humano.",
    },
    {
        "id": "statistician",
        "name": "Estatístico",
        "role": "amostra, incerteza, multiplicidade e dados faltantes",
        "question": "A incerteza foi calculada e o tamanho de amostra sustenta a conclusão?",
        "limit": "Não recalcula números inventados; exige dados.",
    },
    {
        "id": "quantum-experimentalist",
        "name": "Experimentalista quântico",
        "role": "circuito, calibração, leitura e ruído",
        "question": "O resultado tem task ID, backend, data e limite de fidelidade?",
        "limit": "Não executa hardware; audita o que foi registrado.",
    },
    {
        "id": "quantum-theorist",
        "name": "Teórico de informação quântica",
        "role": "formalização, interpretação e complexidade",
        "question": "A afirmação teórica está separada da implementação e do hardware?",
        "limit": "Não promove interpretação a resultado.",
    },
    {
        "id": "hardware-engineer",
        "name": "Engenheiro de hardware",
        "role": "T1/T2, portas, leitura e fila",
        "question": "O número é compatível com a calibração e com o número de tiros?",
        "limit": "Não declara vantagem quântica.",
    },
    {
        "id": "reproducibility",
        "name": "Auditor de reprodutibilidade",
        "role": "ambiente, seed, código, dados e hash",
        "question": "Outra pessoa consegue repetir o resultado com os artefatos publicados?",
        "limit": "Replicação não é garantia de generalização.",
    },
    {
        "id": "ethics",
        "name": "Especialista em ética",
        "role": "consentimento, privacidade, equidade e dupla finalidade",
        "question": "Quem pode ser prejudicado e quem consentiu com os dados?",
        "limit": "Não substitui CEP ou parecer jurídico.",
    },
    {
        "id": "education",
        "name": "Especialista em educação",
        "role": "progressão, avaliação e aprendizagem",
        "question": "O material foi testado com estudantes e mediu retenção?",
        "limit": "Não confunde sensação de aprender com aprendizagem medida.",
    },
    {
        "id": "accessibility",
        "name": "Especialista em acessibilidade",
        "role": "leitura, contraste, neurodivergência e barreiras",
        "question": "O texto é acessível sem infantilizar e sem excluir?",
        "limit": "Não substitui teste com leitores reais.",
    },
    {
        "id": "editor",
        "name": "Editor científico",
        "role": "estrutura, citação, consistência e overclaim",
        "question": "O texto cumpre o contrato de evidência e declara o que não prova?",
        "limit": "Editor não é revisor de mérito.",
    },
    {
        "id": "adversarial",
        "name": "Crítico adversarial",
        "role": "hipótese rival, contraexemplo e falha de generalização",
        "question": "Qual explicação rival derrubaria a conclusão?",
        "limit": "Crítica não é veredito.",
    },
]

# Expansão para 20 revisores: sete lentes adicionais de raciocínio lógico e científico.
REVIEWERS_20 = REVIEWERS_13 + [
    {
        "id": "logician",
        "name": "Lógico-formal",
        "role": "validade, consistência e contraexemplo",
        "question": "A inferência é válida ou apenas retoricamente plausível?",
        "limit": "Validade formal não garante verdade empírica.",
    },
    {
        "id": "complexity-theorist",
        "name": "Teórico da complexidade",
        "role": "BQP/BPP, modelo de custo e comparação justa",
        "question": "A comparação de complexidade usa o mesmo modelo de custo e o mesmo tamanho de entrada?",
        "limit": "Complexidade assintótica não é desempenho no hardware atual.",
    },
    {
        "id": "bayesian-statistician",
        "name": "Estatístico bayesiano",
        "role": "prior, posterior, intervalo e atualização",
        "question": "O prior foi declarado e a atualização é reproduzível?",
        "limit": "Posterior sem prior explícito é opinião disfarçada.",
    },
    {
        "id": "missing-data-auditor",
        "name": "Auditor de dados faltantes",
        "role": "atrito, imputação e viés de seleção",
        "question": "O atrito foi analisado e imputado sem esconder viés?",
        "limit": "Imputação não cria dados; declara suposições.",
    },
    {
        "id": "open-science-auditor",
        "name": "Auditor de ciência aberta",
        "role": "FAIR, pré-registro, código e dados citáveis",
        "question": "Dados, código e plano de análise estão abertos e citáveis?",
        "limit": "Abertura não é garantia de qualidade.",
    },
    {
        "id": "dual-use-security",
        "name": "Especialista em dupla finalidade",
        "role": "segurança, acesso e uso malicioso",
        "question": "Quem pode usar isso e qual é o risco de dupla finalidade?",
        "limit": "Risco não se resolve com disclaimer.",
    },
    {
        "id": "science-translator",
        "name": "Tradutor científico",
        "role": "equivalência conceitual, unidades e limites entre línguas",
        "question": "A tradução preserva conceito, unidade, incerteza e limite?",
        "limit": "Tradução fluente não é equivalência semântica.",
    },
]


def panel() -> dict[str, Any]:
    """Lista os 20 revisores e seus limites."""
    return {
        "total": len(REVIEWERS_20),
        "reviewers": REVIEWERS_20,
        "human_review_required": True,
        "scientific_approval": False,
    }


def questions(claim: str, rounds: int = 2) -> dict[str, Any]:
    """Gera perguntas determinísticas por revisor; não gera respostas."""
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError("claim obrigatório")
    if isinstance(rounds, bool) or not isinstance(rounds, int) or not 1 <= rounds <= 4:
        raise ValueError("rounds deve estar entre 1 e 4")
    itens = []
    for r in REVIEWERS_20:
        for rodada in range(1, rounds + 1):
            itens.append({
                "reviewer": r["id"],
                "role": r["role"],
                "round": rodada,
                "question": f"{r['question']} Aplique a: “{claim.strip()[:240]}”.",
                "required_evidence": "Resposta com fonte, dado, task ID, cálculo ou limite explícito.",
            })
    return {
        "claim": claim.strip(),
        "rounds": rounds,
        "total": len(itens),
        "questions": itens,
        "answers_generated": False,
        "human_review_required": True,
    }
