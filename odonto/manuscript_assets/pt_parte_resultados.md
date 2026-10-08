## 3. Resultados

### 3.1. Reconstrução da coorte de origem

Todas as 11 verificações de contagens previamente especificadas corresponderam à fonte pública: 2.504 linhas de metadados de 89 crianças incluíam 220 linhas de posições compostas e 2.284 linhas de dentes individuais. O pareamento do mesmo dente da mesma criança gerou 1.388 transições observadas, das quais 1.160 conectavam índices de visitas consecutivos. Estas últimas compreenderam 913 transições `H→H`, 84 `H→C`, 163 `C→C` e nenhuma `C→H`. Assim, a coorte original de incidência continha 997 transições de dentes saudáveis em *t*. A exclusão de um intervalo de acompanhamento não positivo resultou em 996 transições, 83 eventos (8,33%), 81 crianças e 44 crianças com pelo menos um evento (Tabela 1). Os intervalos positivos de acompanhamento apresentaram mediana de dois meses, intervalo interquartil de dois a três meses e amplitude de dois a cinco meses.

**Tabela 1. Reprodução da coorte da fonte publicada e definição do conjunto de análise preditiva.**

| Etapa | Registros | Crianças ou eventos | Interpretação |
|:--|--:|:--|:--|
| Planilha pública `all_metadata` | 2.504 | 89 crianças | Registros da fonte, antes da filtragem dos dentes |
| Posição composta `T5161` | 220 | — | Excluída da modelagem de dentes individuais |
| Linhas de dentes individuais | 2.284 | — | Registros no nível do dente |
| Transições observadas do mesmo dente | 1.388 | — | Quaisquer visitas sucessivas registradas |
| Transições entre índices consecutivos | 1.160 | 913 `H→H`; 84 `H→C`; 163 `C→C`; 0 `C→H` | Aplicação exata da regra do notebook |
| Coorte de incidência com dentes saudáveis em *t* | 997 | 84 eventos | Contagens-alvo da fonte reproduzidas |
| Análise preditiva principal | 996 | 83 eventos; 81 crianças | Exclusão de um intervalo de zero mês |

### 3.2. Desempenho preditivo interno

Nas predições fora da amostra, com agrupamento por criança, o modelo clínico mínimo alcançou precisão média de 0,166 (intervalo de 95% por bootstrap de crianças: 0,120–0,246) e área sob a curva ROC de 0,686 (0,618–0,754). O modelo clínico-espacial alcançou precisão média de 0,178 (0,138–0,239) e área sob a curva ROC de 0,737 (0,660–0,804), com precisão média superior à proporção de eventos de 0,083 (Tabela 2; Figura 2). A diferença entre o modelo espacial e o mínimo foi de 0,012 (−0,046 a 0,058) para a precisão média e de 0,051 (−0,009 a 0,112) para a área sob a curva ROC. Ambos os intervalos incluíram zero; a superioridade do modelo espacial não foi estabelecida.

**Tabela 2. Desempenho agregado das predições fora da amostra, com agrupamento por paciente, na coorte clínica pública real (996 transições; 83 eventos).**

| Modelo | Precisão média (intervalo de 95%) | Área sob a curva ROC (intervalo de 95%) | Escore de Brier (intervalo de 95%) | Perda logarítmica |
|:--|:--|:--|:--|--:|
| Clínico mínimo | 0,166 (0,120–0,246) | 0,686 (0,618–0,754) | 0,0806 (0,0624–0,0996) | 0,2884 |
| Clínico com variáveis espaciais | 0,178 (0,138–0,239) | 0,737 (0,660–0,804) | 0,0754 (0,0574–0,0949) | 0,2690 |
| Prevalência do conjunto de treinamento de cada partição | — | — | 0,0764 | 0,2869 |

![Figura 2. Curvas de precisão–revocação e ROC dos modelos não calibrados sob a política corrigida de divisão por grupos. As predições de cada criança foram produzidas somente quando ela integrava a partição externa de teste. A referência horizontal da precisão corresponde à proporção de eventos da análise (0,083); a diagonal ROC representa a ordenação ao acaso. Estes resultados são internos, e não externos.](manuscript_assets/Figure_2_discrimination_corrected_sklearn190_pt.png){width=6.7in}

### 3.3. Calibração e comparação dos modelos

O modelo mínimo não calibrado apresentou risco médio predito de 0,1182, frente à proporção observada de eventos de 0,0833, calibração global de −0,446 e inclinação de 0,516. Os valores correspondentes do modelo espacial foram 0,0878, −0,066 e 0,605. Inclinações inferiores a um indicam predições excessivamente extremas nesta amostra interna. O gráfico com oito grupos de risco apresenta as versões não calibrada e as duas versões recalibradas exclusivamente com dados de treinamento de cada modelo (Figura 3). O escore de Brier do modelo espacial não calibrado, de 0,0754, foi próximo ao da referência baseada na prevalência do treinamento, de 0,0764; o escore do modelo mínimo, de 0,0806, foi pior. A diferença pareada no escore de Brier entre o modelo espacial e o mínimo foi de −0,0052 (intervalo de 95% por bootstrap: −0,0104 a 0,0004), incluindo zero.

A recalibração do intercepto e da inclinação reduziu o escore de Brier do modelo mínimo para 0,0745: diferença pareada de −0,00610 (intervalo de 95% por conglomerados de crianças: −0,01173 a −0,00067). Sua perda logarítmica passou de 0,2884 para 0,2680, mas o intervalo pareado incluiu zero (−0,04058 a 0,00020). O escore de Brier do modelo espacial passou de 0,0754 para 0,0740: diferença pareada de −0,00141 (−0,00308 a 0,00037), também incluindo zero. A atualização apenas do intercepto não proporcionou melhora pareada clara no escore de Brier de nenhum dos modelos. Essas comparações são exploratórias, condicionais às predições obtidas por ajuste cruzado, e não estabelecem benefício clínico. As inclinações após a recalibração permaneceram inferiores a um (Tabela 3). Não foi definido um limiar de tratamento nem uma regra de decisão clínica.

**Tabela 3. Avaliação das probabilidades nas amostras de teste antes e após a recalibração ajustada exclusivamente com crianças dos conjuntos externos de treinamento. A proporção observada de eventos foi de 0,0833; a incerteza pareada das mudanças no escore de Brier é apresentada no texto.**

| Modelo e versão das probabilidades | Risco médio | Inclinação de calibração | Escore de Brier | Perda logarítmica |
|:--|--:|--:|--:|--:|
| Mínimo, não calibrado | 0,1182 | 0,516 | 0,0806 | 0,2884 |
| Mínimo, apenas intercepto | 0,0819 | 0,613 | 0,0762 | 0,2730 |
| Mínimo, intercepto e inclinação | 0,0802 | 0,808 | 0,0745 | 0,2680 |
| Espacial, não calibrado | 0,0878 | 0,605 | 0,0754 | 0,2690 |
| Espacial, apenas intercepto | 0,0810 | 0,603 | 0,0753 | 0,2690 |
| Espacial, intercepto e inclinação | 0,0827 | 0,811 | 0,0740 | 0,2638 |

![Figura 3. Calibração descritiva das predições em amostras de teste dos dois modelos com dados reais: sem calibração, com atualização do intercepto e com atualização do intercepto e da inclinação. Os pontos representam oito grupos definidos por quantis do risco predito, e a diagonal indica calibração perfeita. Este gráfico agrupado tem resolução limitada e não constitui evidência de calibração externa.](manuscript_assets/Figure_3_calibration_corrected_sklearn190_pt.png){width=6.7in}

### 3.4. Estado técnico dos demais componentes do OdontoCA

A execução sintética salva no notebook original registrou 24 verificações técnicas aprovadas e duas verificações de aceitação com dados reais não executadas. A inspeção do código-fonte identificou um teste de chaves duplicadas que poderia capturar sua própria falha de asserção, um teste de sobreposição de pacientes com condição tautológica e dois critérios de aceitação com resultados fixados no código. A análise clínica independente apresentada aqui utilizou asserções explícitas para garantir a separação das crianças e a exclusão de variáveis futuras. Os escores dos modelos da execução sintética arquivada e da reexecução independente não corresponderam, apesar das contagens idênticas de 686 transições e 54 eventos. Na análise com dados reais, o resultado do Colab do usuário foi reproduzido com scikit-learn 1.6.1; a política corrigida de divisão por grupos no scikit-learn 1.9.0 produziu estimativas internas diferentes. Ambas as diferenças estão documentadas no Arquivo Suplementar S2. Nenhum modelo com dados reais de microbioma do Qiita, modelo de imagens, fusão multimodal vinculada por paciente ou validação clínica externa foi executado para este manuscrito.

## 4. Discussão

### 4.1. Principais achados e potencial para pesquisa clínica

Esta análise faz o OdontoCA avançar de uma demonstração de integração com dados sintéticos para uma reconstrução reprodutível de uma coorte pública e um estudo exploratório de predição com dados clínicos reais. As 11 verificações de contagens demonstram que o desfecho no nível do dente foi reconstruído conforme esperado. A validação interna com agrupamento por paciente produziu discriminação superior ao acaso e precisão média superior à prevalência de eventos em ambos os modelos clínicos. A estimativa pontual mais elevada do modelo espacial é compatível com um possível papel do contexto oral local, mas os intervalos de incerteza pareados incluem zero. A recalibração do intercepto e da inclinação, ajustada exclusivamente com dados de treinamento, reduziu o escore de Brier do modelo mínimo nas amostras de teste; a mudança no escore de Brier do modelo espacial permaneceu incerta. Esses resultados justificam estudos metodológicos prospectivos; não demonstram que as variáveis espaciais ou a recalibração melhorem o cuidado dos pacientes.

### 4.2. Interpretação do desempenho e da calibração

A proporção de eventos foi de 8,33%, de modo que a precisão média teve uma referência de prevalência baixa. A área sob a curva ROC de 0,737 descreve a capacidade de ordenação nesta única coorte. O escore de Brier do modelo espacial não calibrado foi próximo ao de um preditor simples baseado na prevalência, enquanto o escore de Brier do modelo mínimo recalibrado foi menor nesta análise interna. Sua inclinação residual de calibração de 0,808 e o número limitado de crianças mostram que as estimativas de probabilidade ainda precisam ser aprimoradas antes de uma interpretação individual. Atualizações monotônicas específicas de cada partição podem alterar a ordenação agregada entre partições; qualquer mudança resultante na discriminação agregada não deve ser interpretada como informação adicional das variáveis preditoras. A avaliação interna fora da amostra limita parte do otimismo, mas não substitui a avaliação da transportabilidade; o PROBAST destaca questões relativas aos participantes, preditores, desfechos e análise [23]. A análise de curva de decisão poderá, futuramente, quantificar o benefício líquido em limiares clínicos previamente especificados [24], mas realizá-la neste momento poderia levar a uma recomendação de tratamento sem sustentação.

### 4.3. Relação com a literatura sobre microbioma e contexto espacial

O delineamento restrito a variáveis clínicas evita atribuir ao OdontoCA os resultados de microbioma de outro grupo. A modelagem recente de risco com microbioma em um pequeno estudo de caso-controle aninhado [25] acrescenta contexto, mas não constitui um comparador direto, pois o perfil dos participantes, o acompanhamento e a validação diferem. Os achados de microbioma no nível de cada dente do artigo de origem [1] e a estrutura observada das comunidades de placa oral [26] motivam uma extensão com vinculação exata por `SampleID`. Essa extensão deve auditar a qualidade das bibliotecas de sequenciamento, o pré-processamento composicional, o agrupamento por paciente e o desempenho incremental em relação ao modelo clínico de referência. Deve utilizar registros correspondentes de paciente, visita e dente; dados de coortes de imagens ou microbioma sem relação entre si não podem ser combinados para criar um paciente multimodal fictício.

### 4.4. Relato e próxima etapa de validação

A declaração TRIPOD original [27], as orientações atualizadas do TRIPOD+AI [10] e as recomendações práticas para desenvolvimento de modelos [28] sustentam a apresentação completa do fluxo da coorte, dos preditores candidatos, do ajuste de parâmetros, da incerteza e dos desvios do planejamento. A próxima etapa deve fixar o algoritmo clínico-espacial, reconstruir ou documentar de forma independente cada variável espacial derivada a partir de medidas disponíveis na visita de predição e validá-lo em uma clínica efetivamente distinta ou em um período posterior. Um horizonte fixo de predição, limiares previamente especificados, verificações por subgrupos, atualização da calibração e análise de utilidade clínica devem ser planejados antes do teste. O mesmo critério de evidência se aplica aos componentes propostos de imagens e microbioma.

### 4.5. Limitações

A análise utiliza uma única coorte pública e um número modesto de crianças e eventos, com múltiplos dentes por criança. O acompanhamento varia de dois a cinco meses, e o alvo é a próxima visita, em vez de um risco em tempo fixo. As variáveis espaciais provenientes da fonte não foram reconstruídas a partir dos exames brutos, e as informações sobre aquisição, dados ausentes e disponibilidade prospectiva precisam ser verificadas pelos autores. O bootstrap de crianças reamostrou as predições fora da amostra já existentes, em vez de reajustar todos os modelos aninhados; portanto, seus intervalos não incorporam a variabilidade do desenvolvimento dos modelos. Duas formas de calibração foram examinadas sem um conjunto de dados externo independente, e a seleção de uma delas após a observação desses resultados pode superestimar seu benefício futuro. Não houve adjudicação independente dos desfechos, população externa, teste prospectivo do fluxo de trabalho ou análise de benefício líquido. O notebook sintético salvo e a reexecução do código atual produziram métricas diferentes, e o Colab clínico anterior e as políticas corrigidas de divisão produziram estimativas internas diferentes; os resultados executáveis e as versões dos programas devem ser fixados. A acurácia diagnóstica ou preditiva relatada no trabalho original [1] não é um resultado do OdontoCA.

## 5. Conclusão

O OdontoCA reproduziu as contagens da coorte pública no nível do dente e realizou uma predição interna exploratória com agrupamento por criança em registros clínicos reais. O modelo clínico-espacial não calibrado apresentou área sob a curva ROC de 0,737 e precisão média de 0,178, mas sua vantagem sobre um modelo clínico mínimo foi incerta. A recalibração do intercepto e da inclinação, ajustada exclusivamente com dados de treinamento, melhorou o escore de Brier do modelo mínimo nesta coorte; a calibração permaneceu imperfeita e a mudança no escore de Brier do modelo espacial foi incerta. A técnica dispõe de um caminho para avaliação clínica por meio da documentação da proveniência dos preditores, da fixação da modelagem e da validação externa independente; ainda não está pronta para apoiar decisões individuais sobre pacientes.

## Declarações

**Aprovação ética:** Não foram recrutados novos participantes. Foi analisada a tabela suplementar disponibilizada publicamente pelo estudo de origem. Os autores devem confirmar a aprovação ética ou a determinação de dispensa aplicável a esta análise secundária antes da submissão.

**Disponibilidade de dados e código:** A planilha de origem está no [repositório dos pesquisadores originais](https://github.com/HuangShiLab/Single-tooth-ECC); os scripts de reconstrução e análise clínica, os resultados agregados em JSON, as figuras e o hash do arquivo de origem acompanham este manuscrito. Os registros brutos da fonte não são redistribuídos. Um identificador de arquivamento permanente e os termos de reutilização do repositório de origem devem ser confirmados antes da submissão.

**Financiamento:** A ser preenchido e verificado pelos autores.

**Declaração de conflitos de interesse:** A ser preenchida e verificada por cada autor.

**Declaração de contribuições de autoria CRediT:** A ser preenchida com base na lista confirmada de autores e nas contribuições efetivas.

**Declaração de uso de inteligência artificial generativa:** O OpenAI Codex auxiliou na revisão de código, execução da análise secundária, redação do manuscrito, conferência das referências e elaboração dos diagramas. Os autores identificados devem examinar a proveniência dos dados, o código, os resultados numéricos, as citações e o texto final, mantendo a responsabilidade pelo trabalho submetido.

**Material suplementar:** O Arquivo Suplementar S1 contém a arquitetura detalhada com distinção dos níveis de evidência. O Arquivo Suplementar S2 documenta a auditoria do notebook sintético, a discrepância na reexecução e os limites da validação. A análise clínica real com predições fora da amostra é independente dos modelos publicados pelos pesquisadores do estudo de origem.
