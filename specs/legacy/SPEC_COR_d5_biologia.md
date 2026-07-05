# SPEC-COR-D5: Biologia Molecular e Genomica (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D5 do CORA-Eval — transcricao, traducao e conteudo GC com codigo genetico padrao.

## Acceptance Criteria
- [x] CT-1 (N1-01): Transcricao DNA->RNA — ATGCGT->AUGCGU, GATTACA->GAUUACA, sequencia sem T permanece igual
- [x] CT-2 (N1-02): Traducao codon->aminoacido — AUG->Metionina, UGG->Triptofano, UAA/UAG/UGA->STOP, sequencia completa AUGGCCUGGUAA->Met-Ala-Trp
- [x] CT-3 (N1-03): Conteudo %GC — ATGCGCAT=50%, GGGCCC=100%, ATATAT=0%, promotor TTGACA ~33.33%

## Test File
tests/test_d5_biologia.py
