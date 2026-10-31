---
spec_id: SPEC-935-R990
title: Evolução delimitada e autoridade operacional dos scanners
component: scanners.scientific_reasoning_scanner
status: draft
test_file: tests/test_r990_scanner_evolution.py
---

# R990 — evolução dos scanners sem autoatribuição de autoridade científica

## Objetivo

Melhorar o scanner científico e seu uso pelo SuperRigorPipeline existentes.
Não declarar todos os scanners calibrados. Evolução autônoma significa medir
candidatos enumerados, identificar regressões e recomendar uma mudança; não
reescrever código, permissões, corpus de teste ou confiança autonomamente.

## Critérios de aceitação

1. O scanner científico expõe alertas com categoria, offsets do texto
   normalizado, contexto afirmativo/negado/citado/título e hash do texto de
   entrada. Preserva scores/rótulos legados e informa explicitamente seus limites.
2. Texto vazio/não informativo permite abstenção; uma citação não vira
   automaticamente afirmação do autor. Alertas citados pedem contexto, não são
   apagados. Limites de tamanho também se aplicam à API Python direta.
3. Scanner e SuperRigorPipeline declaram autoridade de triagem e ausência de
   certificação científica. Campo legado passed não autoriza publicação,
   validação externa, aumento de trust ou alterações de política.
4. Avaliação autônoma compara somente candidatos enumerados legacy/contextual;
   sem aceitar código, regex ou função fornecida pelo chamador. Corpus limitado,
   com IDs/grupos/textos não duplicados entre desenvolvimento e holdout, rótulos
   booleanos e ambas as classes em cada partição. Identifica hashes e tamanho.
5. Seleção usa exclusivamente desenvolvimento; holdout avalia o candidato
   escolhido sem escolher outro depois. Computa TP/FP/TN/FN, precisão, recall e
   acurácia balanceada; denominador zero resulta em null, não 100%.
6. Só recomenda candidato com melhoria em desenvolvimento e sem regressão de
   FP/FN no holdout. Corpus inválido, sem classes, vazado ou empate não produz
   promoção. Resultado sempre declara `promoted=false`, revisão humana e
   autoridade inalterada; corpus fornecido não é validação externa independente.
   Expor delta no holdout e flag de melhoria observada, distinguindo empate no
   holdout de ganho mesmo quando a recomendação não regressiva é permitida.
7. Resultado inclui propostas de trabalho para o conselho R989, sem executar
   agentes, arquivos, rede ou código upstream. CLI pela fachada científica
   oferece `scanner-evolve`; execução dos testes de avaliação é local.

## Fora de escopo

Não tratar termos metodológicos como comprovação de método, treinar modelos,
executar estudos clínicos ou alegar melhoria generalizável com corpus pequeno.
A evolução não corrige automaticamente os demais scanners. Gate SDD/TDD bloqueia
entrega defeituosa de software; heurística textual apenas encaminha revisão.
