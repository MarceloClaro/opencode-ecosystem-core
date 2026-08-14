---
spec_id: SPEC-935-R409
title: Artigo publicável (candidato a submissão) com rigor auditável e validações cruzadas agrupadas
component: academic/papers/arm_education_audit
status: in_progress
test_file: tests/test_r409_artigo_publicavel.py
---

# SPEC-935-R409 — Artigo publicável (candidato a submissão) com rigor auditável

**Data:** 2026-08-12
**Pedido:** "gere um artigo publicável com rigor Qualis A1 com a mesma pesquisa
real e auditável e com validações cruzadas."

## 1. Enquadramento epistêmico (herdado da SPEC-935-R408)

1. "Qualis" classifica **veículos/periódicos**, não manuscritos. Nenhuma saída
   será denominada "artigo Qualis A1" ou "pronta para publicação" sem revisão
   humana, aderência ao periódico escolhido e avaliação por pares. O entregável
   é uma **versão candidata a submissão**.
2. Todo número citado no manuscrito é gerado por script a partir do painel WDI
   auditado (R408, cache com SHA-256) e tem entrada na proveniência numérica.
3. Linguagem estritamente associativa: termos causais ("causa", "efeito
   causal", "causalidade", "impulsiona"), absolutos ("condição necessária"),
   de overclaim ("validado", "inédito") e os resultados false-positive da
   versão original (d=16,06; AUC 0,997; percentil individual) são proibidos no
   texto final.
4. Validações cruzadas legítimas e **sem vazamento**:
   - leave-one-country-out (folds de treino e teste disjuntos por país);
   - bloqueio temporal (anos de treino anteriores aos de teste);
   - aprendizado de máquina com split agrupado por país, comparado ao split por
     linha — a queda é declarada como não identificabilidade com 7 países
     (resultado negativo, não ocultado).
5. Referências do artigo são subconjunto das 33 obras únicas auditadas no R408,
   com DOI ou URL oficial.

## 2. Critérios de aceitação

1. `ARTIGO_PUBLICAVEL.md` existe com estrutura científica completa: Resumo,
   Abstract, Palavras-chave, Introdução, Método, Resultados, Discussão,
   Conclusão, Referências.
2. O artigo se rotula explicitamente como "candidato(a) a submissão" e
   condiciona a publicação à revisão por pares.
3. Nenhum termo da lista bloqueada (R408 + R409) aparece no texto:
   Qualis A1, validado(a), inédito(a), condição necessária, d = 16,06 / 16,06,
   AUC, 0,997, percentil, prova, causalidade/efeito causal/causa.
4. Cada número decimal citado no Resumo tem correspondência na
   `provenance.json` (tolerância 0,005), incluindo valores dentro de listas.
5. LOOCV: `loocv_folds.json` tem ≥ 7 folds com treino/teste disjuntos e um
   único país de teste por fold.
6. Bloqueio temporal: `temporal_blocks.json` tem ≥ 2 blocos com
   `treino_max < teste_min`.
7. ML: `ml_resultados.json` reporta AUC com split por linha e AUC agrupado por
   país; o agrupado é < 0,75 e claramente inferior ao por linha (diferença
   > 0,10), declarando não identificabilidade entre países.
8. Painel com efeitos fixos: `painel_efeitos_fixos.json` reporta coeficiente,
   IC95% com `ic_inf <= coef <= ic_sup`, n, nº de países e lag (5 anos).
9. Referências: ≥ 8 entradas no formato ABNT (sobrenome, N.; ... Ano.) com
   DOI/URL, subconjunto das 33 obras auditadas.
10. Todos os testes em `tests/test_r409_artigo_publicavel.py` passam (GREEN);
    testes R408 permanecem GREEN.

## 3. Não-objetivos

- Não fabricar significância: os resultados negativos (queda em primeiras
  diferenças, AUC agrupado ≈ 0,59) são reportados como achados.
- Não emitir parecer editorial de aceite nem sugerir periódico-alvo específico
  como garantia de publicação.
- Não usar dados fora do painel auditado (Barro-Lee e PISA permanecem fora
  porque sem snapshot com hash no R408).

## 4. Verificação

```bash
python3 -m pytest tests/test_r409_artigo_publicavel.py -q   # 32 testes
python3 -m pytest tests/test_r408_arm_article_audit.py -q   # permanece 34/34
python3 -m marceloclaro.cli doctor                          # 10/12, 0 falhas
```
