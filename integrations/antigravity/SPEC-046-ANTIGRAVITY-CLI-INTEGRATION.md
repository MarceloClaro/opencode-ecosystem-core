# SPEC-046: Ecosystem Capabilities MCP — OpenCode & Antigravity Integration

**Versão**: 1.1.0  
**Status**: Implementado  
**Data**: 2026-06-22  
**Autor**: Marcelo Claro (OpenCode Ecosystem)

---

## 1. Visão Geral

Esta especificação define a integração do OpenCode Ecosystem com dois clientes MCP:
1. **OpenCode CLI** — servidor MCP registrado em `opencode.json` (ecossistema + global SWL)
2. **Antigravity CLI** — servidor MCP registrado em `settings.json` + skill em `~/.gemini/`

O servidor `ecosystem_capabilities_server.py` expõe 13 ferramentas que cobrem scanners,
motores de raciocínio e metadados do ecossistema (162 skills, 130 agentes, 27 módulos).

## 2. Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│  Ecosystem Capabilities MCP Server v1.0                         │
│  nexus/ecosystem_capabilities_server.py                         │
│                                                                 │
│  13 ferramentas MCP via stdio (JSON-RPC 2.0)                    │
│  ├─ Scanners (6): noológico, teleológico, evolutivo,            │
│  │                 potentiality_v2, social_impact, full_pipeline │
│  ├─ Reasoning (3): z3_verify, sympy_analyze, critical_analyze   │
│  └─ Metadados (4): list_skills, list_agents, list_mcps, status  │
│                                                                 │
│  Clientes registrados:                                          │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │ OpenCode CLI     │    │ Antigravity CLI  │                   │
│  │ opencode.json    │    │ settings.json    │                   │
│  │ (ecossistema +   │    │ + SKILL.md       │                   │
│  │  global SWL)     │    │                  │                   │
│  └──────────────────┘    └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```
│  │ Scanners     │                 │ Ecosystem    │          │
│  │ Reasoning    │                 │ Skill        │          │
│  │ Metadados    │                 │ (SKILL.md)   │          │
│  └──────────────┘                 └──────────────┘          │
│                                                              │
│  Fluxo existente (já implementado):                         │
│  OpenCode → AntiBridge → Antigravity (delegação unidirec.)  │
│                                                              │
│  Fluxo novo (SPEC-046):                                     │
│  Antigravity → Ecosystem MCP → Scanners/Reasoning/Metadata  │
└─────────────────────────────────────────────────────────────┘
```

## 3. Componentes

### 3.1 Ecosystem Capabilities MCP Server

**Arquivo**: `nexus/ecosystem_capabilities_server.py`  
**Protocolo**: MCP (Model Context Protocol) via stdio (JSON-RPC 2.0)  
**Versão**: 1.0.0

Ferramentas expostas (13 no total):

| Categoria | Ferramenta | Descrição |
|:----------|:-----------|:----------|
| Scanner | `eco_run_noological_scanner` | Análise de lacunas epistêmicas |
| Scanner | `eco_run_teleological_scanner` | Alinhamento com objetivos |
| Scanner | `eco_run_evolutionary_scanner` | Maturidade evolutiva |
| Scanner | `eco_run_potentiality_v2` | Potencial epistêmico (6 dimensões) |
| Scanner | `eco_run_social_impact` | Impacto social e ESG |
| Scanner | `eco_run_full_pipeline` | Pipeline completo de scanners |
| Reasoning | `eco_z3_verify` | Verificação formal com Z3 |
| Reasoning | `eco_sympy_analyze` | Análise simbólica com SymPy |
| Reasoning | `eco_critical_analyze` | Análise de falácias e vieses |
| Metadado | `eco_list_skills` | Lista 162+ skills |
| Metadado | `eco_list_agents` | Lista 130+ agentes |
| Metadado | `eco_list_mcps` | Lista 4+ MCPs |
| Metadado | `eco_status` | Status geral do ecossistema |

### 3.2 OpenCode Integration

**Arquivos modificados**:
- `opencode.json` (ecossistema): adicionado `ecosystem-capabilities` MCP
- `~/.config/opencode/opencode.json` (global SWL): adicionado `ecosystem-capabilities` MCP
- `~/.config/opencode/skills/ecosystem-capabilities/SKILL.md`: skill para o agente OpenCode

### 3.3 Antigravity Integration

**Arquivos criados**:
- `~/.gemini/antigravity-cli/skills/opencode-ecosystem/SKILL.md`: skill para o agente Antigravity
- `nexus/register_ecosystem_mcp.py`: script de registro no Antigravity

## 4. Fluxos de Integração

### Fluxo 1: Antigravity → Ecosystem (NOVO - SPEC-046)

```
1. Usuário invoca agy.exe
2. Agente Antigravity carrega skill "opencode-ecosystem"
3. Usuário pede: "Analise as lacunas do ecossistema"
4. Agente chama: eco_run_noological_scanner
5. MCP server executa scanner via scanner_integration.py
6. Resultado retorna ao agente Antigravity
7. Agente apresenta resultado em PT-BR formal
```

### Fluxo 2: OpenCode → Antigravity (EXISTENTE)

```
1. Usuário invoca OpenCode
2. AntiBridge detecta trigger (imagem, browser, pesquisa)
3. Tarefa formatada e delegada ao Antigravity
4. Antigravity executa e retorna resultado
5. AntiBridge integra ao estado do ecossistema
```

### Fluxo 3: Híbrido (COMBINADO)

```
1. Usuário pede: "Gere diagrama do scanner e analise criticamente"
2. OpenCode executa scanner (eco_run_noological_scanner)
3. OpenCode delega geração de imagem ao Antigravity
4. Resultados combinados em contexto unificado
```

## 5. CTs (Critérios de Teste)

| CT | Descrição | Status |
|:---|:----------|:-------|
| CT-01 | MCP server inicia sem erros | PASS |
| CT-02 | `tools/list` retorna 13 ferramentas | PASS |
| CT-03 | `eco_status` retorna status válido (162 skills, 130 agents) | PASS |
| CT-04 | `eco_list_skills` lista skills do ecossistema | PASS |
| CT-05 | `eco_list_agents` lista agentes do ecossistema | PASS |
| CT-06 | `eco_list_mcps` lista MCPs do ecossistema | PASS |
| CT-07 | Registration script registra MCP server no Antigravity | PASS |
| CT-08 | Registration script remove MCP server | PASS |
| CT-09 | Registration script verifica status | PASS |
| CT-10 | Settings.json Antigravity contém mcpServers.ecosystem-capabilities | PASS |
| CT-11 | Skill SKILL.md existe no diretório do Antigravity | PASS |
| CT-12 | Compatibilidade com anti-bridge existente | PASS |
| CT-13 | opencode.json ecossistema contém ecosystem-capabilities MCP | PASS |
| CT-14 | opencode.json global contém ecosystem-capabilities MCP | PASS |
| CT-15 | Skill OpenCode existe em ~/.config/opencode/skills/ | PASS |
| CT-16 | MCP server retorna JSON válido via stdio (UTF-8) | PASS |

## 6. Decisões de Design

| Decisão | Justificativa |
|:--------|:-------------|
| MCP via stdio | Padrão nativo do Antigravity; sem dependência de rede |
| 13 ferramentas (não 50+) | Foco em usabilidade; metadados como ferramentas leves |
| Registration script separado | Não modificar settings.json manualmente; automação segura |
| Skill SKILL.md complementar | Instrui o agente Antigravity sem modificar o core |
| Compatibilidade com AntiBridge | Fluxo existente preservado; novo fluxo é aditivo |

## 7. Métricas

| Métrica | Valor |
|:--------|:------|
| Ferramentas MCP expostas | 13 |
| Arquivos criados/modificados | 7 |
| Linhas de código | ~610 (server) + ~147 (register) + ~90 (skill antigravity) + ~80 (skill opencode) |
| CTs totais | 16 (16/16 PASS) |
| Clientes MCP registrados | 2 (OpenCode + Antigravity) |
| Compatibilidade | OpenCode CLI, agy.exe, Antigravity 2.0, Antigravity IDE, Python SDK |
| Impacto no ecossistema | Zero (aditivo, não modificativo) |

## 8. Referências

- SPEC-045: Potentiality Estimator v2.0 (scanners consolidados)
- SPEC-044: Social Impact Scanner
- SPEC-038: Trust Engine & Behavioral Autonomy
- AntiBridge Plugin: `plugins/antigravity-bridge.ts`
- Antigravity MCP Server: `nexus/antigravity_mcp_server.py`
- Antigravity Orchestrator: `agents/antigravity-orchestrator.md`
