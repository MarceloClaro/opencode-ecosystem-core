"""R1002: normalização do adaptador books na fachada comum de conhecimento."""


def test_books_adapter_normalizes_library_output():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    raw = {
        "status": "ready",
        "abstained": False,
        "reason": None,
        "source_kind": "local_technical_book",
        "evidence": [{
            "title": "LivroTecnico",
            "source": "livro.pdf",
            "file": "livro.pdf",
            "page": 12,
            "book_id": "a" * 64,
            "source_sha256": "a" * 64,
            "page_sha256": "b" * 64,
            "text": "trecho citável do livro",
            "citation": "livro.pdf, página PDF 12, SHA-256 " + "a" * 64,
            "uri": "ecosystem://books/" + "a" * 64 + "/pages/12",
        }],
    }
    result = MarceloClaroOrchestrator._normalize_books_result(raw)
    assert result["status"] == "ready"
    assert result["abstained"] is False
    assert result["total_matches"] == 1
    assert result["results"][0]["title"] == "LivroTecnico"
    assert result["results"][0]["source_sha256"] == "a" * 64
    assert result["results"][0]["page"] == 12


def test_books_adapter_preserves_abstention():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    empty = MarceloClaroOrchestrator._normalize_books_result(
        {"abstained": True, "evidence": [], "reason": "not_indexed"}
    )
    assert empty["abstained"] is True
    assert empty["total_matches"] == 0
    assert empty["results"] == []
    assert empty["reason"] == "not_indexed"
