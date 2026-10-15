---
spec_id: SPEC-935-R896
title: Operações de grafo estático Python com resolução conservadora
component: integrations.python_code_graph
status: implemented
test_file: tests/test_r896_python_code_graph.py
---

# R896 — Operações de grafo estático Python com resolução conservadora

## Autorização e desenho

Solicitação explícita de implementar os agentes históricos, manter validação/registro permanente, integrar os plugins nomeados e buscar alternativas à CI hospedada e ao grafo bloqueado. Preservar dados locais e o primário canônico.

## Contrato

1. Implementar alternativa própria para get_symbol_usages/get_call_tree/get_blast_radius com ast Python e corpus de bytes já confinado. Não retirar bloqueios do upstream sem evidência.
2. Operação explícita python_graph no CodeContextProvider; resultado deve indicar backend/scope/static_only, entrada, símbolos, chamadas/referências, unresolved e limites. Outros alvos dinâmicos/não-Python continuam não suportados, com motivo explícito.
3. Símbolos por arquivo::qualname; aliases apenas unívocos. Resolver nomes lexicais/imports explícitos, rejeitar ambiguidades e não inferir self.*, getattr, exec, imports wildcard, parâmetros sombreados ou reatribuições. Defaults/decoradores não pertencem ao corpo da função.
4. Proveniência path/SHA/linhas real; o alvo não é importado/executado. Profundidade, quantidade de arquivos/nós/resposta e ciclos delimitados, tratamento de corpus vazio/syntax error/missing/ambiguous.
5. Manter confinamento e stale-index fail-closed; sem escrita em fontes ou acesso a rede. Reutilizar primário/CLI/MCP e memória sem promoção de confiança.
6. REDs com contraprovas de semântica upstream, testes de cadeia/diamante/ciclo/usos sem chamada/dinâmico/colisões e amostra real do Core. Comparar trecho/hash/linhas com fonte. Testes antigos de bloqueio nativo permanecem válidos.

## Evidência e limites

Execução local delimitada, sem garantia de ausência universal de bugs, validação externa, mérito editorial ou escala de cluster. Registrar RED/GREEN e ciclo evolutivo somente após verificação.
