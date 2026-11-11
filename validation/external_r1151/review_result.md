# Resultado da verificação independente — R1151

**Natureza:** verificação automatizada de claims, não peer review.
**Peer review:** não. **Clínica:** não. **Hardware:** não.

| Claim | Veredito | Evidência |
|---|---|---|
| `formal_complex` | **supported** | `{"ok": true, "statuses": {"interference": "kernel_checked", "relative_phase_not_one": "kernel_checked"}, "certificate_sha256": "5bdad31fe568f8141b221ff4db4df2bbf50bad7f4da4f08ba687fdc86fb46168", "lean_file_sha256": "8e6c25f873fbd15c4ee4bf4a1faa57c81f933fe8775b4644d6730f0f63fe1f43"}` |
| `formal_correlation` | **supported** | `{"ok": true, "statuses": {"marginals_do_not_determine_joint": "kernel_checked", "joints_differ": "kernel_checked"}, "certificate_sha256": "182cc5f1a86a3f1c87d3259ea95b6e4d51598a9e483d3a191ec1c84fcf6f6273", "lean_file_sha256": "73b9ff8566d8effd48a8456bf9df7f706d6ff207689178cc1c43a51a5e861b92"}` |
| `runtime_adapter` | **supported** | `{"ok": true, "returncode": 0, "tail": ["13 passed in 0.29s"]}` |
| `n_of_1_unified` | **supported** | `{"ok": true, "returncode": 0, "tail": ["2 passed in 0.19s"]}` |
| `catalog_audit` | **supported** | `{"ok": true, "report_sha256": "c497a1b31104a687408e3e77cd694e3ef60c1505224eec8c629f220a29cbbf42", "legacy_baseline_mismatches": 2, "reviewed_near_duplicates": 1}` |
| `classification_pilot` | **insufficient** | `{"reason": "dados sintéticos; nenhuma vantagem quântica demonstrada"}` |
| `clinical_claims` | **insufficient** | `{"reason": "sem participante, ética, hardware ou peer review"}` |

**Overclaims:** nenhum
**Claims insuficientes:** ['classification_pilot', 'clinical_claims']
**Reprodutível:** True

Os executores externos Codex/Antigravity foram tentados, mas o roteador
não atribuiu agente interno elegível; a revisão por subagente também
foi bloqueada por assinatura de modelo. Portanto, a validação humana ou
institucional permanece aberta.

Limites: prova formal não é validação empírica; auditoria textual não é
equivalência funcional; teste local não é peer review.
