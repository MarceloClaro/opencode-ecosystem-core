# Upload ao YouTube — bloqueios antes de publicar

Data: 2026-11-03.

## 1. Direito de distribuição

`pilots/r1035-02XpQTA-_XE/authorization.json` registra:

- `user_declared_video_voice_image_authorization: true`
- `voice_cloning_authorized_by_user: true`
- `documents_verified: false`
- `publication: false`

A fonte é um episódio público do canal **Wild Heart - Yabani**
(`02XpQTA-_XE`, “Wild Heart Episode 1 (Long Version)”). Autorização para
editar/clonar não é, por si, autorização do titular para redistribuir a obra
inteira. Antes de upload público, é necessário:

1. declarar que o operador tem direito de distribuição da obra e das vozes; ou
2. usar o YouTube Content ID/licença apropriada; ou
3. manter o vídeo **privado/não listado** para revisão, sem publicação.

Sem essa confirmação, o Core prepara o pacote e os arquivos separados, mas
**não publica**.

## 2. Credenciais

Não foi encontrado:

- `client_secret.json` do Google/YouTube;
- token OAuth com escopo `youtube.upload`;
- CLI `youtube` autenticada.

O upload exige OAuth do canal de destino. O Core não pede nem armazena senha;
o operador precisa autorizar o app e fornecer o token local.

## 3. Qualidade e estado da dublagem

- 107 partes preparadas e diarizadas.
- Tradução automática em andamento (M2M100 local); revisão nativa pendente.
- Agrupamento global de locutores parcial; TTS em lote ainda não iniciado.
- Nenhuma parte foi mixada/renderizada como dublagem final.
- ASR, emoção, lip sync e inteligibilidade não foram aprovados por escuta.

Publicar agora violaria o próprio gate do projeto: `rendered != approved`.

## 4. O que será entregue quando liberado

- `final/Wild-Heart-EP01-PTBR.mp4` — episódio completo montado.
- `final/parts/` — 107 partes separadas.
- `final/subtitles/` — SRT/VTT por parte e do episódio.
- `final/receipts/` — hashes, loudness, frames, origem e limitações.
- `final/youtube-metadata.json` — título, descrição, tags, idioma, categoria.

O upload será `private` por padrão; só vira público com confirmação explícita
de direitos e revisão.
