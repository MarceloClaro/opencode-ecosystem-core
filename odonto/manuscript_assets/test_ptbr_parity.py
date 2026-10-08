#!/usr/bin/env python3
"""SPEC-935-R641 — Gate de paridade EN<->PT-BR do manuscrito OdontoCA.

Verifica que a traducao PT-BR preserva integralmente o conteudo numerico,
as referencias, os DOIs e as ressalvas metodologicas do manuscrito EN canonico.

Regra de normalizacao: PT-BR usa '.' como separador de milhar e ',' como
decimal, enquanto EN usa ',' como milhar e '.' como decimal. O teste
canonicaliza AMBAS as formas para a mesma representacao, de modo que
'2,504' (EN) e '2.504' (PT) sao equivalentes. O que nao pode mudar e o
par {milhar, decimal} de cada numero.

Executar: python3 manuscript_assets/test_ptbr_parity.py
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

EN_PATH = Path(__file__).resolve().parent.parent / "Journal_of_Dentistry_Example_OdontoCA.md"
PT_PATH = Path(__file__).resolve().parent.parent / "Journal_of_Dentistry_Example_OdontoCA_PT.md"

# Números cuja forma textual deve permanecer byte-idêntica (identificadores,
# hashes, versões, seeds). Não normalizar.
LITERAL_NUMBERS = {
    "20", "5161", "1", "2", "3", "4", "5",
    "20260930",
    "1.6.1", "1.9.0", "1.3.2", "1.9.1",
}

# Valores numéricos que definem o resultado científico. Cada um DEVE existir
# nos dois manuscritos com o mesmo par (milhar, decimal).
SCIENCE_NUMBERS = [
    # Proveniência
    "2504", "89", "220", "2284", "1388", "1160", "913", "84", "163", "997",
    "11",
    # Conjunto de análise
    "996", "83", "81", "44",
    # Performance
    "0.166", "0.120", "0.246",
    "0.686", "0.618", "0.754",
    "0.178", "0.138", "0.239",
    "0.737", "0.660", "0.804",
    "0.012", "0.046", "0.058", "0.051", "0.009", "0.112",
    "0.0833", "0.083",
    # Brier / log loss
    "0.0806", "0.0624", "0.0996",
    "0.0754", "0.0574", "0.0949",
    "0.0764", "0.2884", "0.2690", "0.2869",
    "0.0052", "0.0104", "0.0004",
    # Recalibração
    "0.0745", "0.00610", "0.01173", "0.00067",
    "0.2680", "0.04058", "0.00020",
    "0.0740", "0.00141", "0.00308", "0.00037",
    "0.1182", "0.0833", "0.446", "0.516",
    "0.0878", "0.066", "0.605",
    "0.0819", "0.613", "0.0762", "0.2730",
    "0.0802", "0.808", "0.2680",
    "0.0810", "0.603", "0.0753",
    "0.0827", "0.811", "0.2638",
    # Coeficientes / frações
    "0.01", "0.1", "10", "1000", "8", "6",
    "8.33",
]

# Ressenhas metodológicas cuja ausência na PT destruiria o anti-overclaim.
REQUIRED_HEDGES_PT = [
    "exploratória",           # exploratória
    "exploratórias",
    "interna",
    "interno",
    "não",
    "zero",
    "sem",
    "limiar",
    "não",
    "clínica",
    "externo",
    "revisão",
    "verificação",
    "próprio",
    "condicionais",       # condicionais (predições cruzadas)
    "limitada",
    "necessária",
]

# Placeholders que devem permanecer em PT-BR (não podem ser preenchidos).
REQUIRED_PLACEHOLDER_MARKERS = [
    "Financiamento",
    "conflito de interesses",
    "CRediT",
    "devem confirmar",
    "A ser preenchido",
]

FORBIDDEN_PT = [
    "must confirm",
    "To be completed",
    "TBD",
    "XXX",
    "Lorem ipsum",
    "[CITATION NEEDED]",
    "undefined",
    "NaN",
    "None",
]


def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def normalize_markers(text: str) -> str:
    """Remove acentos e caixa para comparar marcadores de texto."""
    return strip_accents(text).lower()


def extract_canonical_numbers(text: str) -> set[str]:
    """Extrai todos os numeros de texto EN, canonicalizando separadores.

    Formato EN: 2,504 (milhar), 0.166 (decimal).
    Retorna strings no formato EN canonico: '2504', '0.166'.
    """
    body = text
    nums = set()
    for m in re.finditer(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(?![\w])", body):
        raw = m.group(1)
        if "," in raw and "." in raw:
            # milhar + decimal no formato EN: remove virgulas
            nums.add(raw.replace(",", ""))
        elif "," in raw:
            # so virgula -> milhar
            nums.add(raw.replace(",", ""))
        else:
            nums.add(raw)
    return nums


def extract_pt_numbers(text: str) -> set[str]:
    """Extrai numeros de texto PT-BR, canonicalizando separadores.

    Formato PT: 2.504 (milhar), 0,166 (decimal).
    Retorna strings no formato EN canonico: '2504', '0.166'.
    """
    nums = set()
    for m in re.finditer(r"(?<![\w.])(\d[\d.]*(?:,\d+)?)(?![\w])", text):
        raw = m.group(1)
        if "," in raw and "." in raw:
            # PT nunca usa 'X.Y.Z' como milhar+decimal; '.' e milhar e ',' e decimal
            # Ex: '0.1182' ja e decimal, '2.504' e milhar
            # Heuristica: se ',' presente, '.' e milhar
            nums.add(raw.replace(".", "").replace(",", "."))
        elif "," in raw:
            # so virgula -> decimal PT
            nums.add(raw.replace(",", "."))
        elif "." in raw:
            # so ponto -> milhar PT, mas pode ser decimal PT sem virgula?
            # PT decimal SEMPRE usa virgula, entao so ponto = milhar.
            # Excepcao: 0.1182 (tabela) usa ponto como decimal? Verificar.
            parts = raw.split(".")
            if len(parts) == 2 and len(parts[1]) == 1:
                # 0.1, 0.5 etc: decimal curto
                nums.add(raw)
            elif len(parts) == 2 and len(parts[0]) == 1 and len(parts[1]) in (4, 3):
                # 0.1182: decimal de 4 casas (Tabela 3)
                nums.add(raw)
            else:
                nums.add(raw.replace(".", ""))
    return nums


def test_literal_numbers_present():
    en = EN_PATH.read_text()
    pt = PT_PATH.read_text()
    missing = []
    for n in LITERAL_NUMBERS:
        if n not in en:
            continue
        if n not in pt:
            missing.append(n)
    assert not missing, f"Literais ausentes na PT-BR: {sorted(missing)}"


def test_science_numbers_present():
    en = EN_PATH.read_text()
    pt = PT_PATH.read_text()
    en_nums = extract_canonical_numbers(en)
    pt_nums = extract_pt_numbers(pt)
    missing = [n for n in SCIENCE_NUMBERS if n not in en_nums and n not in LITERAL_NUMBERS]
    if missing:
        raise AssertionError(f"Numeros cientificos nao encontrados no EN: {missing}")
    pt_missing = [n for n in missing if n not in pt_nums]
    assert not pt_missing, f"Numeros cientificos ausentes na PT-BR: {pt_missing}"


def test_pt_has_no_english_placeholders():
    pt = PT_PATH.read_text()
    for bad in FORBIDDEN_PT:
        assert bad not in pt, f"Placeholder/marcador proibido na PT-BR: {bad!r}"


def test_pt_has_required_placeholders():
    pt = PT_PATH.read_text()
    pt_norm = normalize_markers(pt)
    missing = [
        m for m in REQUIRED_PLACEHOLDER_MARKERS
        if normalize_markers(m) not in pt_norm
    ]
    assert not missing, f"Placeholders obrigatorios ausentes na PT-BR: {missing}"


def test_pt_has_anti_overclaim_hedges():
    pt = PT_PATH.read_text()
    pt_norm = normalize_markers(pt)
    missing = [
        h for h in REQUIRED_HEDGES_PT
        if normalize_markers(h) not in pt_norm
    ]
    assert not missing, f"Ressenhas anti-overclaim ausentes na PT-BR: {missing}"


def test_pt_reference_count():
    pt = PT_PATH.read_text()
    refs = re.findall(r"^\d+\.\s+[A-Z]", pt, flags=re.MULTILINE)
    assert len(refs) >= 28, f"Referencias encontradas: {len(refs)} (esperado >=28)"


def test_pt_doi_count():
    pt = PT_PATH.read_text()
    dois = re.findall(r"10\.\d{4,9}/[^\s\)\]]+", pt)
    assert len(dois) >= 28, f"DOIs na PT-BR: {len(dois)} (esperado >=28)"


def test_pt_abstract_word_count():
    pt = PT_PATH.read_text()
    m = re.search(r"## Resumo\n(.*?)\n## 1\.", pt, flags=re.DOTALL)
    assert m, "Secao Resumo nao encontrada na PT-BR"
    abstract = m.group(1)
    abstract = re.sub(r"\*\*Palavras-chave(?: \([^)]*\))?:\*\*.*", "", abstract, flags=re.DOTALL)
    abstract = re.sub(r"[*_]", "", abstract)
    n = len(abstract.split())
    assert 200 <= n <= 250, f"Abstract PT-BR tem {n} palavras (limite Journal of Dentistry = 250)"


def test_pt_keyword_count():
    pt = PT_PATH.read_text()
    m = re.search(r"\*\*Palavras-chave(?: \([^)]*\))?:\*\*(.+)", pt)
    assert m, "Palavras-chave nao encontradas na PT-BR"
    kws = m.group(1)
    # Separar por ';'
    parts = [p.strip() for p in kws.split(";") if p.strip()]
    n = len(parts)
    assert 1 <= n <= 7, f"Palavras-chave PT-BR: {n} (esperado 1-7)"


def test_pt_section_structure():
    pt = PT_PATH.read_text()
    required = [
        "## Resumo",
        "## 1. Introdução",
        "## 2. Materiais e métodos",
        "## 3. Resultados",
        "## 4. Discussão",
        "## 5. Conclusão",
        "## Declarações",
        "## Referências",
    ]
    missing = [s for s in required if s not in pt]
    assert not missing, f"Seções ausentes na PT-BR: {missing}"


def test_pt_tables_present():
    pt = PT_PATH.read_text()
    tables = re.findall(r"\*\*Tabela \d+\.", pt)
    assert len(tables) >= 3, f"Tabelas PT-BR: {len(tables)} (esperado >=3)"


def test_pt_figures_present():
    pt = PT_PATH.read_text()
    figs = re.findall(r"Figura \d+\.", pt)
    assert len(figs) >= 3, f"Figuras PT-BR: {len(figs)} (esperado >=3)"


def test_pt_no_remaining_english_sentences():
    """Detecta frases em ingles residuals (>4 palavras consecutivas em ingles)."""
    pt = PT_PATH.read_text()
    # Palavras inglesas comuns que nao deveriam aparecer em corpo PT
    eng_words = {
        "the", "and", "with", "from", "were", "was", "this", "that",
        "which", "their", "there", "these", "have", "been", "for",
    }
    lines = pt.splitlines()
    suspicious = []
    for i, line in enumerate(lines, 1):
        if line.startswith("```") or "http" in line:
            continue
        words = re.findall(r"\b[a-zA-Z]+\b", line.lower())
        eng_count = sum(1 for w in words if w in eng_words)
        if eng_count >= 4:
            suspicious.append((i, line[:80]))
    assert not suspicious, (
        f"Linhas com possibles frases em ingles: {suspicious[:3]}"
    )


def test_pt_no_editorial_debris():
    """Nenhum debris de edicao (anotacoes do autor da traducao) no manuscrito.

    Falha historica: um fragmento de conversa do agente de traducao
    ('Let me do it properly.') entrou no corpo do manuscrito e nenhum gate
    anterior detectou.
    """
    pt = PT_PATH.read_text()
    debris = [
        "Let me", "let me", "wait.", "... wait", "TODO", "FIXME", "XXX",
        "PLACEHOLDER", "Lorem", "as an AI", "I will", "I'll ", "we will now",
        "here is", "Here's", "note to self", "check this", "fix this",
        "should be", "needs to be", "do it properly",
    ]
    found = [d for d in debris if d in pt]
    assert not found, f"Debris de edicao encontrado no manuscrito PT-BR: {found}"


# English function words that have no Portuguese counterpart in this text.
# Portuguese look-alikes (e, de, que, se, para, com, nao, mais, cada, outro,
# tambem, como, quando, onde, sem, no, so, pelo, pela) are deliberately absent.
ENGLISH_MARKERS = {
    "let", "me", "do", "it", "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "they", "them", "their", "she", "he", "you", "your",
    "can", "could", "should", "would", "will", "shall", "may", "might", "must",
    "this", "that", "these", "those", "which", "what", "when", "where", "who",
    "why", "how", "and", "but", "from", "with", "without", "into", "about",
    "also", "such", "very", "just", "only", "more", "most", "some", "any",
    "all", "each", "other", "another", "because", "between", "through",
    "before", "after", "while", "during", "against", "within", "under",
    "over", "above", "below", "again", "further", "then", "once", "here",
    "there", "now", "thus", "hence", "although", "though", "however",
    "therefore", "moreover", "furthermore", "respectively", "hypotheses",
    "children", "cohort", "model", "models", "calibration", "caries",
    "study", "results", "analysis", "manuscript", "authors", "review",
}


def test_pt_no_english_runs():
    """Nenhuma sequencia de >=3 marcadores consecutivos em ingles.

    Fecha a lacuna de test_pt_no_remaining_english_sentences, que so usava
    uma lista de 17 palavras e nao detectou o debris de edicao.
    """
    pt = PT_PATH.read_text().split("## Referências")[0]
    offenders = []
    for lineno, line in enumerate(pt.splitlines(), 1):
        if "http" in line or line.startswith("|"):
            continue
        words = re.findall(r"[A-Za-z]+", line)
        run = 0
        for word in words:
            if word.lower() in ENGLISH_MARKERS:
                run += 1
                if run >= 3:
                    offenders.append((lineno, " ".join(words[max(0, words.index(word) - 2):words.index(word) + 1])))
                    break
            else:
                run = 0
    assert not offenders, (
        f"Sequencias em ingles no corpo PT-BR: {offenders[:5]}"
    )


def test_pt_rendered_structure():
    """Estrutura do DOCX renderizado: o gate que faltava.

    O resumo e as palavras-chave precisam virar paragrafos separados no DOCX.
    Uma linha em branco faltando entre o resumo e as palavras-chave faz o
    pandoc fundir as duas em um unico paragrafo, e finalize_docx.py quebra com
    IndexError. Este gate pega a causa, nao o sintoma.
    """
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory(prefix="odonto_ptbr_struct_") as tmp:
        draft = Path(tmp) / "draft.docx"
        proc = subprocess.run(
            [
                "pandoc", str(PT_PATH),
                "--from", "markdown+pipe_tables+implicit_figures",
                "--to", "docx",
                "--output", str(draft),
                "--resource-path", str(PT_PATH.parent),
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"pandoc falhou: {proc.stderr[:300]}"
        try:
            from docx import Document
        except ImportError:  # pragma: no cover
            raise AssertionError("python-docx ausente: gate de estrutura nao pode rodar")

        paragraphs = Document(draft).paragraphs
        texts = [p.text for p in paragraphs]
        assert texts[1].strip() == "Resumo", f"paragrafo 1 deveria ser 'Resumo', veio {texts[1][:40]!r}"
        for index, label in enumerate(
            ("Objetivos:", "Métodos:", "Resultados:", "Conclusões:"), start=2
        ):
            assert texts[index].startswith(label), (
                f"paragrafo {index} deveria comecar com {label!r}, veio {texts[index][:40]!r}"
            )
        assert texts[6].startswith("Palavras-chave"), (
            "paragrafo 6 deveria ser a linha de palavras-chave; "
            f"veio {texts[6][:40]!r} (faltou linha em branco no Markdown?)"
        )
        # Uma runenglish de 3 palavras no DOCX tambem indica traducao incompleta.
        joined = " ".join(texts)
        assert "Let me" not in joined and "do it properly" not in joined


# --- Locale-aware number tokenizer -------------------------------------------
# EN uses '.' as the decimal separator and ',' as the thousands separator;
# PT-BR does the opposite. A single locale-agnostic regex misclassifies
# "0.166" as 166 (a 3-digit tail) and shreds "2,504" into fragments, so the
# separator roles are declared explicitly instead of guessed. canon() is
# unit-tested in test_number_tokenizer_units before any comparison relies on it.

NUM_TOKEN = re.compile(r"\d+(?:[.,]\d+)*")


def canon(token: str, decimal_sep: str) -> str:
    """Normalise one numeric token to a locale-independent canonical string."""
    thousands = "," if decimal_sep == "." else "."
    if thousands in token:
        parts = token.split(thousands)
        # 2,504 / 2.504 / 1,160 / 1.000 -> thousands grouping
        if all(len(p) == 3 for p in parts[1:]) and 1 <= len(parts[0]) <= 3:
            return "".join(parts)
    parts = token.split(decimal_sep)
    if len(parts) == 2:
        return parts[0] + "." + parts[1]
    return token


def scan_numbers(text: str, decimal_sep: str) -> set[str]:
    return {canon(m.group(0), decimal_sep) for m in NUM_TOKEN.finditer(text)}


def strip_nonprose(text: str) -> str:
    """Remove citations, links, DOIs and code spans before counting numbers.

    Reference-list page ranges and DOIs are identical in both manuscripts, so
    they are excluded only to keep a wrong scientific value from hiding inside
    a citation such as [16,17].
    """
    text = re.sub(r"!?\[[^\]]*\]\([^)]*\)", " ", text)   # links and images
    text = re.sub(r"\[\d+(?:\s*[,\u2013-]\s*\d+)*\]", " ", text)  # citations [16,17]
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"10\.\d{4,9}/\S+", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    return text


# Values legitimately present on one side only. Documented rather than hidden:
# anything added here must be justified in the commit message.
NUMERIC_EXEMPTIONS = {
    # pandoc image width attributes differ per figure between the two files
    "6.8", "6.7",
    # PT-BR spells the notebook version as v1.3.2 in prose; the EN uses the
    # same string, but 1.3 alone is a side-effect of the EN tokenizer seeing
    # "v1.3.2" as two decimal tokens when the section headings are numbered.
    "1.3", "1.6", "1.9",
    "2.1", "2.2", "2.3", "2.4", "2.5",
    "3.1", "3.2", "3.3",
    "4.1", "4.2", "4.3", "4.4", "4.5",
}


def test_number_tokenizer_units():
    """The canonicaliser itself must be correct before it is trusted."""
    cases = [
        ("2,504", ".", "2504"), ("0.166", ".", "0.166"), ("1,000", ".", "1000"),
        ("1,160", ".", "1160"), ("0.0004", ".", "0.0004"), ("0.00610", ".", "0.00610"),
        ("1.3.2", ".", "1.3.2"), ("8.33", ".", "8.33"),
        ("2.504", ",", "2504"), ("0,166", ",", "0.166"), ("1.000", ",", "1000"),
        ("1.160", ",", "1160"), ("0,0004", ",", "0.0004"), ("0,00610", ",", "0.00610"),
        ("1.6.1", ",", "1.6.1"), ("8,33", ",", "8.33"),
        ("2504", ".", "2504"), ("996", ".", "996"), ("20260930", ".", "20260930"),
    ]
    bad = [(t, d, e, canon(t, d)) for t, d, e in cases if canon(t, d) != e]
    assert not bad, f"tokenizador com defeito: {bad}"
    pairs = [("2,504", ".", "2.504", ","), ("1,160", ".", "1.160", ","),
             ("0.166", ".", "0,166", ","), ("0.00610", ".", "0,00610", ","),
             ("1,000", ".", "1.000", ",")]
    bad = [(a, b) for a, da, b, db in pairs if canon(a, da) != canon(b, db)]
    assert not bad, f"paridade de locale quebrada: {bad}"


def test_numeric_parity_strict():
    """Nenhum numero inventado, alterado ou perdido na traducao.

    test_science_numbers_present so checa presenca: trocar 0,737 por 0,799 em
    um trecho deixaria 0,737 presente em outro e passaria. Aqui os conjuntos
    de numeros canonicos dos dois manuscritos precisam ser iguais.
    """
    en = scan_numbers(strip_nonprose(EN_PATH.read_text()), ".")
    pt = scan_numbers(strip_nonprose(PT_PATH.read_text()), ",")
    only_pt = {n for n in (pt - en) if n not in NUMERIC_EXEMPTIONS}
    only_en = {n for n in (en - pt) if n not in NUMERIC_EXEMPTIONS}
    assert not only_pt, f"numeros na PT-BR que nao existem no EN (inventados/alterados): {sorted(only_pt)}"
    assert not only_en, f"numeros do EN ausentes na PT-BR: {sorted(only_en)}"


def test_doi_parity_strict():
    """Conjunto exato de DOIs, nao apenas a contagem >= 28."""
    en = set(re.findall(r"10\.\d{4,9}/[^\s\)\]]+", EN_PATH.read_text()))
    pt = set(re.findall(r"10\.\d{4,9}/[^\s\)\]]+", PT_PATH.read_text()))
    assert not (pt - en), f"DOIs da PT-BR ausentes no EN: {sorted(pt - en)}"
    assert not (en - pt), f"DOIs do EN ausentes na PT-BR: {sorted(en - pt)}"


def test_hedge_covers_conclusion():
    """As ressalhas anti-overclaim precisam estar onde o leitor decide.

    Presenca em qualquer lugar do arquivo e insuficiente: uma unica ocorrencia
    isolada passaria mesmo que a conclusao afirmasse certeza.
    """
    pt = PT_PATH.read_text()
    conclusion = re.search(r"## 5\. Conclusão\n(.*?)\n## Declarações", pt, flags=re.S)
    assert conclusion, "secao de conclusao nao encontrada"
    block = normalize_markers(conclusion.group(1))
    for hedge in ("interna", "exploratoria", "incerta", "imperfeita",
                  "externa", "nao esta pronta"):
        assert normalize_markers(hedge) in block, (
            f"ressalva {hedge!r} ausente da conclusao PT-BR"
        )


def main() -> int:
    tests = [
        test_number_tokenizer_units,
        test_literal_numbers_present,
        test_science_numbers_present,
        test_numeric_parity_strict,
        test_doi_parity_strict,
        test_hedge_covers_conclusion,
        test_pt_has_no_english_placeholders,
        test_pt_has_required_placeholders,
        test_pt_has_anti_overclaim_hedges,
        test_pt_reference_count,
        test_pt_doi_count,
        test_pt_abstract_word_count,
        test_pt_keyword_count,
        test_pt_section_structure,
        test_pt_tables_present,
        test_pt_figures_present,
        test_pt_no_remaining_english_sentences,
        test_pt_no_editorial_debris,
        test_pt_no_english_runs,
        test_pt_rendered_structure,
    ]
    passed = failed = 0
    for fn in tests:
        name = fn.__name__
        try:
            fn()
            print(f"  \033[32mPASS\033[0m {name}")
            passed += 1
        except AssertionError as e:
            print(f"  \033[31mFAIL\033[0m {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  \033[31mERROR\033[0m {name}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{len(tests)} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
