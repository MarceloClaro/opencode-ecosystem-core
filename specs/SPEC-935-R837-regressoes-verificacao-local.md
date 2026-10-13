---
spec_id: SPEC-935-R837
title: Verificação determinística de fontes de dados e cancelamento nativo
component: tests/test_r52_data_knowledge_hub.py, tests/test_r823_ghidra_native_rea.py, plugins/lean-nucleo-verificacao/teoremas/roteamento_atencao.lean
status: implemented
round_id: R837
test_file: tests/test_r823_ghidra_native_rea.py
---

# SPEC-935-R837 — Regressões da verificação local

## Problema observado

A execução global `outputs/core-r820/attempt-3` registrou falha do teste Zenodo
quando a fonte declarou `unavailable`, tempo total de inicialização e cancelamento
superior a 12 segundos e tempo limite de 300 segundos na prova Lean R755.
A reprodução isolada confirmou uma corrida: o cancelamento ocorreu antes de o
transporte criar seu arquivo de PID. O teste R816 passou isoladamente.

## Contratos e limites

1. Os testes de DatasetDataSource utilizam respostas HTTP controladas, sem depender
   da rede. Uma falha de aquisição mantém `results == []`, `synthetic is False`
   e `evidence_eligible is False`; exemplos só aparecem mediante opção explícita.
2. O teste de cancelamento só cancela depois de observar uma marca escrita pelo
   processo filho ao entrar na operação bloqueada. O limite de 12 segundos mede
   o cancelamento e a limpeza, separadamente da inicialização. A espera de prontidão
   tem limite próprio e uma falha de prontidão não pode ser tratada como sucesso.
3. Mesmo quando a espera de prontidão falha, o teste cancela e aguarda seu trabalhador,
   sem deixar um processo do teste executando. Depois de cancelar, o PID observado
   não pode permanecer em execução. A execução hermética não valida o Ghidra real.
4. A investigação Lean preserva os 11 enunciados e o contrato `machine_checked`
   somente após retorno zero do compilador real. Não se amplia o prazo de 300 segundos,
   substitui a prova por texto ou marca um tempo limite como aprovação.
   A correção autorizada restringe o import monolítico `Mathlib` aos oito módulos
   necessários. Os 11 enunciados, hipóteses e corpos de prova permanecem idênticos.

## Causa e evidência da compilação

A reprodução independente da fonte original excedeu o mesmo limite de 300 segundos
em 300,07 segundos, sem saída do compilador. Uma cópia com os oito imports específicos
e os mesmos corpos retornou zero em 7,70 segundos no toolchain Lean 4.34.1.
As duas execuções estão registradas em `lean-original-receipt.json` e
`lean-narrow-receipt.json`. Isso sustenta a remoção da dependência de carregamento
do pacote completo neste ambiente; não é uma comparação universal de desempenho.
A mudança canônica precisa passar pelo teste R755 e registrar igualdade dos corpos,
hashes da fonte anterior e posterior e saída real do compilador.

## Aceitação local

- RED reproduzido com falha HTTP forçada e inicialização controladamente lenta;
  GREEN com os testes reparados, incluindo casos de sucesso, falha fechada e demo.
- Regressão de cancelamento com início lento e confirmação de fim do processo.
- Prova Lean examinada e executada independentemente com saída, duração e hashes
  preservados, ou impedimento explicitamente registrado. Não executar a suíte global.
- Os quatro testes R755 devem passar com a fonte canônica. T11 limita `Real.exp`
  no modelo de números reais; não certifica segurança de ponto flutuante IEEE-754.
- Evidências em `outputs/core-r837/`; decisão final humana e nenhuma validação externa.

## Resultado local registrado

- Dados controlados e transporte hermético: 39 testes passaram em 14,52 segundos.
- Cancelamento com atraso de início de 8 segundos: prontidão em 10,67 segundos,
  limpeza em 2,11 segundos; o PID observado não permaneceu executando.
- R755 canônico: quatro testes passaram em 8,92 segundos, sem `skip`.
- Os 11 corpos, incluindo suas hipóteses, são idênticos após remover apenas as
  linhas de imports; hashes registrados em `lean-canonical-receipt.json`.
- A afirmação alterada de soma softmax igual a 2 foi rejeitada pelo compilador real
  em 6,47 segundos. O arquivo canônico preserva a afirmação original igual a 1.
- A saída real de `#print axioms` para os 11 teoremas foi capturada em
  `lean-live-axioms.stdout.txt`: somente `propext`, `Classical.choice` e `Quot.sound`,
  sem `sorryAx`. Esse exame local não corresponde a revisão matemática externa.
- Um mutante que promove aquisição HTTP falha a evidência elegível foi detectado
  pelos oito casos negativos/demonstração; recibo `http-mutant.xml`.
- Esses resultados não substituem a execução global posterior nem aprovação humana.
