---
spec_id: SPEC-935-R934
title: Protocolo reprodutível ccRCC / TCGA-KIRC com dados GDC open access
component: artigos.bio.tcga_kirc_protocol
status: proposed
test_file: tests/test_r934_ccrcc_protocol.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    pergunta:
    - tests/test_r934_ccrcc_protocol.py::test_question_and_no_results_are_explicit
    acesso:
    - tests/test_r934_ccrcc_protocol.py::test_gdc_scope_is_open_access_and_manifested
    - tests/test_r934_ccrcc_protocol.py::test_gdc_file_inventory_query_is_reproducible_and_metadata_only
    - tests/test_r934_ccrcc_protocol.py::test_official_schema_audit_receipt_is_bounded
    leakage:
    - tests/test_r934_ccrcc_protocol.py::test_patient_level_lockbox_and_nested_selection
    integridade:
    - tests/test_r934_ccrcc_protocol.py::test_raw_counts_are_summed_and_aliquots_are_traceable
    prognostico:
    - tests/test_r934_ccrcc_protocol.py::test_validation_model_is_fitted_in_training_only
    resultados:
    - tests/test_r934_ccrcc_protocol.py::test_no_outcome_threshold_is_a_delivery_gate
    interpretacao:
    - tests/test_r934_ccrcc_protocol.py::test_mui_and_immune_claims_are_bounded
    reproducibilidade:
    - tests/test_r934_ccrcc_protocol.py::test_supplied_pipeline_is_not_authorized_or_executed
---

# R934 — protocolo de análise de ccRCC com TCGA-KIRC

## Escopo e estado

O operador confirmou a pergunta sobre carcinoma renal de células claras (ccRCC)
e autorizou consulta/aquisição **somente de dados públicos ou open-access** do
GDC/TCGA-KIRC. Esta spec congela o método proposto antes da consulta de coorte.
Emenda autorizada pelo operador em 2026-10-21: o limite agregado de conteúdo
passa de 2 GiB para **6 GiB (6 × 1024³ bytes)**. Isso não resolve incompatibilidade
de workflow/release, não altera a seleção da coorte e não autoriza por si só
qualquer download. Uma consulta metadata-only já foi executada; nenhum conteúdo
foi baixado nem resultado analítico observado. A análise do rascunho e script em
`artigos/bio/` é estática; o script fornecido não deve ser executado.

Emenda autorizada pelo operador em 2026-10-21: registrar como excluído da coorte
primária somente o file UUID `2b0106c5-7e32-423b-957f-06c9f2e7751b` por seu
`workflow_version` (`5a02c12930eb23436322a7494047b907b97570c5`) divergir do
workflow primário (`5d8c131bbff59fb0c969217fc1d44e6d1503cd1f`). Não foi
encontrado arquivo alternativo para o mesmo paciente/condição. Seu intervalo
`data_release` `36.0-46.0` se sobrepõe a `32.0-46.0`; essa diferença textual não
é, por si só, incompatibilidade. A justificativa é preservar proveniência de
workflow homogênea: sem demonstração de equivalência entre versões distintas do
STAR Counts, combiná-las poderia confundir efeitos de processamento com variação
biológica. A decisão usa apenas metadados, antes de examinar expressão ou
desfecho; não afirma que o arquivo seja inválido. O registro completo e o motivo
permanecem no manifesto. Nenhuma outra incompatibilidade fica automaticamente
dispensada.

## Critérios de Aceitação Executáveis

- `pergunta` — pergunta, objetivos primário/secundários, população, desfecho e
  hipóteses ficam separados; números/resultados do rascunho são marcados não
  verificados e não são reproduzidos como achados.
- `acesso` — consultar somente GDC `/files` metadata após validar filtros/campos
  no schema oficial; filtrar projeto/assay/workflow e `files.access=open`, obter
  vínculo inequívoco arquivo→sample→aliquota e `sample_type`, distinguir UUID de
  barcode, exigir estado `released`, distinguir versão de arquivo por file_id de
   workflow_version, usar `data.pagination.total` da resposta API (não assumir
   `hits.total`), e inventariar `data_release` por arquivo, checksum, bytes e
   contagens reconciliadas por file_id único. Consultar `/files/versions` para
   obter a lista exata `latest_release` de cada arquivo e calcular as versões de
   release comuns; intervalos `data_release` textualmente diferentes não pausam
   se houver interseção não vazia. Divergência de `workflow_version` pausa,
   exceto pela exclusão metadata-only do único UUID explicitamente autorizada
   nesta spec; qualquer outra divergência ou interseção de releases vazia exige
   decisão humana. Não solicitar nem baixar
   controlled-access ou conteúdo antes do manifesto e do limite operacional de
   6 GiB autorizado em 2026-10-21; a única exclusão metadata-only autorizada
   nesta spec não dispensa incompatibilidades de outros arquivos.
- `leakage` — separar por paciente e congelar holdout antes de transformações
  aprendidas; toda seleção/tuning ocorre dentro da validação cruzada aninhada
  operacionalmente especificada no discovery. O holdout não pode escolher
  modelo, limiar ou genes e é avaliado uma vez após o congelamento.
- `integridade` — somar contagens brutas por gene/identificador, não calcular
  média de contagens por símbolo; alíquotas repetidas são resolvidas por regra
  determinística prévia e auditável, com análise de sensibilidade a aliquotas
  alternativas.
- `prognostico` — ajustar modelo clínico-base e modelo ampliado exclusivamente
  no discovery; produzir predições congeladas para validação, com incerteza.
  Modelo Cox estimado no holdout não é rotulado validação do modelo treinado;
  normalização de novos samples usa referência estimada no discovery.
- `resultados` — gates de entrega verificam integridade computacional e
   proveniência, nunca exigem direção, significância, HR, AUC ou calibração
   favoráveis; para o desfecho primário, reportar a diferença da AUC em 5 anos
   com IC de 95%, mesmo se nula, desfavorável ou imprecisa; definir previamente
   estimabilidade do horizonte e método de incerteza.
 - `interpretacao` — MUI tumor-normal é análise descritiva; expressão bulk e
   ssGSEA são associações de assinaturas transcriptômicas, não fluxos metabólicos,
   infiltração celular, exaustão funcional ou causalidade demonstrada. Saídas
   Genomic Intelligence derivadas de sequência de referência são uma linha
   exploratória separada, não medidas de RNA-seq TCGA, não diferenças
   tumor-normal e não entram no modelo primário sem adendo e validação próprios.
 - `reproducibilidade` — não executar o script local fornecido nem instalar
   pacotes automaticamente. Por autorização explícita de 2026-10-21, Colab pode
   montar Google Drive exclusivamente para persistência sob uma pasta única com
   timestamp UTC, sem sobrescrever execuções anteriores; dataset, logs e saídas
   ficam versionados dentro dessa pasta. Qualquer pipeline futuro será original,
   pinado, submetido ao manifesto open-only, limite de 6 GiB, hashes, semente,
   fluxo de inclusão/exclusão, missingness e gates anteriores à análise.

## Portão antes de dados

Depois do RED→GREEN do protocolo e da revisão independente disponível, pode-se
consultar somente metadados do GDC e construir manifesto open-access. A consulta
metadata-only já ocorreu; o manifesto disponível precisa ser regenerado após as
emendas de limite e exclusão autorizada. Não baixar conteúdo até o manifesto
mostrar acesso `open` por arquivo, tamanho total até 6 GiB e hash/checksum
disponível, além da resolução dos bloqueios de compatibilidade workflow/release
remanescentes. Arquivo sem status público
inequívoco é excluído. Se o volume exceder 6 GiB, pausar e pedir decisão humana;
não expandir escopo automaticamente. Nenhuma análise
confirmatória inicia antes do pré-processamento e critérios estatísticos serem
congelados a partir do inventário real, mantendo o holdout fechado.

## Interpretação da validação

O objetivo é avaliação prognóstica observacional e validação interna em uma
partição TCGA; isso não equivale a validação externa, causalidade, efetividade
clínica, decisão assistencial ou aprovação editorial. Não afirmar equivalência
de coortes com testes de equilíbrio `p > 0,05`; apresentar distribuições,
diferenças padronizadas e incerteza. Estimar a diferença de desempenho entre
modelos, com IC; superioridade não é condição para declarar execução válida.
