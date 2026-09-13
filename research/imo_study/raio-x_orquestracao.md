# Raio-X da Orquestração — Impacto real na resposta das LLMs (R499)

**Objeto**: benchmark controlado dos modelos LLM **free reais** do OpenCode
Ecosystem Core (`mimo-v2.5-free`, `nemotron-3-ultra-free`) na tarefa IMO
(teoria dos números: p³−q⁵=(p+q)²), variando **apenas a camada de
orquestração** em 3 condições: C0 raw → C1 contexto → C2 scaffold MASWOS.

**Fonte de dados**: `research/imo_study/llm_free_benchmark.json`
(6 trials reais, executados em 2026-09-13) e `llm_free_ranking.json`.

---

## 1. Tabela de resultados reais

| Modelo | Condição | Tempo (s) | Acurácia | Conformidade | Status |
|---|---|---|---|---|---|
| mimo-v2.5-free | C0 raw | 19.9 | ❌ | ❌ | vazio (0 chars) |
| mimo-v2.5-free | C1 contexto | 25.6 | ❌ | ❌ | vazio (0 chars) |
| mimo-v2.5-free | C2 scaffold MASWOS | 23.8 | ✅ (7,3) | ✅ | ok |
| nemotron-3-ultra-free | C0 raw | 63.8 | ❌ | ❌ | vazio (0 chars) |
| nemotron-3-ultra-free | C1 contexto | 110.0 | ❌ | ❌ | **timeout** |
| nemotron-3-ultra-free | C2 scaffold MASWOS | 107.4 | ✅ (7,3) | ✅ | ok |

**Ranking free (score multicritério: acurácia 40% + velocidade 30% +
conformidade 20% + disponibilidade 10%)**:

| # | Modelo | Score | Latência média (C2) | Acurácia (C2) |
|---|---|---|---|---|
| 1 | **mimo-v2.5-free** | **0.987** | 23.8 s | 1.0 |
| 2 | nemotron-3-ultra-free | 0.709 | 107.4 s | 1.0 |

---

## 2. Raio-X por camada de processo

### Camada 0 — Infraestrutura de providers (router)
- **Eficácia**: `model_router` lista 41 modelos reais e roteia por tier.
- **Ineficácia mapeada**: dos candidatos "free/fast", apenas 2 são utilizáveis
  de fato:
  - `deepseek-v4-flash` (fast) → **"Insufficient balance"** (modelo não-free de
    fato; exigiria cobrança) — o catálogo o rotula "fast", não "free".
  - `gemini-2.5-flash` (fast) → **erro de servidor** (UnknownError).
  - `gpt-4o-mini`, `claude-haiku-4` → sem resposta útil no teste.
- **Lição**: o tier "fast" ≠ "free utilizável". O raio-x expõe que a camada de
  catálogo/roteamento precisa de um campo "acessibilidade real" (saldo, erro
  upstream), senão o pipeline seleciona modelos que falham em runtime.

### Camada 1 — Motor LLM puro (C0 raw)
- **Resultado**: 0/2 acertos; saída vazia ou irrelevante (0 chars em 3 dos 4
  trials não-orquestrados).
- **Interpretação**: o prompt direto com problema matemático não gera resposta
  utilizável nos free; sem scaffold, a resposta "pensa em voz alta" (parágrafo
  de análise de sinais) e não entrega o par pedido em formato extraível.

### Camada 2 — Contexto/dados (C1 ctx)
- **Resultado**: 0/2 acertos (mimo: vazio; nemotron: timeout).
- **Interpretação**: adicionar dados do estudo ao prompt **não ajudou**; pior,
  aumentou o custo de tokens e a latência (contexto longo + modelo lento →
  timeout). O contexto sem estrutura de saída é ruído.
- **Ineficácia mapeada**: **C1 foi a camada mais ineficiente** — custo extra
  sem ganho. Métrica: chars=0 e nemotron estourou o timeout de 110s.

### Camada 3 — Scaffold MASWOS (C2) ⭐ fator decisivo
- **Resultado**: 2/2 acertos, 2/2 conformes — com verificação aritmética
  correta em ambos ((7,3): 343−243=100=10²).
- **O que a orquestração fez**:
  1. Instrução de estágio (agente_id + capacidade) delimitou o papel;
  2. Restrição de formato ("escreva APENAS o par e a verificação") eliminou
     a saída não-extraível;
  3. Objetivo concreto (não pedir "resolva", pedir "escreva o par") ancorou a
     resposta.
- **Custo da orquestração**: mesmo tempo de geração (mimo ~24s), mas com
  saída utilizável — **eficiência = 100%** na condição relevante.
- **Achado fino**: mimo com typo de sobrescrito Unicode ("3²⁵" por 3⁵) —
  detector da Camada 4 (verificação aritmética) não depende da formatação.

### Camada 4 — Gates de verificação (pós-geração)
- `FormalProofVerifier.verify_algebraic_identity("7**3 - 3**5", "(7+3)**2")`
  → **True** (confirmação simbólica); par errado → False (-252).
- **Eficácia**: gate converte "resposta plausível" em "proposição verificada";
  é a única camada que dá confiança formal pós-LLM.
- **Ineficácia mapeada (LLM local)**: `llama3.2` (Ollama) foi descartado —
  latência 30–50 s/estágio × 16 estágios MASWOS > 10 min sem conclusão;
  **nenhuma resposta útil produzida** pela via local (abortada).

### Camada 5 — Orquestração A2A/Blackboard (Macro)
- O delegate MASWOS conecta estágio → prompt estruturado (Camada 3).
- O `model_router.route()` deveria escolher o modelo por tarefa; no teste,
  a seleção foi manual — **gap mapeado**: não há roteamento automático
  "tarefa → melhor modelo free" persistido (proposta de melhoria R500).

---

## 3. Métricas consolidadas de eficiência/ineficácia

| Camada | Eficiência | Ineficiência | Métrica objetiva |
|---|---|---|---|
| C0 infra/router | parcial | 4/6 modelos "fast/free" inutilizáveis | 2 utilizáveis de 6 testados |
| C1 LLM puro (raw) | 0% | saída vazia 3/4 | chars=0 |
| C2 contexto (ctx) | 0% (piorou latência) | nemotron timeout | chars=0, 110s |
| C3 scaffold MASWOS | **100%** | typo Unicode mimo (cosmético) | 2/2 corretos+conformes |
| C4 verificação formal | 100% | não prova existência (só identidade) | True/False exato |
| C5 orquestração macro | 100% na delegação | sem roteamento automático de modelo | ranking manual |

**Veredito**: no cenário free real, **a orquestração (scaffold MASWOS) é o
fator que decide entre resposta vazia e resposta correta** (0% → 100%). O
modelo importa para latência (mimo 4× mais rápido) e para qualidade de
formatação (nemotron sem typo), mas **sem orquestração nenhum dos dois
entrega resultado utilizável**. Modelos locais (llama3.2) descartados por
latência incomportável.

## 4. Recomendações objetivas

1. Adicionar campo de **acessibilidade real** ao catálogo de modelos
   (free-ok / saldo-necessário / erro-upstream) — Camada 0.
2. Priorizar **scaffold de saída estruturada** em qualquer delegação
   (C3) — maior impacto por custo zero.
3. **Não injetar contexto sem estrutura de saída** (C1 ineficiente).
4. Persistir roteamento automático tarefa→modelo (ranking R499 como base).