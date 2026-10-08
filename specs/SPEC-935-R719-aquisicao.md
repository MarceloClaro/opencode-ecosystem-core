# SPEC-935-R719 — Aquisição auditada dos clones piloto sem executar

**Status:** `em implementação`
**Ciclo:** R719→R720
**Data:** 2026-10-07
**Base:** R718 (0 prontas: 3 clones ausentes + override sympy a religar)

## 1. Problema

Readiness aponta clones ausentes, mas não existe rotina auditada para adquiri-los
sem executar código: `git clone` direto não registra consentimento, HEAD, hash
nem decisão que o autorizou. Aquisição sem trilha repete o risco que R711/R712
barraram.

## 2. Objetivo

Módulo `integrations/polymath_aquisicao.py` com `clonar_auditado(url, base,
consentimento, timeout)` em `--depth 1`, validando allowlist + intenção aprovada
antes de qualquer subprocesso, registrando `HEAD, sha256_HEAD, bytes, quando`
em `aquisicoes.jsonl`, sem build/install/execução. Readiness ganha `overrides`
opcional para suprir licença sympy com evidência R715.

## 3. Critérios de aceitação

- [ ] AC1 — `clonar_auditado` fail-closed sem `consentimento is True`; fora da allowlist ou sem intenção aprovada recusa antes de subprocesso; destino `base/org__repo`; existente íntegro reutilizado sem novo clone.
- [ ] AC2 — Subprocesso confinado a `["git","clone","--depth","1",url,destino]` com timeout; retorno não zero vira `ValueError` auditável; nunca executa `pip/docker/npm` nem hooks.
- [ ] AC3 — `avaliar(..., overrides=None)` no readiness: override com 4 campos supre pendência de licença do pin, mantendo exigência de pin federável ou proposto R715.
- [ ] AC4 — Testes herméticos `tests/test_r719_aquisicao.py` com `subprocess.run` mockado: fora da allowlist sem subprocesso, sem consentimento sem subprocesso, sem intenção aprovada sem subprocesso, clone ok com HEAD+hash, overrides suprem licença.
- [ ] AC5 — Anti-execução: grep proíbe `pip install, docker run, npm install, Popen, os.system` no módulo de aquisição.
- [ ] AC6 — Anti-overclaim: aquisição registra `adquirido, não verificado`; readiness mantém `candidato_a_inspecao`.

## 4. Fora de escopo (declarado)

- Build, install, testes do lab, federação, decisão das 12 restantes.

## 5. Verificação

- `pytest tests/test_r719_aquisicao.py tests/test_r718_readiness.py -q` verde.
- Aquisição viva dos 3 piloto em `/tmp/polymath_clones` com tolerância; re-readiness com overrides R715.
- `doctor` sem novos falhos.
