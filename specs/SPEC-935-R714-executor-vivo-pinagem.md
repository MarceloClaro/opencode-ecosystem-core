# SPEC-935-R714 — Executor vivo da pinagem polímata com consentimento e token

**Status:** `em implementação`
**Ciclo:** R714→R715
**Data:** 2026-10-07
**Base:** R713 (`integrations/polymath_pinagem.py` com fetcher injetável)

## 1. Problema

O gate hermético R713 valida a lógica com fetcher falso, mas não produz
`labs_pins.json` real. A federação exige HEAD vivo, `pushed_at`, licença e
arquivamento reais dos 21 labs, com tolerância a falha isolada, limite de taxa
GitHub e trilha de quem autorizou, sem clonar ou executar terceiros.

## 2. Objetivo

Módulo `integrations/polymath_pinagem_viva.py` + CLI que executa a rotina viva
somente com `consentimento=true` explícito do operador (`prossiga` qualificado
+ flag), usando `GITHUB_TOKEN` quando presente (60→5000 req/h), `git ls-remote`
para HEAD e API `repos/{org}/{repo}` para metadados, emitindo os mesmos
artefatos R713 para decisão humana.

## 3. Critérios de aceitação

- [ ] AC1 — `fetcher_vivo(org, repo, token=None, timeout=20)` valida `org/repo` contra allowlist antes de qualquer rede; GET API com `User-Agent opencode-polymath` + `Accept vnd.github+json` + `Authorization Bearer` se token; `git ls-remote https://github.com/org/repo HEAD` com timeout; retorna `commit, pushed_at, license, license_ok, archived`; qualquer falha vira exceção tipada sem dado parcial silencioso.
- [ ] AC2 — `executar(destino_dir, consentimento, dias=90, token=None)` fail-closed sem `consentimento is True`; delega a `revalidar_todos/emitir_pins` R713; escreve além `vivo_meta.json` (`consentido_por, token_presente: bool — nunca o segredo, janela, total`);
  falha isolada não aborta.
- [ ] AC3 — CLI `python3 -m integrations.polymath_pinagem_viva --dest DIR --consentimento true [--dias 90]` com `--dry-run` (falso determinístico) e `--fresco-apenas` (lista só federáveis); `--consentimento` ausente ou diferente de `true` aborta com código 2 e mensagem em português.
- [ ] AC4 — Anti-segredo: token nunca em log, manifesto ou stdout; apenas `token_presente: true|false`; `GITHUB_TOKEN` lido de env, nunca de argumento.
- [ ] AC5 — Testes herméticos `tests/test_r714_pinagem_viva.py` com `urllib` e `subprocess` mockados: API+ls-remote ok→federável; 404→bloqueado via exceção tolerada; sem consentimento→ValueError sem rede; token nunca vazado em `vivo_meta.json`; CLI `--dry-run` em tmp sem rede.
- [ ] AC6 — Anti-overclaim: saída mantém `federavel|bloqueado + motivo`, `candidato_a_inspecao`; nenhum `verificado|Qualis|superhumano|aprovado`.

## 4. Fora de escopo (declarado)

- Clone/build/install/testes do lab; avaliação científica; federação automática; cache de longo prazo; proxy de API.

## 5. Verificação

- `pytest tests/test_r714_pinagem_viva.py tests/test_r713_pinagem_federacao.py tests/test_r712_polimata_superficies.py -q` verde.
- `python3 -m integrations.polymath_pinagem_viva --dest /tmp/polymath_vivo --consentimento true --dry-run` em tmp sem rede real.
- Tentativa viva real documentada com tolerância; `doctor` sem novos falhos.
