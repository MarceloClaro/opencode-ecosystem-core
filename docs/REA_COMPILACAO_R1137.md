# REA aplicado à compilação GJQ — R1137

**Status:** inspeção local; nenhum hardware executado.

## 1. REA disponível

- REA 6.8.0 instalado; **229 ferramentas**, 18 camadas (16 prontas).
- `status`, `catalog`, `session` e `layers` responderam.
- Ghidra 12.1.4 + JDK 21 disponíveis para binário nativo.

## 2. Tentativa nativa

Alvo: `gjq_client/client/runtime.abi3.so` (ELF x86-64, sha256
`63ac97333a56701fe29a83ed3600c7ab4f7ccb96807b35d58cfd8a3862859a1a`).

- `analyze_binary` com `procedure="main"` falhou por entrada inválida.
- Com `procedure="PyInit_runtime"`, o `analyze_function` executou, mas o REA
  não entregou Evidence nativa identificada do provider Ghidra.
- **Limite:** não houve extração nativa utilizável; não inferir comportamento
  do `.so` a partir dessa tentativa.

## 3. Achados por leitura do SDK instalado

O código Python é a evidência primária; o REA não o substitui.

- `gjq_runtime/sampler.py`: `qasm2=dumps(circuit)` — o QASM **original** é
  enviado.
- `gjq_runtime/submit_payload.py`: `measure-position` é removido do payload
  para backends não-MPS; só MPS o reconstrói.
- `build_submit_payload` recebe `instructions` e `options`; o serviço compila
  com `compile=True` e **não devolve** circuito compilado nem layout físico.
- `utils/generate_preset_pass_manager.py` suporta `initial_layout` e
  `layout_method`, mas o sampler não o usa por padrão.

**Consequência:** a renomeação q106/107 → q0/1 observada no log pode ser
renumeração lógica do serviço; o par físico final não é auditável pelo log.

## 4. Rota local implementada

`quantum_mitigation/compilation_audit.py`:

1. circuito de 108 qubits com gates em 106/107;
2. pré-transpilação com `initial_layout` explícito e Target do backend;
3. verificação de `final_index_layout`, qubits ativos e QASM;
4. detecção de troca 106/107 mesmo quando o conjunto ativo é o mesmo.

Resultados dos testes com backend genérico de 108 qubits:

| Caso | layout_preserved | mapping_preserved | identity_preserved |
|---|---|---|---|
| identidade | true | true | true |
| 106/107 trocados | true | true | **false** |

`qreg q[108]` e apenas 106/107 ativos foram preservados.

## 5. Limites

- O backend de teste é uma linha genérica de 108 qubits, não o Baihua.
- A submissão do QASM compilado com `compile=False` **não foi executada**.
- O servidor pode recompilar/renomear mesmo com `compile=False`; isso precisa
  de um teste controlado e autorização.
- A auditoria prova o contrato local; não prova o layout físico do serviço.

## 6. Próximo passo

1. Repetir `audit_layout` com o `Target` real do Baihua.
2. Submeter um circuito de calibração com `compile=False` e `measure-position`
   explicitamente documentado.
3. Comparar o QASM submetido, o task detail e o resultado; se o serviço não
   devolver o compilado, registrar a limitação e não declarar layout auditado.
