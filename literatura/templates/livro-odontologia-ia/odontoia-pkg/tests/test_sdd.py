"""
Testes para o módulo sdd/ (spec, validator)
"""

import pytest

from odontoia.sdd import spec, get_spec, validate_spec, list_specs
from odontoia.sdd.validator import SpecVerifier, SpecError


class TestSpecDecorator:
    """Testes para o decorador @spec."""

    def test_spec_decorator_basic(self):
        """@spec deve anexar especificação à função."""
        @spec(
            problem="Classificar lesão bucal",
            input="Imagem radiográfica 256x256",
            output="Classe predita (0: saudável, 1: cárie, 2: lesão)",
            criteria=["accuracy > 0.80"],
        )
        def classify(img):
            """Classifica lesão bucal."""
            return 0

        spec_data = get_spec(classify)
        assert spec_data is not None
        assert spec_data["problem"] == "Classificar lesão bucal"
        assert len(spec_data["criteria"]) == 1

    def test_spec_registry(self):
        """@spec deve registrar a função no registro global."""
        @spec(
            problem="Segmentar dentes",
            input="Radiografia panorâmica",
            output="Máscara de segmentação",
            criteria=["dice > 0.85"],
            category="segmentacao",
        )
        def segment_dentes(img):
            return img

        specs = list_specs(category="segmentacao")
        assert len(specs) >= 1
        found = any("segment_dentes" in name for name in specs)
        assert found

    def test_get_spec_no_decorator(self):
        """get_spec para função não decorada deve retornar None."""
        def funcao_sem_spec():
            pass
        assert get_spec(funcao_sem_spec) is None


class TestValidateSpec:
    """Testes para validação de especificações."""

    def test_valid_spec(self):
        """validate_spec deve retornar True para spec válida."""
        @spec(
            problem="Teste",
            input="dados",
            output="resultado",
            criteria=["metric > 0.5"],
        )
        def func_valida():
            """Função com docstring."""
            pass

        result = validate_spec(func_valida)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_spec_missing_fields(self):
        """validate_spec deve detectar campos vazios."""
        @spec(
            problem="",
            input="dados",
            output="resultado",
            criteria=["metric > 0.5"],
        )
        def func_campo_vazio():
            pass

        result = validate_spec(func_campo_vazio)
        assert result["valid"] is False
        assert any("problem" in e for e in result["errors"])

    def test_spec_empty_criteria(self):
        """validate_spec deve detectar critérios vazios."""
        @spec(
            problem="Teste",
            input="dados",
            output="resultado",
            criteria=[],
        )
        def func_criteria_vazia():
            pass

        result = validate_spec(func_criteria_vazia)
        assert result["valid"] is False

    def test_spec_no_decorator(self):
        """validate_spec para função sem decorator deve retornar False."""
        def func_sem_spec():
            pass
        result = validate_spec(func_sem_spec)
        assert result["valid"] is False
        assert len(result["errors"]) == 1


class TestSpecVerifier:
    """Testes para SpecVerifier."""

    def test_verify_valid_spec(self):
        """SpecVerifier.verify deve aprovar função correta."""
        @spec(
            problem="Soma dois números",
            input="dois inteiros",
            output="inteiro soma",
            criteria=["retorna_int"],
        )
        def add(a, b):
            """Soma dois números."""
            return a + b

        verifier = SpecVerifier()
        result = verifier.verify(add, 3, 4)
        assert result.valid

    def test_verify_no_spec(self):
        """SpecVerifier.verify para função sem spec deve retornar inválido."""
        def func_sem_spec(x):
            return x

        verifier = SpecVerifier()
        result = verifier.verify(func_sem_spec, 10)
        assert not result.valid
        assert len(result.errors) > 0

    def test_verify_strict_mode(self):
        """SpecVerifier com strict_mode=True deve levantar exceção."""
        def func_sem_spec(x):
            return x

        verifier = SpecVerifier(strict_mode=True)
        with pytest.raises(SpecError):
            verifier.verify(func_sem_spec, 10)

    def test_verify_summary(self):
        """SpecVerifier.summary deve retornar resumo correto."""
        @spec(
            problem="Teste",
            input="x",
            output="x",
            criteria=["ok"],
        )
        def func_ok(x):
            return x

        verifier = SpecVerifier()
        verifier.verify(func_ok, 1)
        summary = verifier.summary()
        assert summary["total"] == 1
        assert summary["passed"] == 1

    def test_verify_with_output_check(self):
        """SpecVerifier deve verificar saída com test_output."""
        @spec(
            problem="Multiplicar",
            input="dois números",
            output="número",
            criteria=["correto"],
        )
        def multiply(a, b):
            return a * b

        verifier = SpecVerifier()
        result = verifier.verify(multiply, 3, 4, test_output=12)
        assert result.valid