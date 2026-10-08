# Integrações científicas executadas — R667 a R671

O Core agora oferece execução externa de Hermes e MiroFish/OASIS, download
por Kaggle e Hugging Face CLI, composição rastreável de datasets e uma ponte
para os doze plugins solicitados. As operações entram pelo orquestrador
`marceloclaro`, registram observações no MetaBus e preservam a diferença entre
capacidade declarada, operação disponível, execução concluída e validação externa.

## Provas observadas em 2026-10-04

| Operação | Resultado observado | Limite do resultado |
|---|---|---|
| Hermes | CLI externa, duas chamadas ao `llama3.2:latest`, sessão e respostas registradas. | Ferramentas desabilitadas, perfil isolado; não demonstra todos os recursos do Hermes. |
| MiroFish | Script externo Twitter/OASIS, dois agentes, uma rodada, duas chamadas ao modelo e banco SQLite. | Personagens e cenário sintéticos; não é observação social ou previsão validada. |
| Hugging Face | `scikit-learn/iris`, CSV obtido pela CLI `hf`, commit fixado e SHA-256. | Metadados e licença declarados pela plataforma. |
| Kaggle | `uciml/iris/1`, ZIP versionado obtido pela CLI oficial e extração delimitada do CSV. | Arquivos versionados limitados a um pacote pequeno, com prévia de todos os tamanhos. |
| Dataset personalizado | 150 observações reais, 150 linhas de espelho reunidas, splits 106/22/22. | Iris em centímetros; sem ampliação de amostra ou mistura automática de áreas. |
| Wolfram | Cálculo efetivo do dilema dos prisioneiros: Nash (2,2); Pareto (1,1), (1,2), (2,1). | Índices começam em 1; cálculo hospedado, sem validação científica externa. |
| Genomic Intelligence | Catálogo de modelos de promotores lido pelo conector real. | Catálogo não é predição genômica. |
| NGS Analysis Workbench | Infraestrutura registrada lida pelo conector real. | Não houve execução de um workflow NGS. |
| Boltz | CLI oficial v0.43.0 instalada por artefato fixado com checksum; autenticação concluída. | Nenhum trabalho molecular foi submetido. |
| Life Sciences Literature | Pesquisa PubMed real pelo script instalado da skill Entrez. | Resultados bibliográficos; não implica leitura integral dos artigos. |

As provas ficam em:

- `docs/evidence/R671_REAL_20261004_195302/probe.json`: CLI/MCP, datasets, composição, runtimes e recibos no MetaBus.
- `docs/evidence/R670_HOST_REAL/probe.json`: respostas hospedadas vinculadas às requisições, autenticação Boltz e busca PubMed.
- `docs/evidence/R663_R666_REAL_20261004_165302/probe.json`: pergunta, fontes públicas reais, métodos Pearson/Welch, execução, reprodução em subprocesso, revisão computacional e exportação.
- `docs/evidence/R667_R671_GREEN.xml`: suíte específica final com 106 testes aprovados.
- `docs/evidence/R667_R671_REGRESSION.xml`: regressão com 777 testes aprovados e 9 testes condicionais ignorados.
- `docs/evidence/R667_R671_MUTATIONS.json`: quatro contraprovas detectadas: ausência de geração, fonte adulterada, ferramenta divergente e mutação do pacote por bytecode.
- `docs/evidence/R667_R671_RELEASE_GATE.json`: consolidação e hashes das evidências e fontes atuais.

Falhas anteriores permanecem arquivadas. O erro de arquivo individual Kaggle
foi corrigido usando o ZIP da versão explícita, com limite para todo o pacote.
A execução de scripts Python usa `-B` para preservar o pacote importado.

## Uso no Core

Os comandos OpenCode `/runtime-cientifico`, `/datasets` e
`/plugins-cientificos` usam o agente central. Na CLI, forneça um JSON e um
diretório de saída novo:

```bash
.venv/bin/python -m marceloclaro.cli ciencia runtime --config runtime.json
.venv/bin/python -m marceloclaro.cli ciencia dataset --config dataset.json
.venv/bin/python -m marceloclaro.cli ciencia personalizar --config custom.json
.venv/bin/python -m marceloclaro.cli ciencia plugins --config plugin.json
```

Exemplo `runtime.json`:

```json
{
  "runtime": "mirofish",
  "model": "llama3.2:latest",
  "prompt": "Simule duas personagens discutindo reprodução científica.",
  "output_dir": "docs/evidence/minha-simulacao-nova",
  "timeout_seconds": 180
}
```

Use `hermes` para a CLI Hermes. Os projetos externos devem estar instalados;
`runtime_dir` permite indicar outro checkout com origem Git permitida.
O modelo deve estar disponível em um servidor local compatível em
`http://127.0.0.1:11434/v1`. Uma consulta de saúde não completa a execução.
Timeout encerra os processos iniciados pela operação. Não há fallback simulado.

Exemplo `dataset.json`:

```json
{
  "provider": "kaggle",
  "dataset_id": "uciml/iris",
  "revision": "1",
  "filenames": ["Iris.csv"],
  "output_dir": "docs/evidence/meu-download-novo"
}
```

Para Hugging Face, use `provider: huggingface` e `dataset_id: scikit-learn/iris`.
A revisão é resolvida para um commit antes de baixar. O adaptador limita
download a 20 MB e bloqueia arquivo ausente, tamanho divergente e saída externa
ao workspace. Para Kaggle versionado, o pacote completo deve conter até dez
arquivos e caber no mesmo limite; não há download automático de pacotes grandes.

`custom.json` recebe `source_manifests`, `output_dir`, `name`,
`domain: botanical_measurements` e `seed`. Informe os manifestos retornados
pelos downloads. A composição valida hashes, licença e unidades, preserva
proveniência por linha, rejeita conflitos e mantém medidas idênticas no mesmo
split. Esse adaptador cobre Iris; outras áreas precisam de contrato semântico
e validação próprios. Não houve treino, upload ou publicação.

## Plugins e skills

Os doze pacotes estão em `.opencode/scientific-plugins/packages/`, com arquivos
e versões preservados no registro local. O cache original não foi alterado.

| Pacotes | Interface incorporada |
|---|---|
| Genomic Intelligence, Wolfram, NGS Analysis Workbench | Tickets para ferramentas conhecidas do host autenticado. |
| SciGrant | Workflow disponível por ticket quando houver intenção de redação de projeto. Não é usado como diagnóstico. |
| Plugin Management, Plugin Creator | Descoberta/metadados por ticket e instruções locais; nenhuma publicação realizada. |
| Boltz | Skills locais e operações delimitadas de versão e estado de autenticação da CLI. |
| Life Sciences Literature | Skills e busca PubMed por script validado. |
| data, cowork-plugin-management, anthropic-skills, AcademiXpertPlus KARIRI | Skills e materiais de apoio preservados, com leitura pelo dispatcher do orquestrador. |

Exemplo `plugin.json` para consultar o catálogo local:

```json
{"operation": "status"}
```

Para ler uma skill, use `operation: skill`, `plugin_id` e `skill_name`.
O resultado contém o documento, sua origem e a política de invocação. Uma skill
restrita é lida e executada no contexto do orquestrador conforme essa política;
importação de instruções não executa automaticamente scripts ou serviços.

Para um conector hospedado, use `operation: request`, `plugin_id`, `action` e
`arguments`. A saída `awaiting_host` inclui a ferramenta exata, o identificador
e o hash da requisição. O host Codex/OpenCode autenticado chama essa ferramenta
com os argumentos e devolve `operation: response` com `request_id`,
`request_sha256`, `host_tool`, `reported_by` e `result`. Consulte a resposta
com `operation: result` e `request_id`.

Essa ponte não inventa transporte OAuth nem copia credenciais para WSL.
O recibo identifica uma resposta reportada pelo host; não é autenticação
criptográfica independente. Ferramenta divergente, resposta de erro e reuso
do recibo são rejeitados ou mantidos como falha.

## Orquestração, metacognição e percurso científico

Os [oito perfis novos](AGENTES_R669.md), incluindo **Live mirofish hermes**,
entram no catálogo e são selecionados pelo Blackboard. A operação concreta
é feita pelos métodos centrais e registra uma observação com escopo e estado.
O MetaBus mantém a transição e o recibo de persistência, sem promover
automaticamente a confiança científica.

A prova R663/R666 foi reexecutada com o código atual: fontes bibliográficas
reais e Iris UCI, análise, reprodução, revisão computacional, artigo e código
e manifesto de origem. A revisão humana e a replicação independente permanecem
pendentes. Nenhuma das provas sustenta capacidade universal, classificação de
periódico, aplicação clínica ou generalização entre domínios.
