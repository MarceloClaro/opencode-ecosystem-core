# SPEC-935-R492 — Successor Generator (Gerador de Sucessores)

Status: **implementado** (R492)
Data: 2026-09-13
Requer: R491 (StructuralDNA), R490, R485-R486; inspiração: proposta do usuário
(camada Successor Generator) + feynman-tutor (match method Feynman → tutoria)

## 1. Contexto (proposta do usuário)

Inovações frequentemente não surgem de componentes novos, mas da **recombinação
de capacidades existentes** (Motor + Asas + Controle → Avião). O sistema precisa
de um mecanismo explícito para gerar hipóteses de sucessores plausíveis.

Exemplos do usuário (curados em SUCCESSOR_BANK):
- Gap Detection + Trajectory Mapping + AutoEvolve → **Potential Discovery Engine**
- Cross Validation + Polymorphic Convergence + Trajectory Mapper → **Scientific Discovery Engine**
- Noological Scanner + Trajectory Mapper + Cross Validation → **Cognitive Manifold Mapper**

## 2. Objetivos

- **OF1** — `SuccessorGenerator` combina capabilities existentes (pares e trios)
  em hipóteses de sucessores; SUCCESSOR_BANK com os curados do usuário.
- **OF2** — Geração combinatória controlada (módulos distintos; `max_combos`);
  exclui combinações já curadas (novelty).
- **OF3** — Score heurístico documentado: diversidade de módulos + novelty +
  centralidade; ranking ordenado.
- **OF4** — Hipóteses explícitas (não implementações): anti-overclaim; cada
  sucessor diz o que seria e que combinação o sustenta.

## 3. Modelo formal

```
score(combo) = 1.0·diversity(combo) + 0.5·novelty(combo) + 0.3·centrality(combo)
diversity    = nº de módulos distintos que contêm as capabilities do combo
novelty      = 1 se combo ∉ SUCCESSOR_BANK, 0 senão
centrality   = nº de capabilities centrais (≥2 módulos) no combo
```

## 4. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | Bank: Gap+Trajectory+AutoEvolve → Potential Discovery Engine |
| CA2 | Bank: CrossValidation+Polymorphic+Trajectory → Scientific Discovery Engine |
| CA3 | Bank: Noological+Trajectory+CrossValidation → Cognitive Manifold Mapper |
| CA4 | Geração produz hipóteses combinatorias (pares/trios) de módulos distintos |
| CA5 | Gerados não duplicam bank (novelty=1) |
| CA6 | Determinismo entre execuções; ranking por score desc |
| CA7 | Anti-overclaim: módulo/relatório sem `superhuman`, `verificad[oa]s?`, `qualis a1`, `superação` |
| CA8 | Documentação do algoritmo |
| CA9 | max_combos limitado; relatório sem candidatas → vazio sem erro |

## 5. Entregáveis

- `scanners/successor_generator.py` — `SuccessorHypothesis`, `SuccessorsReport`,
  `SuccessorGenerator`
- `tests/test_r492_successor_generator.py`
- ciclo R492 + commit; THIRD_PARTY_NOTICES (feynman-tutor já registrado R489)

## 6. Prontidão

- `pytest tests/test_r492_successor_generator.py` verde; regressões R483-R491
  verdes