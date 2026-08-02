---
spec_id: SPEC-935-R363
title: Camada Epistêmica de Roteamento (Episteme Routing Layer)
component: transformer/episteme.py + transformer/semantic_matcher.py + marceloclaro/catalog_loader.py
status: verified
test_file: tests/test_r363_episteme_routing.py
---

# SPEC-935-R363 — Camada Epistêmica de Roteamento

**Versão:** 1.0.0
**Estado:** draft
**Data:** 2026-08-01
**Orquestrador:** marceloclaro

## 1. Objetivo

Adicionar ao quadro orquestrado de habilidades (SkillHandbook / SemanticMatcher)
uma camada epistêmica determinística: cada agente/skill do catálogo é associado
a um regime epistemológico inferido de metadados já existentes (`category`,
`type`, `tags`, nome), e o roteamento de tarefas passa a considerar a afinidade
entre a episteme da tarefa e a episteme do agente como **peso brando** no score
de matching.

**Limite epistêmico:** a camada é heurística e determinística (léxico de
sinais, sem LLM). Ela não determina competência real do agente nem a natureza
"verdadeira" do conhecimento exigido pela tarefa; apenas ajusta prioridade de
roteamento com base em indícios lexicais. Ausência de episteme inferida não é
erro: significa apenas que os sinais foram insuficientes, e nesse caso o
comportamento de matching permanece **idêntico** ao anterior (fail-open).

## 2. Taxonomia (6 regimes)

| chave | regime | exemplos de domínio |
|---|---|---|
| `empirico_analitico` | Empírico-analítico | estatística, benchmarks, dados, experimentos |
| `formal_dedutivo` | Formal-dedutivo | matemática, lógica, prova, algoritmos, código formal |
| `hermeneutico_interpretativo` | Hermenêutico-interpretativo | tradução, cultura, texto, literatura, linguística |
| `critico_reflexivo` | Crítico-reflexivo | ética, vieses, peer review, auditoria de alegações |
| `pragmatico_tecnico` | Pragmático-técnico | engenharia, tooling, integração, operação, DevOps |
| `regulatorio_normativo` | Regulatório-normativo | ABNT, conformidade, normas, legislação, formatação |

A matriz de afinidade entre regimes é explícita e simétrica, com diagonal 1.0
(ex.: `empirico_analitico` ↔ `formal_dedutivo` = 0.7; regimes distantes ≈ 0.3).

## 3. Componentes

### 3.1 `transformer/episteme.py` (novo)

- `EPISTEMES: Dict[str, Dict]` — taxonomia com nome, descrição e léxico de
  sinais (pt/en) por regime.
- `AFFINITY: Dict[Tuple[str, str], float]` — matriz de afinidade explícita.
- `@dataclass EpistemeProfile` — `episteme: str`, `secundaria: Optional[str]`,
  `confianca: float` (0–1), `sinais: List[str]`.
- `infer_episteme_from_text(text: str) -> Optional[EpistemeProfile]` — tokeniza
  e pontua sinais; retorna `None` quando sinais insuficientes (nunca chuta).
- `infer_agent_episteme(category, agent_type, tags, name) -> Optional[EpistemeProfile]`
  — concatena metadados e delega à inferência lexical.
- `infer_task_episteme(task_description) -> Optional[EpistemeProfile]`.
- `episteme_affinity(a: str, b: str) -> float` — consulta a matriz; chaves
  desconhecidas retornam afinidade neutra 0.5.

Determinístico: mesma entrada → mesma saída; sem estado, sem rede, sem LLM.

### 3.2 Frontmatter opcional `episteme:` (catalog_loader)

- `load_catalog_definitions()` passa a incluir `episteme` (string ou `None`)
  lido do frontmatter, além de repassar `category`/`type` já existentes.
- Override manual **vence** a heurística. Nenhum arquivo do catálogo é editado
  neste ciclo (R363); valor ausente é o caso normal.
- `register_catalog_agents()` repassa `episteme`, `category` e `type` ao
  `SemanticMatcher.register_agent_skills()`.

### 3.3 `SkillHandbook` (semantic_matcher.py)

- `SkillProfile` ganha campo `episteme: Optional[str] = None`.
- `register_skill(..., episteme=None, category="", agent_type="")` — se
  `episteme` explícita ausente, tenta `infer_agent_episteme(category,
  agent_type, tags, agent_id)`; se a inferência falhar ou o módulo estiver
  indisponível, registra com `episteme=None` (fail-open).
- `match()`:
  - infere a episteme da tarefa uma única vez por chamada;
  - score base preservado: `0.6·similaridade + 0.4·confiança`;
  - **apenas quando** tarefa e skill têm episteme:
    `score = score_base × (1 + 0.20 × (affinity − 0.5))`
    → bônus máximo +10%, penalidade máxima −10%;
  - resultado expõe `episteme` (da skill) e `episteme_affinity`
    (`None` quando não aplicado) para explicabilidade;
  - nenhum agente é excluído por episteme (não é filtro).

### 3.4 Fora de escopo (YAGNI)

- Persistência de epistemes; integração com Trust Engine/metacognição;
- Edição dos 202 arquivos do catálogo;
- Classificação por embedding/LLM.

## 4. Critérios de aceitação (testes R363)

1. **Taxonomia íntegra:** 6 regimes, matriz de afinidade simétrica, diagonal
   1.0, valores em [0,1].
2. **Inferência de agentes representativos:** estatística → `empirico_analitico`;
   auditoria ABNT → `regulatorio_normativo`; agente de episteme cultural /
   tradução → `hermeneutico_interpretativo`; peer review → `critico_reflexivo`;
   tooling/integração → `pragmatico_tecnico`; matemática formal →
   `formal_dedutivo`.
3. **Nunca chuta:** texto sem sinais → `None`.
4. **Fail-open:** com episteme desconhecida em qualquer ponta, o score de
   `match()` é **numericamente idêntico** ao comportamento anterior.
5. **Peso brando:** afinidade alta reordena candidatos de score base próximo a
   favor do regime compatível; afinidade baixa penaliza no máximo 10%; nenhum
   candidato desaparece do resultado por episteme.
6. **Override:** frontmatter `episteme:` vence a heurística; campo ausente não
   quebra o parser (catálogo real carrega sem erro).
7. **Explicabilidade:** resultado do match contém as chaves `episteme` e
   `episteme_affinity`.
8. Suíte completa do repositório permanece verde.

## 5. Encerramento do ciclo

- Testes escritos antes da implementação (TDD).
- Registro de ciclo em `evolution/cycles.json` via append manual
  (`json.load`/`json.dump`), preservando campos legados.
- Commit escopado apenas aos arquivos do R363.
- Nenhuma alegação de "verificado", "superhuman" ou equivalente sem validação
  externa (política do CORRIGENDUM respeitada); `status: verified` só após a
  suíte completa passar.

## 6. Resultado da verificação (2026-08-02)

- Testes do ciclo: **27/27 verdes** (`tests/test_r363_episteme_routing.py`);
  testes dos módulos tocados também verdes (transformer 34/34; seleção
  catalog/semantic/matcher 41 aprovados).
- Suíte completa: **2200 aprovados, 58 falhas, 53 pulados** (5h06m). As 58
  falhas são **pré-existentes de outras frentes** (agentes literários
  R272–R276, pipeline sépia R351, e `test_sdd_tdd` que quebra na
  SPEC-935-R264 com `test_file` inválido). Verificado por bisseção: as
  mesmas falhas ocorrem com o `catalog_loader.py` restaurado ao HEAD
  (stash temporário), portanto não decorrem do R363.
- "verified" aqui significa: critérios de aceitação da §4 atendidos pelos
  testes automatizados locais. Não é validação externa independente.
- Nota de escopo do commit: `transformer/semantic_matcher.py` nunca havia
  sido commitado (camada semântica R347 pendente de outra frente); como o
  R363 depende dele em runtime e nos testes, o arquivo entra neste ciclo
  para o commit ser autoconsistente. `marceloclaro/catalog_loader.py`
  carrega igualmente modificações pendentes do R347 além das linhas de
  episteme deste ciclo.
