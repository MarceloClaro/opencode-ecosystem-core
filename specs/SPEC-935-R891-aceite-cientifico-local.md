---
spec_id: SPEC-935-R891
title: Aceite local de pacotes científicos com reexecução e rastreabilidade
component: research.provenance_pipeline
status: implemented
test_file: tests/test_r891_scientific_release.py
---

# R891 — Artigos e experimentos no percurso científico existente

## Objetivo autorizado

O usuário autorizou implementar, instalar dependências necessárias e corrigir o
Core para produção científica, priorizando artigos **e** experimentos. O doctor
atual passou em 22 verificações estruturais; isso não constitui aceite de escala.
O percurso R663 já executa CSV, gera artigo e manifesto e reproduz o cálculo.
Falta uma operação canônica para verificar novamente um pacote após sua entrega.

## Contrato

1. Reutilizar `ScientificProvenancePipeline`, os três métodos internos
   (`pearson`, `welch_t`, `descriptive`), o primário e o MCP existentes.
   Não criar um segundo coordenador nem executar código fornecido pelo pacote.
2. Uma verificação exige diretório local e manifesto R663. Validar tipos e
   tamanho, arquivos obrigatórios, caminhos confinados ao pacote, recusa de
   symlinks, bytes e SHA-256 de **todos** os artefatos declarados. Pacotes antigos
   não são rejeitados apenas por registrar caminhos absolutos da pasta original:
   a relocalização pode usar nomes internos inequívocos, sem acessar a origem.
3. Revalidar configuração, CSV, análise, referências e recibos computacionais.
   Falta, alteração, estado parcial, evidência sintética, reprodução discordante
   ou valores não finitos bloqueiam o aceite. Flags de execução devem ser
   booleanos estritos, não strings ou números truthy.
4. Reexecutar a análise usando somente o método confiável do Core, em processo
   separado com prazo e orçamento delimitados. Nunca importar/rodar
   `reproduce.py`, `statistical_methods.py`, hooks ou comandos do pacote.
   Comparar o resultado com a análise exportada; documentar versão do ambiente.
   A concordância do replay admite somente variação de ponto flutuante com
   `rtol=1e-12` e `atol=1e-12`, explicitadas no recibo. Tipos, chaves, estrutura,
   tamanho e ordem das listas,
   contagens, seeds e booleanos continuam exatos. Hashes e a consistência entre
   os documentos do pacote não usam tolerância. Rejeitar números não finitos e
   divergência além do limite; informar a maior diferença numérica observada.
5. Aceite é **computacional local do pacote**. Não autoriza publicação, não
   comprova autenticidade externa de dados/referências, sustentação semântica de
   citações, revisão por pares, causalidade ou escalabilidade multi-host.
   Manter decisões científicas e declarações institucionais sob revisão humana.
6. Integrar `scientific_verify_package` ao primário, à CLI `ciencia verificar`
   e ao MCP `ecosystem_scientific_verify`. Persistir resumo/digest no MetaBus
   sem promoção de confiança. Retorno bloqueado implica código CLI não zero.
7. Usar perfil de regressões científicas explicitamente enumerado, com limites
   de tempo/memória e sem compiladores, GPU ou cargas não autorizadas. Preservar
   JUnit e registrar seleções, falhas e testes não executados; não apresentar o
   perfil como suíte global. Adicionar verificação correspondente à CI.
   O gravador deve resistir a substituições deliberadas de primitivas por
   testes de falha, preservando as três fases e sem suprimir erros reais de I/O.
8. A instalação reproduzível deve terminar com `pip check` sem conflito. Foi
   observado que o pin legado `requests==2.32.5` conflita com a CLI já instalada
   `scihub-cli 0.5.4`, que exige `requests>=2.33.0`; alinhar o pin compatível sem
   reinstalar os runtimes externos da curadoria e preservar recibos do resolvedor.

## Aceite

- Observar RED antes da implementação; positivos com todos os três métodos e
  artigo/manifesto reais de teste. Dados de fixture continuam identificados como
  fixture de contrato, sem alegar aquisição científica externa.
- Negativos: artefato/código/dados alterados, campo/hash ausente, path traversal,
  symlink, JSON inválido/não finito, flags falsas/truthy, reprodução divergente,
  importação ou execução arbitrária tentada e timeout sem sucesso fabricado.
- CLI, primário, MCP e MetaBus compartilham a mesma decisão e preservam o ledger.
- Realizar execução local sobre fonte pública e referência obtida de fato,
  salvar artigo/código/recibos e verificar em outro processo. Isso demonstra
  apenas a amostra executada, com revisão humana e validação externa pendentes.
- Registrar evolução e documentação com limites honestos; atualizar o índice
  somente após congelar as mudanças de produção.
