---
spec_id: SPEC-935-R440
title: Integração com Microsoft APM (Agent Package Manager)
component: integrations/apm, marceloclaro/cli, marceloclaro/orchestrator, doctor
status: verified
test_file: tests/test_microsoft_apm.py
---

# SPEC-935-R440 — Integração com Microsoft APM (Agent Package Manager)

## 1. Contexto e Motivação

O **Microsoft APM (Agent Package Manager)** (disponível em `https://github.com/microsoft/apm`) é o padrão aberto e orientado a manifesto para empacotamento, distribuição, versionamento e governança de primitivas de IA agente.

O OpenCode Ecosystem Core possui um catálogo com mais de 209 agentes, servidores MCP (MCI e Antigravity), habilidades (`skills/`), protocolos de memória metacognitiva (MetaBus) e orquestração A2A via Blackboard.

Esta especificação define a integração bidirecional e de primeira classe do padrão Microsoft APM no OpenCode Ecosystem Core, permitindo:
1. Declarar o ecossistema e seus componentes através de um manifesto canônico `apm.yml`.
2. Garantir reprodutibilidade estrita via lockfile `apm.lock.yaml` com hashes criptográficos SHA-256 de todas as primitivas.
3. Aplicar políticas corporativas de governança e segurança via `apm-policy.yml`, incluindo detecção de ataques de injeção Unicode (Trojan Source / Bidi override / Zero-width characters) e guardas anti-overclaim.
4. Compilação cruzada para múltiplos ambientes de execução (OpenCode CLI `opencode.json`, Antigravity `AGENTS.md`, Claude Code `CLAUDE.md`, Cursor `.cursorrules`, GitHub Copilot `.github/copilot-instructions.md`).
5. Comandos de CLI dedicados em `python3 -m marceloclaro.cli apm` (`init`, `install`, `compile`, `audit`, `pack`, `list`).
6. Diagnóstico de saúde integrado via `python3 -m marceloclaro.cli doctor`.

## 2. As 7 Primitivas Canônicas do APM

A integração mapeia e gerencia as 7 primitivas estruturais do APM:
- **Instructions**: Regras escopadas e diretrizes de agentes (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `rules/*.md`).
- **Prompts**: Fluxos de raciocínio, templates e comandos parametrizados (`prompts/`).
- **Agents**: Personas especialistas do catálogo (`agents/catalog/*.md`, `agents/*.md`).
- **Skills**: Metaguias e ferramentas reutilizáveis (`skills/*/SKILL.md`).
- **Hooks**: Gatilhos de ciclo de vida (`PreToolUse`, `PostToolUse`, `AuditGate`).
- **MCP Servers**: Servidores Model Context Protocol (`mci/mcp_server.py`, `integrations/antigravity/mcp_server.py`).
- **Plugins**: Bundles extensíveis de runtime (`.opencode/plugins/`).

## 3. Critérios de Aceite (CAs)

- **CA1 — Manifest Parsing & Validation (`apm.yml`)**:
  Parser estrito capaz de ler, validar e emitir manifestos `apm.yml` conforme o esquema oficial da Microsoft, suportando metadados de pacote, dependências e as 7 primitivas.
- **CA2 — Lockfile Generation & Integrity (`apm.lock.yaml`)**:
  Geração determinística de lockfile com hashes SHA-256 de conteúdo de cada arquivo/primitiva, garantindo integridade e verificação contra adulteração.
- **CA3 — Security Policy & Trojan Source Audit (`apm-policy.yml`)**:
  Motor de auditoria de segurança capaz de detectar caracteres Unicode perigosos (Trojan Source, zero-width, bidi overrides), injeção de prompt, permissões excessivas e conformidade com regras anti-overclaim.
- **CA4 — Cross-Platform Compiler**:
  Compilador capaz de converter primitivas declaradas em `apm.yml` para configurações válidas de múltiplos harnesses (`opencode.json`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`).
- **CA5 — Package Manager API & Packaging**:
  API programática completa (`APMPackageManager`) com métodos `init()`, `install()`, `compile()`, `audit()`, `pack()`, `list_primitives()`.
- **CA6 — MarceloClaro CLI & Doctor Integration**:
  Comando `python3 -m marceloclaro.cli apm` com subcomandos correspondentes e check de diagnóstico `apm_integration` no `doctor.py`.
- **CA7 — MarceloClaroOrchestrator Native Discovery**:
  O orquestrador primário `MarceloClaroOrchestrator` consegue carregar dinamicamente agentes e MCPs registrados via manifesto APM.
- **CA8 — Testes TDD 100% Verificados**:
  Suíte de testes `tests/test_microsoft_apm.py` cobrindo todos os casos com execução verde e sem dependência de rede externa.
