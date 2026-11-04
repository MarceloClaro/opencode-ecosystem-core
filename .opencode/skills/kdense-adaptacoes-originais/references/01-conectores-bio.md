# Conectores biológicos — adaptação original

**Objetivo:** integrar UniProt, KEGG, ChEMBL, Reactome, QuickGO e UniChem sem
esconder endpoint, versão ou termos.

**Fluxo:** declarar identificador e organismo; consultar endpoint oficial;
registrar data, versão, query e hash da resposta; mapear identificadores sem
assumir equivalência; separar anotação de inferência.

**Gates:** não usar credencial em texto; não contornar rate limit; não tratar
anotação como prova funcional; registrar 404/429 como ausência, não como
resultado negativo.

**Saída:** tabela de registros, fonte, data, hash e limitações.
