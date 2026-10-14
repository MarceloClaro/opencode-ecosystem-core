---
spec_id: SPEC-935-R888
title: Curadoria rastreável por REA e integridade do benchmark IMO
component: integrations.deepmind.imobench_harness
status: implemented
test_file: tests/test_r888_imobench_integrity.py
---

# R888 — Adaptação fundamentada e benchmark sem vazamento de gabarito

## Problema observado e intenção

O usuário pediu avaliar nove repositórios e usar REA na análise e implementação
adaptada. A leitura atual dos materiais `superhuman`, `science-skills` e
`feynman-tutor` reforça uma separação essencial: pergunta, gabarito, execução e
evidência têm papéis distintos. O harness local contém um caminho padrão que
inclui `short_answer` na própria solução e deriva `formal_verified` de uma
heurística textual. Isso não fornece medida independente de raciocínio.

## Escopo

- Avaliar mira-animator, RAGnaRock, superhuman, opentwins, science-skills,
  feynman-tutor, MiroFish, MiroFish-Offline e transformers em revisão fixa.
- Registrar licença declarada, dependências, rede, sobreposição e recomendação.
- Usar inspeções estáticas REA reais pelo primário em alvos compatíveis. Preservar
  falhas e declarar que Python/Markdown não passam a ser analisados por REA
  apenas porque outros arquivos do mesmo repositório foram inspecionados.
- Reimplementar independentemente a separação de gabarito no harness existente,
  sem copiar código de terceiros nem criar outro coordenador ou modelo.

## Contratos e aceite

1. Sem solver explícito, não fabricar solução: status `not_executed`, nenhuma
   acurácia calculada a partir de respostas não executadas.
2. O solver recebe somente a visão pública do problema (id, enunciado, domínio,
   dificuldade e metadados não resolutivos). `short_answer` e soluções completas
   permanecem no avaliador e não são transmitidas ao callback.
3. Acerto de resposta curta depende de igualdade normalizada completa; resposta
   `13` não é acerto para gabarito `3`. A heurística de qualidade é separada.
4. `lema`, `=` ou nota 7 não comprova verificação formal. Somente um contrato de
   verificador formal com evidência produzida por execução poderia sustentá-la;
   sem tal caminho, `formal_verified` permanece falso e a limitação é explícita.
5. Resultados antigos ou simulados não são promovidos a benchmark executado.
   O nome de um repositório não implica desempenho sobre-humano.
6. O consumidor DeepThink não pode usar nota textual como gate de prova,
   título de demonstração concluída ou confiança fixa 0.92/0.98. A validade
   deve acompanhar o resultado e o escopo do verificador da entrada original;
   problemas naturais não formalizados permanecem pendentes. Priorizar uma
   trajetória aceita pelo verificador sobre uma heurística textual alta.
7. DeepThink e AlphaProof no primário registram observação no MetaBus sem
   promover confiança por escores próprios. Falha de persistência aparece como
   degradação; o resultado não deve ser interrompido por confiança nula.
8. RED local antes da correção, GREEN e regressões dirigidas depois. Registrar
   hashes/recibos, limitações e evolução sem alegar histórico TDD autenticado.

## Plano de execução

1. Fixar fontes e completar leituras/REA compatível nos dois levantamentos R888.
2. Escrever testes adversariais do harness; observar falha antes da correção.
3. Corrigir o caminho canônico existente e atualizar contratos de retorno.
4. Executar testes novos, consumidores existentes e diagnóstico estrutural.
5. Publicar avaliação dos nove repositórios, recibo local e ciclo R888.

A implementação de modelos de Transformers, gêmeos digitais, redes de simulação,
outra base RAG e runtimes de tutoria fica condicionada a necessidade concreta;
a análise não instala esses projetos automaticamente.

## Consumidor Deep Think — extensão necessária do mesmo contrato

O consumidor `integrations/deepmind/deep_think_engine.py` não pode usar a nota
textual como gate de validade nem gerar conclusão/confiança fixa. A aceitação
local fica limitada ao fragmento de identidade algébrica: claim de saída ligado
à entrada exata, SymPy disponível e nova execução do verificador restrito sobre
essa entrada. Sinal `is_proven` ou passos textuais do candidato, isolados, não
bastam. Sem backend ou fora do fragmento, conservar `unproven`; um fallback
sintático não é promovido a execução simbólica. O recibo local identifica claim,
hash, backend e resultado; não representa validação externa. A confiança
probabilística permanece ausente (`None`) e `calibrated=false`, inclusive em
uma identidade confirmada no escopo local. A seleção prioriza resultado do
verificador sobre a heurística textual e não a usa como autorização.

Testes: enunciado natural não demonstrado, identidade algébrica verdadeira,
identidade falsa com candidato que se autodeclara provado e backend indisponível.
