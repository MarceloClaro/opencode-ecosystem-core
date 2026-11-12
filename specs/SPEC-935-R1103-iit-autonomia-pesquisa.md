# SPEC-935-R1103 — Pesquisa e auditoria IIT/autonomia

Data: 2026-11-12. Estado inicial: especificado; entrega documental, não implantação.

## Solicitação e escopo

Buscar artigos dos quais extrair técnicas para mitigar lacunas de autonomia,
automonitoramento, qualidade de pesquisa e métricas do MetaBus. Auditar as
alegações anteriores à luz de `mci/iiit_metrics.py` e `mci/__main__.py`.
Consciência fenomenal é questão científica em debate: não é um aceite de
engenharia nem uma consequência demonstrada de métricas informacionais.

## Entregáveis

- Dossiê em `docs/research/iit-autonomia-r1103/`: fontes com identificadores,
  consultas, limites, matriz técnica→lacuna→teste e plano de experimentos.
- Auditoria local reproduzível em ambiente temporário; nenhuma mudança de
  permissões ou do comportamento de produção nesta rodada.
- Testes de integridade documental; o sucesso desses testes NÃO homologa
  o módulo antigo nem valida uma teoria de consciência.

## Critérios de aceitação

- CA01: pelo menos oito fontes primárias resolvidas; título, ano, identificador,
  URL, escopo de leitura, técnica e limite explícitos. Incluir contraprovas.
- CA02: separar IIT 3.0, IIT 4.0, Shannon, causalidade e autorrelato.
- CA03: cada lacuna local possui caminho/localizador e teste proposto; nenhuma
  associação temporal é rotulada como causa demonstrada.
- CA04: não propor dados sintéticos como substitutos silenciosos da telemetria;
  não penalizar abstenção segura ou promover trust por autoavaliação.
- CA05: registrar falhas de ferramentas e distinguir inspeção, reprodução,
  proposta e implementação. Preservar alterações alheias.
- CA06: definir métricas de sucesso independentes de entropia: correção em
  tarefas reservadas, calibração, custo, repetição de erros e ações indevidas.
- CA07: testes do dossiê inicialmente RED por ausência dos artefatos, depois
  GREEN; contraprovas do módulo antigo documentadas separadamente.

## Fora do escopo

Não instalar PyPhi ou outros pacotes, não treinar modelos, não ativar MCP,
não publicar nem executar repositórios de terceiros. Não alegar Phi exato,
consciência, melhoria empírica ou revisão externa concluída.

## Saúde observada antes da escrita

`python3 -m marceloclaro.cli doctor` falhou: whoosh ausente no Python global.
`.venv/bin/python3 -m marceloclaro.cli doctor`: 16 pass, 6 warn, 0 fail;
estado estrutural degraded. Specs, memória e registry acessíveis; provedores
e executores externos não estão homologados por esse diagnóstico.
