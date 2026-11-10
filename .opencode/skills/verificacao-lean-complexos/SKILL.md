---
name: verificacao-lean-complexos
description: Verificação formal com números complexos em Lean 4 + Mathlib para o Core, com prova e contraprova obrigatórias e gate fail-closed. Use para validar inovações algébricas com amplitudes complexas (fase global, interferência, Born, unitariedade) e para recusar alegações sem contraprova, com sorry/admit ou com axiomas nativos; não prova hardware, ruído, canal quântico ou vantagem.
---

# Verificação Lean com números complexos (SPEC-935-R1146)

## Quando acionar

Quando a alegação envolver **números complexos** e precisar de verificação
formal: amplitudes, fases, interferência, normalização, portas unitárias,
conjugação, ou uma “inovação” que será adaptada/mitigada no Core.

Não acionar para: hardware, calibração, ruído real, canal quântico, vantagem
quântica ou resultado experimental — o Lean não prova isso.

## Contrato mínimo

Toda entrega deve conter:

1. enunciado em PT-BR;
2. premissas explícitas;
3. código `.lean` com imports;
4. **prova** (`theorem`) e **contraprova** (`theorem` com `≠` ou `¬`);
5. versão Lean/Mathlib;
6. log de compilação;
7. SHA-256 do `.lean` e do log;
8. declaração do que **não** foi provado.

Sem contrato completo: produzir protocolo, nunca veredito.

## Fluxo

```
spec → enunciado complexo → prova → contraprova → compilar → gate → certificado
```

```bash
# 1. compilar o arquivo
cd livro-core/lean
lake env lean ../../lean/quantum-cb/ComplexProofs.lean

# 2. rodar o gate (escreve certificado)
cd ../..
python3 quantum_mitigation/complex_proof_gate.py

# 3. teste dedicado
RUN_LEAN_COMPLEX=1 .venv-quantum/bin/python \
  -m pytest tests/test_r1146_complex_proof_gate.py -q
```

## Regras fail-closed

| Situação | Resultado |
|---|---|
| `sorry`/`admit` | `blocked` |
| `axiom` não declarado | `blocked` |
| `sorryAx` no `#print axioms` | `blocked` |
| `Lean.ofReduceBool`/`trustCompiler` | `native`, gate não aceito |
| teorema ausente | `blocked` |
| alegação sem contraprova | `blocked` |
| sem `lake` | `blocked`; nunca `machine_checked` |

## Como escrever a contraprova

A contraprova deve negar uma alegação vizinha plausível, não repetir a prova:

- fase global: provar invariância; contraprovar que **fase relativa** muda o
  estado (`e^{iπ} ≠ 1`);
- normalização: provar `‖z‖² ≥ 0`; contraprovar probabilidade negativa;
- unitariedade: provar a porta de fase; contraprovar que **escalar** a
  amplitude muda `‖z‖²`.

O pareamento é editorial: o gate verifica presença e forma de negação, não a
semântica. Revisão humana é obrigatória.

## Limites

- Identidades algébricas ideais, sem ruído, calibração ou hardware.
- Aceitar o gate não promove confiança nem autoriza execução.
- Não usar “provado” para afirmar vantagem quântica, eficácia ou validação
  experimental.

## Ferramentas

- Formal: `lean/quantum-cb/ComplexProofs.lean`
- Gate: `quantum_mitigation/complex_proof_gate.py`
- Certificado: `harnesses/quantum-error-mitigation/resultados/r1146_complex_proofs/`
- Skill relacionada: `lean-verificacao-total`
