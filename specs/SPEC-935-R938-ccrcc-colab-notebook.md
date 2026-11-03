---
spec_id: SPEC-935-R938
title: Notebook Colab seguro para o piloto ccRCC/TCGA-KIRC e Genomic Intelligence
component: artigos.bio.pacote_pesquisa_ccrcc_colab
status: proposed
test_file: tests/test_r938_ccrcc_colab_notebook.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    structure:
    - tests/test_r938_ccrcc_colab_notebook.py::test_notebook_is_valid_unexecuted_nbformat4
    safety:
    - tests/test_r938_ccrcc_colab_notebook.py::test_notebook_removes_hidden_r_and_unbounded_download_execution
    drive_storage:
    - tests/test_r938_ccrcc_colab_notebook.py::test_drive_run_is_timestamped_and_non_overwriting
    manifest:
    - tests/test_r938_ccrcc_colab_notebook.py::test_manifest_guard_accepts_only_audited_metadata_only_manifest
    execution_gate:
    - tests/test_r938_ccrcc_colab_notebook.py::test_manifest_guard_rejects_paused_or_hash_failure
    - tests/test_r938_ccrcc_colab_notebook.py::test_colab_p0_p1_gate_fails_closed_until_human_acceptance
    reporting:
    - tests/test_r938_ccrcc_colab_notebook.py::test_notebook_states_primary_estimand_and_current_gates
    genomic_intelligence:
    - tests/test_r938_ccrcc_colab_notebook.py::test_genomic_intelligence_pilot_is_separate_from_tcga_measurements
---

# R938 — notebook Colab ccRCC / Genomic Intelligence

## Escopo

Melhorar somente o notebook
`artigos/bio/Pacote_Pesquisa_ccRCC_Genomic_Intelligence/Pesquisa_ccRCC_Genomic_Intelligence_Colab.ipynb`
para torná-lo coerente com o protocolo R934, o inventário metadata-only R935 e
o parecer condicional recebido. A edição não executa células, o R script, a API
GI, consultas GDC, instalações, downloads ou análises de pacientes.

## Critérios de aceitação

- `structure` — JSON parseável como nbformat 4; células sem `execution_count` e
  sem outputs persistidos. Não incorporar outputs de TCGA nem afirmar execução.
- `safety` — remover R em Base64 e qualquer execução `Rscript`, `GDCdownload`,
  `GDCprepare`, instalação de dependências ou bundle automático de diretórios
  com dados. GI REST permanece desativada por padrão.
- `drive_storage` — a pedido explícito do operador, montar o Drive somente sob
  Colab e escrever dataset, logs, manifesto, resultados e artefatos dentro de um
  diretório de execução único em `MyDrive/ccRCC_Genomic_Intelligence/runs/`.
  `RUN_ID` deve conter timestamp UTC e cada nova execução deve usar
  `mkdir(..., exist_ok=False)`, sem sobrescrever ou apagar execuções anteriores.
  Registrar etapas e hashes no próprio diretório versionado; não montar Drive ou
  criar arquivos ao testar/editar o notebook fora do runtime Colab.
- `manifest` — incluir guard local/metadata-only que confere sidecar SHA-256,
  `status=metadata_manifest_ready`, `download_eligible=true`, limite exato de
  6 GiB, soma e contagem dos file IDs selecionados, unicidade, `access=open`,
  `state=released`, checksums MD5, workflow único, `common_data_releases` não
  vazio, release comum escolhido presente, flags de conteúdo/análise/controlled
  falsas e exclusão autorizada auditável do UUID
  `2b0106c5-7e32-423b-957f-06c9f2e7751b`. Falha em qualquer verificação bloqueia
  o uso do manifesto; o guard não baixa conteúdo.
- `reporting` — declarar como estimando primário a diferença da AUC
  cumulative/dynamic em cinco anos com IC 95%; citar TRIPOD+AI como diretriz de
  relato, não validação. Declarar P0–P4 pendentes/condicionais conforme evidência
  atual; testes do notebook não equivalem a validação do pipeline científico.
- `Genomic Intelligence` — manter previsões de sequência como linha in silico
  separada, não medidas de RNA-seq TCGA, expressão tumoral ou observações por
  paciente. Não fundi-las à matriz TCGA nem ao preditor primário.
- `status` — registrar consulta GDC metadata-only já realizada, 614 IDs únicos,
  605 selecionados na versão anterior do manifesto, nenhum arquivo de conteúdo
  baixado e nenhum resultado TCGA observado. Avisar que o manifesto deve ser
  regenerado após a emenda de exclusão e do cálculo de releases comuns.
- `execution_gate` — qualquer etapa futura de download/análise no Colab deve
  parar se P0/P1 não estiverem aceitos, se o guard do manifesto falhar ou se
  `download_eligible` não for true. O gate deve também exigir sidecar SHA-256
  verificado e flags metadata-only falsas para análise/download prévios. A
  autorização de Drive permite persistência, não contorna os gates científicos
  nem torna a execução atual automaticamente aprovada. Metadados e testes
  sintéticos podem ser executados sem aprovação P0; downloads e análise exigem
  aceites separados.

## Critérios de Aceitação Executáveis

- `structure` — o artefato é nbformat 4 válido e as células persistidas não têm
  estado de execução nem outputs armazenados.
- `safety` — não há R em Base64, execução `Rscript`, `GDCdownload`, `GDCprepare`,
  instalação automática de pacotes nem bundle indiscriminado de dados; GI REST
  permanece desativado por padrão.
- `drive_storage` — o notebook monta Drive somente em Colab, cria `RUN_ID` UTC,
  cria `RUN_DIR` com `exist_ok=False` e grava piloto, manifesto, logs e índice de
  artefatos na execução versionada sem sobrescrever runs anteriores.
- `manifest` — o guard aceita somente manifesto metadata-only com SHA-256 válido,
  open/released, limite de 6 GiB, IDs únicos, workflow homogêneo, releases comuns,
  soma/contagem reconciliadas e exclusão workflow autorizada presente como
  excluída e fora da coorte primária.
- `execution_gate` — estado pausado, hash inválido, incompatibilidade ou falta de
  aceite P0/P1 bloqueia a continuação; o notebook não implementa bypass ou
  download silencioso.
- `reporting` — objetivo prognóstico, IC 95% e estado factual dos gates são
  explícitos; não se atribui GREEN científico a testes sintéticos.
- `genomic_intelligence` — piloto de sequência fica identificado como in silico,
  separado das medições TCGA e fora do preditor primário.

## Verificação

Testes estáticos e unitários do guard operam somente sobre JSON sintético e o
texto do notebook. Não executar `nbclient`, células Colab, montar Drive, R, APIs,
rede GDC ou download de dados. O manifesto real só será validado em operação
metadata-only separada, conforme R935.
