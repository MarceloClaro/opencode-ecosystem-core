# Protocolo pré-análise R934 — ccRCC / TCGA-KIRC

**Status:** protocolo para revisão; consulta metadata-only ao GDC concluída em
2026-10-21, sem download de arquivo ou análise, e nenhum resultado observado.
A autorização do operador cobre somente dados públicos/open-access do GDC para
este estudo.
Os números no manuscrito-fonte são resultados não verificados e não entram
como dados, metas ou achados deste protocolo.
Este protocolo precisa completar seu próprio ciclo RED→GREEN antes da consulta
ao GDC; o GREEN documental não equivale a GREEN do pipeline de análise.

## Pergunta primária

Entre pacientes com tumor primário de carcinoma renal de células claras no
TCGA-KIRC e desfecho de sobrevida global (OS) avaliável, um modelo de risco
transcriptômico baseado em uma lista metabólica predefinida melhora a discriminação
prognóstica em cinco anos, comparado a um modelo clínico-base com idade, sexo e
estágio AJCC, numa partição interna de validação mantida fechada até o modelo
ser congelado?

**Objetivo primário:** estimar a diferença na AUC dependente do tempo de 5 anos
entre modelos clínico-base e clínico-metabólico, com intervalo de confiança.
Reportar também C-index, Brier e calibração como medidas secundárias. Não há
limiar de superioridade nem resultado esperado que transforme um achado nulo,
impreciso ou desfavorável em falha computacional. A diferença de AUC será
estimada com IC e sem limiar de superioridade. Nenhum resultado biológico é gate de sucesso do pipeline.

## Objetivos secundários

1. Descrever a diferença do escore MUI entre tumor primário e tecido renal
   normal disponível, preferindo pares do mesmo paciente e reportando também
   a análise não pareada quando aplicável. Esta é uma comparação descritiva.
2. Estimar, apenas como análise exploratória, a associação do escore metabólico
   congelado com assinaturas de expressão imune predefinidas no holdout; aplicar
   FDR à família de testes declarada antes da análise.

“Imunometabólico” não significa que transcriptômica bulk mede fluxo metabólico,
infiltração celular ou exaustão funcional. Expressão/ssGSEA são associações de
assinaturas transcriptômicas; não demonstram causalidade nem mecanismo celular.
O resultado é uma associação transcriptômica, não é medida de fluxo metabólico,
não demonstra infiltração celular e não demonstra causalidade.

## Fonte de dados e autorização

- Projeto: TCGA-KIRC, Genomic Data Commons (GDC).
- RNA-seq candidato: Gene Expression Quantification, workflow STAR Counts,
  amostras `Primary Tumor` (código de barcode TCGA 01); `Solid Tissue Normal`
  (código 11) somente para o objetivo descritivo tumor-normal. O metadata GDC
  fornece termos de tipo de amostra, não presumir que os valores são `01`/`11`.
- Consultar primeiro apenas metadados e manifesto. Usar filtro de acesso
  **open-access** por arquivo. Exigir GDC file UUID, nome/tipo, workflow,
  release/versão, estado de acesso, checksum (MD5/SHA-256 quando fornecido),
  bytes e data/URL da consulta. Registrar identificadores de paciente apenas
  no mínimo necessário à deduplicação, nunca em texto público.
- Emitir um inventário de metadados GDC antes de qualquer download de conteúdo;
  registrar explicitamente a versão do GDC e as datas de consulta.
- Schema conferido em 2026-10-20 contra a documentação oficial de busca GDC
  <https://docs.gdc.cancer.gov/API/Users_Guide/Search_and_Retrieval/> e os mapas
  <https://api.gdc.cancer.gov/files/_mapping> e
  <https://api.gdc.cancer.gov/cases/_mapping>. A documentação demonstra o
  endpoint `/files`, `from`/`size`, `fields`, `data.pagination.total`, campos de amostra e
  barcode de aliquota (`aliquot_id` e `submitter_id`). Os mapas oficiais
  confirmam `files.access`, `files.file_size`, `files.md5sum`,
  `files.analysis.workflow_type` e `files.analysis.workflow_version`; exemplos
  de resposta `/files` expõem `version` e `data_release`. O guia também documenta
  `/files/versions`: cada versão ativa tem sua própria lista `latest_release`.
  `version` e `data_release` são metadados distintos; faixas `data_release`
  diferentes podem ter releases comuns e não exigem igualdade textual. Consulta
  metadata-only de coorte foi executada. Em 2026-10-21, registrou 614 file IDs
  únicos; 605 foram selecionados antes da exclusão autorizada. A API de data dictionary usada numa tentativa inicial
  (`/data_dictionary/v1`) retornou 404 e não é fonte deste contrato. O resumo
  delimitado desta conferência está em
  `outputs/core-r934/gdc-schema-audit.json`; corpos externos e hashes-fonte não
  foram preservados, e a consulta ao schema deve ser revalidada no manifesto.
- O inventário consultará somente o GDC /files endpoint. Filtros pretendidos:
  `cases.project.project_id = TCGA-KIRC`, `files.data_category = Transcriptome Profiling`,
  `files.data_type = Gene Expression Quantification`,
  `files.analysis.workflow_type = STAR - Counts`, `files.access = open` e
  `files.state = released`. Validar
  os filtros contra o schema oficial na requisição; se o filtro/field não existir
  ou retornar ambiguidade, parar e corrigir o protocolo; nunca relaxar `open`.
  Filtrar no metadata recuperado `Primary Tumor` e `Solid Tissue Normal`; não usar filtro literal 01/11, que são códigos no barcode. A lista de arquivos permanece open-only.
- Pedir apenas metadata: `file_id`, `file_name`, `file_size`, `md5sum`, `access`,
  `state`, `data_category`, `data_type`, `analysis.workflow_type`,
  `analysis.workflow_version`, `version`, `data_release`, `cases.project.project_id`,
  `cases.case_id`, `cases.submitter_id`, `cases.samples.sample_type`,
  `cases.samples.sample_id`, `cases.samples.submitter_id`,
  `cases.samples.portions.analytes.aliquots.aliquot_id` e
  `cases.samples.portions.analytes.aliquots.submitter_id`. aliquot_id é UUID GDC;
   aliquot submitter_id é barcode (campo cases.samples.portions.analytes.aliquots.submitter_id).
   O `version` do endpoint `/files` é a versão ativa do file; consultar
   `/files/versions` para cada arquivo selecionado a fim de validar latest
   ID/versão/MD5/tamanho e obter a lista exata `latest_release`. Usar
   `from`/`size`; pagination até data.pagination.total; reconciliar hits, bytes
   e duplicatas. A compatibilidade de release é a interseção das listas latest_release, não
   igualdade textual de `data_release`. Requisição somente metadata; sem file content.
   A consulta metadata-only de coorte foi executada contra `api.gdc.cancer.gov`
   com pagination até data.pagination.total, retornando 614 file ids únicos e
   somente metadata; sem file content. Nenhum arquivo foi baixado.
- Saída outputs/core-r934/gdc-manifest.json: escrever o manifesto com schema e
  campos efetivamente suportados, filtro serializado, endpoint, versão GDC,
  data/hora UTC, data.pagination.total, contagem/páginas, arquivos, acesso, tamanhos e
   checksums. Gerar uma linha por file_id; manter os metadados associados a sample_id/aliquot_id como relação explícita. Exigir exatamente um sample_id e um aliquot_id por data file. Se houver múltiplos sample_id ou múltiplos aliquot_id, sample_id ou barcode de aliquota ausente, ou vinculação ambígua, não baixar esse file_id até resolver. Reconciliar data.pagination.total igual a file_id únicos antes do filtro local; tamanho agregado soma file_id únicos, sem duplicar joins. Tamanho ou md5sum ausente pausa; valor inválido também pausa. Version é atributo por file_id, não exige homogeneidade entre arquivos, e deve ser validada no endpoint `/files/versions`. O `data_release` é proveniência por arquivo: data_release por arquivo, com a faixa textual preservada como metadado do arquivo e a compatibilidade decidida pela interseção das listas `latest_release`. Exigir workflow_version uniforme na coorte primária, exceto a única exclusão autorizada abaixo; outras divergências pausam. Não exigir igualdade textual de `data_release`: calcular a interseção das listas `latest_release` exatas dos arquivos selecionados, registrar `common_data_releases` e fixar o release comum mais recente. Interseção vazia pausa. O md5sum do GDC será conferido após transferência; gerar SHA-256 local pós-download. Nenhum download sem access=open e state=released. O manifesto não prova que conteúdo foi baixado.
- Excluir qualquer arquivo controlled-access, arquivo sem status inequívoco,
  arquivo não necessário ou material que requeira credencial/dbGaP. Não tentar
  contornar controles. Proibido publicar dados individuais.
- O script fornecido não será executado; não instalar pacotes automaticamente;
  não publicar dados. Por autorização explícita do operador em 2026-10-21, o
  runtime Colab pode montar o Google Drive apenas para persistência sob uma pasta
  única com timestamp UTC, sem sobrescrever execuções anteriores. Dataset,
  logs e saídas ficam dentro dessa pasta versionada. A autorização não abrange
  executar esse pipeline Markdown nem usar seus resultados; a análise será
  escrita em um pipeline original, isolado e versionado.

### Limite operacional de aquisição

Emitir manifesto open-access antes de qualquer download de conteúdo. A primeira
etapa é consulta de metadados/manifesto, sem baixar conteúdo. Só depois
de validar que todos os itens são open-access, o download autorizado pode ser
considerado. Por autorização explícita do operador em 2026-10-21, o limite é
**6 GiB agregados (6 × 1024³ bytes)**, substituindo o teto anterior de 2 GiB.
Se o manifesto exceder 6 GiB, ou qualquer item não for claramente open-access,
**pausar e pedir nova decisão humana antes de qualquer download de conteúdo**.
Esta autorização não resolve incompatibilidade workflow/release nem altera a
coorte; esses bloqueios continuam exigindo decisão humana separada. Não é uma
medição de espaço livre em disco nem promessa de que os arquivos caberão no
ambiente disponível.
Regra fail-closed: sem execução da análise antes do GREEN do protocolo e do registro da revisão metodológica pertinente.

### Exclusão metadata-only autorizada

Em 2026-10-21, o operador autorizou excluir da coorte primária somente o arquivo
GDC `2b0106c5-7e32-423b-957f-06c9f2e7751b`. Seu `workflow_version`
(`5a02c12930eb23436322a7494047b907b97570c5`) difere do workflow uniforme do
grupo principal (`5d8c131bbff59fb0c969217fc1d44e6d1503cd1f`). Seu intervalo
`data_release` (`36.0-46.0`) se sobrepõe ao intervalo principal
(`32.0-46.0`); as listas exatas `latest_release` do inventário original
confirmam releases comuns `36.0`–`46.0`. Portanto, a faixa textual de release
**não** é motivo de exclusão. A justificativa autorizada é exclusivamente a
diferença de proveniência do workflow: sem demonstração de equivalência entre
versões distintas do STAR Counts, combiná-las poderia confundir efeitos de processamento/anotação com variação biológica. Esta decisão usa somente metadados, antes de examinar expressão ou desfecho, e não declara o arquivo inválido.
Não há arquivo alternativo para o mesmo paciente/condição; por isso, o paciente
não entra na coorte primária. O manifesto manterá arquivo, checksum, tamanho,
workflow/release, releases disponíveis e rationale como excluídos, fora da soma
de bytes e das análises primárias. Nenhuma outra incompatibilidade é dispensada.

## População, unidade de análise e desfecho

- Unidade da coorte de sobrevida: paciente, nunca aliquota.
- Para o prognóstico, a unidade estatística é o nível de paciente.
- Incluir uma amostra de tumor primário por paciente; manter normais em trilha
  separada para o objetivo secundário. Se houver aliquotas elegíveis repetidas
  por paciente/condição, primeiro exigir arquivo open e released (`access=open`,
  `state=released`), workflow STAR Counts e sample type previsto. Entre as elegíveis,
  ordenar pelo barcode completo da aliquota em ordem lexicográfica crescente e selecionar a primeira, sem consultar OS ou expressão. Reanalisar os pacientes com aliquotas alternativas como sensibilidade; registrar a escolha e razão em manifesto.
- OS: documentar origem temporal, dias até óbito, dias até último
  acompanhamento e indicador de evento a partir dos campos GDC efetivamente
  disponíveis. Tempos ausentes ou não positivos são excluídos segundo regra
  explícita; apresentar diagrama de fluxo e motivos. Não impor corte de 30 dias
  sem justificativa e análise de sensibilidade.
- A análise primária de casos completos (complete-case) será para OS, idade,
  sexo e estágio; usar o mesmo conjunto de pacientes nos modelos comparados. O denominador OS-elegível é o conjunto com OS temporal/status válido antes de excluir por covariável
  clínica. Relatar missingness e fluxo de inclusão e exclusão. Se mais de 10% do
  denominador OS-elegível tiver missingness em qualquer
  covariável clínica do modelo, pausar antes de modelar e emendar o protocolo;
  não imputar nem excluir silenciosamente.

## Integridade e pré-processamento

- Fixar o workflow/versão de anotação; preservar Ensembl ID como identidade
  primária, remover sufixo de versão com tabela de mapeamento registrada e
  verificar colisões. Para contagens de várias linhas que mapeiam à mesma
  entidade gene, **somar contagens brutas inteiras; não calcular média com
  `limma::avereps`**. Registrar linhas excluídas e ambiguidades.
- Validar inteiros não negativos, duplicatas, valores ausentes/infinitos,
  biblioteca zero, correspondência barcode/metadata e unidade paciente.
- Filtragem de baixa expressão, fatores de normalização, transformação,
  centralização e escala usados pelo modelo são estimados só com o discovery
  (e, dentro da seleção de hiperparâmetros, só no fold interno de treino
  pertinente). Para novos samples do holdout, calcular size factors com geoMeans do discovery,
  usando as médias geométricas de referência do discovery; não recalcular size factors no holdout.
   Aplicar transformação congelada para novos pacientes; **não calcular
  `estimateSizeFactors` ou Z-score da distribuição do holdout**.
- Separar PCA/DE/MUI descritivos do modelo prognóstico. Estatísticas calculadas
  em toda a coorte não podem alimentar feature selection nem o preditor.

## Desenho prognóstico, prevenção de leakage e avaliação

1. Congelar o conjunto de pacientes por identificador antes de qualquer
   transformação aprendida: **70% discovery / 30% holdout**, estratificado por
   evento e paciente, com semente `2026`; salvar índices/hashes. Nenhum paciente
   ou aliquota do mesmo paciente pode cruzar partições. Se contagem de eventos
   não suportar o desenho, pausar e emendar protocolo antes de modelar.
2. Fixar painel metabólico e fontes biológicas antes de examinar associação com
   OS. Remover a triagem univariada global pré-CV do script original. Qualquer
   filtragem/seleção, ajuste de parâmetros e escolha de lambda será feito por
   validação cruzada aninhada (nested cross-validation): outer 5-fold em 5 repetições
   e inner 5-fold para lambda, estratificados por evento. Usar semente-base 2026
   e fold IDs salvos para cada dobra/repetição. Todas as
   transformações/seleções são ajustadas dentro do fold interno de treino; se uma
   dobra não tiver eventos ou não for estimável, pausar antes de modelar.
    Escolher lambda.1se como seleção primária e lambda.min como sensibilidade
    somente dentro do discovery. Predições out-of-fold agregadas por repetição
      descrevem estabilidade; outer-fold não escolhe o modelo final. Fazer CV final no full discovery
      com 5 folds/seed 2026; ajustar modelo final em lambda.1se
     usando todo discovery. Lambda.min não avaliado no holdout. O holdout permanece fechado e sem feedback do holdout até modelo e métricas estarem congelados.
    Nenhuma decisão de genes,
   cutoff, modelo ou especificação usa o holdout.
3. Ajustar o Modelo clínico-base e o modelo ampliado (clínico-metabólico),
   ajustados apenas no discovery. Coeficientes e transformação ficam congelados; produzir
   predições congeladas para holdout. Não estimar coeficientes no holdout e
   rotular isso como validação do modelo treinado.
4. Avaliar o holdout uma vez, com estimador AUC cumulative/dynamic com IPCW em 5
   anos como métrica primária. Só estimar AUC de 60 meses se houver seguimento
   até 60 meses, Ghat(60) ≥ 0,10 — Ĝ(60) pela Kaplan-Meier de censura — e pelo menos 10 eventos até 60 meses no holdout.
     Diferenças de AUC com IC percentil 95% por 1.000 reamostragens bootstrap
      pareadas por paciente. Exigir 90% das reamostragens convergentes; abaixo de 90%, não estimar IC confirmatório. Reportar também
   C-index, Brier e calibração com incerteza. Se critérios não forem atingidos,
   reportar não estimável; não mudar o horizonte depois de ver resultados.
5. Uma única divisão interna não é validação externa. Nomograma/calibração
   aparente ou corrigida por bootstrap no discovery não pode ser descrita como
   calibração out-of-sample. Comparação secundária deve usar o mesmo conjunto de
   pacientes, comparadores e predições bloqueadas.

## Balanço, MUI, assinaturas imunes e multiplicidade

- Não usar `p > 0,05` da Tabela 1 para afirmar homogeneidade ou ausência de viés;
  esse resultado não demonstra equivalência. Mostrar distribuição, diferenças
  padronizadas e intervalos/descritivos de idade, sexo, estágio e eventos.
- Painel metabólico candidato, transcrito do rascunho e ainda não congelado:
  **glycolysis** = SLC2A1, SLC2A3, HK1, HK2, HK3, GPI, PFKP, PFKM, PFKL, ALDOA,
  ALDOC, TPI1, GAPDH, PGK1, PGAM1, ENO1, ENO2, PKM, LDHA, PDK1, PDK3, SLC16A3;
  **TCA/OXPHOS** = PDHA1, PDHB, DLAT, DLD, CS, ACO2, IDH1, IDH2, IDH3A, OGDH,
  DLST, SUCLA2, SUCLG1, SDHA, SDHB, SDHC, SDHD, FH, MDH1, MDH2, PPARGC1A.
  PCK1/PCK2 ficam separados como gluconeogênese, não presumidos como TCA.
   As fontes ainda não verificadas para cada lista devem ser auditadas; usar
   fontes biológicas verificadas antes de congelar o painel e consultar resultados.
  Sem triagem Cox univariada; a lista não será filtrada por associação observada
  com OS antes ou fora da validação cruzada aninhada.
- MUI candidato: diferença entre escore predefinido de genes glicolíticos e
  escore de genes TCA/OXPHOS. Será **descritivo tumor-normal**, sem ser usado
  como preditor primário salvo se aprovado em adendo e calculado sem holdout.
  Escores e genes serão fixados/versionados antes da análise; a comparação
  pareada terá método pareado quando a amostra permitir.
- Assinaturas imunes serão chamadas de scores de expressão/ssGSEA. Não usar
  “infiltração de Treg/M2”, “exaustão” ou “remodelamento” como observação medida
  por RNA-seq bulk. Analisar associação no holdout com limitação explícita e
  ajuste FDR para os testes predefinidos.
- Resultados-piloto do Genomic Intelligence originados de sequência de referência
  (promotores, cromatina, splicing ou expressão prevista) são uma linha
  computacional exploratória separada. Não são leituras TCGA, não estimam
  diferença tumor-normal e não entram no modelo prognóstico primário sem adendo,
  proveniência de modelo e validação próprios.
- O relato prognóstico seguirá TRIPOD+AI (2024) e, quando aplicável, REMARK;
  essas diretrizes aumentam transparência de relato, mas não certificam validade,
  baixo risco de viés, validação externa ou utilidade clínica.
- AUC, HR, log-rank, MUI, calibração ou correlação não têm valor pré-fixado para
  aprovar execução. Estimar e reportar resultados com IC, denominadores,
  eventos, censura, missingness e todas as análises previstas, inclusive
  resultados negativos.

## Correções obrigatórias frente ao material fornecido

O rascunho do manuscrito informa previamente MUI `p < 10^-10`, HR `> 1,85`,
AUC `0,79 vs 0,69`, MAE `< 0,05` e outras alegações. Esses números não foram
verificados nem existem nos arquivos fornecidos como dados/logs; ficam
**[NÃO VERIFICADOS — NÃO RELATAR COMO RESULTADOS]** até análise reproduzida.

No script Markdown fornecido, a especificação original exige resultados
direcionais como condição de `assert_tdd`; a triagem Cox é feita antes de
`cv.glmnet`; há modelo Cox ajustado no `test_clin`; a calibração bootstrap ocorre
no discovery; a análise imune combina discovery e holdout; `avereps` é aplicado
às contagens e o holdout estima size factors. Estas operações não fundamentam
as alegações fortes descritas no rascunho e não serão reutilizadas como
verificação do novo pipeline.

O arquivo anexado `Pacote_Pesquisa_ccRCC_Genomic_Intelligence/TCGA_KIRC_SDD_TDD.R`
também foi apenas inspecionado estaticamente e não será executado. Na versão
fornecida, `GDCquery` não filtra explicitamente `access=open`/`state=released` e
`GDCdownload` pode transferir conteúdo sem o manifesto/teto do R934. A etapa
prognóstica executa um `cv.glmnet` no conjunto de treino, mas não demonstra a
validação cruzada aninhada outer/inner prevista neste protocolo. O corte
`OS_days >= 30` também requer justificativa ou remoção antes da execução. O
artefato não demonstra RED→GREEN da análise, nem foi usado para produzir os
metadados GDC deste estudo.

## Gates e parada

| Gate | Critério de passagem | Estado atual |
|---|---|---|
| P0 — protocolo | Método congelado, revisão condicional respondida e aceitação metodológica humana; GREEN documental não equivale a pipeline científico validado | pendente — revisão condicional; correções documentais em curso |
| P1 — manifesto | Inventário metadata-only reconciliado, exclusões/rationale, checksums de metadados, releases comuns e volume ≤ 6 GiB | pendente — regenerar após emendas autorizadas |
| P2 — dados | Download open-only, verificação MD5 do conteúdo e SHA-256 local, fluxo/missingness reprodutíveis | pendente — nenhum conteúdo baixado |
| P3 — pipeline | TDD sintético com contraprovas de leakage e nested CV; transformações somente em treino/folds; holdout lockbox | pendente — pipeline científico não executado nem integralmente testado |
| P4 — análise | Métricas/IC/denominadores e artefatos reexecutáveis; resultados desfavoráveis também reportados; revisão metodológica humana | pendente — nenhum resultado TCGA observado |

Em 2026-10-21 foi realizada consulta metadata-only ao GDC: 614 file IDs únicos,
605 selecionados antes da exclusão autorizada e duas passagens metadata-only
estáveis. O manifesto correspondente à política anterior ainda precisa ser
regenerado para aplicar a exclusão workflow autorizada e registrar a interseção
de releases. A verificação local R934/R935 cobre critérios de documento e
inventário; ela não fecha P0–P4 nem valida a análise científica. Parar se o acesso
não for open, o manifesto exceder 6 GiB, faltar release comum, surgir
incompatibilidade de workflow não autorizada, houver cruzamento de pacientes,
transformação/seleção no holdout, checksum divergente, execução/cleanup incerto
ou faltar revisão/aceite para mudança de escopo.

## Reprodutibilidade e ética

Gerar protocolo versionado, manifesto, hashes, fluxo de inclusão/exclusão,
session info/lock de dependências, sementes, logs, log de inclusões e exclusões,
e outputs com rastreabilidade da execução. Não instalar nem executar código do documento fornecido, nem usar
Google Drive. A análise é observacional, retrospectiva e interna ao TCGA-KIRC.
Não declarar dispensa de IRB nem conformidade institucional sem confirmação da
política aplicável; não é ferramenta clínica nem autoriza decisão assistencial.

**Próxima operação:** regenerar somente o inventário metadata-only com a
exclusão autorizada e o cálculo de releases comuns. Nenhuma transferência de
conteúdo ou execução do pipeline científico nesta etapa.
