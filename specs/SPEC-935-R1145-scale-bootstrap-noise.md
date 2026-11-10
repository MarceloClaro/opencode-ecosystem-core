# SPEC-935-R1145 — Escala amostral, bootstrap, curva de aprendizado e ruído de leitura

**Status:** implementação local, sem hardware
**Data:** 2026-11-10
**Depende de:** R1142, R1143, R1144
**Fontes:** Caro et al. 2022 (`10.1038/s41467-022-32550-3`); Havlíček 2019
(`10.1038/s41586-019-0980-2`); Huang 2021 (`10.1038/s41467-021-22539-9`).

## 1. Objetivo

Fechar quatro lacunas declaradas no relatório R1142/R1144:

1. aumentar `n_per_class` e reportar intervalo de confiança por bootstrap;
2. medir curva de aprendizado (acurácia vs `N`) e comparar o expoente empírico
   com a previsão `sqrt(T/N)` de Caro 2022;
3. simular ruído de leitura e shots no kernel antes de qualquer gate de
   hardware;
4. executar QAOA p>3 sob orçamento explícito e comparar com solver clássico
   exato, sem alegar escala.

## 2. Requisitos

- **R1.** `bootstrap_accuracy_ci(confusion, n_boot, confidence, seed)`:
  percentil sobre a matriz de confusão; não usa o conjunto de teste para
  selecionar nada.
- **R2.** `improved_audit` devolve `test_confusion` e `validation_confusion`
  dos configs selecionados; seleção continua na validação.
- **R3.** `benchmark_improved` adiciona IC bootstrap por seed e IC agregado.
- **R4.** `learning_curve(per_class_sizes, seeds, noise)`:
  - para cada tamanho, roda o mesmo protocolo de seleção em validação;
  - agrega acurácia e IC por tamanho;
  - ajusta `erro = a * N^(-b)` em log-log e reporta `b` com IC bootstrap;
  - reporta `caro_prediction_exponent = 0.5` e deixa claro que a comparação é
    descritiva, não um teste do teorema.
- **R5.** `noisy_kernel_audit`:
  - estima o kernel por *compute-uncompute* com `shots`;
  - aplica modelo de ruído de leitura simétrico ou assimétrico `(e01, e10)`;
  - reporta acurácia exata vs ruidosa, erro médio absoluto do kernel e
    `readout_model`;
  - a seleção de hiperparâmetros é feita no kernel exato e declarada como tal.
- **R6.** `noise_sweep` reutiliza a seleção por seed e varre `shots` e
  `readout_error` sem reexecutar a busca.
- **R7.** `qaoa_audit` aceita `max_evaluations_per_depth`; profundidades que
  estouram o orçamento são marcadas `budget_exhausted` e não entram no melhor
  resultado. Inclui `exact_solver` (enumeração) e `gap` vs ótimo.
- **R8.** Nenhum hardware, nenhuma chave, nenhuma alegação de vantagem ou de
  escala.

## 3. Critérios de aceitação

- IC bootstrap em `[0,1]`, contém a acurácia pontual e é degenerado quando a
  matriz de confusão é perfeita;
- `test_confusion` soma `n_test`;
- curva de aprendizado tem um ponto por tamanho, leakage `disjoint=True` e
  expoente `None` quando todos os erros são zero (caso censurado);
- kernel ruidoso com `shots=100000` e `readout_error=0` tem erro médio absoluto
  `< 0,02` contra o kernel exato;
- QAOA com orçamento mínimo retorna `budget_exhausted` e `qaoa_energy=None`;
- QAOA p=4 retorna energia `>=` ótimo exato e razão em `[0,1]`;
- `hardware_executed=False`, `rates_measured=False` em todos os payloads.

## 4. Limites

Dataset sintético, QUBO sintético, ruído de leitura modelado (não calibrado),
sem hardware. A curva de aprendizado usa um único dataset por seed; o expoente
é descritivo e não valida nem refuta Caro 2022. QAOA p=4–5 em 4 variáveis não
demonstra escalabilidade.
