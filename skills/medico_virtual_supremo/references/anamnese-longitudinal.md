# Anamnese longitudinal e reconstrução retrospectiva — v3.0

Aplicar ao reconstruir história clínica, comparar exames ao longo do tempo, investigar evolução ou atender pedido de “rastreio forense reverso”. Usar essa expressão somente como metáfora de revisão documental. Não alegar perícia médico-legal, prova de culpa/negligência ou cadeia de custódia certificada.

## 1. Delimitar o caso

Confirmar a vinculação dos documentos ao mesmo paciente e episódio com o mínimo de dados necessário. Usar identificador local pseudonimizado, por exemplo P01; não solicitar CPF ou endereço completo. Se houver pacientes diferentes ou identificação incerta, separar os conjuntos e impedir que sejam combinados em uma conclusão.

Usar a versão atual dos arquivos. Memórias de conversas, resumos anteriores e respostas de IA são pistas para recuperar fontes; não equivalem a achados clínicos confirmados. Não importar automaticamente dados de terceiros, familiares ou outro caso. Quando a fonte original não estiver disponível, atribuir expressamente o dado ao relato/resumo e reduzir a confiança na documentação.

## 2. Anamnese adaptativa

Organizar, conforme a pergunta: queixa e objetivo do paciente; início e evolução; sintomas associados e repercussão funcional; doenças/diagnósticos prévios e sua fonte; cirurgias, internações e procedimentos; medicamentos, suplementos, início/alteração e adesão relatada; alergias e reação; antecedentes familiares relevantes; exposições ocupacionais/ambientais, viagens e hábitos; saúde reprodutiva quando pertinente; contexto social, apoio, preferências e acesso ao cuidado.

Reaproveitar os dados disponíveis. Fazer até três perguntas prioritárias por rodada, começando pelas que alteram urgência ou interpretação. Informação sensível só quando necessária, explicando sua pertinência. Não usar um questionário exaustivo como condição para uma resposta útil.

## 3. Livro de evidências

Cada fonte recebe um ID estável dentro do caso. Conservar o documento original e registrar:

| Campo | Regra |
| --- | --- |
| `source_id`, `source_type` | Identificar laudo, consulta, prescrição, relato, resumo ou outra origem |
| `source_locator`, `page_or_section` | Arquivo/versão/página ou mensagem; usar null quando desconhecido |
| `document_date`, `received_date` | Distinguir data do documento da de recebimento; não inventar |
| `patient_key`, `episode_id` | Vínculo local; impedir fusão automática de pacientes |
| `original_excerpt`, `extraction_method` | Trecho mínimo necessário; manual/OCR conforme realmente observado |
| `legibility`, `verification_state` | Conferido na fonte, só relatado, ilegível, contraditório ou não conferido |

Hashes servem apenas à integridade de bytes quando efetivamente calculados. Não demonstram autenticidade médica ou veracidade do conteúdo. Não inventar hash, carimbo de tempo ou assinatura.

## 4. Eventos e linha do tempo

Separar data do acontecimento, data da coleta, data do resultado e data do registro. Registrar precisão como exata, aproximada, intervalo ou desconhecida. Não converter “há alguns meses” em dia exato nem ordenar eventos de data desconhecida como se fossem certos.

Para cada evento, registrar `event_id`, `patient_key`, `episode_id`, `event_time`, `time_precision`, `recorded_time`, `event_type`, `description`, `information_state`, `source_refs`, `value`, `unit`, `reference_interval`, `method`, `status` e `conflicts` quando aplicáveis. Campo desconhecido fica null/“não informado”; não zero, normal ou falso.

Estados de informação: relato; achado documentado; negativa explícita; diagnóstico atribuído à fonte; hipótese; não informado; não avaliado; contraditório. Estados do problema: ativo, resolvido conforme fonte, recorrente ou situação atual desconhecida. Uma prescrição antiga não comprova uso atual, e ausência de nova menção não comprova resolução.

Apresentar a cronologia com colunas suficientes: data/precisão, evento ou mudança, fonte e limite da interpretação. Agrupar duplicatas sem apagar a origem. Preservar versões conflitantes de dose, alergia, data, unidade ou diagnóstico até esclarecimento. Medidas de métodos/unidades diferentes só entram numa tendência após conferência e, se necessária, conversão reproduzível que preserve o original.

## 5. Reconstrução reversa e conferência para a frente

1. Partir da queixa ou achado atual e delimitar o que se busca explicar, sem assumir causa única.
2. Retroceder até o primeiro indício documentado, o último estado basal conhecido e os pontos de mudança. Buscar exames prévios relevantes, exposições, início/alteração de medicamentos, intervenções, recorrências e lacunas.
3. Para cada ligação candidata, verificar se a exposição precede o desfecho, se há intervalo biologicamente plausível segundo fonte pertinente, explicações alternativas e informação faltante. Não retroprojetar o diagnóstico atual em sintomas antigos inespecíficos.
4. Distinguir fator de risco, possível gatilho, mecanismo proposto, consequência, coincidência e achado incidental. Rotular causalidade como hipótese salvo documentação/evidência que a sustente; temporalidade isolada não prova causa.
5. Refazer a sequência do passado ao presente e procurar incompatibilidades. Um evento posterior não explica o início anterior sem justificativa específica. Separar início da doença, agravamento e detecção tardia.
6. Descrever o que é observado, o que é plausível e o que não pode ser inferido. Não preencher lacunas para criar uma narrativa contínua. Perguntar apenas pelo documento/dado com maior potencial de mudar a interpretação.

Resposta ou piora após tratamento pode ser relevante, mas não é prova causal isolada. Não propor suspensão, reexposição ou “teste terapêutico” não supervisionado para demonstrar uma hipótese. Contrafactuais são cenários de discussão; não revelam o que teria ocorrido de fato.

## 6. Mapa de relações

Construir um grafo conceitual apenas se ajudar a explicar relações. Não declarar banco de grafos executado quando houver somente uma tabela/diagrama.

Nós possíveis: evento, sintoma, exame, diagnóstico documentado, hipótese, medicamento/exposição, intervenção e desfecho. Arestas permitidas: `precede`, `coincide`, `documentado_em`, `sustenta`, `contradiz` e `possivel_relacao`. Toda aresta interpretativa deve ter fontes, justificativa breve, alternativas e grau de incerteza. Relação extraída por IA não é um fato validado automaticamente.

Não transformar pontuação de similaridade vetorial, frequência de menção, centralidade ou confiança de extração em probabilidade de doença. Se os dados forem insuficientes, entregar uma linha do tempo parcial e uma lista de lacunas, sem inventar uma rede completa.

## 7. Atualização e persistência

Ao receber nova informação, vincular à fonte, registrar correção e mostrar o que mudou nas hipóteses/prioridades. Manter o histórico anterior como superado ou contestado, sem apagar silenciosamente. Decisões passadas devem ser avaliadas com os dados disponíveis naquela época, evitando viés retrospectivo.

Organizar o histórico no contexto atual não garante memória permanente, prontuário, lembrete ou monitoramento. Para salvar/exportar um dossiê solicitado, usar o mecanismo real disponível, manter acesso adequado e confirmar o resultado observado. Não enviar dados clínicos para repositórios públicos, telemetria, memória global entre pacientes ou provedores externos sem autorização específica para o destino e finalidade. Não alegar criptografia, segregação, exclusão ou conformidade apenas porque uma implantação é “offline”.

## 8. Entrega proporcional

Em caso extenso, entregar: resumo clínico; linha do tempo; pontos de mudança; relações plausíveis e contraditórias; hipóteses integradas; documentos/lacunas prioritários; próximo passo para revisão profissional. Uma tabela de hipóteses deve separar achados a favor, contra e ainda desconhecidos.

Ao usuário leigo, explicar a história em linguagem simples e destacar duas ou três pendências decisivas. Ao profissional, acrescentar `source_register`, `timeline`, `relationship_map`, `unresolved_conflicts`, `hypothesis_revisions` e `follow_up`. Esses campos organizam evidências; não representam um prontuário oficial ou laudo pericial.
