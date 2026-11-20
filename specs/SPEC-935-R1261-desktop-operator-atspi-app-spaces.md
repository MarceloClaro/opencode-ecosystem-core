---
spec_id: SPEC-935-R1261
title: Aceitar espaços internos em nomes de aplicações AT-SPI
component: integrations.desktop_operator.policy
status: specified
test_file: tests/test_r1261_desktop_operator_app_labels.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1261-APP-LABEL:
      - tests/test_r1261_desktop_operator_app_labels.py::test_allowlisted_app_name_with_spaces_is_preserved_as_one_argv_value
    R1261-POLICY:
      - tests/test_r1261_desktop_operator_app_labels.py::test_app_name_still_requires_exact_allowlist_match
      - tests/test_r1261_desktop_operator_app_labels.py::test_app_name_rejects_boundary_whitespace_controls_and_shell_syntax
---

# SPEC-935-R1261 — espaços em nomes de aplicações AT-SPI

## Objetivo

Corrigir o seletor de aplicação do `desktop-operator` para aceitar nomes
visíveis AT-SPI que contenham espaços internos, em particular `Burp Suite`,
sem enfraquecer a validação lexical nem a allowlist explícita. O nome aceito
deve continuar sendo entregue ao subprocesso como um único argumento, sem
interpretação por shell.

## Escopo

- Ajustar somente a validação lexical de nome de aplicação em
  `integrations/desktop_operator/policy.py`.
- Acrescentar testes unitários offline em
  `tests/test_r1261_desktop_operator_app_labels.py`.
- Registrar os critérios executáveis neste contrato de evidência.

## Fora de escopo e limites de segurança

- Não alterar a allowlist de aplicações, os fluxos de aprovação, os backends
  AT-SPI/agent-desktop, a configuração do Burp ou a configuração do OpenCode.
- Não operar a interface gráfica, aceitar termos, emitir token de aprovação
  para o app real, clicar, digitar ou enviar tráfego a qualquer alvo.
- Preservar a comparação case-insensitive, mas exata, com cada entrada da
  allowlist; a inclusão de espaço não autoriza apps não listados.
- Continuar rejeitando espaços nas extremidades, controles, NUL, metacaracteres
  de shell e nomes com mais de 120 caracteres. Restringir a inclusão nova ao
  caractere ASCII espaço; não ampliar a classe de caracteres histórica.

## Contrato funcional

1. `Burp Suite` e outros nomes permitidos pela classe lexical podem ser
   validados quando constarem na allowlist.
2. A validação de `build_argv("snapshot", ...)` conserva o nome integral em
   um único item `--app <nome>`, sem split, quoting ou expansão de shell.
3. Nome com espaço não presente na allowlist continua negado com
   `app_not_allowed`; espaços nas extremidades e caracteres não permitidos
   continuam negados com `app_invalid`.
4. Permanecem inalterados os limites de comprimento, comandos, refs, aprovações,
   escopo AT-SPI e o restante da política.

## Critérios de aceitação executáveis

- `R1261-APP-LABEL`: o teste demonstra que `Burp Suite`, quando explicitamente
  allowlisted, passa em `require_app` e aparece intacto como um único valor do
  argv de `snapshot`.
- `R1261-POLICY`: os testes demonstram que a allowlist permanece necessária e
  exata, e que whitespace de borda, controles, metacaracteres e comprimento
  acima de 120 continuam rejeitados.
- A regressão `tests/test_r1060_desktop_operator.py` permanece verde.

## Plano RED → GREEN → REFACTOR e verificação

1. Criar este contrato e os testes focais antes da implementação.
2. Executar o novo teste e registrar a falha inicial causada pela regex que
   atualmente rejeita espaço interno.
3. Aplicar a menor alteração em `APP_RE`; repetir os testes focais e a regressão
   desktop-operator.
4. Executar `git diff --check`, validar o contrato no `SpecVerifier` e revisar
   o diff para confirmar os limites de escopo.

O gate de execução cobre apenas a validação local e montagem segura de argv; não
prova que o Burp esteja operacional nem autoriza qualquer interação com sua UI.
