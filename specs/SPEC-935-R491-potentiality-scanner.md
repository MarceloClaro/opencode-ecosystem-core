# SPEC-935-R491 — Potentiality Scanner (Scanner de Potenciais Latentes)

Status: **implementado** (R491)
Data: 2026-09-13
Requer: R483-R490; inspiração: proposta do usuário (camada Potentiality)

## 1. Contexto (proposta do usuário)

Os scanners atuais operam sobre elementos **explicitamente identificados**:
ausências, capacidades necessárias, dependências, trajetórias. O que falta é
responder: **"o que está prestes a nascer?"** — capacidades emergentes cujos
componentes estruturais já estão parcialmente presentes (ex.: o avião surgiu
da convergência de aerodinâmica + materiais + propulsão).

A proposta descreve 5 módulos; esta revisão implementa o núcleo verificável:

- **Structural DNA Extractor** — extrai o mapa de capacidades fundamentais do
  ecossistema a partir de um catálogo declarativo (módulos → capabilities).
- **Emergence Scan** — para cada candidata emergente (hipótese de latentidade),
  computa presença de componentes (cobertura), lacunas restantes, potencial de
  emergência e resistência estrutural.

## 2. Objetivos

- **OF1** — `StructuralDNA` declara módulos → capabilities e expõe
  `capabilities`, `redundant`, `central` (capacidade presente em ≥2 módulos).
- **OF2** — `PotentialityScanner.scan(dna, candidates)` avalia hipóteses de
  latentidade: cobertura ∈ [0,1] = |requires ∩ dna| / |requires|.
- **OF3** — Tiering: cobertura ≥ 0.66 → `latente-alto`; ≥ 0.34 → `emergente`;
  senão `distante`. `resistencia = 1 - cobertura`.
- **OF4** — Relatório com `missing` por candidata; determinístico; anti-overclaim.

## 3. Modelo formal

```
coverage(c)   = |requires(c) ∩ dna.capabilities| / |requires(c)|
missing(c)    = requires(c) - dna.capabilities
resistencia(c)= 1 - coverage(c)
tier(c)       = latente-alto se coverage ≥ 0.66; emergente se ≥ 0.34; distante
```

## 4. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | DNA extractor: capabilities indexadas dos módulos; central = aparecer ≥2× |
| CA2 | Candidata com 2/3 requeridos presentes → `emergente` (0.67) |
| CA3 | Candidata com 3/3 → `latente-alto` (1.0) |
| CA4 | Candidata com 0/3 → `distante` (0.0), missing completo |
| CA5 | Determinismo entre execuções |
| CA6 | Anti-overclaim: módulo/relatório sem `superhuman`, `verificad[oa]s?`, `qualis a1`, `superação` |
| CA7 | Documentação do algoritmo |
| CA8 | Relatório vazio sem candidatas; sem erro |

## 5. Entregáveis

- `scanners/potentiality_scanner.py` — `StructuralDNA`, `PotentialityCandidate`,
  `PotentialityReport`, `PotentialityScanner`
- `tests/test_r491_potentiality_scanner.py`
- ciclo R491 + commit

## 6. Prontidão

- `pytest tests/test_r491_potentiality_scanner.py` verde; regressões R483-R490
  verdes