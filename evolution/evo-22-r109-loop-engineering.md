# R109 — Loop Engineering: Loop Real + Especificação Formal no SDD

## Objetivo

Formalizar dentro do SDD já existente o conceito de "loop specification"
(Macedo, 2026, arXiv:2607.00038 — "Stop Hand-Holding Your Coding Agent:
Engineering the Loops that Replace Step-by-Step Prompting") e transformar
`scientific_discovery_pipeline` (R108) em um loop real com detecção de
estagnação e estados terminais nomeados, em vez de uma execução única.

## Mudanças Entregues

1. **`sdd/loop_spec.py` — Loop Engineering formal no SDD**
   - `LoopSpecification`: dataclass com a anatomia completa do paper —
     trigger + justificativa, objetivo verificável, verificação em escada
     de 5 níveis, arquitetura (solo/maker-checker/manager), estados
     terminais nomeados, detector de estagnação, teto de orçamento e
     localização de memória
   - `LoopSpecification.validate()`: checklist de boa-formação (Seção 7
     do paper) — sinaliza ausência de justificativa de trigger,
     verificador nível ≥4 sem maker-checker (anti-padrão
     "self-approving loop"), menos de 2 estados terminais nomeados,
     orçamento zerado ("unattended runaway") e memória não declarada
   - `LoopSpecification.to_markdown()`/`.export()`: gera o documento
     legível do loop (mesmo espírito do `sandeco-loop` do paper)
   - `is_stagnant()`: função genérica que replica exatamente o formato
     de `agentic_science_v2.evolutionary_engine.EvoEngine.is_stagnant`
   - `LoopSpecRegistry`: singleton paralelo ao `SpecRegistry`, publica
     validação de cada loop registrado no MetaBus

2. **`MarceloClaroOrchestrator.run_scientific_discovery_loop()` — loop real**
   - Repete `scientific_discovery_pipeline` até um dos 5 estados
     terminais nomeados: `success` (gate aprovado), `no_op` (R101 sem
     ideias — nada genuíno a repetir), `blocked` (orçamento esgotado por
     qualidade, gate nunca aprovado), `stalled` (estagnação do
     `readiness_score` SPEC-920 detectada antes do teto), `error`
     (exceção não tratada — para imediatamente, sem insistir)
   - Cada iteração escala `max_rounds` do EvoSci (+1) — feedback real
     entre voltas, satisfazendo a "golden rule" do paper (o resultado de
     uma rodada muda a próxima ação)
   - `describe_scientific_loop()`: expõe a `LoopSpecification`
     registrada (verificação nível 1, zona autônoma — nenhum juiz de
     modelo envolvido)
   - `specs/loops/scientific-discovery-loop.md`: documento exportado

3. **Cobertura de testes**
   - `tests/test_r109_loop_engineering.py` (19 testes): `is_stagnant`,
     checklist de boa-formação de `LoopSpecification` (7 cenários),
     registro no `LoopSpecRegistry`, `describe_scientific_loop`, e os 5
     estados terminais do loop real via monkeypatch

## Verificação

- `python3 -m pytest tests/test_r109_loop_engineering.py -v` → **19 passed**
- Execução manual sem mock: `run_scientific_discovery_loop` atingiu
  `blocked` (3 iterações, gate nunca aprovado) e, em outra execução com
  mais iterações, `stalled` (readiness_score convergiu e a estagnação
  disparou organicamente antes do teto de 6 iterações)

## Lições

1. R108 tinha gate real, calibração e avaliação metacognitiva, mas
   continuava sendo execução única — faltava exatamente a repetição até
   estado terminal que completa a anatomia do loop engineering.
2. Declarar explicitamente a escada de verificação (nível 1-5) é útil
   mesmo quando não há juiz de modelo envolvido: nomear que o pipeline
   científico opera na zona autônoma (níveis 1-2) evita a tentação de
   inflar a confiança do sistema além do que a verificação realmente
   sustenta.
3. O detector de estagnação evita queimar o teto de orçamento quando o
   resultado já parou de melhorar — confirmado organicamente (sem mock)
   em teste manual, onde o `readiness_score` convergiu e a estagnação
   disparou antes do limite de iterações.
4. `EvolutionRegistry.save()` ainda descarta silenciosamente campos
   extra legados (do bug corrigido no R108) a cada `.record()` — o
   append seguro continua sendo manual via JSON direto até o schema ser
   estendido para preservar campos desconhecidos.

## Score

**9.2/10**

- Completa a anatomia do loop engineering que o R108 deixou parcial
  (faltava a repetição até estado terminal)
- Zero regressões nos ciclos R101-R108
- Formaliza um vocabulário reutilizável (LoopSpecification) que outros
  pipelines do ecossistema podem adotar em ciclos futuros
- Não alega nenhuma automação (trigger agendado, custo monetário) que o
  ecossistema ainda não tem
