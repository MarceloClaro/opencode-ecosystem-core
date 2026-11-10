# SPEC-935-R1137 — Auditoria local de compilação e layout

**Status:** implementação local, sem hardware
**Depende de:** R1123, R1124, R1133
**Fonte de comportamento:** `gjq_client` instalado (sampler/submit_payload)

## 1. Achados do SDK

- `gjq_runtime/sampler.py` envia `qasm2.dumps(circuit)` ao serviço.
- `build_submit_payload` remove `measure-position` para backends não-MPS.
- O serviço compila (`compile=True`) e não devolve o circuito compilado nem o
  layout físico.
- `generate_preset_pass_manager` suporta `initial_layout` e `layout_method`,
  mas o sampler não o usa por padrão.

Consequência: o QASM q106/107 pode ser renumerado para q0/1 e o par físico
final não é auditável apenas pelo log.

## 2. Rota

1. Construir o circuito físico com `qreg` de 108 e gates em 106/107.
2. Pré-transpilar com `initial_layout` explícito e o `Target` do backend.
3. Verificar localmente `final_index_layout`, qubits ativos e QASM.
4. Submeter o QASM compilado com `compile=False` (a ser validado no serviço).

## 3. Requisitos

- **R1.** `build_physical_circuit`, `transpile_with_layout`, `audit_layout`.
- **R2.** `layout_preserved`, `mapping_preserved`, `identity_preserved`.
- **R3.** Detectar troca 106/107 mesmo quando o conjunto ativo é o mesmo.
- **R4.** Nenhum hardware, rede ou credencial.
- **R5.** Não declarar que o servidor respeita `compile=False` sem teste.

## 4. Critérios

- circuito com 108 qubits, 2 clbits, CZ em 106/107;
- layout identidade preserva 106/107;
- layout trocado tem `identity_preserved=False`;
- QASM com `qreg q[108]`;
- testes e relatório.

## 5. Limites

O backend de teste é genérico (linha de 108 qubits), não o Baihua. A submissão
com `compile=False` não foi executada. A auditoria prova o contrato local, não
o comportamento do servidor.
