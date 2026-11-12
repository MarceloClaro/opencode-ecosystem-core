# SPEC-935-R1104 — IIT-Metrics P0: correções de confiabilidade

Data: 2026-11-12. Estado: implementado e verificado; testes GREEN.
Origem: `specs/SPEC-935-R1103-iit-autonomia-pesquisa.md` e
`docs/research/iit-autonomia-r1103/audit.json`.
Evidência: `docs/research/iit-autonomia-r1103/p0-verification.md`.

## Escopo

Corrigir as lacunas P0 reproduzidas na auditoria R1103:

- G01: substituir `hash()` randomizado por bucket determinístico.
- G02: diversidade de estratégias deve distinguir uma de várias estratégias.
- G04: ler `payload`, distinguir `missing` de `abstained` e não inventar
  `outcome`, `confidence` ou `strategy`.
- G05: não penalizar abstenção segura no score; reportar cobertura e risco
  seletivo separadamente.
- G06: remover fallback sintético silencioso do comando `analyze`.
- G07: usar a assinatura real de `EvolutionRegistry.record` e não escrever
  no registry real durante testes.
- G08: remover rótulos de “apto para publicação” e “research_grade”.
- G09: fazer `n_states` controlar a distribuição de confiança.
- G10: manter uma única `iiit_metrics_cli` e fazer `--help` sair com 0.
- G11: ausência de telemetria deve retornar `insufficient_data`, sem score
  numérico.

## Fora do escopo

Não calcular Φ, não instalar PyPhi/MindSpore, não treinar modelos, não
alterar permissões, não promover trust e não reescrever o grafo sequencial
como causal. G03 permanece aberto e deve ser tratado em rodada própria.
Nenhum teste pode gravar em `evolution/cycles.json` real.

## Critérios de aceitação

- CA01: o mesmo JSON de traces produz o mesmo score e mutual information
  em processos com `PYTHONHASHSEED` diferentes.
- CA02: uma estratégia produz diversidade 0; quatro estratégias equilibradas
  produzem diversidade próxima de 1; distribuição enviesada produz valor
  intermediário.
- CA03: evento com `payload.outcome='success'` conta como sucesso; evento
  sem outcome conta como `missing`; confiança e estratégia ausentes são
  contadas como missing, não preenchidas por default.
- CA04: o score não contém termo de penalização por abstenção; cobertura,
  taxa de abstenção, taxa de missing e risco seletivo aparecem separados.
- CA05: sem traces, `available=False`, `score=None` e
  `status='insufficient_data'`; o CLI `analyze` sai com código não zero e
  não imprime score.
- CA06: `record_to_evolution_registry` grava um `EvolutionCycle` válido em
  registry temporário e retorna dicionário serializável; o hash de
  `evolution/cycles.json` real permanece inalterado.
- CA07: existe exatamente uma definição de `iiit_metrics_cli`;
  `python -m mci iiit-metrics --help` sai com 0; `analyze` não gera dados
  sintéticos quando o MetaBus falha; `synthetic` é explícito e rotulado.
- CA08: nenhum rótulo contém “apto para publicação”, “research_grade” ou
  equivalente; a saída descreve a influência sequencial como não causal.
- CA09: `n_states` controla o comprimento da distribuição e a normalização
  da entropia.
- CA10: testes novos iniciam RED e terminam GREEN; a suíte existente
  permanece passando; nenhum estado de produção é alterado.

## Plano TDD

1. Escrever `tests/test_r1104_iit_metrics_p0.py` cobrindo CA01–CA10.
2. Executar e registrar RED.
3. Implementar em `mci/iiit_metrics.py` e `mci/__main__.py`.
4. Executar o teste novo, os testes R1103 e a suíte de MCI.
5. Registrar evidência em `docs/research/iit-autonomia-r1103/` sem
   sobrescrever o `audit.json` original.

## Evidência de conclusão

- Saída RED e GREEN dos testes.
- Hash de `evolution/cycles.json` antes/depois dos testes.
- Nenhuma alteração em `federation/activated.json` ou permissões.
- Relatório final distinguindo corrigido, não corrigido e não testado.
