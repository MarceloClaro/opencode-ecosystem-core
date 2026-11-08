# Apêndice GJQ — resultados explícitos {#apendice-gjq}

<p class="mini">Leia este apêndice depois da lauda do estado de Bell. Ele mostra os números que sustentam a frase “S = 2,871 ± 0,044” e separa o que foi medido do que foi simulado.</p>

## 1. O que foi executado {#gjq-1}

| Item | Valor |
|---|---|
| Plataforma | GJQ / CETC-ICQ (Tiangong) |
| SDK | `gjq-client==0.2.1` |
| Qiskit | 2.3.0 |
| Backend | `FAS-GPU` — simulador GPU, 32 qubits |
| Shots | 1024 por circuito |
| Data | 2026-11-08 |
| Hardware | Não |
| Credencial | apenas `GJQ_API_KEY` no ambiente; não registrada no livro |

O `FAS-GPU` é um simulador. Ele não tem T1, T2, acoplamento físico nem fila de QPU. Por isso, o resultado serve para **verificar o circuito e a leitura dos counts**, não para medir fidelidade de hardware.

## 2. Bell state: o preparo {#gjq-2}

O primeiro teste prepara

```text
|Φ+> = (|00> + |11>) / √2
```

com `H` no qubit 0 e `CNOT(0,1)`, e mede os dois qubits.

| Campo | Valor |
|---|---|
| Task ID | `5db11f42-fcdc-4b80-a5c7-cabe0432ef90` |
| Backend | `FAS-GPU` |
| Shots | 1024 |
| Counts `00` | 507 |
| Counts `11` | 517 |
| Total | 1024 |
| P(00) | 0,495117 |
| P(11) | 0,504883 |
| Auditoria | soma 1024; sem alerta |
| QASM SHA-256 | `ae0cd142574796138ef95bd28378ae0a56b611999e3e31369cdacefe51a7b825` |

**Leitura:** apenas `00` e `11` aparecem, em proporção próxima de 50/50. O Bell é o controle do experimento: se ele não produzisse `00` e `11`, o CHSH não deveria ser interpretado.

## 3. CHSH: as quatro bases {#gjq-3}

O teste usa duas bases para o qubit A e duas para o qubit B:

- `A0 = Z`, medida direta;
- `A1 = X`, obtida com `H` antes da medida;
- `B0 = (Z + X)/√2`, obtida com `Ry(-π/4)`;
- `B1 = (Z − X)/√2`, obtida com `Ry(+π/4)`.

Cada circuito começa pelo Bell state. A rotação de base é aplicada antes da medida.

| Caso | A | B | N00 | N01 | N10 | N11 | E |
|---|---|---:|---:|---:|---:|---:|
| A0B0 | Z | B0 | 441 | 72 | 77 | 434 | +0,708984 |
| A0B1 | Z | B1 | 435 | 83 | 69 | 437 | +0,703125 |
| A1B0 | X | B0 | 440 | 60 | 71 | 453 | +0,744141 |
| A1B1 | X | B1 | 68 | 428 | 450 | 78 | −0,714844 |

**Task IDs — prova de submissão:**

| Caso | Task ID |
|---|---|
| A0B0 | `8651f95c-dba8-474b-a5e2-ad3b913c9472` |
| A0B1 | `b2bc4f8a-a1da-4185-acd4-de9cd8ea40db` |
| A1B0 | `950c9a34-cbc0-47f0-b22b-fdd4da84f8a0` |
| A1B1 | `77da2f60-0bd0-4a43-a341-f2d564f0c31d` |

Cada linha soma 1024. O correlacionador é

```text
E = (N00 + N11 − N01 − N10) / N
```

e o parâmetro CHSH é

```text
S = E00 + E01 + E10 − E11
```

Conta com os valores da tabela:

```text
E00 = (441 + 434 − 72 − 77) / 1024 = +0,708984
E01 = (435 + 437 − 83 − 69) / 1024 = +0,703125
E10 = (440 + 453 − 60 − 71) / 1024 = +0,744141
E11 = (68 + 78 − 428 − 450) / 1024 = −0,714844

S = 0,708984 + 0,703125 + 0,744141 − (−0,714844)
S = 2,871094
```

| Grandeza | Valor |
|---|---:|
| `S` | **2,871094** |
| Erro padrão de `S` | **0,043506** |
| Ideal quântico `2√2` | 2,828427 |
| Limite clássico | 2,000000 |
| `S − 2` | 0,871094 |
| `S − 2` em erros padrão | ≈ 20,0 |
| `S − 2√2` | 0,042667 |
| `S − 2√2` em erros padrão | ≈ 0,98 |
| Excede Tsirelson? | Não; consistente com `2√2` dentro de ~1 SE |

## 4. Hardware e simulador {#gjq-4}

O mesmo CHSH foi executado antes no `Guoji08` (hardware supercondutor, 20 qubits), com 1024 shots por circuito. O resultado foi `S = 2,383`, também acima de 2, mas abaixo de `2√2`.

| Backend | Tipo | S | Leitura |
|---|---|---:|---|
| `Guoji08` | hardware supercondutor | 2,383 | desvia do ideal por ruído, calibração e leitura |
| `FAS-GPU` | simulador GPU | 2,871 ± 0,044 | próximo de `2√2`, sem ruído físico de hardware |

A diferença `2,871 − 2,383 = 0,488` não é uma “melhora quântica”: é a diferença entre um simulador e um dispositivo físico. O hardware perde correlação; o simulador preserva o circuito ideal.

## 5. Como ler `S` {#gjq-5}

- `S > 2` afasta o modelo local clássico para as correlações medidas no circuito e nas shots usados.
- `S = 2,871` está a cerca de **20 erros padrão** acima de 2. Isso é forte contra o modelo local clássico.
- `S = 2,871` está a cerca de **1 erro padrão** de `2√2`. Portanto, **não** é uma violação do limite de Tsirelson; é consistente com o valor quântico ideal dentro da flutuação estatística.
- Uma execução de 1024 shots não é prova definitiva. Aumentar shots reduz o erro padrão; repetir em outro backend testa robustez.
- Simulador não prova emaranhamento físico, fidelidade de hardware ou vantagem quântica.

## 6. Reproduza {#gjq-6}

Com o MCP `gjq-runtime`:

```text
gjq_runtime_status()
gjq_list_backends()
gjq_sample(qasm=QASM, backend_name="FAS-GPU", shots=1024, confirm=True)
gjq_task_status(task_id="...")
gjq_task_result(task_id="...")
gjq_audit_counts(counts={...}, shots=1024)
```

Modelo de QASM para `A0B0`:

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
ry(-0.785398) q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
```

Para os outros casos:

| Caso | Acrescente antes das medidas |
|---|---|
| A0B1 | `ry(+0.785398) q[1];` |
| A1B0 | `h q[0];` e `ry(-0.785398) q[1];` |
| A1B1 | `h q[0];` e `ry(+0.785398) q[1];` |

Para hardware, `allow_hardware=True` e aprovação explícita de custo. Para E01–E18, use o MCP `gjq-experiments`, que exige simulação prévia.

## 7. Checklist de estudo {#gjq-7}

1. Qual é o `S` do `Guoji08`? **2,383**.
2. Qual é o `S` do `FAS-GPU`? **2,871 ± 0,044**.
3. Por que o simulador fica mais perto de `2√2`? Porque não tem ruído físico de hardware.
4. O que `S > 2` prova? Que as correlações medidas não são explicadas por um modelo local clássico.
5. O que `S > 2` **não** prova? Emaranhamento físico, fidelidade de hardware ou vantagem quântica.
6. O que muda se você aumentar os shots? O erro padrão cai; o valor central pode oscilar.
7. Onde estão os task IDs? Na tabela da seção 3 e nos JSON de proveniência.

## 8. Proveniência {#gjq-8}

- `docs/gjq-runtime/bell-2026-11-08.json`
- `docs/gjq-runtime/chsh-2026-11-08.json`
- `docs/gjq-runtime/README.md`
- `educacao_quantica_bohm/dados_experimentos/GJQ_CHSH.json`
- `educacao_quantica_bohm/dados_experimentos/GJQ_BELL.json`

Nenhuma API key foi gravada nesses arquivos. O job do `FAS-CPU` (`b3c9a748-5528-4f0a-81cd-81a36a96ef4b`) permaneceu na fila e não entrou nestes resultados.

## 9. Limites {#gjq-9}

- Resultados de simulador, não de hardware.
- Uma execução por base, 1024 shots.
- O `S` de 2,871 é consistente com `2√2` dentro de ~1 SE; não excede Tsirelson.
- Não há estudo de eficácia, peer review ou replicação independente.
- A documentação e os backends da GJQ podem mudar; cite a data e a versão.
