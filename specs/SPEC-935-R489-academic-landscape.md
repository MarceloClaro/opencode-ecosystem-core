# SPEC-935-R489 — Paisagem Acadêmica (manifest academic + convergência ampliada)

Status: **implementado** (R489)
Data: 2026-09-13
Requer: R482, R486 (PolymathicConvergence), R487 (análise science-skills)

## 1. Contexto

A demo da R486 revelou cobertura quase nula da paisagem (20 agentes de produto)
para lacunas **epistemológicas** (raciocínio formal, métodos, bases de dados
científicas). A R487 sinalizou como próximo passo expandir o manifest com fontes
acadêmicas. O usuário apontou 3 repos DeepMind (superhuman, alphageometry,
alphageometry2); a R487 já auditou science-skills.

## 2. Objetivos

- **OF1** — `landscape/manifest.json` ganha chave `academic` com 4 fontes
  curadas (Apache-2.0): deepmind-superhuman (guarda-chuva AG/AG2/IMO Bench/
  Aletheia), alphageometry, alphageometry2, science-skills.
- **OF2** — `PolymathicConvergence` cruza `agents` **e** `academic` nas lacunas;
  `source` distingue a origem; score usa title/description/tags (academic).
- **OF3** — Lacunas de raciocínio formal passam a ter pelo menos 1 match
  acadêmico (superhuman/alphageometry cobrem geometria/prova; science-skills
  cobrem literatura/bancos de dados).
- **OF4** — Anti-overclaim: o nome do repo contém "superhuman"; o Core registra
  como **fonte de paisagem**, jamais como veredicto ("superhuman" não aparece
  em capacidade/tierto/juízo do relatório — apenas no id/título da fonte).
- **OF5** — Retrocompatível: fixture agents; suíte R486 intacta.

## 3. Não-objetivos

- Não integra os repos (metadados curados apenas; Apache-2.0 respektado).
- Não auto-baixa science-skills (37 skills são referência de paisagem).

## 4. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | Manifest default expõe ≥4 fontes acadêmicas e 20 agentes |
| CA2 | Match acadêmico: "racionamento.dedutivo" encontra superhuman/alphageometry |
| CA3 | Literature search: "literature.pubmed" encontra science-skills |
| CA4 | source inclui "academic:" para fontes acadêmicas |
| CA5 | Anti-overclaim: texto do relatório não contém veredicto "superhuman" como capacidade; id da fonte pode citar o nome (fonte, não veredicto) |
| CA6 | Suíte R486 continua verde (fixture agents intacta) |
| CA7 | Total de fontes indexadas = 24 (20+4); params refletem |

## 5. Entregáveis

- `landscape/manifest.json` — chave academic (4 entradas)
- `scanners/polymathic_convergence.py` — carregamento e cruzamento academic
- `tests/test_r489_academic_landscape.py`
- ciclo R489 + THIRD_PARTY_NOTICES + commit

## 6. Prontidão

- `pytest tests/test_r489_academic_landscape.py` verde; R486 verde;