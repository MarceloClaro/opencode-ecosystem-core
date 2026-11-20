---
spec_id: SPEC-935-R1238
title: Instalacao condicional e isolada do MCP OpenReverseLab
component: integrations.open_reverselab
status: planned
test_file: tests/test_r1238_open_reverselab_install.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1238-PLAN:
      - tests/test_r1238_open_reverselab_install.py::test_install_plan_pins_commit_lock_and_separates_checkout_environment_cache
      - tests/test_r1238_open_reverselab_install.py::test_install_without_yes_is_dry_run_and_creates_nothing
    R1238-INSTALL:
      - tests/test_r1238_open_reverselab_install.py::test_install_success_uses_staging_locked_wheels_and_never_starts_mcp
      - tests/test_r1238_open_reverselab_install.py::test_install_lockfile_must_match_pinned_git_blob
    R1238-IDEMPOTENCE:
      - tests/test_r1238_open_reverselab_install.py::test_valid_managed_install_is_idempotent_without_subprocesses
      - tests/test_r1238_open_reverselab_install.py::test_existing_or_partial_destination_fails_closed_without_overwrite
    R1238-STATUS:
      - tests/test_r1238_open_reverselab_install.py::test_install_receipt_records_provenance_and_forbids_activation
      - tests/test_r1238_open_reverselab_install.py::test_managed_config_uses_isolated_interpreter_but_remains_disabled
---

# SPEC-935-R1238 — Instalação condicional e isolada do MCP OpenReverseLab

## Objetivo e autorização

Completar `integrations/open_reverselab.py` para instalar o checkout e as
dependências do MCP somente quando ausentes no prefixo gerenciado, após a busca
local limitada sem correspondências resumida no checkpoint de 2026-11-20. A
instrução do usuário “instale se não encontrar” autoriza esta instalação
condicional; não autoriza iniciar/ativar o servidor MCP, analisar alvos nem
emitir parecer jurídico.

Destino padrão do checkout:
`~/.local/share/opencode-core/external-tools/open-reverselab`. O ambiente Python,
cache, HOME privado e recibo ficam em caminhos irmãos dedicados, fora do checkout.
Não copiar conteúdo upstream para o Core nem alterar o `opencode.json` ativo.

## Proveniência fixada

- Repositório: `https://github.com/LING71671/open-reverselab`.
- Commit: `c42da86aadcbea4f2dd20822653f83da5f6aba54`.
- Lockfile: `tools/skills/mcp/ReverseLabToolsMCP/uv.lock`, Git blob
  `30c5bbb363442264d3b0581e33455a791944196b` (SHA-1 do objeto Git observado).
- Projeto MCP declara `reverselab-tools-mcp` versão `0.1.0`, `GPL-3.0-only`;
  a raiz declara `Apache-2.0`. As declarações permanecem separadas e não são
  interpretadas como aprovação legal.
- Instalação apenas de dependências do projeto: `uv sync --locked
  --no-install-project --no-build`. `--locked` impede atualizar o lockfile;
  `--no-install-project` exclui o código do MCP como pacote instalado; `--no-build`
  recusa builds de sdist de dependências. O checkout e seu lockfile pinado devem
  ser inspecionados antes desta operação.

## Contrato

1. `install_plan()` descreve, sem efeitos, os comandos fixos Git/uv, o commit,
   o lockfile esperado e caminhos absolutos distintos para checkout, venv,
   cache, HOME e recibo. O destino padrão não pode apontar para dentro do
   repositório Core.
2. `install_isolated()` é dry-run por padrão; somente `yes=True`/CLI `--yes`
   executa. Timeout é limitado (1–600 s), argumentos são listas fixas, sem shell,
   ambiente mínimo com HOME/config/cache privados e sem credenciais herdadas.
3. Instalar em staging dentro do mesmo filesystem: inicializar Git sem executar
   scripts do projeto, buscar apenas o commit fixado, fazer checkout detached,
   validar checkout e blob do lockfile, sincronizar somente dependências pinadas
   em venv externo usando `--locked --no-install-project --no-build`, validar
   resultados e só então publicar o checkout no caminho final.
4. Se o destino já estiver completo e o recibo válido, retornar
   `already_installed` sem rede, Git, uv ou alterações. Qualquer destino
   existente parcial, symlinkado, divergente ou sem recibo confiável falha
   fechado, sem sobrescrever/remover arquivos preexistentes.
5. Gravar atomicamente um recibo fora do checkout com commit, blob do lockfile,
   caminhos gerenciados, sucesso de `uv sync`, data UTC, e estados explícitos
   `upstream_mcp_executed=false`, `mcp_enabled=false`, `target_analysis=false` e
   `legal_review=not_performed`. O recibo documenta a operação, não prova
   segurança do upstream nem execução funcional do servidor.
6. `status()` pode observar apenas o prefixo gerenciado e seu recibo local, sem
   receber caminho arbitrário, acessar rede ou executar o projeto. Deve separar
   instalação observada de execução/ativação. A configuração candidata para o
   checkout gerenciado usa o Python do venv externo, mas permanece
   `disabled: true`; não escrever configurações ativas.
7. Preservar a entrada histórica bloqueada R1232 e o manifesto R1237 como
   registros históricos da integração anterior. Acrescentar registro/recibo
   R1238 sem converter as declarações de licença em revisão jurídica.
8. Testes usam fixtures e runners mockados/offline: sem clonar, instalar, baixar
   dependências, iniciar MCP, chamar ferramentas MCP ou analisar amostras/alvos.

## Critérios executáveis

- `R1238-PLAN`: o plano fixa origem/commit/blob e separa ambientes; o caminho
  sem confirmação não cria diretórios nem invoca subprocessos.
- `R1238-INSTALL`: o fluxo confirmado opera em staging, rejeita lockfile fora do
  pin, sincroniza somente dependências por lock e não inicia o MCP/alvos.
- `R1238-IDEMPOTENCE`: instalação válida é no-op; caminho parcial, conflitante
  ou inseguro não é alterado.
- `R1238-STATUS`: recibo distingue instalação de execução/ativação; configuração
  gerada aponta para o ambiente isolado e continua desabilitada.

## Verificação e limites

- TDD RED antes da implementação e GREEN após; validar os critérios através do
  `SpecVerifier`, testes focais e regressão R1237, `git diff --check`.
- Depois do gate, executar instalação real apenas no prefixo padrão se ele
  continuar ausente; registrar saída, código de retorno, caminhos e hashes.
- Não iniciar o MCP como smoke test: disponibilidade, segurança, licença e
  comportamento do upstream permanecem não verificados; a avaliação jurídica
  continua não realizada.
