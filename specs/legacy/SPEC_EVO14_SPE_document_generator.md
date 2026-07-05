# SPEC_EVO14_SPE_DOCUMENT_GENERATOR -- Document Generator Engine v1.0

**Domain**: agency-agents/specialized/specialized-document-generator
**Python**: 3.12, stdlib only
**Status**: Draft

---

## CT-01: Template Variable Extraction
Template com 3 variaveis {{number}}, {{client_name}}, {{amount}} → required_vars captura todas.

## CT-02: Template Filling
fill() substitui todas as variaveis. Resultado sem "{{" residual.

## CT-03: Document Generation Pipeline
Registro + geracao: Document com word_count>3, has_metadata=True, conteudo correto.

## CT-04: Missing Variable Detection
check_missing_vars() retorna ["party_b", "value"] quando apenas 2 de 4 fornecidas.

---

## Implementation
- `scripts/document_generator_engine.py`: Template, Document, DocumentGenerator, OutputFormat
- `tests/test_document_generator.py`: 4 CTs via pytest
