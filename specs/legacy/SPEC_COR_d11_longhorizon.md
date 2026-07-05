# SPEC-COR-D11: Raciocinio de Longo Horizonte em DAG (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: pending

## Objective
Suite TDD para D11 do CORA-Eval — validacao de raciocinio de longo horizonte em grafos aciclicos dirigidos (DAG). 150 CTs em 5 dominios (Logica, Matematica, Planejamento, Fluxo de Codigo, Cientifico) × 4 niveis (N1-N4). Engine DAG propria com propagacao de estados.

## Acceptance Criteria

### Dominio 1: Logica (DAG-L) — 30 CTs
- [ ] CTs L:N1 (5): Propagacao booleana em DAGs de 2-3 nos (AND, OR, NOT)
- [ ] CTs L:N2 (7): Implicacao multi-nivel, 4-6 nos
- [ ] CTs L:N3 (8): Satisfatibilidade booleana, 7-10 nos
- [ ] CTs L:N4 (10): Logica de predicados com quantificadores, 11-20 nos

### Dominio 2: Matematica (DAG-M) — 30 CTs
- [ ] CTs M:N1 (5): Expressoes aritmeticas simples, DAGs 2-3 nos
- [ ] CTs M:N2 (7): Operacoes matriciais encadeadas, 4-6 nos
- [ ] CTs M:N3 (8): Composicao funcional aninhada, 7-10 nos
- [ ] CTs M:N4 (10): Cadeias de prova, 11-20 nos

### Dominio 3: Planejamento (DAG-P) — 30 CTs
- [ ] CTs P:N1 (5): Cadeias de dependencia linear, 2-3 nos
- [ ] CTs P:N2 (7): Alocacao de recursos, 4-6 nos
- [ ] CTs P:N3 (8): Satisfacao de restricoes, 7-10 nos
- [ ] CTs P:N4 (10): Planejamento temporal interdependente, 11-20 nos

### Dominio 4: Fluxo de Codigo (DAG-C) — 30 CTs
- [ ] CTs C:N1 (5): Arvores de expressao, 2-3 nos
- [ ] CTs C:N2 (7): Fluxo de controle condicional, 4-6 nos
- [ ] CTs C:N3 (8): Propagacao de parametros multi-etapa, 7-10 nos
- [ ] CTs C:N4 (10): Execucao simbolica multi-modulo, 11-20 nos

### Dominio 5: Cientifico (DAG-S) — 30 CTs
- [ ] CTs S:N1 (5): Cadeias de raciocinio cientifico simples, 2-3 nos
- [ ] CTs S:N2 (7): Multiplas hipoteses em paralelo, 4-6 nos
- [ ] CTs S:N3 (8): Propagacao de evidencia multi-fonte, 7-10 nos
- [ ] CTs S:N4 (10): Sintese interdisciplinar multi-metodo, 11-20 nos

## Distribuicao

| Dominio | N1 | N2 | N3 | N4 | Total |
|---------|----|----|----|----|-------|
| Logica (DAG-L) | 5 | 7 | 8 | 10 | 30 |
| Matematica (DAG-M) | 5 | 7 | 8 | 10 | 30 |
| Planejamento (DAG-P) | 5 | 7 | 8 | 10 | 30 |
| Fluxo de Codigo (DAG-C) | 5 | 7 | 8 | 10 | 30 |
| Cientifico (DAG-S) | 5 | 7 | 8 | 10 | 30 |
| **Total** | **25** | **35** | **40** | **50** | **150** |

## Fundamento Teorico
Inspirado por "The Power of Reasoning in Long-Horizon Tasks" (2604.14140v1):
tarefas DAG com nos de baixa dificuldade individual exigem raciocinio de
horizonte estendido para propagacao correta atraves do grafo.

## Verificadores CORA-Debate
V1 (Consistencia Interna), V2 (Completude), V3 (Correcao Formal),
V4 (Robustez), V5 (Generalizacao), V6 (Eficiencia Cognitiva),
V7 (Rastreabilidade).

## Test File
tests/test_d11_longhorizon.py

## Execucao
```bash
cd tests
python -m pytest test_d11_longhorizon.py -v
```

## Peso CORA-Eval
Peso 7% no CORA-Score total. Integrado com verificadores V1-V7.
