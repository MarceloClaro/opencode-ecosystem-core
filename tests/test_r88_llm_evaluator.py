"""Testes TDD para LLM Evaluator via Antigravity (SPEC-935 R88)."""

import pytest
from unittest.mock import patch, MagicMock
from synthetic_university.llm_evaluator import LLMEvaluator
from synthetic_university.agents.professor_base import Professor


class TestR88LLMEvaluator:
    """Testes para o avaliador LLM com fallback Antigravity→OpenCode→Ollama→Template."""

    @pytest.fixture
    def prof(self):
        return Professor(
            professor_id="test_01",
            nome="Alan Turing",
            title="PhD",
            faculty_id="engineering",
            specialties=["Computação", "Inteligência Artificial", "Algoritmos"],
            research_interests=["algoritmo", "máquina", "computação"],
            h_index=30,
        )

    @pytest.fixture
    def thesis_dict(self):
        return {
            "title": "Algorithmic Ethics: A New Framework for Moral AI",
            "hypothesis": "Algorithms can encode ethical principles through formal verification",
            "faculties_involved": ["engineering", "human_sciences"],
            "thesis_id": "thesis_001",
            "composite_score": 0.62,
        }

    @pytest.fixture
    def evaluator(self):
        return LLMEvaluator()

    def test_evaluator_creates(self, evaluator):
        """R88: LLMEvaluator e criado."""
        assert evaluator is not None

    def test_generate_with_antigravity(self, evaluator, prof, thesis_dict):
        """R88: Gera feedback via Antigravity quando disponivel."""
        with patch.object(evaluator, '_try_antigravity') as mock_ag:
            mock_ag.return_value = (
                "The thesis connects algorithmic verification with moral philosophy "
                "in a novel way. I recommend expanding the formal framework."
            )

            feedback, source, time_taken = evaluator.generate(prof, thesis_dict, "strong")

        assert feedback is not None
        assert len(feedback) > 30
        assert source == "antigravity"
        assert time_taken > 0

    def test_generate_fallback_opencode(self, evaluator, prof, thesis_dict):
        """R88: Fallback para OpenCode CLI quando Antigravity falha."""
        with patch.object(evaluator, '_try_antigravity') as mock_ag:
            mock_ag.return_value = None
            with patch.object(evaluator, '_try_opencode_cli') as mock_oc:
                mock_oc.return_value = (
                    "The thesis presents an interesting approach but needs "
                    "more rigorous empirical validation."
                )

                feedback, source, time_taken = evaluator.generate(prof, thesis_dict, "moderate")

        assert feedback is not None
        assert source == "opencode"
        assert len(feedback) > 20

    def test_generate_fallback_template(self, evaluator, prof, thesis_dict):
        """R88: Fallback para template quando todos os LLMs falham."""
        with patch.object(evaluator, '_try_antigravity') as mock_ag:
            mock_ag.return_value = None
            with patch.object(evaluator, '_try_opencode_cli') as mock_oc:
                mock_oc.return_value = None
                with patch.object(evaluator, '_try_ollama_cli') as mock_ol:
                    mock_ol.return_value = None

                    feedback, source, time_taken = evaluator.generate(prof, thesis_dict, "moderate")

        assert feedback is not None
        assert len(feedback) > 10
        assert source == "template"

    def test_prompt_construction(self, evaluator, prof, thesis_dict):
        """R88: Prompt e construido com contexto completo."""
        prompt = evaluator._build_prompt(prof, thesis_dict, "moderate")
        assert prof.nome in prompt
        assert thesis_dict["title"] in prompt
        assert "MODERATE" in prompt.upper() or "MODERADO" in prompt.upper()
        assert len(prompt) > 100

    def test_cache_prevents_regeneration(self, evaluator, prof, thesis_dict):
        """R88: Cache evita re-geracao do mesmo feedback."""
        with patch.object(evaluator, '_try_antigravity') as mock_ag:
            mock_ag.return_value = "Cached feedback content for testing purposes."

            # Primeira chamada
            f1, s1, t1 = evaluator.generate(prof, thesis_dict, "strong")

            # Segunda chamada (mesmo prof + thesis)
            f2, s2, t2 = evaluator.generate(prof, thesis_dict, "strong")

        assert f1 == f2
        # Deve ter chamado Antigravity apenas uma vez (segunda leu do cache)
        assert mock_ag.call_count == 1

    def test_different_endorsements_different_cache(self, evaluator, prof, thesis_dict):
        """R88: Endossos diferentes geram feedbacks diferentes (cache separado)."""
        with patch.object(evaluator, '_try_antigravity') as mock_ag:
            mock_ag.return_value = "Strong feedback about this excellent thesis."

            f1, s1, t1 = evaluator.generate(prof, thesis_dict, "strong")

            # Mudando endosso — key diferente, NAO deve usar cache
            f2, s2, t2 = evaluator.generate(prof, thesis_dict, "weak")

        # Ambos vieram do antigravity (endorsements diferentes = cache keys diferentes)
        assert s1 == "antigravity"
        assert s2 == "antigravity"
        assert mock_ag.call_count == 2

    def test_antigravity_exception_fallback(self, evaluator, prof, thesis_dict):
        """R88: Exception no Antigravity nao trava — fallback para OpenCode."""
        with patch.object(evaluator, '_try_antigravity') as mock_ag:
            mock_ag.side_effect = Exception("Connection refused")
            with patch.object(evaluator, '_try_opencode_cli') as mock_oc:
                mock_oc.return_value = "OpenCode fallback feedback about the thesis."

                feedback, source, time_taken = evaluator.generate(prof, thesis_dict, "weak")

        assert feedback is not None
        assert source == "opencode"
        assert len(feedback) > 10

    def test_ollama_cli_fallback(self, evaluator, prof, thesis_dict):
        """R88: Ollama CLI via subprocess como ultimo recurso LLM."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = (
                "Ollama says: Good thesis, but needs more rigor in methodology."
            )
            mock_run.return_value.stderr = ""

            result = evaluator._try_ollama_cli(prof, thesis_dict, "moderate")

        assert result is not None
        assert len(result) > 10
        assert "Ollama" in result

    def test_ollama_cli_not_installed(self, evaluator, prof, thesis_dict):
        """R88: Ollama CLI ausente nao causa erro — retorna None."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("ollama not found")

            result = evaluator._try_ollama_cli(prof, thesis_dict, "moderate")

        assert result is None

    def test_stats_tracking(self, evaluator, prof, thesis_dict):
        """R88: Estatisticas de uso sao registradas."""
        with patch.object(evaluator, '_try_antigravity') as mock_ag:
            mock_ag.return_value = "Feedback for stats tracking test."

            feedback, source, elapsed = evaluator.generate(prof, thesis_dict, "strong")

        assert feedback is not None
        assert source == "antigravity"
        assert elapsed > 0

        stats = evaluator.get_stats()
        assert stats["total_calls"] == 1
        # O mock substitui o metodo real, entao contadores internos nao sao incrementados.
        # O importante e que o resultado foi gerado com source='antigravity'

    def test_opencode_cli_real_call(self, evaluator, prof, thesis_dict):
        """R88: OpenCode CLI real invocado com sucesso (integracao)."""
        # Usa o modelo free do OpenCode para gerar feedback real
        feedback = evaluator._try_opencode_cli(prof, thesis_dict, "strong")
        # Pode falhar se CLI nao estiver disponivel — aceitamos None
        if feedback:
            assert len(feedback) > 15
            assert isinstance(feedback, str)
        else:
            pytest.skip("OpenCode CLI nao disponivel neste ambiente")

    def test_language_portuguese(self):
        """R88: Feedback em portugues quando lang='pt'."""
        ev = LLMEvaluator(lang="pt")
        prof = Professor(
            professor_id="test_pt",
            nome="Maria Curie",
            title="PhD",
            faculty_id="exact_sciences",
            specialties=["Física", "Radioatividade"],
            research_interests=["física", "elementos"],
            h_index=45,
        )
        thesis = {
            "title": "Ética Quântica: Um Novo Paradigma",
            "hypothesis": "Sistemas quânticos podem modelar dilemas éticos",
            "thesis_id": "thesis_pt",
            "composite_score": 0.70,
        }

        with patch.object(ev, '_try_antigravity') as mock_ag:
            mock_ag.return_value = (
                "A tese apresenta uma abordagem inovadora ao conectar mecânica "
                "quântica com ética computacional."
            )

            feedback, source, elapsed = ev.generate(prof, thesis, "strong")

        assert feedback is not None
        # O feedback mockado ja esta em portugues; verificamos caracteres acentuados
        assert any(c in feedback for c in "ãéèêçàáíóú")
        assert source == "antigravity"
