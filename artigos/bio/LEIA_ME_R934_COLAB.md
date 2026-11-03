# TCGA-KIRC R934.1 — Notebook Colab auditável

**Notebook:** `TCGA_KIRC_R934_SDD_TDD_Colab.ipynb`
**Origem:** protocolo pré-análise R934 anexado pelo pesquisador (21/10/2026).

## O que já funciona

- Especificação SDD congelada e identificada por SHA-256.
- Testes sintéticos RED→GREEN e contraprovas de acesso controlado, volume e vazamento de pacientes.
- Validação de schema e consulta **opcional** ao GDC somente em `/files`, `/files/_mapping` e `/status`.
- Inventário paginado, arquivo bruto por página, seleção por tipo, vínculo inequívoco paciente/amostra/alíquota, escolha lexicográfica sem inspecionar desfecho, checagem de acesso/versão/release/MD5 e limite de **6 GiB**.
- Download de dados **opcional e inicialmente bloqueado** com hash MD5 do GDC e SHA-256 local.
- Partição 70/30 por paciente e folds estratificados, em demonstração **sintética**.
- Genomic Intelligence: previsões exploratórias SLC2A1/SDHB explicitamente separadas da análise TCGA.

## O que ainda não está implementado/comprovado

- Pipeline completo de análise de RNA-seq/biologia do TCGA-KIRC, transformação VST congelada dentro de todas as dobras de CV aninhada, nested LASSO-Cox final, AUC/IPCW, bootstrap B=1000, C-index, Brier, calibração, MUI pareado/ssGSEA e revisão metodológica independente.
- Os gates P0–P4 são **RED por padrão**; testes sintéticos verdes não autorizam abrir P0.

## Usar

1. Abra https://colab.research.google.com, menu **Arquivo → Fazer upload de notebook**.
2. Faça upload de `TCGA_KIRC_R934_SDD_TDD_Colab.ipynb`.
3. Execute célula a célula; inicialmente nada baixa RNA-seq ou monta Drive.
4. Para consultar exclusivamente metadados, altere `CONSULTAR_GDC_METADATA=True` e reexecute desde a célula de parâmetros.
5. Os dados e manifestos detalhados são armazenados localmente no Colab em `private_metadata/`; **não compartilhe** a pasta.
6. Não habilite download antes de P0/P1 aprovados; mesmo com flags ativadas, downloader permanece bloqueado até confirmações explícitas.

**Atenção:** este material implementa o controle operacional e governança, não produz resultados prognósticos clínicos. Código original fornecido anteriormente não é executado. Não exige credenciais dbGaP ou acesso controlado.
