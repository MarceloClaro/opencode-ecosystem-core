# SPEC-935-R1215 — Instalação isolada e auditável do Wakaru 1.14.0 para REA

## 1. Objetivo

Instalar o Wakaru 1.14.0 exclusivamente como dependência local da REA 6.8.0, em diretório isolado, com versão fixada, fonte oficial, hashes verificados e sem efeitos colaterais em configurações, credenciais, permissões, aplicativos ou código de terceiros não auditado.

## 2. Contexto

A REA 6.8.0 expõe `recover_javascript_sources`, mas exige um executável externo Wakaru `^1.13.0`, verificado com `1.14.0`, via variável de ambiente absoluta `REA_WAKARU_COMMAND`. O provider não instala o Wakaru. Esta spec registra a instalação autorizada pelo operador e o contrato de verificação.

## 3. Decisão de versão e fonte

- Pacote: `wakaru`
- Versão: `1.14.0` (fixada; satisfaz `^1.13.0` e é a versão verificada pela REA 6.8.0)
- Registro npm: `https://registry.npmjs.org/wakaru/-/wakaru-1.14.0.tgz`
- Integridade npm publicada: `sha512-gJ4LJQtkrF7b1oaXMWXqqiThIZl4t3HA+tSbSqHCuqxruljWZKD5tRLvdYhEY3MTFkin5tGFusLr6QByatJqyA==`
- Repositório oficial: `https://github.com/pionxzh/wakaru`
- Revisão verificada pela REA: `8219bf5016a063d7fb215101a8c45d5959ec733f`
- Licença: Apache-2.0
- Site oficial: `https://wakarujs.com`

## 4. Diretório isolado

Todo artefato desta instalação fica em:

`/home/marceloclaro/opencode-ecosystem-core/.opencode/rea/wakaru/1.14.0`

Nenhuma instalação global, nenhuma edição de `package.json` do Core, nenhuma alteração em `~/.codex/config.toml`, `app.asar`, bridge REA, auth, permissões ou configuração persistente de MCP.

## 5. Critérios de aceitação

1. Esta spec existe e é carregada pelo doctor do Core.
2. O tarball oficial é baixado apenas para o diretório isolado.
3. O SHA-256 local do tarball é calculado e registrado no manifesto.
4. A integridade `sha512` publicada pelo npm é registrada e conferida.
5. A instalação usa `--ignore-scripts`; nenhum lifecycle script de terceiro é executado.
6. O `package.json` instalado declara `name = wakaru`, `version = 1.14.0` e `license = Apache-2.0`.
7. Existe um wrapper executável `bin/wakaru` que responde a `--version` com `wakaru 1.14.0`, formato exigido pelo parser da REA.
8. O valor bruto de `--version` do CLI oficial é registrado no manifesto antes de qualquer normalização.
9. `prlimit` está disponível em `/usr/bin/prlimit`.
10. O hash de `C:\Users\marce\.codex\config.toml` é idêntico antes e depois da instalação.
11. `REA_WAKARU_COMMAND` não é gravado em arquivo de config; somente é passado inline em comandos futuros.
12. Testes RED falham antes da instalação e testes GREEN passam depois dela.

## 6. SDD — desenho da implementação

1. Criar `tests/test_r1215_wakaru_isolado.py` com testes de integridade, metadata, banner, prlimit e guardrails.
2. Executar os testes no estado inicial para confirmar RED.
3. Baixar o tarball oficial com `npm pack` usando `npm --cache` isolado.
4. Instalar no diretório isolado com `npm install --ignore-scripts --no-audit --no-fund`.
5. Criar wrapper `bin/wakaru` que preserve o CLI real e normalize apenas o banner para o contrato da REA.
6. Gerar `install-manifest.json` com hashes, comandos, versões e guardrails.
7. Executar testes GREEN.
8. Registrar ciclo de evolução e lição metacognitiva.

## 7. TDD — sequência obrigatória

- RED: `pytest -q tests/test_r1215_wakaru_isolado.py` deve falhar por artefatos ausentes.
- GREEN: após instalação, o mesmo comando deve passar.
- REFACTOR: apenas se necessário, sem alterar contratos.

## 8. Limites e não metas

- Não instalar globalmente.
- Não executar scripts de instalação de terceiros.
- Não modificar bridge REA.
- Não modificar `app.asar` nem qualquer aplicativo.
- Não ler, imprimir ou copiar `runtime.key`.
- Não alterar auth, credenciais, permissões ou MCPs existentes.
- Não declarar que a recuperação de código da REA funcionou até executar `recover_javascript_sources` com sucesso e revisão humana.

## 9. Evidências esperadas

- `install-manifest.json`
- `wakaru-1.14.0.tgz`
- `node_modules/wakaru/package.json`
- `bin/wakaru`
- saída de `wakaru --version`
- saída de `pytest -q tests/test_r1215_wakaru_isolado.py`
- hash antes/depois de `/mnt/c/Users/marce/.codex/config.toml`

## 10. Status

- Autorização do operador: **INSTALAR WAKARU** (explícita nesta sessão).
- Execução: pendente até GREEN.
