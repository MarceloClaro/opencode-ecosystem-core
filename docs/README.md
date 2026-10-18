# Documentação do OpenCode Ecosystem Core

Comece pelo [README principal](../README.md) e pelo [manual](../MANUAL.md).
Esta organização separa orientação atual, contratos específicos e registros de
execuções anteriores. Arquivos de evidência não são certificados de prontidão.

| Necessidade | Documento atual |
|---|---|
| Instalar e executar pela primeira vez | [Quickstart](../quickstart.md), [instalador](../installer/README.md) |
| Comandos, exemplos e estados | [Manual](../MANUAL.md) |
| Entender o sistema conectado | [Arquitetura técnica](../ARCHITECTURE.md), [guia R916](ARQUITETURA_COMPLETA_CORE_R916.md) |
| Explorar o mapa completo | [Atlas offline](architecture_map.html), [Mermaid integral](architecture/dependencies.mmd) |
| Conferir mudanças e pendências | [Estado atual R916](ESTADO_ATUAL_CORE_R916.md), [PROGRESS](../PROGRESS.md) |
| ChatGPT, Gemini e NotebookLM | [Autenticação](AUTENTICACAO_CHATGPT_NOTEBOOKLM.md), [NotebookLM](GEMINI_NOTEBOOK_CORE.md) |
| Reduzir custo de modelos/contexto | [Modelos e tokens](MODELOS_E_CUSTO_DE_TOKENS.md) |
| Usar plugins privados | [Plugins locais](PLUGINS_LOCAIS_CORE.md), [Core no ChatGPT](USAR_CORE_NO_CHATGPT.md) |
| Engenharia reversa | [REA](REA.md), [assistente local](ASSISTENTE_REA_LOCAL.md) |
| Agentes, plugins, grafo e CI | [Guia R894–R897](ORQUESTRACAO_AGENTES_PLUGINS_CI_R894_R897.md) |
| Fluxos retomáveis | [Workflows](WORKFLOWS_R644.md) |
| Navegação controlada | [Navegador](NAVEGADOR_REAL.md) |
| Biblioteca e busca | [Biblioteca R657](BIBLIOTECA_AI_R657.md) |
| Ciência, runtimes e datasets | [Integrações R667–R671](INTEGRACOES_CIENTIFICAS_R667_R671.md) |
| Corrigir alegações históricas | [CORRIGENDUM](../CORRIGENDUM.md) |
| Contribuir com agentes | [AGENTS](../AGENTS.md), [CLAUDE](../CLAUDE.md) |

## Como ler as evidências

`specs/` declara requisitos; `tests/` contém verificações; `docs/evidence/`
preserva recibos públicos delimitados; `outputs/` pode conter dados locais e
resultados privados. Hash confirma identidade de bytes, não a verdade da
conclusão. Não copiar sessões, cookies, chaves ou fontes privadas para o Git.

Os atlas R433–R438, R879, R900 e R911 permanecem como retratos históricos. O
livro possui processo editorial e atlas próprios; atualizar estes mapas não
recompila nem revalida automaticamente o livro ou seus teoremas.
