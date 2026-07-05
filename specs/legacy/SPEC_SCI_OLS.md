# SPEC-SCI-007: Embl Ebi Ols
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Query and search the EMBL-EBI Ontology Lookup Service (OLS) for biomedical

## Acceptance Criteria
- [x] CT-1: obo id to iri
- [x] CT-2: obo id to iri chebi
- [x] CT-3: double encode iri
- [x] CT-4: resolve ontology from prefix
- [x] CT-5: resolve ontology explicit
- [x] CT-6: search ols outputs success
- [x] CT-7: obo prefixes
- [x] CT-8: base url
- [x] CT-9: class:TestOlsUtils
- [x] CT-10: class:TestOlsSearch

## Engine
scripts/ -> get_individual.py, get_ontology.py, get_property.py, get_stats.py, get_term.py, ols_utils.py, search_ols.py, suggest_ols.py

## Test File
tests/test_ols.py
