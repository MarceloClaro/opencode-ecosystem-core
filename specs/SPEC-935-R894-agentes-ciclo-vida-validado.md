---
spec_id: SPEC-935-R894
title: Ciclo de vida validado de agentes e perfis de sessão
component: agents.lifecycle
status: implemented
test_file: tests/test_r894_agent_lifecycle.py
---

# R894 — Ciclo de vida validado de agentes e perfis de sessão

## Autorização e desenho

Solicitação explícita de implementar os agentes históricos, manter validação/registro permanente, integrar os plugins nomeados e buscar alternativas à CI hospedada e ao grafo bloqueado. Preservar dados locais e o primário canônico.

## Contrato

1. Incorporar rótulos históricos desta tarefa e os perfis explicitamente pedidos, deduplicando aliases e sem declarar que um nome prova execução.
2. Manter MarceloClaro como único primário. Criar, validar, registrar e preparar ativação pelo primário; registrar no Blackboard e MetaBus com origem, hash, capacidades, permissões e contrato de saída.
3. Novos arquivos do catálogo fora do baseline histórico não podem ser compilados/ativados sem contrato válido. Alterações do baseline invalidam a isenção histórica; isso não é qualidade científica certificada.
4. Disponibilizar operações de inventário, validação, criação e ativação por CLI/MCP. Caminhos confinados, slugs seguros, limites de tamanho, tipos estritos, política de ferramentas e referências a spec/testes existentes. Nenhum comando arbitrário ou autoaprovação por substring.
5. Reutilizar catálogo/gerador/Blackboard e critérios de elegibilidade. Uma ativação pode resultar em tarefa atribuída/pendente; não afirmar inferência, execução ou conclusão sem resultado real. Novas tarefas mantêm fonte/perfil exato e contrato verificável.
6. Criações fora da interface também passam pelo gate na carga/compilação. Instruções AGENTS exigem registrar antes de gerar novo agente/subagente para trabalhos futuros. Preservar perfis antigos por baseline explícito, com auditoria de divergências.
7. Testes RED/GREEN negativos, roteamento real ALL_OF por capacidade única em estado temporário, geração reproduzível, adulteração de perfil, colisão e ausência de dependência. Não elevar confiança por validação própria.

## Evidência e limites

Execução local delimitada, sem garantia de ausência universal de bugs, validação externa, mérito editorial ou escala de cluster. Registrar RED/GREEN e ciclo evolutivo somente após verificação.
