# R1104 — Verificação da fase P0

Data: 2026-11-12.  
Spec: `specs/SPEC-935-R1104-iit-metrics-p0.md`.  
Estado: implementado e verificado por testes; sem cálculo de Φ, sem declaração de consciência e sem alteração de permissões.

## 1. Resultado dos testes

| Gate | Comando | Resultado |
|---|---|---|
| RED inicial | `pytest tests/test_r1104_iit_metrics_p0.py -q` | 12 failed |
| GREEN P0 | `pytest tests/test_r1104_iit_metrics_p0.py -q` | 13 passed |
| R1103 + R1104 | `pytest tests/test_r1103_iit_research.py tests/test_r1104_iit_metrics_p0.py -q` | 20 passed |
| Evolução/ecossistema | 8 arquivos de evolução/ecossistema | 109 passed |
| Integração ampliada | `test_r216`, `test_r233`, `test_r640`, `test_r665`, `test_r983`, `test_r110` | 79 passed, 1 failed (preexistente) |
| Suíte completa | `pytest -q` | interrompida na coleta por 23 erros preexistentes de dependências/arquivos opcionais |

O único teste falho do subconjunto ampliado é
`tests/test_r640_ecosystem_surface.py::test_orchestrator_is_default_and_network_is_connected`,
com `UnboundLocalError: cannot access local variable 'colab_mcp_config'` em
`integrations/opencode_cli.py:914`. Esse arquivo já estava modificado antes do
P0 e não foi tocado nesta rodada. A falha não envolve `mci/iiit_metrics.py` ou
`mci/__main__.py`.

A suíte completa também encontrou erros de coleta por `fastapi`/`psutil`
ausentes, arquivos não encontrados e um erro de importação em
`integrations/opencode_cli.py`. Nenhum desses erros foi introduzido pelo P0.

## 2. Correções implementadas

- **G01 determinismo:** `stable_bucket()` usa SHA-256, não `hash()` randomizado.
  A MI passou a ser condicionada à estratégia (com `missing` como categoria),
  evitando que `action_id` único infle artificialmente a métrica.
- **G02 diversidade:** entropia categórica normalizada; uma estratégia → 0;
  quatro equilibradas → ~1; distribuição enviesada → valor intermediário.
- **G04 payload/missing:** leitura de `payload`, nenhum default para outcome,
  confiança ou estratégia. `missing` tem contagem e taxa próprias.
- **G05 abstenção:** removido o termo `-0.10 * abstention_rate`. Cobertura,
  abstenção, missing e risco seletivo são reportados separadamente.
- **G06 fallback sintético:** `analyze` não gera dados sintéticos; retorna
  `insufficient_data` e código de saída 2. `synthetic` é um subcomando explícito.
- **G07 registry:** usa `record(objective, changes, score, lessons, round_id)`;
  retorna dicionário (`asdict`) e aceita registry temporário para testes.
- **G08 rótulos:** removidos “research_grade”, “apto para publicação” e
  equivalentes. A saída declara “Sinal descritivo” e “não é validação científica”.
- **G09 `n_states`:** o histograma de confiança usa o `n_states` solicitado;
  metadata registra `confidence_distribution_length`.
- **G10 CLI:** uma única `iiit_metrics_cli`; parser argparse real;
  `python -m mci iiit-metrics --help` sai com 0.
- **G11 dados insuficientes:** sem traces ou sem outcomes utilizáveis,
  `available=False`, `score=None`, `status='insufficient_data'`.

## 3. Evidência de isolamento

Hashes SHA-256 no estado final (os dois primeiros são também os hashes
antes/depois do audit histórico):

| Arquivo | Hash |
|---|---|
| `.mci_state/shared_memory.json` | `e700897f9d72bfdfca246d7865cf662012d8bbe4c07132cb5d972c819b43f9cc` |
| `evolution/cycles.json` | `66e25696050e80b4ead8bdc1fb674b5497e4ed7806f9f730ead743a59a375209` |
| `mci/iiit_metrics.py` | `a08b3207b19f74341102201521ed3fc333324d89d918081ea922650b3528072d` |
| `mci/__main__.py` | `c114226ad1d9158194427ce555cf85d49e01921b468a375afae411a732726350` |
| `tests/test_r1104_iit_metrics_p0.py` | `8882cccda482f8401d3471106b3b5e46edb7f306cd8e8a21254cb32707427eda` |
| `specs/SPEC-935-R1104-iit-metrics-p0.md` | `fcfec23d5f109a4abb046fd997aa5d22f085f4ed46e113611b4158dc2cc4fa20` |

Os dois primeiros hashes são idênticos aos registrados no `audit.json`
histórico antes/depois das contraprovas. Isso mostra que o P0 não gravou no
estado real do MetaBus nem no `evolution/cycles.json`. O `audit.json`
permanece histórico e não foi sobrescrito; seus hashes de código antigo não
correspondem mais ao código atual, como esperado.

## 4. Comandos verificados

```text
python -m mci iiit-metrics --help                 -> exit 0
python -m mci iiit-metrics synthetic --n-traces 5 -> exit 0, rótulo "não representam telemetria"
python -m mci iiit-metrics score --traces ...     -> exit 0, "não causal" e "não é Φ"
python -m mci iiit-metrics analyze --limit 3      -> exit 2, insufficient_data/no_outcomes
```

O `analyze` real encontrou eventos recentes sem outcome utilizável e falhou
de forma fechada, em vez de produzir score ou dados sintéticos.

## 5. Riscos residuais

- **G03 não corrigido:** o campo `causal_efficacy` permanece por
  compatibilidade; a saída o rotula como “Influência Sequencial (não causal)”.
  Um grafo de adjacência temporal não demonstra causalidade. A correção
  metodológica completa exige intervenção/TPM e fica para rodada própria.
- **Suíte completa não concluída:** 23 erros de coleta preexistentes impedem
  uma execução integral. O subconjunto de 109 testes de evolução/ecossistema
  passou; o teste R640 falhou por um defeito preexistente em
  `integrations/opencode_cli.py`, fora do escopo P0.
- **Sem benchmark held-out:** o P0 corrige implementação e rótulos; não
  demonstra melhoria de autonomia em tarefas reais. Isso continua sendo o
  experimento A0–A4 de `experiments.json`, não executado.
- **Sem Φ e sem consciência:** nenhum cálculo de Φ foi feito; nenhuma
  afirmação de consciência, publicação ou superioridade científica é sustentada.
