# SPEC-935-R495 — Structural Compression Engine (SCE)

Status: **implementado** (R495)
Data: 2026-09-13
Requer: R494 (StructuralNoiseScanner); proposta do usuário "Proposta de
Ferramenta — Structural Compression Engine (SCE)".

## 1. Contexto (proposta do usuário)

Em textos longos o problema não é resumir — é **reduzir volume sem perda
cognitiva**. Um resumo comum pode apagar partes importantes da estrutura
argumentativa. O SCE é uma aplicação operacional do SNS (R494) que comprime
textos gigantes preservando a estrutura cognitiva essencial:

    T = P1 + P2 + ... + Pn         (fragmentação)
    SNS(Pi) = Vi                   (vetorização estrutural por parte)
    T' = ΣV                        (reconstrução global)
    Δ = Estrutura(T) − Estrutura(T')  (teste delta)

## 2. Objetivos

- **OF1** — `StructuralCompressionEngine.fragment(text, chunk_size)` divide
  texto gigante em partes (sem cortar frases no meio, stdlib).
- **OF2** — Para cada parte, aplica SNS (R494) e extrai vetores cognitivos
  (função/tese/argumento/conceito estruturante; ruído descartado).
- **OF3** — Reconstrução global: concatena estruturas preservadas de todas as
  partes em texto denso.
- **OF4** — Métricas do usuário: CR (Compression Ratio = tokens originais /
  finais), CPS (cognitive preservation score = estruturas preservadas /
  totais), FLI, DG = CPS × CR.
- **OF5** — Teste delta inicial-final: CPS alto + FLI baixo → compressão válida.

## 3. Modelo formal

```
fragment: corta em N partes respeitando fronteiras de frase (máx. chunk)
vetor(Pi) = SNS(Pi).preserved                     (estruturas preservadas)
CPS       = Σ|preserved(Pi)| / Σ|elementos(Pi)|  (equivalentes para o texto)
CR        = token_count(original) / token_count(final)
FLI       = 1 − CPS                               (funções perdidas)
DG        = CPS × CR
nível     = seguro se CPS ≥ 0.90 | moderado se CPS ≥ 0.70 | destrutivo
```

## 4. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | CR = tokens originais / tokens finais (≥ 1, texto menor) |
| CA2 | CPS = estruturas preservadas / totais (0-1) |
| CA3 | FLI = 1 − CPS; DG = CPS × CR |
| CA4 | Fragmentação respeita fronteiras de frase e não perde elementos |
| CA5 | SNS por parte preserva estruturas e remove redundância |
| CA6 | Texto final é denso e contém as funções essenciais (reconstrução) |
| CA7 | Anti-overclaim: sem `superhuman`, `verificad[oa]s?`, `qualis a1`, `superação` |
| CA8 | Documentação (CR/CPS/FLI/DG) |
| CA9 | CR alto + CPS alto → nível seguro; FLI baixo |
| CA10 | Determinismo; texto vazio → relatório vazio sem erro |
| CA11 | Corpus com repetição → CR > 1 e CPS ≥ 0.90 (compressão segura) |
| CA12 | Delta report: original/final counts + tokens economizados |

## 5. Entregáveis

- `scanners/compression_engine.py` — `SCEReport`, `StructuralCompressionEngine`
- `tests/test_r495_compression_engine.py`
- ciclo R495 + commit

## 6. Prontidão

- `pytest tests/test_r495_compression_engine.py` verde; regressões R483-R494
  verdes