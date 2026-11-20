---
spec_id: SPEC-935-R1265
title: Permitir snapshots AT-SPI até profundidade 12 com as mesmas barreiras de ação
component: integrations.desktop_operator.atspi_backend
status: specified
test_file: tests/test_r1265_desktop_operator_atspi_depth.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1265-DEPTH:
      - tests/test_r1265_desktop_operator_atspi_depth.py::test_policy_accepts_depth_12_and_rejects_depth_13
      - tests/test_r1265_desktop_operator_atspi_depth.py::test_atspi_snapshot_returns_qualified_ref_at_depth_12
    R1265-READ-ONLY:
      - tests/test_r1265_desktop_operator_atspi_depth.py::test_deep_snapshot_only_reads_tree_and_does_not_activate_action
---

# SPEC-935-R1265 — snapshots AT-SPI até profundidade 12

## Objetivo

Permitir que o snapshot somente de leitura do `desktop-operator` alcance nós
AT-SPI até profundidade 12. A tela inicial do Burp expõe a opção Community
Edition nessa profundidade, fora do limite atual 8; o seletor aprovado não
consegue gerar um ref qualificado para o botão sem esse alcance.

## Escopo

- Elevar o limite máximo de `max_depth` de 8 para 12 em
  `integrations/desktop_operator/policy.py` e no backend AT-SPI.
- Preservar o default atual 6, o mínimo 1, o orçamento de nós, a allowlist de
  apps, a validação de refs e a montagem de argv.
- Cobrir o limite de política e a serialização de um controle sintético em
  profundidade 12, sem abrir ou alterar uma UI real.

## Limites de segurança

- A mudança amplia somente leitura da árvore de acessibilidade; snapshot não
  ativa ações nem autoriza cliques ou digitação.
- Cada ação `click`/`type` continua exigindo aprovação local de uso único
  vinculada ao app, ref e, quando aplicável, texto.
- Não aumentar orçamento de nós, alterar allowlists, habilitar screenshot,
  teclado/mouse, shell ou modos de sessão.
- Não editar configurações do Burp/OpenCode nem emitir token nesta alteração.

## Critérios de aceitação executáveis

- `R1265-DEPTH`: `max_depth=12` é aceito e chega intacto ao argv; `13` continua
  negado. O backend AT-SPI serializa um controle de profundidade 12 e lhe dá
  ref qualificado conforme o snapshot.
- `R1265-READ-ONLY`: a cobertura sintética demonstra que serializar o controle
  apenas o descreve; nenhuma interface de ação é invocada pelo snapshot.
- A regressão `tests/test_r1060_desktop_operator.py` permanece verde, incluindo
  o gate que nega clique sem aprovação.

## Plano RED → GREEN → REFACTOR

1. Registrar este contrato e os testes antes da implementação.
2. Registrar RED por falha de asserção: política rejeita 12 e backend omite o
   controle além de profundidade 8.
3. Elevar o mesmo limite para 12 nas duas fronteiras, sem alterar outras
   permissões; repetir testes e regressão.
4. Validar SpecVerifier e `git diff --check`.

A aprovação cobre somente serialização local e contrato de profundidade. Ela
não comprova instalação do BApp, execução de clique ou comunicação MCP.
