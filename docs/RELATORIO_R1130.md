# R1130 — Twirl/frame, ruído das correções e pré-registro

**Status:** simulação local, sem hardware.
**Depende de:** R1129.
**Artefato:** `harnesses/quantum-error-mitigation/resultados/r1130_twirl_noise/`.

## Twirl/frame

Cada CZ pode ser substituído por `P · CZ · P'`, com `P' = CZ P CZ`. O circuito
ideal permanece equivalente e os frames ficam registrados em
`cycle_body_framed`. O twirl é determinístico por seed e não alterou a
recuperação exata nos testes com taxas uniformes e não uniformes.

Isso é twirl de Pauli em nível de CZ; não é uma implementação completa de RC
com pós-processamento de frames em hardware. O ruído das correções de 1 qubit
não é twirlado.

## Ruído das correções

`correction_rate` aplica depolarização 1q após cada correção marcada.

| Twirl | Taxa | Ajustes | Erro absoluto máximo |
|---|---:|---:|---:|
| não | 0,000 | 13/13 | 3,33×10⁻¹⁶ |
| não | 0,001 | 13/13 | 2,58×10⁻³ |
| não | 0,005 | 13/13 | 1,29×10⁻² |
| não | 0,010 | 13/13 | 2,57×10⁻² |
| sim | 0,000 | 13/13 | 3,33×10⁻¹⁶ |
| sim | 0,001 | 13/13 | 2,58×10⁻³ |
| sim | 0,005 | 13/13 | 1,29×10⁻² |
| sim | 0,010 | 13/13 | 2,57×10⁻² |

**13/13 ajustes não significa 13/13 precisão.** O erro cresce com a taxa de
correção; a 0,5% já é ~1,3×10⁻², grande para PEC. O modelo é depolarização 1q
simulada, não o ruído real do Baihua.

## Pré-registro

- 13 funções × 5 profundidades × 5 seeds de twirl = **325 jobs**.
- 4.096 shots/job; **1.331.200 shots** no orçamento.
- Ruído de correção declarado: 0,002 (depolarização 1q).
- Hash: `4a74762ecd5f7a6a…` (completo no JSON).
- `hardware_submission_allowed=False`, `analysis_allowed=False`.
- Regras de decisão e limites no JSON; validação rejeita alteração.

## Limites

- Twirl e ruído simulados; nada executado no Baihua.
- As 2 funções de corte continuam não medidas.
- PEC 2q, ZNE e comparação de layouts continuam bloqueados.
- O desenho de 13 funções ainda não tem twirl/frame em hardware nem
  compilação auditada.

## Reprodução

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py \
  interleaved-noise --out /tmp/opencode/noise.json
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py \
  preregister --out /tmp/opencode/prereg.json
```

Testes: `tests/test_r1130_twirl_noise_prereg.py`.
