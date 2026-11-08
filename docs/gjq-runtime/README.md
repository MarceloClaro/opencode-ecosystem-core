# Resultados GJQ — proveniência

Registros brutos de execuções feitas pelo MCP `gjq-runtime` em 2026-11-08.

| Arquivo | Experimento | Backend | Task ID |
|---|---|---|---|
| `bell-2026-11-08.json` | Bell state | `FAS-GPU` | `5db11f42-fcdc-4b80-a5c7-cabe0432ef90` |
| `chsh-2026-11-08.json` | CHSH, 4 circuitos | `FAS-GPU` | ver `cases` |

## Esquema

- `schema_version`, `kind`, `generated_at`;
- `backend`, `hardware`, `shots`;
- `task_id`, `status`, `platform_submit_time`;
- `qasm_sha256`;
- `counts`, `total`, `probabilities`;
- `E`, `E_se` por caso do CHSH;
- `S`, `S_se`, `S_ideal`, `classical_bound`;
- `audit` e `limits`.

## Limites

- São resultados de simulador da plataforma, não de hardware.
- Uma execução não prova emaranhamento físico, fidelidade ou vantagem quântica.
- Nenhuma API key é gravada nestes arquivos.
- O task ID é a prova de submissão; o resultado só vale com `status = DONE`.

## Reprodução

```text
gjq_sample(qasm=..., backend_name="FAS-GPU", shots=1024, confirm=True)
gjq_task_status(task_id="...")
gjq_task_result(task_id="...")
gjq_audit_counts(counts={...}, shots=1024)
```

Para o CHSH, repita o sampling com as quatro bases e calcule
`E = (N00 + N11 - N01 - N10) / shots` e
`S = E00 + E01 + E10 - E11`.
