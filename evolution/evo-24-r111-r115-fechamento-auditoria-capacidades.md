# R111-R115 — Fechamento da Auditoria de Capacidades vs. Código Real

## Contexto

Uma auditoria comparou uma lista de ~16 "capacidades" divulgadas do
ecossistema contra o código real de `opencode-ecosystem-core`, encontrando
um padrão consistente: parte das alegações eram reais (Z3/SymPy/Kanren,
MASWOS de 16 estágios, `phd_auditor.py` com Nash/Cohen/Bonferroni), mas
várias eram jargão sem implementação (Manus Evolve, N3.5 "consciência
operacional", Liquid Swarm N4.0, Active Inference/Friston/VFE, Process
Verifier) ou apontavam para lacunas reais e corrigíveis (falta de PubMed
nas fontes de pesquisa, sem detecção de goal drift, sem detector de
falácias, "ARCHE RLT" citado mas nunca implementado, "revisão cega"
nunca de fato ocultando nada).

Este ciclo fecha as lacunas **corrigíveis com substância real**, e
deliberadamente NÃO fabrica semântica para os itens de puro jargão
(RUMI — sem algoritmo definido em nenhuma spec; Liquid Swarm N4.0 —
contradiz a arquitetura estática de agent cards existente).

## Mudanças Entregues (5 ciclos R111-R115)

1. **R111 — Fontes de pesquisa**: `research/searchers.py` de 8 para 11
   fontes (+ PubMed, bioRxiv, CORE)
2. **R112 — Goal drift**: `GoalDriftDetector` real em
   `trust/trust_engine.py`, substituindo o jargão "N3.5" por detecção
   heurística funcional e testável
3. **R113 — Falácias/vieses**: `reasoning/fallacies.py`, 15 falácias +
   4 vieses catalogados e detectáveis
4. **R114 — ARCHE RLT**: `reasoning/arche_rlt.py`, primeira
   implementação em código de `specs/legacy/SPEC-057-ARCHE-RLT.md`
   (6 tipos de Peirce, cobertura 100% dos 12 motores reais)
5. **R115 — Revisão às cegas real**: `agentic_science_v2/blind_review.py`
   integrado ao R103, anonimização real + detecção de vazamento +
   conflito de interesse afetando o gate de exportação

Ver specs individuais: `SPEC-935-R111.md` a `SPEC-935-R115.md`.

## Verificação

- `python3 -m pytest tests/ -q --tb=short` → **1223 passed, 5 skipped, 0 failed**
  (suíte completa após os 5 ciclos, antes deste registro)
- 90 testes novos ao todo (23+6+29+21+17 - alguns já existentes ampliados)

## Lições Consolidadas

1. Nem toda alegação "não encontrada" merece ser implementada — jargão
   sem definição operacional (RUMI, Liquid Swarm N4.0, "N3.5") deveria
   ser corrigido na documentação (via `CORRIGENDUM.md`), não fabricado
   em código só para "bater a lista".
2. Vale sempre checar `specs/legacy/` antes de assumir que uma alegação
   é pura invenção — SPEC-057 (ARCHE RLT) já existia, completa e
   rigorosa, há vários ciclos, só nunca foi codificada.
3. Estender contratos existentes com parâmetros opcionais (author_names
   em R115, reviewer_affiliations) é a forma mais segura de adicionar
   capacidade real sem quebrar chamadores existentes (R108/R109 continuam
   funcionando sem qualquer mudança).

## Score médio do lote

**9.0/10** — 5 lacunas reais fechadas com substância testável, zero
regressões, e duas alegações de puro jargão deliberadamente não
fabricadas (documentado, não silenciado).
