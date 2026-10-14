---
spec_id: SPEC-935-R889
title: Reprovar índice parcial e recuperar processos limitados do provedor local
component: integrations.code_context
status: specified
test_file: tests/test_r887_code_context.py
---

# R889 — Aceite integral do índice local

## Contraprova

Após R887/R888, o índice do commit `a0efdcd` descobriu 763 fontes (8.508.274
bytes), mas persistiu apenas 179 arquivos. O processo retornou zero e respondeu
a ping, apesar de 584 falhas `tree-sitter parse failed: operation limit was hit`.
As consultas do primário por MetacognitiveLoop e por seu arquivo falharam. O
recibo anterior permanece em `outputs/core-r887/core-post-commit.json`.

A leitura do provedor sugere condição associada à reutilização/cancelamento do
parser, mas esta é hipótese de causa raiz. A reprodução comprova a indexação
parcial, não a corrida interna. Não foi constatado esgotamento do limite de
arquivo/DB (o banco tinha aproximadamente 2,65 MB).

## Contrato

1. Exit code zero e ping não bastam para promover um índice. Exigir resumo
   coerente, zero erros finais e auditoria dos caminhos/hashes do banco contra
   todas as fontes materializadas esperadas. Divergência é falha explícita.
2. Gerações antigas sem recibo de integridade integral não são prontas. Não
   apresentar um índice parcial como cobertura completa do corpus.
3. Permitir recuperação incremental por novos processos isolados, até seis
   passadas por invocação e dentro do orçamento global solicitado (até 120 s).
   Uma nova operação explícita de indexação pode retomar o candidato privado
   com o mesmo corpus, versão binária e hashes; consulta comum não o retoma.
   Preservar estatísticas de todas as passadas. Sem reduzir o corpus para
   ocultar erros, sem alterar o binário fixado ou baixar pesos.
4. Sem progresso, prazo esgotado, schema inesperado do DB ou fonte divergente
   mantêm o gate fechado e a geração anterior preservada para inspeção.
5. Alteração de fonte invalida o índice; commit apenas documental com todos
   os hashes selecionados idênticos pode conservá-lo. Registrar `source_head`
   original e `current_head` separado, sem atribuir ao commit anterior o código
   que só existe no working tree. Testar ambas as situações.
6. Testes negativos antes da correção: exit zero com erros, ping com erro,
   banco parcial, geração antiga e limite de tentativas. GREEN deve preceder
   a nova indexação real e consultas do primário por fontes conhecidas.
7. Reindexar o Core completo selecionado (763 arquivos ou nova contagem exata
   após a alteração) e consultar código/skeleton conhecidos, com hashes e
   proveniência. Dados continuam locais e confiança não é promovida.

## Entrega

Adaptar somente o contrato de aceite do provedor existente, preservando as
três consultas de grafo bloqueadas por R887. Publicar recibo de execução,
limitações, testes dirigidos e ciclo R889 após a correção. Recuperação por
novos processos não demonstra eliminação da causa raiz upstream.
