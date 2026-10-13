# Soluções GitHub e lacunas da orquestração

Pesquisa e decisões consolidadas em 12/10/2026. As capacidades externas abaixo
foram consultadas nos repositórios oficiais. A adequação ao Core é uma decisão
de arquitetura local; popularidade e descrições dos projetos não constituem
validação das integrações deste repositório.

| Lacuna ou necessidade | Fonte primária | Decisão e estado no Core |
|---|---|---|
| Análise estática de binários | [REA](https://github.com/MarceloClaro/rea), [Ghidra 12.1.4](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build) | Implementado R808/R823 pelo primário; análise real de ELF conhecido, hashes, sessão e limpeza registrados. |
| Navegação, leitura e interação web | [Playwright MCP](https://github.com/microsoft/playwright-mcp), [BrowserMCP](https://github.com/BrowserMCP/mcp) | Playwright MCP implementado R824 com sessão isolada em WSL, ações delimitadas e prova CLI/MCP. BrowserMCP com extensão permanece opcional. |
| Workflows persistentes, estados e interrupções | [LangGraph](https://github.com/langchain-ai/langgraph) | Avaliado como referência. O Core conserva o WorkflowCoordinator e os checkpoints existentes; R825 corrigiu a propagação de cancelamento e a retomada de etapas incertas. Nenhuma migração LangGraph foi realizada. |
| Colaboração por grafos e checkpoints | [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | Avaliado. Suporta padrões sequenciais, concorrentes e handoff. Um segundo framework exigiria adapter, migração de estado e novos testes; não foi adicionado ao caminho primário já existente. |
| Execução durável entre serviços | [Temporal Python SDK](https://github.com/temporalio/sdk-python) | Candidato se houver necessidade comprovada de workers e serviço distribuído. A execução documentada envolve um servidor Temporal e workers; não foi instalado nesta revisão local. |
| Persistência de workflows em banco | [DBOS Python](https://github.com/dbos-inc/dbos-transact-py) | Candidato se o produto exigir persistência transacional compartilhada. O README consultado descreve checkpoints e filas em Postgres; não foi introduzido um banco adicional nesta revisão. |
| Pesquisa com experimentos e redação | [AI-Researcher](https://github.com/HKUDS/AI-Researcher) | Avaliado como executor científico opcional. Exige piloto reproduzível, recursos e aceite próprios; não foi instalado nem usado como prova científica. |
| Formação e exercícios para pessoas | [SkillTree](https://github.com/NationalSecurityAgency/skills-service) | Opcional de capacitação; não é um runtime de skills de agentes. |
| Simulações de trajetórias | [fractalrabbit](https://github.com/NationalSecurityAgency/fractalrabbit) | Opcional de pesquisa com dados sintéticos explicitamente identificados; não demonstra melhoria de roteamento de agentes. |

## Mudanças que atendem às falhas observadas

O Core mantém `MarceloClaroOrchestrator` como entrada central. CLI e gateway
encaminham as novas ações ao primário e registram observações no MetaBus.
Não se duplicou o catálogo REA em cada agente. A capacidade de análise nativa
e a interação web têm provas executadas, distintas dos inventários de instalação.

A R825 corrigiu uma falha que adicionar um framework não resolveria por si só:
cancelar a requisição MCP podia abandonar uma thread em andamento, permitindo
a continuação do workflow. Agora há sinal por requisição, espera cooperativa
pela rede, recusa antes do próximo despacho e limpeza aguardada. A CLI POSIX
encerra seu grupo de processos; a prova local observou pais e filhos ausentes.
Cancelamento de um efeito já iniciado não prova reversão desse efeito.

A R824 recusou entradas inválidas antes de iniciar o provider, registrou
evidência integral e corrigiu o controle de redirects após uma contraprova
real. O proxy de sessão verifica destinos HTTP/CONNECT antes de abrir a conexão.
A origem autorizada é um limite do tráfego encaminhado ao proxy, sem promessa
de isolamento universal do sistema operacional ou funcionamento em todo site.

## Redução de ruído e preservação do histórico

Os guias operacionais recebem contagens e rotas geradas da configuração e do
diagnóstico atuais. O checkpoint antigo de PROGRESS foi preservado como histórico
datado; deixou de ser a indicação do estado vigente. Referências e exemplos
sem saída funcional foram corrigidos. As avaliações de 11/10 receberam uma
atualização datada com o que foi efetivamente implementado.

Bridges antigos ainda utilizados por consumidores e testes foram conservados.
Não foram tratados como arquivos mortos somente pela idade. Logs RED, provas
com limites, ciclos de evolução e dados científicos não foram apagados para
produzir um inventário aparentemente mais favorável.

## Evidências e limites

- [Documentação corrente](../outputs/core-r822/release-summary.json).
- [Ghidra e REA](../outputs/core-r823/summary.json).
- [Navegador real](../outputs/core-r824/release-summary.json).
- [Cancelamento e workflows](../outputs/core-r825/freeze-summary.json).
- [Planejamento de páginas](../outputs/core-r826/release-summary.json).
- [Cancelamento das demais rotas MCP](../outputs/core-r827/release-summary.json).
- [Avaliação NSA](AVALIACAO_PROJETOS_NSA.md) e [BrowserMCP/AI-Researcher](AVALIACAO_BROWSER_MCP_AI_RESEARCHER.md).

Inferência de cada provider, execução nativa no Windows, acesso a sessões
pessoais, eficácia científica e operação distribuída contínua não decorrem
desses recibos locais. Os resultados da suíte completa e do livro constam
na consolidação final da revisão R820.
