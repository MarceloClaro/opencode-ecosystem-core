---
spec_id: SPEC-935-R408
title: Auditoria reprodutível e reconstrução editorial do artigo sobre educação e armadilha da renda média
component: academic/papers/arm_education_audit
status: in_progress
test_file: tests/test_r408_arm_article_audit.py
---

# SPEC-935-R408 — Auditoria reprodutível do artigo ARM–educação

**Data:** 2026-08-12  
**Pedido:** revisar o artigo, reproduzir e auditar dados e citações reais,
corrigir o necessário para publicação e realizar validação cruzada.  
**Artefatos recebidos:**

| Artefato | Caminho somente leitura | SHA-256 |
|---|---|---|
| Manuscrito | `/mnt/c/Users/marce/Downloads/artigo_arm_QUALIS_A1_MASTER.docx.md` | `df829326937baee115899a5070b1d8e50a234d3b1d127106fbf39ef5d24d7378` |
| Ficha técnica | `/mnt/c/Users/marce/Downloads/Ficha_Tecnica_Medico_Virtual_Supremo_v4.pdf` | `8e7dcb47b397a4c53a42c69a0a10b4da06ab6e3e92b4ffbfe040c5f8291a67b5` |

## 1. Enquadramento epistêmico

1. O manuscrito é um objeto a auditar, não evidência de que seus próprios
   números estejam corretos.
2. A ficha do *Médico Virtual Supremo v4.0* declara ser protótipo/PoC sem
   validação clínica externa. Ela será usada apenas como inspiração para os
   princípios `associação ≠ causalidade`, rastreabilidade e *fail-closed*;
   não valida dados, estatística, referências ou qualidade editorial do
   artigo econômico.
3. “Qualis” classifica veículos/periódicos, não manuscritos. Nenhuma saída
   será denominada “artigo Qualis A1” ou “pronta para publicação” sem revisão
   humana, aderência ao periódico escolhido e avaliação por pares.
4. Resultados antigos sem código, dados e definição inequívoca do estimando
   serão classificados como **não reproduzidos**, nunca ajustados por
   tentativa e erro para coincidir.
5. O original no volume Windows não será sobrescrito.

## 2. Diagnóstico RED que motiva a reconstrução

Antes da implementação, a auditoria independente encontrou bloqueadores:

- 448 é a grade teórica `7 países × 64 anos`, não 448 observações completas
  em cada variável;
- país-ano foi tratado como unidade independente, produzindo
  pseudorreplicação e ignorando autocorrelação e clusters nacionais;
- `StratifiedKFold` por linha permite anos do mesmo país em treino e teste;
- o rótulo ARM é ambíguo e pode conter circularidade ou informação futura;
- `ρ²` foi interpretado indevidamente como variância predita;
- `d = 16,06` para PISA usa variação entre médias agregadas e foi transposto
  indevidamente para distribuições de estudantes;
- gasto/PIB teve Pearson não significativo, mas Spearman significativo, e a
  conclusão selecionou apenas o primeiro;
- o texto contém contradições entre tabelas, amostras, períodos e hipóteses;
- não foi fornecido repositório, commit, dataset, dicionário, logs ou código
  que reproduza as Tabelas 1–6;
- alegações de causalidade, necessidade, ineditismo e validade externa
  excedem o desenho.

O estado inicial é, portanto, **RED / publicação bloqueada**.

## 3. Escopo de implementação

Será criado `academic/papers/arm_education_audit/` com quatro camadas:

1. **Proveniência:** manifesto dos originais, fontes, consultas, datas,
   licenças, hashes e ambiente.
2. **Dados:** snapshot imutável de fontes oficiais, grade país-ano e painel
   processado; cada célula deverá conservar fonte e estado
   observado/ausente. Interpolação e extrapolação ficam proibidas na análise
   principal.
3. **Análise:** reprodução exata quando os artefatos permitirem; caso
   contrário, reconstrução diagnóstica explicitamente rotulada. A unidade de
   inferência, dependência por país, tempo, dados faltantes, *look-ahead* e
   *leakage* deverão ser tratados.
4. **Editorial:** relatório forense, matriz alegação–evidência, auditoria de
   referências únicas, versão revisada em Markdown e instruções de submissão.

## 4. Fontes e variáveis permitidas

### 4.1 Banco Mundial

Somente a API oficial `https://api.worldbank.org/v2/`, com códigos de
indicador explícitos, resposta bruta preservada, data/hora UTC, URL completa,
status HTTP e SHA-256. O núcleo mínimo será:

- `NY.GDP.PCAP.KD` — PIB per capita, US$ constantes;
- `NY.GDP.PCAP.KD.ZG` — crescimento anual do PIB per capita;
- `SE.TER.ENRR` — matrícula bruta terciária;
- `SE.XPD.TOTL.GD.ZS` — gasto público em educação/PIB;
- `GB.XPD.RSDV.GD.ZS` — P&D/PIB;
- `SI.POV.GINI` — índice de Gini;
- `SP.DYN.LE00.IN` — expectativa de vida;
- `SP.URB.TOTL.IN.ZS` — urbanização;
- `NV.IND.MANF.ZS` — manufatura/PIB;
- `BX.KLT.DINV.WD.GD.ZS` — IDE líquido/PIB;
- `TX.VAL.TECH.MF.ZS` — exportações de alta tecnologia.

Países: `ARG`, `BRA`, `CHL`, `CHN`, `KOR`, `SGP`, `VNM`; período:
1960–2023. O snapshot corrente não será falsamente descrito como idêntico ao
estado da API em 17/03/2026.

### 4.2 OECD PISA

Serão usados valores de fonte oficial identificável, preservando ano,
domínio, unidade geográfica, erro-padrão quando disponível e limitações de
comparabilidade. A China subnacional não será representada como média
nacional. Sem microdados e pesos replicados, serão reportadas diferenças de
pontos entre estimativas nacionais — não Cohen `d` estudantil nem percentis
individuais.

### 4.3 Barro–Lee e fontes adicionais

Só entram na versão analítica se arquivo oficial, versão, URL, licença e hash
forem obtidos. Valores quinquenais não serão convertidos em observações
anuais independentes. Fonte não recuperada vira limitação e a variável é
retirada, não preenchida manualmente.

## 5. Protocolo estatístico e de validação cruzada

### 5.1 Descritivo principal

- reportar, para cada país e variável, média/mediana do período definido,
  primeiro e último ano observado e `n` de valores realmente observados;
- distinguir grade de 448 linhas da contagem válida de cada variável;
- não atribuir p-valores de linha independente a descrições do painel.

### 5.2 Associações exploratórias

- correlações brutas em níveis serão exibidas apenas como diagnóstico de
  replicação e marcadas como vulneráveis a tendência/pseudorreplicação;
- análise principal deverá usar transformação temporal adequada
  (diferenças/taxas), efeitos de país e ano quando identificáveis, exposição
  defasada e sensibilidade *leave-one-country-out*;
- com sete clusters, inferência será declarada frágil; coeficientes, intervalos
  e estabilidade terão prioridade sobre dicotomização por `p`;
- nenhuma associação será descrita como mecanismo, causa ou condição
  necessária/suficiente.

### 5.3 Machine learning

- a AUC original só pode ser mantida como resultado reproduzido se houver
  dataset, alvo e código originais;
- a auditoria comparará, quando possível, divisão ingênua por linha com
  validação agrupada por país e bloqueio temporal;
- imputação e transformação deverão ocorrer dentro dos folds;
- serão exigidos baseline, ablação de renda/tempo, predição *out-of-country*,
  incerteza e descrição inequívoca do alvo;
- se o evento tiver apenas sete países e poucos escapes, o RF será removido
  da versão científica e mantido apenas no relatório como demonstração de
  não identificabilidade.

## 6. Auditoria bibliográfica

Cada referência única receberá:

- chave estável;
- metadados citados e metadados verificados;
- DOI/ISBN/URL normalizado;
- status `confirmed`, `corrected`, `partial`, `not_verified` ou `rejected`;
- qualidade da fonte e correspondência com a alegação;
- evidência usada na verificação e data de acesso.

Resolver DOI ou abrir uma página não basta para afirmar que a fonte sustenta
uma frase. Alegações factuais de alto risco terão matriz localizada
alegação→fonte→trecho/tabela→limite de uso. Citações ausentes da lista final e
notas repetitivas serão corrigidas para sistema autor–data coerente.

## 7. Entregáveis

1. `SOURCE_MANIFEST.json` — hashes e imutabilidade dos originais.
2. `README.md` — execução, ambiente, limites e mapa dos artefatos.
3. `data/raw/manifest.json` + snapshots oficiais permitidos.
4. `data/processed/panel_wdi_1960_2023.csv` e dicionário de dados.
5. `outputs/reproduction_matrix.csv` — número antigo, número refeito,
   diferença, status e decisão editorial.
6. `outputs/citation_audit.csv` e `outputs/claim_evidence_matrix.csv`.
7. `RELATORIO_AUDITORIA.md` — achados, severidade, rastreabilidade e gate.
8. `MANUSCRITO_REVISADO.md` — texto corrigido e calibrado, sem resultados
   bloqueados; rótulo explícito de versão candidata à revisão humana.
9. `scripts/` — coleta, validação, análise e geração das tabelas.
10. `environment/requirements.txt` ou equivalente versionado.
11. Evidências TDD e relatório de testes.

## 8. Critérios de aceitação

1. Os dois hashes de entrada são testados e os arquivos originais permanecem
   inalterados.
2. Testes RED são escritos antes dos scripts de produção e demonstram falhas
   em: fonte não oficial, hash ausente, duplicata país-ano, valor fabricado,
   leakage por país e resultado sem proveniência.
3. Toda requisição oficial é cacheada com URL, timestamp, status e SHA-256;
   uma nova execução pode operar offline sobre o cache.
4. O painel tem exatamente uma linha por país-ano na grade, sem converter
   ausência em zero, sem interpolação silenciosa e com contagens por variável.
5. Todas as tabelas e números mantidos no manuscrito são gerados por script e
   aparecem na matriz de reprodução.
6. O `d = 16,06`, o percentil individual, os p-valores de pseudorreplicação e
   a AUC 0,997 são removidos da versão científica, salvo reprodução e
   validação que superem os gates desta spec.
7. Nenhum resultado de CV aleatória por linha é rotulado como validade
   externa; países do teste não podem aparecer no treino no teste agrupado.
8. Todas as referências únicas são contabilizadas; DOI/URL e pertinência são
   campos distintos e incerteza nunca é convertida em confirmação.
9. Título, resumo, discussão e conclusão usam linguagem associativa e
   exploratória compatível com o desenho.
10. “Qualis A1”, “validado”, “inédito”, “necessário”, “suficiente”, “confirma”
    e equivalentes não aparecem como alegações de mérito sem evidência externa.
11. O relatório declara que a ficha clínica é um protótipo e não valida o
    artigo econômico.
12. A suíte direcionada passa; o gate final distingue testes internos de
    revisão humana/por pares e mantém publicação bloqueada se qualquer achado
    crítico permanecer.

## 9. Fora de escopo

- inventar dados ausentes ou reconstruir por aproximação números não
  rastreáveis;
- prometer aceitação em periódico;
- converter o artigo automaticamente ao formato final de um periódico antes
  de o autor escolher um único alvo e revisar autoria, afiliação, conflitos,
  ética e disponibilidade de dados;
- usar o protótipo clínico como certificador científico.
