---
spec_id: SPEC-935-R828
title: Remediação de cobertura, disciplina SDD/TDD e governança
status: proposed
component: marceloclaro/orchestrator + sdd/spec_engine + trust_economy
test_file: tests/test_r828_remediacao_cobertura_governanca.py
---

# R828 — Remediação de cobertura, SDD/TDD e governança

Origem: `diagnose` domínio `ecosystem` — cobertura noológica 42% grau C (35/83, 48 ausentes), teleológico 0.381 com 10 gaps (4 críticos: tdd_red_green_refactor, sdd_spec_first, sdd_gate, trust_scoring), 58 gaps evolutivos, camadas raciocinio_conhecimento 25%, integracao_infra 27%, governanca_economia 31%, core_orchestration 41%, diagnostico_evolucao 76%. Federação com 354 degraded por license_undeclared. Operação local, sem validação externa.

## Objetivo mensurável (1 ciclo)

1. Cobertura noológica 42% -> >=55% sem reduzir diagnostico_evolucao abaixo de 70%.
2. Score teleológico 0.381 -> >=0.55, com zero críticos remanescentes nos 4 itens acima.
3. Federação: reduzir degraded por license_undeclared de 354 -> <100 por triagem declarativa, sem alegar relicenciamento.
4. Nenhuma entrega sem spec linkada e teste RED->GREEN correspondente.

## Escopo fechado

Inclui:
- Reativação fail-closed do gate SDD (SpecVerifier barra entrega sem spec_id válido).
- Reativação do trust_scoring no roteamento (prioriza trust alto; trust <0.3 exige supervisão).
- Ciclo TDD obrigatório por gap crítico (teste que falha antes, passa depois).
- Triagem de licenças dos 354 degraded (declarar SPDX quando presente no artefato; quando ausente, marcar `license_undeclared` e manter degraded, sem inventar licença).
- Reconexão declarativa dos motores de raciocínio (Z3, SymPy) via `/reason` com fallback explícito, sem alegar desempenho.

Exclui:
- Reescrita de agentes, re-treinamento, mudança de provedor LLM, relicenciamento de terceiros, prova formal Lean, validação clínica ou editorial Qualis.

## Regras fail-closed

- `sdd_spec_first`: todo diff de código exige spec_id R828 ou sucessora; sem spec, gate reprova.
- `tdd_red_green_refactor`: todo fix exige teste RED prévio com hash e log; REFACTOR só com verde.
- `trust_scoring`: roteamento pondera confidence_score + load + histórico; slashing proporcional em entrega reprovada.
- Licença ausente permanece degraded; inventar licença reprova o ciclo.

## Testes exigidos (TDD)

`tests/test_r828_remediacao_cobertura_governanca.py` deve cobrir, com fixtures sem rede/inferência/escrita externa:
1. `test_gate_barra_sem_spec`: entrega sem spec_id é reprovada.
2. `test_gate_aprova_com_spec`: entrega com R828 e teste verde é aprovada.
3. `test_tdd_red_exigido`: fix sem RED prévio é reprovado.
4. `test_trust_prioriza_e_supervisiona`: trust alto priorizado; trust <0.3 exige flag de supervisão.
5. `test_licenca_nao_inventada`: artefato sem SPDX permanece degraded, nunca ok por presunção.
6. `test_reason_fallback_declarado`: motor ausente retorna fallback explícito, não sucesso presumido.

Aceite: 6/6 verdes + regressão dos testes R821-R827 sem quebra + novo `diagnose` com números acima. Evidências em `outputs/core-r828/release-summary.json`.

## Limites anti-overclaim

### Retificação de medida após revisão cega

Os valores 42%, 0.381, 48 ausências e 354 licenças são o relato histórico
fornecido pelo usuário, não uma medição reexecutada nesta spec. Os objetivos
numéricos permanecem pendentes; não se obtém aceite adicionando termos aos
próprios arquivos rastreados. Autodescoberta lexical e cobertura funcional são
medidas distintas. A projeção com corpus retido usa o DiagnosticPipeline real,
ID e SHA-256 exato da entrada, sem enriquecimento por código local (R835).

O teste de formatação usa dados artificiais explicitamente identificados;
o teste de medição executa o pipeline. Diagnose registra observações e não
altera confiança, inclusive no ramo opcional de impacto jurídico. A explicação
deve derivar números do relatório recebido e declarar escopo e incerteza.
Nenhum indicador de ruído ou compressão certifica integridade ou qualidade.

### Retificação dos auxiliares declarativos SDD/TDD

Os auxiliares adicionados `sdd.spec_engine.verify_delivery`,
`sdd.tdd_runner.require_red_first` e o método correspondente de `TDDRunner`
não têm consumidores no fluxo do repositório e aprovavam prefixo/flag ou texto
arbitrário. São removidos como atalhos sem evidência de execução. A entrega
real continua exclusivamente pelo primário, `SpecVerifier.verify` e evidência
confiável emitida por `TDDRunner.run_spec_test`.

Os três protocolos `sdd_spec_first`, `sdd_gate` e `tdd_red_green_refactor`
permanecem como contratos declarativos de entrada. Seu campo `approved`
significa aceitação da forma dos argumentos; os resultados explicitam
`runtime_gate: false`, `execution_verified: false` e
`verification: input_contract_only`. Uma flag verde ou texto informado pelo
chamador não representa fase RED, teste executado nem aprovação de entrega.
`approved_str` redundante é removido dessas três projeções após busca de
consumidores. Não se infere correspondência entre contrato e artefato existente.

Aceitação delimitada em `tests/test_r828_declarative_boundaries.py`, com
RED/GREEN e regressão R448. Os objetivos percentuais originais desta spec
continuam pendentes; passar esse teste não cumpre todos os critérios de R828.


Resultado é operação local (`verification: local_operation`). Não declara cobertura total, eficácia causal, cura, desempenho superhuman, prova formal, Qualis A1 ou aceite editorial. Números de potencialidade permanecem hipótese sem probabilidade calibrada. Revisão humana obrigatória antes de federar ou publicar.

## Rastreabilidade

- Base: saída `diagnose` 2026-10-12 (42%, 0.381, 58 gaps, SPS 0.9451, CR 0.9563, reversa 3).
- Doctor prévio: 22/22 pass, 186 specs formais, 668/668 ciclos, MetaBus 306 entradas.
- Estado de executores no ciclo: codex `execution_succeeded`, claude `account_limit`, antigravity `installation_only`.
