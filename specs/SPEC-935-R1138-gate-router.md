# SPEC-935-R1138 — Roteador de gates e evidência

**Status:** implementação local, sem hardware
**Depende de:** R1135

## 1. Objetivo

Quando um gate bloqueia, o harness/agente deve consultar a rota e a evidência
necessária, em vez de apenas reportar “bloqueado”.

## 2. Comando

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/gate_router.py \
  --gate pec_2q
```

Saída: status fail-closed, rota, campos de evidência e fontes. Com
`--evidence evidencia.json`, avalia a política.

## 3. Rotas

| Gate | Rota | Evidência |
|---|---|---|
| PEC 2q | GSPN/MLCB + gauge | GSPN validado, held-out, overhead |
| ZNE | LRE | configurações, resíduo, held-out |
| Layout | pareado randomizado | n, randomização, r1, drift, efeito |
| Cortes | gauge GSPN+MLCB | autoconsistência e MLCB |

## 4. Requisitos

- **R1.** `route(gate, evidence)` e CLI.
- **R2.** Fail-closed sem evidência.
- **R3.** Fontes/DOI e campos obrigatórios.
- **R4.** Nenhum hardware, rede ou submissão.
- **R5.** Não declarar gate aprovado sem evidência.

## 5. Critérios

- rota PEC contém GSPN e campos;
- evidência sintética aprova PEC;
- CLI grava arquivo novo e recusa sobrescrita;
- gate inválido falha;
- testes e documentação.
