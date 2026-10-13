---
spec_id: SPEC-935-R826
title: Alocação positiva e conservação de páginas no NanoPlanner
status: implemented
component: nano_orchestration/planner.py
test_file: tests/test_r826_nano_positive_allocation.py
---

# R826 — Planejamento de páginas sem seções negativas

## Falha reproduzida

O preview de duas páginas mantinha seis seções, destinava -3 páginas à
conclusão e declarava plano válido com nota 10. A construção pulava as páginas
negativas, mas conservava o nome da seção omitida; a validação não examinava
nem a alocação nem a cobertura das seções.

## Contrato

1. Páginas e parâmetros de discretização são inteiros positivos; recusar zero,
   negativos, booleanos, floats, NaN, infinitos e texto antes de criar blocos.
2. Cada seção tem nome não vazio e único e recebe pelo menos uma página.
   `total_pages` explícito deve corresponder à soma, sem ajuste silencioso.
3. O preview padrão conserva suas seis seções e exige pelo menos seis páginas.
   Para totais de uma a cinco páginas, o chamador fornece uma lista explícita
   de seções compatível. Recusar orçamento inferior ao número de seções.
4. Distribuir páginas inteiras de forma determinística, com mínimo de uma por
   seção e soma exata. Os seis nomes padrão usam seus pesos históricos;
   listas de outro tamanho usam pesos iguais. Nenhuma seção é descartada.
5. Persistir alocação e densidade de blocos nos metadados do plano. Validar
   positividade, soma, cobertura e contadores, sem atribuir sucesso a um plano
   vazio ou inconsistente. Antes de alocar, recusar mais de 50.000 blocos.
6. Planos legados sem alocação persistida conservam validação estrutural, com
   escopo e aviso explícitos: não afirmar que a alocação desconhecida foi
   verificada. Metadados disponíveis, mesmo em plano legado, devem ser válidos.
7. O contrato é computacional. Páginas, linhas e tokens são estimativas, não
   certificados de extensão final, qualidade científica ou inferência real.
8. Validar planos restaurados pelo consumidor `NanoOrchestrator.load_checkpoint`
   conserva os valores de tipos de bloco serializados como texto no JSON,
   sem fabricar nem apagar a alocação ausente de checkpoints legados.

## Aceitação

RED/GREEN de entradas inválidas, padrão insuficiente, previews curtos explícitos,
distribuições com soma exata, metadados adulterados, plano vazio e compatibilidade
de checkpoint. Regressões do pacote Nano completas e consumidor NanoOrchestrator
sem alterar seus testes históricos. Evidências em `outputs/core-r826/`.
