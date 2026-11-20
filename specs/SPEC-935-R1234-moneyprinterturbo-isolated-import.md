---
spec_id: SPEC-935-R1234
title: MoneyPrinterTurbo v1.3.10 isolado e importação local de MP4
component: integrations.moneyprinterturbo
status: specified
test_file: tests/test_r1234_moneyprinterturbo_import.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1234-PROVENANCE:
      - tests/test_r1234_moneyprinterturbo_import.py::test_manifest_pins_upstream_version_commit_and_wheel_hash
    R1234-ISOLATION:
      - tests/test_r1234_moneyprinterturbo_import.py::test_install_plan_uses_private_environment_and_data_root
      - tests/test_r1234_moneyprinterturbo_import.py::test_no_core_dependency_or_secret_configuration
    R1234-IMPORT:
      - tests/test_r1234_moneyprinterturbo_import.py::test_import_copies_mp4_and_creates_single_clip_project
      - tests/test_r1234_moneyprinterturbo_import.py::test_import_preserves_audio_and_accepts_explicit_silent_media
      - tests/test_r1234_moneyprinterturbo_import.py::test_import_rejects_traversal_nested_intermediate_non_mp4_and_invalid_id
      - tests/test_r1234_moneyprinterturbo_import.py::test_import_refuses_existing_project_and_hash_collision
    R1234-BOUNDARIES:
      - tests/test_r1234_moneyprinterturbo_import.py::test_import_does_not_launch_mpt_or_render_or_publish
      - tests/test_r1234_moneyprinterturbo_import.py::test_release_import_contract_does_not_assume_scene_clips
      - tests/test_r1234_moneyprinterturbo_import.py::test_probe_failure_rolls_back_new_asset_without_partial_project
    R1234-EDITOR-INTEGRATION:
      - tests/test_r1234_moneyprinterturbo_import.py::test_mcp_import_creates_project_from_configured_local_root
      - tests/test_r1234_moneyprinterturbo_import.py::test_mcp_exposes_only_local_import_not_generation
      - tests/test_r1234_moneyprinterturbo_import.py::test_mpt_mcp_tool_is_not_exposed_without_explicit_output_root
      - tests/test_r1234_moneyprinterturbo_import.py::test_mpt_home_configures_only_its_tasks_directory
      - tests/test_r1234_moneyprinterturbo_import.py::test_toolchain_registers_only_confined_asset_import
---

# SPEC-935-R1234 — MoneyPrinterTurbo isolado e importação local

## Objetivo

Preparar MoneyPrinterTurbo na versão `1.3.10` em ambiente Python privado e
integrar apenas a importação de um MP4 já produzido localmente para um projeto
do editor do Core. O Core continua dono da timeline, do plano, da aprovação e do
render subsequente.

## Proveniência e fronteira de instalação

| Item | Referência fixada | Tratamento |
|---|---|---|
| Repositório | `harry0703/MoneyPrinterTurbo`, release `v1.3.10`, commit `8b0206be2c7977e3bc3cf25ff99a2adc3c9c65f9` | Código MIT; não editar nem importar módulos do terceiro no processo do Core. |
| Distribuição oficial | PyPI `mpt==1.3.10`, wheel `mpt-1.3.10-py3-none-any.whl`, SHA-256 `5a2a9ca8b3e43502f32c8e27ae1a8c7c13ff75e6adad6be45a3e051b088f8c9f`, Python `>=3.11` | Instalar somente no venv privado `~/.local/share/marceloclaro/tools/mpt/1.3.10/venv`; confirmar a correspondência de versão/hash antes de registrar instalado. |
| Dados/saídas | `$MPT_HOME/storage/tasks`, sob diretório dedicado `~/.local/share/marceloclaro/data/mpt/1.3.10` | Não criar `config.toml`, não ler/gravar chaves, não iniciar a aplicação. O importador recebe somente caminho relativo a um diretório de exportação explicitamente configurado. |

O pacote fixa `starlette==1.3.1`, enquanto o ambiente Core usa outra versão de
Starlette. Dependências MPT não podem ser instaladas no `.venv` do Core nem
acrescentadas a `requirements.txt`.

## Contrato funcional

1. O importador aceita apenas a forma relativa `{task_id}/final-{n}.mp4`
   (`n` inteiro positivo) sob a raiz `$MPT_HOME/storage/tasks` configurada;
   caminho absoluto, níveis extras, `..`, symlink, path escape, arquivo ausente
   e projeto inválido falham de modo fechado. A forma deriva dos caminhos de
   download `.../{task_id}/final-1.mp4` documentados pela release.
2. O importador copia o asset para uma pasta própria sob
   `EDITOR_PROJECT_ROOT`, verifica a integridade SHA-256, sonda a mídia e grava
   um novo projeto sem sobrescrever projeto existente. A origem não é movida,
   apagada nem modificada.
3. O projeto recém-criado contém um único clipe de vídeo começando no frame zero
   e, se a fonte tiver áudio, clipe de áudio alinhado. Vídeo silencioso exige
   consentimento explícito via `allow_silent=true`.
4. A superfície MCP não chama a CLI/API/WebUI MPT, não executa geração, não
   renderiza, não publica e não pede nem manipula credenciais.
5. A release não fornece o campo `scene_clips` observado em `main` posterior;
   esta integração importa somente o MP4 final e não inventa timeline por cena.
6. O status/toolchain distingue instalação isolada e importação de mídia de
   geração/execução do app. Nenhum status `executed`/`rendered` é inferido da
   instalação.

## Critérios de aceitação

1. Manifesto e instalador identificam release, commit e hash do wheel; instalação
   ocorre apenas no ambiente privado e `pip check` é limitado a esse ambiente.
2. Nenhuma dependência é adicionada ao Core, nenhuma chave/configuração MPT é
   criada e nenhuma interface de geração ou publicação é exposta pelo MCP.
3. Testes RED→GREEN exercitam importação bem-sucedida, áudio/silêncio, hash,
   path traversal, symlink, extensão não permitida, projeto repetido e
   bloqueios de escopo sem executar o binário `mpt` ou FFmpeg real.
4. O teste do importador e da ferramenta MCP verifica que o projeto do Core
   contém o clipe em timeline; apenas copiar o arquivo ou abrir projeto vazio
   não satisfaz o contrato. A ferramenta só aparece quando `MPT_OUTPUT_ROOT`
   (ou parâmetro de inicialização equivalente) aponta para diretório local
   existente e não symlink, por `MPT_OUTPUT_ROOT`, `MPT_HOME/storage/tasks` ou
   parâmetro de inicialização explícito.
5. Evidência pós-instalação limita-se a `pip show`/`pip check` no venv isolado,
   SHA-256 do pacote instalado e diagnóstico do Core. Não executar MPT.

## Critérios de aceitação executáveis

- `R1234-PROVENANCE` Manifesto e installer plan fixam PyPI, release, commit, hash do wheel e Python mínimo.
- `R1234-ISOLATION` O plano aponta apenas para venv/data root privados, sem modificar dependências do Core, configurar credenciais ou criar `config.toml`.
- `R1234-IMPORT` O importador copia um `task_id/final-N.mp4` local, verifica hash, sonda a mídia e cria projeto não sobrescrevível com clipe no frame zero.
- `R1234-BOUNDARIES` Path traversal, symlink, arquivo não-MP4, ID inválido, silêncio não consentido, colisão e escopo de geração/render/publicação são bloqueados ou explicitamente falsos.
- `R1234-EDITOR-INTEGRATION` Ferramenta MCP confinada e catálogo do toolchain expõem somente importação quando a raiz local estiver configurada.

## Fora de escopo

- Executar WebUI, API, CLI, agente ou qualquer gerador do MoneyPrinterTurbo.
- Gerar, editar, renderizar ou publicar vídeos; baixar modelos, mídias ou vozes.
- Configurar, importar ou acessar chaves, contas, OAuth, cookies, tokens ou
  arquivos `config.toml`.
- Importar cenas individuais/clipes de produção não disponibilizados na release
  `v1.3.10`; integrar `main` ou atualizar a versão.
- Alterar a timeline de um projeto já existente, preservar alpha, ou aprovar
  qualidade estética/editorial do vídeo.
- Alterar dependências do ambiente compartilhado do Core.

## Evidência observada (2026-11-20)

- RED observado antes do módulo: a suíte focal falhou com `16 failed` porque
  `integrations.moneyprinterturbo` ainda não existia. Esse resultado foi uma
  execução pytest manual, não um recibo RED do `TDDHistory`; o histórico formal
  não deve ser alegado retrospectivamente.
- GREEN focal: `./.venv/bin/python -m pytest
  tests/test_r1234_moneyprinterturbo_import.py -q` → `16 passed` (um aviso de
  Pydantic/FastMCP de dependência, sem falha).
- Execução dos alvos do contrato pelo `TDDRunner.run_spec_test` → `15/15
  nodeid(s)` aprovados; `SpecVerifier` → `5/5` critérios aprovados em modo
  `criteria_only` (`require_red_history=false`). Isso não valida nem substitui
  o pareamento formal RED→GREEN do `TDDHistory`.
- Regressão do editor: cinco suítes R1042/R1043/R1046 → `66 passed` (o mesmo
  aviso de dependência).
- Instalação: wheel obtido do PyPI e SHA-256 confrontado com o manifesto, sem
  divergência. `mpt==1.3.10` instalado somente em
  `~/.local/share/marceloclaro/tools/mpt/1.3.10/venv` com pacotes binários;
  `pip check` → `No broken requirements found`; `pip show mpt` → `1.3.10`.
  Instalação não executou o CLI/WebUI/API e não criou `config.toml` nem chaves.
- Doctor pelo `.venv` do Core → `overall=degraded`, 16 checks pass, 6 warnings,
  0 failed; avisos são capacidades/provedores opcionais ausentes. A execução
  estrutural confirmou specs, registro de evolução e memória disponíveis.
- `git diff --check` sem erro de whitespace. Não houve render, geração,
  publicação, alteração de dependências do `.venv` Core nem mudança em dados
  do usuário.
- O gate estrito de RED→GREEN do `TDDHistory` e revisão independente não têm
  recibo nesta sessão; os resultados acima comprovam testes locais executados,
  não validação externa nem conclusão desse gate estrito.
