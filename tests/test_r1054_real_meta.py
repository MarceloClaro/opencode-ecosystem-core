"""R1054 — validação numérica do módulo quantitativo contra o dataset BCG."""
from __future__ import annotations

from scientific_lab import real_benchmark


def test_bcg_reml_matches_public_reference():
    result = real_benchmark.run(
        "reports/r1054/bcg.csv",
        "reports/r1054/reference.json",
    )
    assert result["status"] == "pass"
    assert result["observed"]["k"] == 13
    assert result["observed"]["random_method"] == "REML"
    assert abs(result["observed"]["pooled_or"] - 0.4746499130523234) < 1e-5
    assert abs(result["observed"]["tau2"] - 0.3377720450772514) < 1e-5
    assert abs(result["observed"]["q"] - 163.16491518079985) < 1e-6
    assert result["truth_claim"] is False
    assert result["external_validation"] is False
    assert result["human_review_required"] is True
    checks = {item["id"]: item for item in result["checks"]}
    assert checks["pooled_or"]["status"] == "pass"
    assert checks["i2_standard"]["status"] == "pass"
    assert checks["i2_published"]["status"] == "pass"
    assert 0.5 < checks["i2_published"]["difference"] < 0.7
    assert len(result["csv_sha256"]) == 64


def test_bcg_rejects_zero_cell(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "trial,author,year,tpos,tneg,cpos,cneg,ablat,alloc\n"
        "1,A,2024,0,10,5,10,0,random\n",
        encoding="utf-8",
    )
    try:
        real_benchmark.load_bcg(path)
    except ValueError as exc:
        assert "positiva" in str(exc) or "inválida" in str(exc)
    else:
        raise AssertionError("contagem zero deveria ser recusada")
