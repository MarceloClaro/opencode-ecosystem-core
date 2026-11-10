# SPEC-935-R1140 — Teste controlado de compile=False

**Status:** pré-registro executado; tentativa bloqueada por machine config
**Data:** 2026-11-10
**Depende de:** R1137, R1139

## 1. Objetivo

Testar uma única submissão com `compile=False`, QASM pré-compilado e
`initial_layout` identidade em 106/107, sem transformar um job em estudo
estatístico.

## 2. Pré-registro

- backend Baihua, par 106/107, 108 qubits, 4.096 shots, 1 job;
- `compile=False`, `transpile=True`, `initial_layout=identity_108`;
- regras: task_id, soma 4.096, layout 106/107, qubits ativos [106,107], sem
  alegar fidelidade.

## 3. Tentativa

`provider.compilation_audit` falhou antes da submissão:

```
APIError: [HTTP 200] Failed to fetch machine config for Baihua.
```

Nenhum `task_id` foi criado; nenhum job foi submetido. O `run.json` registra
`status=blocked`, `stage=layout_audit`, `executed=false`.

## 4. Requisitos

- **R1.** Pré-registro determinístico com hash.
- **R2.** Auditoria de layout antes da submissão.
- **R3.** Um job, sem retry automático.
- **R4.** Bloquear se layout não for identidade 106/107.
- **R5.** Registrar erro de rede/servidor sem inventar task ID.
- **R6.** Testes com mocks; nenhum hardware nos testes.

## 5. Critérios

- manifesto com 1 job, 4.096 shots e compile=False;
- `run` sem confirm/allow/hardware-enabled bloqueia;
- caminho mockado grava `run.json`/`layout_audit.json`;
- tentativa real grava blocked com APIError;
- nenhum task ID fictício; nenhuma taxa medida.

## 6. Próximo passo

Quando `machine config` do Baihua estiver acessível, repetir **uma** vez o
run; se aceito, consultar status/result e auditar counts. Se o serviço
recompilar/renomear, registrar e não repetir sem nova autorização.
