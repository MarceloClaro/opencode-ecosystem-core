# PROTOCOLO DE PESQUISA – TCGA-KIRC + GENOMIC INTELLIGENCE

**Versão:** 1.0, 20 de outubro de 2026  
**Natureza:** estudo retrospectivo observacional e investigação computacional exploratória, sem finalidade clínica.  
**Título provisório:** Desacoplamento entre glicólise e ciclo TCA no carcinoma renal de células claras: integração transcriptômica e inteligência genômica.

## Resumo do protocolo (não confundir com resumo de resultados)

O carcinoma renal de células claras apresenta heterogeneidade molecular e alterações no metabolismo energético. O objetivo deste estudo será quantificar o índice de desacoplamento glicólise–TCA (MUI), testar sua associação com o fenótipo tumoral e investigar o valor prognóstico de genes metabólicos previamente definidos na coorte TCGA-KIRC. A investigação integrará análise diferencial de RNA-seq (STAR counts), avaliação pareada de tecidos tumorais e normais, modelagem de sobrevivência via LASSO-Cox, validação interna separada e predições independentes de sequência genômica pelo Genomic Intelligence. A pesquisa adotará SDD e TDD para verificar integridade, isolamento treino–teste e rastreabilidade. Os resultados preliminares do Genomic Intelligence constituem somente evidência **in silico** sobre regiões regulatórias e níveis de expressão previstos a partir da sequência de referência, sem demonstração de diferenças entre tumor e normal. Os resultados da coorte TCGA-KIRC, os intervalos de confiança e a calibração do modelo só poderão ser reportados após sua execução, auditoria e avaliação de dados faltantes.

**Objetivo prognóstico primário:** estimar a diferença de AUC dependente do tempo em 5 anos entre os modelos clínico-metabólico e clínico-base, com IC de 95%, sem presumir superioridade. MUI tumor-normal e Genomic Intelligence são linhas secundárias/exploratórias distintas.

**Palavras-chave:** carcinoma renal de células claras; glicólise; ciclo do ácido tricarboxílico; transcriptômica; prognóstico.

## Problema e hipótese

**Problema:** o contraste entre atividade glicolítica e TCA/OXPHOS está associado à transformação tumoral e adiciona discriminação prognóstica para além do estágio tumoral?

- H1, confirmatória dentro da coorte especificada: ΔMUI (tumor − normal) será distinto de zero em comparações pareadas; direção e significância serão estimadas empiricamente.
- H2, prognóstica exploratória: assinatura de genes metabólicos predefinidos pode mostrar discriminação out-of-sample acima de modelo clínico simples; a hipótese pode ser refutada.
- H3, mecanística exploratória: regiões classificadas como promotoras, padrões de cromatina e sítios de splicing em genes metabólicos poderão priorizar candidatos para ensaios laboratoriais futuros.

## Desenho e métodos

**Origem de dados:** Genomic Data Commons, projeto público TCGA-KIRC, arquivos de quantificação STAR - Counts; anotações Ensembl GRCh38 para os loci das sequências e transcritos canônicos. Dados clínicos e de seguimento dependem das variáveis efetivamente disponíveis na extração. São elegíveis amostras primárias 01 e normais sólidas 11, desduplicadas por participante e condição. A consulta realizada até aqui foi somente de metadados; não houve download de arquivos transcriptômicos nem execução de análise TCGA.

`data_release` no `/files` é um valor/faixa por arquivo; não deve ser confundido com `version`. `/files/versions` lista releases exatos associados à versão corrente. Faixas textuais diferentes não são automaticamente incompatíveis: registrar a interseção das listas `latest_release` e exigir pelo menos um release comum para o conjunto selecionado.

**Transcritômica:** genes `protein_coding` com CPM >1 em pelo menos 15% das amostras, mantendo identificadores Ensembl para análise primária. A expressão diferencial prioritária será realizada com DESeq2 em pares tumor–normal com fator de pareamento do paciente. A multiplicidade será controlada por Benjamini–Hochberg. Para o MUI, as contribuições glicolítica e TCA serão agregadas de genes predefinidos, usando média e desvio de pacientes normais pareados como referência, com teste de Wilcoxon pareado e estimativa do tamanho do efeito. A lista de genes candidatos ao modelo de sobrevida será pré-especificada e **não** selecionada pela comparação diferencial global.

**Prognóstico:** pacientes tumorais com sobrevida observável e covariáveis completas serão divididos uma única vez, com estratificação do evento, em descoberta (aproximadamente 70%) e validação interna (aproximadamente 30%). Filtragem, estimação de fatores e dispersão, transformação VST, seleção LASSO-Cox, centragem/escalonamento e ponto de corte serão ajustados exclusivamente na descoberta. A coorte de validação receberá parâmetros congelados. AUC dependente do tempo em 1, 3 e 5 anos será estimada quando o suporte do seguimento permitir; coeficientes do modelo integrado clínico serão aprendidos só no treino.

**Genômica preditiva:** duas sondas do piloto, SLC2A1 e SDHB, foram recuperadas pelo serviço Genomic Intelligence do Ensembl humano GRCh38, preservando orientação sense. Foram estimados promotores (`g0-promoter-2000bp`), cromatina (`g0-deepsea`), splicing de SLC2A1 (`g0-splice-bigbird`) e expressão de referência (`g0-expression-8192`). Não se utilizará `g0-deepstarr` para inferência de enhancer humano porque o modelo padrão tem treinamento em Drosophila. Os resultados da etapa REST independente requerem chave de API, separada do acesso ao plugin no chat.

**Confiabilidade:** dados ausentes e falhas de rede interromperão a etapa correspondente. O software não força `p < 0,05`, `AUC integrada > AUC estágio`, um número mínimo de genes esparsos nem `MAE < 0,05`. Um eventual nomograma RMS e sua calibração bootstrap B=1000 são uma **etapa ainda pendente**, e bootstrap interno não substitui validação externa. Recomendam-se avaliação de poder estatístico, estudo de censura, testes de sensibilidade, intervalos de confiança, reamostragem aninhada e teste em coortes externas antes de qualquer pretensão translacional.

## Estado operacional e gates (21/10/2026)

- Consulta metadata-only: 614 file IDs únicos; o inventário anterior selecionou
  605 arquivos e somou 2.566.647.024 bytes. Esse manifesto precisa ser regenerado
  para aplicar a exclusão autorizada e reconciliar releases pela interseção de
  `latest_release`.
- O operador autorizou excluir da coorte primária somente o arquivo
  `2b0106c5-7e32-423b-957f-06c9f2e7751b` por workflow STAR Counts divergente. A
  faixa `data_release` deste arquivo se sobrepõe às demais; a exclusão não se
  baseia em diferença textual de faixa, mas na proveniência do workflow. O
  rationale e o registro integral devem permanecer no manifesto. Nenhum conteúdo
  foi baixado.
- **P0** continua pendente de fechamento metodológico humano; GREEN dos testes
  documentais não valida o pipeline científico. **P1** aguarda novo manifesto.
  **P2** permanece pendente (sem downloads/checksum de conteúdo); **P3** não foi
  executado e ainda requer testes sintéticos de leakage/nested CV; **P4** não tem
  resultados TCGA observados.
- TRIPOD+AI (2024) será usado como guia de relato, não como validação, certificação
  de baixo risco de viés ou evidência de validade clínica.

**Auditoria estática do código anexado:** `TCGA_KIRC_SDD_TDD.R` não foi executado.
Na versão fornecida, `GDCquery` não fixa `access=open`/`state=released` antes de
`GDCdownload`, o download não está subordinado ao manifesto/teto de 6 GiB e há
um corte `OS_days >= 30` que precisa de justificativa. O modelo faz uma divisão
treino/validação e uma chamada `cv.glmnet` dentro do treino, mas não demonstra a
validação cruzada aninhada outer/inner prevista pelo protocolo R934. Esse arquivo
não é autorizado como pipeline de aquisição/análise sem revisão e correção.

## Resultados-piloto executados em 20/10/2026

| Medida | SLC2A1 | SDHB |
|---|---:|---:|
| Ensembl | ENSG00000117394 | ENSG00000117118 |
| Tamanho de sequência gene + 2 kb/lado | 37.552 bp | 39.547 bp |
| Janelas de promotor previstas ≥0,5 | 13/38 | 7/40 |
| Máxima pontuação de promotor | 0,9861 | 0,8815 |
| Janelas de cromatina inspecionadas | 188 | 198 |
| Rótulos de cromatina acima do limiar | 17.531 | 4.321 |
| Rótulos RPTEC no conjunto acima | 270 | 50 |
| TPM previsto G0 de referência | 39,9449 | 126,9445 |
| Splicing previsto | 11 doadores; 13 aceptores | não executado |

As contagens de cromatina não são sítios únicos, e a comparação bruta entre genes é confundida por comprimento, densidade de janelas e modelo. Os TPM não são mensurações empíricas de rim normal e não estimam fold change tumoral. Nenhuma inferência de prognóstico ou significância TCGA foi realizada na sessão que produziu este piloto.

## Produtos anexos

1. `Pesquisa_ccRCC_Genomic_Intelligence_Colab.ipynb`: notebook com resultados-piloto, conexão Ensembl/REST opcional, testes automatizados e orquestração R.
2. `TCGA_KIRC_SDD_TDD.R`: pipeline R de extração, controle de amostras, DESeq2, MUI, modelo LASSO-Cox e validação timeROC. Requer execução com rede e bibliotecas R; não foi executado nesta sessão.
3. `Resultados_Piloto_Genomic_Intelligence.tsv`: métricas reais obtidas via plugin.

## Referências (ABNT)

THE CANCER GENOME ATLAS RESEARCH NETWORK. Comprehensive molecular characterization of clear cell renal cell carcinoma. **Nature**, v. 499, p. 43–49, 2013. DOI: https://doi.org/10.1038/nature12222.

COLLINS, Gary S. et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. **BMJ**, v. 385, e078378, 2024. DOI: https://doi.org/10.1136/bmj-2023-078378.

MCSHANE, Lisa M. et al. Reporting recommendations for tumor marker prognostic studies (REMARK). **Journal of the National Cancer Institute**, v. 97, n. 16, p. 1180–1184, 2005. DOI: https://doi.org/10.1093/jnci/dji237.

GENOMIC INTELLIGENCE. **REST API**. Disponível em: https://docs.genomicintelligence.ai/rest-api. Acesso em: 20 out. 2026.

GENOMIC INTELLIGENCE. **Tasks**. Disponível em: https://docs.genomicintelligence.ai/tasks. Acesso em: 20 out. 2026.
