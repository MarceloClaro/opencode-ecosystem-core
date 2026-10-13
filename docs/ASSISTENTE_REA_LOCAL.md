# Assistente REA local

O assistente inspeciona artefatos por CLI e MCP stdio, coordenado pelo primário
MarceloClaro. A saída distingue instalação, prontidão da camada e análise
realmente executada. A explicação dos recibos é determinística; um LLM não é
requisito para inspeção ou leitura dos resultados.

As operações `rea layers` e `rea layer --layer ID CAMINHO` continuam disponíveis
na ponte do Core para inventário e inspeção das camadas R841. `--encoding raw|hex`
é aceito somente na camada EVM. Para a inspeção com isolamento de rede descrita
neste guia, utilize `rea inspect`; a ponte legada não aplica o novo namespace
por conta própria. Prontidão de uma camada não comprova sua execução.

## Início no Ubuntu/WSL

Execute os comandos a partir da raiz deste repositório. A instalação local
utiliza o interpretador de `.venv`.

```bash
.venv/bin/python -m marceloclaro.cli doctor
.venv/bin/python -m marceloclaro.cli rea setup
.venv/bin/python -m marceloclaro.cli rea inspect CAMINHO --kind auto --format text
.venv/bin/python -m marceloclaro.cli rea explain RECIBO --format text
```

Substitua `CAMINHO` por um artefato que você tem autorização para examinar e
`RECIBO` pelo caminho informado pela inspeção. A detecção automática usa
assinatura/extensão; um tipo reconhecido não implica que seu provedor está
pronto ou que a análise produzirá uma reconstrução completa.

O setup gera um perfil de agente local e exemplos de conexão MCP Linux e
Windows/WSL sem substituir a configuração global do operador. Os caminhos
efetivamente gravados são informados na saída. Para uma conversa com agente,
utilize modelo disponível em endpoint loopback e confirme sua inferência
separadamente; configuração não equivale a inferência executada.

Para ativar o perfil no OpenCode, primeiro escolha um modelo que já esteja
servido localmente e confira a configuração efetiva:

```bash
.venv/bin/python -m marceloclaro.cli rea setup --model NOME_DO_MODELO --model-endpoint http://127.0.0.1:11434/v1
.venv/bin/python -m marceloclaro.cli rea agent --check
.venv/bin/python -m marceloclaro.cli rea agent
```

`agent` abre o cliente com HOME/XDG próprios, diretório temporário fora do
projeto e somente o MCP local do assistente. `--check` não executa inferência.
O valor padrão `modelo-local` é um marcador de configuração, não um modelo
instalado. Para uma mensagem direta, utilize `agent --prompt "sua pergunta"`.

Não ative este modo apenas com `OPENCODE_CONFIG`: o OpenCode combina
configurações, e a configuração do projeto pode sobrepor esse arquivo. O
lançador confere o modelo, o primário, os MCPs, as permissões e a ausência de
plugins herdados antes de iniciar a conversa. Veja a
[precedência oficial de configuração](https://opencode.ai/docs/config/).

## MCP stdio

O cliente inicia o servidor como processo local:

```bash
.venv/bin/python -m integrations.rea_assistant_mcp
```

Use os perfis gerados pelo setup, que contemplam execução Linux e o lançamento
via WSL no Windows. MCP stdio entrega dados ao cliente. O cliente precisa
conservar a política de processamento local; um cliente que depois remete os
dados à nuvem está fora da garantia desta configuração.

## Site de instruções

```bash
.venv/bin/python -m marceloclaro.cli rea site --port 8767
```

Abra [o guia local](http://127.0.0.1:8767/). O servidor permanece ativo até
`Ctrl+C`; a porta pode ser alterada. A API Python é
`webapp.rea_assistant_site.serve_instructions(*, port=8767)`.

O site responsivo em português utiliza apenas recursos locais. Ele apresenta
instruções, exemplos ilustrativos, fluxo de execução e comandos copiáveis;
não analisa aplicativos pelo navegador. Não possui upload, telemetria, CDN ou
dependência de recursos externos.

O servidor vincula exclusivamente `127.0.0.1`, aceita somente GET para `/`,
`/index.html`, `/styles.css`, `/script.js` e `/favicon.svg`, e não converte
caminhos da requisição em caminhos de disco. Host e Origin externos ou de outra
porta são recusados, bem como caminhos não canônicos e traversal. A política
do navegador bloqueia conexões, formulários e enquadramento por outros sites.
Isso não representa um servidor público de produção.

## Entradas e limites

| Entrada | Rota | O que pode estabelecer |
| --- | --- | --- |
| JavaScript/Electron | Provedor JavaScript REA | Sinais e estrutura estáticos; não executa a aplicação |
| ELF/PE/Mach-O | Ghidra instalado, quando pronto para a operação | Achados do provedor no arquivo; suporte depende do formato e da análise |
| Assembly .NET | Inspeção de metadados | Estrutura e metadados; não comprova recuperação integral das fontes |
| HTML e arquivos exportados | Inspeção de estrutura | Referências e conteúdo do arquivo; não executa JavaScript |
| URL literal loopback | Snapshot local | Conteúdo obtido sem redirects, proxy herdado ou JavaScript; não testa comportamento dinâmico |
| IDA/Hopper/JEB |    comerciais opcionais | Dependem de licença e configuração; não estão prontos apenas por constarem do inventário |

Exemplos abaixo são **ilustrativos**, não execuções nem arquivos fornecidos:

```bash
.venv/bin/python -m marceloclaro.cli rea inspect ./aplicativo.js --kind auto --format text
.venv/bin/python -m marceloclaro.cli rea inspect ./aplicativo --kind auto --format text
.venv/bin/python -m marceloclaro.cli rea inspect ./Biblioteca.dll --kind auto --format text
.venv/bin/python -m marceloclaro.cli rea inspect ./pagina.html --kind auto --format text
```

O worker analítico exige namespaces Linux de usuário, rede e PID, com somente
loopback privado e sem saída para o host ou internet. Ausência do isolamento
bloqueia a análise. A aplicação alvo não é executada. Isolamento de rede não é
sandbox universal de arquivos nem proteção contra o proprietário do host.

O REA aceita diretório ou `.asar` na análise JavaScript. Para um arquivo avulso,
o assistente prepara uma cópia temporária dos mesmos bytes e informa que imports
e arquivos vizinhos não foram incluídos. O recibo mantém o hash do arquivo
original. Nenhum código JavaScript é avaliado durante essa adaptação.

## Evidência e leitura do resultado

Fluxo: agente local → CLI/MCP → MarceloClaro → REA → provedores → EvidenceLedger
→ achados e limites. O site apresenta esse fluxo em SVG, com IDA/Hopper/JEB
explicitamente opcionais.

Instalação indica componente localizado; prontidão indica pré-requisitos e
configuração; execução exige evidência identificada da operação solicitada.
Examine no recibo o alvo, seus hashes, o provedor/versão, a operação, os
identificadores dos achados e os limites. Uma hipótese ou sinal estático não
comprova comportamento dinâmico, equivalência funcional ou segurança do alvo.

## Verificação da implementação

```bash
.venv/bin/python -m pytest -q tests/test_r841_rea_layers.py tests/test_r851_rea_assistant_site.py tests/test_r850_rea_assistant_local.py tests/test_r860_rea_runtime_review.py
```

O contrato do site está em `specs/SPEC-935-R851-site-assistente-rea.md` e seus
testes fazem requisições HTTP reais em porta loopback temporária. A interação
de cópia executa o script entregue em Node com um adaptador mínimo DOM/Clipboard;
esse teste não substitui inspeção visual ou integração real do cliente MCP.
O contrato do backend é R850. Os recibos públicos do histórico do site ficam
em `outputs/core-r851`; o estágio inicial de API ausente fica separado do RED
funcional. Resultados locais não são validação externa da qualidade analítica.
