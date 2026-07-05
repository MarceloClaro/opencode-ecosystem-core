# SPEC-047: Avaliação TDD/SDD da Orquestração Marcelo Claro

## 1. Visão Geral
Especificação de Desenvolvimento Orientado a Documentação (SDD) e Testes (TDD) para validar a orquestração completa do agente `/marceloclaro` (Orquestrador Supremo). Esta SPEC expande a SPEC-042 existente, adicionando testes robustos de comportamento, cadeia de delegação, integração com TrustEngine e conformidade com os Cinco Pilares.

## 2. Objetivos
- Garantir que o agente `marceloclaro.md` esteja configurado corretamente (nome, modo, temperatura, ferramentas, permissões).
- Validar a cadeia de delegação: `marceloclaro` → `master-orchestrator` → `stage-orchestrator` → `antigravity-orchestrator`.
- Verificar a integração com o TrustEngine (Goal Drift, Guardrails, <15ms).
- Assegurar que os Cinco Pilares estejam mapeados e acionados.
- Garantir que a pergunta obrigatória de template LaTeX seja documentada.
- Validar a rastreabilidade: toda decisão gera alteração no `ecosystem-state.json`.
- Verificar o monitoramento de Token Economy.

## 3. Cenários de Teste (TDD)

| ID | Descrição | Critério de Aceite | Arquivo |
|----|-----------|-------------------|---------|
| CT-4701 | Agente existe e possui metadados corretos | `name: marceloclaro`, `mode: agent`, `temperature: 0.1` | `tests/core/test_marceloclaro.py` |
| CT-4702 | Ferramentas obrigatórias habilitadas | `bash`, `read`, `write`, `edit`, `task` todas `true` | `tests/core/test_marceloclaro.py` |
| CT-4703 | Permissões de segurança configuradas | `bash.*: allow`, `bash.rm -rf *: deny`, `bash.sudo *: deny` | `tests/core/test_marceloclaro.py` |
| CT-4704 | Cinco Pilares mapeados no agente | Pilar 1-5 explicitamente documentados com nomes | `tests/core/test_marceloclaro.py` |
| CT-4705 | Cadeia de delegação documentada | Menções a `master-orchestrator`, `stage-orchestrator`, `antigravity-orchestrator` | `tests/core/test_marceloclaro.py` |
| CT-4706 | Integração TrustEngine referenciada | Menção a `SPEC-038`, `Goal Drift`, `Guardrails`, `<15ms` | `tests/core/test_marceloclaro.py` |
| CT-4707 | Directiva LaTeX documentada | Seção de templates LaTeX com categorias Livro/Tese/CV | `tests/core/test_marceloclaro.py` |
| CT-4708 | Rastreabilidade (ecosystem-state.json) | Referência explícita a `ecosystem-state.json` no agente | `tests/core/test_marceloclaro.py` |
| CT-4709 | Token Economy monitoramento | Menção a tokens, Pay-as-you-go, TaaS | `tests/core/test_marceloclaro.py` |
| CT-4710 | Potentiality Scanner integração | Referência a `potentiality_scanner.py` e SPEC-043 | `tests/core/test_marceloclaro.py` |
| CT-4711 | Comando `/marceloclaro` registrado | Arquivo `command/marceloclaro.md` existe e documenta o comando | `tests/core/test_marceloclaro.py` |
| CT-4712 | SPEC-042 existente e válida | Arquivo `specs/SPEC-042-MARCELOCLARO-ORCHESTRATOR.md` existe | `tests/core/test_marceloclaro.py` |
| CT-4713 | Bridge TypeScript integração | `antigravity-bridge.ts` menciona `marceloclaro` e `supreme-orchestration` | `tests/core/test_marceloclaro.py` |
| CT-4714 | Temperatura determinística | `temperature: 0.1` (baixa entropia para orquestração) | `tests/core/test_marceloclaro.py` |
| CT-4715 | Persona autoritária documentada | Seção 2 (Padrão de Comportamento) com 3 regras | `tests/core/test_marceloclaro.py` |
| CT-4716 | Instruções de Invocação Interna | Seção 3 com 5 passos de invocação | `tests/core/test_marceloclaro.py` |
| CT-4717 | CLI Unificação referenciada | Pilar 4 menciona Ollama, OpenCode CLI, Antigravity CLI | `tests/core/test_marceloclaro.py` |
| CT-4718 | Dissertação rastreabilidade | Referência a "dissertação de mestrado" e "reprodutível" | `tests/core/test_marceloclaro.py` |
| CT-4719 | Modo de delegação: usuário nunca coordena | Constraint: "Nunca peça ao usuário para coordenar subagentes" | `tests/core/test_marceloclaro.py` |
| CT-4720 | TDD/SDD obrigatório | Constraint: "Use sempre TDD e SDD" | `tests/core/test_marceloclaro.py` |

## 4. Dependências
- `agents/marceloclaro.md` — Definição do agente
- `command/marceloclaro.md` — Documentação do comando
- `specs/SPEC-042-MARCELOCLARO-ORCHESTRATOR.md` — SPEC original
- `specs/SPEC-038-TRUST-ENGINE.md` — TrustEngine
- `specs/SPEC-043-POTENTIALITY-SCANNER.md` — Potentiality Scanner
- `plugins/antigravity-bridge.ts` — Bridge TypeScript
- `agents/master-orchestrator.md` — Suborquestrador
- `agents/antigravity-orchestrator.md` — Suborquestrador
- `ecosystem-state.json` — Estado do ecossistema

## 5. Fluxo de Execução TDD
1. **RED**: Escrever os 20 CTs acima (falham — arquivos não validados)
2. **GREEN**: Verificar que os arquivos existem e contêm os padrões esperados
3. **REFACTOR**: Refinar asserts para cobertura completa
4. **VALIDATE**: Executar `pytest tests/core/test_marceloclaro.py -v`
5. **REPORT**: Gerar relatório de conformidade dos 5 Pilares

## 6. Critérios de Aceite Finais
- Todos os 20 CTs devem passar (status GREEN)
- Cobertura: 100% das seções do agente validadas
- Zero falhas críticas (agent missing, spec missing, delegation missing)
- Relatório de conformidade gerado com status de cada Pilar
