# Piloto Qiskit — cenário único, dublagem e lip sync (R1026–R1032)

## Autorização

- Uso do clipe: o operador confirmou ter autorização da Qiskit.
- Voz: o operador declarou **consentimento escrito** da apresentadora para a
  clonagem; o Core **não verificou** o documento.
- Remotion: enquadramento **pessoa física**, uso gratuito conforme o resumo da
  Remotion License.
- Uso pretendido: **piloto pessoal/estudo, não comercial**.

## Fonte

- URL: https://youtu.be/sVRpKhCfKRI
- Canal: Qiskit
- Título: Run Large-Scale Quantum Circuits (100+ Qubits Explained)
- Trecho: 00:02:00–00:02:20 (20,05 s)
- Original: 1920×1080, 29,97 fps, H.264/AAC
- `source.mp4` preservado na pasta.

## Entrega final

### Versão didática com voz (principal)

| Arquivo | Formato | Duração | Tamanho | SHA-256 |
|---|---|---|---|---|
| `pilot-16x9-didatico-voz.mp4` | 1920×1080, H.264/AAC | 44,1 s | 5,6 MB | `50caf1e8001a8ca0b4be16ed6e5b70dc24eb759cdd98cdb43ccc07c7361f4682` |
| `pilot-9x16-didatico-voz.mp4` | 1080×1920, H.264/AAC | 44,1 s | 4,3 MB | `9b3969dde280f9e795a9dab4dab2dee074c2d0754147443708d1145e7bae3739` |

Estrutura: **abertura narrada (14,2 s) + miolo novo no cenário escuro
(20 s) + encerramento narrado (9,8 s)**. O miolo **não** é o vídeo antigo:
usa `didactic-middle-16/9.mp4`, com `slide-sequence-dark.mp4` e
`presenter-middle-card.mp4`.

- Abertura e encerramento usam a **voz clonada da apresentadora**:
  - “Neste vídeo: por que a IBM oferece processadores de mais de 100 qubits e
    por que os menores saíram de linha. E o limite da simulação.”
  - “Em resumo: 100+ qubits disponíveis; chips menores desativados; e a
    simulação clássica ainda é um limite.”
- As legendas destacam **“100 qubits”**, **“desativados”** e **“simulados
  classicamente”** em roxo.
- O miolo mantém o slide animado em três cenas, agora em tema escuro, e a apresentadora no cartão.
- Loudness: **−16,28 LUFS**; áudio conferido em 3 s, 20 s, 30 s e 37 s.
- Frames conferidos: `r1032-16x9-0.5/7/12/14.5/20/30/35/40/43.png` e
  `r1032-9x16-0.5/7/12/14.5/20/30/35/40/43.png`.

### Apresentadora falando nos cartões (R1031)

- A abertura e o encerramento usam **vídeo com lip sync** da apresentadora,
  gerado pelo Wav2Lip em CPU a partir das narrações clonadas.
- O vídeo é recortado em **cabeça e ombros** (560×700), com matte suave por
  frame (`V*(1-S)`), fundo do cartão assado no vídeo e fade inferior.
- No Remotion, o vídeo é mudo (`<Video muted>`) e a narração continua em
  `<Audio>`, preservando loudness e edição.
- O cartão tem fundo escuro com glow roxo; a área da esquerda/topo fica livre
  para o roadmap animado.
- No 9:16, o roadmap vira uma **linha do tempo vertical** com três passos que
  acendem na ordem da narração; no 16:9, as três linhas compactas fazem o mesmo.
- O miolo usa o mesmo tratamento: `presenter-middle-card.mp4` (20 s) +
  `slide-sequence-dark.mp4` dentro de `didactic-middle-16/9.mp4`. O vídeo
  antigo do slide **não** é concatenado.
- O lip sync é gerado em **passada contínua** (`render-presenter-card-whole.sh`),
  sem blocos de 5 s; a versão em blocos
  (`render-presenter-card-lipsync.sh`) fica como fallback.
- O rótulo “APRESENTADORA / VOZ SINTÉTICA” identifica a voz como sintética.
- Pipeline: `render-presenter-card-whole.sh` (Wav2Lip contínuo),
  `compose-presenter-card.py` (matte/composição) e
  `DarkSlideSequence` (slide escuro). O retrato estático
  `presenter-cutout.png` permanece como fallback sem lip sync.
- Evidência: `presenter-intro-card.mp4`, `presenter-outro-card.mp4`,
  `presenter-middle-card.mp4`, `didactic-middle-16/9.mp4`,
  `slide-sequence-dark.mp4`, `intro-card4-7.png` e `lipsync-intro16-7.png`.

### Versão com slides animados (intermediária)

| Arquivo | Formato | Duração | Tamanho | SHA-256 |
|---|---|---|---|---|
| `pilot-16x9-lipsync-anim.mp4` | 1920×1080, H.264/AAC | 20,0 s | 4,1 MB | `5d626de1d2ae8382013c1574446ad5f1344de27f4dcd77cafa09af79ac0f47d9` |
| `pilot-9x16-lipsync-anim.mp4` | 1080×1920, H.264/AAC | 20,0 s | 2,6 MB | `81e7a7d9d92f20baec7a111455fea8cd25c555d5c3a576962e214f41a3b1b24f` |

A sequência animada foi criada em Remotion (`SlideSequence`, 934×864,
escalada para 935×864) e composta na área do slide:

| Cena | Tempo | Função |
|---|---|---|
| 1 | 0,0–5,47 s | contexto: 100+ qubits amplamente disponíveis |
| 2 | 5,67–12,23 s | mudança: Eagle/Heron e a desativação dos menores |
| 3 | 12,63–20,0 s | por quê: simulação clássica e limite dos chips maiores |

O slide animado tem cabeçalho, barra de progresso, indicador `01/03`, entrada
por `spring` e transições nos intervalos de silêncio. Fonte: `slide-sequence.mp4`
(hash `4f937283eb87b5f7f4fe7dd972edb380b1c9b4d3d2bbee5abcc67edca854f3da`).

### Versão com slide estático (fallback)

| Arquivo | Formato | Duração | Tamanho | SHA-256 |
|---|---|---|---|---|
| `pilot-16x9-lipsync-pt.mp4` | 1920×1080, H.264/AAC | 20,0 s | 3,5 MB | `bb4b58796843cf7f0e85fef7926222f396b3717b37362eac510b0b424b43a860` |
| `pilot-9x16-lipsync-pt.mp4` | 1080×1920, H.264/AAC | 20,0 s | 2,2 MB | `5e0084f2fe802e7db9a1e5ef36bda03e2e51a21d6477a992fb1b02b458554312` |

As duas versões contêm voz feminina clonada, legendas PT-BR queimadas, lip sync
e loudness **−16,5 LUFS**. A diferença é o slide: estático (`-pt`) ou animado
(`-anim`).

### Slide PT-BR

O slide original foi identificado em `(165, 56, 1615×910)`, fundo `#F5F3FF`.
O patch em português tem **935×864**, aplicado em **(210, 76)**, e cobre o texto
antigo à esquerda sem tocar na apresentadora.

Conteúdo: “Computação quântica na prática”, cards Eagle/Heron e o callout
“Por que a mudança?”, que conecta a desativação dos chips menores à
possibilidade de simulação clássica. Detalhes em [SLIDE_PT.md](SLIDE_PT.md).

### Como o lip sync foi feito

- Wav2Lip `wav2lip_gan.pth`, commit `bac9a81e...`.
- 4 blocos de 5 s em **640×360**, 2 threads, `nice`/`ionice`.
- Watchdog de **4,5 GB**; lock e retomada por bloco.
- A boca sincronizada foi sobreposta ao vídeo original 1080p **apenas na
  região do rosto**, com máscara elíptica suavizada (`face-mask-1080.png`).
- O restante do quadro permanece o original 1080p, preservando slide, fundo e
  detalhe da apresentadora.

### Verificação

**Versão didática com voz (principal)**

- Duração: **44,0 s**; 1920×1080 e 1080×1920; H.264/AAC 48 kHz.
- Estrutura: abertura 14,2 s + miolo 20 s + encerramento 9,8 s.
- Loudness: **−16,29 LUFS**.
- Áudio não silencioso confirmado em 3 s, 20 s e 37 s.
- Frames conferidos em 5/15/20/30/34/40 s nos dois formatos.
- O miolo de 20 s mantém o plano R1024 `plan-lipsync-anim.json`; os cartões de
  abertura/encerramento são verificados por `ffprobe`, não pelo schema de edição.
- Testes de regressão: R1029 (8) + R1030 (8) + R1031 (6) + R1032 (5) = **27 passed**.
- `visual_quality_verified`: **falso**.

**Versão animada (intermediária)**

- Plano R1024 `plan-lipsync-anim.json`: **válido**, 600 frames, 3 legendas.
- Digest: `7812ddf33bf88773a4bee9515482d04a9db2342db9185bd0f4ac5c6ea46dd22e`.
- `render_metadata_matched`: **verdadeiro**.
- `visual_quality_verified`: **falso**.
- Loudness: **−16,5 LUFS**.
- Frames inspecionados: `anim-16x9-2/8/15.png` e `anim-9x16-2/8/15.png`.
- As três cenas aparecem nos pontos esperados (contexto, mudança e por quê).

**Versão com slide estático**

- Plano R1024 `plan-lipsync-pt.json`: **válido**, 600 frames, 3 legendas.
- Digest: `464956fa46bbbab1997b4815c41c39631144e9f9467f1165327face758cc5b0b`.
- `render_metadata_matched`: **verdadeiro**.
- Loudness: **−16,5 LUFS**.
- A inspeção visual confirma slide PT-BR, ausência de texto antigo, máscara sem
  emenda aparente e legenda legível. **Não** prova sincronia labial quadro a
  quadro nem inteligibilidade; isso exige reprodução com áudio e revisão humana.

## Versões anteriores (mantidas para comparação)

- `pilot-16x9-standard.mp4` / `pilot-9x16-standard.mp4`: 20 s legendados, sem
  dublagem.
- `pilot-16x9-dub.mp4` / `pilot-9x16-dub.mp4`: dublagem Piper masculina, sem
  lip sync.
- `pilot-16x9-dub-clone.mp4` / `pilot-9x16-dub-clone.mp4`: voz clonada, sem lip
  sync.
- `pilot-16x9-lipsync.mp4` / `pilot-9x16-lipsync.mp4`: lip sync sem o slide
  PT-BR.
- `pilot-16x9-didatico-voz.mp4` / `pilot-9x16-didatico-voz.mp4`: versão
  didática com abertura/encerramento narrados pela voz clonada, slides
  animados e legendas com palavras-chave.
- `pilot-16x9.mp4` / `pilot-9x16.mp4` / `remotion-pilot.mp4`: primeira versão
  de 8 s.

## Limitações

- A tradução e o slide são **adaptação didática para estudo**, não material
  oficial da Qiskit; precisam de revisão humana.
- O consentimento de voz é **declarado**, não verificado pelo Core.
- XTTS v2/CPML e Wav2Lip são **não comerciais**; não use em produto comercial.
- O clone de voz não foi avaliado por escuta humana; pode haver sotaque,
  artefatos ou perda de naturalidade.
- O lip sync foi verificado por frames, não por reprodução contínua; pode haver
  tremor, dessincronia localizada ou artefatos nos limites dos blocos.
- Na versão 9:16, o slide é reduzido junto com o frame 16:9; a legenda carrega a
  mensagem principal.
- A sequência animada usa Remotion sob a **Remotion License** (pessoa física,
  ONG ou empresa até 3 funcionários; acima disso, licença comercial).
- As transições das cenas caem nos intervalos de silêncio; se a fala for
  remontada, o timing precisa ser refeito.
- A versão didática tem **44 s**: 14,2 s de abertura e 9,8 s de encerramento
  narrados, além do miolo de 20 s. O texto é uma adaptação, não a fala original.
- A narração de abertura/encerramento usa a **mesma voz clonada**; o
  consentimento é declarado, não verificado. Não é uma gravação nova da
  apresentadora.
- O lip sync dos cartões (abertura/encerramento) foi verificado por frames, não
  por reprodução contínua ou escuta humana; pode haver dessincronia localizada.
- A matte suave por frame é heurística, não segmentação profissional; pode
  deixar franjas no cabelo/ombros. O recorte em cabeça e ombros reduz as
  manchas da base, mas não prova qualidade de recorte.
- O vídeo do cartão é mudo; a narração é o áudio clonado separado, para preservar
  loudness e edição.
- O miolo novo usa o lip sync do áudio de 20 s e o slide escuro; ele substitui
  o antigo `pilot-*-didatico-base.mp4` no master. O vídeo antigo não é
  concatenado.
- A passada contínua do Wav2Lip removeu os congelamentos de 5 s/10 s, mas ainda
  pode haver pausas naturais da fala e uma leve deriva de frames no fim.
- O cartão 9:16 usa linha do tempo vertical; ainda há respiro inferior, mas a
  leitura dos três passos é preservada.
- Os níveis de áudio confirmam presença de som, não inteligibilidade ou
  naturalidade; falta escuta humana.
- Nada foi publicado.
- O guard `remotion-guard` bloqueia comandos diretos, mas `npm run <script>`
  contorna a checagem lexical; heredocs com o literal de instalação geram falso
  positivo.

## Reprodução

```bash
# 1. slide, retrato e cartões
python3 make_slide_patch.py
python3 make-presenter-cutout.py

# 2. lip sync contínuo das pontas (sem blocos de 5 s)
./render-presenter-card-whole.sh intro-narracao.wav 14.187 intro
./render-presenter-card-whole.sh outro-narracao.wav 9.813 outro

# 3. matte por frame e cartões escuros das pontas
python3 compose-presenter-card.py --video presenter-intro-1080.mp4 --duration 14.187 --label intro
python3 compose-presenter-card.py --video presenter-outro-1080.mp4 --duration 9.813 --label outro

# 4. fonte da apresentadora do miolo (lip sync do áudio de 20 s)
./render-lipsync-cpu.sh
python3 compose-presenter-card.py --video pilot-16x9-lipsync-pt.mp4 --duration 20 --label middle

# 5. render dos cartões e do slide escuro
cd remotion-template
npm install
npm run render:darkslides
cp out/slide-sequence-dark.mp4 public/
cp ../presenter-intro-card.mp4 ../presenter-outro-card.mp4 ../presenter-middle-card.mp4 public/
cp ../dub-pt-BR-clone.wav public/middle-clone.wav
npm run render:intro16
npm run render:intro9
npm run render:outro16
npm run render:outro9
npm run render:middle16
npm run render:middle9
cd ..

# 6. leva o miolo novo para a pasta do piloto e concatena
cp remotion-template/out/didactic-middle-16.mp4 remotion-template/out/didactic-middle-9.mp4 .
./concat-didatico.sh

# 7. verificação
python3 -m integrations.video_edit_plan validate plan-lipsync-anim.json
python3 -m integrations.video_edit_plan verify plan-lipsync-anim.json report-lipsync-anim.json
```

> O master final **não usa** `pilot-*-didatico-base.mp4` nem o slide branco
> antigo. O miolo é `didactic-middle-16/9.mp4`, composto no cenário escuro com
> `slide-sequence-dark.mp4` e `presenter-middle-card.mp4`.

O lip sync dos cartões usa o Wav2Lip em `/home/marceloclaro/.cache/opencode-pilot`
em **passada contínua**, com watchdog de memória. A versão em blocos de 5 s
(`render-presenter-card-lipsync.sh`) fica como fallback; ela foi a causa dos
congelamentos nas emendas. O áudio da narração é mantido fora do vídeo; o cartão
usa `<Video muted>` + `<Audio>`.

A narração de abertura/encerramento é gerada com XTTS v2 e a referência
`presenter-ref.wav` (ver `consent-and-licenses.md`); os WAVs usados estão em
`intro-narracao.wav` e `outro-narracao.wav`.

Para a versão com slide estático, use `./apply-slide.sh` e os planos `-pt`.

Arquitetura, padrões e QC: [STUDIO.md](STUDIO.md) e [QC.md](QC.md).
Template de intro/outro Remotion: `remotion-template/`.
