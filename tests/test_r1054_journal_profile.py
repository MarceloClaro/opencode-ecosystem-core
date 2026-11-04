"""R1054 — perfil real de periódico e checagem objetiva de manuscrito."""
from __future__ import annotations

import pytest

from scientific_lab import journal_profiles


def test_plos_one_profile_is_real_and_sourced():
    profile = journal_profiles.load_profile("plos-one")
    assert profile["name"] == "PLOS ONE"
    assert profile["language"] == "en"
    assert profile["abstract_max_words"] == 300
    assert profile["title_max_chars"] == 250
    assert profile["reference_style"] == "Vancouver/ICMJE"
    assert profile["source_url"].startswith("https://journals.plos.org/")
    assert profile["verified_at"] == "2026-11-04"
    assert profile["journal_id"] == "plos-one"
    assert any("não é exaustivo" in note for note in profile["notes"])


def test_portuguese_manuscript_fails_plos_one_objective_checks(tmp_path):
    path = tmp_path / "manuscript.md"
    path.write_text(
        "# Evidências sobre o tema\n\n"
        "## Resumo\n\nResumo curto sem citação.\n\n"
        "## 1. Introdução\n\nTexto.\n\n"
        "## 2. Métodos\n\nTexto.\n\n"
        "## 3. Resultados\n\nTexto.\n\n"
        "## 4. Discussão\n\nTexto.\n\n"
        "## 5. Limitações\n\nTexto.\n\n"
        "## 6. Conclusão\n\nTexto.\n\n"
        "## Referências\n\n[ART-0001] Autor. Título. 2024.\n",
        encoding="utf-8",
    )
    profile = journal_profiles.load_profile("plos-one")
    result = journal_profiles.validate_manuscript(path, profile)
    checks = {item["id"]: item["status"] for item in result["checks"]}
    assert result["status"] == "blocked"
    assert checks["language"] == "fail"
    assert checks["required_sections"] == "fail"
    assert checks["reference_style"] == "fail"
    assert checks["title_length"] == "pass"
    assert checks["abstract_length"] == "pass"
    assert result["truth_claim"] is False
    assert result["external_validation"] is False


def test_english_manuscript_is_pending_human_not_blocked(tmp_path):
    path = tmp_path / "manuscript.md"
    path.write_text(
        "# Evidence on the topic\n\n"
        "## Abstract\n\nShort abstract without citations.\n\n"
        "## Introduction\n\nText [1].\n\n"
        "## Materials and Methods\n\nText [2].\n\n"
        "## Results\n\nText [3].\n\n"
        "## Discussion\n\nText [4].\n\n"
        "## Acknowledgments\n\nText.\n\n"
        "## References\n\n1. Author. Title. 2024.\n2. Author. Title. 2023.\n",
        encoding="utf-8",
    )
    profile = journal_profiles.load_profile("plos-one")
    result = journal_profiles.validate_manuscript(path, profile)
    checks = {item["id"]: item["status"] for item in result["checks"]}
    assert result["status"] == "pending_human"
    assert checks["language"] == "pass"
    assert checks["required_sections"] == "pass"
    assert checks["reference_style"] == "pass"
    assert checks["declaration_data_availability"] == "pending_human"
    checklist = journal_profiles.checklist(profile, result)
    assert checklist["status"] == "pending_human"
    assert checklist["policy"] == "journal_rules_not_inferred"


def test_generic_abnt_profile_and_unknown_profile(tmp_path):
    path = tmp_path / "manuscript.md"
    path.write_text(
        "# Título\n\n## Resumo\n\nTexto.\n\n## 1. Introdução\n\nTexto.\n\n"
        "## 2. Métodos\n\nTexto.\n\n## 3. Resultados\n\nTexto.\n\n"
        "## 4. Discussão\n\nTexto.\n\n## 5. Conclusão\n\nTexto.\n\n"
        "## Referências\n\nAUTOR. Título. 2024.\n",
        encoding="utf-8",
    )
    profile = journal_profiles.load_profile("generic-abnt")
    result = journal_profiles.validate_manuscript(path, profile)
    assert result["status"] in {"pending_human", "pass"}
    with pytest.raises(ValueError):
        journal_profiles.load_profile("nao-existe")
