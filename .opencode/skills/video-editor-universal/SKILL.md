---
name: video-editor-universal
description: Dirija edição de vídeo e animação com decisão editorial, 10 modelos de composição, 16 comandos, amostra de 8 segundos, FFmpeg/Remotion e adaptadores locais. Use para planejar, editar, legendar, dublar, animar, revisar e exportar; não copie referências, não invente dados e não declare qualidade sem revisão humana.
---

# Editor de vídeo universal

## Princípio

O problema raramente é técnico: é **direção**. Antes de animar, cortar ou
dublar, escreva o que o espectador deve entender, olhar, sentir e reter em cada
trecho. A ferramenta executa; a decisão precisa existir em texto.

Esta skill integra:

- as 7 skills autorais `cp-*` e as 3 `meia-*` do pacote **Caixa Preta IA**
  (Tiago Lemos, 2026), já disponíveis em `.claude/skills`;
- os **10 modelos de composição** e os **16 comandos** do livro;
- o núcleo `integrations.video_editor` (FFmpeg + Remotion + plugins);
- o registro `integrations.video_toolchain` e o dossiê
  `reports/r1043/toolchain.json`.

## Fluxo obrigatório

1. **Ficha de direção** — preencha público, mensagem, oferta/CTA reais,
   formato, fontes, assets, referência, voz/música autorizadas, enquadramento,
   legenda, o que preservar e o que não pode entrar.
2. **Mapa de cenas** — transcreva a fala real e divida por unidades de sentido,
   não por intervalos iguais. Para cada unidade: foco visual, asset, ação,
   texto na tela, áudio e critério de revisão.
3. **Modelo** — escolha um dos 10 modelos (ver referência). Se nenhum servir,
   preserve a imagem original em vez de inventar movimento.
4. **Amostra de 8 s** — inclua a transição mais difícil, uma explicação
   completa e o retorno à fala. Assista em tamanho de celular.
5. **Aprovação** — se o usuário pediu aprovar o estilo, pare na amostra. Se já
   autorizou concluir, use a amostra como validação interna e prossiga.
6. **Lote** — aplique o padrão aprovado; comece por uma peça e amplie só depois
   de conferir. Registre versões e materiais ausentes.
7. **Revisão localizada** — cada pedido tem intervalo, problema, mudança e o
   que preservar. Corrija primeiro mensagem/dados, depois áudio/legenda, por
   último enquadramento/acabamento. Não refaça o projeto inteiro.
8. **Exportação** — prévia aprovada ≠ MP4 entregue. Abra o arquivo fora da
   prévia, confira início, inserções, final, áudio, sincronização e leitura no
   celular. Preserve o original e a versão anterior.

## Backends

- **FFmpeg**: corte, concatenação, escala/crop/pad, áudio, mux, legendas.
- **Remotion**: composições React, overlays, motion graphics e cenas
  programáticas. Exige `license_ack`, `render_approved`, projeto local e
  `npx --no-install`; a licença não é OSI.
- **Plugins**: Demucs (stems), XTTS/Chatterbox/Kokoro (voz), faster-whisper
  (ASR), Nemotron/pyannote (diarização), Tesseract/Florence-2 (OCR), SAM2/
  BiRefNet (matting), SeedVR2 (upscale). Sem plugin, a operação é recusada.
- **Nunca** instale, baixe modelo ou renderize por conta própria sem
  autorização do operador. Detecção não é instalação; registro não é execução.

## Dublagem e voz

- Diarização e ASR são **hipóteses**. Um locutor não mapeado bloqueia TTS; não
  invente nome, gênero, idade ou emoção.
- Uma referência por personagem, versionada por hash. Trocar referência exige
  reconciliar todas as falas daquele personagem.
- Não remova palavras, não corte fonemas e não afirme que “ponto” é clique.
  Pontuação final pode alterar a síntese; registre a normalização.
- ASR exato é triagem lexical, não aprovação de inteligibilidade, emoção,
  identidade ou lip sync.

## Custos e tokens

- Separe assinatura, uso adicional, API, extras e tempo humano.
- Reutilize a base aprovada; corrija só o trecho afetado; interrompa tentativas
  repetidas e peça diagnóstico.
- Calcule custo por **peça aprovada**, não por tentativa. Não converta
  porcentagem de limite em preço.
- Só compare consumo quando houver dados medidos.

## Critérios de aceite

- Cada mudança tem foco principal relacionado à fala.
- Dados, oferta, CTA, nomes e números são os confirmados.
- Rosto, demonstração e legenda não disputam a mesma área.
- O resultado permanece legível no formato final e no celular.
- O arquivo renderizado preserva a transformação da prévia.
- Original, versão aprovada e versão de treino não se confundem.

## Referências

- `references/modelos-e-comandos.md` — 10 modelos, 16 comandos, fichas e ciclo.
- `references/claude-skills-extraidas.md` — inventário e hashes das skills.
- `references/toolchain.md` — ferramentas/modelos GitHub/Hugging Face.
- `references/claude-skills-manifest.json` — manifesto machine-readable.

Atribuição: métodos, modelos e comandos adaptados de **Caixa Preta IA** e
**Máquina de Edição IA**, de Tiago Lemos de Abreu Oliveira (2026), adquiridos
pelo operador; uso local nos próprios projetos. Não redistribua o conteúdo
integral publicamente sem autorização. As skills `cp-*`/`meia-*` permanecem
em `.claude/skills` como fonte única; esta skill as orquestra.
