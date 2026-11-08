# Anexo: exercício — VQC, ruído benéfico e validação {#anexo-qualis}


Este anexo analisa, como exercício de **parecer Qualis A1**, o relatório
*“Otimização Bayesiana de Hiperparâmetros em Classificadores Variacionais
Quânticos com Ruído Benéfico”* (Qiskit + Optuna TPE, Two Moons, 2 qubits, 5
trials). O objetivo não é destruir o trabalho: é separar **o que foi feito**,
**o que foi medido** e **o que ainda não pode ser afirmado**. Este texto é um
exercício de leitura crítica; não é um parecer oficial nem uma classificação de
periódico.

> **Nota sobre “Qualis A1”:** Qualis é a classificação de **periódicos**, não de
> um manuscrito isolado. Usamos aqui o padrão de exigência editorial associado a
> A1 — originalidade, rigor, reprodutibilidade, estatística, limites e ética —
> como lista de verificação, não como promessa de aceite.

## 1. O que o relatório afirma

O relatório apresenta cinco afirmações principais:

1. **Ruído benéfico:** phase damping em γ ≈ 0,005 eleva a
   acurácia de teste de 85,00% para 88,50% (+3,50 pp).
2. **Arquitetura:** “strongly entangling” é superior às demais, com média 3,9%
   maior.
3. **Importância:** o nível de ruído é o hiperparâmetro mais crítico (0,45),
   seguido por arquitetura (0,28) e taxa de aprendizado (0,14).
4. **Metodologia:** Optuna TPE com 5 trials em espaço hexadimensional.
5. **Novidade:** “primeira aplicação documentada” de Optuna TPE para VQCs em
   Qiskit e “confirmação experimental” do ruído benéfico.

## 2. O que o relatório realmente faz

| Dimensão | O que está no relatório | O que isso permite concluir |
|---|---|---|
| Qubits | 2 | Prova de conceito; não testa escala |
| Amostras | 70 (50 treino / 20 teste) | Um único split; 20 pontos de teste |
| Trials | 5 | Exploratório; não é busca convergida |
| Shots | 256 | Ruído amostral relevante, sem barras de erro |
| Backend | `AerSimulator(method='density_matrix')` | Simulação, não hardware |
| Dataset | Two Moons sintético | Um único problema não linear |
| Métrica | Acurácia de teste | Sem IC, sem teste pareado, sem múltiplas seeds |
| Comparação de arquiteturas | 1–3 trials por arquitetura | Não sustenta “superioridade estatística” |
| Importância de hiperparâmetros | 5 trials | Instável; Optuna precisa de mais trials |

**Leitura:** o relatório é um **pipeline demonstrativo** bem organizado, não um
estudo confirmatório. Isso não o invalida como engenharia; invalida o vocabulário
de “confirmação”, “superioridade estatística” e “primeira aplicação”.

## 3. A inconsistência central: phase damping preserva populações

O classifying output do VQC é, no relatório e na nossa réplica, uma
**probabilidade de medição na base Z** — por exemplo, P(q₀=1). O canal de
phase damping tem operadores de Kraus

<div class="formula">
E₀ = diag(1, √(1−γ)) &nbsp;&nbsp; E₁ = [[0, 0], [0, √γ]]
</div>

A população se transforma como

<div class="formula">
ρ₁₁′ = (1−γ)ρ₁₁ + γρ₁₁ = ρ₁₁
</div>

e o mesmo vale para ρ₀₀. **Phase damping não muda P(0) nem
P(1)**. Se o forward pass do classificador é uma população Z, o ruído de
phase damping **não pode** melhorar a acurácia de teste por si só. Qualquer
ganho relatado teria de vir de:

- dinâmica de treino (gradientes estimados com ruído, shot noise, regularização
  do otimizador);
- um observable diferente de Z;
- uma implementação em que o ruído é aplicado **durante** o treino e altera a
  atualização dos parâmetros;
- ou de flutuação estatística com 5 trials e 20 pontos de teste.

Essa é a pergunta que um parecer A1 faria primeiro: **o mecanismo proposto é
compatível com o observable medido?** No relatório, a resposta não é dada.

## 4. O teste que faltou: mais qubits e validação cruzada

Para testar a robustez, esta edição inclui o script
`scripts/analise_vqc_ruido.py`. Ele:

- usa **2 e 4 qubits** (o relatório usa 2);
- faz **validação cruzada estratificada de 5 folds** (o relatório usa um único
  split 50/20);
- compara **baseline, phase damping γ=0,005, phase damping
  γ=0,010, depolarizing γ=0,005 e amplitude damping
  γ=0,005**;
- reporta média, desvio e **IC95% bootstrap** por configuração;
- simula a matriz densidade sem Aer, com canais de Kraus explícitos.

O comando é:

```bash
.venv-quantum/bin/python educacao_quantica_bohm/scripts/analise_vqc_ruido.py \
  --qubits 2 4 --folds 5
```

Os resultados da triagem rápida ficam em `dados_qualis/vqc_ruido_rapido.json` e
`dados_qualis/RELATORIO_VALIDACAO_RAPIDA.md`. A versão com matriz densidade
completa é `scripts/analise_vqc_ruido.py` (mais cara, para poucos folds).

### Resultados da validação forte

O primeiro piloto usou um ansatz raso e Nelder-Mead; ficou em 58,6% (2 qubits)
e 34,3% (4 qubits). Era **underfitting**, não refutação. A validação forte usa
3 camadas strongly entangling, COBYLA 120, 5 seeds e split 50/20. O baseline
agora reproduz o relatório:

| n | Baseline | Phase 0,005 | Phase 0,050 | Depol. 0,005 | Depol. 0,050 | Ampl. 0,005 | Ampl. 0,050 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | **0,970 ± 0,045** | 0,970 | 0,970 | 0,970 | 0,970 | 0,970 | 0,970 |
| 4 | **0,950 ± 0,061** | 0,950 | 0,950 | 0,950 | 0,950 | 0,950 | 0,940 |

**Leitura honesta:**

1. **O baseline é reproduzível.** 97,0% em 2 qubits e 95,0% em 4 qubits; o
   valor de 85–88,5% do relatório é plausível. O piloto anterior estava
   subtreinado.
2. **Phase damping é idêntico ao baseline em todos os γ.** Isso confirma a
   invariância das populações Z: o forward pass não muda. O “ganho” de 3,5 pp
   não pode ser atribuído a esse canal no observable medido.
3. **Depolarizing e amplitude damping não melhoram.** Em 4 qubits, amplitude
   damping em γ=0,05 cai para 0,940. Não há “sweet spot” nesta réplica.
4. **Efeito teto:** com baseline em 97%/95%, não há espaço para +3,5 pp. Um
   ganho só apareceria se o baseline fosse baixo — e aí a pergunta é se o
   ganho é ruído ou treino.

**Limite:** 5 seeds, um dataset (Two Moons), um split 50/20. Isso é uma
validação forte, mas **não** é A1 completo. Ainda faltam 30–50 trials, 4–6
datasets, 5 folds, IC95% por diferença e hardware.

Scripts: `scripts/validar_vqc_forte.py`; dados:
`dados_qualis/vqc_forte.json`; relatório:
`dados_qualis/RELATORIO_VQC_FORTE.md`.

## 5. O que um parecer A1 exigiria

| Critério | O que falta no relatório | Como corrigir |
|---|---|---|
| **Amostra** | 5 trials, 20 pontos de teste | 30–50 trials; 5 folds × 5 seeds; IC95% |
| **Mecanismo** | phase damping vs observable Z | Medir um observable afetado (X/Y) ou explicar o treino |
| **Comparação** | arquiteturas com 1–3 trials | Mesmo orçamento de treino, mesma inicialização, múltiplas seeds |
| **Generalização** | um dataset | 4–6 datasets; curvas de aprendizado |
| **Hardware** | só simulação | Validar o melhor circuito em IBM/Guangji/Baihua com calibração |
| **Reprodutibilidade** | checksums incompletos | Código, ambiente, seeds, JSONs e logs versionados |
| **Novidade** | “primeira aplicação” | Revisão sistemática com data e bases consultadas |
| **Ética/dados** | dataset sintético | Declarar licença, privacidade e limites de uso |
| **Escopo** | “universalidade” | Trocar por “neste dataset, nestas condições” |

### Abstract corrigido (exemplo)

> Este trabalho apresenta um *pipeline* exploratório de otimização bayesiana de
> VQCs com Optuna TPE em um dataset sintético Two Moons. Em cinco trials, a
> melhor configuração alcançou 88,5% de acurácia de teste, contra 85,0% do
> baseline sem ruído. O intervalo de confiança é largo e o desenho não permite
> afirmar superioridade estatística, universalidade ou mecanismo causal. Os
> resultados motivam uma validação com mais trials, múltiplos splits e hardware.

## 6. Veredito

- **Como engenharia:** o pipeline é útil, claro e reproduzível em parte.
- **Como ciência confirmatória:** não sustenta as afirmações de “confirmação”,
  “superioridade estatística” e “primeira aplicação”.
- **Como pedagogia:** é um excelente caso para ensinar a diferença entre
  **resultado exploratório** e **evidência publicável**.
- **O que falta:** mais trials, validação cruzada, IC, múltiplos datasets,
  mecanismo compatível com o observable e validação em hardware.

> **Mensagem final:** ruído pode ser ferramenta, mas não por decreto. Um número
> bom em cinco trials é uma hipótese; uma hipótese só vira evidência quando
> sobrevive a um desenho que poderia derrubá-la.

## 7. Referências do anexo

BERGSTRA, J.; BARDENET, R.; BENGIO, Y.; KÉGL, B. *Algorithms for Hyper-Parameter
Optimization*. NeurIPS, 2011.

CEREZO, M. et al. *Variational Quantum Algorithms*. Nature Reviews Physics, v. 3,
p. 625–644, 2021.

HAVLÍČEK, V. et al. *Supervised Learning with Quantum-Enhanced Feature Spaces*.
Nature, v. 567, p. 209–212, 2019.

NIELSEN, M. A.; CHUANG, I. L. *Quantum Computation and Quantum Information*.
Cambridge University Press, 2010.

PRESKILL, J. *Quantum Computing in the NISQ Era and Beyond*. Quantum, v. 2,
p. 79, 2018.

SCHULD, M. et al. *Evaluating Analytic Gradients on Quantum Hardware*. Physical
Review A, v. 99, n. 3, 2019.

SRIVASTAVA, N. et al. *Dropout: A Simple Way to Prevent Neural Networks from
Overfitting*. JMLR, v. 15, p. 1929–1958, 2014.

AKIBA, T. et al. *Optuna: A Next-generation Hyperparameter Optimization
Framework*. KDD, 2019.