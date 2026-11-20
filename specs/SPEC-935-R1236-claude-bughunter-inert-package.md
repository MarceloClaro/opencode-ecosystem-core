---
spec_id: SPEC-935-R1236
title: Importar Claude-BugHunter como snapshot completo inerte com Burp MCP desligado
component: external.claude_bughunter_snapshot
status: implemented
test_file: tests/test_r1236_claude_bughunter_package_snapshot.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1236-SNAPSHOT:
      - tests/test_r1236_claude_bughunter_package_snapshot.py::test_manifest_pins_snapshot_commit_and_separates_license_scopes
      - tests/test_r1236_claude_bughunter_package_snapshot.py::test_inventory_hashes_match_the_vendored_snapshot
    R1236-INERT:
      - tests/test_r1236_claude_bughunter_package_snapshot.py::test_package_is_not_registered_executed_or_installed
      - tests/test_r1236_claude_bughunter_package_snapshot.py::test_burp_mcp_and_target_testing_remain_disabled
---

# SPEC-935-R1236 — Claude-BugHunter como pacote inerte

## Objetivo

Atender à autorização explícita do usuário para integrar o pacote Claude-BugHunter
ao Core, vendorizando um snapshot integral e versionado em `external/` como
material de referência inerte. Nenhum skill, comando ou executável será ativado
automaticamente. Burp MCP deve permanecer desabilitado.

## Proveniência

- Repositório: `elementalsouls/Claude-BugHunter`.
- Snapshot-alvo: commit `0e70a021e59d6875004e7a563f8511aca2ba3bc1`, observado
  anteriormente no feed Atom `main`; assinatura e posição atual da branch não
  foram verificadas.
- O README anuncia 83 skills e 15 slash commands. São contagens declaradas pelo
  upstream; a integração deve registrar também contagens medidas no snapshot, sem
  apresentar alegações do README como auditoria independente.
- As declarações upstream observadas são MIT para código e CC BY 4.0 para
  conteúdo documental/skills. Referências a projetos ou skills de terceiros
  retêm licenças próprias. Preservar `LICENSE`, `LICENSE-CONTENT` e `NOTICE`.

## Contrato

1. Baixar somente o arquivo-fonte estático do commit fixado, para área temporária
   aprovada; não clonar histórico Git. Extrair com validação de caminhos e
   rejeitar caminhos absolutos, traversal, links simbólicos e arquivos especiais.
2. Preservar a árvore do snapshot em `external/claude-bughunter-snapshot/`, sem
   alterar o conteúdo upstream. Gravar manifesto em
   `federation/claude-bughunter-package-r1236.json`, contendo hash SHA-256 do
   arquivo baixado, commit, contagens observadas e SHA-256/tamanho de cada
   arquivo extraído.
3. Manter todos os arquivos do snapshot sem bit executável. Eles são dados de
   referência em `external/`, não skills/commands auto-descobertos do OpenCode.
   Não copiar comandos para diretórios ativos do Core nem adicionar executores,
   dependências ou ganchos globais.
4. Não executar bootstrap, scripts, CLI, testes do upstream, instalações ou
   serviços. A inclusão do conteúdo é estática; não é validação de segurança do
   pacote nem endosso de cada técnica descrita.
5. Burp MCP permanece desligado: não incluir sua configuração em `opencode.json`
   ou `.opencode/`, não solicitar credenciais, não iniciar Burp e não realizar
   chamadas MCP. Registrar `mcp_enabled=false` no manifesto.
6. Nenhum alvo está autorizado para avaliação. Não testar ativos externos ou
   públicos; a autorização do usuário cobre somente a integração do pacote.
7. Atualizar a skill local defensiva existente para apontar para o snapshot
   inerte, preservando o gate de autorização e sem instruções operacionais de
   exploração. Os conteúdos upstream permanecem acessíveis apenas por leitura
   explícita e não são promovidos a instruções de execução do Core.
8. Testes Core devem operar offline sobre manifesto e hashes locais; não executar
   código contido no snapshot nem realizar rede.

## Critérios de aceitação executáveis

- `R1236-SNAPSHOT` O manifesto fixa o commit, o hash do arquivo-fonte e a
  proveniência/licença; sua lista de arquivos corresponde integralmente ao
  snapshot, sem symlinks ou executáveis.
- `R1236-INERT` Skills e comandos existem apenas no snapshot de referência; não
  estão registrados/ativados pelo Core, não há execução/instalação, Burp MCP
  permanece falso e testes a alvos permanecem não autorizados.

## Verificação

- RED válido antes de materializar o snapshot e alterar a skill.
- Executar os quatro testes offline, formar par RED/GREEN, validar a entrega com
  SpecVerifier, rodar `git diff --check` e o diagnóstico local do Core.
- O snapshot não certifica qualidade, segurança, atualização, licença de cada
  recurso referenciado nem autorização para testar qualquer ativo.

## Fora de escopo

- Ativar ou disponibilizar para invocação automática as skills e os comandos
  upstream.
- Executar bootstrap, scripts, scanners, CLI, ferramentas ou instruções do
  Claude-BugHunter.
- Habilitar/configurar Burp MCP ou qualquer integração externa.
- Testar alvos, mesmo que mencionados no README upstream ou em programas de
  bug bounty; autorização para integrar não é autorização para testar.
