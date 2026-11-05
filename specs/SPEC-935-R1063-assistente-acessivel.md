# SPEC-935-R1063 — assistente acessível com voz, UIA e memória de 24 h

**Status:** fundação implementada; gravação contínua de 24 h e reprodução
autônoma de rotinas ainda não homologadas. Uso pessoal autorizado pelo
operador, que declara deficiência motora.
**Objetivo:** permitir operar o Windows por voz, ouvir a interface e manter uma
memória local de 24 h para apoiar tarefas, com consentimento explícito.

## 1. Princípios

- **Acessibilidade primeiro:** voz, leitura de interface e confirmação falada.
- **Consentimento visível:** iniciar/parar; indicador no terminal; `Core, parar`.
- **Minimização:** não gravar tela contínua nem áudio bruto por 24 h; gravar
  eventos de acessibilidade, comandos e transcrições.
- **Local e criptografado:** memória Fernet, chave 0600, TTL de 24 h.
- **Nada destrutivo sem confirmação:** clique/escrita exigem “sim” falado.
- **Allowlist:** só janelas autorizadas; terminais, bancos, saúde e mensagens
  privadas ficam de fora.

## 2. Arquitetura

```
microfone WSLg (RDPSource)
  → faster-whisper local
  → parser de comandos PT-BR
  → confirmação falada
  → UIA Windows (PowerShell) → app Windows
  → TTS Edge → RDPSink
  → memória Fernet 24 h (eventos + transcrições)
```

A ponte UIA roda no Windows (`powershell.exe`), porque o AT-SPI do WSL não vê
apps Windows. O Core permanece no WSL e chama a ponte por argv, sem shell.

## 3. Componentes

| Componente | Função |
|---|---|
| `windows_uia_bridge.ps1` | listar janelas, snapshot/read/read-text, invoke, set-value, foco |
| `windows_uia.py` | allowlist, confirmação, redação e limite |
| `voice.py` | gravar, transcrever, sintetizar e tocar |
| `dialog.py` | parser de comandos e confirmação |
| `memory.py` | log cifrado com TTL 24 h |
| `routine.py` | captura periódica de janela + voz, sem pixels/áudio bruto |
| `opencode_gateway.py` | envia pergunta ao OpenCode via CLI, agente `plan`, sem teclado na TUI |
| `__main__.py` | CLI `windows`, `voice`, `routine`, `say`, `listen`, `memory` |

## 4. Comandos de voz

- “Core, o que está na tela?” → lê a janela em foco.
- “Core, clicar em Salvar” → pede confirmação e invoca.
- “Core, escrever …” → pede confirmação e escreve no campo em foco.
- “Core, apertar” → aciona o elemento em foco.
- “Core, perguntar …” → confirma, envia ao OpenCode (`--agent plan`) e fala a resposta.
- “Core, parar” → encerra o loop.

Sem confirmação (“sim”), nenhuma ação é executada.

## 5. Memória de 24 h

- Eventos: janela, elemento focado, até 8 nomes de elementos, timestamp.
- Voz: transcrição redigida; áudio bruto não é mantido.
- Criptografia: Fernet; chave local `0600`; log `activity.jsonl`.
- TTL: 24 h; `memory prune` remove expirados; `memory forget` apaga tudo.
- Nada é enviado ao Drive ou à nuvem.

## 6. Segurança e privacidade

- Janelas permitidas: Bloco de notas, Calculadora, Explorer, Edge, ChatGPT,
  Word, Excel. Negadas: terminal, PowerShell, bancos, senhas, WhatsApp.
- `sk-…`, `ghp_…`, `xox…`, e-mail, CPF, cartão e bearer são redigidos.
- Texto de UIA é dado não confiável; nunca é executado como instrução.
- Aprovação local não é identidade humana nem sandbox.
- Gravação de terceiros exige consentimento; LGPD é responsabilidade do
  operador.
- `C:` tem ~12 GB livres; a memória não grava vídeo contínuo para não esgotar.

## 7. Aceitação

1. `windows list` lista janelas e marca allowlist.
2. `windows snapshot/read` só funciona em janela permitida e redige segredos.
3. `click/write/press` sem confirmação retorna `CONFIRMATION_REQUIRED`.
4. Memória cifrada não contém texto em claro; TTL remove expirados; `forget`
   apaga.
5. Microfone grava e ASR transcreve; TTS toca no RDPSink.
6. Loop de voz só age após “sim”.
7. `routine` registra eventos e voz sem armazenar áudio bruto.

## 8. Estado atual

- Ponte UIA Windows: **funciona** (list/snapshot/read/read-text/focused/invoke).
- Terminal OpenCode: **somente leitura**; `read-text` devolveu 7.224 caracteres.
  `click`/`type` no terminal retornam `WINDOW_NOT_ALLOWED`.
- Redação: **funciona** (`sk-…` em aba do Notepad foi redigido).
- Voz: microfone grava (`RDPSource`), ASR local disponível, TTS Edge toca.
- Memória 24 h: implementada e testada com TTL.
- Loop de voz: implementado; falta piloto com fala real do operador.
- Gateway OpenCode: **funciona** com `--agent plan` (teste “Responda somente: OK”
  retornou “OK”); não usa `--auto` e não simula teclado na TUI.
- `routine`: implementado; **não** executado por 24 h nesta sessão.
- Reprodução autônoma de rotinas (“faça o que eu faço”): **não implementada**;
  exige episódios revisados e confirmação.

## 9. Limites

- UIA do Windows não cobre todos os apps; alguns expõem árvore mínima.
- `set-value` substitui o conteúdo do campo; não é digitação incremental.
- O terminal é somente leitura; não há injeção de teclado. Executar comandos
  nele exigiria um modo guardado, com revisão, allowlist e confirmação.
- O gateway usa o agente `plan` (somente leitura) por padrão; agentes de edição
  exigem liberação explícita e não são usados no loop de voz.
- Microfone depende da permissão do Windows e do dispositivo padrão.
- Voz sintética Edge envia texto ao serviço da Microsoft; para uso offline,
  trocar por Piper local.
- Gravar 24 h de fala ainda captura terceiros; precisa de pausa e exclusões.
- Não há validação externa, publicação ou promessa de qualidade clínica.
