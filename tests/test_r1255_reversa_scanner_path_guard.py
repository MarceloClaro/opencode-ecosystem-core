"""R1255: probing de caminho não deve abortar o fallback do ReversaScanner."""

from reversa_universal.engine import ReversaUniversalEngine
from scanners.reversa_scanner import ReversaScanner


def _scan_capturing_oserror(corpus):
    try:
        return ReversaScanner().scan(corpus)
    except OSError as exc:
        return exc


def test_overlong_relative_path_with_code_falls_back_to_text():
    corpus = "x" * 260 + " def extracted():"

    result = _scan_capturing_oserror(corpus)

    assert not isinstance(result, OSError), f"scan propagated filesystem error: {result}"
    assert result.score >= 5.0
    assert any("Código estruturado detectado" in finding for finding in result.findings)


def test_overlong_absolute_path_falls_back_without_exception():
    corpus = "/" + "x" * 260

    result = _scan_capturing_oserror(corpus)

    assert not isinstance(result, OSError), f"scan propagated filesystem error: {result}"
    assert result.score == 3.0
    assert result.findings == ["Nenhum código estruturado detectado para engenharia reversa."]


def test_existing_path_still_uses_universal_engine(tmp_path, monkeypatch):
    calls = []

    def analyze(self, path):
        calls.append(path)
        return {
            "gaps": {"gaps": [], "correlations": [], "solutions": [], "innovations": []},
            "inventory": {"total_files": 1, "total_loc": 1, "languages": ["Python"]},
            "modules": [{"name": "sample"}],
        }

    monkeypatch.setattr(ReversaUniversalEngine, "analyze", analyze)
    result = ReversaScanner().scan(str(tmp_path))

    assert calls == [str(tmp_path)]
    assert any("Reversa Universal analisou" in finding for finding in result.findings)


def test_plain_text_scanning_remains_unchanged():
    result = ReversaScanner().scan("def foo():\n    pass\n")

    assert result.score >= 5.0
    assert any("Código estruturado detectado" in finding for finding in result.findings)
