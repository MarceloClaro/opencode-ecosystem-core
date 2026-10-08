# Arquivo suplementar S3 — Avaliação de relato TRIPOD+AI

**Estudo:** predição de cárie por dente com OdontoCA, análise secundária com desenvolvimento e avaliação interna agrupada por criança.

**Instrumento:** TRIPOD+AI 2024, lista oficial de 11 de janeiro de 2024: 27 itens numerados, 52 linhas incluindo subitens com letras. Os identificadores correspondem ao original; os rótulos breves são paráfrases e não substituem as recomendações completas. Fonte: Collins et al., *BMJ* 2024;385:e078378, [doi:10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378); [lista oficial](https://www.tripod-statement.org/wp-content/uploads/2019/12/TRIPODAI_checklist.pdf) e [lista de resumos](https://www.tripod-statement.org/wp-content/uploads/2019/12/TRIPODAI-for-Abstracts.pdf).

**Data:** 1 de outubro de 2026. Auditoria interna de relato com assistência de IA; não constitui revisão externa independente, certificação ou escore numérico. Abrange ambos os modelos e a recalibração exploratória. Completude do relato não comprova baixo risco de viés; consulte S4 separadamente.

**Evidências:** seções/tabelas, `real_clinical_prediction.py`, `calibrated_clinical_prediction.py` e `calibrated_clinical_internal_validation_corrected_sklearn190.json`. As localizações por seção valem para ambos os idiomas. **Atendido:** informação suficiente encontrada. **Parcial:** informação existente, com componente ausente. **Ausente:** informação necessária não encontrada. **N/A:** análise condicional não realizada. A conferência pelos autores permanece necessária. Reconhecer uma lacuna não a resolve.

## Título, resumo e introdução

| ID | Tema | Situação | Localização e avaliação |
|---|---|---|---|
| 1 | Título | Parcial | Identifica predição por dente e validação interna; não explicita desenvolvimento de modelo multivariável. |
| 2 | Resumo | Parcial | Apresenta métodos/resultados principais. Conferir versão final com a lista específica de 13 itens; cenário, elegibilidade e registro seguem insuficientes. Limite de palavras não comprova completude. |
| 3a | Justificativa | Atendido | §1 e §4.3 explicam o problema, modelos anteriores e limites das comparações entre coortes. |
| 3b | Uso | Parcial | §§1, 4.1–4.4, 5 definem escopo de pesquisa; faltam usuários futuros e posição no percurso assistencial. |
| 3c | Desigualdades | Ausente | Desigualdades sociodemográficas e sua pertinência para dados/aplicação não são discutidas substancialmente. |
| 4 | Objetivos | Atendido | Final de §1 e §2.1 identificam reconstrução, desenvolvimento, avaliação interna e calibração; não se alega avaliação externa. |

## Métodos

| ID | Tema | Situação | Localização e avaliação |
|---|---|---|---|
| 5a | Fontes | Parcial | §2.1 identifica planilha, repositório, revisão e hash; amostragem e representatividade exigem maior descrição. |
| 5b | Datas | Ausente | Faltam datas de recrutamento e seguimento; publicação ou execução não as substituem. |
| 6a | Cenário | Parcial | §§1–2.1 identificam a fonte longitudinal, mas incompletamente o recrutamento, número de centros e geografia. |
| 6b | Elegibilidade | Parcial | §2.2/Tabela 1 descrevem seleção de transições, mas não todos os critérios originais das crianças. Análise secundária não torna o item inaplicável. |
| 6c | Tratamento | Ausente | Tratamentos odontológicos/preventivos durante o seguimento e seu manejo não são descritos; verificar pertinência e disponibilidade. |
| 7 | Preparação | Parcial | §§2.1–2.4 detalham conferências, reconstrução e processamento; diferenças de qualidade entre grupos demográficos não foram avaliadas. |
| 8a | Desfecho | Parcial | §2.2 define transição saudável–cariado em 2–5 meses; exames diagnósticos e consistência demográfica precisam de verificação. |
| 8b | Avaliadores | Ausente | Qualificações e características relevantes dos examinadores do desfecho não são relatadas. Reutilizar registros não dispensa isso. |
| 8c | Mascaramento | Ausente | Não se documenta mascaramento na avaliação original do desfecho. Ordem temporal não o comprova. |
| 9a | Seleção | Atendido | §2.3 descreve dois conjuntos definidos antes da inspeção de desempenho e sua justificativa. Isso não comprova registro prospectivo. |
| 9b | Mensuração | Parcial | §§2.2–2.3/código identificam campos da visita t e campos futuros proibidos; definições/aquisição de derivados e mascaramento permanecem incompletos. |
| 9c | Avaliadores | Ausente | Qualificações e características relevantes dos examinadores dos preditores não estão documentadas; verificar procedimentos originais. |
| 10 | Tamanho | Parcial | §3.1/Tabela 1 mostram 996 transições, 83 eventos e 81 crianças; falta cálculo de suficiência para complexidade e avaliação agrupada. |
| 11 | Ausências | Parcial | §§2.2–2.3 descrevem exclusões e imputação no treinamento; faltam ausências por variável e eventuais perdas por identificador/desfecho ausente. |
| 12a | Partições | Atendido | §2.4/código apresentam cinco partições externas/três internas, agrupamento por criança, semente, divisão corrigida e conferência de separação. |
| 12b | Codificação | Atendido | §2.3 apresenta codificação categórica, padronização e transformações ajustadas no treinamento. |
| 12c | Ajuste | Atendido | §§2.3–2.4/código especificam regressão logística penalizada, quatro valores de C, seleção por precisão média e avaliação interna aninhada. |
| 12d | Heterogeneidade | Parcial | §2.4 trata dependência por agrupamento/reamostragem; heterogeneidade de parâmetros/desempenho entre grupos não foi quantificada. São análises distintas. |
| 12e | Medidas | Atendido | §2.4 define escores, discriminação, calibração, referências e comparações pareadas; utilidade clínica não foi avaliada. |
| 12f | Atualização | Atendido | §2.4 explica recalibração de intercepto e inclinação positiva no treinamento, predições internas e caráter exploratório. |
| 12g | Predições | Atendido | §2.4/código mostram probabilidades da classe positiva e recalibração do treinamento aplicada a cada partição retida. |
| 13 | Desbalanceamento | Parcial | §2.4 explica precisão–sensibilidade. Código não aplica pesos/reamostragem de classes, mas essa ausência não está explícita no manuscrito. |
| 14 | Equidade | Ausente | Não há abordagem de equidade ou diferenças demográficas de desempenho; não se justifica alegação de equidade. |
| 15 | Saída | Atendido | §§2.2, 2.4, 3.3 definem probabilidades na próxima visita e ausência de limiar terapêutico/regra decisória. |
| 16 | Conjuntos | Atendido | §§2.1–2.4 estabelecem definições/elegibilidade comuns numa coorte, separada por criança. Não existe conjunto externo independente. |
| 17 | Ética | Parcial | Declarações identificam dados públicos secundários; aprovação/dispensa e determinação de consentimento aguardam os autores. |

## Ciência aberta e participação

| ID | Tema | Situação | Localização e avaliação |
|---|---|---|---|
| 18a | Financiamento | Ausente | Declarações mantêm campo a preencher; fontes e papéis dos financiadores aguardam confirmação. |
| 18b | Interesses | Ausente | Conflitos de interesses dependem da confirmação de cada autor. |
| 18c | Protocolo | Ausente | Não há protocolo acessível ou declaração explícita de inexistência; o fluxograma isolado é insuficiente. |
| 18d | Registro | Ausente | Não há registro ou declaração explícita de não registro. Repositório de software não equivale automaticamente a registro do estudo. |
| 18e | Dados | Parcial | Declaração liga a fonte e identifica o arquivo; termos de reutilização e redação definitiva precisam de verificação. |
| 18f | Código | Parcial | Scripts/resultados acompanham o manuscrito; acesso público persistente e reutilização não estão finalizados. Não há DOI de depósito estabelecido. |
| 19 | Participação | Ausente | Participação de pacientes/público ou sua ausência não é relatada. Ausência de recrutamento novo não responde ao item. |

## Resultados

| ID | Tema | Situação | Localização e avaliação |
|---|---|---|---|
| 20a | Fluxo | Parcial | §3.1/Tabela 1 mostram filtros, amostra/eventos/seguimento. JSON contém 44 crianças com evento; distinguir desfechos infantis de transições. |
| 20b | Características | Parcial | §3.1/Tabela 1 dão contagens/seguimento; falta tabela descritiva de preditores, demografia, tratamento e ausências por variável. |
| 20c | Distribuições | Parcial | Partições compartilham a coorte. Registros apresentam contagens, mas não distribuições de preditores entre desenvolvimento e avaliação. |
| 21 | Contagens | Parcial | §3.1/JSON dão totais e crianças/eventos das partições externas; contagens de cada partição interna não são apresentadas. |
| 22 | Especificação | Parcial | Há código de análise reprodutível; não se libera modelo final único, coeficientes/processamento e condições de acesso para implantação. |
| 23a | Desempenho | Parcial | Tabelas 2–3/Figuras 2–3 apresentam estimativas/intervalos selecionados; faltam intervalos de calibração, de todos os escores e subgrupos. Incerteza condicionada às predições existentes. |
| 23b | Heterogeneidade | N/A | Heterogeneidade de desempenho entre grupos não foi examinada; este julgamento condicional não demonstra ausência de heterogeneidade. |
| 24 | Atualização | Parcial | §3.3/Tabela 3/JSON mostram escores atualizados, intervalos selecionados e parâmetros por partição; não há modelo final único para implantação. |

## Discussão e uso

| ID | Tema | Situação | Localização e avaliação |
|---|---|---|---|
| 25 | Interpretação | Parcial | §§4.1–4.4, 5 interpretam diferenças incertas/atualização exploratória à luz da literatura; equidade não é discutida substancialmente. |
| 26 | Limitações | Atendido | §4.5 aborda coorte, tamanho, seguimento, derivados, ausências, incerteza condicionada e atualização exploratória. Declarar limitações não elimina viés. |
| 27a | Entradas | Parcial | §§2.3, 4.4 discutem processamento/disponibilidade prospectiva; falta procedimento clínico para entradas ausentes ou de baixa qualidade. |
| 27b | Usuários | Ausente | Interação, treinamento e conhecimentos para implantação futura não estão definidos; o software permanece ferramenta de pesquisa. |
| 27c | Pesquisa | Atendido | §§4.4, 5 descrevem verificação dos preditores, modelo fixado, validação independente, horizonte fixo, subgrupos e futura utilidade clínica. |

## Providências antes da submissão

Resolver declarações de ética/consentimento, financiamento, interesses, protocolo/registro e participação de pacientes/público. Acrescentar cenário, datas/critérios de recrutamento, mensuração e avaliadores após verificação. Apresentar descrições/ausências e esclarecer contagens por partição, ausência de análise de equidade e situação do modelo final. Reconciliar este mapa com resumo e acesso a dados/código após as edições. Informações indisponíveis devem ser reconhecidas, nunca inventadas.

Esta avaliação substitui o documento anterior com 54 questões, cuja numeração não correspondia ao TRIPOD+AI. Não se conclui suficiência amostral pelos 83 eventos isoladamente; regra de eventos por variável, penalização ou validação agrupada não comprovam baixo viés. A avaliação PROBAST+AI complementar é separada. Este arquivo não altera a sequência de 28 referências do manuscrito.
