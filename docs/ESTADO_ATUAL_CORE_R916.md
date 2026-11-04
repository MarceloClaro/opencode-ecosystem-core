# Estado atual do Core — R916

Leitura local em 18/10/2026. Este documento descreve o checkout amostrado,
incluindo alterações ainda não commitadas. Não substitui validação de produção,
parecer científico externo ou autorização para operações concretas.

## O que foi observado

| Superfície | Resultado e alcance |
|---|---|
| Configuração OpenCode | 312 agentes, 16 MCPs e 33 comandos; padrão `ollama-local/llama3.2` |
| Doctor após R929 | 21 checks estruturais aprovados, 1 advertência e 0 falhas; `degraded`, `installation_only`. Advertência: 78 entradas históricas preservadas e não modeladas, sem migração inferida |
| Atlas | 711 módulos Python, 1014 pares e 22 fluxogramas; imports declarados, sem rastreamento de execução |
| NotebookLM | R915: 0.15.6, 53 ferramentas MCP, 165 callbacks CLI, 234 notebooks na sonda datada; 353 testes selecionados aprovados naquela revisão |
| Modelos OpenAI | Sondas sintéticas Luna e Sol aceitas no ensaio comum; primeiro ensaio Luna rejeitado por conteúdo |
| Gemini | CLI 0.61.0 instalado e autorização relatada pelo operador; sonda recusada por `UNSUPPORTED_CLIENT`, sem inferência observada |
| Ollama | `ollama show --modelfile llama3.2` não mostrou `num_ctx`; `gemma4:e2b-tuned` mostrou 24576; `ollama ps` vazio; sem inferência nesta inspeção |
| Plugins locais | Entradas MCP do Core, REA, MiroFish e Lean expostas no host; execução concreta exige recibo próprio |
| Extensão R920–R923 | MiroFish MIT: 21 casos/42 rounds/84 ações, sem validação científica. Sequence Viewer: instruções/licença importadas; Zotero: reference_only |
| ITS-FINE R924–R926 | 0.0.15: 15 skills/120 arquivos; instalador offline/SRI, verificador Core e três motores com dependências/sondas CPU aprovadas. GPU não disponível e testes upstream não distribuídos |

As sondas de modelos não enviaram código ou documentos do repositório. Não
foi medida economia em produção. Veja [comparação de modelos](architecture/MODELOS_E_ECONOMIA_DE_TOKENS_R916.md),
[pesquisa de quantização](architecture/QUANTIZACAO_LOCAL_GITHUB_R916.md) e
[evidência das sondas](evidence/r916/model-selection.json). Nenhum provedor
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
4. **MiroFish Offline externo.** A fonte atual exige endpoint loopback previamente
   ativo. A execução sintética histórica e o timeout posterior não comprovam
    disponibilidade atual sob carga. O gerenciador sob demanda foi removido.
    A extensão MIT local R920 executou cenários determinísticos sem endpoint,
    LLM ou equivalência demonstrada a pareceristas humanos.
5. **Lean 4.** A interface atual verifica uma declaração por entrada e recusa
    múltiplas declarações e sorryAx; não valida um arquivo inteiro pela primeira
    prova. Limita o processo a
    6 GiB de espaço virtual e heap Lean de 2 GiB. A regressão R923 ajustou o
    teto de 4 GiB, que impedia criar thread no compilador 4.34.1. Isso não
    amplia a interface aceita nem remove isolamento. O verificador legado da CLI admite
   `syntax_verified`. Nenhuma dessas condições comprova todas as fórmulas do
   livro ou pressupostos empíricos. Recibos antigos se referem a outros bytes.
6. **Escala e ciência.** Concorrência sob carga, orçamento de longo prazo,
    recuperação de falhas, revisão externa e validação empírica científica
    precisam de ensaios próprios. Um diagnóstico estrutural aprovado não fecha
    essas pendências.
7. **Ollama padrão do OpenCode.** O cliente ainda aponta a `llama3.2` e declara
    32768 no catálogo, mas o Modelfile observado não define `num_ctx`; o SDK R918
    consulta `/api/show` e bloqueia estimativas acima da janela, porém não
    intercepta o aplicativo OpenCode. Criar uma nova tag/modelo com contexto
    explícito requer decisão do operador, teste de memória e benchmark pareado.

## Origem e leitura do atlas

Base Git `b7f5683f84609a5e957a56af4ca090c905f5ab80`; identidade das fontes locais `1a170ef08b78071c65b55ee5cc0bb4821d77622b8326d018835dbf4a27d6ec7a`.

O manifesto registra 28 fontes modificadas e
52 caminhos removidos da base; o inventário contém
10267 arquivos rastreados presentes. Produção e configuração
usam bytes locais; as demais categorias usam metadados da base Git. Arquivos
não rastreados, incluindo os novos adaptadores R919–R923, não entram na coleta;
seus hashes e testes são registrados separadamente na evidência desta entrega.
O hash identifica a amostra, sem certificar correção. Não confundir essa origem
com um commit contendo todas as alterações funcionais locais.

Consulte o [atlas minucioso](ARQUITETURA_COMPLETA_CORE_R916.md), o
[mapa navegável](architecture_map.html), os [plugins](PLUGINS_LOCAIS_CORE.md),
as [autenticações](AUTENTICACAO_CHATGPT_NOTEBOOKLM.md) e o
[recibo da extensão documental](verification-documentation-r916-ollama-quantizacao.json).
O recibo anterior em `verification-documentation-r916.json` descreve outra
amostra/histórico. Evidências R879, R881, R912, R913 e R915 conservam seus escopos e datas.
