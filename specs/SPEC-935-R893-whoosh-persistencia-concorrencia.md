---
spec_id: SPEC-935-R893
title: Preservar índices Whoosh entre processos e somente confirmar escritas efetivas
component: skills.tooling.whoosh3_engine
status: implemented
test_file: tests/test_r893_whoosh_persistence.py
---

# R893 — Busca local persistente sem recriação indevida

## Defeito observado

Dois diagnósticos concorrentes registraram erro de renomeação do arquivo de
índice em `/tmp/opencode_whoosh/opencode_memoria/`. A leitura encontrou que
`_open_or_create` procura `_*.seg` para decidir se há índice, embora segmentos
Whoosh usem nomes `MAIN_*.seg`; assim, outro processo pode recriar um índice
existente e perder seus documentos. A contraprova local usa somente diretório
temporário: indexar documento, limpar cache em memória, reabrir e consultar.

## Contrato

1. Usar a detecção oficial de existência do índice e abrir o índice existente.
   Não apagar/recriar dados válidos durante importação ou diagnóstico.
2. Serializar criação inicial por lock de processo e proteger cache em threads;
   inicialização concorrente não deve corromper o TOC nem descartar dados.
3. Escritas devem liberar/cancelar writer quando falham. `index_batch` não pode
   devolver quantidade positiva se o commit falhou; estatísticas só mudam após
   commit real. Aplicar o mesmo cuidado a indexação simples e remoção.
4. Testar persistência em processo separado, criação concorrente, falha de commit
   e recuperação posterior, sem usar o diretório de memória de produção.
5. Não prometer SLA de consulta, semântica neural ou escalabilidade multi-host
   por esses testes. Registrar a correção e seus limites no perfil científico.
6. O consumidor `ContextAmplifier` deve receber conteúdo recuperado real. Novos
   índices devem armazenar conteúdo para recuperação; índices legados sem esse
   campo não são recriados nem recebem texto inventado. Distinguir explicitamente
   metadados de conteúdo. Um engine fornecido não deve ser substituído só porque
   seu contador de operações da sessão é zero. Testar o percurso indexar → reabrir
   → recuperar → bloco de contexto, sem rede ou aumento de confiança.

7. Indexação simples e em lote não devem converter `None`, objetos ou números
   em suposto conteúdo documental. Rejeitar entradas não textuais antes de
   modificar o índice; busca e grounding só classificam texto real armazenado.
