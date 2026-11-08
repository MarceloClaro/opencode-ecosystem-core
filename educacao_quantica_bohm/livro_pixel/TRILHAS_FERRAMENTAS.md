# Trilhas de ferramentas: instalar, acessar, executar, interpretar e auditar {#trilhas-ferramentas}

> **Para quem nunca abriu um terminal.** Este capítulo assume que o leitor — aluno, professor ou PhD — está tendo o primeiro contato com simuladores, plataformas, bibliotecas e prova formal. Cada passo é explicado, justificado e auditável. Nada de “instale e veja”.

## 1. Por que ferramentas, e por que não começar por elas

Uma ferramenta não ensina física. Ela executa uma receita. Se o leitor não sabe
o que esperar, o resultado vira oráculo. Por isso a ordem do livro é:

```text
manual → simulação → hardware → prova formal → auditoria
```

O manual cria a previsão. A simulação compara a previsão com um mundo ideal. O
hardware confronta o ideal com a matéria. A prova formal verifica a matemática.
A auditoria separa o que foi medido do que foi interpretado.

Este capítulo mostra como fazer cada passo sem depender de um professor ao lado
— e sem acreditar que o software pensa.

## 2. O mapa das ferramentas

| Ferramenta | O que é | Para que serve | Onde entra |
|---|---|---|---|
| **Python** | linguagem de programação | escrever e rodar os scripts | todas as trilhas |
| **venv** | ambiente virtual | isolar versões e dependências | todas |
| **pip** | instalador de pacotes | instalar bibliotecas | todas |
| **Qiskit** | biblioteca de circuitos (IBM) | montar, transpilar e simular circuitos | B–E |
| **Qiskit Aer** | simulador local | simular com ruído | B–E |
| **PennyLane** | biblioteca diferenciável | gradientes e QML | C–E |
| **Cirq** | biblioteca de circuitos (Google) | momentos e agendamento | C–E |
| **NumPy** | computação numérica | vetores, matrizes, amostragem | todas |
| **SciPy** | computação científica | otimização e estatística | D–E |
| **Matplotlib** | gráficos | figuras e inspeção | todas |
| **Optuna** | otimização de hiperparâmetros | VQC | D–E |
| **gjq-client** | SDK da plataforma GJQ | enviar ao backend Tiangong/Guoji | B–E |
| **Lean 4 + Mathlib** | assistente de provas | verificar identidades matemáticas | C–E |
| **Git** | controle de versão | registrar o que foi executado | D–E |

### 2.1 Por que três bibliotecas, e não uma

Qiskit, PennyLane e Cirq olham o mesmo circuito por ângulos diferentes:

- **Qiskit** é orientada a hardware: circuitos, transpilação, backend, calibração.
- **PennyLane** é orientada a diferenciação: gradientes, treino, QML.
- **Cirq** é orientada a momentos: agendamento, portas, estrutura temporal.

Se o leitor só conhece uma, pode confundir a API com o conceito. Montar o mesmo
Bell nas três mostra que o circuito é o mesmo; o que muda é a linguagem.

### 2.2 Por que Lean 4 depois, e não antes

Lean 4 não simula um qubit. Ele verifica uma **afirmação matemática**. Por isso
vem depois do experimento: primeiro o leitor vê o fenômeno, depois aprende a
provar a identidade que o descreve. O Lean não substitui o backend; ele impede
que uma conta errada seja apresentada como prova.

## 3. Trilha 0 — Preparar o computador

### 3.1 O que você precisa {#ferramentas-pre-requisitos}

- Um computador com 8 GB de RAM (16 GB para Lean/Mathlib).
- 5 GB livres (mais para Mathlib).
- Internet para instalar.
- Terminal (Linux/macOS) ou PowerShell (Windows).
- Um editor de texto simples: VS Code, Sublime, Gedit ou Notepad++.

### 3.2 Instalar Python

Baixe Python 3.12 ou superior em <https://www.python.org/downloads/>. No
Windows, marque **“Add Python to PATH”**. Verifique:

```bash
python3 --version
```

Se aparecer `Python 3.12.x` ou maior, está pronto.

### 3.3 Criar o ambiente virtual

```bash
mkdir -p ~/quantica
cd ~/quantica
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .\.venv\Scripts\Activate.ps1   # Windows PowerShell
```

O prompt muda para `(.venv)`. Isso significa que as bibliotecas ficarão isoladas
naquela pasta.

### 3.4 Instalar as bibliotecas

```bash
python -m pip install --upgrade pip
pip install qiskit qiskit-aer pennylane cirq gjq-client numpy scipy matplotlib optuna
```

### 3.5 Verificar a instalação

```bash
python - <<'PY'
import qiskit, pennylane, cirq, numpy
print("qiskit", qiskit.__version__)
print("pennylane", pennylane.__version__)
print("cirq", cirq.__version__)
print("numpy", numpy.__version__)
PY
```

Se as quatro versões aparecerem, a base está instalada. Se uma falhar, copie a
mensagem de erro e consulte a tabela da seção 10.

## 4. Trilha 1 — Simulação local

### 4.1 O primeiro circuito

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
estado = Statevector(qc)
print(estado)
```

Saída esperada:

```text
Statevector([0.70710678+0.j, 0.        +0.j,
             0.        +0.j, 0.70710678+0.j],
            dims=(2, 2))
```

Isso é o estado de Bell: amplitudes `1/√2` em `|00⟩` e `|11⟩`.

### 4.2 Rodar os 18 experimentos

```bash
python 08_experimentos_18.py --sim --only E09
python 08_experimentos_18.py --sim
python 08_experimentos_18.py --report
```

O primeiro comando roda só o E09; o segundo, os 18; o terceiro gera
`dados/RELATORIO_EXPERIMENTOS.md` e `dados/experimentos.csv`.

### 4.3 Ler o JSON

```python
import json
d = json.load(open("dados/E09.json", encoding="utf-8"))
print(d["simulado"]["counts"])
print(d["simulado"]["leitura"])
```

O campo `counts` é uma lista de dicionários. No E09, há um dicionário com as
chaves `"0"` e `"1"`. A soma deve ser 1024.

### 4.4 Interpretar

```python
counts = d["simulado"]["counts"][0]
total = sum(counts.values())
p1 = counts.get("1", 0) / total
print(p1)
```

Se `p1 ≈ 0,75`, o simulador reproduziu o ideal. Se não, verifique a seed, o
número de tiros e a versão do Qiskit.

## 5. Trilha 2 — As três bibliotecas

### 5.1 Qiskit

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0); qc.cx(0, 1); qc.measure([0, 1], [0, 1])
print(qc.draw("text"))
```

### 5.2 PennyLane

```python
import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def bell():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.probs(wires=[0, 1])

print(bell())
```

### 5.3 Cirq

```python
import cirq

q0, q1 = cirq.LineQubit.range(2)
circuito = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1, key="m"),
)
print(circuito)
```

### 5.4 Comparar

As três saídas representam o mesmo estado. O leitor deve comparar:

- a ordem dos qubits;
- a convenção de bits;
- o desenho do circuito;
- o resultado de 1024 amostras.

Se as três não concordarem, o problema não é a física: é a convenção da API.

## 6. Trilha 3 — Plataforma GJQ

### 6.1 O que é

A plataforma **Tiangong/GJQ** oferece simuladores e backends supercondutores.
O `gjq-client` é o SDK Python que envia o circuito e devolve counts, task ID e
metadados.

### 6.2 Criar a conta e a API key

1. Abra <https://tiangongqs.com/cloud/circuit>.
2. Crie a conta (ou use a conta do responsável, se você for menor).
3. Gere a **API key** no perfil.
4. Leia os termos de uso e a política de dados.

> **Menores:** a conta e a chave devem ser do responsável. O livro não autoriza
> criar conta de plataforma sem consentimento.

### 6.3 Configurar a chave

```bash
export GJQ_API_KEY="sua-chave"        # Linux/macOS
# $env:GJQ_API_KEY = "sua-chave"      # PowerShell
```

Nunca escreva a chave no script, no caderno ou no PDF. O `gjq-client` grava o
cache em:

```text
~/.gjq_client/gjq_client_account.json
```

Proteja:

```bash
chmod 600 ~/.gjq_client/gjq_client_account.json
```

### 6.4 Rodar um job

```bash
python 08_experimentos_18.py --sim --only E09
python 08_experimentos_18.py --real --backend Guoji08 --only E09
```

O primeiro comando é obrigatório: o script exige o JSON simulado antes do
hardware. O segundo envia o circuito e grava `real.counts`, `real.task_ids`,
`real.backend`, `real.shots` e `real.timestamp`.

### 6.5 Interpretar o resultado

```python
import json
d = json.load(open("dados/E09.json", encoding="utf-8"))
real = d["real"]
print(real["backend"], real["task_ids"])
counts = real["counts"][0]
print(counts, sum(counts.values()))
```

Compare com o livro: E09 tem `761` em `1` e `263` em `0`, com 1024 tiros. A
diferença para o ideal é compatível com 1024 tiros e com erro de porta/leitura.

### 6.6 Auditar a execução

- O `task_id` existe?
- O backend é o que você pediu?
- A soma dos counts é 1024?
- A data é a da execução?
- A calibração foi registrada?
- O resultado está no JSON, não só na tela?

Se qualquer resposta for “não”, o resultado não é auditável.

## 7. Trilha 4 — Hardware real

### 7.1 Simulador × backend

O simulador é limpo. O backend tem:

- erro de porta;
- erro de leitura;
- T1/T2;
- fila;
- calibração que muda com o tempo.

### 7.2 Dois backends

```bash
python 08_experimentos_18.py --real --backend Guoji08 --only E05
python 08_experimentos_18.py --real --backend Baihua --only E05
```

Compare `P(00)+P(11)`, `S`, `sobreposicao` e `task_ids`. Não diga “um é melhor”
sem definir o critério.

### 7.3 O que o número não prova

- Não prova fidelidade de estado.
- Não prova emaranhamento.
- Não prova vantagem quântica.
- Não generaliza para outro backend ou outra data.

## 8. Trilha 5 — Lean 4

### 8.1 O que é

Lean 4 é um assistente de provas. Mathlib é a biblioteca de matemática. O
arquivo `QuantumTrails.lean` verifica identidades como `H² = I`, `HZH = X`,
`CHSH|Φ+⟩ = 2√2|Φ+⟩` e modelos fenomenológicos de ruído.

### 8.2 Instalar

```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
source ~/.elan/env
lean --version
lake --version
```

No Windows, use o instalador oficial de `elan`.

### 8.3 Verificar o arquivo

```bash
cd livro-core/lean
lake env lean QuantumTrails.lean
```

A primeira execução baixa Mathlib e pode demorar. Se terminar sem erro, os
teoremas foram verificados. Se aparecer `sorry` ou `admit`, o arquivo não está
completo.

### 8.4 O que o Lean não prova {#ferramentas-lean-limites}

- counts de hardware;
- calibração;
- fidelidade;
- interpretação de Bohm;
- vantagem quântica.

O Lean prova a matemática. O experimento prova — ou não — a física.

## 9. Trilha 6 — Auditoria e reprodutibilidade

### 9.1 Registre o ambiente

```bash
python --version > ambiente.txt
pip freeze > requirements.lock.txt
sha256sum dados/E09.json > hashes.txt
```

### 9.2 Registre a execução

- data e hora;
- backend;
- shots;
- task ID;
- seed;
- versão das bibliotecas;
- commit do código, se houver.

### 9.3 Repita

- outra seed;
- outro backend;
- outro dia;
- outro computador.

Se o resultado não se repete, o problema pode ser ruído, calibração ou código.
A auditoria não elimina a incerteza; ela mostra de onde ela vem.

### 9.4 Classifique a afirmação

Use o **Ledger de afirmações**:

- `machine-checked` — Lean;
- `calculated` — conta à mão;
- `measured` — hardware com task ID;
- `bibliographic` — DOI;
- `interpretive` — Bohm;
- `protocol` — estudo ainda não executado.

## 10. Erros comuns e como diagnosticar

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `ModuleNotFoundError` | ambiente não ativado | ative o `.venv` |
| `pip: command not found` | Python sem pip | reinstale com “Add to PATH” |
| `GJQ_API_KEY ausente` | variável não definida | exporte e reabra o terminal |
| `SSL: CERTIFICATE_VERIFY_FAILED` | rede/proxy | tente outra rede |
| fila longa | backend ocupado | use simulador ou outro backend |
| `timeout` | job demorou | aumente `--timeout` |
| `QFTGate` ausente | Qiskit antigo | `pip install --upgrade qiskit` |
| Lean baixa Mathlib para sempre | primeira execução | espere; precisa de rede |
| `sorry` no Lean | prova incompleta | não declare verificado |
| counts não somam 1024 | backend devolveu menos | registre o valor real |

## 11. Ferramentas por trilha {#ferramentas-por-trilha-tabela}

| Trilha | Ferramentas mínimas | Ferramentas opcionais | Onde |
|---|---|---|---|
| **A — Despertar** | papel, moeda, cartão; Python com adulto | simulador | `08_experimentos_18.py` |
| **B — Fundamentos** | Qiskit, NumPy | PennyLane, Cirq | `01`–`08` |
| **C — Graduação** | Qiskit, PennyLane, Cirq, Matplotlib | Lean 4 | `01`–`08`, `QuantumTrails.lean` |
| **D — Mestrado** | Qiskit Aer, SciPy, Optuna | Lean 4, Git | `07`, `QuantumTrails.lean` |
| **E — Doutorado** | stack completa + Git + Lean | backend duplo | tudo |
| **P — Professor** | Qiskit, projetor | hardware demonstrativo | `08` + resultados documentados |

## 12. Primeiros 90 minutos

| Tempo | O que fazer | Produto |
|---:|---|---|
| 0–10 min | ler a seção 1 e 2 | mapa mental |
| 10–25 min | criar venv e instalar | `(.venv)` ativo |
| 25–40 min | rodar `--sim --only E09` | `dados/E09.json` |
| 40–55 min | ler o JSON e calcular `P(1)` | conta à mão |
| 55–70 min | rodar E03 e comparar | contagem |
| 70–85 min | rodar `--report` | CSV |
| 85–90 min | escrever o que provou/não provou | uma frase |

## 13. Argumento final

A ferramenta é meio, não fim. O leitor deve conseguir dizer:

1. **O que eu instalei** e por quê.
2. **O que eu executei** e com quais parâmetros.
3. **O que eu medi** e com qual incerteza.
4. **O que eu calculei** à mão.
5. **O que eu provei** no Lean.
6. **O que eu não posso afirmar.**

Se ele consegue responder às seis, a ferramenta virou conhecimento. Se só
consegue mostrar a tela, ainda está no começo.

## 14. Referências

QISKIT. *Qiskit 0.44.0*. Zenodo, 2020.
DOI: <https://doi.org/10.5281/zenodo.2573505>.

PENNYLANE. *PennyLane: Automatic differentiation of hybrid quantum-classical
computations*. Documentação oficial. Disponível em:
<https://docs.pennylane.ai>.

CIRQ. *Cirq: A Python framework for creating, editing, and invoking quantum
circuits*. Documentação oficial. Disponível em:
<https://quantumai.google/cirq>.

LEAN. *Lean 4*. Disponível em: <https://lean-lang.org>.

MATHLIB. *Mathlib4*. Disponível em: <https://leanprover-community.github.io>.

TIANGONG / CETC-ICQ. *Quantum Computing Platform User Guide*. Disponível em:
<https://tiangongqs.com/docs/quantum/>.

GUOJI QUANTUM. *gjq-client* e *gjq-runtime-mcp-server*. Repositórios públicos,
Apache 2.0.

NIELSEN, M. A.; CHUANG, I. L. *Quantum Computation and Quantum Information*.
Cambridge: Cambridge University Press, 2000.
DOI: <https://doi.org/10.1017/CBO9780511976667>.
