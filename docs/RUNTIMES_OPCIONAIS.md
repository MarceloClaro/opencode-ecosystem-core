# Instalações locais de RunAI e Tig

Em 11/10/2026, os dois runtimes foram instalados fora do ambiente Python do
Core. Os lançadores em `/usr/local/bin` apontam para instalações do usuário;
nenhum executável preexistente foi substituído. O diagnóstico também encontra
CLIs da `.venv` do projeto ao ser iniciado pelo Python do sistema, respeitando
overrides explícitos e permissões de execução.

## RunAI

Fonte oficial: [midudev/canirun.ai](https://github.com/midudev/canirun.ai),
commit `cc10946fc491f047f18ff8b5537759c45af7c9fc`, pacote 0.2.1, Bun 1.4.0 e
pnpm 11.22.0. O checkout está em
`~/.local/share/opencode-core/canirun-ai`. A instalação npm indicada pelo
instalador remoto respondeu 404; o Core agora orienta a instalação pela fonte.

Na raiz de um checkout oficial com Bun e pnpm disponíveis:

```bash
pnpm install --frozen-lockfile --filter @canirun/runai...
pnpm packages:build
pnpm --filter @canirun/runai build
```

O modo fonte do Core usa `RUNAI_SOURCE_DIR`, `RUNAI_BUN_BIN` e
`RUNAI_PNPM_BIN` quando esses programas estão fora do PATH. O lançador local
registrado nesta rodada usa caminhos absolutos para Bun e `dist/cli.js`,
preservando os argumentos. Para ajuda, use `runai --help`; opções após um
subcomando podem não interromper sua execução no upstream.

`runai doctor --json` carregou os bindings nativos e identificou três modelos
GGUF já existentes. O equipamento utiliza CPU; avisos de ausência de GPU
permanecem explícitos no diagnóstico upstream. Não foram baixados novos
modelos para esta validação.

A prova real via `MarceloClaroOrchestrator` usou `llama3.2-1b`: chat retornou
`Paris.`, completion retornou `4` e embedding teve 2.048 dimensões. Os dois
testes reais HTTP passaram. Outra prova iniciou e encerrou o daemon pela
interface central. Esses casos confirmam execução local desse modelo;
não medem qualidade geral, não habilitam todos os modelos e não são validação
científica externa.

A saúde HTTP exige `ok=true`, `service=runai` e PID inteiro positivo. `stop`
não reporta sucesso quando o servidor identificado continua respondendo,
mesmo se a CLI retornar código zero.
Timeouts, erros HTTP e identidades inválidas deixam o término sem confirmação;
somente uma conexão recusada confirma ausência do servidor no endereço.

## Tig

[tig-code](https://pypi.org/project/tig-code/) 0.1.7 está instalado na venv
isolada `~/.local/share/opencode-core/tig-env`, com Python 3.12.14. A instalação
foi feita por `uv pip install --python <venv>/bin/python tig-code==0.1.7`.
`tig --help` foi executado e retornou zero. Ripgrep 15.1.0 também foi instalado.

O Tig exige escolha de provedor/modelo para execução do agente. Essa rodada
comprovou instalação e ajuda; não atribui inferência ao Tig nem configura
credenciais de terceiros. A ajuda emite um aviso de compatibilidade entre
LlamaIndex e Pydantic; o aviso permanece no recibo e não foi ocultado.

## Evidências

`outputs/core-r817/installation-receipt.json` registra versões, origem,
lançadores, comandos reais e hashes. `central-inference.json` conserva as
respostas completas. `central-lifecycle.json`, `runai-real-tests.txt`,
`runai-doctor.json` e `doctor-live-after.json` registram as provas operacionais.
O recibo de instalação tem `inference_executed=false` porque antecede a
sondagem: a inferência posterior está documentada separadamente.

Specs R817/R819 e as contraprovas preservam a diferença entre instalação,
prontidão operacional, inferência local e validação externa.
