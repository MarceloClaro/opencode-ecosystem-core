# R110 — Doctor (Diagnóstico de Saúde) + Prática de CORRIGENDUM

## Objetivo

Portar dois elementos de valor residual identificados numa auditoria do
projeto original `OpenCode_Ecosystem` (já majoritariamente esgotado por
portagens anteriores): um comando de health-check estrutural rápido
(`doctor`) e a prática de `CORRIGENDUM.md` — documento público de
autocorreção de alegações do próprio projeto.

## Mudanças Entregues

1. **`marceloclaro/doctor.py` — diagnóstico estrutural rápido**
   - `run_doctor()`: 6 checks em menos de 5 segundos (specs formais,
     registro de evolução, loop specs, memória metacognitiva,
     `opencode.json`, presença do `CORRIGENDUM.md`)
   - O check de `evolution_registry` compara a contagem bruta do JSON em
     disco vs. a contagem carregada pelo `EvolutionRegistry` — detecção
     proativa do mesmo tipo de bug de perda silenciosa de dados corrigido
     no R108
   - `MarceloClaroOrchestrator.doctor()`: agrega `catalog_agents` e
     `trust_status` ao relatório, registra reflexão na memória
     metacognitiva global
   - `python3 -m marceloclaro.cli doctor` (novo comando direto, exit code
     não-zero se `unhealthy`) e item `[6]` no menu interativo

2. **`CORRIGENDUM.md` — prática de autocorreção pública**
   - 5 alegações identificadas via auditoria da documentação atual:
     1. Tabela comparativa (README.md) que dá nota máxima (⭐⭐⭐⭐⭐) em
        **100% das 7 categorias** contra LangGraph/CrewAI/AutoGen/MetaGPT,
        sem metodologia de benchmark
     2. Rótulo "Qualis A1" aplicado ao pipeline MASWOS — uma
        classificação real da CAPES para periódicos, não algo que um
        pipeline de software possa se autoatribuir
     3. "Score médio: 9.4/10" apresentado como métrica objetiva quando é
        a média das autoavaliações de cada ciclo de evolução (inclusive
        as notas que os próprios agentes implementadores se deram)
     4. "160+ agentes especializados" sem esclarecer que são agent cards
        elegíveis para delegação via Blackboard, não processos de IA
        sempre ativos
     5. Nomenclatura "Superhuman" — já coberta pela política existente em
        `mci/metacognitive_evaluator.py` (SPEC-920), registrada aqui só
        para deixar claro que essa cautela não se estendia à prosa solta
   - Referências cruzadas leves adicionadas em `README.md` e
     `ARCHITECTURE.md`, junto às métricas/tabelas identificadas, sem
     reescrever a cópia de marketing inteira

3. **Cobertura de testes**
   - `tests/test_r110_doctor_corrigendum.py` (13 testes): forma do
     relatório, velocidade (<5s), detecção de perda silenciosa de ciclos
     (cenário controlado), detecção de loop spec mal-formado, JSON
     inválido do `opencode.json`, ausência/presença do
     `CORRIGENDUM.md`, `MarceloClaroOrchestrator.doctor()`, e
     presença/conteúdo do próprio `CORRIGENDUM.md`

## Verificação

- `python3 -m pytest tests/test_r110_doctor_corrigendum.py -v` → **13 passed**
- `python3 -m marceloclaro.cli doctor` → relatório JSON estruturado,
  exit code 0 (estado `degraded`/`healthy` conforme presença do
  `CORRIGENDUM.md` no momento da execução)

## Lições

1. Uma auditoria do projeto que originalmente inspirou o core mostrou que
   a maior parte do valor já tinha sido portada em ciclos anteriores — o
   residual real (doctor + corrigendum) era pequeno, mas genuíno, e
   valeu a auditoria mesmo assim.
2. A política anti-overclaim já existente no código (SPEC-920,
   `classify_metacognitive_tier`) nunca tinha sido estendida à prosa
   solta do README/ARCHITECTURE — uma tabela comparativa com nota máxima
   auto-atribuída em 100% das categorias contra frameworks externos reais
   é exatamente o tipo de alegação que o próprio código do projeto já
   sabe evitar.
3. Singletons globais (`LoopSpecRegistry`, `MetaBus.memory`) exigem
   isolamento explícito em testes que registram specs/loops de teste —
   mesmo cuidado já identificado nos ciclos R108/R109, reincidiu aqui e
   foi corrigido do mesmo jeito (fixture autouse que snapshot/restaura).

## Score

**9.1/10**

- Fecha o loop da auditoria do projeto original com um resultado
  concreto e testado, não apenas documentado
- Estende a disciplina anti-overclaim já existente no código para a
  documentação em prosa, com evidência concreta (5 alegações reais
  encontradas, não hipotéticas)
- Zero regressões nos ciclos R101-R109
- Não alega nenhuma automação ou correção retroativa completa da
  documentação — é um primeiro passo, registrado como tal
