# SPEC_EVO14_SPE_DATA_CONSOLIDATION -- Data Consolidation Agent Engine v1.0

**Domain**: agency-agents/specialized/data-consolidation-agent
**Python**: 3.12, stdlib only
**Status**: Draft

---

## CT-01: Schema Registration
2 sources registrados, common_columns={"client_id","client_name"}, registro duplicado rejeitado.

## CT-02: Data Merging with Key
Merge de CRM (2 rows) + ERP (2 rows, 1 duplicada) = 3 rows. source_counts: CRM=2, ERP=1, warnings=1.

## CT-03: Aggregation Functions
SUM=80000, AVG=20000.0, COUNT=4, MIN=15000, MAX=25000. None values ignorados.

## CT-04: Empty and Edge Cases
Datasets vazios → 0 rows. Coluna inexistente → aggregacao retorna 0. common_columns vazio.

---

## Implementation
- `scripts/data_consolidation_engine.py`: DataConsolidator, SourceSchema, ColumnSchema, ConsolidationResult, AggFunc
- `tests/test_data_consolidation.py`: 4 CTs via pytest
