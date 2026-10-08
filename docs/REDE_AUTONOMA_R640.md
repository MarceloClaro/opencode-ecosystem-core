# Rede coordenada do OpenCode Ecosystem Core

Ao abrir o projeto com o comando WSL habitual, novas sessões começam no
orquestrador `marceloclaro`. O MCP `ecosystem-network` conecta esse agente ao
orquestrador Python, ao roteamento Transformer, ao Blackboard e ao MetaBus.

No OpenCode, use `/ecosystem status` para verificar a rede ou
`/ecosystem analise esta tarefa e coordene os agentes: ...` para pedir trabalho.
Também pode solicitar em linguagem natural: “Use a rede do ecossistema para
analisar esta tarefa”. As ferramentas disponíveis são `ecosystem_status`,
`ecosystem_route` e `ecosystem_run`. A R644 acrescenta `ecosystem_workflow`
e `ecosystem_workflow_status` para execução em etapas e retomada; consulte o
[guia de workflows](WORKFLOWS_R644.md).

A execução seleciona um especialista interno e instruções federadas, chama
um executor Claude, Antigravity ou Codex e registra a conclusão e a reflexão.
Se um serviço falhar, o modo automático pode tentar outro executor dentro do
limite de passos e de tempo; as tentativas e os motivos ficam no resultado.
Quando um executor é escolhido explicitamente, a ponte respeita essa escolha.

## Uso direto no Ubuntu

```bash
cd /home/marceloclaro/opencode-ecosystem-core
.venv/bin/python -m marceloclaro.cli network status
.venv/bin/python -m marceloclaro.cli network route "Revisar a arquitetura"
.venv/bin/python -m marceloclaro.cli network run "Analisar a arquitetura" --max-steps 3 --timeout 120
.venv/bin/python -m marceloclaro.cli network run "Revisar o código" --ecosystem codex --max-steps 2
```

## Limites observados

- Esta ponte executa análise e geração de texto com acesso de leitura. O agente
  principal continua usando as ferramentas nativas do OpenCode para editar e
  testar mudanças autorizadas.
- Transformer é roteamento inspirado em atenção, com pesos auditáveis.
  Não há treinamento de uma rede neural nem daemon trabalhando sem uma tarefa.
- A verificação interna de texto é heurística; não comprova correção científica.
- Instruções importadas preservam origem e hashes. Hooks e scripts importados
  permanecem inertes; os aplicativos originais não têm todas as funções portadas.
- Codex usa a CLI instalada, inclusive a versão Windows pela ponte WSL, com
  sandbox de leitura. O aplicativo ChatGPT não é controlado.
- O inventário confirma instalações, mas autenticação e saldo são confirmados
  apenas durante uma execução. Neste computador, o Claude recusou o probe por
  saldo insuficiente; não se alteraram credenciais ou assinatura.

## Evidência de execução em 2026-10-03

O OpenCode instalado conectou os oito servidores MCP. Codex e Antigravity
responderam a probes reais limitados. Uma chamada real de `ecosystem_run`
selecionou o especialista `auditor`, incorporou instruções com origem Claude,
executou via Codex e terminou como `completed` no Blackboard, com reflexão no
MetaBus. A nota de texto produzida pelo pipeline é uma avaliação heurística.
Outra chamada real, sem escolher executor, registrou a recusa de saldo do
Claude, mudou automaticamente para Codex e concluiu em dois passos. O retorno
preservou o motivo da troca, sem repetir o executor que falhou.

Os relatórios completos desta execução ficam em `.backups/r640/`. A
especificação e os testes de regressão são `SPEC-935-R640` e `tests/test_r640_*`.
O gate final passou com **185 testes aprovados e um teste externo pulado**;
lint e verificação de diferenças não apontaram erros.

Configuração conforme os formatos oficiais de
[agentes](https://opencode.ai/docs/agents/) e
[servidores MCP do OpenCode](https://opencode.ai/docs/mcp-servers/).
