# Oito especialistas adicionados ao Core — R669

Todos os perfis são registrados pelo `MarceloClaroOrchestrator`. O fluxo de
atribuição passa por Blackboard, CFP, seleção de capacidades e MetaBus.
Requisitos simultâneos usam ALL_OF. Um perfil registrado permanece declarado;
sua atribuição não significa que uma tarefa foi executada.

| Perfil | Responsabilidade e método do Core |
|---|---|
| Scientific capabilities audit | Auditar capacidades, lacunas e proveniência com `knowledge_evolution_plan`. |
| Simulation game audit | Verificar cenários, jogos e limites da simulação com `simulate_game`. |
| Book mcp | Consultar livros locais com `library_search` e `library_status`. |
| Book finetuning | Preparar e validar dados de treino com `finetuning_prepare`; não executa treinamento. |
| Library architecture | Verificar a estrutura e integridade da biblioteca com `library_status`. |
| Hooks integration | Verificar contratos de SDK e hooks com `integration_verify`. |
| Mcp cli integration | Verificar as interfaces de CLI/MCP com `integration_verify`. |
| Live mirofish hermes | Executar os projetos externos por `scientific_runtime_run`, preservando respostas e artefatos. |

Os cartões em `agents/catalog/` preservam português brasileiro, ferramentas
permitidas e limites de entrega. A seleção e os métodos associados foram
testados em subprocessos com estado temporário. Isso verifica o protocolo
real com entradas sintéticas; não demonstra inferência pelos oito perfis.
Hermes e MiroFish possuem prova adicional com processos externos e modelo local.

Para regenerar a configuração após editar um cartão:

```bash
.venv/bin/python -m integrations.opencode_cli
```

Na geração de 2026-10-04, `opencode.json` contém 235 agentes, 11 servidores MCP
e 28 comandos. Consulte a configuração para as contagens atuais.

Veja [o guia de integração científica](INTEGRACOES_CIENTIFICAS_R667_R671.md).
