"""Testes TDD para Visual Abstract Generation via Antigravity Image (SPEC-935 R90)."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from synthetic_university.visual_abstract import VisualAbstractGenerator


class TestR90VisualAbstract:
    """Testes para geracao de abstracts visuais com Antigravity Image."""

    @pytest.fixture
    def generator(self, tmp_path):
        out_dir = str(tmp_path / "visual_abstracts")
        return VisualAbstractGenerator(output_dir=out_dir)

    @pytest.fixture
    def top_theses(self):
        return [
            {
                "thesis_id": "thesis_001",
                "title": "Quantum Ethics: A Framework for Moral AI Systems",
                "hypothesis": "Quantum principles can model ethical decision-making",
                "composite_score": 0.92,
                "faculties_involved": ["engineering", "human_sciences"],
            },
            {
                "thesis_id": "thesis_002",
                "title": "Deep Learning for Tropical Disease Diagnosis",
                "hypothesis": "CNNs can diagnose tropical diseases from medical imaging",
                "composite_score": 0.85,
                "faculties_involved": ["health_sciences", "engineering"],
            },
            {
                "thesis_id": "thesis_003",
                "title": "Algorithmic Fairness in Criminal Justice",
                "hypothesis": "Formal verification ensures fairness in sentencing algorithms",
                "composite_score": 0.78,
                "faculties_involved": ["human_sciences", "law"],
            },
        ]

    def test_generator_creates(self, generator):
        """R90: VisualAbstractGenerator e criado."""
        assert generator is not None
        assert os.path.exists(generator.output_dir)

    def test_generate_visual(self, generator, top_theses):
        """R90: Gera visual (figura academica) para uma tese."""
        with patch.object(generator, '_generate_image') as mock_gen:
            mock_gen.return_value = {
                "thesis_id": "thesis_001",
                "image_path": "/path/to/quantum_ethics.png",
                "description": "Diagrama conceitual: Etica Quantica para IA Moral",
                "source": "antigravity_image",
                "success": True,
            }

            result = generator.generate(top_theses[0])

        assert result is not None
        assert result["success"] is True
        assert result["source"] == "antigravity_image"
        assert "image_path" in result

    def test_generate_all_top(self, generator, top_theses):
        """R90: Gera visuals para todas as top teses."""
        with patch.object(generator, '_generate_image') as mock_gen:
            mock_gen.return_value = {
                "thesis_id": "test",
                "image_path": "/path/to/img.png",
                "description": "Test figure",
                "source": "antigravity_image",
                "success": True,
            }

            results = generator.generate_all(top_theses)

        assert len(results) == 3
        assert all(r["success"] for r in results)

    def test_cache_prevents_regeneration(self, generator, top_theses):
        """R90: Cache evita re-geracao da mesma imagem."""
        with patch.object(generator, '_generate_image') as mock_gen:
            mock_gen.return_value = {
                "thesis_id": "thesis_001",
                "image_path": "/path/to/img.png",
                "source": "antigravity_image",
                "success": True,
            }

            # Primeira geracao
            generator.generate(top_theses[0])
            # Segunda geracao (mesma tese)
            generator.generate(top_theses[0])

        # Deve ter chamado _generate_image apenas uma vez
        assert mock_gen.call_count == 1

    def test_cache_by_content_hash(self, generator):
        """R90: Cache usa hash do conteudo da tese."""
        thesis_a = {
            "thesis_id": "t1",
            "title": "Quantum Ethics",
            "hypothesis": "QH1",
            "composite_score": 0.9,
        }
        thesis_b = {
            "thesis_id": "t2",
            "title": "AI Ethics",
            "hypothesis": "QH2",
            "composite_score": 0.8,
        }

        with patch.object(generator, '_generate_image') as mock_gen:
            mock_gen.return_value = {
                "success": True,
                "image_path": "/path/img.png",
                "source": "antigravity_image",
            }

            generator.generate(thesis_a)
            generator.generate(thesis_b)

        # Teses diferentes = 2 chamadas
        assert mock_gen.call_count == 2

    def test_fallback_svg_diagram(self, generator, top_theses):
        """R90: Fallback para diagrama SVG quando image gen falha."""
        with patch.object(generator, '_generate_image') as mock_gen:
            mock_gen.side_effect = RuntimeError("API unavailable")

            result = generator.generate(top_theses[0])

        assert result is not None
        assert result["success"] is True
        assert result["source"] == "svg_fallback"
        assert result["image_path"].endswith(".svg")

    def test_output_structure(self, generator, top_theses):
        """R90: Estrutura de saida com metadados."""
        with patch.object(generator, '_generate_image') as mock_gen:
            mock_gen.return_value = {
                "thesis_id": "thesis_001",
                "image_path": "/path/to/quantum_ethics.png",
                "description": "Diagrama conceitual",
                "source": "antigravity_image",
                "success": True,
            }

            result = generator.generate(top_theses[0])

        assert "thesis_id" in result
        assert "image_path" in result
        assert "description" in result
        assert "source" in result
        assert "success" in result
        assert "generated_at" in result

    def test_index_creation(self, generator, top_theses):
        """R90: Cria arquivo de indice com todas as imagens geradas."""
        with patch.object(generator, '_generate_image') as mock_gen:
            mock_gen.return_value = {
                "thesis_id": "test",
                "image_path": "/path/to/img.png",
                "description": "Test",
                "source": "antigravity_image",
                "success": True,
            }

            results = generator.generate_all(top_theses)
            index_path = generator.write_index(results)

        assert index_path is not None
        assert os.path.exists(index_path)

        with open(index_path) as f:
            index_data = json.load(f)

        assert "visual_abstracts" in index_data
        assert len(index_data["visual_abstracts"]) == 3

    def test_description_building(self, generator, top_theses):
        """R90: Descricao para geracao de imagem e construida."""
        desc = generator._build_description(top_theses[0])
        assert desc is not None
        assert len(desc) > 50
        assert "Quantum Ethics" in desc

    def test_select_top_n(self, generator):
        """R90: Selecao das top N teses por composite_score."""
        theses = [
            {"thesis_id": "t1", "composite_score": 0.5, "title": "A"},
            {"thesis_id": "t2", "composite_score": 0.9, "title": "B"},
            {"thesis_id": "t3", "composite_score": 0.3, "title": "C"},
            {"thesis_id": "t4", "composite_score": 0.7, "title": "D"},
            {"thesis_id": "t5", "composite_score": 0.8, "title": "E"},
        ]

        top = generator._select_top(theses, n=3)
        assert len(top) == 3
        assert top[0]["thesis_id"] == "t2"  # 0.9
        assert top[1]["thesis_id"] == "t5"  # 0.8
        assert top[2]["thesis_id"] == "t4"  # 0.7
