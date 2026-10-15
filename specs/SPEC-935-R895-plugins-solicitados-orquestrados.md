---
spec_id: SPEC-935-R895
title: Ampliar plugins locais e pontes hospedadas solicitadas
component: integrations.scientific_plugins
status: implemented
test_file: tests/test_r895_requested_plugins.py
---

# R895 — Ampliar plugins locais e pontes hospedadas solicitadas

## Autorização e desenho

Solicitação explícita de implementar os agentes históricos, manter validação/registro permanente, integrar os plugins nomeados e buscar alternativas à CI hospedada e ao grafo bloqueado. Preservar dados locais e o primário canônico.

## Contrato

1. Incluir os 20 plugins nomeados pelo usuário reutilizando ScientificPluginService, versões locais existentes e o primário. Não criar segundo coordenador ou segundo diretório concorrente de registro.
2. Importar pacotes/skills somente de cache local autorizado, com origem/hash/versão e limites. Nunca copiar credenciais, executar hooks ou publicar instruções privadas no Git; manter instruções locais fora de controle de versão.
3. Preservar disable-model-invocation/allow_implicit_invocation e despacho determinístico no contexto do primário. Descrever quais capacidades são instruções, ferramentas locais ou conectores hospedados.
4. Conectores hospedados mantêm tickets ligados a host_tool/request_sha256 e recibos; disponibilidade da ferramenta no host não equivale a OAuth funcional no Core. Falha, erro ou falta de habilitação mantém bloqueio.
5. SciGrant somente para intenção de redação de projeto, nunca para teste de integração sem solicitação de redação. Sites/Pets/Plugin Creator não publicam nem alteram apps por mera importação. Domínios clínicos/jurídicos/escolares preservam limites e proveniência.
6. Novos perfis de plugin entram na governança R894 (root fará cartões). Testes de todos pedidos, ausência/adulteração de cache, política explícita, negação de operação externa e reenquadramento do status. Executar importação real local e amostra de skill sem alegar execução de suas tarefas.

## Evidência e limites

Execução local delimitada, sem garantia de ausência universal de bugs, validação externa, mérito editorial ou escala de cluster. Registrar RED/GREEN e ciclo evolutivo somente após verificação.
