# Estado atual do Core — R916

Leitura local em 18/10/2026. Este documento descreve o checkout amostrado,
incluindo alterações ainda não commitadas. Não substitui validação de produção,
parecer científico externo ou autorização para operações concretas.

## O que foi observado

| Superfície | Resultado e alcance |
|---|---|
| Configuração OpenCode | 312 agentes, 16 MCPs e 33 comandos; padrão `ollama-local/llama3.2` |
| Doctor | 22/22 checks estruturais; `healthy`, `installation_only`; não fez inferência dos executores |
| Atlas | 707 módulos Python, 995 pares e 21 fluxogramas; imports declarados, sem rastreamento de execução |
| NotebookLM | R915: 0.15.6, 53 ferramentas MCP, 165 callbacks CLI, 234 notebooks na sonda datada; 353 testes selecionados aprovados naquela revisão |
| Modelos OpenAI | Sondas sintéticas Luna e Sol aceitas no ensaio comum; primeiro ensaio Luna rejeitado por conteúdo |
| Gemini | CLI 0.61.0 instalado e autorização relatada pelo operador; sonda recusada por `UNSUPPORTED_CLIENT`, sem inferência observada |
| Plugins locais | Entradas MCP do Core, REA, MiroFish e Lean expostas no host; execução concreta exige recibo próprio |

As sondas de modelos não enviaram código ou documentos do repositório. Não
foi medida economia em produção. Veja [comparação de modelos](MODELOS_E_CUSTO_DE_TOKENS.md)
e [evidência das sondas](evidence/r916/model-selection.json). Nenhum provedor
padrão ou credencial foi alterado nesta revisão.

## Pendências que permanecem

1. **Rigor acadêmico parcial.** A fachada `academic_rigor_action` e o serviço
   estão presentes. O padrão executa regras locais; `managed_profiles` tenta
   validar/ativar perfis pelo primário e mantém `awaiting_executor` sem saída
   do especialista. Os 34 cartões `research-*`, `profiles.py`, `scoring.py`, a
   CLI dedicada e a spec R914 estão removidos. A ausência da spec impede G0
   quando esse identificador é usado. Registros em `specialists.json` não
   comprovam agentes disponíveis ou inferência. `_academic_preflight` não
   tem chamador no código amostrado; não é uma etapa automática dos manuscritos.
   A operação `banca_rate` chama `sessions.rate`, ausente em `BancaSessionStore`;
   não há pontuação funcional demonstrada por essa rota. Essa frente tem
   alterações concorrentes e não foi concluída pela revisão documental.
2. **Três operações nativas de grafo bloqueadas.** O adaptador de contexto
   preserva falhas conhecidas; `python_graph` fornece extração estática local.
   O fallback não transforma o backend bloqueado em operacional.
3. **CI remota.** O bloqueio de cobrança informado na execução GitHub continua
   pendente. A alternativa `ci-local` executa grupos fechados do perfil
   científico, gera recibos locais e declara `github_check_created=false`.
   Esta revisão não reexecutou a CI remota ou a suíte integral.
4. **MiroFish Offline.** A fonte atual exige endpoint loopback previamente
   ativo. A execução sintética histórica e o timeout posterior não comprovam
   disponibilidade atual sob carga. O gerenciador sob demanda foi removido.
5. **Lean 4.** O plugin atual extrai o primeiro teorema e limita o processo a
   4 GiB de espaço de endereçamento. O verificador legado da CLI admite
   `syntax_verified`. Nenhuma dessas condições comprova todas as fórmulas do
   livro ou pressupostos empíricos. Recibos antigos se referem a outros bytes.
6. **Escala e ciência.** Concorrência sob carga, orçamento de longo prazo,
   recuperação de falhas, revisão externa e validação empírica científica
   precisam de ensaios próprios. Um diagnóstico estrutural aprovado não fecha
   essas pendências.

## Origem e leitura do atlas

Base Git `84ef0820a71f52756203854ea83d5a1211d8c254`; identidade das fontes locais `19e1b500a9d05bd7d2633a60b4c203f52ce8abc5697773afec55ee6386fce8f1`.

O manifesto registra 18 fontes modificadas e
52 caminhos removidos da base; o inventário contém
10222 arquivos rastreados presentes. Produção e configuração
usam bytes locais; as demais categorias usam metadados da base Git. Arquivos
não rastreados, incluindo a frente R917 em trabalho, não entram na coleta.
O hash identifica a amostra, sem certificar correção. Não confundir essa origem
com um commit contendo todas as alterações funcionais locais.

Consulte o [atlas minucioso](ARQUITETURA_COMPLETA_CORE_R916.md), o
[mapa navegável](architecture_map.html), os [plugins](PLUGINS_LOCAIS_CORE.md),
as [autenticações](AUTENTICACAO_CHATGPT_NOTEBOOKLM.md) e o
[recibo documental](verification-documentation-r916.json). Evidências R879,
R881, R912, R913 e R915 conservam seus escopos e datas.
