# BrowserMCP e AI-Researcher no Core

Avaliação de 11/10/2026, baseada nos repositórios e documentos oficiais. As
prioridades abaixo são inferências de adequação ao Core. Este documento não
instala os projetos nem afirma que suas integrações já foram executadas.

## Atualização executada em 12/10/2026

A lacuna de navegador foi atendida pela R824 com o
[Playwright MCP oficial](https://github.com/microsoft/playwright-mcp), pacote
`@playwright/mcp@0.0.83`, Chromium e dependências instalados em runtime privado.
A escolha e os limites estão na [decisão de arquitetura](ADR-R824-NAVEGADOR.md).
O browser usa sessão isolada, sandbox habilitado e ações delimitadas por URL,
origens e alvo acessível, coordenadas pelo `marceloclaro`.

O fluxo real leu, preencheu, clicou, observou o resultado e produziu captura;
o gateway MCP registrou a evidência no MetaBus. O controle de redirects foi
corrigido após uma contraprova: um proxy de sessão verifica cada destino
HTTP/CONNECT antes da conexão. Essa prova limitada não certifica isolamento
universal de rede. Consulte o [manual atual](NAVEGADOR_REAL.md) e o
[recibo de execução](../outputs/core-r824/release-summary.json).

BrowserMCP, com extensão no navegador pessoal, e AI-Researcher não foram
instalados. O segundo continua candidato a piloto científico delimitado,
com recursos, execução e revisão próprios. O texto abaixo conserva a avaliação
original de 11/10, anterior à implementação do provider Playwright.

| Projeto | Prioridade proposta | Papel no ecossistema |
|---|---|---|
| BrowserMCP | Alta para fluxos que exigem navegador interativo | Provider opcional de navegação e interação, coordenado pelo agente `marceloclaro` |
| AI-Researcher | Alta como piloto científico, condicionada a orçamento e evidências | Executor de pesquisa isolado, com revisão e aceite pelo orquestrador central |

## BrowserMCP: conexão com um navegador real

O [BrowserMCP](https://github.com/BrowserMCP/mcp) combina um servidor MCP com
uma extensão do Chrome para operar o navegador do usuário. O README informa
que o repositório depende de pacotes de um monorepo e não pode ser compilado
isoladamente no estado documentado. A [instalação oficial do servidor](https://docs.browsermcp.io/setup-server)
usa o pacote publicado `@browsermcp/mcp`; também é necessária a configuração
da extensão. Em uma integração reproduzível, a versão do pacote deve ser
fixada depois de sua verificação, em vez de conservar `@latest`.

O inventário atual do OpenCode Core contém 16 servidores MCP e não configura
BrowserMCP. Menções a Playwright no catálogo ou preparação de instruções para
o Antigravity não comprovam que o navegador foi conectado e operado pelo Core.
A ferramenta de navegador disponível no ambiente Codex também é uma capacidade
distinta da configuração deste repositório.

A integração proposta mantém a coordenação em `MarceloClaroOrchestrator` e
limita as operações às tarefas autorizadas. Seu aceite inclui conexão real
com a extensão, abertura de uma página de teste, leitura de um elemento,
interação reversível, registro do resultado e recuperação de desconexão.
Snapshots e capturas devem guardar somente os dados necessários à evidência;
sessões autenticadas exigem cuidado com o conteúdo que é enviado ao modelo.
O uso local do navegador, por si só, não demonstra que todos os dados
permanecem locais em um fluxo que também utiliza um modelo externo.

## AI-Researcher: um executor científico com escopo delimitado

O [AI-Researcher](https://github.com/HKUDS/AI-Researcher) descreve um fluxo de
pesquisa que abrange literatura, ideias, implementação, experimentos e
redação. A instalação documentada envolve Python, Playwright, um ambiente
Docker para execução e configuração de modelos por API. A configuração admite
execução sem GPU, mas a viabilidade depende dos experimentos selecionados.

O [Dockerfile do projeto](https://github.com/HKUDS/AI-Researcher/blob/main/docker/Dockerfile)
usa uma imagem base `pytorch/pytorch:latest` e instala dependências científicas
e de navegador. Há divergência entre o comentário sobre a versão de
PyTorch/CUDA e a versão instalada. Isso justifica construir e testar uma
imagem fixada para o piloto, antes de afirmar reprodutibilidade nesse host.

O papel recomendado é um executor subordinado ao `marceloclaro`, aproveitando
os mecanismos existentes de workflow, isolamento, checkpoint e auditoria.
Não se introduz um segundo agente primário. Cada execução recebe objetivo,
fontes, critérios de aceite e limites de tempo, iterações, chamadas de modelo
e recursos. Os artefatos registram revisões do código, dados, parâmetros,
comandos executados, resultados e hashes. Resultados reais, simulações,
propostas e texto gerado permanecem identificados separadamente.

O aceite inicial deve usar uma tarefa pequena e conhecida: localizar fontes
primárias, reproduzir um experimento limitado e entregar código, resultados
e um texto que corresponda à execução. Revisão humana e validação externa,
quando necessárias, continuam pendentes até sua realização. Redação automática
e testes locais não equivalem a aprovação científica nem qualidade editorial
certificada.

## Relação com as outras propostas

O [Ghidra](AVALIACAO_PROJETOS_NSA.md) preenche uma lacuna concreta do provider
nativo REA e BrowserMCP adiciona interação web. AI-Researcher merece um piloto
controlado após os gates atuais. SkillTree depende de uma demanda de
capacitação de pessoas, e fractalrabbit de um experimento com trajetórias
sintéticas. Nenhum deles precisa tornar-se uma dependência obrigatória de
todo o Core.
