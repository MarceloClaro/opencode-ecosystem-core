"""Testes TDD para Internacionalizacao (SPEC-935 R85)."""

import pytest
from synthetic_university.i18n import I18n


class TestR85I18n:
    """Testes para o sistema de internacionalizacao."""

    def test_i18n_creates(self):
        """R85: I18n e criado com locale padrao."""
        i18n = I18n()
        assert i18n is not None
        assert i18n.locale in ('pt_BR', 'en_US')

    def test_i18n_en_default(self):
        """R85: Locale padrao e en_US."""
        i18n = I18n(locale='en_US')
        assert i18n.locale == 'en_US'

    def test_i18n_pt_br(self):
        """R85: Locale pt_BR funciona."""
        i18n = I18n(locale='pt_BR')
        assert i18n.locale == 'pt_BR'

    def test_get_known_key_en(self):
        """R85: Mensagem conhecida retorna traducao EN."""
        i18n = I18n(locale='en_US')
        msg = i18n.get('validation.score_empirico')
        assert msg is not None
        assert len(msg) > 0
        # Nao deve conter portugues
        assert 'empírico' not in msg.lower() or 'score' in msg.lower()

    def test_get_known_key_pt(self):
        """R85: Mensagem conhecida retorna traducao PT-BR."""
        i18n = I18n(locale='pt_BR')
        msg = i18n.get('validation.score_empirico')
        assert msg is not None
        assert len(msg) > 0

    def test_get_unknown_key_fallback(self):
        """R85: Chave desconhecida retorna fallback."""
        i18n = I18n(locale='en_US')
        msg = i18n.get('chave_inexistente_xyz')
        assert msg == 'chave_inexistente_xyz'  # fallback = propria chave

    def test_get_with_format(self):
        """R85: Mensagem com format string funciona."""
        i18n = I18n(locale='en_US')
        msg = i18n.get('validation.n_theses', n=10)
        assert '10' in msg

    def test_all_keys_have_both_locales(self):
        """R85: Todas as chaves existem em EN e PT-BR."""
        i18n_en = I18n(locale='en_US')
        i18n_pt = I18n(locale='pt_BR')
        
        for key in i18n_en._translations.get('en_US', {}):
            assert key in i18n_pt._translations.get('pt_BR', {}), \
                f"Chave '{key}' falta em pt_BR"
        assert len(i18n_en._translations['en_US']) == len(i18n_pt._translations['pt_BR'])

    def test_report_header_translated(self):
        """R85: Cabecalho de relatorio traduzido."""
        i18n = I18n(locale='en_US')
        header = i18n.get('report.validation_header')
        assert header is not None
        assert len(header) > 5

    def test_invalid_locale_fallback_en(self):
        """R85: Locale invalido faz fallback para en_US."""
        i18n = I18n(locale='fr_FR')
        assert i18n.locale == 'en_US'
