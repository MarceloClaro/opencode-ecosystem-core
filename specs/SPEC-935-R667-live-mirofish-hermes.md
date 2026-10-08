---
id: SPEC-935-R667
title: Transporte externo real MiroFish/OASIS e Hermes
status: green
created: 2026-10-04
validation_scope: local_external_runtime
---

# Problema e contrato

A ponte Hermes sem transporte e o healthcheck MiroFish não comprovam inferência nem simulação externa. O Core deve invocar os projetos externos por composição, sem copiar seus motores, e registrar exatamente o que executou.

`LiveScientificRuntime.run(config)` aceita `runtime` (hermes/mirofish), `prompt`, `model`, `base_url` exclusivamente de loopback, `output_dir` novo, `runtime_dir` opcional e `timeout_seconds` (5–600). Não aceita comandos, variáveis de ambiente ou código arbitrário.

## Critérios de aceitação

- AC1: validar todos os campos antes de efeitos; argv fixo, shell=False e diretórios externos identificados por origem Git permitida.
- AC2: Hermes executa sua CLI real, com ferramentas desabilitadas e perfil isolado; MiroFish executa o script externo de Twitter/OASIS, um cenário sintético de dois agentes e uma rodada limitada.
- AC3: uma ponte HTTP de auditoria encaminha requisições reais ao modelo local. Sem resposta com geração efetiva e sem artefato do runtime, o resultado fica bloqueado mesmo quando o processo retorna zero.
- AC4: erro, timeout, ausência de modelo ou dependência não permitem fallback mock/offline. Timeout encerra o grupo de processos que esta execução iniciou.
- AC5: preservar comando, commit remoto, hash da entrada externa, entradas do cenário, resposta do modelo, artefatos e hashes; excluir credenciais das evidências.
- AC6: modelo gerando personagens é simulação sintética executada, não observação social real, previsão validada nem evidência clínica. Inferência local não é validação externa científica.

## TDD e evidências

Testes em `tests/test_r667_live_scientific_runtime.py`; prova real repetível em `scripts/probe_mirofish_hermes_real.py`. Cada prova usa diretório novo, sem sobrescrever resultados anteriores.

RED: `docs/evidence/R667_RED.xml`, `R667_DEPENDENCY_RED.xml` e
`R667_STREAMING_RED.xml`. GREEN final: `docs/evidence/R667_R671_GREEN.xml`.
Prova central atual: `docs/evidence/R671_REAL_20261004_195302/probe.json`.
Consolidação: `docs/evidence/R667_R671_RELEASE_GATE.json`.

## Limites

Não há treinamento/fine-tuning neste contrato. O pequeno cenário OASIS valida conexão e execução, não realismo de população. O Core não atribui ao seu motor determinístico local uma execução dos projetos externos.
