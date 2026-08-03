# -*- coding: utf-8 -*-
"""
Literary Scanners — 8 scanners determinísticos para crítica literária
====================================================================

Este módulo complementa os scanners científicos/ecossistêmicos com instrumentos
calibrados para literatura. Os resultados são heurísticos, auditáveis e
serializáveis; servem para estudo, produção, revisão e comparação interna de
obras, sem pretender substituir crítica humana, recepção especializada ou
validação externa.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Type


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return round(max(lo, min(hi, value)), 2)


def _normalize(text: str) -> str:
    return (text or "").strip()


def _lower(text: str) -> str:
    return _normalize(text).lower()


def _words(text: str) -> List[str]:
    return re.findall(r"[\wÀ-ÿ]+(?:[-'][\wÀ-ÿ]+)?", _lower(text), flags=re.UNICODE)


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"[.!?]+", _normalize(text)) if s.strip()]


def _count_keywords(text_lower: str, keywords: Iterable[str]) -> int:
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def _keyword_hits(text_lower: str, keywords: Iterable[str], limit: int = 10) -> List[str]:
    return [kw for kw in keywords if kw.lower() in text_lower][:limit]


def _presence_score(count: int, target: int) -> float:
    if target <= 0:
        return 0.0
    return _clamp((count / target) * 100.0)


def _frequency_score(total_hits: int, word_count: int, target_per_1000: float) -> float:
    if word_count <= 0 or target_per_1000 <= 0:
        return 0.0
    per_1000 = (total_hits / word_count) * 1000.0
    return _clamp((per_1000 / target_per_1000) * 100.0)


def _term_frequency(text_lower: str, keywords: Iterable[str]) -> int:
    total = 0
    for kw in keywords:
        total += len(re.findall(rf"\b{re.escape(kw.lower())}\b", text_lower, flags=re.UNICODE))
    return total


def _mean_segmental_ttr(words: Sequence[str], window: int = 1000) -> float:
    """MSTTR (Mean Segmental Type-Token Ratio): TTR calculado em janelas fixas
    e depois calculado a média entre elas. Ao contrário do TTR global, não
    penaliza textos longos apenas por serem longos (Heaps'/Herdan's law faz o
    TTR bruto cair conforme o texto cresce, mesmo com vocabulário rico e
    estável) — é a métrica padrão em linguística de corpus para comparar
    riqueza lexical entre textos de tamanhos diferentes."""
    if not words or window <= 0:
        return 0.0
    ratios = []
    for i in range(0, len(words), window):
        chunk = words[i:i + window]
        if len(chunk) < window // 2 and ratios:
            # última janela incompleta demais: descarta em vez de distorcer a média
            continue
        if chunk:
            ratios.append(len(set(chunk)) / len(chunk))
    return statistics.mean(ratios) if ratios else (len(set(words)) / max(1, len(words)))


def _lexical_variety_score_msttr(words: Sequence[str], window: int = 1000) -> Tuple[float, float]:
    """Retorna (score 0-100, msttr bruto) usando MSTTR em vez de TTR global."""
    msttr = _mean_segmental_ttr(words, window=window)
    # calibrado sobre o mesmo alvo de referência (~0.42) usado no TTR global,
    # mas agora comparável entre textos curtos e longos
    return _clamp((msttr / 0.42) * 100.0), msttr


def _grade(score: float) -> str:
    if score >= 85.0:
        return "excelente"
    if score >= 70.0:
        return "forte"
    if score >= 50.0:
        return "consistente"
    if score >= 25.0:
        return "emergente"
    return "insuficiente"


def _empty_result(scanner_id: str, name: str, dimension_names: Sequence[str]) -> Dict[str, Any]:
    dimensions = {
        dim: {"score": 0.0, "evidence": [], "rationale": "Texto ausente ou insuficiente."}
        for dim in dimension_names
    }
    return {
        "scanner_id": scanner_id,
        "name": name,
        "score": 0.0,
        "grade": "insuficiente",
        "dimensions": dimensions,
        "evidence": [],
        "warnings": ["Texto vazio ou insuficiente para avaliação literária confiável."],
        "recommendations": ["Forneça um excerto literário substancial, com personagens, imagens, conflitos e paratextos."],
    }


@dataclass(frozen=True)
class DimensionSpec:
    name: str
    score: float
    evidence: List[str]
    rationale: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "score": _clamp(self.score),
            "evidence": list(self.evidence),
            "rationale": self.rationale,
        }


class LiteraryScannerBase:
    """Base comum para scanners literários determinísticos."""

    scanner_id: ClassVar[str] = "literary_base"
    name: ClassVar[str] = "Scanner Literário Base"
    description: ClassVar[str] = "Base abstrata para avaliação literária."
    dimension_names: ClassVar[Tuple[str, ...]] = ()

    def scan(self, text: str, metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        clean = _normalize(text)
        if not clean:
            return _empty_result(self.scanner_id, self.name, self.dimension_names)

        dims = self._evaluate(clean, metadata or {})
        score = _clamp(sum(d.score for d in dims) / max(1, len(dims)))
        dimensions = {d.name: d.as_dict() for d in dims}
        evidence = self._collect_evidence(dims)
        warnings = self._warnings(score, dimensions, clean)
        recommendations = self._recommendations(score, dimensions, clean)
        return {
            "scanner_id": self.scanner_id,
            "name": self.name,
            "score": score,
            "grade": _grade(score),
            "dimensions": dimensions,
            "evidence": evidence,
            "warnings": warnings,
            "recommendations": recommendations,
        }

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        raise NotImplementedError

    def _collect_evidence(self, dims: Sequence[DimensionSpec]) -> List[str]:
        evidence: List[str] = []
        for dim in dims:
            for item in dim.evidence:
                if item not in evidence:
                    evidence.append(item)
        return evidence[:14]

    def _warnings(self, score: float, dimensions: Mapping[str, Any], text: str) -> List[str]:
        warnings: List[str] = []
        low_dims = [name for name, payload in dimensions.items() if payload["score"] < 35.0]
        if low_dims:
            warnings.append("Dimensões literárias frágeis: " + ", ".join(low_dims[:4]) + ".")
        if score < 25.0:
            warnings.append("Amostra literária muito pobre para conclusão crítica robusta.")
        return warnings

    def _recommendations(self, score: float, dimensions: Mapping[str, Any], text: str) -> List[str]:
        recommendations: List[str] = []
        for name, payload in dimensions.items():
            if payload["score"] < 50.0:
                recommendations.append(f"Fortaleça a dimensão '{name}' com marcas textuais mais explícitas.")
        if not recommendations:
            recommendations.append("Manter a complexidade literária observada e submeter a leitura crítica humana comparativa.")
        return recommendations[:6]


class NarrativeArchitectureScanner(LiteraryScannerBase):
    scanner_id = "narrative_architecture"
    name = "Scanner de Arquitetura Narrativa"
    description = "Avalia enredo, estrutura, temporalidade, tensão e fechamento/abertura narrativa."
    dimension_names = ("estrutura", "conflito_e_tensao", "temporalidade", "fechamento_circular")

    STRUCTURE = ["parte", "capítulo", "fragmento", "ato", "cena", "epílogo", "prólogo", "mapa", "rota", "grafo"]
    CONFLICT = ["conflito", "tensão", "segredo", "revela", "descobre", "perda", "morte", "fuga", "medo", "crise", "ameaça"]
    TEMPORAL = ["passado", "presente", "futuro", "antes", "depois", "década", "ano", "memória", "retorna", "começou"]
    CLOSURE = ["epílogo", "fim", "final", "desfecho", "ciclo", "recomeça", "retorna", "converge", "destino"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        years = re.findall(r"\b(?:18|19|20)\d{2}\b", low)
        dims = [
            DimensionSpec("estrutura", _presence_score(_count_keywords(low, self.STRUCTURE), 5), _keyword_hits(low, self.STRUCTURE), "Marcas de macroestrutura, partes e navegação."),
            DimensionSpec("conflito_e_tensao", _presence_score(_count_keywords(low, self.CONFLICT), 5), _keyword_hits(low, self.CONFLICT), "Presença de forças dramáticas e revelações."),
            DimensionSpec("temporalidade", _clamp((_presence_score(_count_keywords(low, self.TEMPORAL), 4) * 0.65) + (_presence_score(len(set(years)), 3) * 0.35)), _keyword_hits(low, self.TEMPORAL) + years[:4], "Gestão de camadas temporais, memória e cronologia."),
            DimensionSpec("fechamento_circular", _presence_score(_count_keywords(low, self.CLOSURE), 3), _keyword_hits(low, self.CLOSURE), "Capacidade de organizar conclusão, retorno ou abertura interpretativa."),
        ]
        return dims


class CharacterPsychologyScanner(LiteraryScannerBase):
    scanner_id = "character_psychology"
    name = "Scanner de Personagem e Psicologia"
    description = "Avalia agência, desejo, conflito interno, transformação e rede relacional."
    dimension_names = ("presenca_personagens", "agencia_e_desejo", "conflito_interno", "rede_relacional")

    CHARACTER = ["personagem", "protagonista", "narrador", "joaquim", "lúcia", "oliveira", "paciente", "leitor", "arquivista", "médico", "mãe", "pai"]
    AGENCY = ["deseja", "quer", "precisa", "tenta", "escolhe", "escolhi", "escolher", "recusa", "aceita", "procura", "investiga", "decide", "enfrenta", "opção", "ato de investigação"]
    INNER = ["trauma", "culpa", "medo", "fome", "desejo", "delírio", "sonho", "sintoma", "transformação", "torna-se", "crise"]
    RELATION = ["mãe", "pai", "filho", "médico", "leitor", "paciente", "família", "instituição", "hospedeiro", "testemunha"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        capitalized = re.findall(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]{2,}\b", text)
        named_score = _presence_score(len(set(capitalized)), 4)
        dims = [
            DimensionSpec("presenca_personagens", _clamp((_presence_score(_count_keywords(low, self.CHARACTER), 4) * 0.7) + (named_score * 0.3)), _keyword_hits(low, self.CHARACTER) + list(dict.fromkeys(capitalized[:5])), "Densidade de agentes narrativos nomeados ou funcionais."),
            DimensionSpec("agencia_e_desejo", _presence_score(_count_keywords(low, self.AGENCY), 4), _keyword_hits(low, self.AGENCY), "Verbos e marcas de decisão, busca e ação."),
            DimensionSpec("conflito_interno", _presence_score(_count_keywords(low, self.INNER), 4), _keyword_hits(low, self.INNER), "Marcas de interioridade, trauma e alteração psicológica."),
            DimensionSpec("rede_relacional", _presence_score(_count_keywords(low, self.RELATION), 4), _keyword_hits(low, self.RELATION), "Relações que situam personagem em vínculos sociais e afetivos."),
        ]
        return dims


class StyleVoiceScanner(LiteraryScannerBase):
    scanner_id = "style_voice"
    name = "Scanner de Estilo e Voz"
    description = "Avalia léxico, ritmo, campos sensoriais, variação discursiva e assinatura vocal."
    dimension_names = ("riqueza_lexical", "ritmo_sintatico", "sensorialidade", "variedade_discursiva")

    SENSORY = ["cheiro", "som", "silêncio", "luz", "escuro", "olho", "sangue", "frio", "quente", "voz", "cor", "textura", "noite"]
    DISCOURSE = ["diário", "laudo", "carta", "relatório", "nota", "prontuário", "transcrição", "depoimento", "arquivo"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        ws = _words(text)
        sent = _sentences(text)
        lengths = [len(_words(s)) for s in sent] or [0]
        avg_len = sum(lengths) / max(1, len(lengths))
        variation = (max(lengths) - min(lengths)) if len(lengths) > 1 else 0
        rhythm_score = _clamp(45.0 + min(35.0, variation * 2.0) + (20.0 if 6 <= avg_len <= 28 else 0.0))
        low = _lower(text)
        quote_marks = len(re.findall(r"[\"“”‘’—]", text))
        lex_score, msttr = _lexical_variety_score_msttr(ws)
        dims = [
            DimensionSpec("riqueza_lexical", lex_score, [f"{len(set(ws))} vocábulos únicos em {len(ws)} palavras", f"MSTTR (janelas de 1000 palavras): {msttr:.3f}"], "Variedade lexical medida por MSTTR (janelas de 1000 palavras) — comparável entre textos curtos e longos, ao contrário do TTR global."),
            DimensionSpec("ritmo_sintatico", rhythm_score, [f"média de {avg_len:.1f} palavras/frase", f"variação sintática {variation}"], "Alternância de frases curtas e longas, útil para voz e cadência."),
            DimensionSpec("sensorialidade", _presence_score(_count_keywords(low, self.SENSORY), 5), _keyword_hits(low, self.SENSORY), "Marcas sensoriais e imagéticas que dão corpo à voz."),
            DimensionSpec("variedade_discursiva", _clamp((_presence_score(_count_keywords(low, self.DISCOURSE), 4) * 0.75) + (_presence_score(quote_marks, 4) * 0.25)), _keyword_hits(low, self.DISCOURSE) + ([f"{quote_marks} marcas de citação/travessão"] if quote_marks else []), "Variação de registros, documentos e vozes."),
        ]
        return dims


class SymbolicImageryScanner(LiteraryScannerBase):
    scanner_id = "symbolic_imagery"
    name = "Scanner de Simbologia e Imagens"
    description = "Avalia símbolos recorrentes, motivos, imagens sensoriais e densidade metafórica."
    dimension_names = ("motivos_simbolicos", "campos_sensoriais", "metaforicidade", "recorrencia")

    SYMBOLS = ["olho", "cheiro", "vala", "fome", "coruja", "sangue", "arquivo", "página", "porta", "noite", "diário", "ciclo", "cinza"]
    VISUAL = ["olho", "luz", "escuro", "sombra", "amarelo", "fotografia", "imagem"]
    SOUND = ["som", "voz", "silêncio", "zumbido", "canto", "grito", "sussurro"]
    SMELL = ["cheiro", "odor", "adocicado", "fedor", "aroma"]
    TACTILE = ["frio", "quente", "pele", "textura", "mão", "toque"]
    METAPHOR = ["metáfora", "como", "parece", "símbolo", "imagem", "figura", "torna-se", "encarna"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        symbol_counts = Counter({kw: len(re.findall(rf"\b{re.escape(kw)}\b", low)) for kw in self.SYMBOLS})
        repeated = [kw for kw, count in symbol_counts.items() if count >= 2]
        fields = {
            "visual": _count_keywords(low, self.VISUAL),
            "sonoro": _count_keywords(low, self.SOUND),
            "olfativo": _count_keywords(low, self.SMELL),
            "tátil": _count_keywords(low, self.TACTILE),
        }
        active_fields = [name for name, count in fields.items() if count > 0]
        dims = [
            DimensionSpec("motivos_simbolicos", _presence_score(_count_keywords(low, self.SYMBOLS), 5), _keyword_hits(low, self.SYMBOLS), "Inventário de símbolos e motivos imagéticos."),
            DimensionSpec("campos_sensoriais", _presence_score(len(active_fields), 3), active_fields, "Diversidade de campos sensoriais mobilizados."),
            DimensionSpec("metaforicidade", _presence_score(_count_keywords(low, self.METAPHOR), 3), _keyword_hits(low, self.METAPHOR), "Marcas explícitas ou implícitas de figuração metafórica."),
            DimensionSpec("recorrencia", _presence_score(len(repeated), 3), repeated[:8], "Retorno de motivos, essencial para coesão simbólica."),
        ]
        return dims


class IntertextualTheoryScanner(LiteraryScannerBase):
    scanner_id = "intertextual_theory"
    name = "Scanner Intertextual e Teórico"
    description = "Avalia diálogo com gêneros, teorias, paratextos e tradições literárias."
    dimension_names = ("generos_e_tradicoes", "conceitos_teoricos", "paratextualidade", "cuidado_documental")

    GENRES = ["romance", "horror", "fantástico", "arquivo", "laudo", "diário", "carta", "ficção", "forense", "documental"]
    THEORY = ["trauma", "memória", "ética", "representação", "metaficção", "ergódica", "hipertexto", "intertextualidade", "paratexto", "arquivo"]
    PARATEXT = ["nota do autor", "nota histórica", "nota do arquivista", "nota do editor", "n.e.", "aparato paratextual", "editorial", "epígrafe", "prefácio", "passaporte", "índice", "mapa", "bibliografia"]
    CARE = ["ficção", "não substitui", "testemunho", "histórica", "documento", "reparação", "limite", "validação externa"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        dims = [
            DimensionSpec("generos_e_tradicoes", _presence_score(_count_keywords(low, self.GENRES), 5), _keyword_hits(low, self.GENRES), "Sinais de filiação genérica e tradição literária."),
            DimensionSpec("conceitos_teoricos", _presence_score(_count_keywords(low, self.THEORY), 5), _keyword_hits(low, self.THEORY), "Vocabulário crítico-teórico mobilizado pela obra ou análise."),
            DimensionSpec("paratextualidade", _presence_score(_count_keywords(low, self.PARATEXT), 3), _keyword_hits(low, self.PARATEXT), "Uso consciente de molduras editoriais e paratextuais."),
            DimensionSpec("cuidado_documental", _presence_score(_count_keywords(low, self.CARE), 3), _keyword_hits(low, self.CARE), "Distinção entre documento, ficção, testemunho e limite interpretativo."),
        ]
        return dims


class ReaderResponseScanner(LiteraryScannerBase):
    scanner_id = "reader_response"
    name = "Scanner de Resposta e Comportamento do Leitor"
    description = "Avalia imersão, instruções, participação, pactos e efeitos comportamentais de leitura."
    dimension_names = ("enderecamento_ao_leitor", "participacao", "imersao_afetiva", "protocolo_de_leitura")

    ADDRESS = ["você", "leitor", "sua", "seu", "te", "contigo", "quem lê"]
    PARTICIPATION = ["rota", "escolha", "marque", "passaporte", "mapa", "fragmento", "hipertexto", "percurso", "grafo"]
    IMMERSION = ["medo", "sonho", "sintoma", "contaminação", "suspense", "atmosfera", "imersão", "cheiro", "noite"]
    PROTOCOL = ["leia", "siga", "comece", "volte", "escolha", "ao final", "recomenda-se", "marque", "consulte", "não falhe", "não vire", "feche o livro", "em voz alta", "não pare", "continue lendo"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        words = _words(text)
        address_frequency = _term_frequency(low, self.ADDRESS)
        dims = [
            DimensionSpec("enderecamento_ao_leitor", _clamp((_presence_score(_count_keywords(low, self.ADDRESS), 3) * 0.7) + (_frequency_score(address_frequency, len(words), 12.0) * 0.3)), _keyword_hits(low, self.ADDRESS), "Chamadas diretas ao leitor e segunda pessoa."),
            DimensionSpec("participacao", _presence_score(_count_keywords(low, self.PARTICIPATION), 5), _keyword_hits(low, self.PARTICIPATION), "Dispositivos de escolha, navegação e ação leitora."),
            DimensionSpec("imersao_afetiva", _presence_score(_count_keywords(low, self.IMMERSION), 4), _keyword_hits(low, self.IMMERSION), "Efeitos afetivos e sensoriais esperados na leitura."),
            DimensionSpec("protocolo_de_leitura", _presence_score(_count_keywords(low, self.PROTOCOL), 3), _keyword_hits(low, self.PROTOCOL), "Instruções que organizam comportamento de leitura."),
        ]
        return dims


class EthicalRepresentationScanner(LiteraryScannerBase):
    scanner_id = "ethical_representation"
    name = "Scanner de Ética da Representação"
    description = "Avalia risco e responsabilidade ao representar trauma, violência, alteridade e história social."
    dimension_names = ("contexto_de_trauma", "avisos_e_limites", "anti_exploracao", "violencia_institucional")

    TRAUMA = ["trauma", "violência", "fome", "morte", "confinamento", "hospital", "manicômio", "seca", "vítimas", "dor"]
    DISCLAIMERS = ["ficção", "não existiram", "baseado", "nota histórica", "cuidado", "advertência", "aviso", "limitação", "aviso de conteúdo", "conteúdo sensível", "trigger warning"]
    ANTI_EXPLOIT = ["ética", "responsabilidade", "não substitui", "reparação", "testemunho", "respeito", "limites", "romantização", "apropriação", "horror real", "distinção", "autoproteção", "representação ética"]
    INSTITUTIONAL = ["instituição", "estado", "hospital", "governo", "paciente", "diagnóstico", "prontuário", "arquivo", "colônia", "curral"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        dims = [
            DimensionSpec("contexto_de_trauma", _presence_score(_count_keywords(low, self.TRAUMA), 5), _keyword_hits(low, self.TRAUMA), "Reconhecimento de dor, violência e sofrimento histórico/social."),
            DimensionSpec("avisos_e_limites", _presence_score(_count_keywords(low, self.DISCLAIMERS), 3), _keyword_hits(low, self.DISCLAIMERS), "Molduras que demarcam ficção, risco e limites de leitura."),
            DimensionSpec("anti_exploracao", _presence_score(_count_keywords(low, self.ANTI_EXPLOIT), 3), _keyword_hits(low, self.ANTI_EXPLOIT), "Cuidados contra exploração estética do trauma."),
            DimensionSpec("violencia_institucional", _presence_score(_count_keywords(low, self.INSTITUTIONAL), 4), _keyword_hits(low, self.INSTITUTIONAL), "Consciência de mediações institucionais e burocráticas da violência."),
        ]
        return dims

    def _warnings(self, score: float, dimensions: Mapping[str, Any], text: str) -> List[str]:
        warnings = super()._warnings(score, dimensions, text)
        trauma = dimensions.get("contexto_de_trauma", {}).get("score", 0.0)
        limits = dimensions.get("avisos_e_limites", {}).get("score", 0.0)
        anti = dimensions.get("anti_exploracao", {}).get("score", 0.0)
        if trauma >= 60.0 and (limits < 40.0 or anti < 35.0):
            warnings.append("Há alta densidade de trauma com proteção ética insuficiente; risco de estetização da dor.")
        return warnings


class LiteraryInnovationScanner(LiteraryScannerBase):
    scanner_id = "literary_innovation"
    name = "Scanner de Inovação Literária"
    description = "Avalia experimentação formal, hibridismo, materialidade editorial e contribuição potencial."
    dimension_names = ("experimento_formal", "hibridismo_generico", "materialidade", "contribuicao_potencial")

    FORMAL = ["fragmento", "rota", "grafo", "mapa", "hipertexto", "ergódica", "não linear", "passaporte", "percurso", "interativo", "apropriação", "apropriação formal", "dsm", "laudo clínico", "estrutura narrativa"]
    HYBRID = ["romance-arquivo", "romance", "laudo", "diário", "prontuário", "carta", "horror", "forense", "documental", "metaficção"]
    MATERIAL = ["tipografia", "página", "folio", "miolo", "sépia", "margem", "impressão", "mapa", "capa", "paratexto", "lápis", "tinta", "papel", "caligrafia", "exumação", "restauro", "caneta", "manuscrito", "tinta borrada"]
    CONTRIBUTION = ["inovação", "contribuição", "dispositivo", "projeto literário", "experiência", "leitor", "forma", "experimento"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[DimensionSpec]:
        low = _lower(text)
        dims = [
            DimensionSpec("experimento_formal", _presence_score(_count_keywords(low, self.FORMAL), 5), _keyword_hits(low, self.FORMAL), "Recursos que alteram a forma tradicional de leitura."),
            DimensionSpec("hibridismo_generico", _presence_score(_count_keywords(low, self.HYBRID), 5), _keyword_hits(low, self.HYBRID), "Combinação de gêneros, registros e suportes discursivos."),
            DimensionSpec("materialidade", _presence_score(_count_keywords(low, self.MATERIAL), 4), _keyword_hits(low, self.MATERIAL), "Consciência do livro como objeto material e editorial."),
            DimensionSpec("contribuicao_potencial", _presence_score(_count_keywords(low, self.CONTRIBUTION), 3), _keyword_hits(low, self.CONTRIBUTION), "Sinais de projeto autoral e contribuição formal potencial."),
        ]
        return dims

    def _recommendations(self, score: float, dimensions: Mapping[str, Any], text: str) -> List[str]:
        recommendations = super()._recommendations(score, dimensions, text)
        recommendations.append("Compare a inovação proposta com corpus de referência antes de declarar contribuição consolidada.")
        return recommendations[:6]


LITERARY_SCANNER_CLASSES: Tuple[Type[LiteraryScannerBase], ...] = (
    NarrativeArchitectureScanner,
    CharacterPsychologyScanner,
    StyleVoiceScanner,
    SymbolicImageryScanner,
    IntertextualTheoryScanner,
    ReaderResponseScanner,
    EthicalRepresentationScanner,
    LiteraryInnovationScanner,
)


def run_literary_scanner_suite(text: str, metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Executa os 8 scanners literários e consolida uma nota exploratória.

    A nota agregada é um índice interno de apoio à análise, não uma validação
    externa de qualidade literária.
    """
    meta = dict(metadata or {})
    results: Dict[str, Dict[str, Any]] = {}
    for scanner_cls in LITERARY_SCANNER_CLASSES:
        scanner = scanner_cls()
        results[scanner.scanner_id] = scanner.scan(text, meta)

    scores = [payload["score"] for payload in results.values()]
    excellence = _clamp(sum(scores) / max(1, len(scores))) if _normalize(text) else 0.0

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
        "domain": "literary",
        "scanner_count": len(results),
        "literary_excellence_score": excellence,
        "grade": _grade(excellence),
        "results": results,
        "metadata": meta,
        "recommendations": recommendations[:12],
        "warnings": warnings[:12],
        "overclaim_guard": (
            "Este índice não substitui crítica literária humana, recepção especializada, "
            "comparação de corpus ou validação externa; use-o como instrumento exploratório."
        ),
    }


literary_scanner_suite = run_literary_scanner_suite
