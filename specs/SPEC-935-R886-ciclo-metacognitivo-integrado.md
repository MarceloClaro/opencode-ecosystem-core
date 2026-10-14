---
spec_id: SPEC-935-R886
title: Memória, raciocínio e reflexão ligados ao primário sem autopromoção
component: mci.metacognitive_loop
status: implemented
test_file: tests/test_r886_metacognitive_loop.py
---

# R886 — Ciclo metacognitivo integrado

## Problema observado

O diagnóstico estrutural inicial passou em 22/22 verificações locais. Leitura
e reprodução isolada identificaram: buscas lexical/hierárquica omitem o
conteúdo de observações; a delegação utiliza lições genéricas; Reflexion ignora
o resultado e produz texto fixo; motor e primário aumentam confiança usando
suas próprias notas. Essas propriedades não demonstram adaptação à tarefa.

## Escopo e desenho

1. Unificar o texto recuperável de episódios, incluindo observações JSON.
2. Preparar cada delegação no primário com memória relevante, IDs de origem,
   limites de tamanho e análise crítica local do motor existente. A análise
   é um roteiro heurístico, não prova matemática nem inferência LLM.
3. Após o gate autoritativo, Blackboard transmite seu resultado e estado SDD
   ao Reflexion. Um controlador canônico registra episódio tipado com tarefa,
   resumo do resultado, falha observada, limites e próxima ação. Não inventa
   causa raiz nem valida referências declaradas pelo executor.
4. Alimentar o MetacognitiveEvaluator com traço real delimitado; conservar
   sua avaliação como heurística sem promover confiança ou alegar calibração.
5. Tornar esses episódios recuperáveis pela próxima tarefa e pelo caminho
   `reason` do primário. A rede autônoma já transporta o briefing; seu retorno
   também deve declarar se a reflexão foi persistida ou houve degradação.
6. Remover autopromoção de confiança nos caminhos automáticos modificados.
   A API legada `add_reflection` permanece explícita; TrustEngine operacional
   e gates SDD/TDD continuam responsáveis pelos seus contratos existentes.

Sem instalar runtimes externos nesta etapa. Os cinco repositórios indicados
serão avaliados em snapshots pinados, com licença, interfaces e limites.
Knowl orienta proveniência/tipagem; Laya não substitui gates; OpenShell é
sandbox opcional; Awesome LLM Apps é referência; Feynman é especialista
opcional distinto do port `reversa_feynman` existente. Não haverá tráfego de
análise para esses serviços nem downloads de pesos para cumprir este escopo.

## Critérios de aceitação

- Observação encontrada por conteúdo na busca lexical e hierárquica.
- Conclusões diferentes produzem episódios diferentes e preservam referências
  como declaradas, sem convertê-las em evidência verificada.
- Falha e veto SDD geram lição contextual com próxima ação, sem alegar causa
  raiz não observada; próximo briefing recupera a origem correta.
- Primário → Blackboard → executor controlado → gate → reflexão → memória →
  próxima delegação é exercitado em teste integrado, sem atalhar o primário.
- ReasoningResult mantém campos existentes; chamadas de raciocínio não alteram
  o ledger por confiança autodeclarada. Semântica lexical não implica verdade.
- Entrada inválida e falha de persistência têm resultado observável; orçamento
  do briefing é limitado e conteúdo histórico é identificado como dado.
- Contratos existentes de bloqueio, execução limitada, retomada de workflow
  e entrega SDD/TDD não são enfraquecidos.
- RED antes da implementação, GREEN, regressões, execução local real de razão
  simbólica e segundo ciclo recuperando memória. Replay idêntico é idempotente; revisões A→B→A conservam os três estados
  e o briefing exclui revisões substituídas mesmo em consulta por termo antigo.
  Dublês e inferência externa
  serão identificados separadamente.

## Plano de implementação e verificação

1. Testar os contratos acima contra o comportamento inicial.
2. Implementar controlador e projeção textual compartilhada; integrar os
   caminhos existentes de delegação, reason e reflexão pós-gate.
3. Atualizar apenas testes antigos que exigiam autopromoção, substituindo-os
   por estado do ledger e evidência do resultado persistido.
4. Executar testes novos, regressões de memória/rede/workflow/SDD e suíte
   abrangente. Revisar o diff independentemente e corrigir falhas encontradas.
5. Documentar o ciclo atual, os candidatos e os recibos locais; preservar o
   snapshot arquitetural R879/R881 como histórico e registrar a evolução R886.

## Limites

Uma mudança delimitada não demonstra ausência de todas as ilhas no repositório.
O aceite se refere aos caminhos conectados e testados, não à qualidade geral,
probabilidade calibrada ou validação externa do ecossistema.
