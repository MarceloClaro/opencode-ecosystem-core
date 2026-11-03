# -*- coding: utf-8 -*-
"""Gate de integridade de gráficos e narrativas (SPEC-935-R1003).

As regras são heurísticas declaradas: cada achado traz evidência e remédio.
Nenhuma regra prova qualidade científica ou veracidade dos dados.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .util import (
    SCHEMA_VERSION,
    LIMITS,
    DataStoryError,
    canonical_json,
    is_blank,
    is_traceable_source,
    normalize_space,
    sha256_text,
)

SUPPORTED_CHARTS = {
    "bar", "stacked_bar", "area", "histogram", "diverging_bar",
    "line", "scatter", "pie", "dot", "heatmap", "treemap",
}
BAR_FAMILY = {"bar", "stacked_bar", "area", "histogram", "diverging_bar"}
CAUSAL_DESIGNS = {"experimental", "quasi_experimental", "causal"}

CAUSAL_RE = re.compile(
    r"\b("
    r"causa|causou|causam|causado|causada|"
    r"provoca|provocou|gera|gerou|determina|determinou|"
    r"leva\s+a|levou\s+a|devido\s+a|em\s+raz[aã]o\s+de|por\s+causa\s+de|"
    r"resulta\s+em|resultou\s+em|efeito\s+de|impacta|impactou|influencia|influenciou"
    r")\b",
    re.IGNORECASE,
)
HYPE_RE = re.compile(
    r"\b("
    r"explodiu|explos[aã]o|despencou|disparou|astron[oô]mico|"
    r"sem\s+precedentes|surreal|inacredit[aá]vel|revolucion[aá]rio|"
    r"colossal|avassalador|game\s+changer"
    r")\b",
    re.IGNORECASE,
)
ABSOLUTE_RE = re.compile(
    r"\b(sempre|nunca|todos|todas|nenhum|nenhuma|prova\s+que|comprova|"
    r"garante|imposs[ií]vel)\b",
    re.IGNORECASE,
)
LIMIT_RE = re.compile(
    r"(limita|limite|n[aã]o\s+permite|n[aã]o\s+autoriza|n[aã]o\s+prova|"
    r"cautela|n[aã]o\s+implica)",
    re.IGNORECASE,
)
PERCENT_BASE_RE = re.compile(
    r"(de|entre|em\s+cada|a\s+cada|n\s*=|base|sobre)\s*[\d.]+",
    re.IGNORECASE,
)
TITLE_TYPE_RE = re.compile(
    r"^(gr[aá]fico|figura|tabela|quadro|mapa|chart|figure|graph)\b",
    re.IGNORECASE,
)

SEVERITIES = ("critical", "high", "medium", "low")
_WEIGHTS = {"critical": 25, "high": 10, "medium": 3, "low": 1}


def _finding(
    code: str, severity: str, message: str, evidence: dict[str, Any], remedy: str
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "evidence": evidence,
        "remedy": remedy,
    }


def _report(kind: str, findings: list[dict[str, Any]], subject_sha: str) -> dict[str, Any]:
    counts = {severity: 0 for severity in SEVERITIES}
    for finding in findings:
        counts[finding["severity"]] += 1
    score = max(
        0,
        100 - sum(_WEIGHTS[severity] * counts[severity] for severity in SEVERITIES),
    )
    if counts["critical"]:
        status = "blocked"
    elif counts["high"]:
        status = "revise"
    elif counts["medium"] or counts["low"]:
        status = "pass_with_notes"
    else:
        status = "approved"
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": kind,
        "status": status,
        "score": score,
        "counts": counts,
        "findings": findings,
        "subject_sha256": subject_sha,
        "rules_version": SCHEMA_VERSION,
        "limits": list(LIMITS),
    }


def _is_red(hex_color: str) -> bool:
    match = re.fullmatch(r"#?([0-9a-fA-F]{6})", str(hex_color).strip())
    if not match:
        return False
    value = int(match.group(1), 16)
    red, green, blue = (value >> 16) & 255, (value >> 8) & 255, value & 255
    return red > 120 and red > 1.6 * green and red > 1.6 * blue


def _is_green(hex_color: str) -> bool:
    match = re.fullmatch(r"#?([0-9a-fA-F]{6})", str(hex_color).strip())
    if not match:
        return False
    value = int(match.group(1), 16)
    red, green, blue = (value >> 16) & 255, (value >> 8) & 255, value & 255
    return green > 100 and green > 1.4 * red and green > 1.2 * blue


def _has_red_green_pair(palette: Any) -> bool:
    if not isinstance(palette, (list, tuple)):
        return False
    colors = [str(c) for c in palette if isinstance(c, str)]
    return any(_is_red(c) for c in colors) and any(_is_green(c) for c in colors)


def audit_chart(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Audita a especificação de um gráfico e devolve achados classificados."""
    if not isinstance(spec, Mapping):
        raise DataStoryError("invalid_spec", "Especificação deve ser um mapeamento.")

    chart = str(spec.get("chart") or "")
    if chart not in SUPPORTED_CHARTS:
        raise DataStoryError("unsupported_chart", f"Gráfico não suportado: {chart!r}")

    y = spec.get("y") if isinstance(spec.get("y"), Mapping) else {}
    x = spec.get("x") if isinstance(spec.get("x"), Mapping) else {}
    encodings = spec.get("encodings") if isinstance(spec.get("encodings"), Mapping) else {}
    uncertainty = (
        spec.get("uncertainty") if isinstance(spec.get("uncertainty"), Mapping) else {}
    )
    title = normalize_space(spec.get("title"))
    claim = normalize_space(spec.get("claim"))
    source = normalize_space(spec.get("source"))
    note = normalize_space(spec.get("note"))
    legend = normalize_space(spec.get("legend"))
    alt_text = normalize_space(spec.get("alt_text"))
    design = str(spec.get("design") or "observational")
    sample_n = spec.get("sample_n")
    category_count = spec.get("category_count")
    slice_count = spec.get("slice_count") or category_count
    series_count = spec.get("series_count")
    decimals = spec.get("decimals")

    findings: list[dict[str, Any]] = []

    if not title:
        findings.append(_finding(
            "MISSING_TITLE", "critical",
            "Gráfico sem título-mensagem: o leitor não recebe a conclusão.",
            {"title": title},
            "Escrever uma frase com sujeito e resultado, não o nome do gráfico.",
        ))
    elif len(title) < 12 or TITLE_TYPE_RE.match(title):
        findings.append(_finding(
            "TITLE_NOT_MESSAGE", "medium",
            "O título nomeia o gráfico em vez de anunciar a mensagem.",
            {"title": title},
            "Trocar por uma frase-mensagem com o achado principal.",
        ))

    if chart in BAR_FAMILY:
        if y.get("zero") is False:
            findings.append(_finding(
                "TRUNCATED_AXIS", "critical",
                "Barra/área com base diferente de zero distorce a proporção.",
                {"chart": chart, "y_zero": y.get("zero")},
                "Fixar y.zero=true ou trocar por ponto/linha com eixo sinalizado.",
            ))
        elif y.get("zero") is not True:
            findings.append(_finding(
                "UNDECLARED_BASELINE", "high",
                "A base do eixo não foi declarada para um gráfico de magnitude.",
                {"chart": chart, "y_zero": y.get("zero")},
                "Declarar y.zero=true e recomputar a escala.",
            ))

    if chart == "line" and spec.get("axis_break") and not spec.get("axis_break_labeled"):
        findings.append(_finding(
            "UNLABELED_AXIS_BREAK", "high",
            "Quebra de eixo não sinalizada induz leitura de continuidade falsa.",
            {"axis_break": True},
            "Marcar a quebra no eixo e explicar na nota.",
        ))

    if spec.get("dual_axis") is True:
        findings.append(_finding(
            "DUAL_AXIS", "critical",
            "Dois eixos Y permitem correlação visual artificial.",
            {"dual_axis": True},
            "Separar em dois painéis ou indexar as séries a uma base comum.",
        ))

    if spec.get("three_d") is True:
        findings.append(_finding(
            "THREE_D", "critical",
            "Perspectiva 3D altera áreas e ângulos percebidos.",
            {"three_d": True},
            "Usar projeção 2D com codificação proporcional.",
        ))

    if chart == "pie":
        slices = int(slice_count) if isinstance(slice_count, (int, float)) else 0
        if slices > 5:
            findings.append(_finding(
                "PIE_OVERLOAD", "critical",
                f"Pizza com {slices} fatias é ilegível e difícil de comparar.",
                {"slice_count": slices},
                "Trocar por barra ordenada ou barra empilhada.",
            ))
        elif slices == 5:
            findings.append(_finding(
                "PIE_OVERLOAD", "high",
                "Cinco fatias já exigem comparação de ângulos.",
                {"slice_count": slices},
                "Preferir barra ordenada; se mantiver pizza, rotular valores.",
            ))
        if spec.get("part_to_whole") is not True:
            findings.append(_finding(
                "PIE_NOT_PART_TO_WHOLE", "high",
                "Pizza só é legítima para partes exatas de um todo.",
                {"part_to_whole": spec.get("part_to_whole")},
                "Declarar part_to_whole=true e garantir soma de 100%.",
            ))

    if chart == "scatter" and isinstance(sample_n, (int, float)) and not isinstance(sample_n, bool):
        if sample_n > 500 and not spec.get("overplotting_control"):
            findings.append(_finding(
                "OVERPLOTTING", "high",
                "Mais de 500 pontos sem controle de sobreposição esconde densidade.",
                {"sample_n": sample_n},
                "Usar alpha, binning, hexbin ou densidade; declarar o controle.",
            ))

    if spec.get("estimate") is True and uncertainty.get("displayed") is not True:
        findings.append(_finding(
            "MISSING_UNCERTAINTY", "high",
            "Estimativa exibida sem intervalo, erro ou margem.",
            {"estimate": True, "uncertainty": dict(uncertainty)},
            "Exibir IC, erro padrão ou margem e declarar o método.",
        ))

    if (
        not isinstance(sample_n, (int, float))
        or isinstance(sample_n, bool)
        or sample_n <= 0
    ):
        findings.append(_finding(
            "MISSING_SAMPLE_SIZE", "high",
            "O tamanho da amostra não foi declarado.",
            {"sample_n": sample_n},
            "Informar n no rodapé e na nota metodológica.",
        ))

    if not source:
        findings.append(_finding(
            "MISSING_SOURCE", "critical",
            "Gráfico sem fonte: a proveniência não é auditável.",
            {"source": source},
            "Declarar instituição, ano e link/DOI quando houver.",
        ))
    elif not is_traceable_source(source):
        findings.append(_finding(
            "SOURCE_NOT_TRACEABLE", "high",
            "A fonte não contém ano, DOI ou URL verificável.",
            {"source": source},
            "Acrescentar ano de publicação e identificador persistente.",
        ))

    if not note:
        findings.append(_finding(
            "MISSING_NOTE", "high",
            "Gráfico sem nota metodológica.",
            {"note": note},
            "Declarar n, período, filtros, definições e limitação.",
        ))
    elif len(note) < 40 or not re.search(r"\d", note):
        findings.append(_finding(
            "NOTE_TOO_THIN", "high",
            "A nota não sustenta a leitura: falta número ou detalhe metodológico.",
            {"note": note, "length": len(note)},
            "Incluir n, período e critério em ao menos uma frase completa.",
        ))

    if claim:
        if CAUSAL_RE.search(claim) and design not in CAUSAL_DESIGNS:
            findings.append(_finding(
                "CAUSAL_CLAIM_OBSERVATIONAL", "critical",
                "Linguagem causal em desenho que não identifica causa.",
                {"claim": claim, "design": design},
                "Trocar por 'associado a', 'coincide com' ou declarar o desenho causal.",
            ))
        if HYPE_RE.search(claim) and not re.search(r"\d", claim):
            findings.append(_finding(
                "UNQUANTIFIED_SUPERLATIVE", "high",
                "Hipérbole sem âncora numérica.",
                {"claim": claim},
                "Substituir por magnitude, período e comparador explícitos.",
            ))
        if ABSOLUTE_RE.search(claim) and not spec.get("scope_declared"):
            findings.append(_finding(
                "ABSOLUTE_CLAIM", "high",
                "Absoluto sem escopo declarado.",
                {"claim": claim},
                "Delimitar período, população e condição do achado.",
            ))

    if spec.get("color_only") is True and not spec.get("direct_labels"):
        findings.append(_finding(
            "COLOR_ONLY_ENCODING", "high",
            "Cor como único canal exclui leitores com daltonismo e impressão P&B.",
            {"color_only": True, "direct_labels": bool(spec.get("direct_labels"))},
            "Adicionar rótulo direto, forma ou padrão têxtil.",
        ))

    color_used = bool(encodings.get("color")) or spec.get("color_only") is True
    if spec.get("colorblind_safe") is False:
        findings.append(_finding(
            "COLORBLIND_RISK", "high",
            "Paleta declarada como não segura para daltonismo.",
            {"colorblind_safe": False},
            "Usar paleta Okabe-Ito ou codificar também por forma/rótulo.",
        ))
    elif color_used and _has_red_green_pair(spec.get("palette")):
        findings.append(_finding(
            "COLORBLIND_RISK", "medium",
            "Paleta combina vermelho e verde, par de baixa discriminação.",
            {"palette": list(spec.get("palette") or [])},
            "Trocar por azul/laranja ou acrescentar padrão.",
        ))

    if not alt_text:
        findings.append(_finding(
            "NO_ALT_TEXT", "medium",
            "Sem texto alternativo: a figura não é acessível.",
            {"alt_text": alt_text},
            "Descrever a mensagem e os valores principais em uma frase.",
        ))

    numeric_axis = y.get("kind") == "numeric" or chart in {
        "bar", "stacked_bar", "area", "histogram", "line", "scatter", "diverging_bar",
    }
    if (
        chart != "pie"
        and numeric_axis
        and not y.get("unit")
        and not y.get("dimensionless")
        and not spec.get("dimensionless")
    ):
        findings.append(_finding(
            "MISSING_UNITS", "high",
            "Eixo numérico sem unidade e sem declaração de adimensional.",
            {"y": dict(y)},
            "Declarar unidade ('%', 'R$', 'hab.') ou dimensionless=true.",
        ))

    if isinstance(decimals, int) and not isinstance(decimals, bool):
        if decimals > 2 and not spec.get("precision_justified"):
            findings.append(_finding(
                "INCONSISTENT_PRECISION", "low",
                "Precisão acima de duas casas sem justificativa.",
                {"decimals": decimals},
                "Arredondar para a precisão dos dados ou justificar na nota.",
            ))

    if y.get("scale") == "log" and not (
        y.get("log_declared") or spec.get("log_scale_declared")
    ):
        findings.append(_finding(
            "LOG_SCALE_UNDECLARED", "high",
            "Escala logarítmica sem declaração explícita.",
            {"scale": "log"},
            "Rotular o eixo como log e explicar a razão na nota.",
        ))

    if spec.get("has_missing") is True and is_blank(spec.get("missing_policy")):
        findings.append(_finding(
            "MISSING_MISSING_POLICY", "medium",
            "Há dados ausentes sem política declarada.",
            {"has_missing": True},
            "Declarar exclusão, imputação ou categoria 'não informado'.",
        ))

    if spec.get("intent") == "ranking" and str(spec.get("sorting") or "none") == "none":
        findings.append(_finding(
            "UNSORTED_RANKING", "medium",
            "Ranking sem ordenação obriga o leitor a comparar barras dispersas.",
            {"sorting": "none"},
            "Ordenar por valor e destacar o recorte relevante.",
        ))

    if (encodings.get("color") or encodings.get("size")) and not legend and not spec.get("direct_labels"):
        findings.append(_finding(
            "NO_LEGEND", "medium",
            "Codificação visual sem legenda nem rótulo direto.",
            {"encodings": dict(encodings)},
            "Adicionar legenda ou rotular diretamente as marcas.",
        ))

    if chart == "line" and isinstance(series_count, (int, float)) and series_count > 5:
        findings.append(_finding(
            "CROWDED_SERIES", "medium",
            f"{int(series_count)} séries em uma linha competem por atenção.",
            {"series_count": series_count},
            "Destacar poucas séries e agrupar o restante em 'outras'.",
        ))

    if chart in {"bar", "stacked_bar"} and isinstance(category_count, (int, float)):
        if category_count > 12:
            findings.append(_finding(
                "CROWDED_CATEGORIES", "medium",
                f"{int(category_count)} categorias dificultam a leitura.",
                {"category_count": category_count},
                "Agrupar, filtrar ou trocar para barras horizontais com rolagem.",
            ))

    return _report("chart_audit", findings, sha256_text(canonical_json(dict(spec))))


def audit_narrative(
    text: str,
    *,
    design: str = "observational",
    base_declared: bool = False,
    scope_declared: bool = False,
) -> dict[str, Any]:
    """Audita a narrativa que acompanha a figura."""
    narrative = normalize_space(text)
    if not narrative:
        raise DataStoryError("empty_narrative", "Narrativa vazia não pode ser auditada.")
    design = str(design or "observational")
    findings: list[dict[str, Any]] = []

    if CAUSAL_RE.search(narrative) and design not in CAUSAL_DESIGNS:
        findings.append(_finding(
            "CAUSAL_CLAIM_OBSERVATIONAL", "critical",
            "Verbo causal em narrativa de desenho não causal.",
            {"design": design},
            "Reescrever como associação ou explicitar o desenho causal.",
        ))

    if ABSOLUTE_RE.search(narrative) and not scope_declared:
        findings.append(_finding(
            "ABSOLUTE_CLAIM", "high",
            "Absoluto sem delimitação de escopo.",
            {"scope_declared": scope_declared},
            "Delimitar período, população e condição.",
        ))

    if (
        re.search(r"%|por\s+cento", narrative, re.IGNORECASE)
        and not base_declared
        and not PERCENT_BASE_RE.search(narrative)
    ):
        findings.append(_finding(
            "PERCENT_WITHOUT_BASE", "high",
            "Percentual sem denominador declarado.",
            {"base_declared": base_declared},
            "Informar a base: 'de 1.200 casos', 'entre os 40 municípios'.",
        ))

    if HYPE_RE.search(narrative) and not re.search(r"\d", narrative):
        findings.append(_finding(
            "HYPE_WITHOUT_NUMBER", "high",
            "Hipérbole sem número que a sustente.",
            {},
            "Substituir por magnitude e comparador.",
        ))

    if not LIMIT_RE.search(narrative):
        findings.append(_finding(
            "NO_STATED_LIMIT", "medium",
            "A narrativa não declara limite ou abstenção.",
            {},
            "Acrescentar o que o desenho não permite concluir.",
        ))

    return _report("narrative_audit", findings, sha256_text(narrative))
