# SPEC-935-R490 — Composição Unitária do Conhecimento

Status: **implementado** (R490)
Data: 2026-09-13
Requer: R483 (ReverseScanner), R485 (TrajectoryMapper)

## 1. Contexto (proposta do usuário — camada Composição Unitária)

Assim como um cronograma de obras não é suficiente para executar um
empreendimento (a parede precisa de tijolos, cimento, areia, mão de obra,
equipamentos e tempo), uma lista de capacidades futuras não basta: cada
capacidade possui **componentes estruturais** necessários para sua construção.

O Scanner Reverso (R483) responde "o que precisará existir?"; o Trajectory Mapper
(R485) responde "em que ordem?"; a **Composição Unitária** responde
**"do que isso é feito?"** — decompondo cada lacuna em insumos cognitivos:
conceitos, métodos, bases de conhecimento, ferramentas, domínios de apoio e
critérios de validação.

## 2. Objetivos

- **OF1** — `KnowledgeComposition` decompõe cada `g ∈ Δ` em 6 classes de insumo.
- **OF2** — Fonte primária: **bank curado** (`COMPOSITION_BANK`) com composições
  por capacidade-chave (Meta-análise, Prova geométrica, etc.); fallback léxico
  derivado dos tokens para capacidades não curadas (origem `lexical` + warning).
- **OF3** — Integração com `ReverseScanner` (evolution_gap). Consumido depois
  pelo Potentiality (R491) e Successor (R492).
- **OF4** — Anti-overclaim: composição é heurística (curadoria humana necessária);
  origem explícita por item (bank|lexical); nenhum veredicto absoluto.

## 3. Modelo formal

```
compose(g) = {conceitos, metodos, bases, ferramentas, dominios, validacoes, origem}
origem     = "bank" se g ∈ COMPOSITION_BANK, senão "lexical" (derivado de tokens)
scan(scan, alvo) = {por cada g ∈ Δ: compose(g)}   # Δ do ReverseScanner R483
```

Nos relatórios, cada insumo carrega `fonte` ("bank:curada" ou "lexical:tokens").
Validação: critérios de validação são insumos também (benchmarks, testes,
comparação com especialistas).

## 4. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | `compose("metodos.Meta-análise")` → insumos curados (bank) com 6 classes não vazias |
| CA2 | `compose("raciocinio.Prova geométrica")` → insumos curados (bank) |
| CA3 | Capacidade desconhecida → origem lexical, warning, 6 classes presentes (pode ser parcial) |
| CA4 | `scan` integra ReverseScanner e produz composição por cada g ∈ Δ |
| CA5 | Determinismo entre execuções |
| CA6 | Sem alvos → relatório vazio, sem erro |
| CA7 | Anti-overclaim: módulo/relatório sem `superhuman`, `verificad[oa]s?`, `qualis a1`, `superação` |
| CA8 | Campos de cada insumo documentados (fonte) |
| CA9 | Algoritmo documentado no docstring do módulo |

## 5. Entregáveis

- `scanners/knowledge_composition.py` — `KnowledgeComposition`, `CompositionInsight`,
  `CompositionReport`
- `tests/test_r490_knowledge_composition.py`
- Ciclo R490 + reflexão + commit

## 6. Prontidão

- `pytest tests/test_r490_knowledge_composition.py` verde; regressões R483-R489
  verdes; suíte sem novas falhas