# -*- coding: utf-8 -*-
"""
Psychological Immersion Scanners — 4 scanners determinísticos para
horror psicológico, indução textual, ritmo frenético e imersão sensorial
=========================================================================

Complementa `scanners/literary_scanners.py` com instrumentos calibrados
especificamente para as dimensões que aquele módulo não cobre: cadência de
indução (repetição, pressuposição, comando incorporado — categorias
descritivas da linguística de sugestão, não um veredito clínico de
hipnose), dinâmica de ritmo (aceleração/desaceleração ao longo do texto,
não só contagem agregada), densidade e cruzamento de canais sensoriais, e
técnicas narrativas de manipulação psicológica do leitor (endereçamento
imperativo, cumplicidade, dupla vinculação, quebra da quarta parede).

Mesma disciplina do módulo irmão: heurísticas determinísticas por
contagem de marcadores lexicais/sintáticos, sem qualquer chamada a LLM,
com `overclaim_guard` explícito. Contar marcadores de indução NÃO prova
que um leitor real entra em transe, sente medo visceral ou é
"manipulado psicologicamente" — isso só se mede empiricamente com
leitores reais (fisiologia, autorrelato, estudo de recepção).

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence, Tuple, Type

from scanners.literary_scanners import (
    DimensionSpec,
    LiteraryScannerBase,
    _clamp,
    _count_keywords,
    _frequency_score,
    _grade,
    _keyword_hits,
    _lower,
    _normalize,
    _presence_score,
    _sentences,
    _term_frequency,
    _words,
)


def _paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", _normalize(text)) if p.strip()]


def _windowed_means(values: Sequence[float], window: int = 40) -> List[float]:
    """Média móvel não sobreposta — usada para medir aceleração ao longo do texto."""
    if not values or window <= 0:
        return []
    return [
        statistics.mean(values[i:i + window])
        for i in range(0, len(values), window)
        if values[i:i + window]
    ]


def _acceleration_score(window_means: Sequence[float]) -> Tuple[float, str]:
    """Compara a 2ª metade do texto com a 1ª: quanto as frases encurtam.

    Retorna (score 0-100, evidência textual). Encurtamento = ritmo mais
    frenético na progressão da leitura; não distingue se é intencional.
    """
    if len(window_means) < 2:
        return 0.0, "texto curto demais para medir aceleração por janelas"
    mid = len(window_means) // 2
    first_half = statistics.mean(window_means[:mid]) if mid else window_means[0]
    second_half = statistics.mean(window_means[mid:])
    if first_half <= 0:
        return 0.0, "janela inicial sem dados"
    delta = (first_half - second_half) / first_half
    # delta > 0 => frases encurtam ao longo da obra (aceleração frenética)
    score = _clamp(50.0 + delta * 200.0)
    evidence = (
        f"média de palavras/frase: 1ª metade {first_half:.2f} → "
        f"2ª metade {second_half:.2f} ({'encurta' if delta > 0 else 'alonga'} "
        f"{abs(delta) * 100:.1f}%)"
    )
    return score, evidence


class HypnoticInductionScanner(LiteraryScannerBase):
    """Marcadores linguísticos de indução textual (repetição, pressuposição,
    comando incorporado, ancoragem temporal) — categorias descritivas da
    linguística de sugestão (ex.: Erickson, PNL popular), não diagnóstico
    clínico de hipnose real."""

    scanner_id = "hypnotic_induction"
    name = "Scanner de Indução Hipnótica Textual"
    description = (
        "Avalia repetição rítmica, pressuposição, comando incorporado e "
        "ancoragem temporal — marcadores linguísticos associados a indução "
        "de transe leve em textos de sugestão, aplicados como heurística "
        "descritiva sobre prosa narrativa."
    )
    dimension_names = (
        "repeticao_ritmica", "pressuposicao", "comando_incorporado", "ancoragem_temporal",
    )

    PRESUPPOSITION = [
        "já sabe", "você sabe que", "sem perceber", "antes mesmo de",
        "você já", "aos poucos", "sem que você note", "enquanto você lê",
        "no momento em que você", "quando você perceber",
    ]
    EMBEDDED_COMMAND = [
        "sinta", "perceba", "imagine", "respire", "olhe", "escute", "pare",
        "feche os olhos", "repare", "note", "observe", "lembre-se", "conte",
        "espere", "aguarde", "continue", "vire a página", "não pare",
    ]
    TEMPORAL_ANCHOR = [
        "agora", "neste exato momento", "nesse instante", "3:14",
        "de novo", "outra vez", "mais uma vez", "sempre que", "toda vez que",
    ]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        words = _words(text)
        sentences = _sentences(text)

        # repetição rítmica: frases que começam com o mesmo bigrama (anáfora)
        openers = [" ".join(_words(s)[:2]) for s in sentences if len(_words(s)) >= 2]
        opener_counts = Counter(openers)
        repeated_openers = [op for op, c in opener_counts.items() if c >= 3 and op]
        anaphora_score = _presence_score(len(repeated_openers), 4)

        pressup_hits = _term_frequency(low, self.PRESUPPOSITION)
        command_hits = _term_frequency(low, self.EMBEDDED_COMMAND)
        anchor_hits = _term_frequency(low, self.TEMPORAL_ANCHOR)

        dims = [
            DimensionSpec(
                "repeticao_ritmica",
                anaphora_score,
                [f"'{op}...' repetido {opener_counts[op]}x" for op in repeated_openers[:6]],
                "Anáfora e repetição de abertura de frase — cadência de indução por repetição.",
            ),
            DimensionSpec(
                "pressuposicao",
                _frequency_score(pressup_hits, len(words), 1.5),
                _keyword_hits(low, self.PRESUPPOSITION),
                "Estruturas que pressupõem um estado do leitor como fato dado.",
            ),
            DimensionSpec(
                "comando_incorporado",
                _frequency_score(command_hits, len(words), 3.0),
                _keyword_hits(low, self.EMBEDDED_COMMAND),
                "Verbos imperativos dirigidos ao leitor, incorporados à narração.",
            ),
            DimensionSpec(
                "ancoragem_temporal",
                _frequency_score(anchor_hits, len(words), 2.0),
                _keyword_hits(low, self.TEMPORAL_ANCHOR),
                "Marcadores de presente contínuo e recorrência temporal ritualizada.",
            ),
        ]
        return dims

    def _warnings(self, score, dimensions, text):
        warnings = super()._warnings(score, dimensions, text)
        warnings.append(
            "Contagem de marcadores linguísticos NÃO prova efeito hipnótico real "
            "sobre leitores — isso exige medição empírica (fisiologia, autorrelato)."
        )
        return warnings


class FreneticPacingScanner(LiteraryScannerBase):
    """Ritmo dinâmico ao longo do texto (não apenas contagem agregada):
    aceleração sentencial, fragmentação visceral e escalada de pontuação."""

    scanner_id = "frenetic_pacing"
    name = "Scanner de Ritmo Frenético e Dinâmico"
    description = (
        "Mede a dinâmica do ritmo ao longo da leitura: aceleração/desaceleração "
        "do comprimento de frase por janelas, fragmentação visceral (rajadas de "
        "frases muito curtas) e escalada de pontuação expressiva."
    )
    dimension_names = (
        "aceleracao_sentencial", "fragmentacao_visceral",
        "escalada_pontuacao", "variancia_paragrafo",
    )

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        sentences = _sentences(text)
        lengths = [len(_words(s)) for s in sentences] or [0]
        window_means = _windowed_means(lengths, window=40)
        accel_score, accel_evidence = _acceleration_score(window_means)

        short_bursts = sum(1 for l in lengths if 0 < l <= 4)
        burst_ratio = short_bursts / max(1, len(lengths))
        burst_score = _clamp(burst_ratio * 250.0)

        exclam = len(re.findall(r"!", text))
        ellipsis = len(re.findall(r"\.\.\.|…", text))
        dash = len(re.findall(r"[—–]", text))
        punctuation_density = ((exclam + ellipsis + dash) / max(1, len(_words(text)))) * 1000.0
        punctuation_score = _clamp((punctuation_density / 25.0) * 100.0)

        paragraphs = _paragraphs(text)
        para_lengths = [len(_words(p)) for p in paragraphs] or [0]
        para_variance = statistics.pstdev(para_lengths) if len(para_lengths) > 1 else 0.0
        variance_score = _clamp((para_variance / 60.0) * 100.0)

        dims = [
            DimensionSpec(
                "aceleracao_sentencial",
                accel_score,
                [accel_evidence],
                "Encurtamento progressivo do comprimento médio de frase ao longo da obra.",
            ),
            DimensionSpec(
                "fragmentacao_visceral",
                burst_score,
                [f"{short_bursts}/{len(lengths)} frases com ≤4 palavras ({burst_ratio * 100:.1f}%)"],
                "Rajadas de frases muito curtas — golpes secos, ritmo visceral.",
            ),
            DimensionSpec(
                "escalada_pontuacao",
                punctuation_score,
                [f"{exclam} exclamações, {ellipsis} reticências, {dash} travessões "
                 f"({punctuation_density:.1f}/1000 palavras)"],
                "Densidade de pontuação expressiva (exclamação, reticência, travessão).",
            ),
            DimensionSpec(
                "variancia_paragrafo",
                variance_score,
                [f"desvio-padrão do comprimento de parágrafo: {para_variance:.1f} palavras"],
                "Alternância entre parágrafos longos e curtos — respiração dinâmica.",
            ),
        ]
        return dims

    def _warnings(self, score, dimensions, text):
        warnings = super()._warnings(score, dimensions, text)
        warnings.append(
            "Ritmo textual medido por pontuação e comprimento de frase é proxy "
            "grosseiro — não substitui leitura em voz alta ou teste com leitores reais."
        )
        return warnings


class SensoryImmersionScanner(LiteraryScannerBase):
    """Densidade e cruzamento de canais sensoriais (incluindo interocepção —
    sensações corporais internas centrais ao horror visceral)."""

    scanner_id = "sensory_immersion"
    name = "Scanner de Imersão Sensorial"
    description = (
        "Mede densidade por canal sensorial (visual, sonoro, olfativo, tátil, "
        "gustativo, interoceptivo) e cruzamento de múltiplos canais na mesma "
        "frase — proxy de intensidade imersiva sensorial."
    )
    dimension_names = (
        "densidade_multissensorial", "interocepcao_corporal",
        "cruzamento_sensorial", "amplitude_de_canais",
    )

    CHANNELS: ClassVar[Dict[str, List[str]]] = {
        "visual": ["olho", "luz", "escuro", "sombra", "brilho", "vulto", "imagem", "cor", "amarelo"],
        "sonoro": ["som", "voz", "silêncio", "zumbido", "grito", "sussurro", "passos", "batida"],
        "olfativo": ["cheiro", "odor", "fedor", "aroma", "adocicado"],
        "tatil": ["frio", "quente", "pele", "textura", "mão", "toque", "arrepio", "calafrio"],
        "gustativo": ["gosto", "sabor", "amargo", "metálico", "boca seca"],
        "interoceptivo": ["coração", "pulso", "respiração", "falta de ar", "estômago",
                          "náusea", "tontura", "suor", "tremor", "fôlego"],
    }

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        words = _words(text)
        sentences = _sentences(text)

        channel_hits: Dict[str, int] = {}
        for channel, terms in self.CHANNELS.items():
            channel_hits[channel] = _term_frequency(low, terms)

        total_hits = sum(channel_hits.values())
        density_score = _frequency_score(total_hits, len(words), 30.0)

        interoceptive_hits = channel_hits["interoceptivo"]
        interoceptive_score = _frequency_score(interoceptive_hits, len(words), 4.0)

        cross_count = 0
        for sentence in sentences:
            s_low = _lower(sentence)
            channels_present = sum(
                1 for terms in self.CHANNELS.values()
                if _count_keywords(s_low, terms) > 0
            )
            if channels_present >= 2:
                cross_count += 1
        cross_ratio = cross_count / max(1, len(sentences))
        cross_score = _clamp(cross_ratio * 400.0)

        active_channels = [c for c, hits in channel_hits.items() if hits > 0]
        amplitude_score = _presence_score(len(active_channels), len(self.CHANNELS))

        dims = [
            DimensionSpec(
                "densidade_multissensorial",
                density_score,
                [f"{total_hits} marcações sensoriais em {len(words)} palavras"],
                "Frequência total de marcadores sensoriais por 1000 palavras.",
            ),
            DimensionSpec(
                "interocepcao_corporal",
                interoceptive_score,
                _keyword_hits(low, self.CHANNELS["interoceptivo"]),
                "Sensações corporais internas (coração, respiração, náusea) — núcleo do horror visceral.",
            ),
            DimensionSpec(
                "cruzamento_sensorial",
                cross_score,
                [f"{cross_count}/{len(sentences)} frases combinam ≥2 canais sensoriais"],
                "Frases que cruzam múltiplos canais sensoriais na mesma unidade — imersão composta.",
            ),
            DimensionSpec(
                "amplitude_de_canais",
                amplitude_score,
                active_channels,
                "Quantidade de canais sensoriais distintos mobilizados (de 6 possíveis).",
            ),
        ]
        return dims


class PsychologicalManipulationScanner(LiteraryScannerBase):
    """Técnicas narrativas de manipulação/implicação psicológica do leitor:
    comando direto, cumplicidade/culpa, dupla vinculação e quebra da quarta
    parede. Descreve técnica de narração, não estado psicológico real do
    leitor."""

    scanner_id = "psychological_manipulation"
    name = "Scanner de Manipulação Psicológica Narrativa"
    description = (
        "Avalia técnicas de implicação do leitor: comando direto em 2ª "
        "pessoa, indução de cumplicidade/culpa, enquadramento de dupla "
        "vinculação (sem saída) e quebra explícita da quarta parede."
    )
    dimension_names = (
        "comando_direto_2a_pessoa", "cumplicidade_e_culpa",
        "dupla_vinculacao", "quebra_da_quarta_parede",
    )

    SECOND_PERSON_COMMAND_VERBS = [
        "sinta", "olhe", "pare", "continue", "escolha", "leia", "vire",
        "feche", "abra", "responda", "decida", "confesse", "admita",
    ]
    COMPLICITY = [
        "você já sabia", "você não pode negar", "você escolheu",
        "você poderia ter parado", "a culpa é sua", "você quis",
        "você continuou lendo", "você voltou", "foi você quem",
    ]
    DOUBLE_BIND = [
        "não importa o que você faça", "de qualquer forma", "não há como voltar",
        "não há saída", "tarde demais", "já não pode fechar", "não adianta parar",
        "o ciclo não se fecha", "não vai conseguir esquecer",
    ]
    FOURTH_WALL = [
        "este livro", "este parágrafo", "esta página", "quem está lendo isto",
        "você, leitor", "a pessoa segurando este livro", "enquanto lê estas linhas",
        "neste exato parágrafo",
    ]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        words = _words(text)

        # Frases (não só depois de .!? — cada parágrafo em LaTeX começa com
        # \noindent, não com pontuação, então tratar cada frase isoladamente
        # evita subcontar imperativos no início de parágrafo.
        imperative_hits = 0
        for sentence in _sentences(text):
            s_words = _words(sentence)
            idx = 0
            while idx < len(s_words) and s_words[idx] in ("noindent", "textit", "textbf"):
                idx += 1
            if idx < len(s_words) and s_words[idx] in self.SECOND_PERSON_COMMAND_VERBS:
                imperative_hits += 1

        complicity_hits = _term_frequency(low, self.COMPLICITY)
        double_bind_pattern_hits = len(re.findall(
            r"n[ãa]o h[áa] (?:tratamento|cura|escape|sa[íi]da|jeito|volta|como)\b"
            r"|imposs[íi]vel (?:fechar|parar|escapar|voltar|esquecer)"
            r"|n[ãa]o (?:se|há como) fech(?:a|á)",
            low,
        ))
        double_bind_hits = _term_frequency(low, self.DOUBLE_BIND) + double_bind_pattern_hits
        fourth_wall_hits = _term_frequency(low, self.FOURTH_WALL)

        dims = [
            DimensionSpec(
                "comando_direto_2a_pessoa",
                _frequency_score(imperative_hits, len(words), 2.0),
                [f"{imperative_hits} comandos imperativos em início de frase"],
                "Verbos imperativos endereçados ao leitor no início de frase/período.",
            ),
            DimensionSpec(
                "cumplicidade_e_culpa",
                _frequency_score(complicity_hits, len(words), 0.5),
                _keyword_hits(low, self.COMPLICITY),
                "Frases que atribuem ao leitor responsabilidade/escolha pela leitura.",
            ),
            DimensionSpec(
                "dupla_vinculacao",
                _frequency_score(double_bind_hits, len(words), 0.4),
                _keyword_hits(low, self.DOUBLE_BIND) + (
                    [f"{double_bind_pattern_hits} ocorrências do padrão 'não há {{cura|tratamento|saída...}}'"]
                    if double_bind_pattern_hits else []
                ),
                "Enquadramento de impossibilidade de escape ou reversão — dupla vinculação narrativa.",
            ),
            DimensionSpec(
                "quebra_da_quarta_parede",
                _frequency_score(fourth_wall_hits, len(words), 0.3),
                _keyword_hits(low, self.FOURTH_WALL),
                "Referências explícitas ao livro/página/ato de leitura como objeto dentro da ficção.",
            ),
        ]
        return dims

    def _warnings(self, score, dimensions, text):
        warnings = super()._warnings(score, dimensions, text)
        warnings.append(
            "Estes marcadores descrevem TÉCNICA NARRATIVA (o que o texto faz), não "
            "o efeito psicológico real em leitores — 'manipulação' aqui é termo "
            "literário-técnico, não avaliação clínica ou ética do efeito sobre pessoas."
        )
        return warnings


PSYCHOLOGICAL_IMMERSION_SCANNER_CLASSES: Tuple[Type[LiteraryScannerBase], ...] = (
    HypnoticInductionScanner,
    FreneticPacingScanner,
    SensoryImmersionScanner,
    PsychologicalManipulationScanner,
)


def run_psychological_immersion_scanner_suite(
    text: str, metadata: Optional[Mapping[str, Any]] = None
) -> Dict[str, Any]:
    """Executa os 4 scanners de imersão psicológica e consolida um índice
    exploratório. Complementa `run_literary_scanner_suite` — não a substitui."""
    meta = dict(metadata or {})
    results: Dict[str, Dict[str, Any]] = {}
    for scanner_cls in PSYCHOLOGICAL_IMMERSION_SCANNER_CLASSES:
        scanner = scanner_cls()
        results[scanner.scanner_id] = scanner.scan(text, meta)

    scores = [payload["score"] for payload in results.values()]
    index = _clamp(sum(scores) / max(1, len(scores))) if _normalize(text) else 0.0

    recommendations: List[str] = []
    warnings: List[str] = []
    for payload in results.values():
        for rec in payload.get("recommendations", []):
            if rec not in recommendations:
                recommendations.append(rec)
        for warn in payload.get("warnings", []):
            if warn not in warnings:
                warnings.append(warn)

    return {
        "domain": "psychological_immersion",
        "scanner_count": len(results),
        "psychological_immersion_score": index,
        "grade": _grade(index),
        "results": results,
        "metadata": meta,
        "recommendations": recommendations[:12],
        "warnings": warnings[:12],
        "overclaim_guard": (
            "Estes índices contam marcadores linguísticos associados a indução, "
            "ritmo, imersão sensorial e implicação do leitor. NÃO medem efeito "
            "psicológico real, estado de transe, resposta fisiológica ou "
            "manipulação efetiva de pessoas — isso exige estudo empírico com "
            "leitores reais (fisiologia, autorrelato, recepção). Use como "
            "instrumento exploratório de revisão, nunca como prova de eficácia."
        ),
    }


psychological_immersion_scanner_suite = run_psychological_immersion_scanner_suite
