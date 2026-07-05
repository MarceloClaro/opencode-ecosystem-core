# Notebooks de Demonstração End-to-End

Esta pasta contém notebooks Jupyter executáveis que documentam os principais fluxos do **OpenCode Ecosystem Core**, do básico ao avançado. Todos os notebooks foram executados de ponta a ponta e incluem as saídas reais, servindo simultaneamente como tutorial e como evidência de funcionamento auditável.

| Notebook | Conteúdo | Subsistemas |
| :--- | :--- | :--- |
| [`01_getting_started.ipynb`](01_getting_started.ipynb) | Inicialização do orquestrador, percepção do Global Workspace, roteamento por atenção explicável, delegação, pipeline Reflexion e memória hierárquica. | MCI, Transformer, Trust Engine, Token Economy |
| [`02_academic_pipeline.ipynb`](02_academic_pipeline.ipynb) | Busca acadêmica multiplataforma, fichamentos ABNT/APA, pipeline MASWOS Qualis A1, produção LaTeX modular e design automático de capa. | Research, MASWOS, Publishing, CoverDesigner |
| [`03_swarm_gametheory_diagnose.ipynb`](03_swarm_gametheory_diagnose.ipynb) | Predição por enxame MiroFish, validação Delphi com GraphMemory, meta-raciocínio (38 tipos), equilíbrio de Nash, motores formais, experimento quântico e Deep Diagnose M1–M5. | MiroFish, GameTheory, Reasoning, Scanners |

## Como Executar

A partir da raiz do repositório, sem nenhuma chave de API:

```bash
pip install jupyter
jupyter notebook notebooks/
```

Ou execute de forma não interativa:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/01_getting_started.ipynb
```

## Regenerar os Notebooks

Os notebooks são gerados de forma reprodutível pelo script [`build_notebooks.py`](build_notebooks.py):

```bash
python3 notebooks/build_notebooks.py
```

**Observação:** as células de busca acadêmica (`research_search`, `research`) exigem conexão com a internet; quando offline, degradam graciosamente retornando listas vazias sem interromper a execução.
