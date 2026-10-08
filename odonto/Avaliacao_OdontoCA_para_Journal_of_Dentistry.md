# Avaliação científica atualizada do OdontoCA para o Journal of Dentistry

## Síntese

O trabalho evoluiu de uma prova de execução sintética para uma análise exploratória de predição com dados clínicos públicos reais. A tabela suplementar do estudo de origem foi obtida da versão `e5868fe5664460c7aac1c5b6d7980776ad26b29c` do [repositório dos autores](https://github.com/HuangShiLab/Single-tooth-ECC), com SHA-256 `b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa`. Todas as 11 contagens previstas no notebook foram reproduzidas. Depois de excluir uma transição com intervalo registrado de zero meses, dois modelos clínicos pré-especificados foram avaliados com validação cruzada aninhada e separação por criança.

O modelo clínico-espacial mostrou discriminação interna promissora, mas a vantagem sobre o modelo clínico mínimo não ficou estabelecida pelos intervalos da diferença. Sua calibração ainda é insuficiente para uso de probabilidades individuais em decisões assistenciais. A etapa seguinte é validação externa independente com modelo e variáveis travados.

## Proveniência e coorte

| Etapa | Resultado confirmado |
|:--|--:|
| Registros da planilha pública | 2.504 |
| Crianças na planilha | 89 |
| Registros de dentes individuais | 2.284 |
| Transições entre visitas consecutivas | 1.160 |
| Transições elegíveis de dentes saudáveis | 997 |
| Eventos `H→C` antes da exclusão | 84 |
| Transições com intervalo positivo na análise | 996 |
| Eventos e crianças na análise | 83 eventos; 81 crianças |

O desfecho positivo é a passagem de dente saudável na visita *t* para cariado na próxima visita consecutiva. O seguimento positivo variou de dois a cinco meses, portanto o resultado não representa risco em horizonte fixo. `HostGroup`, estado futuro, tempo até lesão e informações da próxima visita foram excluídos dos preditores.

## Técnica e resultados

O modelo mínimo usou posição dentária, idade, experiência de cárie da criança e contagem de dentes adjacentes cariados, todos na visita *t*. O modelo espacial acrescentou estado clínico atual da criança e campos de nicho e resumos espaciais da planilha. Imputação, codificação e padronização foram ajustadas apenas no treino. Cinco partições externas e três internas mantiveram todas as observações de cada criança no mesmo lado da divisão. A seleção da penalização ocorreu somente nas partições internas.

| Medida, dados reais com validação interna | Clínico mínimo | Clínico-espacial |
|:--|--:|--:|
| PR-AUC / precisão média (IC bootstrap 95%) | 0,166 (0,120–0,246) | 0,178 (0,138–0,239) |
| ROC-AUC (IC bootstrap 95%) | 0,686 (0,618–0,754) | 0,737 (0,660–0,804) |
| Brier | 0,0806 | 0,0754 |
| Inclinação de calibração | 0,516 | 0,605 |

A prevalência foi 0,0833; o Brier de um comparador pela prevalência do treino foi 0,0764. A diferença espacial menos mínimo na ROC-AUC foi 0,051, com intervalo de −0,009 a 0,112; na PR-AUC foi 0,012, com intervalo de −0,046 a 0,058. Ambos incluem zero. As inclinações inferiores a um sugerem probabilidades excessivamente extremas. Os 1.000 bootstraps reamostraram crianças com predições fora da amostra já fixadas; não repetiram o ajuste completo do modelo e, por isso, não incluem toda a incerteza do desenvolvimento.

## Auditoria do notebook e fluxograma

O notebook v1.3.2 salvo executou `CI_SMOKE` em 36 crianças sintéticas, 686 transições e 54 eventos. Seus 24 testes `PASS` e dois `SKIP` não equivalem a uma validação clínica. Um teste de duplicata pode capturar a própria falha; outro teste de separação de pacientes é tautológico; dois gates estão fixados como verdadeiros. Uma nova execução do código atual reproduziu as contagens sintéticas, mas não as métricas salvas. A causa não foi demonstrada porque o ambiente original e o pacote de resultados não estavam disponíveis. As duas séries foram preservadas em [auditoria suplementar](manuscript_assets/Supplementary_Reproducibility_Audit.md), sem serem apresentadas como desempenho clínico.

O [fluxograma compacto](manuscript_assets/Figure_1_pipeline_v2_compact.png) e a [arquitetura detalhada v2.1](manuscript_assets/Supplementary_Architecture_v2_1.mmd) distinguem quatro vias: simulação técnica executada, reprodução e predição clínica interna executadas, microbioma real ainda não pareado e imagens ainda não analisadas. A fusão multimodal exige a mesma criança, visita e posição dentária; resultados de coortes distintas permanecem separados. Validação externa, calibração e avaliação de utilidade clínica são gates antes de qualquer alegação assistencial.

## Artigo e referências

O [manuscrito em inglês](Journal_of_Dentistry_Example_OdontoCA.md) foi reescrito no formato de artigo de pesquisa, com resumo de 245 palavras, sete palavras-chave, tabelas editáveis, figuras separadas e citações numéricas em ordem. Contém **28 artigos relevantes** de odontologia, microbioma e metodologia preditiva. Cada DOI foi consultado no Crossref (HTTP 200) e redirecionou pelo doi.org (HTTP 302) em 30 de setembro de 2026. A [lista conferida](manuscript_assets/references_verified.md) e os [metadados da checagem](manuscript_assets/references_crossref_verified.json) acompanham o artigo.

Antes da submissão, os autores devem confirmar autoria e contribuições, financiamento, conflitos de interesse, situação ética da análise secundária, permissões e depósito permanente de código/dados. O artigo é apropriado para revisão crítica dos autores como estudo de desenvolvimento e validação interna exploratória. A alegação de ferramenta clínica validada depende de coorte externa independente e demonstração de calibração e utilidade.
