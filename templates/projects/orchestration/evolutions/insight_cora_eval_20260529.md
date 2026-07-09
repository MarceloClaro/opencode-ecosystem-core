# CORA-Eval: Evolução Completa — 28-29 Maio 2026

## Resumo

Em 2 sessões, o ecossistema OpenCode avançou de **0.67 (Básico)** para **2.70 (Pós-Graduação)**,
completando os marcos M1, M2 e M3 e ficando a apenas 0.30 pontos do M4 (Pesquisa).

## Cronologia

| # | Data/Hora | Evento | CORA-Score | $\Delta$ | Dim | Fonte |
|---|:---------:|--------|:----------:|:--------:|:---:|-------|
| 0 | 28/05 19:00 | Baseline | 0.67 | — | 4/10 | Pipeline LaTeX SDD+TDD |
| 1 | 28/05 20:52 | +Listas DCA (18 questões) | 1.55 | +0.88 | 6/10 | DCA pós-graduação |
| 2 | 28/05 21:01 | Cobertura horizontal N1 | 1.90 | +0.35 | **10/10** | D4-D8 avaliados |
| 3 | 28/05 21:07 | Salto M3 (D3-D8→N2) | 2.52 | +0.62 | 10/10 | Mapeamento N2/N3 |
| 4 | 28/05 21:52 | GAT TDD (D10 N4) | 2.58 | +0.06 | 10/10 | Farinelli 2021 |
| 5 | 29/05 05:22 | D3+D7 TDD (estatística+código) | 2.62 | +0.04 | 10/10 | TDD real |
| 6 | 29/05 05:45 | Validação externa (PE+Rosalind) | **2.70** | **+0.08** | 10/10 | Project Euler + Rosalind |

## Marcos

| Marco | Score | Status | Data | Como |
|-------|:-----:|:------:|------|------|
| M1 Fundação | 0.90 | ✅ | 28/05 | Baseline (D1,D3,D7,D9) |
| M2 Graduação | 1.90 | ✅ | 28/05 | Listas DCA + cobertura N1 |
| M3 Especialização | 2.52 | ✅ | 28/05 | D3-D8→N2, D2/D3/D9→N3 |
| M4 Pesquisa | 3.00 | 🔄 | — | faltam 0.30 |
| M5 Fronteira | 4.00 | ⬜ | — | catálogo 60+ problemas |

## Fontes de Ground Truth

| Fonte | Tipo | Verificações | Confiança |
|-------|------|:------------:|:---------:|
| Project Euler | Matemática (externo) | 7 problemas, 4M solvers | Muito Alta |
| Rosalind | Bioinformática (externo) | 5 problemas, 270K solvers | Muito Alta |
| DCA Listas | Física-Matemática | 18 questões | Alta |
| GAT Farinelli | Geometria/Finanças | 30 refs + 10 testes TDD | Alta |
| TDD Interno | Química/Bio/Geo/Lit | 47 testes | Alta |
| TDD Estatística | Estatística/Código | 16 testes | Alta |

## Suites TDD — 91/91 GREEN

```
D3  Estatistica       9/9   ✅
D4  Quimica            9/9   ✅
D5  Biologia          11/11  ✅
D6  Geociencias       15/15  ✅
D7  Codigo             7/7   ✅
D8  Literatura (N1)   12/12  ✅
D8  Bibliografia (N2)  6/6   ✅
D10 GAT (N4)          10/10  ✅
EXT Validacao         12/12  ✅
─────────────────────────────
TOTAL                 91/91  ✅
```

## Próximo Passo: M4 (3.00)

Faltam **0.30 pontos**. Estratégia: D4→N3 (+0.08) + D6→N3 (+0.06) + D2→N4 (+0.10) + D3→N4 (+0.06) = +0.30.
