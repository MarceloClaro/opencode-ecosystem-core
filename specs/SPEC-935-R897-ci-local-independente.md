---
spec_id: SPEC-935-R897
title: CI local auditável independente de runners hospedados
component: integrations.local_ci
status: implemented
test_file: tests/test_r897_local_ci.py
---

# R897 — CI local auditável independente de runners hospedados

## Autorização e desenho

Solicitação explícita de implementar os agentes históricos, manter validação/registro permanente, integrar os plugins nomeados e buscar alternativas à CI hospedada e ao grafo bloqueado. Preservar dados locais e o primário canônico.

## Contrato

1. Implementar LocalCIService start(profile=scientific), status(run_id=None), runs(limit), cancel(run_id), sem daemon, scheduler, registro de runner remoto ou comandos arbitrários.
2. Reutilizar runner R891 com perfil explicitamente enumerado, subprocesso próprio e limites. Single-writer flock durante execução, identidade PID+create_time, resultados em diretório privado isolado e único por run.
3. Só aceitar verificação nova do runner, coleta/fases/JUnit/hash/HEAD/fontes/seleção exata. Summary anterior, retorno0 sem recibo, teste ignorado, fonte alterada, artefato trocado ou escape de path bloqueia. Histórico e aplicabilidade às fontes atuais são estados separados.
4. Cancelamento deve terminar somente árvore de processos criada pela execução, inclusive grupos em sessões próprias; limpeza incompleta bloqueia. Limites originais do R891 não aumentam para esconder falha.
5. Root integrará ao primário, CLI e MCP. Metacognição registra observação sem prêmio de confiança. Não converter aprovação local em check remoto ou revisão científica externa.
6. Testes RED/GREEN com subprocessos reais pequenos e negativos de concorrência, integridade, cancelamento e tipos. Executar perfil científico real final pelo novo caminho; registrar motivo observado de bloqueio remoto separadamente.

## Evidência e limites

Execução local delimitada, sem garantia de ausência universal de bugs, validação externa, mérito editorial ou escala de cluster. Registrar RED/GREEN e ciclo evolutivo somente após verificação.
