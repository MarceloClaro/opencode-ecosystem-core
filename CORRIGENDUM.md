# Corrigendum

Documento público e vivo de autocorreção de alegações do próprio projeto.
Prática adotada a partir do R110 (SPEC-935-R110), inspirada no
`CORRIGENDUM.md` do projeto original `OpenCode_Ecosystem`, e alinhada com a
política anti-overclaim já codificada em `mci/metacognitive_evaluator.py`
(SPEC-920): `classify_metacognitive_tier()` nunca retorna um tier
"verified" sem `external_validation=True` explícito. Este documento aplica
o mesmo princípio à documentação em prosa (README/ARCHITECTURE), que não
passa por nenhum gate automático equivalente.

Cada entrada abaixo identifica uma alegação encontrada na documentação
atual que soa mais forte do que o que está de fato verificado, e propõe a
leitura correta. Nenhuma entrada aqui significa que o recurso é falso —
significa que a forma como está anunciado precisa de contexto para não
induzir a uma conclusão que o projeto não pode sustentar sozinho.

---

## 1. Tabela comparativa vs. frameworks externos (README.md, linhas ~991-1000)

**Alegação:** uma tabela dá a este projeto ⭐⭐⭐⭐⭐ (nota máxima) em **todas
as 7 categorias** comparadas contra LangGraph, CrewAI, AutoGen e MetaGPT.

**Por que é um overclaim:** as notas são auto-atribuídas pelo próprio
projeto, sem metodologia de benchmark, sem os frameworks concorrentes
terem sido executados nas mesmas tarefas, e sem nenhuma fonte externa
citada. Uma comparação em que o autor se dá nota máxima em 100% das
categorias contra projetos maduros e amplamente adotados é, por
construção, não confiável como comparação objetiva.

**Leitura correta:** a tabela descreve *quais recursos este projeto
implementa* (pipeline científico fechado, roteamento por atenção
multi-cabeça, staking/slashing, etc.), não uma avaliação de qualidade
comparativa validada externamente. Nenhuma estrela nesta tabela deve ser
lida como resultado de benchmark.

## 2. "Qualis A1" como rótulo do pipeline (README.md linha 925, ARCHITECTURE.md, MASWOS)

**Alegação:** o pipeline MASWOS e o pacote `su_submission` são descritos
como produzindo trabalho de nível "Qualis A1" — um estrato real do
sistema brasileiro de avaliação de periódicos (CAPES), atribuído por um
processo de avaliação externo e institucional.

**Por que é um overclaim:** "Qualis A1" não é uma característica que um
pipeline de software possa se autoatribuir — é uma classificação que a
CAPES aplica a *periódicos*, não a manuscritos ou pipelines. Nenhum artigo
produzido por este ecossistema foi submetido, avaliado ou aceito por um
periódico Qualis A1 até o momento deste documento.

**Leitura correta:** "MASWOS Qualis A1" descreve o **padrão de rubrica
interno** que o pipeline usa como meta de qualidade (16 estágios + gate
AUTO_SCORE), não uma certificação obtida. Sugerimos ler como "MASWOS
(meta: padrão Qualis A1)" até que exista validação externa (aceite real
em periódico).

## 3. "Score médio: 9.4/10" e "Ciclos de evolução: 65+" (README.md, ARCHITECTURE.md)

**Alegação:** o README exibe "Score médio: 9.4/10" com destaque, ao lado
de métricas objetivas como contagem de testes.

**Por que é um overclaim:** esse número é a média aritmética das notas que
os próprios ciclos de evolução se atribuem (`evolution/cycles.json`,
`EvolutionRegistry.average_score()`) — inclusive as notas 9.3 e 9.2 dos
ciclos R108 e R109 foram atribuídas pelo mesmo agente que implementou o
código correspondente. Não é uma avaliação de terceiros, nem um benchmark,
nem uma revisão por pares.

**Leitura correta:** "Score médio" é uma métrica de **autoavaliação
interna e qualitativa** por ciclo (documentada em `evolution/evo-*.md`),
útil para rastrear tendência ao longo do tempo, não uma nota de qualidade
objetiva ou validada externamente.

## 4. "160+ agentes especializados" (README.md, badge e diagrama)

**Alegação:** o projeto anuncia um catálogo de "160+ agentes
especializados" de forma proeminente (badge, subtítulo, diagrama).

**Contexto que falta:** o número é real — `orch.catalog_size` carrega
efetivamente 160 `AgentCard`s de `agents/catalog/*.md` — mas a
documentação não esclarece que a maioria desses agentes é **heurística/
baseada em regras Python**, não um agente com um LLM próprio sempre ativo,
e que "registrado no catálogo" significa elegível para ser escolhido pelo
roteador de atenção quando uma tarefa combina com suas capacidades
declaradas — não 160 processos rodando simultaneamente.

**Leitura correta:** "160+ agent cards registrados e elegíveis para
delegação via Blackboard", não "160+ agentes de IA ativos".

## 5. Nomenclatura "Superhuman" (SPEC-918, SPEC-920, `Bench[Superhuman Readiness]`)

**Status:** este item já está coberto pela política existente. O próprio
`mci/metacognitive_evaluator.py::classify_metacognitive_tier()` nunca
retorna `metacognitive_superhuman_verified` sem `external_validation=True`
explícito, e a suíte de testes (`no_verified_without_external`) garante
isso programaticamente. Mantemos a entrada aqui só para deixar registrado
que a mesma cautela **não** se estende automaticamente ao texto solto do
README/ARCHITECTURE fora do módulo — os itens 1-4 acima são exatamente os
lugares onde a prosa ficou mais confiante do que o código garante.

## 6. "Nível N3.5 de consciência operacional" (materiais de divulgação externos)

**Alegação:** um resumo de capacidades divulgado descreve o Trust Engine
como operando em um "Nível 3.5 de consciência operacional (N3 completo +
barreira preventiva)".

**Por que é um overclaim:** não existe, em nenhuma spec ou módulo deste
repositório, uma escala numerada de "níveis de consciência operacional"
(N1, N2, N3, N3.5...). O R112 (SPEC-935-R112) implementou o núcleo real
por trás da alegação — um `GoalDriftDetector` real em
`trust/trust_engine.py` que detecta desvio de objetivo por sobreposição
lexical em janela deslizante — mas deliberadamente **não** adotou a
numeração "N3.5", por não haver nenhuma definição operacional do que
distingue um "nível 3" de um "nível 3.5" em lugar nenhum do projeto.

**Leitura correta:** "detecção heurística de desvio de objetivo (goal
drift) via sobreposição lexical", não um "nível de consciência" numerado.

## 7. "Liquid Swarm Architecture (N4.0)" (materiais de divulgação externos)

**Alegação:** agentes seriam "sintetizados em runtime" e "evaporariam
após a execução" — um pool dinâmico em vez de um catálogo estático.

**Por que é um overclaim:** contradiz diretamente a arquitetura real.
Os agentes deste ecossistema são `AgentCard`s pré-catalogados
estaticamente em `agents/catalog/*.md` (ver também item 4 acima) e
carregados uma vez na inicialização do orquestrador — não há síntese de
agente em tempo de execução nem descarte pós-tarefa. Implementar essa
alegação de verdade exigiria uma mudança arquitetural de alto risco
(geração dinâmica de agentes por LLM em runtime); decidimos não simular
isso superficialmente só para "fechar" a alegação.

**Leitura correta:** catálogo estático de agent cards elegíveis para
delegação via Blackboard — não síntese/evaporação dinâmica de agentes.

## 8. "RUMI" (descoberta causal) (materiais de divulgação externos)

**Alegação:** o projeto integraria um "motor de descoberta causal (RUMI)".

**Por que é um overclaim:** nenhuma especificação do repositório define
o algoritmo, a entrada/saída ou o comportamento esperado de "RUMI" — é um
nome citado sem substância correspondente. A necessidade que a alegação
sugere (descoberta causal, geração de hipóteses) já é coberta
substancialmente por `agentic_science_v2` (EvoSci) e `mci/oqs/` (Optimal
Question Scanner), que são reais e testados.

**Leitura correta:** descoberta de hipóteses e geração de perguntas de
pesquisa cobertas por EvoSci + OQS — "RUMI" não é um componente deste
projeto.

---

## Como este documento é mantido

- `MarceloClaroOrchestrator.doctor()` (`marceloclaro/doctor.py`) verifica
  a presença deste arquivo como parte do diagnóstico de saúde do
  ecossistema — sua ausência gera um aviso (`warn`), não uma falha.
- Novas entradas devem ser adicionadas sempre que uma alegação em prosa
  (README, ARCHITECTURE, badges) for identificada como mais forte do que
  o que o código/dados realmente sustentam — não é preciso esperar uma
  auditoria formal para registrar uma correção aqui.
- Este documento não substitui a correção do texto original quando
  viável; ver referências cruzadas adicionadas em `README.md` e
  `ARCHITECTURE.md` junto às métricas citadas.
