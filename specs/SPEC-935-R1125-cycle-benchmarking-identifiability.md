---
spec_id: SPEC-935-R1125
title: CB por observável e identificabilidade Pauli-Lindblad
component: quantum_mitigation.cycle_benchmarking
status: red
test_file: tests/test_r1125_cycle_benchmarking.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1125-1:
      - tests/test_r1125_cycle_benchmarking.py::test_parity_is_not_p00_and_ignores_identity_bits
      - tests/test_r1125_cycle_benchmarking.py::test_invalid_counts_rejected
      - tests/test_r1125_cycle_benchmarking.py::test_ideal_parity_all_observables
      - tests/test_r1125_cycle_benchmarking.py::test_odd_or_invalid_depth_is_not_silently_recovered
      - tests/test_r1125_cycle_benchmarking.py::test_invalid_observable_or_mapping_rejected
    R1125-2:
      - tests/test_r1125_cycle_benchmarking.py::test_cz_orbits_against_independent_matrix_conjugation
      - tests/test_r1125_cycle_benchmarking.py::test_rank_nine_and_nonnegative_indistinguishable_generators
      - tests/test_r1125_cycle_benchmarking.py::test_full_spectrum_inversion_not_scalar_gamma
      - tests/test_r1125_cycle_benchmarking.py::test_physical_pauli_channel_not_always_lindblad_embeddable
      - tests/test_r1125_cycle_benchmarking.py::test_density_matrix_oracle_injects_actual_pauli_noise
      - tests/test_r1125_cycle_benchmarking.py::test_explicit_xi_xz_counterexample
    R1125-3:
      - tests/test_r1125_cycle_benchmarking.py::test_joint_bootstrap_propagates_without_discarding_negative_draws
      - tests/test_r1125_cycle_benchmarking.py::test_parity_decay_recovers_known_value_and_is_reproducible
      - tests/test_r1125_cycle_benchmarking.py::test_uninformative_or_misspecified_decay_blocked
      - tests/test_r1125_cycle_benchmarking.py::test_opposing_sets_are_not_averaged_before_fit
      - tests/test_r1125_cycle_benchmarking.py::test_fit_diagnostics_are_not_validated_inference
      - tests/test_r1125_cycle_benchmarking.py::test_tolerance_is_not_exact_positivity
    R1125-4:
      - tests/test_r1125_cycle_benchmarking.py::test_manifest_hash_budget_and_tamper_gate
      - tests/test_r1125_cycle_benchmarking.py::test_analysis_rejects_missing_data_and_legacy_metadata
      - tests/test_r1125_cycle_benchmarking.py::test_harness_offline_only_and_refuses_overwrite
      - tests/test_r1125_cycle_benchmarking.py::test_harness_rejects_ambiguous_json
      - tests/test_r1125_cycle_benchmarking.py::test_imported_jobs_reject_wrong_receipts_before_fitting
    R1125-5:
      - tests/test_r1125_cycle_benchmarking.py::test_guidance_reconciles_hardware_and_identifiability
      - tests/test_r1125_cycle_benchmarking.py::test_readout_reports_real_calibration_scope
      - tests/test_r1125_cycle_benchmarking.py::test_readout_missing_runs_remains_fail_closed
---

# SPEC-935-R1125 — CB por observável e identificabilidade Pauli-Lindblad

Data: 2026-11-09. Estado: especificado, antes da correção do protótipo.
Responsável: marceloclaro. Antecedentes: R1119, R1122–R1124.

## Problema e escopo

O protótipo não versionado `quantum_mitigation/cycle_benchmarking.py`
usa P(00) para todo Pauli e chama −log(lambda)/2 de taxa individual.
Esses procedimentos não caracterizam, em geral, um gerador Pauli-Lindblad.
A implementação anterior precedeu a spec/testes; não se reivindica TDD
retroativo. Esta correção terá RED real, GREEN e revisão independente.

Entregar um pipeline **offline** de circuitos, observáveis, ajuste, auditoria
de identificabilidade e contraprovas em simulador. Não submeter hardware,
instalar dependências, repetir RC, executar PEC/GST ou comparar layouts nesta
correção. A autorização histórica de hardware não dispensa estes gates.

## Modelo explícito

- Rótulos Pauli em ordem q1q0; counts em ordem c1c0.
- Observable: média da paridade somente nas posições não identidade, não P00.
- Modelo estacionário: ciclo CZ ideal seguido de canal Pauli e portas locais
  ideais no simulador. Ruído local/compilação reais não foram caracterizados.
- Decaimento de paridade E(P,m)=A f_eff(P)^m, com profundidades pares. Não
  ajustar log(P00), não acrescentar recuperação ruidosa dependente da paridade.
- L(rho)=sum_Q gamma_Q (Q rho Q-rho), gamma_Q>=0 por ciclo.
  −log(f_P)/2 = sum_{Q anticomuta P} gamma_Q. É um sistema linear, não uma
  igualdade entre uma fidelidade e uma taxa individual.
- Repetição de CZ mede produtos nas órbitas P <-> CZ P CZ. Verificar posto
  do desenho e recusar inversão não identificável; não usar pseudoinversa
  ou regularização como prova de identificação.

## Critérios de aceitação

1. Testes RED detectam P00 versus paridade (incluindo I, Y, hexadecimal),
   mistura de profundidades par/ímpar e conversão escalar indevida.
2. Circuitos ideais para os 15 Paulis, m=0,2,4,8,16 têm paridade +1;
   m ímpar/negativo, Pauli II e mapeamento ambíguo são recusados. Twirls e
   barreiras explícitos; nenhuma alegação de preservação pelo servidor GJQ.
3. Counts inválidos (vazios, negativos, fracionários, bits fora da largura)
   são recusados. Paridade ignora bits I. Incerteza binomial declarada.
4. Ajuste direto de E=A f^m, domínio e informação verificados, IC95% por
   bootstrap paramétrico condicional de shots, seed e número de réplicas.
   Contraprovas de contraste insuficiente, crescimento e má adequação não
   promovem taxas. O IC não cobre drift nem variação de seeds.
5. Matriz anticomutação de 15x15 recupera taxas conhecidas de espectro
   completo. Espectro não físico/gerador negativo é recusado, não truncado.
   Propagar amostras conjuntas; IC por parâmetro não é simultâneo.
6. Auditar posto para CZ e demonstrar dois geradores distintos não negativos
   indistinguíveis sob este desenho. Resultado parcial não libera PEC 2q.
7. Teste independente por matriz densidade com canal conhecido, além de
   dados de ajuste gerados pela equação. Simulação identificada como tal.
8. Harness local escreve manifesto determinístico com hashes QASM e protocolo
   antes de qualquer aquisição; análise recusa chaves ausentes/extras,
   origem indevida e formato legado. Nenhum import/submissão GJQ no harness.
9. Agentes, skill e handoff distinguem RC realizado, readout 2x2/subespaço
   versus 4x4, observáveis versus taxas e limitações SPAM/compilação.
10. Registrar comandos RED/GREEN, revisão, hashes, limitações e reflexão.
    Não alterar arquivos alheios, credenciais ou permissões para hardware.

## Parada e entrega

150 jobs é apenas o orçamento histórico; não garante 15 parâmetros nem
poder. Mesmo um ajuste bom permanece bloqueado para PEC se o posto for
insuficiente. Uma revisão do protocolo/recursos deve preceder novas
submissões. Testes locais e pareceres de agentes não são validação externa.

## Critérios de aceitação executáveis

- `R1125-1` — Paridade, identidade, bits, domínio e profundidades pares.
- `R1125-2` — Posto, contraprova física, inversão completa e oráculo de canal.
- `R1125-3` — Ajustes condicionais, incerteza sem projeção, heterogeneidade e limites.
- `R1125-4` — Manifesto, hashes, dados completos, JSON inequívoco e offline sem sobrescrita.
- `R1125-5` — Documentação e análise de leitura coerentes com os counts históricos.

O primeiro RED/GREEN foi observado em logs do pytest (44 falhas, depois 46
passagens). A segunda rodada incorpora a revisão adversarial e tem contrato
runtime selado; não se fabricará recibo retroativo da primeira rodada.
