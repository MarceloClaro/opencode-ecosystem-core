# SPEC-935-R211 — Reconciliação dos MCPs, do Core e do LiteRT-LM

**Versão**: 1.1.0  
**Status**: Em execução  
**Data**: 2026-07-22  
**Autor**: Marcelo Claro (OpenCode Ecosystem Core)  
**Rótulos**: `mcp`, `core`, `litert-lm`, `opencode`, `reprodutibilidade`, `segurança`

### Histórico de revisão

| Versão | Mudança |
|---|---|
| 1.0.0 | Contratos MCP/Core/LiteRT e testes determinísticos iniciais. |
| 1.1.0 | Incorpora findings P1 da revisão consolidada: IDs canônicos, erros MCP SDK, loopback, redaction, dependências e registro evolutivo. |

## 1. Objetivo

Restabelecer um caminho operacional único e verificável para os servidores MCP,
o CLI/orquestrador do OpenCode Ecosystem Core e a integração LiteRT-LM, sem
confundir um servidor HTTP OpenAI-compatible com um transporte MCP stdio.

Esta especificação cobre as falhas reproduzidas na árvore atual e não declara
que dependências externas (servidor LiteRT-LM, `bun` ou credenciais de nuvem)
estejam disponíveis no ambiente de validação.

## 2. Escopo

1. Handshake MCP e tratamento de notificações em `mci` e Synthetic University.
2. Respostas JSON-RPC previsíveis para entradas inválidas e falhas de segurança.
3. Configuração OpenCode gerada de forma determinística, portátil e sem registrar
   o daemon HTTP `litert-lm serve` como MCP.
4. Comando `python3 -m marceloclaro.cli doctor` funcional.
5. Compatibilidade LiteRT-LM: dependência Hugging Face opcional mockável,
   identificadores canônicos e aliases, respeito a `auto_start=False`, backend
   solicitado sem downgrade silencioso e política de contexto explícita.
6. Testes de regressão determinísticos, sem exigir um servidor LiteRT-LM real.

## 3. Critérios de aceitação (SDD Gate)

| ID | Critério | Verificação |
|---|---|---|
| CA1 | O comando `python3 -m marceloclaro.cli doctor` existe, emite JSON válido e retorna código não fatal para estado `healthy` ou `degraded`; `status` e `agents` permanecem compatíveis. | Teste de subprocesso/CLI |
| CA2 | `mci/mcp_server.py` responde a `initialize` com `protocolVersion`, `capabilities` e `serverInfo`, aceita `ping` e não emite resposta para notificações sem `id`. | Testes R118 + round-trip stdio real |
| CA3 | `synthetic_university/mcp_server.py` implementa o mesmo contrato mínimo MCP (`initialize`, `ping`, `tools/list`, `tools/call`, notificações e erro JSON-RPC). | Testes de handshake e subprocesso |
| CA4 | Entrada que não seja objeto JSON, método desconhecido, ferramenta inexistente ou argumento malicioso produz erro estruturado, sem traceback, `KeyError` ou resposta de sucesso falsa. | Testes MCP/security |
| CA5 | A varredura de segurança cobre strings aninhadas e preserva o campo `flags`; erros de validação são marcados como `isError` no envelope MCP. | Testes R100 + regressões novas |
| CA6 | `build_config()` reproduz exatamente `opencode.json`; o arquivo não registra `litert-lm-serve` em `mcp`, não usa caminho absoluto específico da máquina e mantém somente processos MCP stdio. | R137 + auditoria estrutural |
| CA7 | A configuração continua contendo os providers/modelos LiteRT-LM canônicos e o plugin TypeScript não é necessário para iniciar o servidor HTTP. | Teste JSON/plugin |
| CA8 | Ausência de `huggingface_hub` não impede importação de `skills.litert_lm.model_manager`; os pontos de integração podem ser mockados e o método real retorna erro de instalação claro. | Testes R209 com e sem dependência |
| CA9 | `auto_start=False` não cria subprocesso; o backend escolhido é construído sob demanda e uma indisponibilidade explícita não é silenciosamente convertida em outro backend. | Testes unitários com mock |
| CA10 | O contexto LiteRT-LM é separado do limite de saída e usa uma política documentada/configurável, compartilhada pelo provider e pelos scripts. | Testes de configuração |
| CA11 | Todos os testes direcionados de MCP, core, R209/R210 e configuração passam; testes que dependem de servidor externo são apenas pulados com motivo explícito. | `python3 -m pytest` |
| CA12 | Após a alteração, o ciclo evolutivo e a reflexão registram falhas encontradas, correções e limitações remanescentes no EvolutionRegistry/MetaBus. | Auditoria de evolução |
| CA13 | O roteador, os providers e a configuração compartilham IDs LiteRT-LM canônicos; aliases, quando aceitos, normalizam para um ID anunciado e nenhum modelo roteado é órfão. | Teste de catálogo/roteamento |
| CA14 | O servidor MCP LiteRT-LM usa `isError=true` para ferramenta desconhecida, payload inválido e falha operacional, inclusive no resultado produzido pelo SDK MCP. | Teste do handler/SDK com mocks |
| CA15 | URL/host remotos do LiteRT-LM não são aceitos por padrão; o backend usa loopback, não publica credenciais em status e somente um opt-in explícito permite configuração remota revisada. | Teste de configuração/segurança |
| CA16 | Auditoria MCP redige recursivamente campos sensíveis em argumentos, resultados e exceções, inclusive em listas/objetos aninhados. | Teste R100 ampliado |
| CA17 | Dependências necessárias para execução/testes (`mcp`, `httpx`, `click`, `prompt_toolkit`, `huggingface-hub` opcional e frontend `build`) estão declaradas em manifests apropriados, sem fingir que dependência ausente é serviço disponível. | Auditoria de manifests |
| CA18 | O EvolutionRegistry registra R211 com score provisório honesto e lições; o MetaBus recebe reflexão sobre limitações (servidor real offline, compilador TS ausente e testes externos). | Auditoria de `cycles.json`/MetaBus |

## 4. Não objetivos

- Instalar automaticamente credenciais, `bun`, `huggingface-hub` ou o servidor
  LiteRT-LM.
- Prometer inferência real quando `localhost:9379` estiver offline.
- Expor o servidor LiteRT-LM além de `localhost` sem autenticação e revisão de
  segurança específica.
- Reescrever todos os agentes catalogados ou os artefatos não relacionados ao
  fluxo MCP/Core/LiteRT-LM.

## 5. Estratégia TDD

1. **RED**: adicionar testes para os critérios reproduzidos (handshake,
   notificações, CLI, configuração, segurança e providers).
2. **GREEN**: aplicar correções mínimas e compatíveis com os contratos atuais.
3. **REFACTOR**: eliminar duplicação de envelopes/validação e alinhar a fonte
   geradora da configuração.
4. **VERIFICAR**: executar o gate direcionado, o doctor e a comparação
   `build_config() == opencode.json`.

## 6. Limitações conhecidas

O servidor LiteRT-LM real pode permanecer offline ou exigir cold start de vários
minutos. Nesses casos, a validação fica limitada a contratos, mocks e health
checks; isso não é evidência de inferência real.
