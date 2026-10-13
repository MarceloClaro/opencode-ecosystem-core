---
spec_id: SPEC-935-R864
title: Separar fontes reproduzíveis de estado privado e artefatos locais
component: repository_release
status: implemented
test_file: tests/test_r864_repository_release.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    privacidade:
    - tests/test_r864_repository_release.py::test_estado_privado_fica_fora_do_git
    artefatos:
    - tests/test_r864_repository_release.py::test_outputs_nao_declarados_ficam_fora_do_git
    reproducao:
    - tests/test_r864_repository_release.py::test_fixtures_do_contrato_continuam_versionaveis
    - tests/test_r864_repository_release.py::test_recibos_publicos_linkados_continuam_versionaveis
    - tests/test_r864_repository_release.py::test_whitelist_nao_libera_diretorios_inteiros
---

# R864 — Repositório reproduzível

O commit do Core deve conter código, specs, testes, documentação e assets que
permitam reproduzir a entrega. Perfis pessoais gerados por setup, conteúdo de
alvos inspecionados, memória de execução, capturas do navegador e saídas não
declaradas permanecem locais. A alteração não apaga nem move arquivos.

## Critérios de Aceitação Executáveis

- `privacidade`: Git ignora toda a árvore `.opencode/rea`, o estado do navegador
  e requisições locais do gerenciador de plugins científicos, inclusive arquivos
  JSON que regras anteriores autorizavam genericamente.
- `artefatos`: Git ignora `outputs` por padrão, bem como cópias suplementares de
  exportação em `livro-core/output`; nenhuma exceção genérica por extensão.
- `reproducao`: exceções explícitas preservam somente fixtures R842/R843/R844/R852,
  a reprodução pública R853 e os pequenos recibos vinculados nos relatórios
  R820/R862. O backend, frontend e páginas esperados por R853 permanecem íntegros.
  Uma exceção de diretório permite atravessar o diretório, mas não libera irmãos
  nem arquivos adicionais.

As execuções históricas registram o ambiente de origem e não comprovam prontidão
em outra máquina. Perfis e motores opcionais continuam exigindo setup local.
Os artefatos R853 foram capturados de conteúdo público e destinam-se ao operador
do domínio; a captura não estabelece uma licença de reutilização de terceiros.
Uma alteração de `.gitignore` não remove arquivos que já sejam rastreados.

O contrato cobre higiene e disponibilidade das fixtures; a execução em clone
limpo e a revisão do restante do índice são verificações complementares.
