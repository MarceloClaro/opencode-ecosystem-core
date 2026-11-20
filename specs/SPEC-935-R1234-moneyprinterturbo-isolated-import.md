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
      - tests/test_r1234_moneyprinterturbo_import.py::test_import_rejects_traversal_symlink_non_mp4_and_invalid_project_id
      - tests/test_r1234_moneyprinterturbo_import.py::test_import_refuses_existing_project_and_hash_collision
    R1234-BOUNDARIES:
      - tests/test_r1234_moneyprinterturbo_import.py::test_import_does_not_launch_mpt_or_render_or_publish
      - tests/test_r1234_moneyprinterturbo_import.py::test_release_import_contract_does_not_assume_scene_clips
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

1. O importador aceita apenas arquivo regular `.mp4` sob a raiz local MPT
   configurada; caminho absoluto, `..`, symlink, path escape, arquivo ausente e
   projeto inválido falham de modo fechado.
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
4. O teste verifica que o projeto do Core contém o clipe em timeline; apenas
   copiar o arquivo ou abrir projeto vazio não satisfaz o contrato.
5. Evidência pós-instalação limita-se a `pip show`/`pip check` no venv isolado,
   SHA-256 do pacote instalado e diagnóstico do Core. Não executar MPT.

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
