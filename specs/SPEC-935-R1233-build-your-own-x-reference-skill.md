---
spec_id: SPEC-935-R1233
title: Integrar Build Your Own X como referência educacional segura
component: .opencode/skills/build-your-own-x
status: green
test_file: tests/test_r1233_build_your_own_x.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1233-PROVENANCE:
      - tests/test_r1233_build_your_own_x.py::test_source_manifest_pins_repository_commit_and_license_boundary
    R1233-REFERENCE-ONLY:
      - tests/test_r1233_build_your_own_x.py::test_manifest_forbids_install_execution_and_mcp_enablement
    R1233-SKILL:
      - tests/test_r1233_build_your_own_x.py::test_skill_is_discoverable_and_uses_pinned_upstream_reference
      - tests/test_r1233_build_your_own_x.py::test_skill_preserves_downstream_license_and_execution_boundaries
---

# SPEC-935-R1233 — Integração de referência Build Your Own X

## Objetivo

Adicionar ao Core uma skill OpenCode sob demanda que ajude a selecionar
tutoriais de implementação “from scratch” do repositório
`codecrafters-io/build-your-own-x` e convertê-los em planos originais de estudo
ou implementação, preservando proveniência e fronteiras de licença.

## Evidência observada (2026-11-20)

- Repositório: <https://github.com/codecrafters-io/build-your-own-x>.
- Commit observado na branch `master`: `94e4be4102452119008fe47199f3cb915abe0c50`;
  a API GitHub reportou assinatura verificada (`verified=true`, motivo `valid`).
- A API GitHub reportou `license=null` e o endpoint `/license` respondeu 404.
- O README desse commit exibe o distintivo CC0-1.0 e declara a renúncia de
  direitos da CodeCrafters, Inc. “to the extent possible under law”. A integração
  registra isso como declaração do README, não como parecer jurídico.
- O README é uma lista de links para materiais de terceiros. A licença e os
  termos de cada tutorial/projeto vinculado não são determinados pela licença
  declarada para a compilação do README.

## Contrato

1. Criar `.opencode/skills/build-your-own-x/SKILL.md` com identificação e
   descrição úteis para descoberta pelo OpenCode, roteiro de seleção e saída
   educacional original em português.
2. Criar `federation/build-your-own-x.json` como registro de proveniência
   versionado, fixando URL, commit, assinatura observada, declaração de licença,
   data da observação e estado `reference_only`.
3. Registrar separadamente que GitHub não forneceu metadado de licença e que
   CC0 é uma declaração observada no README; não afirmar certificação legal.
4. Tratar cada tutorial/projeto vinculado como fonte independente: confirmar
   origem, atualidade e licença antes de reproduzir conteúdo, código ou ativos.
5. Não copiar o README completo, tutoriais, código, assets ou materiais
   vinculados. Não clonar, instalar, executar, habilitar MCP, acessar credenciais
   nem alterar a configuração do ChatGPT/OpenCode como parte desta integração.
6. A skill pode propor um plano original e testes para um projeto do usuário, mas
   qualquer implementação real continua sujeita à autorização específica,
   SDD/TDD, revisão de segurança e testes próprios do Core.
7. A integração não habilita nem autoriza o conector Tunnel no workspace ou na
   conversa ChatGPT; essa configuração externa não é controlada pelo Core local.

## Critérios de aceitação executáveis

- `R1233-PROVENANCE` O manifesto fixa repositório e commit observado, registra a
  assinatura declarada pela API e distingue CC0 declarado no README de licença
  não informada pela API e de revisão jurídica não realizada.
- `R1233-REFERENCE-ONLY` A adoção permanece `reference_only`; instalação,
  execução, ativação e MCP permanecem falsos, e nenhum conteúdo upstream é
  importado.
- `R1233-SKILL` A skill é descoberta no diretório de projeto, cita URL e commit
  fixados, descreve fluxo e saída originais e preserva a licença independente
  de cada recurso vinculado.

## Verificação e limites

- Executar primeiro os testes novos e registrar RED antes de adicionar o
  manifesto e a skill. Os testes são offline e não baixam nem executam conteúdo
  de terceiros.
- Executar testes focais, `python3 -m marceloclaro.cli doctor` pelo `.venv` e
  `git diff --check`.
- Mudanças preexistentes em `SPEC-935-R1232` e artefatos associados são
  preservadas; nenhum estado externo é declarado executado ou habilitado.

## Fora de escopo

- Replicar ou indexar localmente todos os tutoriais/links do README.
- Avaliar a qualidade, segurança, compatibilidade ou eficácia pedagógica de
  cada link listado.
- Instalar executores/projetos, chamar APIs de terceiros ou ativar servidores
  MCP.
- Alterar ou autorizar integrações no ChatGPT, no Codex ou em workspaces externos.
