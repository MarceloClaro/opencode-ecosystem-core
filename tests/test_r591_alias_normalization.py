"""
Testes R-976.22: normalização tolerante de aliases editoriais (ciclo R593).

Cobre variações de barra, parênteses, acento, hífen e caixa mista que o
get_profile() não resolvia antes da normalização (R-976.22), ex.:

    "educação/pucrs"          -> Educação (PUCRS)
    "rbe/anped"               -> Revista Brasileira de Educação
    "seqüência (ufsc)"        -> Seqüência (UFSC)
    "npj/quantum/information" -> npj Quantum Information

Regra SDD/TDD estrita: estes testes devem falhar (RED) antes da
implementação da normalização e passar (GREEN) depois.
"""
import re
import unicodedata

import pytest

from mirofish.social import (
    EDITORIAL_PROFILES,
    get_profile,
    normalize_institution_alias,
    resolve_institution_name,
)


def norm(v: str) -> str:
    """Referência canônica da normalização esperada (R-976.22)."""
    if not v:
        return ""
    decomposed = unicodedata.normalize("NFD", v.lower())
    no_accents = "".join(
        c for c in decomposed if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", no_accents)).strip()


def profile_for(expected: str):
    """Resolve o OBJETO perfil esperado: chave canônica exata ou cujo
    journal expandido comece com o rótulo esperado (ex.: chave curta
    'npj Quantum Information' vs journal 'npj Quantum Information (Nature Portfolio)')."""
    if expected in EDITORIAL_PROFILES:
        return EDITORIAL_PROFILES[expected]
    for p in EDITORIAL_PROFILES.values():
        if p.journal == expected or p.journal.startswith(expected):
            return p
    return None


# --------------------------------------------------------------------------
# 1. Função pública de normalização
# --------------------------------------------------------------------------
class TestNormalizeInstitutionAlias:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Educação / PUCRS", "educacao pucrs"),
            ("RBE/ANPEd", "rbe anped"),
            ("Seqüência (UFSC)", "sequencia ufsc"),
            ("npj/quantum/information", "npj quantum information"),
            ("Computers & Education", "computers education"),
            ("Educação & Sociedade", "educacao sociedade"),
            ("Revista Direito e Práxis (UERJ)", "revista direito e praxis uerj"),
            ("  Suprema /  STF  ", "suprema stf"),
            ("Direito-GV", "direito gv"),
            ("Práxis Educativa", "praxis educativa"),
            ("", ""),
            (None, ""),
        ],
    )
    def test_normalized_form(self, raw, expected):
        assert normalize_institution_alias(raw) == expected
        assert norm(raw) == expected  # referência canônica idêntica


# --------------------------------------------------------------------------
# 2. get_profile resolve variações antes não resolvidas (RED original)
# --------------------------------------------------------------------------
class TestGetProfileFuzzyVariants:
    @pytest.mark.parametrize(
        "raw,expected_journal",
        [
            # barras / parênteses / acento / hífen / caixa mista — falhavam antes
            ("educação/pucrs", "Educação (PUCRS)"),
            ("Educação / PUCRS", "Educação (PUCRS)"),
            ("rbe/anped", "Revista Brasileira de Educação"),
            ("RBE/ANPEd", "Revista Brasileira de Educação"),
            ("seqüência (ufsc)", "Seqüência (UFSC)"),
            ("Seqüência (UFSC)", "Seqüência (UFSC)"),
            ("Sequência (UFSC)", "Seqüência (UFSC)"),
            ("npj/quantum/information", "npj Quantum Information"),
            ("Suprema / STF", "Suprema (STF)"),
            ("Direito e Práxis (UERJ)", "Revista Direito e Práxis"),
            ("Direito-GV", "Revista Direito GV"),
        ],
    )
    def test_fuzzy_variants_resolve(self, raw, expected_journal):
        profile = get_profile(raw)
        expected = profile_for(expected_journal)
        assert expected is not None, f"perfil esperado não encontrado: {expected_journal}"
        assert profile is expected, f"resolveu {profile.journal if profile else None!r}, esperado {expected_journal!r}"


# --------------------------------------------------------------------------
# 3. Compatibilidade: nada que resolvia antes pode deixar de resolver
# --------------------------------------------------------------------------
class TestGetProfileBackwardCompat:
    @pytest.mark.parametrize(
        "raw,expected_journal",
        [
            # chaves canônicas exatas
            ("Revista Brasileira de Educação", "Revista Brasileira de Educação"),
            ("Educação & Sociedade", "Educação & Sociedade"),
            ("npj Quantum Information", "npj Quantum Information"),
            ("Revista Direito GV", "Revista Direito GV"),
            ("Revista Direito e Práxis", "Revista Direito e Práxis"),
            ("Seqüência (UFSC)", "Seqüência (UFSC)"),
            ("Suprema (STF)", "Suprema (STF)"),
            ("Quantum Science and Technology", "Quantum Science and Technology"),
            # aliases históricos
            ("educacao pucrs", "Educação (PUCRS)"),
            ("rbe", "Revista Brasileira de Educação"),
            ("sequencia", "Seqüência (UFSC)"),
            ("seqüência", "Seqüência (UFSC)"),
            ("npjqi", "npj Quantum Information"),
            ("npj qi", "npj Quantum Information"),
            ("qip", "Quantum Information Processing"),
            ("tqe", "IEEE Transactions on Quantum Engineering"),
            ("tqc", "ACM Transactions on Quantum Computing"),
            ("jod", "Journal of Dentistry"),
            ("jbi", "Journal of Biomedical Informatics"),
            ("suprema stf", "Suprema (STF)"),
            ("direitogv", "Revista Direito GV"),
        ],
    )
    def test_backward_compat(self, raw, expected_journal):
        profile = get_profile(raw)
        expected = profile_for(expected_journal)
        assert expected is not None, f"perfil esperado não encontrado: {expected_journal}"
        assert profile is expected, f"quebrou compatibilidade {raw!r}: {profile.journal if profile else None!r}"

    def test_none_and_unknown(self):
        assert get_profile(None) is None
        assert get_profile("") is None
        assert get_profile("periódico inexistente xyz") is None
        assert get_profile("   ") is None

    @pytest.mark.parametrize(
        "raw,expected_journal",
        [
            # códigos curtos continuam resolvendo pelo alias exato
            ("eit", "Education and Information Technologies"),
            ("ire", "International Review of Education"),
            ("mia", "Medical Image Analysis"),
            ("coi", "Clinical Oral Investigations"),
            ("ees", "Educação & Sociedade"),
            ("reed", "Revista de Estudos Empíricos em Direito"),
        ],
    )
    def test_short_codes_still_resolve(self, raw, expected_journal):
        profile = get_profile(raw)
        expected = profile_for(expected_journal)
        assert expected is not None
        assert profile is expected

    @pytest.mark.parametrize(
        "raw,forbidden_journal",
        [
            # anti-falso-positivo: 'eit' NÃO pode casar por substring em 'direito'
            ("Direito e Práxis (UERJ)", "Education and Information Technologies"),
            ("direito", "Education and Information Technologies"),
            # 'ireito' dentro de nome real NÃO pode casar 'ire' (IRE) por substring
            ("revista de direito administrativo", "International Review of Education"),
        ],
    )
    def test_no_short_code_substring_false_positive(self, raw, forbidden_journal):
        profile = get_profile(raw)
        assert profile is not None
        forbidden = profile_for(forbidden_journal)
        assert profile is not forbidden, (
            f"falso positivo: {raw!r} resolveu {profile.journal!r}"
        )


# --------------------------------------------------------------------------
# 4. Integração com a banca (resolve_institution_name)
# --------------------------------------------------------------------------
class TestResolveInstitutionNameIntegration:
    @pytest.mark.parametrize(
        "raw,expected_suffix",
        [
            ("educação/pucrs", "Educação (PUCRS)"),
            ("rbe/anped", "Revista Brasileira de Educação"),
            ("seqüência (ufsc)", "Seqüência (UFSC)"),
            ("revista direito e práxis", "Revista Direito e Práxis"),
            ("suprema", "Suprema (STF)"),
        ],
    )
    def test_banca_label_resolves(self, raw, expected_suffix):
        label = resolve_institution_name(raw)
        expected_profile = profile_for(expected_suffix)
        assert expected_profile is not None
        assert label == f"{expected_profile.journal} (Qualis A1 — simulação)"

    def test_unknown_returns_none(self):
        assert resolve_institution_name("nothing here") is None
        assert resolve_institution_name(None) is None
        assert resolve_institution_name("") is None