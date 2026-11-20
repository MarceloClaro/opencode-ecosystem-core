---
spec_id: SPEC-935-R1266
title: Seleção AT-SPI de page tabs somente por click aprovado
component: integrations.desktop_operator.atspi_backend
status: specified
test_file: tests/test_r1266_desktop_operator_atspi_tab_selection.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1266-SELECT:
      - tests/test_r1266_desktop_operator_atspi_tab_selection.py::test_snapshot_qualifies_page_tab_with_parent_selection
      - tests/test_r1266_desktop_operator_atspi_tab_selection.py::test_page_tab_without_selection_iface_is_not_clickable
    R1266-APPROVAL:
      - tests/test_r1266_desktop_operator_atspi_tab_selection.py::test_click_selects_tab_only_after_one_time_approval
---

# SPEC-935-R1266 — seleção de abas AT-SPI sob aprovação

## Objetivo

Permitir que o backend AT-SPI represente e selecione um nó `page tab` quando
seu pai oferecer a interface `Selection.select_child(index)`. O snapshot do
Burp expõe a aba BApp Store dessa forma, sem interface de ação no próprio nó;
portanto, atualmente não há ref qualificado para selecioná-la pelo fluxo
seguro do desktop-operator.

## Escopo

- Incluir refs somente para nós de papel `page tab` cujo pai exponha
  `Selection.select_child` chamável.
- Ao receber `click` para esse ref, revalidar app, PID e caminho do snapshot e
  selecionar o índice exato da aba no pai por `Selection.select_child`.
- Manter a rota existente para nós com `Action.do_action`; não usar Selection
  como fallback genérico para outros papéis.
- Preservar o fluxo existente de token de aprovação local, de uso único e
  vinculado a `click`/app/ref; nenhuma seleção ocorre antes dessa validação.

## Limites de segurança

- Snapshot continua somente leitura.
- Ação de seleção usa apenas o ref atual e o caminho armazenado no snapshot;
  não procura abas por texto no momento do clique, não aceita índice do
  chamador e não muda a allowlist nem o schema MCP.
- Não adicionar teclado, mouse, clipboard, screenshot, shell, digitação,
  requisições Burp ou ações de scanners.
- Refs de tabs sem interface Selection adequada não são emitidos.
- A seleção é reportada como `delivered_unverified`; o estado posterior deve
  ser observado por novo snapshot, sem retry automático.

## Critérios de aceitação executáveis

- `R1266-SELECT`: snapshot emite ref qualificado para page tab sob pai com
  `Selection.select_child`, conserva o índice do filho e não emite ref para
  page tab cujo pai não tenha essa interface. Click seleciona exatamente esse
  índice e não chama `Action.do_action`.
- `R1266-APPROVAL`: chamada `click` sem token é negada e não seleciona nada;
  aprovação válida de uso único permite uma única seleção, com retorno
  `delivered_unverified`.
- Os testes de regressão R1060 e R1265 continuam aprovados; nenhum contrato de
  aprovação, allowlist ou comando é relaxado.

## Plano RED → GREEN → REFACTOR

1. Registrar spec e testes sintéticos antes da implementação.
2. Registrar RED por falha de asserção: o snapshot não emite ref para page tab
   selecionável e o teste de aprovação não chega à seleção.
3. Implementar suporte restrito a `page tab`/`Selection.select_child`, sem
   tocar nos demais comandos ou permissões.
4. Validar critérios com TDDRunner/SpecVerifier, regressões focais e
   `git diff --check`.

A validação cobre somente o contrato AT-SPI sintético/local. Não afirma que a
aba BApp Store foi selecionada, que o BApp foi instalado, nem que o endpoint
MCP está ativo.
