---
spec_id: SPEC-935-R1237
title: Adaptador OpenReverseLab opcional com MCP desabilitado por padrão
component: integrations.open_reverselab
status: implemented
test_file: tests/test_r1237_open_reverselab_adapter.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1237-PROVENANCE:
      - tests/test_r1237_open_reverselab_adapter.py::test_manifest_pins_source_and_preserves_license_boundary_and_authorization_scope
      - tests/test_r1237_open_reverselab_adapter.py::test_manifest_validation_fails_closed_on_license_or_runtime_drift
      - tests/test_r1237_open_reverselab_adapter.py::test_historical_r1232_block_remains_unchanged
    R1237-CHECKOUT:
      - tests/test_r1237_open_reverselab_adapter.py::test_inspection_accepts_only_exact_clean_local_checkout_without_running_project_code
      - tests/test_r1237_open_reverselab_adapter.py::test_inspection_rejects_wrong_commit_dirty_tree_and_missing_mcp_files
      - tests/test_r1237_open_reverselab_adapter.py::test_inspection_rejects_upstream_license_declaration_drift
      - tests/test_r1237_open_reverselab_adapter.py::test_inspection_rejects_source_file_drift_even_if_git_status_reports_clean
      - tests/test_r1237_open_reverselab_adapter.py::test_inspection_rejects_symlinked_root_and_mcp_components
    R1237-OPT-IN:
      - tests/test_r1237_open_reverselab_adapter.py::test_generated_opencode_entry_is_disabled_and_never_mutates_active_config
      - tests/test_r1237_open_reverselab_adapter.py::test_config_refuses_invalid_or_unpinned_checkout
      - tests/test_r1237_open_reverselab_adapter.py::test_cli_status_and_config_are_read_only_json_operations
---

# SPEC-935-R1237 — Adaptador OpenReverseLab opcional e inerte por padrão

## Objetivo e autorização

Implementar um adaptador original do Core para reconhecer um checkout local do
OpenReverseLab no commit fixado e emitir, somente em stdout, uma configuração
candidata de MCP para OpenCode. A entrada gerada deve manter o servidor
explicitamente desabilitado. Este trabalho não instala, clona, baixa, inicia,
ativa nem executa o OpenReverseLab ou seu MCP e não analisa qualquer alvo.

A mensagem explícita do usuário autorizou a integração no Core. Essa autorização
não é parecer jurídico, não transforma declarações de licença em aprovação e não
altera retroativamente o estado histórico de R1232.

## Proveniência observada

- Repositório: `LING71671/open-reverselab`.
- Commit fixado: `c42da86aadcbea4f2dd20822653f83da5f6aba54`.
- A raiz do repositório declara Apache-2.0 em `LICENSE`.
- `tools/skills/mcp/ReverseLabToolsMCP/pyproject.toml` declara versão `0.1.0`
  e licença `GPL-3.0-only` para o subprojeto MCP.
- O upstream contém `DISCLAIMER.md` (blob GitHub observado
  `025efb705062b5782b826d317388674bfe88a5ff`); seu conteúdo não é tratado como
  orientação jurídica vinculante ou como substituto da autorização do usuário.
- README do MCP documenta execução com `uv` e enumera ferramentas locais de
  gerenciamento/análise de amostras. Essas capacidades elevam o risco de uma
  ativação implícita; este adaptador não invoca nem importa o MCP.

## Contrato

1. Adicionar `federation/open-reverselab-adapter-r1237.json` como registro novo,
   preservando a entrada histórica bloqueada em
   `federation/repository-curation-r1232.json`. Separar licença declarada da
   raiz e do MCP GPL, registrar escopo da autorização do usuário e declarar
   explicitamente `legal_review=not_performed`.
2. Implementar `integrations/open_reverselab.py` com operações de status,
   inspeção de checkout local e emissão de configuração candidata. Status não
   recebe caminhos nem faz I/O externo; inspeção exige caminho explícito e
   fixo no commit observado, valida os arquivos/manifests requeridos e consulta
   somente metadados Git por argv fixo, sem shell e com timeout limitado.
3. Recusar caminhos inexistentes, não absolutos, symlinkados ou fora da raiz
   Git; recusar commit divergente, working tree suja, arquivos MCP ausentes ou
   symlinkados e declaração de licença/versão diferente. Conferir os blobs das
   fontes relevantes no commit fixado contra os bytes locais, mesmo se o Git
   informar uma working tree aparentemente limpa. Não seguir caminhos que
   escapem do checkout.
4. A configuração candidata é apenas saída JSON: servidor MCP local com
   `disabled: true`, `command` em lista argv, `cwd` explícito e execução de
   `uv run --no-sync`. Não escrever `opencode.json`, `.opencode/` ou arquivos do
   checkout. `--no-sync` evita sincronização automática de dependências; o
   adaptador não instala nem garante dependências previamente instaladas. Como
   o processo herdaria ambiente do OpenCode, o fragmento exige revisão explícita
   dessa exposição antes de qualquer ativação posterior.
5. Não copiar, adaptar, importar, empacotar ou executar código, documentação,
   scripts, skills, ferramentas, binários ou conteúdo do OpenReverseLab. O Core
   mantém somente o adaptador próprio, metadados de proveniência e caminhos
   apontados pelo usuário.
6. Preservar os estados runtime `installed=false`, `executed=false`,
   `enabled=false`, `mcp_enabled=false`, `content_imported=false`. Nenhuma
   instalação/ativação, chamada a ferramentas MCP, análise de amostra ou teste
   de alvo faz parte da autorização atual.
7. Testes devem usar fixtures e runner Git mockado/offline; não executar código
   upstream, acessar a rede, instalar dependências, iniciar servidor MCP ou
   modificar configurações ativas.

## Critérios de aceitação executáveis

- `R1237-PROVENANCE` O manifesto valida commit, fonte, declarações separadas de
  licenças, disclaimer observado e limite da autorização; runtime permanece
  inerte e R1232 continua historicamente bloqueado.
- `R1237-CHECKOUT` A inspeção só aceita checkout local limpo no commit fixado,
  valida arquivos e metadados sem importar/executar código do projeto, e falha
  de modo fechado para caminhos, symlinks, dirty tree, blobs locais, pin ou
  licença inválidos.
- `R1237-OPT-IN` A saída candidata usa o schema OpenCode local MCP com
  `disabled: true`, `uv run --no-sync`, argv sem shell e caminhos absolutos; as
  operações não alteram `opencode.json`, não instalam, não ativam e não lançam
  o processo.

## Verificação e limites

- Registrar RED antes de implementar o adaptador; GREEN deve executar os
  critérios por meio do contrato formal desta SPEC.
- Rodar testes focais, regressões relevantes, SpecVerifier, `git diff --check`
  e doctor estrutural.
- A verificação local não é revisão jurídica, validação de segurança do
  upstream, prova de funcionamento do servidor MCP, nem autorização para
  instalar/ativar serviços ou analisar alvos.

## Uso local

- `python3 -m integrations.open_reverselab status` valida somente o manifesto.
- `python3 -m integrations.open_reverselab inspect --path /caminho/absoluto`
  consulta checkout local e seus metadados Git sem executar o projeto.
- `python3 -m integrations.open_reverselab config --path /caminho/absoluto`
  emite um fragmento OpenCode v2 com `disabled: true`; não o grava nem o ativa.

## Fora de escopo

- Clonar, baixar, instalar, atualizar, compilar ou executar o OpenReverseLab ou
  suas dependências; iniciar CLI, GUI, MCP, Ghidra ou ferramentas de terceiros.
- Ativar/registrar o MCP no `opencode.json` ou qualquer configuração do usuário.
- Executar ou analisar arquivos, amostras, alvos ou ativos de qualquer natureza.
- Copiar qualquer conteúdo do upstream, avaliar juridicamente a interação entre
  licenças ou declarar conformidade legal.
