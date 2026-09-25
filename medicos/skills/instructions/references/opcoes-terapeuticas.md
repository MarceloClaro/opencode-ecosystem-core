# Comparação de possibilidades terapêuticas — v3.0

Aplicar quando houver pedido de possíveis tratamentos, alternativas, revisão de conduta ou discussão do manejo após o diferencial. Respeitar as regras de emergência e medicamentos do SKILL.md. Organizar opções para decisão compartilhada com profissional habilitado; não emitir receita ou autorização de uso.

## Delimitar a decisão

Identificar o que se busca: aliviar sintoma, investigar causa, modificar doença, prevenir complicação, reabilitar, acompanhar ou revisar uma prescrição existente. Distinguir hipótese ainda não confirmada de diagnóstico documentado. Não aguardar fechamento diagnóstico para orientar atendimento quando houver urgência; a eventual terapêutica urgente cabe à equipe assistencial.

Adaptar ao modo de uso. Para paciente/cuidador, explicar categorias e perguntas para a consulta. Para profissional, detalhar comparação e auditoria com evidências verificadas, sem substituir protocolo local e avaliação direta. A palavra “PhD” ou um pedido de tratamento não comprova habilitação.

## Selecionar alternativas com evidências

Buscar diretriz atual específica e fonte primária aplicável. Conferir data/versão, população, diagnóstico/estágio, desfechos relevantes, benefícios, eventos adversos e limitações. Verificar contraindicações e interações em fonte oficial pertinente. Uma referência geral de IA ou um repositório de agentes não sustenta uma recomendação terapêutica.

Comparar poucas opções pertinentes: medidas não farmacológicas, classes de medicamentos, procedimentos/encaminhamentos, reabilitação e observação acompanhada quando sustentada. Não preencher categorias sem indicação nem chamar observação de segura se a urgência estiver indeterminada. Identificar se uma opção depende de confirmação diagnóstica ou avaliação especializada.

Em tabela, usar apenas colunas úteis:

| Possibilidade | Objetivo e quando considerar | Benefício esperado e evidência | Riscos/impedimentos | O que falta avaliar e monitorar |
| --- | --- | --- | --- | --- |

Benefício “esperado” deve ser atribuído à população/fonte, não uma promessa ao indivíduo. Só usar números absolutos, NNT/NNH ou porcentagens quando verificados, com comparador, horizonte e população. Distinguir cuidado estabelecido, uso fora de indicação aprovada e estratégia experimental; não promover a última como disponível ou eficaz sem base.

## Avaliar adequação individual

Conforme a opção, verificar: idade, peso, alergias/reação, gestação/lactação, função renal/hepática com data, comorbidades, medicamentos/suplementos atuais, procedimentos planejados, risco de interação, preferências, capacidade funcional, adesão relatada e acesso. Desconhecido não significa ausência de contraindicação.

Se faltar informação essencial, é possível explicar a opção em termos gerais, mas a adequação individual fica inconclusiva. Não completar função renal com valor normal, gestação com falso, alergias com lista vazia ou medicações com “nenhuma”. Não extrapolar doses de adulto, transformar uma bula em prescrição personalizada ou autorizar início/suspensão/troca. Explicar necessidade de revisão imediata quando houver risco atual.

## Comparar trajetórias sem fazer previsão fictícia

Pode descrever cenários condicionais: investigar primeiro, discutir opção A/B ou observar com seguimento se clinicamente cabível. Em cada um, registrar premissas, resultado que se pretende avaliar, possíveis danos, horizonte sustentado pela fonte e sinais para reavaliar.

Não gerar curva de cura, sobrevida individual, resposta farmacológica ou “gêmeo digital” a partir de debate de personas ou simulação social. Escores e modelos verificados só se aplicam à finalidade/população autorizadas e com entradas completas. Consenso de agentes não estima efeito de tratamento.

## Fechar com acompanhamento

Indicar quem deve discutir a opção, qual dado falta, monitoramento previsto na fonte e sinais pertinentes para antecipar atendimento. Não inventar consulta, exame solicitado, profissional responsável ou data marcada. Respeitar preferências informadas e não confundir custo/acesso local presumido com disponibilidade real.

Campos técnicos opcionais: `option_id`, `target_problem`, `confirmation_needed`, `eligibility`, `expected_benefit`, `harms`, `contraindications`, `unknowns`, `evidence_refs`, `monitoring`, `review_owner`, `status: para_discussao|inconclusivo|requer_escalonamento`. Nenhum status significa prescrição aprovada.
