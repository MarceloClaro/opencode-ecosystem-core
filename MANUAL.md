# Manual do OpenCode Ecosystem Core

Este manual descreve a interface disponível no checkout atual. Para arquitetura
técnica, consulte [ARCHITECTURE.md](ARCHITECTURE.md); para procedência e
instalação local, consulte [installer/README.md](installer/README.md).

> Os comandos produzem saídas operacionais locais. Elas não constituem
> certificação externa, garantia de resultado ou aconselhamento profissional.

## Estado estrutural

As contagens atuais estão no bloco gerado abaixo. A referência local R916
foi conferida em 18/10/2026. Para repetir a conferência:

```bash
python3 -m marceloclaro.cli doctor
python3 -c "import json; c=json.load(open('opencode.json', encoding='utf-8')); print(len(c.get('mcp', {})), len(c.get('agent', {})))"
```

O diagnóstico pode retornar avisos ou falhas conforme as dependências locais.
Não use esta contagem como indicador de cobertura, qualidade ou validação
externa.

<!-- core-state:start -->
**329 agentes** · **25 MCPs** · **35 comandos** · **22 checks**

Inventário derivado de [opencode.json](opencode.json) e do [diagnóstico estrutural](marceloclaro/doctor.py). Contagens de configuração e checks não comprovam disponibilidade, autenticação, inferência ou validação externa.

Para conferir estes blocos, execute na raiz `.venv/bin/python scripts/reconcile_operational_docs.py --check`; para sincronizá-los, execute o mesmo comando sem `--check`.
<!-- core-state:end -->

O servidor
`ecosystem-network` liga o orquestrador, seu roteamento Transformer inspirado
em atenção e a memória MetaBus/Blackboard aos executores de análise e leitura
Claude, Antigravity e Codex disponíveis no ambiente. A execução limita passos
e tempo e reporta sucesso após conclusão; confira instalação e autenticação
locais. O identificador `chatgpt` não controla o aplicativo ChatGPT; selecione
`codex` explicitamente para usar sua CLI.

Para coordenar análise e revisão, peça no OpenCode: `/ecosystem analise esta
tarefa e depois peça revisão a outro especialista: ...`. A rede salva as
etapas e informa um identificador para consultar e retomar o trabalho. Veja o
[guia de execução em etapas](docs/WORKFLOWS_R644.md).

Para páginas web, consulte o [guia do navegador coordenado](docs/NAVEGADOR_REAL.md).

Para compreender aplicativos sem fontes, utilize o
[assistente REA local](docs/ASSISTENTE_REA_LOCAL.md): `rea inspect CAMINHO
--format text` inspeciona estaticamente e informa evidências e limitações;
`rea explain RECIBO --format text` lê o resultado. O setup gera os perfis MCP;
`rea agent --check` confere a configuração efetiva do cliente local antes da
conversa. `rea site --port 8767` abre o guia em loopback. O modo local exige
Linux/WSL com namespaces e um cliente que conserve os dados na máquina.

`python3 -m marceloclaro.cli browser status` confere a instalação sem iniciar
um navegador; `python3 -m marceloclaro.cli browser run ARQUIVO.json` executa
as ações explícitas daquele arquivo pelo orquestrador primário. Leitura e
snapshot observam a página; preenchimento e clique podem alterar o site.
Defina o efeito pretendido e as origens permitidas. A sessão isolada não
herda os logins do navegador pessoal e conserva evidência da execução.

Para execução externa de Hermes/MiroFish, download de datasets e plugins,
consulte o [guia das integrações científicas](docs/INTEGRACOES_CIENTIFICAS_R667_R671.md).
No OpenCode, use `/runtime-cientifico`, `/datasets` e `/plugins-cientificos`.

## Conexões, plugins e modelos

- [ChatGPT/OpenAI, Gemini/Google e NotebookLM](docs/AUTENTICACAO_CHATGPT_NOTEBOOKLM.md)
  usam autenticações distintas. Login não comprova inferência, cota ou
  autorização de uma operação específica.
- [NotebookLM 0.15.6](docs/GEMINI_NOTEBOOK_CORE.md): `/gemini-notebook` mantém
  a coordenação e os gates; o conector é comunitário e o serviço roda no Google.
- [Plugins locais](docs/PLUGINS_LOCAIS_CORE.md): REA, MiroFish e Lean 4 usam o
  mesmo primário; consulte os limites do código atual antes de reutilizar recibos.
- [Modelos e tokens](docs/MODELOS_E_CUSTO_DE_TOKENS.md): selecione por custo de
  tarefa aceita; assinatura, créditos e API têm métricas diferentes.
- [Atlas atual](docs/architecture_map.html) e [guia técnico](docs/ARQUITETURA_COMPLETA_CORE_R916.md)
  relacionam as interfaces, os fluxos e as fontes amostradas.

## Registrar e ativar agentes

Antes de criar um agente ou subagente de trabalho, use a entrada `agentes` da
CLI ou `ecosystem_agent_profile` pelo MarceloClaro. Reutilize um perfil quando
seu escopo já estiver coberto. Validação exige capacidades, origem, spec/teste,
permissões e contrato de saída; somente depois registre/ative o perfil e
correlacione o identificador A2A ao executor real. `pending_executor` é espera,
não execução. Consulte a [governança de agentes](AGENTS.md).

## Como começar

```bash
python3 -m marceloclaro.cli
```

Esse comando abre o menu interativo. Para evitar confusão entre a interface e
funções internas, o menu possui uma única opção `[10]`: a apresentação MIRA.

| Opção | O que faz |
|---|---|
| `[1]` | Lista agentes registrados. |
| `[2]` | Posta uma tarefa no Blackboard. |
| `[3]` | Reporta a conclusão de uma tarefa. |
| `[4]` | Consulta a memória metacognitiva. |
| `[5]` | Mostra o status geral. |
| `[6]` | Executa o doctor. |
| `[7]` | Exibe Ajuda. |
| `[8]` | Abre o helpdesk com orientações. |
| `[9]` | Inicia pesquisa científica. |
| `[10]` | Gera uma apresentação MIRA a partir de uma pasta com `manuscrito.md`. |
| `[0]` | Encerra o menu. |

### O vocabulário do menu

- **Blackboard**: fila compartilhada em que tarefas podem receber agentes.
- **Memória metacognitiva**: registros de contexto e reflexões do ecossistema.
- **doctor**: diagnóstico estrutural por padrão, com os checks do inventário acima;
  `doctor --live` executa probes locais e de rede. O inventário não substitui
  inferência executada, prova formal ou avaliação externa.
- **helpdesk**: leitura do diagnóstico com sugestões de próximos passos.
- **Ajuda**: resumo embutido do próprio CLI.

## Comandos diretos disponíveis

Os comandos abaixo correspondem a handlers presentes em
`marceloclaro/cli.py`. Os exemplos mostram a forma canônica; aliases são
aceitos apenas quando listados na tabela seguinte.

```bash
python3 -m marceloclaro.cli status
python3 -m marceloclaro.cli agents
python3 -m marceloclaro.cli doctor
python3 -m marceloclaro.cli helpdesk
python3 -m marceloclaro.cli ajuda
python3 -m marceloclaro.cli pesquisa "tema" --max-papers 8 --no-download
python3 -m marceloclaro.cli apresentacao caminho/da/producao
python3 -m marceloclaro.cli apm audit
python3 -m marceloclaro.cli amplify "pergunta" --model ox-alpha-free
python3 -m marceloclaro.cli aletheia "proposição" --domain math
python3 -m marceloclaro.cli deepthink "problema" --budget 3
python3 -m marceloclaro.cli alphaproof "meta"
python3 -m marceloclaro.cli erdos erdos --c 1
python3 -m marceloclaro.cli lean4 "código Lean ou caminho"
python3 -m marceloclaro.cli egraph "(+ (* x 1) 0)"
python3 -m marceloclaro.cli geometry midpoint_theorem
python3 -m marceloclaro.cli autoformalize "para todo x real, x + 0 = x"
python3 -m marceloclaro.cli shortcuts
python3 -m marceloclaro.cli clinical "queixa" --mode professional_cds
python3 -m marceloclaro.cli network status
python3 -m marceloclaro.cli network route "revisar o projeto" --ecosystem claude
python3 -m marceloclaro.cli quantum-catalog status
python3 -m marceloclaro.cli quantum-catalog buscar "variational" --limit 5
python3 -m marceloclaro.cli conhecimento fontes
python3 -m marceloclaro.cli conhecimento buscar "cirq" --fonte quantum_catalog --limite 5
```

| Comando canônico | Aliases tratados pelo CLI | Observação |
|---|---|---|
| `pesquisa` | `research` | Exige um tema; `--no-download` evita tentativa de baixar PDFs. |
| `apresentacao` | `present`, `mira` | A pasta deve conter `manuscrito.md`. |
| `podcast` | `audio` | Gera áudio m4a do `manuscrito.md` via Gemini Notebook (`nlm`, SPEC-972 — uso explícito do operador; `--title`, `--language`, `--length`, `--format`). |
| `amplify` | `amplificar`, `dsh` | Aceita opções de modelo, tipo e iterações. |
| `aletheia` | `prove`, `decompor` | Decompõe uma proposição; examine o estado retornado. |
| `deepthink` | `think` | Aceita orçamento e domínio. |
| `alphaproof` | `prover` | O resultado deve ser interpretado conforme o campo de estado retornado. |
| `erdos` | `conjecture`, `hirzebruch` | Aceita parâmetros compatíveis com o tipo selecionado. |
| `lean4` | `lean` | Recebe texto Lean ou caminho de arquivo local. |
| `egraph` | `saturate`, `egg` | Recebe expressão S-expression. |
| `geometry` | `alphageometry`, `wu` | Usa `midpoint_theorem` quando o tipo não é informado. |
| `autoformalize` | `formalize`, `crossval` | Recebe enunciado informal. |
| `shortcuts` | `atalhos` | Solicita a criação de atalhos pela rotina local. |
| `clinical` | `medico`, `anamnese` | Demonstra uma rotina de apoio; não substitui profissional habilitado. |
| `quantum-catalog` | — | Catálogo quântico local (SQLite, somente leitura na consulta). |
| `conhecimento` | — | Fachada comum de consulta às fontes de conhecimento locais. |

`apm` aceita os subcomandos `init`, `install`, `compile`, `audit`, `pack` e
`list`. Para ver o resumo nativo de uso, execute
`python3 -m marceloclaro.cli ajuda`.

### Catálogo quântico e fachada de conhecimento

O catálogo quântico é uma fonte local de consulta, derivada do JSON histórico
`outputs/pesquisa-inovacao-enfoque/quantica-repositorios.json` e materializada
em SQLite (`data/quantum_catalog/catalog.sqlite3`, gitignored). A importação é
explícita e idempotente; a consulta nunca importa, não executa repositórios nem
abre URLs.

```bash
python3 -m marceloclaro.cli quantum-catalog importar        # importa (uma vez)
python3 -m marceloclaro.cli quantum-catalog status          # inventário + hash da fonte
python3 -m marceloclaro.cli quantum-catalog listar --historico
python3 -m marceloclaro.cli quantum-catalog buscar "ruído" --category "Quantum simulators"
python3 -m marceloclaro.cli quantum-catalog ver org/cirq    # detalhe com proveniência
python3 -m marceloclaro.cli quantum-catalog historico       # snapshots importados
python3 -m marceloclaro.cli quantum-catalog painel          # exporta index_quantica.html
```

`conhecimento` consulta a fachada comum (`quantum_catalog` e `books`):

```bash
python3 -m marceloclaro.cli conhecimento fontes
python3 -m marceloclaro.cli conhecimento buscar "cirq" --fonte quantum_catalog --limite 5
```

No OpenCode, as mesmas operações de leitura estão em
`ecosystem_quantum_catalog` (status/list/search/get/history) e
`ecosystem_knowledge_query` (sources/search). Escritas (`importar`, `painel`)
são apenas da CLI. **TRL, licença, atividade e relevância são alegações da
fonte, não fatos verificados**; a busca é literal por tokens normalizados (sem
interpretar operadores). Consulte a [especificação R1002](specs/SPEC-935-R1002-quantum-catalog-source.md).

## Camada científica, conselho e sandbox

A fachada científica usa `python3 -m marceloclaro.scientific_lab`:

```bash
python3 -m marceloclaro.scientific_lab status
python3 -m marceloclaro.scientific_lab doctor
python3 -m marceloclaro.scientific_lab native-status
python3 -m marceloclaro.scientific_lab council list
python3 -m marceloclaro.scientific_lab council plan --question "pergunta"
python3 -m marceloclaro.scientific_lab author-editor brief --topic "tema"
python3 -m marceloclaro.scientific_lab scanner-evolve --corpus-json '[...]'
python3 -m marceloclaro.scientific_lab openshell preflight
```

| Comando | O que faz | Limite |
|---|---|---|
| `council list/plan/run` | Conselho de 13 cientistas (busca, revisão, análise, validação, auditoria). | `run` exige corpus, `--confirm` e executor real; votos não produzem verdade. |
| `author-editor structure/style/brief` | Estrutura IMRaD, perfil de estilo anti-plágio e plano de raciocínios. | Pontuação não vira Qualis/aceite; revisão humana obrigatória. |
| `scanner-evolve` | Compara candidatos de triagem em corpus dev/holdout. | Recomenda sem autopromover; corpus não é validação externa. |
| `openshell preflight/plan` | Inventário do sandbox OpenShell e plano de ensaios de isolamento. | Inventário não comprova isolamento; execução real é à parte. |

`council run` e `author-editor` enviam texto ao executor configurado (custo da
conta do serviço); a busca externa e a validação científica continuam distintas.
Consulte [conselho e scanners](docs/CONSELHO_CIENTIFICO_E_SCANNERS_R989_R990.md)
e o [procedimento OpenShell/Gemini](docs/PROCEDIMENTO_OPENSHELL_GEMINI_CONSELHO.md).

## Fluxos usuais

### Diagnosticar o ambiente

```bash
python3 -m marceloclaro.cli doctor
python3 -m marceloclaro.cli helpdesk
```

O primeiro mostra o estado dos checks; o segundo organiza sugestões. Se o
resultado for `degraded`, leia a lista de avisos antes de modificar o ambiente.

### Fazer uma pesquisa sem baixar arquivos

```bash
python3 -m marceloclaro.cli pesquisa "governança de IA" --max-papers 5 --no-download
```

Fontes, disponibilidade de rede e resultados variam. Examine o manifesto
retornado antes de reutilizar uma referência.

### Gerar uma apresentação MIRA

```bash
python3 -m marceloclaro.cli apresentacao caminho/da/producao
```

O pipeline MIRA percorre `extract`, `plan`, `copywrite`, `build`, `animate` e
`validate`. A etapa final registra conformidade do artefato segundo regras
internas; não avalia externamente o mérito científico do manuscrito.

## Usar os livros da biblioteca de IA

Os livros técnicos locais podem ser consultados pelo orquestrador, com arquivo,
página física e hash da fonte em cada resultado:

No OpenCode, use `/biblioteca tema da consulta`.

```bash
.venv/bin/python -m marceloclaro.cli biblioteca indexar
.venv/bin/python -m marceloclaro.cli biblioteca buscar "independência documento inteiro split" --top-k 3
```

O índice é local. Após substituir ou acrescentar um PDF, execute `indexar`
novamente. Fontes alteradas não fornecem trechos como se ainda estivessem
atuais. A interface MCP oferece catálogo, páginas, busca e prompt de revisão.

Para validar dados antes de fine-tuning, use `fine-dados validar dados.json`.
Esse comando confere pares e separação por fonte; ele não inicia treinamento.
Consulte os formatos, os livros usados e a evidência em
[Biblioteca de IA R657/R658](docs/BIBLIOTECA_AI_R657.md).

## Usar Gemini Notebook na orquestração

No OpenCode, use `/gemini-notebook tarefa`. O orquestrador consulta o catálogo
do conector comunitário instalado e coordena CLI, MCP e leitura da skill. Para inspecionar
esse catálogo pela CLI:

```bash
.venv/bin/python -m marceloclaro.cli notebook --config exemplos/notebook/catalog.json
```

Consulte [Gemini Notebook no Core](docs/GEMINI_NOTEBOOK_CORE.md) para login,
perfis, efeitos que precisam de confirmação, downloads e limites das provas.

## Inspecionar aplicações com REA

Use `/rea <tarefa>` no OpenCode. MarceloClaro consulta o servidor local e
coordena a análise com origem e evidências. Na CLI, use
`.venv/bin/python -m marceloclaro.cli rea status` ou
`rea analyze /caminho/absoluto/app`. Consulte [REA no Core](docs/REA.md)
para catálogo, disponibilidade e instalação identificada.

## Limites e solução de problemas

| Situação | Ação inicial |
|---|---|
| `doctor` aponta configuração inválida | Rode `python3 -m integrations.opencode_cli` somente após revisar as alterações esperadas em `opencode.json`. |
| CLI externa ausente | Use `helpdesk` e siga o procedimento local e versionado em `installer/README.md`. |
| Checkout não corresponde à revisão desejada | Pare e confira `git rev-parse HEAD` contra o commit Git informado pelo manifesto da versão. |
| Instalação de dependências falha | Recrie o ambiente virtual e use os manifestos de requisitos presentes no checkout revisado. |

Para alegações históricas e ressalvas, consulte [CORRIGENDUM.md](CORRIGENDUM.md).
