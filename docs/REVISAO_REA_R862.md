# Revisão local da integração REA

Esta revisão utiliza leitura do checkout e execução local. Não representa
validação externa, recuperação integral de fontes ou garantia de ausência de
todas as falhas. A decisão de publicação e de uso dos resultados permanece humana.

## Lista R841 conferida

- [x] `integrations/rea_layers.py`: registro, sonda de prontidão e descoberta dos motores.
- [x] `integrations/rea_bridge.py`: `layers/layer`, schema do tool conferido no handshake e Evidence da operação solicitada.
- [x] `marceloclaro/rea_cli.py`: `layers/layer/--layer/--encoding`, com recusa de combinações inválidas.
- [x] Docstring `ecosystem_rea` e template `/rea`: encaminhamento pelo primário e distinção entre prontidão e execução.
- [x] Unblob, Apktool e Binwalk presentes; cinco submódulos inicializados e commits registrados.
- [x] `specs/SPEC-935-R841-rea-camadas-provedor.md` presente.
- [x] `tests/test_r841_rea_layers.py` executado, junto às regressões de configuração/comandos.

A sonda corrente identificou **18 camadas, 16 prontas e 2 pendentes**: IDA e JEB
precisam de registro/serviço local explícito. Prontidão é resolução de requisitos,
não execução nem comprovação de licença. O snapshot R841 de 11/18 permanece
histórico. Unblob 26.6.4, Apktool 2.7.0-dirty e Binwalk 3.1.0 responderam às sondas
de versão; isso não demonstra análise bem-sucedida de qualquer firmware/APK.
Veja [a conferência de motores](../outputs/core-r852/engine-recheck.json).

## Falhas reproduzidas e corrigidas

| Falha observada | Correção | Evidência |
| --- | --- | --- |
| Arquivo JS avulso enviado a uma operação que aceita diretório ou `.asar` | Cópia temporária dos mesmos bytes; imports/arquivos vizinhos ausentes declarados | [Falha original](../outputs/core-r850/initial-live-attempt/javascript-stdout.txt), [execuções](../outputs/core-r850/live-summary.json) |
| Configuração do projeto sobrepunha `OPENCODE_CONFIG` e reativava os MCPs | Cliente em cwd/HOME próprios, configuração inline local e verificação efetiva | [Antes](../outputs/core-r850/profile-precedence-before.json), [check](../outputs/core-r852/agent-check-cli.txt) |
| Endpoint/comando MCP/permissão do primário poderiam divergir no resultado resolvido | Comparação estrita antes de conversar; divergência bloqueia lançamento | [Contraprovas](../outputs/core-r852/resolved-guard-red.xml) |
| Guard falho ainda reportava sucesso e erro do worker perdia detalhes | Conjunção de prontidão, booleanos/prazos tipados e erro estruturado preservado | [RED](../outputs/core-r860/core-current-oracles-red-cli.txt), [GREEN](../outputs/core-r860/core-final-oracles-green-cli.txt) |
| Um novo primário por chamada MCP acumulava subscrições | Inicialização única por servidor, protegida por lock | [RED de reuso](../outputs/core-r852/mcp-primary-reuse-red.xml) |
| Specs de mesmo ID eram sobrescritas pela ordem de arquivos | IDs próprios R860/R861; R440 qualificado; IDs ambíguos ficam indisponíveis | [Migração](../outputs/core-r862/identity-migration.json), [gate](../outputs/core-r862/primary-delivery-accepted.json) |

Os trabalhos simultâneos JEB/R852 e RX/R853 não foram removidos ou renomeados.
Os dois corpos históricos R440 foram preservados, com identificadores derivados
de seus nomes de arquivo. Uma recarga do mesmo caminho é permitida; duas
definições em caminhos diferentes não escolhem uma vencedora. As fixtures de
teste isolam também o registro de caminhos formais entre projetos temporários.

## Assistente e execução real

O [guia de uso](ASSISTENTE_REA_LOCAL.md) descreve `rea setup`, `inspect`,
`explain --format text`, `agent --check` e `site`. O primário MarceloClaro
coordena CLI e MCP. Quatro tools MCP locais anunciam schemas de entrada;
status, inspeção e explicação foram chamados por uma sessão stdio real.

Os alvos controlados foram JavaScript/Electron, ELF via Ghidra 12.1.4,
HTML/URL literal loopback e uma fixture PE32/CLI de metadados .NET gerada da
fonte do REA. Essa fixture não é um aplicativo .NET de produção compilado.
Hashes da entrada foram preservados. O ELF possuía sentinela de execução;
ela permaneceu ausente. O cancelamento chegou a observar Java/Ghidra real e
terminou sem descendentes vivos pertencentes ao pedido.
Veja [MCP real](../outputs/core-r850/mcp-live.json) e
[cancelamento real](../outputs/core-r850/cancellation-live.json).

O worker utiliza namespaces Linux de usuário, rede e PID, com somente loopback
privado. Sem isolamento, a análise é bloqueada. Isso não é sandbox universal
de arquivos. O cliente MCP e o servidor de modelo precisam conservar os dados
localmente; clientes que encaminhem o conteúdo à nuvem ficam fora desse modo.
O modelo padrão é um marcador de configuração: **nenhuma inferência desse perfil
foi comprovada**. A explicação determinística funciona sem LLM.

O site foi exercitado em navegador real desktop/mobile, com cópia de comandos,
sem erro de página, sem transbordamento da página e somente recursos de origem
local. Não possui upload nem endpoint de análise.
[Recibo do navegador](../outputs/core-r851/browser-receipt.json).

## Histórico e limites de aceitação

R850: 16 falhas por asserção no baseline conservado → 16 aprovações. O RED
inclui bootstrap de interfaces novas, separado das falhas funcionais de
validação e CLI. Os quatro arquivos anteriores recuperados coincidiram
exatamente com os hashes do RED original; os três módulos novos estavam ausentes.

R860: 16 falhas e 1 aprovação → 17 aprovações. R861 integra 44 casos:
16 falhas e 28 aprovações no baseline parcial conservado → 44 aprovações.
R862: 2 falhas funcionais de identidade e 4 aprovações → 6 aprovações.
Essas são reexecuções com oráculos atuais, não criação retroativa de eventos
históricos ausentes. Os recibos anteriores permanecem preservados.

O gate atual do primário aceitou R861 e R862 com registros por critério e par
RED→GREEN correspondente. [Resumo dos contratos](../outputs/core-r862/rea-release-summary.json).
A suíte global e seus skips são apresentados na
[consolidação do ecossistema](REVISAO_ECOSSISTEMA_R820.md): 7.074 testes
aprovados, 65 não executados e 34 subtestes aprovados. Os hashes das fontes
monitoradas permaneceram iguais durante e após essa execução.

Click foi alinhado ao pin 8.4.2 declarado pelo Core depois da suíte integral.
O componente opcional gTTS, sem uso encontrado no código do Core, foi conservado
em ambiente separado para manter sua exigência de Click <8.2. Ambos os ambientes
passaram na conferência de dependências e os 160 testes afetados passaram em
regressão própria. A suíte integral não foi repetida após essa alteração de ambiente.
[Recibo de dependências](../outputs/core-r862/dependency-isolation.json),
[regressão afetada](../outputs/core-r862/post-dependency-regression.json).

A revisão independente desta extensão não foi concluída por limite de uso dos
revisores. A revisão do primário e as provas executadas estão registradas; isso
não se apresenta como parecer independente nem validação externa.
