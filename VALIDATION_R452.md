# Recibo de validação local — SPEC-935-R450 a R452

## Escopo

Este recibo registra gates locais executados em 2026-08-24 para as specs
`SPEC-935-R450`, `SPEC-935-R451` e `SPEC-935-R452`. Ele registra limites de
entrada do verificador formal e hardening de instaladores já descritos nas
specs; não é release, certificação externa, auditoria independente nem E2E
Windows elevado.

## Ambiente registrado

| Campo | Valor observado |
|---|---|
| Base Git (`git rev-parse HEAD`) | `067ba78156663daa8c3e9b98d2e75b68d8b85278` |
| Estado do checkout | working tree com mudanças ainda não commitadas; a base Git não identifica o snapshot integral dos gates. |
| Runtime | Python 3.14.4 |
| Plataforma | Linux 6.18.33.2-microsoft-standard-WSL2 |
| Doctor | 18 checks aprovados e 1 aviso para a CLI opcional `scihub-cli`. |

## Evidência SDD emitida pelo runtime

O `TDDRunner` executou `tests` para cada spec e o `SpecVerifier` recebeu a
evidência selada pelo runtime. Cada execução local observou:

```text
3512 passed, 70 skipped, 1 warning, 4 subtests passed
```

| Spec | Critérios | Duração observada |
|---|---:|---:|
| `SPEC-935-R450` | 7/7 | 428,79 s |
| `SPEC-935-R451` | 5/5 | 424,44 s |
| `SPEC-935-R452` | 6/6 | 427,11 s |

Os resultados descrevem o checkout e o ambiente usados na execução. Uma nova
revisão deve executar seus próprios gates antes de promover uma alteração.

Em `SPEC-935-R454`, as specs `SPEC-935-R450`, `SPEC-935-R451` e
`SPEC-935-R452` foram revalidadas em modo `criterion-runtime-v1`, com **10/10**,
**8/8** e **11/11 nodeids** aprovados para sustentar, respectivamente, as
contagens **7/7**, **5/5** e **6/6** de critérios. Ver `VALIDATION_R454.md`.

## Comandos e revisões complementares

```bash
python3 -m marceloclaro.cli doctor
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_r452_domain_soundness_budgets.py \
  tests/test_r451_formal_resource_soundness.py \
  tests/test_r450_security_boundaries.py \
  tests/test_r449_readme_release.py \
  tests/test_r448_hardening.py \
  tests/test_r448_installer_security.py \
  tests/test_r448_formal_mutation.py \
  tests/test_r442_deepmind_superhuman_reasoning.py
.venv/bin/python -m ruff check --select E4,E7,E9,F \
  integrations/deepmind/formal_verifier.py \
  tests/test_r452_domain_soundness_budgets.py
```

O recorte focado acima passou com **60 passed**. A revisão estática interna
posterior da R452 não encontrou bloqueador concreto; ela não substitui uma
auditoria de segurança externa.

## Limites conhecidos

- Z3 recebe timeout local, mas isso não constitui sandbox completo de CPU ou
  memória para dependências simbólicas.
- O fragmento algébrico é deliberadamente restrito; recusa domínio parcial e
  sintaxe fora da gramática em vez de provar universalidade.
- PowerShell e WSL foram validados por testes locais e parsing quando aplicável;
  não houve E2E Windows elevado.
