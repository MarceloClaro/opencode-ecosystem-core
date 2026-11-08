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
2. Qiskit 2.3.0/Aer, PennyLane, Cirq, NumPy.
3. MindQuantum 0.11.0 + MindSpore + `GJQ_API_KEY`.
4. Lean 4 + Mathlib.
5. Auditoria.

## Comandos mínimos

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install 'qiskit==2.3.0' 'qiskit-aer==0.18.2' 'gjq-client==0.2.1' pennylane cirq numpy scipy matplotlib optuna
pip install 'mindquantum==0.11.0'
python -c "import qiskit, pennylane, cirq, mindquantum, gjq_client; print('ok')"
python 08_experimentos_18.py --sim --only E09
python 08_experimentos_18.py --real --backend Guoji08 --only E09
cd livro-core/lean && lake env lean QuantumTrails.lean
```

## MindQuantum

- Versão fixada: `mindquantum==0.11.0`; espelho GitHub em 0.12.0.
- Trilha: VQC, ruído, simulador HiQ, QML, química e otimização.
- Citação: arXiv:2406.17248.
- Docs: <https://www.mindspore.cn/mindquantum/docs/en/stable/index.html>.
- O Gitee é snapshot migrado para o AtomGit; confirme a versão antes de citar.
- Não copie tutorial ou código sem preservar a licença Apache-2.0.

## Segurança

- Chave só em `GJQ_API_KEY`.
- Cache `~/.gjq_client/` com `chmod 600`.
- Menor de idade: conta do responsável.
- Não publique task ID com dado pessoal.

## Critério

O leitor deve saber o que instalou, o que executou, o que mediu, o que calculou,
o que provou e o que não pode afirmar.
