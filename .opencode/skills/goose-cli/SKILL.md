---
name: goose-cli
description: >-
  Integração da CLI do Goose (aaif-goose/goose, Apache-2.0, AAIF/Linux Foundation)
  como executor externo orquestrável no OpenCode Ecosystem Core (SPEC-935-R598).
  Use quando o usuário mencionar Goose (agente de IA generalista em Rust, 15+
  providers, 70+ extensões MCP) e quiser consultar status, executar uma tarefa
  headless (goose run --text), ou comparar segunda opinião com outro agente.
  NÃO instala o Goose automaticamente — mostra a instrução oficial e mantém o
  card goose-cli no catálogo para invocação tolerante (warn se ausente).
---

# Skill Goose CLI — executor externo orquestrável (SPEC-935-R598)

O **Goose** (https://github.com/aaif-goose/goose, Apache-2.0, 53k+ stars) é um
agente de IA nativo open source da **Agentic AI Foundation (AAIF)** no Linux
Foundation: desktop app + CLI em Rust + API. Generalista — código, pesquisa,
escrita, automação, análise de dados — com 15+ providers (Anthropic, OpenAI,
Google, Ollama, OpenRouter, Azure, Bedrock; assinaturas existentes via ACP) e
70+ extensões via Model Context Protocol (MCP).

Nesta skill, o Goose é um **executor externo** invocado por subprocess através
de `integrations/goose_cli` (padrão M7, mesma família de bernstein e
opencode-go-agent). O orquestrador primário `marceloclaro` permanece dono do
ciclo SDD/TDD: spec antes, testes verdes, gate de verificação, reflexão.

## Fluxo de uso

1. **Descobrir estado**
   ```
   python3 -m integrations.goose_cli status
   python3 -m integrations.goose_cli doctor
   ```
   Goose ausente → `disponivel: false` e `warn` no doctor (NUNCA fail; é
   opcional). O comando mostra a instrução oficial de instalação.

2. **Executar tarefa headless**
   ```
   python3 -m integrations.goose_cli run '<tarefa em linguagem natural>'
   ```
   A CLI resolve o provider padrão da config local do Goose. Para provider
   explícito use o runner Python:
   ```python
   from integrations.goose_cli import goose_run
   resultado = goose_run("revisar este relatório", provider="ollama", model="qwen3:8b")
   # resultado = {ok, returncode, stdout, stderr, timeout, version, comando}
   ```

3. **Integrar ao pipeline do Core**
   - Conte ao usuário o que o Goose produziu e marque claramente como
     **execução externa** (anti-overclaim).
   - Confira validade/qualidade (gate do orquestrador) antes de qualquer
     alegação ou commit.
   - Se a tarefa virar mudança de código/doc, crie spec + testes (SDD/TDD).

## Providers e MCP do Goose

- Providers: Anthropic, OpenAI, Google, Ollama, OpenRouter, Azure, Bedrock,
  OpenCode (plugin), entre outros — 15+. ACP permite reutilizar assinaturas
  existentes de Claude/ChatGPT/Gemini.
- Extensões: 70+ via MCP (o Core já expõe 7 servidores MCP próprios:
  litert-lm, metacognitive-interconnect, antigravity-bridge, pypi-search,
  colibri-mcp, scanners-mcp, web-deploy-mcp — podem ser registrados no Goose
  como fontes de ferramentas, se o operador desejar).

## Regras

- **Não instalar por conta própria**: mostrar a instrução oficial
  (`curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash`);
  instalação exige consentimento do operador.
- **Não inserir segredos/chaves no prompt**; respeitar o permission model.
- **Nunca** declarar resultado do Goose como "verificado/superhuman" sem
  validação externa (CORRIGENDUM.md / R110).
- Em caso de timeout do `goose run`, o runner retorna `ok: false, timeout: true`
  sem lançar exceção — tratar como falha de execução, não como erro do Core.