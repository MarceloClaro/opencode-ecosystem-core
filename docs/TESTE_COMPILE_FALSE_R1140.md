# Teste controlado `compile=False` — R1140

**Status:** tentativa única bloqueada antes da submissão.
**Pré-registro:** `harnesses/quantum-error-mitigation/resultados/r1140_compile_false/preregistration.json`
**Execução:** `.../run.json`

## 1. Desenho

- backend **Baihua**;
- par físico **106/107**; `qreg` de 108 qubits;
- **1 job**, **4.096 shots**;
- QASM pré-compilado com `initial_layout` identidade de 108 qubits;
- opção **`compile=False`**;
- regras: task ID, soma dos counts, layout 106/107 e qubits ativos [106,107].

Não é estudo estatístico; um job não prova fidelidade, emaranhamento ou
vantagem quântica.

## 2. Pré-registro

Hash do manifesto: `d84a9efe2cc17c721cc1a9610e27a4c1891f4e9c1506dfb654c77a78b1db0829`.

O manifesto declara `hardware_submission_allowed=False`; a autorização é dada
pelos flags `--confirm --allow-hardware` e por `GJQ_HARDWARE_ENABLED=1`.

## 3. Tentativa

A auditoria de layout foi executada antes da submissão. O serviço respondeu:

```
APIError: [HTTP 200] Failed to fetch machine config for Baihua.
```

O `run.json` registra:

```json
{
  "status": "blocked",
  "stage": "layout_audit",
  "error_type": "APIError",
  "reason": "[HTTP 200] Failed to fetch machine config for Baihua.",
  "executed": false
}
```

**Nenhum task ID foi criado; nenhum job foi submetido.** Não houve retry
automático.

## 4. Interpretação

- A listagem de backends funcionou (Baihua apareceu), mas o `machine config`
  necessário para `target`/layout não foi obtido.
- Sem `Target`, não é possível verificar `initial_layout`/106/107 antes de
  submeter; o gate corretamente bloqueou.
- Não se deve enviar o QASM sem essa auditoria, pois o servidor não devolve o
  layout e a alegação de preservação seria infundada.

## 5. Próximo passo

1. Repetir **uma** vez quando o machine config do Baihua estiver acessível.
2. Se aceito, consultar status/result e auditar a soma dos counts.
3. Se o serviço recompilar/renomear, registrar e não repetir sem nova
   autorização.
4. Não reenviar o job; usar o `task_id`.

## 6. Reprodução

```bash
GJQ_HARDWARE_ENABLED=1 .venv-quantum/bin/python \
  harnesses/quantum-error-mitigation/hardware_compile_false_test.py \
  plan --out /tmp/opencode/r1140
GJQ_HARDWARE_ENABLED=1 .venv-quantum/bin/python \
  harnesses/quantum-error-mitigation/hardware_compile_false_test.py \
  run --out /tmp/opencode/r1140 --confirm --allow-hardware --use-cached-account
```

Testes: `pytest tests/test_r1140_compile_false.py -q`.
