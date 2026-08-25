# Recibo de validação local — SPEC-935-R448

## Escopo

Este documento registra uma execução local de gates feita durante o hardening
R448 em 2026-08-23. Ele não é uma release, um artefato de CI remoto nem uma
certificação externa. O resultado aplica-se ao checkout e ao ambiente que
executaram os comandos abaixo; uma nova revisão deve executar seus próprios
gates.

## Ambiente registrado

| Campo | Valor observado |
|---|---|
| Base Git (`git rev-parse HEAD`) | `067ba78156663daa8c3e9b98d2e75b68d8b85278` |
| Estado do checkout | working tree com as mudanças R448 ainda não commitadas; não interpretar a base Git como snapshot completo da execução. |
| Runtime | Python 3.14.4 |
| Plataforma | Linux 6.18.33.2-microsoft-standard-WSL2 |
| Dependências | `.venv/bin/python -m pip check` retornou `No broken requirements found.` |

## Evidência observada

```text
3488 passed, 70 skipped, 1 warning, 4 subtests passed
```

O gate SDD correspondente registrou `SPEC-935-R448` com 18/18 critérios e
evidência emitida pelo runtime para a suíte vinculada `tests`.

Em `SPEC-935-R454`, a mesma spec foi revalidada no modo
`criterion-runtime-v1`, com **34/34 nodeids** explicitamente vinculados aos 18
critérios. A sustentação granular atual está registrada em
`VALIDATION_R454.md`.

## Comandos executados

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/ -q --tb=short --timeout=120 -p no:cacheprovider
.venv/bin/python -m ruff check --select E4,E7,E9,F \
  sdd/spec_engine.py sdd/tdd_runner.py integrations/deepmind/formal_verifier.py \
  integrations/deepmind/formal_safety_predicates.py marceloclaro/orchestrator.py
.venv/bin/python -m pip check
bash -n installer/common/install_clis.sh
bash -n installer/linux/install.sh
bash -n installer/macos/install.sh
bash -n installer/windows/provision.sh
pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw 'installer/windows/Install-OpenCodeEcosystem.ps1')) | Out-Null; [scriptblock]::Create((Get-Content -Raw 'installer/windows/Create-Shortcuts.ps1')) | Out-Null"
.venv/bin/mutmut run --max-children 4
.venv/bin/mutmut results
```

O gate de mutação focado em `solver_result_proves_implication` eliminou a
mutação que inverteria a decisão `unsat`/`sat`: **1/1** mutação foi eliminada
e `mutmut results` não listou sobreviventes. Esse recorte não representa
cobertura total do verificador formal. O comando PowerShell acima apenas
analisa sintaxe; ele não substitui E2E Windows elevado.

## Limites conhecidos

- houve um aviso de depreciação do Pillow durante a suíte;
- o `doctor` tinha um aviso de CLI externa opcional ausente (`scihub-cli`);
- scripts PowerShell foram analisados sintaticamente, sem E2E Windows elevado;
- lint completo do repositório possui achados legados fora da superfície crítica
  da CI.
