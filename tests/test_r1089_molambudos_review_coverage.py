"""R1089: cobertura rastreável do parecer sem modificar o manuscrito."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "literatura/molambudos/Molambudos_Revisada_R1075"
REPORT = ROOT / "reports/r1089/revisao_integral_r1075.md"


def test_review_covers_every_fragment_in_book_order_with_real_line_locator():
    manuscript = (BOOK / "main.tex").read_text(encoding="utf-8")
    entries = re.findall(r"\\fragdef\{([^}]+)\}\\input\{(fragmentos/[^}]+)\}", manuscript)
    assert len(entries) == len({uid for uid, _ in entries}) == 84
    report = REPORT.read_text(encoding="utf-8")
    rows = re.findall(r"^\| ((?:MEM|DOC|LUC|CONT)-[^ |]+) \| (.+?) \| (fragmentos/[^ |]+\.tex):(\d+) \|$",
                      report, re.MULTILINE)
    assert len(rows) == 84
    for (uid, rel), (seen_id, finding, seen_path, line) in zip(entries, rows):
        assert uid == seen_id
        assert seen_path == rel + ".tex"
        assert len(finding.strip()) >= 20
        assert not re.search(r"pendente|placeholder|todo", finding, re.I)
        source = BOOK / seen_path
        assert source.is_file()
        assert 1 <= int(line) <= len(source.read_text(encoding="utf-8").splitlines())


def test_review_covers_included_paratexts_epilogue_and_limits():
    manuscript = (BOOK / "main.tex").read_text(encoding="utf-8")
    included = set(re.findall(r"\\input\{(frontmatter/[^}]+)\}", manuscript))
    assert len(included) == 16
    text = REPORT.read_text(encoding="utf-8")
    for source in included:
        assert source + ".tex" in text
    for phrase in ("fragmentos/epilogo_revisado.tex", "apendice/aparato_de_leitura.tex",
                   "_removidos", "421", "não certifica KDP", "não é validação clínica"):
        assert phrase in text
