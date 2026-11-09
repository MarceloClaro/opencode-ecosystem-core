# SPEC-935-R1119 — Passe de Pauli-frame para randomized compiling

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1114 (QEM), R1118 (calibração)

## 1. Contexto

O operador pediu RC real, mas o pré-requisito era o passe de Pauli-frame.
Transpilação aleatória não é RC. Esta spec implementa o twirl de Pauli em
portas Clifford:

```
P' · G · P = G,   P' = G P G†
```

Cada porta Clifford recebe um Pauli aleatório `P` antes e o conjugado `P'`
depois. O circuito permanece logicamente idêntico (a menos de fase global), mas
o ruído entre portas é twirlado.

## 2. Requisitos

- **R1.** Implementar `conjugate_pauli` via representação simplética, validado
  contra multiplicação de matrizes para H, S, CX e CZ.
- **R2.** Implementar `pauli_frame_pass` para portas Clifford 1q e 2q.
- **R3.** Preservar medições, barreiras e registradores.
- **R4.** Sorteio reproduzível com `seed`.
- **R5.** `strict=True` recusa portas não-Clifford; `strict=False` registra e
  mantém a porta.
- **R6.** `verify_equivalence` confirma igualdade up to fase global.
- **R7.** Comando `rc` no harness gera QASM twirlado + relatório, sem hardware.
- **R8.** Testes com 1q, 2q, medição, determinismo e porta não-Clifford.
- **R9.** Não chamar o resultado de “RC validado” sem execução e validação.
- **R10.** Nenhuma chave, nenhum hardware.

## 3. Portas suportadas

`id, h, x, y, z, s, sdg, sx, sxdg, cx, cy, cz, swap, rx, ry, rz` com ângulos
Clifford (múltiplos de π/2). `rx(0.1)` é recusado em modo estrito.

## 4. Critérios de aceitação

- conjugação 1q/2q sem divergência contra matriz;
- twirl de 1q e 2q equivalente up to fase;
- medições preservadas;
- mesma seed → mesmo QASM;
- `strict=False` mantém porta não-Clifford e registra em `skipped`;
- comando `rc` gera artefatos sem hardware;
- testes R1119 passam;
- nenhum overclaim.

## 5. Não objetivos

- Executar RC em hardware.
- Corrigir 2q com decodificador em tempo real.
- Declarar redução de erro sem run twirlado vs baseline.
- Substituir GST/cycle benchmarking.
