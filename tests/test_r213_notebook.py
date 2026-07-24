#!/usr/bin/env python3
"""
Testes TDD para SPEC-935-R213.
Valida: não-redundância, estrutura, consistência e execução do notebook Colab.
"""

import json, re, sys, os, ast

NOTEBOOK = os.path.join(os.path.dirname(__file__), "..", "orquestracao_ia_colab.ipynb")
EXPECTED_CODE_CELLS = 9
EXPECTED_CELLS_TOTAL = 18

# ── HELPERS ──

def load_notebook():
    with open(NOTEBOOK) as f:
        return json.load(f)

def get_code_cells(nb):
    return [c for c in nb["cells"] if c["cell_type"] == "code"]

def get_markdown_cells(nb):
    return [c for c in nb["cells"] if c["cell_type"] == "markdown"]

def extract_classes(source):
    return re.findall(r'^\s*class\s+(\w+)\s*[:\(]', source, re.MULTILINE)

def source_text(cell):
    return "\n".join(cell["source"])


# ═══════════════════════════════════════════════════════════════
# TC-01: Estrutura do Notebook
# ═══════════════════════════════════════════════════════════════

def test_notebook_total_cells():
    """Devem existir exatamente 18 células (9 markdown + 9 code)."""
    nb = load_notebook()
    assert len(nb["cells"]) == EXPECTED_CELLS_TOTAL, \
        f"Esperado {EXPECTED_CELLS_TOTAL}, obtido {len(nb['cells'])}"

def test_notebook_code_cells():
    """Devem existir exatamente 9 células de código."""
    nb = load_notebook()
    code = get_code_cells(nb)
    assert len(code) == EXPECTED_CODE_CELLS, \
        f"Esperado {EXPECTED_CODE_CELLS} code cells, obtido {len(code)}"

def test_notebook_markdown_cells():
    """Devem existir exatamente 9 células de markdown."""
    nb = load_notebook()
    md = get_markdown_cells(nb)
    assert len(md) == EXPECTED_CODE_CELLS, \
        f"Esperado {EXPECTED_CODE_CELLS} markdown, obtido {len(md)}"


# ═══════════════════════════════════════════════════════════════
# TC-02: Consistência Markdown → Code
# ═══════════════════════════════════════════════════════════════

def test_markdown_followed_by_code():
    """Toda célula markdown com 'FASE' deve ser seguida por célula de código."""
    nb = load_notebook()
    cells = nb["cells"]
    for i, cell in enumerate(cells):
        if cell["cell_type"] != "markdown":
            continue
        if "FASE" not in source_text(cell) and "FASE" not in source_text(cell):
            continue
        assert i + 1 < len(cells), f"Cell {i} sem célula seguinte"
        assert cells[i + 1]["cell_type"] == "code", \
            f"Cell {i} (markdown FASE) → cell {i+1} não é code"

def test_code_cell_starts_with_print_or_header():
    """Toda célula de código deve ter um print de cabeçalho ou import."""
    nb = load_notebook()
    for i, cell in enumerate(get_code_cells(nb)):
        src = source_text(cell)
        has_import = bool(re.search(r'^import |^from ', src, re.MULTILINE))
        has_print = 'print("' in src or "print('" in src
        assert has_import or has_print, \
            f"Cell {i}: sem import nem print (célula vazia?)"


# ═══════════════════════════════════════════════════════════════
# TC-03: NÃO-REDUNDÂNCIA (regra de ouro da SPEC-935-R213)
# ═══════════════════════════════════════════════════════════════

def test_no_class_redefinition():
    """Nenhuma classe pode ser definida em mais de uma célula."""
    nb = load_notebook()
    classes_seen = {}  # class_name -> first_cell_index
    violations = []

    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = source_text(cell)
        classes = extract_classes(src)
        for cls in classes:
            if cls in classes_seen:
                violations.append(
                    f"'{cls}' redefinida nas cells {classes_seen[cls]} e {i}"
                )
            else:
                classes_seen[cls] = i

    assert not violations, \
        f"REGRESSÃO: {len(violations)} classe(s) redefinida(s):\n" + "\n".join(violations)


# ═══════════════════════════════════════════════════════════════
# TC-04: Imports por célula
# ═══════════════════════════════════════════════════════════════

def test_each_code_cell_has_imports():
    """Toda célula de código deve ter ao menos um import."""
    nb = load_notebook()
    for i, cell in enumerate(get_code_cells(nb)):
        src = source_text(cell)
        assert re.search(r'^import |^from ', src, re.MULTILINE), \
            f"Cell {i}: sem imports"


# ═══════════════════════════════════════════════════════════════
# TC-05: Classes-chave existem UMA única vez
# ═══════════════════════════════════════════════════════════════

KEY_CLASSES_SINGLE = [
    "Spec",          # Fase 1
    "SpecRegistry",  # Fase 1
    "SpecVerifier",  # Fase 1
    "TestResult",    # Fase 2
    "TestRunner",    # Fase 2
    "CoverageTracker", # Fase 2
    "BaseAgent",     # Fase 3
    "Task",          # Fase 3
    "Orchestrator",  # Fase 3
    "EventType",     # Fase 4
    "Hook",          # Fase 4
    "HookManager",   # Fase 4
    "PromptBuilder", # Fase 5
]

def test_key_classes_defined_once():
    """Classes-chave devem ser definidas exatamente UMA vez."""
    nb = load_notebook()
    src_total = "\n".join(source_text(c) for c in nb["cells"] if c["cell_type"] == "code")

    for cls_name in KEY_CLASSES_SINGLE:
        pattern = rf'^\s*class\s+{cls_name}\s*[:\(]'
        matches = re.findall(pattern, src_total, re.MULTILINE)
        assert len(matches) == 1, \
            f"{cls_name}: esperado 1 definição, obtido {len(matches)}"


# ═══════════════════════════════════════════════════════════════
# TC-06: Classes de fases posteriores NÃO redefinem as anteriores
# ═══════════════════════════════════════════════════════════════

CLASSES_BY_PHASE = {
    1: ["Spec", "SpecRegistry", "SpecVerifier"],
    2: ["TestResult", "TestRunner", "CoverageTracker"],
    3: ["BaseAgent", "Task", "Orchestrator", "ResearcherAgent", "WriterAgent", "ReviewerAgent"],
    4: ["EventType", "Hook", "LoggingHook", "MetricsHook", "HookManager", "HookedOrchestrator"],
    5: ["PromptBuilder"],
}

def test_phase_6_does_not_redefine_previous_classes():
    """Fase 6 (cell 13) NÃO pode definir classes já definidas nas Fases 1-5."""
    nb = load_notebook()
    cell13 = nb["cells"][13]
    assert cell13["cell_type"] == "code"
    src13 = source_text(cell13)
    classes13 = extract_classes(src13)

    previous_classes = set()
    for phase_num in [1, 2, 3, 4, 5]:
        previous_classes.update(CLASSES_BY_PHASE[phase_num])

    redefinitions = [c for c in classes13 if c in previous_classes]
    assert not redefinitions, \
        f"Fase 6 REDEFINE classes das Fases 1-5: {redefinitions}"


# ═══════════════════════════════════════════════════════════════
# TC-07: LiteRT-LM CLI commands
# ═══════════════════════════════════════════════════════════════

def test_fase8_has_litertlm_cli():
    """Fase 8 (cell 17) deve usar LiteRT-LM CLI, não HuggingFace."""
    nb = load_notebook()
    cell17 = nb["cells"][17]
    src17 = source_text(cell17)
    assert "litert-lm" in src17, "Cell 17 sem litert-lm CLI"
    assert "transformers" not in src17, "Cell 17 ainda usa HuggingFace transformers"
    assert "subprocess" in src17, "Cell 17 deve usar subprocess para CLI"


# ═══════════════════════════════════════════════════════════════
# TC-08: Execução completa (dry-run via compile)
# ═══════════════════════════════════════════════════════════════

def test_all_cells_compile():
    """Todas as células de código compilam sem SyntaxError."""
    nb = load_notebook()
    for i, cell in enumerate(get_code_cells(nb)):
        src = source_text(cell)
        if not src.strip():
            continue
        try:
            ast.parse(src)
        except SyntaxError as e:
            raise AssertionError(f"Cell {i}: SyntaxError - {e}")


# ═══════════════════════════════════════════════════════════════
# TC-09: Fase 2 TDD RED→GREEN
# ═══════════════════════════════════════════════════════════════

def test_tdd_red_green_present():
    """Fase 2 (cell 5) deve conter ambas as fases RED e GREEN."""
    nb = load_notebook()
    cell5 = nb["cells"][5]
    src5 = source_text(cell5)
    assert "FASE RED" in src5, "Cell 5 sem FASE RED"
    assert "FASE GREEN" in src5, "Cell 5 sem FASE GREEN"
    assert "0/5 PASS" in src5 or "test_target_class_exists" in src5, \
        "Cell 5 sem testes RED"


# ═══════════════════════════════════════════════════════════════
# TC-10: Fase 8 tem arXiv API
# ═══════════════════════════════════════════════════════════════

def test_fase8_has_arxiv():
    """Fase 8 deve consultar arXiv API."""
    nb = load_notebook()
    cell17 = nb["cells"][17]
    src17 = source_text(cell17)
    assert "arxiv.org" in src17 or "export.arxiv" in src17


# ═══════════════════════════════════════════════════════════════
# Execução direta
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
