# Transcriptômica espacial — adaptação original

**Objetivo:** organizar predição virtual de expressão a partir de histologia,
com QC explícito.

**Fluxo:** validar lâmina e resolução; dividir em tiles com registro de
coordenadas; aplicar modelo somente se licença e pesos estiverem autorizados;
consultar painel gênico declarado; agregar por região; comparar com medição
quando existir.

**Gates:** predição não é medição; modelo não comercial; não usar para decisão
clínica; documentar versão, pesos, resolução e artefatos.

**Saída:** mapa previsto, QC, incerteza e limitações.
