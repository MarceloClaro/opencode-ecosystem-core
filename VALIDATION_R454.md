# Recibo local de validação — SPEC-935-R454

## Escopo

Este recibo registra a migração do gate SDD das specs `SPEC-935-R447` a
`SPEC-935-R453` para o contrato `criterion-runtime-v1`, no qual cada critério
executável é vinculado a um ou mais `pytest nodeids` explícitos. Ele descreve
uma execução **local** e não constitui certificação externa, auditoria
independente nem garantia absoluta.

## Ambiente registrado

| Campo | Valor observado |
|---|---|
| Base Git (`git rev-parse HEAD`) | `067ba78156663daa8c3e9b98d2e75b68d8b85278` |
| Estado do checkout | working tree com mudanças ainda não commitadas; a base Git não identifica sozinha o snapshot integral desta execução. |
| Runtime | Python 3.14.4 |
| Plataforma | Linux 6.18.33.2-microsoft-standard-WSL2 |

## Evidência granular observada

As specs abaixo foram revalidadas com `TDDRunner.run_spec_test()` emitindo
registros selados por `criterion_id → nodeid`, e `SpecVerifier.verify()`
aceitando a promoção apenas quando **todos** os nodeids exigidos passaram sem
skip, xfail ou replay do mesmo envelope.

| Spec | Critérios | Nodeids aprovados | Duração observada |
|---|---:|---:|---:|
| `SPEC-935-R447` | 6/6 | 6/6 | 9,48 s |
| `SPEC-935-R448` | 18/18 | 34/34 | 220,99 s |
| `SPEC-935-R449` | 8/8 | 9/9 | 13,45 s |
| `SPEC-935-R450` | 7/7 | 10/10 | 32,06 s |
| `SPEC-935-R451` | 5/5 | 8/8 | 20,16 s |
| `SPEC-935-R452` | 6/6 | 11/11 | 37,26 s |
| `SPEC-935-R453` | 9/9 | 20/20 | 63,11 s |
| `SPEC-935-R454` | 9/9 | 9/9 | 16,43 s |

## Comandos executados

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_r212_doctor_litert.py \
  tests/test_r221_self_correction_engine.py \
  tests/test_r425_pacote_submissao.py \
  tests/test_r435_harness_universal.py \
  tests/test_r445_alphageometry_autoformalization.py \
  tests/test_mirofish_gametheory_publishing.py \
  tests/test_r447_auditoria_tecnica_ecossistema.py \
  tests/test_r448_hardening.py \
  tests/test_r448_installer_security.py \
  tests/test_r448_formal_mutation.py \
  tests/test_r448_sdd_contracts.py \
  tests/test_r448_documentation_reconciliation.py \
  tests/test_r449_readme_release.py \
  tests/test_r450_security_boundaries.py \
  tests/test_r451_formal_resource_soundness.py \
  tests/test_r452_domain_soundness_budgets.py \
  tests/test_r453_precommit_security_closure.py \
  tests/test_r454_criterion_runtime_evidence.py

python3 - <<'PY'
from sdd.spec_engine import SpecRegistry, SpecVerifier
from sdd.tdd_runner import TDDRunner
registry = SpecRegistry()
verifier = SpecVerifier(registry)
runner = TDDRunner()
for sid in [f"SPEC-935-R{n}" for n in range(447, 455)]:
    spec = registry.get(sid)
    evidence = runner.run_spec_test(spec)
    result = verifier.verify(sid, {"delivery": "presente"}, trusted_test_evidence=evidence)
    print(sid, result["verified"], result["passed_count"], result["total_count"], evidence.summary)
PY
```

## Relação com os recibos anteriores

- `VALIDATION_R448.md`, `VALIDATION_R452.md` e `VALIDATION_R453.md` continuam
  registrando os gates locais observados nas respectivas rodadas.
- A partir de `SPEC-935-R454`, a sustentação **granular** das contagens de
  critérios passou a depender dos mapas `criterion_id -> nodeid(s)` nas specs e
  da revalidação local acima, e não apenas de uma suíte global verde.

## Limites conhecidos

- a associação explícita `critério → nodeid` melhora a auditabilidade, mas não
  substitui revisão humana da suficiência semântica do teste;
- a prova continua local ao mesmo processo Python; ela bloqueia autoatestado por
  payload do agente, não constitui sandbox contra código arbitrário;
- este recibo não transforma resultados locais em validação externa.
