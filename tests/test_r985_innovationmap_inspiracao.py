from pathlib import Path
import json

def test_innovation_json_valido():
    p = Path("outputs/pesquisa-inovacao-enfoque/tecnologias.json")
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 25
    req = {"id", "titulo", "cluster", "trl", "descricao_curta", "casos_de_uso", "sdgs"}
    for item in data:
        assert req.issubset(item.keys())
        assert 1 <= item["trl"] <= 9
        assert isinstance(item["casos_de_uso"], list)

def test_quantica_catalogo_valido():
    p = Path("outputs/pesquisa-inovacao-enfoque/quantica-repositorios.json")
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 30
    req = {"id", "org_repo", "tipo", "trl_estimado", "relevancia_inovacao", "justificativa_pesquisa"}
    for item in data:
        assert req.issubset(item.keys())
        assert 1 <= item["trl_estimado"] <= 9
        assert item["justificativa_pesquisa"]
    ids = [d["id"] for d in data]
    assert "marceloclaro-beneficial-quantum-noise-in-variational-quantum-classifiers" in ids

def test_index_html_embedded_data():
    html = Path("outputs/pesquisa-inovacao-enfoque/index.html").read_text(encoding="utf-8")
    assert "const DATA" in html
    assert "Pesquisa de Inovação" in html

def test_publicacao_pacote():
    root = Path("outputs/pesquisa-inovacao-enfoque/publicacao")
    assert (root / "manuscrito/01-introducao.md").exists()
    assert (root / "manuscrito/06-conclusao.md").exists()
    assert (root / "PROTOCOLO_FOMENTO.md").exists()
    assert (root / "living-review/README.md").exists()
    assert (root / "manuscrito/00-resumo-abstract.md").exists()
    assert (root / "caso-estudo-bqnvqc.md").exists()
    assert (root / "manuscrito-final/main.pdf").exists()
