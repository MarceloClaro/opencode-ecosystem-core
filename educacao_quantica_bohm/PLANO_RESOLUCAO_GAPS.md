# Plano de resolução dos gaps {#plano-gaps}


Este plano responde, sem otimismo, à pergunta: **os três gaps do Anexo Qualis A1
têm solução?** Sim, mas não com os dados atuais e não no mesmo custo. A ordem
importa: sem resolver o gap 1, a palavra “hardware” fica ambígua; sem resolver o
gap 2, o gap 3 não tem base experimental.

| Gap | Status | O que resolve | Custo |
|---|---|---|---|
| 1. `(simulate)` vs hardware | **resolvido em 7 nov. 2026** | `simulator=False` → hardware | 1 chamada de API |
| 2. baseline de 4 qubits não reproduzido | **resolvido em simulação** | ansatz de 3 camadas + COBYLA; baseline 97%/95% | ~3 min |
| 3. validação A1 (30–50 trials, 5 datasets, seeds, IC, hardware) | aberto, exige protocolo completo | pipeline A1 + hardware | 1–2 dias de compute |

## Gap 1 — o console diz `(simulate)`, o código diz “máquina real”

**Evidência conflitante:**

- O console da Tiangong exibe `Guoji No.8 (simulate)`.
- O código do `gjq-client` chama Guoji08 de **“máquina real”** (máquina real) em um
  comentário do estimador.
- A API estava indisponível no momento da verificação (SSL EOF), então não foi
  possível ler `backend.configuration().simulator`.

**Resolução (executada em 7 nov. 2026):** o comando abaixo retornou
`simulator=False`, `n_qubits=20`, `veredito=hardware`. O guia oficial da Tiangong
também lista Guoji No. 8 como **quantum hardware**. O console exibe `(simulate)`
como **modo** de execução, não como tipo de backend. Evidências:
`dados_hardware/verificacao_guoji08.json` e o guia oficial.

```bash
.venv-quantum/bin/python educacao_quantica_bohm/scripts/checar_backend.py
```

O script imprime `configuration().simulator`, `n_qubits`, `basis_gates`,
`coupling_map`, `properties()` e `status()`. Regra de decisão:

- `simulator is True` → é simulador; o livro deve retirar qualquer “hardware”.
- `simulator is False` → é hardware; o rótulo `(simulate)` do console é modo de
  execução, não tipo de backend.
- `simulator is None` → não declarado; manter “resultados do backend” e pedir
  confirmação ao operador.

**O que o livro faz agora:** usa a evidência `simulator=False` e mantém
“resultados do backend” como linguagem de segurança: hardware não é sinônimo de
resultado perfeito.

## Gap 2 — o baseline de 4 qubits não reproduziu

**O que foi feito:** o primeiro piloto (ansatz raso + Nelder-Mead) ficou em
58,6% (2 qubits) e 34,3% (4 qubits). Era underfitting. A validação forte usa
3 camadas strongly entangling, COBYLA 120 e 5 seeds: baseline **97,0%** em 2
qubits e **95,0%** em 4 qubits. O baseline do relatório é reproduzível.

**O que a validação forte mostra:**

- phase damping é idêntico ao baseline em todos os γ (preserva P(1));
- depolarizing e amplitude damping não melhoram; em γ=0,05, amplitude cai para
  0,940 em 4 qubits;
- com baseline 97%/95%, não há espaço para +3,5 pp (efeito teto).

**O que ainda falta:** 30–50 trials, 4–6 datasets, 5 folds, IC95% da diferença
e validação em hardware. A parte de simulação do gap 2 está resolvida; a parte
A1 continua aberta.

**Scripts:** `scripts/validar_vqc_forte.py` e `scripts/validar_vqc_hardware.py`.

## Gap 3 — o que falta para uma validação A1

| Item | Padrão mínimo | Como o pipeline cobre |
|---|---|---|
| Trials | 30–50 | Optuna TPE, `--trials 50` |
| Datasets | 4–6 | Two Moons, Circles, XOR, linear, checkerboard |
| Seeds | 5 | `--seeds 1 2 3 4 5` |
| Validação | 5 folds estratificados | `--folds 5` |
| Incerteza | IC95% bootstrap | por configuração e por diferença |
| Efeito | Cohen’s d / diferença pareada | phase vs baseline |
| Multiplicidade | correção de Bonferroni/Holm | família de comparações |
| Hardware | execução no backend | `--backend Guoji08` |
| Código/dados | repositório, seeds, JSONs | `dados_a1/` |

**O que já está resolvido e não depende de novo compute:**

- **Phase damping preserva populações Z** — prova matemática; nenhum número de
  trials muda isso.
- **5 trials e 20 pontos de teste não sustentam “confirmação”** — o IC de uma
  proporção com 20 pontos é largo; 3,5 pp cabem dentro da incerteza.
- **44 DOIs verificados** e 5 URLs oficiais; 100 fichas com fonte e grau.
- **Gap 1 resolvido:** guia oficial + `simulator=False`; Guoji08 é hardware; o rótulo `(simulate)` é modo.
- **Gap 2 resolvido em simulação:** baseline 97%/95% com 3 camadas + COBYLA;
  phase damping invariante; sem ganho de ruído.

## Resposta curta

**Sim, tem como resolver — mas na ordem certa:**

1. **Feito:** `checar_backend.py` fechou o gap 1 (`simulator=False`).
2. **Depois:** rodar o baseline de 2 qubits com o protocolo original; só então
   escalar para 4/6 qubits.
3. **Por fim:** rodar o pipeline A1 completo (30–50 trials, 5 datasets, 5 seeds,
   IC, hardware) e registrar tudo em `dados_a1/`.

Sem o passo 2, o passo 3 é teatro estatístico. Com o passo 2, o livro deixa de
dizer “não reproduzimos” e passa a dizer **“reproduzimos o baseline e testamos o
ruído”** — que é o padrão A1.