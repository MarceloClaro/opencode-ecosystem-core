---
name: plandex-cli
description: >-
  Integração da CLI do Plandex (plandex-ai/plandex, MIT, Go) como executor
  externo orquestrável no OpenCode Ecosystem Core (SPEC-935-R599). Use quando
  o usuário mencionar Plandex, quiser criar um plano de implementação grande,
  descrever uma tarefa em modo scripting (plandex tell), revisar diff pendente
  ou comparar um plano com outro agente. NÃO instala automaticamente — mostra
  a instrução oficial e mantém o card plandex-cli no catálogo com invocação
  tolerante (warn se ausente). Plandex Cloud encerrado (03/10/2025): assumir
  modo local/self-hosted ou BYO key (ex.: OpenRouter).
---

# Skill Plandex CLI — executor de codificação com planos e sandbox de diff

O **Plandex** (https://github.com/plandex-ai/plandex, MIT, 15.5k+ stars) é um
agente de codificação AI open source, terminal-based, escrito em Go — feito
para tarefas grandes: planos incrementais, **sandbox de diff** (as mudanças
ficam separadas dos arquivos até `apply`), até 2M tokens de contexto,
tree-sitter project maps, autonomia configurável e mix de modelos (Anthropic,
OpenAI, Google, open source).

Nesta skill, o Plandex é um **executor externo** invocado por subprocess via
`integrations/plandex_cli` (padrão M7, mesma família do bernstein, opencode-go-
agent e goose-cli). O orquestrador primário `marceloclaro` permanece dono do
ciclo SDD/TDD.

## Fluxo de uso (scripting, não-REPL)

1. **Descobrir estado**
   ```
   python3 -m integrations.plandex_cli status
   python3 -m integrations.plandex_cli doctor
   ```
   Ausente → `disponivel: false` e `warn` no doctor (NUNCA fail).

2. **Criar plano e descrever a tarefa**
   ```
   python3 -m integrations.plandex_cli new [-n nome] [--semi|--full]
   python3 -m integrations.plandex_cli tell '<tarefa em linguagem natural>'
   ```
   O `tell` roda no sandbox: as mudanças ficam **pendentes** (não tocam os
   arquivos). Flags úteis no runner Python:
   ```python
   from integrations.plandex_cli import plandex_tell, plandex_diff, plandex_apply
   r = plandex_tell("implemente X", apply=False)   # apenas propõe
   diff = plandex_diff()                            # revisa pendências
   # aprovado pelo humano? então:
   plandex_apply(commit=False)                      # aplica (sem git commit)
   ```
   `apply=True/--apply` e `commit=True/--commit` existem, mas exigem
   consentimento explícito do operador — o padrão do Core é revisar o diff
   antes de aplicar (gate SDD/TDD).

3. **Perguntar sem alterar nada**
   ```
   python3 -m integrations.plandex_cli chat '<pergunta>'
   ```

4. **Integrar ao pipeline do Core**
   - Confira o diff e rode a bateria de testes antes de aplicar.
   - Marque claramente como **execução externa** (anti-overclaim).
   - Se a tarefa virar mudança de código/doc, mantenha spec + testes (SDD/TDD).

## Configuração de hosting

- **Plandex Cloud**: encerrando/restringindo (03/10/2025) — não dependa dele.
- **Local/self-hosted**: Docker (docs.plandex.ai/hosting/self-hosting/local-mode-quickstart).
- **BYO key**: `export OPENROUTER_API_KEY=...` (ou provider próprio) antes de rodar.
- Alias: `pdx` equivale a `plandex` (o runner aceita ambos via `_binary()`).

## Regras

- **Não instalar por conta própria**: mostrar a instrução oficial
  (`curl -sL https://plandex.ai/install.sh | bash`); instalação exige
  consentimento do operador.
- **Nunca** aplicar mudanças sem revisão humana (o sandbox de diff existe para isso).
- **Nunca** declarar resultado do Plandex como "verificado/superhuman" sem
  validação externa (CORRIGENDUM.md / R110).
- Em caso de timeout, o runner retorna `ok: false, timeout: true` sem exceção.