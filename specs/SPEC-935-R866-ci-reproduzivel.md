---
spec_id: SPEC-935-R866
title: CI com dependências Node declaradas e relatório da execução única
component: .github.workflows.ci, scripts.quality_report
status: implemented
test_file: tests/test_r866_ci_release.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    reproducao:
    - tests/test_r866_ci_release.py::test_ci_instala_node_e_lock_antes_da_suite
    - tests/test_r866_ci_release.py::test_ci_gera_junit_e_reutiliza_sem_segunda_suite
    relatorio:
    - tests/test_r866_ci_release.py::test_junit_conta_casos_sem_somar_agregados_duas_vezes
    - tests/test_r866_ci_release.py::test_subtestes_apenas_no_agregado_pytest_nao_inventam_aprovacoes
    - tests/test_r866_ci_release.py::test_relatorio_junit_nao_executa_pytest
    - tests/test_r866_ci_release.py::test_falha_e_erro_do_junit_nao_recebem_pass
    - tests/test_r866_ci_release.py::test_junit_so_com_skips_nao_recebe_pass
    - tests/test_r866_ci_release.py::test_junit_recusa_dados_ausentes_ou_incoerentes
    - tests/test_r866_ci_release.py::test_quick_nao_inventa_medicao_verde
    execucao:
    - tests/test_r866_ci_release.py::test_execucao_cli_default_mantem_timeout_suficiente
    - tests/test_r866_ci_release.py::test_returncode_nao_zero_reprova_mesmo_sem_contador_failed
    - tests/test_r866_ci_release.py::test_timeout_cli_e_falha_tipificada
    - tests/test_r866_ci_release.py::test_cli_junit_reprovado_retorna_falha
---

# R866 — Relatório fiel e reprodutibilidade da CI

O job de testes instala Node 22, executa `npm ci` em `.opencode` com lockfile
declarado e roda pytest uma única vez por versão Python. Pytest escreve JUnit;
o relatório de qualidade utiliza esse mesmo arquivo, inclusive após falha, e
os recibos são preservados como artefatos. A execução remota da CI ainda requer
um run efetivo no GitHub; inspeção do workflow não equivale a esse run.

O parser conta cada testcase uma vez, distingue falha, erro e skip e recusa
ausência de casos ou contadores declarados incoerentes. XML não é uma assinatura
de autenticidade: o relatório descreve o arquivo fornecido, sem certificar sua
proveniência externa. Uma bateria somente com skips e o modo quick recebem
`NOT_RUN`, sem percentual ou score de qualidade inventados. Bateria mista com
aprovações e skips informa `PASS_WITH_SKIPS`; skips continuam explícitos.

O JUnit efetivo do pytest pode contabilizar subtestes no agregado `tests` sem
emitir testcases próprios para suas aprovações. Em suites nomeadas `pytest`,
esse excesso positivo é registrado separadamente como `unrepresented_tests`,
com ressalva no relatório; não eleva `passed`, `total` medido ou percentual.
Falhas, erros e skips declarados ainda precisam corresponder a casos físicos.

A execução direta sem `--junit` permanece disponível, com prazo de 3600 segundos
e tratamento explícito de timeout e código de saída não zero. A coleta de lint
e a contagem de arquivos de teste são inventários locais; o score permanece
heurístico e não comprova cobertura funcional ou qualidade científica.
