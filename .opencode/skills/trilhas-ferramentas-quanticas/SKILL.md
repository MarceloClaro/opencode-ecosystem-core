---
name: trilhas-ferramentas-quanticas
description: Guia passo a passo para instalar Python, Qiskit, PennyLane, Cirq, gjq-client e Lean 4, acessar a plataforma GJQ, executar scripts, extrair resultados e auditar. Use com alunos e PhDs em primeiro contato; não crie conta de menor sem responsável nem exponha API key.
metadata:
  version: "1"
  origem: "R1099 — capítulo Trilhas de ferramentas"
---

# Trilhas de ferramentas

## Ordem

1. Python + venv + pip.
2. Qiskit/Aer, PennyLane, Cirq, NumPy.
3. `gjq-client` + `GJQ_API_KEY`.
4. Lean 4 + Mathlib.
5. Auditoria.

## Comandos mínimos

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install qiskit qiskit-aer pennylane cirq gjq-client numpy scipy matplotlib optuna
python -c "import qiskit, pennylane, cirq; print('ok')"
python 08_experimentos_18.py --sim --only E09
python 08_experimentos_18.py --real --backend Guoji08 --only E09
cd livro-core/lean && lake env lean QuantumTrails.lean
```

## Segurança

- Chave só em `GJQ_API_KEY`.
- Cache `~/.gjq_client/` com `chmod 600`.
- Menor de idade: conta do responsável.
- Não publique task ID com dado pessoal.

## Critério

O leitor deve saber o que instalou, o que executou, o que mediu, o que calculou,
o que provou e o que não pode afirmar.
