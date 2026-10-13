# Revisão do ecossistema — R820

Consolidação de 2026-10-13T11:56:24.826709+00:00. O conjunto atual passou na suíte
completa local: **7074 passed, 65 skipped, 7 warnings, 34 subtests passed in 1261.35s (0:21:01)**. O recibo registra retorno zero e hashes iguais
das fontes operacionais antes e depois da execução. Não há certificação externa nem
garantia de ausência de todas as falhas.

## Correções e execução observada

| Área | Correção ou resultado | Evidência |
|---|---|---|
| REA | Caminho central pelo marceloclaro/MetaBus e análise JavaScript real, com artefato integral e recibo compacto | [Execução](../outputs/core-r820/gateway-analysis-summary.json) |
| Integridade/doctor | Inventários, imports, aliases, especificações, overrides de executáveis e diagnóstico estrutural reconciliados | [Doctor final](../outputs/core-r820/doctor-after-final-suite.json) |
| Scanner científico | Contexto bilíngue de negação/modalidade, custo lexical reduzido e recusa MCP sem eco de entrada excessiva | [R815](../outputs/core-r815/corrective-summary.json) |
| Comandos OpenCode | 21 templates usam ferramenta JSON/allowlist e caminho primário; cancelamento e encerramento preservados | [R816](../outputs/core-r816/regression-summary.json) |
| Runtimes | RunAI e Tig instalados; RunAI executou chat, conclusão, embedding e ciclo de início/encerramento confirmado | [Inferência](../outputs/core-r817/central-inference.json), [ciclo real](../outputs/core-r817/central-lifecycle.json) |
| Matemática | Parsing restrito, divisão real, domínio de divisores/potências e recusa de resultados indefinidos; 283 regressões e 6/6 mutações detectadas | [R818/R821](../outputs/core-r820/math-domain-final-summary.json) |
| SDK OpenCode | ESM, tipos e imports; plugin retorna Hooks/ferramenta Zod/JSON representável sem cast ocultando contrato | [30 casos reais do plugin](../outputs/core-r820/plugin-sdk-final-summary.json), [tipos finais](../outputs/core-r820/typecheck-expanded-final.txt) |
| Documentação | Sete guias reconciliados, checkpoint histórico preservado e referências obsoletas corrigidas | [R822](../outputs/core-r822/release-summary.json) |
| Ghidra nativo | Versão 12.1.4 e JDK privado; função conhecida recuperada de ELF sem execução do alvo; cancelamento/timeout reais | [R823](../outputs/core-r823/summary.json) |
| Navegador | Fluxo real de leitura, preenchimento, clique e captura; CLI e MCP pelo primário; redirects bloqueados antes da conexão | [R824](../outputs/core-r824/release-summary.json) |
| Cancelamento/retomada | Sinal por requisição, fila cooperativa, limpeza aguardada e recusa do próximo nó após cancelamento | [R825](../outputs/core-r825/freeze-summary.json) |
| Demais rotas MCP | Operações canceladas na fila não iniciam após a liberação; worker permanece acompanhado | [R827](../outputs/core-r827/release-summary.json) |
| Planejamento Nano | Orçamento de páginas conservado; entradas e alocações inválidas recusadas | [R826](../outputs/core-r826/release-summary.json) |
| Capa e assets | Título inclui Core, subtítulo explicita validação computacional e coincide com a folha de rosto; imagens citadas têm hashes no inventário | [Capa](../outputs/core-r822/cover-release-summary.json), [assets](../outputs/core-r822/assets-release-summary.json) |
| Livro | Fontes reproduzíveis e inventário atualizado; 388 páginas compiladas, comparação integral de pixels e inspeção das páginas alteradas | [Aceite editorial e visual atualizado](../outputs/core-r822-refresh-20261013-rea/book-release-summary.json) |
| Revisão cega | Booleanos estritos, negações, parser restrito, categorias canônicas e numeral derivado do ledger | [Resposta técnica](REVISAO_CEGA_R828_R830_R832.md) |
| Histórico RED | Execução local autenticada, oráculo conservado e bloqueio de software sem par RED→GREEN; autocorreção bloqueada antes do patch e refatoração reprovada fecha o ciclo | [R839](../outputs/core-r839/release-summary.json), [uso](TDD_HISTORICO_RED.md) |
| Catálogo/oráculo | Cache limitado com leitura fresca e cópias independentes; alvo externo recusado pelo teste canônico; requisito R110 preservado | [R840 e gate real do Core](../outputs/core-r840/release-summary.json) |
| Rede visual | Terminal e painel observam memória, agentes e evidências; demonstração é explícita e consulta local não afirma inferência LLM | [R829](../outputs/core-r829/release-summary.json) |
| Assistente REA | CLI/MCP local, namespace privado, snapshots loopback, recibos por hash e explicação baseada na Evidence | [Execuções locais](../outputs/core-r850/live-summary.json), [guia](ASSISTENTE_REA_LOCAL.md) |
| Revisão REA | Encaminhamento JS, ativação efetiva do perfil, erros/guard, reuso do primário e cancelamento Ghidra corrigidos | [Revisão](../outputs/core-r862/root-review.json), [gate integrado](../outputs/core-r861/primary-delivery-accepted.json) |
| Identidade de spec | IDs ambíguos bloqueados; documentos históricos e trabalhos simultâneos preservados | [R862](../outputs/core-r862/identity-migration.json), [aceite](../outputs/core-r862/primary-delivery-accepted.json) |

Os oito problemas restantes da primeira suíte completa R820 foram corrigidos
antes desta execução. A tentativa seguinte foi interrompida após uma divergência
documental demonstrada; ela foi corrigida junto das novas integrações e do
planejador de páginas. Os logs anteriores, reproduções RED e casos de mutação
permanecem preservados; não foram substituídos pelo resultado verde.
A terceira tentativa registrou quatro falhas: rede externa no teste de dataset,
timeout de importação Lean, timeout isolado de comando e prazo de inicialização
confundido com limpeza Ghidra. R837 corrigiu os contratos reproduzidos; o comando
passou isoladamente. A suíte atual usa as fontes finais e preserva esses logs.
A quarta tentativa foi interrompida após um teste antigo exigir promoção por
reflection; o diagnóstico atual registra observation sem elevar confiança.
A quinta executou integralmente e encontrou duas falhas: latência R110 e unidade
de memória contaminada pelos registros das baterias anteriores. R840 conservou
o limite de cinco segundos, reduziu interpretação repetida do catálogo e isolou
os dados da unidade. A sexta foi interrompida sem falha de teste depois de uma
contraprova independente mostrar que o teste R840 aceitava candidato externo via
ambiente. O seletor foi removido do teste canônico, com RED adversarial por asserção
e GREEN; a versão anterior conservada e o produto corrigido foram reexecutados
com o mesmo oráculo final, obtendo um novo par RED→GREEN autenticado. Todos os
recibos anteriores foram conservados, sem convertê-los em aprovação das fontes finais.
A sétima tentativa passou antes das mudanças posteriores de REA; o resultado
permanece como snapshot datado. A execução atual inclui R841–R844, o assistente
R850/R851, a revisão R860/R861 e o guard de identidade R862. A colisão com os IDs
JEB/RX foi corrigida sem reclassificar os recibos antigos como outro contrato.
A oitava tentativa encontrou cinco falhas e quatorze erros de setup após o
registro passar a recusar specs ambíguas. As fixtures antigas conservavam parte
do estado formal entre testes; esse estado foi isolado, mantendo o bloqueio
estrito de IDs duplicados. A nona tentativa passou integralmente com as fontes
iguais antes e depois da execução. Os resultados da oitava permanecem arquivados.
Depois da nona, Click foi alinhado ao pin declarado pelo Core e o componente
optativo gTTS foi conservado em ambiente separado. Ambos os ambientes passaram
na verificação de dependências; os comandos afetados tiveram regressão própria.
A suíte integral não foi repetida depois dessa alteração de ambiente.
Além do raciocínio R838 (oito falhas em treze casos, depois treze aprovações),
cinco contratos de R828/R835/R836 foram reexecutados com nove snapshots anteriores
genuinamente preservados e dependências correntes identificadas: cinco asserções
falharam no RED e os mesmos cinco casos passaram no GREEN. Os pares possuem
assinatura local e data atual. A seleção é pontual; não equivale a um checkout
histórico completo nem reproduz todos os RED originais dessas frentes.
O histórico R839 é execução local atual; não preenche retroativamente registros
antigos incompletos e não valida a qualidade do oráculo ou fornece certificação externa.

## Inventário e histórico

A configuração atual declara **255 agentes, 16
servidores MCP e 30 comandos**. A prova de conexão dos 16
servidores está [registrada novamente](../outputs/core-r820/mcp-connections-after-final-suite.txt); conexão
não comprova toda a funcionalidade nem inferência de cada provider.

O doctor estrutural final passou em 22/22
checagens, com 0 avisos e 0 falhas.
O modo estrutural verifica instalação/configuração e não inicia modelos para
produzir uma alegação de execução.

Foram acrescentados os ciclos R814, R815, R816, R817, R818, R819, R821, R822, R823, R824, R825, R826, R827, R820, R835, R836, R837, R838, R839, R840, R850, R851, R860, R861, R862 por
`EvolutionRegistry.record`. Os 678 registros anteriores
foram preservados integralmente; o total passou a 703.
Os novos ciclos não recebem pontuação, selo de auditoria externa ou veredito
externo. [Recibo de preservação](../outputs/core-r820/evolution-record-receipt.json).

## Testes não executados na suíte completa

Os skips abaixo ficam explicitamente separados dos resultados aprovados.
As duas sondagens RunAI optativas foram executadas em uma bateria real própria;
isso não altera seu status optativo no JUnit global.

O console registra 7074 testes aprovados e 34 subtestes aprovados
separadamente. O JUnit contém 7173 casos, dos quais 7108
não têm falha, erro ou skip. Subtestes são incluídos no JUnit e não devem ser
somados novamente à sua contagem.

| Casos | Motivo registrado |
|---|---|
| 32 | teste externo desabilitado; defina OPENCODE_RUN_EXTERNAL_TESTS=1 |
| 12 | inferência LiteRT-LM real é opt-in; defina OPENCODE_RUN_EXTERNAL_TESTS=1 |
| 9 | Servidor externo indisponível; pulando. |
| 1 | Log não gerado ainda |
| 1 | OpenCode CLI nao disponivel neste ambiente |
| 1 | SPEC-935-R266: ficha_estudo_critico.pdf não presente no checkout -- já documentado como overclaim histórico em test_r265_r279_spec_deliverables.py::TestR266FichaEstudo |
| 1 | SPEC-935-R266: ficha_estudo_critico.tex não presente no checkout -- já documentado como overclaim histórico em test_r265_r279_spec_deliverables.py::TestR266FichaEstudo |
| 1 | Smoke real HTTP só executa sob RUNAI_REAL=1 |
| 1 | Smoke real do runai só executa sob RUNAI_REAL=1 |
| 1 | bun não está instalado |
| 1 | ficha_estudo_critico.tex não presente no checkout -- já documentado como overclaim histórico |
| 1 | fpdf2 indisponível |
| 1 | haystack-ai não instalado; smoke opcional |
| 1 | integração agy externa requer OPENCODE_RUN_EXTERNAL_AGY_TEST=1 e binário disponível |
| 1 | nenhum PDF real disponível |

## Limites e próximas integrações

REA anuncia 170 ferramentas; o provider Ghidra foi instalado e executado.
O registro atual tem 18 camadas, 16 prontas. Hopper tem prova específica em
R844; IDA e JEB permanecem pendentes. Prontidão não demonstra execução de todas
as camadas. O perfil local do assistente ainda tem marcador de modelo, sem
inferência comprovada. A análise JavaScript legada conserva 67
relações desconhecidas e cobertura semântica `unknown`, sem promoção de
confiança. Tig tem prova de instalação/CLI, sem prova de inferência.

A proteção dos templates não altera o parser upstream do OpenCode para
comandos inline. As fachadas matemáticas têm limites de entrada e de solver,
sem certificação de custo algébrico total ou de domínio universal. O plugin de
acesso aberto apenas orienta; DOI sintático e URL candidata não demonstram
existência de artigo, licença ou acesso aberto. O livro conserva avisos
editoriais não fatais detalhados no recibo de compilação.

A capa foi exportada em 2481×3508 pixels, 300 dpi, com textos vetoriais no PDF.
O retrato conserva o detalhe da fonte original, equivalente a aproximadamente
213 dpi em A4; a exportação não recupera detalhe fotográfico ausente.

O livro atual substitui a entrega anterior somente após novo aceite; os recibos
e PDFs anteriores foram conservados. A fonte intermediária encontrada antes
da atualização não foi apresentada como versão aprovada. A revisão visual do
último refresh foi realizada pelo primário; revisão independente ficou
indisponível por limite de uso e não é apresentada como executada.

As avaliações de [Ghidra, SkillTree e fractalrabbit](AVALIACAO_PROJETOS_NSA.md)
e de [BrowserMCP e AI-Researcher](AVALIACAO_BROWSER_MCP_AI_RESEARCHER.md) explicam
as prioridades e os critérios de implementação. Ghidra preencheu a lacuna
nativa do REA e o Playwright MCP implementou o navegador coordenado.
AI-Researcher permanece candidato a piloto científico limitado. A
[pesquisa e decisões de orquestração](SOLUCOES_GITHUB_ORQUESTRACAO.md) compara
também LangGraph, Agent Framework, Temporal e DBOS. Esses frameworks não foram
instalados; os checkpoints e o coordenador existentes foram corrigidos.

O proxy de navegador limita HTTP/CONNECT enviado a ele; não certifica todos os
canais de rede. O pacote MCP fixado utiliza uma dependência Playwright alpha,
registrada no lock. Cancelamento não demonstra reversão de efeitos já iniciados
nem certificação de Windows nativo. No timeout Ghidra, a limpeza dos processos
foi observada sem confirmação graciosa da sessão.

[Recibo completo e hashes](../outputs/core-r820/release-review.json).
