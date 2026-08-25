# Manual do OpenCode Ecosystem Core

Este manual descreve a interface disponível no checkout atual. Para arquitetura
técnica, consulte [ARCHITECTURE.md](ARCHITECTURE.md); para procedência e
instalação local, consulte [installer/README.md](installer/README.md).

> Os comandos produzem saídas operacionais locais. Elas não constituem
> certificação externa, garantia de resultado ou aconselhamento profissional.

## Estado estrutural

Na configuração consultada em **2026-08-23**, `doctor` relacionava **19 checks**,
e `opencode.json` continha **6 MCPs** e **209 agentes**. Execute os
comandos abaixo no seu checkout para confirmar o estado presente:

```bash
python3 -m marceloclaro.cli doctor
python3 -c "import json; c=json.load(open('opencode.json', encoding='utf-8')); print(len(c.get('mcp', {})), len(c.get('agent', {})))"
```

O diagnóstico pode retornar avisos ou falhas conforme as dependências locais.
Não use esta contagem como indicador de cobertura, qualidade ou validação
externa.

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
- **doctor**: diagnóstico estrutural; os 19 checks não substituem inspeção do
  ambiente nem avaliação externa.
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
```

| Comando canônico | Aliases tratados pelo CLI | Observação |
|---|---|---|
| `pesquisa` | `research` | Exige um tema; `--no-download` evita tentativa de baixar PDFs. |
| `apresentacao` | `present`, `mira` | A pasta deve conter `manuscrito.md`. |
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

`apm` aceita os subcomandos `init`, `install`, `compile`, `audit`, `pack` e
`list`. Para ver o resumo nativo de uso, execute
`python3 -m marceloclaro.cli ajuda`.

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

## Limites e solução de problemas

| Situação | Ação inicial |
|---|---|
| `doctor` aponta configuração inválida | Rode `python3 -m integrations.opencode_cli` somente após revisar as alterações esperadas em `opencode.json`. |
| CLI externa ausente | Use `helpdesk` e siga o procedimento local e versionado em `installer/README.md`. |
| Checkout não corresponde à revisão desejada | Pare e confira `git rev-parse HEAD` contra o commit Git informado pelo manifesto da versão. |
| Instalação de dependências falha | Recrie o ambiente virtual e use os manifestos de requisitos presentes no checkout revisado. |

Para alegações históricas e ressalvas, consulte [CORRIGENDUM.md](CORRIGENDUM.md).
