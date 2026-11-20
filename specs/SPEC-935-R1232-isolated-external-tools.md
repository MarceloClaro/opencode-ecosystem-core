---
spec_id: SPEC-935-R1232
title: Integrar ferramentas externas isoladas e referências curadas
component: integrations.external_tools_isolated
status: specified
test_file: tests/test_r1232_isolated_external_tools.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1232-CATALOG:
      - tests/test_r1232_isolated_external_tools.py::test_manifest_pins_sources_licenses_and_isolation_states
      - tests/test_r1232_isolated_external_tools.py::test_reference_only_and_blocked_entries_have_no_install_or_execution_claim
      - tests/test_r1232_isolated_external_tools.py::test_prompts_chat_is_catalog_only_with_dual_license_boundary
      - tests/test_r1232_isolated_external_tools.py::test_manifest_records_license_and_adoption_states_without_collapsing_them
      - tests/test_r1232_isolated_external_tools.py::test_manifest_policy_validation_fails_closed_for_contradictory_states
      - tests/test_r1232_isolated_external_tools.py::test_status_is_read_only_local_inventory
    R1232-RUST:
      - tests/test_r1232_isolated_external_tools.py::test_rust_anything_install_plan_isolated_and_integrity_pinned
      - tests/test_r1232_isolated_external_tools.py::test_rust_anything_runner_never_uses_shell_or_global_install
      - tests/test_r1232_isolated_external_tools.py::test_install_without_confirmation_is_plan_only
      - tests/test_r1232_isolated_external_tools.py::test_npm_integrity_mismatch_stops_before_install
      - tests/test_r1232_isolated_external_tools.py::test_npm_install_uses_only_tarball_verified_against_pinned_integrity
    R1232-UOS:
      - tests/test_r1232_isolated_external_tools.py::test_universal_os_isolated_and_mcp_disabled_by_default
      - tests/test_r1232_isolated_external_tools.py::test_universal_os_never_accepts_iso_or_vm_execution_in_this_scope
    R1232-CAVEMAN:
      - tests/test_r1232_isolated_external_tools.py::test_caveman_environment_disables_telemetry_cloud_and_global_state
      - tests/test_r1232_isolated_external_tools.py::test_caveman_runner_rejects_setup_login_and_agent_install_commands
    R1232-SKILLS:
      - tests/test_r1232_isolated_external_tools.py::test_only_selected_anthropic_skills_are_imported_with_license_and_hashes
      - tests/test_r1232_isolated_external_tools.py::test_imported_skills_are_not_implicitly_activated
    R1232-REA:
      - tests/test_r1232_isolated_external_tools.py::test_existing_rea_install_is_reused_without_upgrade_or_duplicate
    R1232-REGRESSION:
      - tests/test_r1232_isolated_external_tools.py::test_catalog_does_not_expose_unapproved_mcp_servers
---

# SPEC-935-R1232 — Integrações externas isoladas e referências curadas

## Objetivo

Registrar e integrar, em fronteiras separadas, os repositórios indicados pelo
usuário para engenharia reversa, ferramentas de agente e gestão de tokens. O
Core permanece responsável pelo ciclo SDD/TDD e não transforma disponibilidade,
instalação, metadados upstream ou alegações de benchmark em prova de qualidade.

## Escopo autorizado e proveniência observada

| Fonte | Referência observada | Licença/situação | Tratamento autorizado |
|---|---|---|---|
| `erkamyaman/rust-anything` / npm `rust-anything` | versão `2.1.0`; `gitHead=71c78e10c5beb39acecd52c2eb3f675a199f3cea`; npm integrity `sha512-3djIcDXD5kQIQJRnR/4dtiBZYoKf6pKnPaU38AuhxN5HBpZfnyedOSUDdAqQA5uFQ/rSuDJvA4GVfVjUUXZV9w==` | MIT | Integração/instalação isolada, sem instalação global. A instalação de 126,965,553 bytes desempacotados deve ser explicitada no plano e não deve ser executada como efeito colateral dos testes. |
| `AIshihzong/awesome-reverse-engineer-anything` | commit `578cb1108760eed8cf09a22b49355909cf86c91f` | CC0-1.0 | Somente referência/catálogo. Não executar projetos listados nem repetir claims como evidência verificada. |
| `LING71671/open-reverselab` | commit `c42da86aadcbea4f2dd20822653f83da5f6aba54` | Apache-2.0 na raiz; disclaimer com obrigações incompatíveis/ambíguas e pacote MCP aninhado `GPL-3.0-only` | Estado `blocked_legal_review`; somente metadados mínimos e registro do bloqueio. Não clonar, instalar, importar, executar, adaptar conteúdo ou habilitar MCP nesta entrega. |
| `Jenischristan/universal-os` | commit `661f15fc1afbbe1158ac5d14673e188238f29c0c`, versão `0.2.1` | MIT | Adaptador/instalação isolada, MCP desabilitado por padrão. Sem fornecer ISO, iniciar QEMU/VM, analisar imagem ou reconstruir/testar SO. |
| `anthropics/skills` | commit `e4bb5d960d87126ff3b3a8af1a104b7db67560ba` | Licença por skill; `mcp-builder` e `skill-creator` observadas com Apache-2.0 | Importar somente estas duas skills, preservando licença, atribuição, commit e hashes. Nenhuma outra pasta do repositório é incluída. As skills permanecem explícitas/não implícitas conforme política local. |
| `JuliusBrussee/caveman` / npm `@caveman-ai/cli` | repositório commit `a192894723a8f47e7f504c7b5041967ff1f18e55`; pacote `4.1.0`, integrity `sha512-5+qoA9GydY6OlQYQLhAtAt+eQC8xW7mzWeuq4XBSAacgyOJ4fyyurzLFlc9r1YTcobL4lZbDYwewSPINOXqNdg==` | Apache-2.0 | CLI isolada; sem interceptar/substituir comandos globais de agentes. `DO_NOT_TRACK=1`, `CAVEMAN_TELEMETRY=0`, `CAVEMAN_OFFLINE=1` e `CAVEMAN_HOME` privado devem ser aplicados em cada processo. Auto, login, gateway/cloud, hooks e integração de agentes ficam bloqueados. |
| `farion1231/cc-switch` | commit `2a750c3fcbbefa9550047d7dd3363d9120e545ed` observado em 2026-11-20 | MIT | Somente catalogação. Não instalar/abrir aplicativo, importar configs, ler credenciais, reescrever endpoints ou iniciar roteamento/sync. |
| `f/prompts.chat` | commit `29417a15542c01938e2230d4c2dcee95771ae6aa`, observado em 2026-11-20 | Licença dupla: app/código MIT; prompts/dados CC0-1.0 | Somente catalogação. Não baixar o corpus, instalar/self-host a aplicação, habilitar MCP local/remoto nem tratar prompts enviados por usuários como instruções confiáveis. |
| `morluto/rea` | `rea-agents@6.8.0`, já instalado; trilha existente em `SPEC-935-R1066` | MIT | Reutilizar a integração existente. Não instalar outra cópia, atualizar, duplicar ferramentas nem ampliar permissões nesta entrega. |

As referências a commits e metadados são fotografias da pesquisa, não auditoria
de segurança nem validação jurídica. A condição de OpenReverseLab permanece
bloqueante, apesar da escolha de incluí-lo no escopo isolado; qualquer liberação
exige revisão jurídica humana explícita.

## Contrato de implementação

1. O manifesto `federation/repository-curation-r1232.json` distingue `installed`,
   `executed`, `enabled`, `license_status` e `integration_status`; desconhecido,
   planejado, bloqueado e observado não podem ser colapsados em `ready`. A
   validação falha fechada diante de estados ausentes ou contraditórios.
2. Rust Anything, Universal OS e Caveman usam diretórios/ambientes isolados.
   Pacotes npm são obtidos por `npm pack --ignore-scripts`; o SRI reportado e o
   SHA-512 local do tarball precisam coincidir com o pin antes de instalar o
   tarball local. Universal OS fixa o commit completo e configura `UV_TOOL_DIR`,
   `UV_TOOL_BIN_DIR` e cache privados. Subprocessos usam argv fechado, sem shell
   e com timeout; instalação só ocorre por chamada explícita confirmada. `status`,
   doctor e testes não instalam nem consultam serviços externos.
3. Nenhum MCP de terceiros é adicionado automaticamente ao `opencode.json` nem
   iniciado. A ativação futura exige configuração separada e consentimento
   explícito; essa entrega pode apenas preparar a configuração desabilitada.
4. Universal OS não recebe caminho de ISO nem aceita comandos de VM/QEMU. Rust
   Anything não recebe alvo do usuário nesta entrega; nenhuma reescrita de
   projeto é executada.
5. Caveman não toca `$HOME` real de agentes nem escreve em `.claude`, `.codex`,
   `.gemini`, `.config/opencode` ou `opencode.json`. Os comandos proibidos
   incluem setup/login, instalação de hooks/extensões, mudança de provider,
   Auto/cloud e execução de agentes-alvo. O executor injeta os quatro controles
   ambientais definidos acima, configura cache/arquivos npm privados e não
   herda segredos do ambiente do Core.
6. As duas skills Anthropic são importadas em diretórios próprios, cada uma com
   `SKILL.md`, `LICENSE.txt`, `source.json` (repo, commit, caminho, SHA-256,
   política de ativação) e todos os arquivos regulares do respectivo diretório
   de skill no commit pinado. O overlay local do frontmatter desliga invocação
   implícita; os hashes upstream e importados são reconciliáveis. Scripts ficam
   sem bit executável e não são executados durante importação ou testes.
7. Awesome REA, CC Switch e prompts.chat são entradas `reference_only`;
   OpenReverseLab é `blocked_legal_review`. Não se copia conteúdo desses itens.
8. REA 6.8.0 permanece como implementação canônica de reverse engineering; o
   novo catálogo aponta para a integração existente, sem recapturar sua
   instalação nem declarar que suas camadas externas estejam disponíveis.

## Critérios de aceitação

1. O manifesto JSON é validado por schema/testes, registra proveniência e
   mantém estados de instalação, execução e ativação separados.
2. O plano de Rust Anything fixa pacote, versão, integridade, diretório e
   tamanho estimado; a instalação aborta antes de extrair se SRI/metadados/hash
   local divergirem. Nenhuma instalação global ou análise de alvo ocorre.
3. Universal OS fica isolado e desabilitado; os testes provam que ISO, QEMU,
   VM, MCP e comandos de reconstrução não são invocados.
4. Caveman fica isolado, com telemetria e rede de cloud desativadas no processo,
   sem escrita em configs globais nem comandos de setup/login/hooks/agent.
5. Apenas `mcp-builder` e `skill-creator` são incluídas no commit Anthropic
   fixado; arquivos, licenças e SHA-256 são reconciliáveis; invocação implícita
   fica desativada.
6. OpenReverseLab não é baixado nem executado; o conflito de licenças permanece
   marcado como bloqueio. Awesome REA, CC Switch e prompts.chat não alegam
   instalação nem uso; prompts.chat mantém separadas as licenças do código e do
   corpus de prompts.
7. REA existente é reutilizado sem alteração da versão, instalação ou MCP.
8. Testes focais, regressões pertinentes, `python -m marceloclaro.cli doctor`
   com o Python de `.venv` e revisão de diff passam; testes de instalação usam
   runners mockados e não baixam pacotes. Todo estado externo não observado é
   relatado como não observado.

## Fora de escopo

- Resolver conflito legal do OpenReverseLab ou incorporar seu MCP GPL.
- Baixar/imagem/boot de SOs, executar análise sobre alvos, construir binários,
  ou testar software de terceiros.
- Habilitar qualquer MCP de fornecedor, integrar credenciais, contas, provider
  routing, telemetria, hooks globais, login ou Cloud.
- Declarar benchmarks/benefícios de token do Caveman ou qualidade de qualquer
  executor como confirmados pelo Core.
