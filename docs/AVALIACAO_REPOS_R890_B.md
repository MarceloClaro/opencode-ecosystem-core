# Avaliação dirigida R890 — voz, dispositivos e modalidades de entrada

Data: 14 de outubro de 2026. Grupo B: cinco repositórios solicitados pelo usuário.

Os projetos oferecem referências úteis para interfaces de voz, terminais ESP32 e organização de providers. A contribuição mais imediata ao Core é um contrato explícito de modalidade e política de rede antes do roteamento ou fallback. Não é adequado instalar cinco runtimes ou substituir o primário `MarceloClaro` por outro coordenador.

## Método e alcance

Foram consultadas as páginas GitHub e fixados os commits das branches padrão com clones bare rasos, `filter=blob:none`, sem checkout ou execução de scripts. A leitura dirigida abrangeu 87 arquivos selecionados, somando 1.071.710 bytes. Foram examinados licença, entrypoints, dependências, protocolos, providers, configuração de rede e referências de privacidade/analytics.

O [manifesto de avaliação](repo-reviews-r890-b.json) registra commit, data, SHA-256, tamanho e URL fixa de cada fonte. A amostra não é auditoria integral do código ou das dependências transitivas. Nenhum runtime destes cinco projetos foi instalado; não houve ativação de microfone, câmera, contas, ESP32 ou envio de mensagens. Não foram baixados modelos ou imagens/datasets.

| Projeto | Commit consultado | Arquivos / bytes | Decisão para o Core |
|---|---|---:|---|
| ASSISTENTE-SHI | `d60749a608b3c1317b527b491bfc50cafb98cecb` | 21 / 394.720 | Adaptar fronteiras de voz/visão e política de fallback; não importar o cliente inteiro. |
| py-xiaozhi | `2c6eca47873d19f5fc7227a1d0460926c1b55e69` | 16 / 197.890 | Referência do cliente ancestral; evitar duplicação com SHI. |
| xiaozhi-esp32-server | `1f6a89ada5375ac10f09c5246ef8c6f389aef167` | 19 / 169.790 | Referência para separar VAD/ASR/LLM/TTS e providers; adaptador opcional futuro. |
| xiaozhi-esp32 | `b48506171b89f25eff99f46d18ac7808cd3564b6` | 12 / 146.587 | Referência de dispositivo de borda e negociação de áudio/MCP; não executor de código no hospedeiro. |
| anny | `68a310e2a0eaa2dba1a9e0676525f99f94886bc4` | 19 / 162.723 | Baixa prioridade para orquestração; separar modelo de corpo e aplicação de classificação de pele presentes no fork. |

## REA como apoio: execuções e limites

As operações passaram por `MarceloClaroOrchestrator(auto_load_agents=False)`. O REA foi usado somente onde havia alvo compatível; leitura de Python/C++ não foi apresentada como análise semântica executada pelo REA.

| Alvo selecionado | Resultado real | O que isso não demonstra |
|---|---|---|
| `ASSISTENTE-SHI/main.py` e `py-xiaozhi/main.py` | `rea_assistant_action(inspect)` recusou tipo não reconhecido. | Não houve parser Python ou execução dos clientes. A avaliação correspondente veio de leitura direta. |
| `xiaozhi-esp32-server/main/manager-web` | `rea_action(analyze)` concluído: 3 arquivos relevantes, 2 JavaScript, 4.196 bytes, 40 nós e 46 arestas, zero falhas de parsing. | Não cobre backend Python, componentes Vue completos, servidores, autenticação ou voz em funcionamento. |
| `xiaozhi-esp32/scripts/sonic_wifi_config.html` | Inspeção HTML concluída em worker isolado: 1 script e 3 inputs declarados; alvo intacto. | Não configurou Wi-Fi, não reproduziu som nem analisou firmware binário. |
| `anny/client/index.html` | Inspeção HTML concluída em worker isolado: 2 scripts declarados; identificada referência Umami; alvo intacto. | Não executou TypeScript, navegador, classificação, inferência ou analytics. |

Os workers HTML declararam apenas interface loopback, ausência de rota externa e sonda sem conexão ao hospedeiro. Isso vale para o worker analítico e seus descendentes, não para a coleta inicial de fontes públicas no GitHub nem para um eventual cliente de inferência externo. Os recibos estão em `outputs/core-r890/b-*-rea.json`; seus hashes constam no manifesto. As observações concluídas foram registradas no MetaBus sem promoção de confiança.

As relações JavaScript são estáticas: imports, endpoints e chamadas candidatas não comprovam invocação em tempo de execução. A conclusão operacional MCP não equivale a validação externa, prontidão de voz ou garantia de privacidade de um deploy.

## ASSISTENTE-SHI e py-xiaozhi: escolher um papel, evitar duplicação

Os dois repositórios possuem licença MIT. O [SHI](https://github.com/MarceloClaro/ASSISTENTE-SHI/blob/d60749a608b3c1317b527b491bfc50cafb98cecb/README.md) identifica-se como fork personalizado do py-xiaozhi, com interface em português e extensões de visão/áudio. A leitura dos protocolos e dependências confirma sobreposição relevante: GUI PyQt5, áudio por sounddevice/Opus, detecção de ativação, plugins MCP e transportes WebSocket/MQTT. Instalar ambos não acrescentaria dois papéis independentes ao Core.

Há questões concretas a resolver antes de adotar um cliente:

- O [WebSocket do SHI](https://github.com/MarceloClaro/ASSISTENTE-SHI/blob/d60749a608b3c1317b527b491bfc50cafb98cecb/src/protocols/websocket_protocol.py#L13) e o [do py-xiaozhi](https://github.com/MarceloClaro/py-xiaozhi/blob/2c6eca47873d19f5fc7227a1d0460926c1b55e69/src/protocols/websocket_protocol.py#L13) criam contexto SSL sem verificação de certificado e o fornecem às conexões WSS. A configuração deve ser corrigida; não é um padrão a transplantar.
- O arquivo SHI chamado [local_tts_fallback.py](https://github.com/MarceloClaro/ASSISTENTE-SHI/blob/d60749a608b3c1317b527b491bfc50cafb98cecb/src/audio_tts/local_tts_fallback.py#L25) declara gTTS via internet e chama `gTTS(...).write_to_fp(...)`. O nome local não estabelece execução offline.
- Os [defaults de configuração](https://github.com/MarceloClaro/py-xiaozhi/blob/2c6eca47873d19f5fc7227a1d0460926c1b55e69/src/utils/config_manager.py#L22) incluem OTA/ativação externos e Vision remoto. Um modelo Ollama ou SmolVLM2 local não torna o restante do cliente local.
- O [carregamento SmolVLM2](https://github.com/MarceloClaro/ASSISTENTE-SHI/blob/d60749a608b3c1317b527b491bfc50cafb98cecb/src/mcp/tools/camera/smolvlm2_optimized.py#L118) usa `from_pretrained` com `trust_remote_code=True`; preparação, origem do modelo e código associado exigem controle próprio. Esse caminho não foi executado.
- A [identidade do dispositivo](https://github.com/MarceloClaro/py-xiaozhi/blob/2c6eca47873d19f5fc7227a1d0460926c1b55e69/src/utils/device_fingerprint.py#L126) inclui informações de máquina/rede e persistência. Isso precisa constar da política de dados do cliente; não presumir anonimato ou ausência de transmissão apenas por não localizar uma biblioteca de analytics.

A contribuição aproveitável é uma interface opcional de entrada/saída, com estado de escuta e esquema de ferramenta explícitos, subordinada ao primário. Captura, câmera, ferramentas de sistema e calendário não devem ser habilitados pela simples importação do catálogo MCP. Não foram reproduzidas alegações do README sobre velocidade, taxas de sucesso ou desempenho de visão.

## xiaozhi-esp32-server: providers separados, prontidão separada

O [servidor MIT](https://github.com/MarceloClaro/xiaozhi-esp32-server/blob/1f6a89ada5375ac10f09c5246ef8c6f389aef167/LICENSE) separa módulos de VAD, ASR, LLM e TTS. Essa distinção é útil ao Core: identificar capacidade e condições de uso de cada etapa, em vez de registrar apenas um rótulo genérico de assistente de voz.

A [configuração consultada](https://github.com/MarceloClaro/xiaozhi-esp32-server/blob/1f6a89ada5375ac10f09c5246ef8c6f389aef167/main/xiaozhi-server/config.yaml#L10) escuta em `0.0.0.0` e traz autenticação desabilitada por default; o transporte e o endpoint devem ser restringidos antes de um eventual uso. A seleção padrão inclui LLM ChatGLMLLM e TTS EdgeTTS. Há providers ASR locais opcionais, mas o [Sherpa local](https://github.com/MarceloClaro/xiaozhi-esp32-server/blob/1f6a89ada5375ac10f09c5246ef8c6f389aef167/main/xiaozhi-server/core/providers/asr/sherpa_onnx_local.py#L49) baixa arquivos ausentes via ModelScope antes de usar o recognizer offline. Instalação/preparação com rede e inferência local são etapas distintas.

O [gerenciador de conexão](https://github.com/MarceloClaro/xiaozhi-esp32-server/blob/1f6a89ada5375ac10f09c5246ef8c6f389aef167/main/xiaozhi-server/core/connection.py#L100) possui fila e flags de relatórios ASR/TTS associadas à configuração por API. `delete_audio: true` não demonstra, isoladamente, ausência de relato, persistência ou transporte de transcrição. A revisão não iniciou conexão de áudio nem consultou contas remotas.

Os [requirements](https://github.com/MarceloClaro/xiaozhi-esp32-server/blob/1f6a89ada5375ac10f09c5246ef8c6f389aef167/main/xiaozhi-server/requirements.txt) recomendam Python 3.10 e fixam versões antigas específicas de torch, torchaudio e NumPy. Não há demonstração de compatibilidade desse conjunto com a venv Python 3.14 do Core. Um adaptador deve permanecer isolado, caso sua instalação seja especificada e validada futuramente.

## xiaozhi-esp32: terminal de borda, sem mudar a autoridade do Core

O [firmware MIT](https://github.com/MarceloClaro/xiaozhi-esp32/blob/b48506171b89f25eff99f46d18ac7808cd3564b6/LICENSE) depende de [ESP-IDF e componentes de hardware](https://github.com/MarceloClaro/xiaozhi-esp32/blob/b48506171b89f25eff99f46d18ac7808cd3564b6/main/idf_component.yml). Não é um runtime de programação para instalar na máquina do Core.

A contribuição mais clara está na [negociação de transporte](https://github.com/MarceloClaro/xiaozhi-esp32/blob/b48506171b89f25eff99f46d18ac7808cd3564b6/main/protocols/websocket_protocol.cc#L203): anuncia MCP, formato Opus, taxa de amostragem, canais e duração de frame. O [registro MCP](https://github.com/MarceloClaro/xiaozhi-esp32/blob/b48506171b89f25eff99f46d18ac7808cd3564b6/main/mcp_server.cc#L33) também separa ferramentas comuns e ferramentas marcadas para usuário. Esse é um padrão de descrição de capacidades, não autorização para acionar volume, tela, rede ou atuadores a partir de qualquer agente.

Uma integração futura pode apresentar o dispositivo como terminal do primário, com entrada/saída e ações delimitadas. Não houve compilação, flash, conexão ao ESP32, medição de áudio ou inferência. A inspeção REA do HTML de configuração Wi-Fi não constitui análise nativa do firmware ou prova de funcionamento do dispositivo.

## anny: o fork contém dois produtos de escopos distintos

A [descrição e o README](https://github.com/MarceloClaro/anny/blob/68a310e2a0eaa2dba1a9e0676525f99f94886bc4/README.md) apresentam o modelo diferenciável de corpo humano Anny, em PyTorch. Entretanto, a árvore atual também contém uma aplicação React/Express para classificação de pele: o [package.json](https://github.com/MarceloClaro/anny/blob/68a310e2a0eaa2dba1a9e0676525f99f94886bc4/package.json) declara `skin_cancer_classifier_k230_page`. A avaliação precisa manter esses eixos separados.

O código original do modelo de corpo declara Apache-2.0 e seus assets MPFB2 são identificados como CC0-1.0 no README; a aplicação web declara MIT no package.json. Essa heterogeneidade não permite rotular todo o conteúdo ou os dados com uma única licença sem análise por componente.

Há integrações externas na aplicação web:

- O [helper LLM](https://github.com/MarceloClaro/anny/blob/68a310e2a0eaa2dba1a9e0676525f99f94886bc4/server/_core/llm.ts#L212) usa Forge remoto por default.
- O [helper de transcrição](https://github.com/MarceloClaro/anny/blob/68a310e2a0eaa2dba1a9e0676525f99f94886bc4/server/_core/voiceTranscription.ts#L97) baixa `audioUrl` e verifica o limite de 16 MB após materializar o conteúdo; depois prepara envio à API configurada. A leitura não comprovou como esse helper é exposto num deploy.
- O [HTML](https://github.com/MarceloClaro/anny/blob/68a310e2a0eaa2dba1a9e0676525f99f94886bc4/client/index.html#L13) declara Google Fonts e script Umami com placeholders de analytics. REA confirmou a referência estática, sem executar analytics ou verificar sua configuração em produção.

O código de classificação contém textos e números sobre desempenho de modelo; eles não foram reproduzidos e não constituem validação clínica nesta avaliação. Não foram consultadas imagens, pesos ou dados de pacientes. O Core não deve importar essas alegações para seu diagnóstico ou sua governança.

Para orquestração geral, o ganho imediato é baixo. O modelo corporal pode ser considerado para avatar/visão com objetivo próprio; o logger e as fronteiras multimodais da aplicação podem servir como referência limitada. Nenhum desses papéis justifica importar o repositório inteiro ou acrescentar uma segunda memória canônica.

## Uma adaptação pequena, aproveitável no Core existente

Proposta ainda não implementada neste relatório: validar modalidade e política de rede antes de escolher provider ou fallback.

Pontos existentes onde essa regra pode se integrar: `integrations/harness_runtime.py::HarnessRuntime.status/execute`, `integrations/harness/model_registry.py::HarnessModelRegistry.route`, `marceloclaro/autonomous.py::AutonomousCoordinator.route` e cartões de capacidade do `mci/blackboard.py`. O primário continua responsável por coordenação e o MetaBus por memória.

O contrato mínimo deve declarar modalidade de entrada/saída, serviço/endpoint necessário, etapa de preparação e evidência de prontidão. Se a tarefa exigir `local_only`, provider remoto ou de localidade não declarada é inelegível; fallback gTTS/Vision/STT externo não pode ocorrer silenciosamente. A ausência de provider compatível deve produzir estado bloqueado/degradado com motivo, sem ativar captura ou inventar suporte multimodal.

Testes de aceite sugeridos: provider cujo nome contém local mas usa rede deve ser recusado em tarefa local-only; modalidade desconhecida deve falhar de forma explícita; fluxo de texto existente deve continuar roteando; rótulo de provider local não deve promover confiança nem substituir sondas reais de instalação, autenticação e inferência.

Apenas as referências Umami/analytics de anny foram localizadas na amostra pelo rastreamento desses identificadores. Nos demais projetos, a ausência desses termos na seleção não demonstra ausência de telemetria, envio de voz, identidade persistida ou chamadas de serviço. A avaliação distingue essas observações e não promete execução integralmente offline de nenhum dos cinco projetos como recebido.
