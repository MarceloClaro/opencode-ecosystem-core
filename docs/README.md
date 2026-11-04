# Documentação do OpenCode Ecosystem Core

Comece pelo [README principal](../README.md) e pelo [manual](../MANUAL.md).
Esta organização separa orientação atual, contratos específicos e registros de
execuções anteriores. Arquivos de evidência não são certificados de prontidão.

| Necessidade | Documento atual |
|---|---|
| Instalar e executar pela primeira vez | [Quickstart](../quickstart.md), [instalador](../installer/README.md), [one-click](../installer/ONECLICK.md) |
| Comandos, exemplos e estados | [Manual](../MANUAL.md) |
| Entender o sistema conectado | [Arquitetura técnica](../ARCHITECTURE.md), [guia R916](ARQUITETURA_COMPLETA_CORE_R916.md) |
| Explorar o mapa completo | [Atlas offline](architecture_map.html), [Mermaid integral](architecture/dependencies.mmd) |
| Conferir mudanças e pendências | [Estado atual R1045](ESTADO_ATUAL_CORE_R1045.md), [R916 histórico](ESTADO_ATUAL_CORE_R916.md), [PROGRESS](../PROGRESS.md) |
| Editar vídeo e animar | [Editor universal R1042](EDITOR_VIDEO_UNIVERSAL_R1042.md), [Remotion auditável](../.opencode/skills/remotion-auditavel/SKILL.md) |
| Dublar, legendar e diarizar | [Pipeline R1041–R1045](DUBBING_PIPELINE_R1041_R1045.md), [status do piloto](../pilots/r1035-02XpQTA-_XE/STATUS.md) |
| Ver evidência de vídeo real R1026 | [Aceitação R1046](../reports/r1046/QUANTUM-REAL-EVIDENCE.md), [pesquisa GitHub](../reports/r1046/github-research.json) |
| Dublar o piloto R1026 em PT-BR | [R1047](../pilots/r1026-quantum/r1047-dub/README.md), [evidência](../reports/r1047/QUANTUM-DUB-EVIDENCE.md) |
| Pesquisar skills Claude para vídeo, ciência e código | [Catálogo R1048](../reports/r1048-claude-skills-github/README.md), [JSON](../reports/r1048-claude-skills-github/candidates.json) |
| Adotar skills seletivas no Core | [Evidência R1049](../reports/r1049/README.md), [fontes pinadas](../reports/r1049/sources.json) |
| Consultar as 177 skills K-Dense | [Catálogo por categoria](../reports/r1049/kdense-177.md), [CLI](../integrations/kdense_catalog.py) |
| Ver as 9 adaptações originais | [Skill](../.opencode/skills/kdense-adaptacoes-originais/SKILL.md) |
| Auditar a macro-rede e o gate metacognitivo | [R1050](../reports/r1050/README.md), [grafo](../reports/r1050/macro-network.json) |
| Escolher ferramentas/modelos de vídeo | [Catálogo R1043](VIDEO_EDITOR_TOOLCHAIN_R1043.md), [toolchain.json](../reports/r1043/toolchain.json) |
| ChatGPT, Gemini e NotebookLM | [Autenticação](AUTENTICACAO_CHATGPT_NOTEBOOKLM.md), [NotebookLM](GEMINI_NOTEBOOK_CORE.md) |
| Reduzir custo de modelos/contexto | [Governança de custo de tokens](GOVERNANCA_DE_CUSTO_DE_TOKENS.md), [Modelos e tokens](MODELOS_E_CUSTO_DE_TOKENS.md) |
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
