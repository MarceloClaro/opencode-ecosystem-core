# SPEC-935-R650 — Integração Kaggle CLI (Kaggle/kaggle-cli)

**Ronda:** R650 (SPEC)
**Status:** em implementação
**Data:** 2026-10-04
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 — Executor externo orquestrável (espelho de R645 colab-cli)

## Objetivo

Tornar o Kaggle CLI (`kaggle`, 2.2.4 instalado) orquestrável pelo Core:
competições, datasets, kernels, models, forums, benchmarks, config, auth e
quota — via passthrough genérico (20+ subcomandos inviabilizam atalhos
exaustivos). Execução externa; nada "verificado" sem validação (R110).

## Fonte de verdade (anti-overclaim)

- `kaggle --help` local (2.2.4): grupos `competitions|datasets|kernels|
  models|files|forums|benchmarks|config|auth|quota` (+ aliases de 1 letra).
- Credencial presente: `~/.kaggle/kaggle.json` (600) + `access_token`;
  `kaggle competitions list --page-size 2` respondeu ao vivo (ARC Prize 2026).
- Auth pertence ao operador; quota/GPU (`quota`, `kernels push`) consome
  recursos da conta.

## Escopo

- `integrations/kaggle_cli.py`: `kaggle_available/version/run_args`,
  `auth_check()` (arquivo de credencial, SEM rede no doctor),
  `doctor_check()`, `install_instructions()`, `main()` —
  `status|run|auth|doctor|install`.
- `agents/catalog/kaggle-cli.md` + `.opencode/skills/kaggle-cli/SKILL.md`.
- `marceloclaro/doctor.py`: `kaggle` em `EXTERNAL_CLIS` + versionamento.
- `integrations/opencode_cli.py`: `/kaggle`.
- `tests/test_r650_kaggle_cli.py` (mocks) + prova ao vivo (lista real).

## Critérios de aceitação

1. `kaggle_version()` semver de `kaggle --version`; `None` se ausente.
2. `kaggle_run_args(args, timeout)` em lista, sem shell; nunca lança;
   timeout → `timeout: True`.
3. `auth_check()` = `{"present": bool, "path": ...}` sem rede.
4. `doctor_check()`: pass/warn (nunca fail); detail cita auth quando ausente.
5. `install_instructions()`: `pip install kaggle` + `kaggle.json` (kaggle.com/settings/account) + `chmod 600`.
6. `main()`: `status|run|auth|doctor|install` + `--help`; exit 2 em misuse.
7. Gate TDD 100% + `opencode.json` com `/kaggle` + ciclo de evolução.
