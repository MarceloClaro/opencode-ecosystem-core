# SPEC-TOP-004: Docling PDF Extraction
Version: 1.0.0 | Domain: document-processing

## Objective
Skill de extracao de conhecimento de PDFs usando Docling (IBM Research). Wrapper que conecta a skill ao adapter em nexus/scripts/docling_adapter.py.

## Acceptance Criteria
- [x] CT-1: extrair_pdf returns dict with status key
- [x] CT-2: Fallback mode works when adapter not found
- [x] CT-3: main function exists and accepts CLI args
- [x] CT-4: SKILL.md describes Docling integration

## Assets
- scripts/docling_skill.py
- SKILL.md
- tests/test_docling_pdf.py
