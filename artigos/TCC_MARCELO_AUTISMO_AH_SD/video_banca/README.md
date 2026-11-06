# Vídeo de banca — Dupla excepcionalidade no Brasil

Apresentação em vídeo do Trabalho de Conclusão de Curso **“Dupla excepcionalidade no
Brasil: autismo, altas habilidades/superdotação e desafios de identificação a partir do
Censo Escolar (2021–2024)”**, de **Marcelo Claro Laranjeira** — FACUMINAS, Pós-graduação
Lato Sensu em Educação Especial e Inclusiva, Neuropsicopedagogia Institucional e Clínica,
Brasília, 2026.

> **Voz sintética.** A narração foi gerada por TTS neural (`edge-tts`, voz
> `pt-BR-AntonioNeural`) e está identificada no vídeo e nos créditos finais.
> O trabalho não possui linha de orientador(a), conforme decisão do autor.

## Especificações

| Item | Valor |
|---|---|
| Arquivo | `Dupla_Excepcionalidade_Banca.mp4` |
| Duração | 7 min 12 s (432,0 s) |
| Imagem | 1920 × 1080 (16:9), 30 fps, H.264, yuv420p |
| Áudio | AAC, 48 kHz, estéreo, 192 kbps, −16 LUFS, pico −1,4 dBTP |
| Legendas | 71 blocos queimados; `legendas.srt` equivalente |
| Cenas | 14 |
| Tamanho | ≈ 16,3 MB |

## Estrutura

| # | Início | Cena | Duração |
|---|---|---|---|
| 01 | 00:00 | Abertura: título, autoria e recorte | 25,0 s |
| 02 | 00:25 | Roteiro em três ideias | 21,7 s |
| 03 | 00:47 | O problema: duas condições, um estudante | 36,4 s |
| 04 | 01:23 | Pergunta de pesquisa e objetivos | 25,1 s |
| 05 | 01:48 | Metodologia: revisão e Censo Escolar | 31,5 s |
| 06 | 02:20 | Dados nacionais: 212% e 86% | 49,2 s |
| 07 | 03:09 | A razão TEA/AH/SD: 12,4 → 20,8 | 26,4 s |
| 08 | 03:35 | Regiões: Nordeste 45,2 e Sul 8,0 | 30,5 s |
| 09 | 04:06 | Estados: Ceará 121,8 e Paraná 3,9 | 29,6 s |
| 10 | 04:35 | Cenários 2025–2027 | 35,4 s |
| 11 | 05:11 | Literatura: mascaramento e diagnóstico tardio | 28,5 s |
| 12 | 05:39 | Neuropsicopedagogia: avaliar, intervir, articular | 33,4 s |
| 13 | 06:13 | Conclusão: três ideias para levar | 40,0 s |
| 14 | 06:53 | Encerramento: autor, agradecimento e voz sintética | 19,3 s |

## Dados apresentados

Todos os números vêm das Sinopses Estatísticas da Educação Básica do INEP
(2021–2024), extraídas diretamente das planilhas oficiais:

- TEA: 294.394 (2021) → 918.877 (2024), **+212%**;
- AH/SD: 23.758 (2021) → 44.171 (2024), **+86%**;
- razão TEA/AH/SD: **12,4 → 20,8**;
- classes comuns: **96,2%** do TEA e **99,5%** das AH/SD;
- regiões: Nordeste **45,2**, Sul **8,0**;
- estados: Ceará **121,8**, Paraná **3,9**;
- cenários 2027: linear **22,9**; convergência **14,2**.

Os cenários são exploratórios e não são previsões. O Censo não cruza TEA e AH/SD,
de modo que os dados não permitem estimar a prevalência da dupla excepcionalidade.

## Como regenerar

Dependências: `ffmpeg`/`ffprobe`, Python 3 com `Pillow` e `matplotlib`, e `edge-tts`
em um virtualenv (o projeto usou `/tmp/ttsvenv`).

```bash
cd video_banca

# 1. narração (gera audio/*.mp3, audio/*.srt e audio/durations.json)
EDGE_TTS=/tmp/ttsvenv/bin/edge-tts python3 scripts/gerar_audio.py

# 2. gráficos a partir dos CSVs oficiais
python3 scripts/gerar_graficos.py

# 3. slides 1920x1080
python3 scripts/gerar_slides.py

# 4. segmentos, concatenação, legendas e encode final
python3 scripts/montar_video.py            # reutiliza segmentos existentes
python3 scripts/montar_video.py --force    # refaz tudo
```

O roteiro (textos, narração e layouts) fica em `roteiro.py`; alterações nele exigem
refazer o áudio das cenas afetadas.

## Arquivos

```
video_banca/
├── Dupla_Excepcionalidade_Banca.mp4   vídeo final com legendas queimadas
├── legendas.srt                        legendas equivalentes (71 blocos)
├── roteiro.py                          roteiro e narração das 14 cenas
├── audio/                              MP3, SRT por cena e durations.json
├── charts/                             national, ratio, regions, states (PNG)
├── slides/                             14 slides 1920x1080 (PNG)
├── segments/                           segmentos por cena (MP4)
├── build/                              concat, áudio normalizado e legendas.ass
└── scripts/
    ├── gerar_audio.py
    ├── gerar_graficos.py
    ├── gerar_slides.py
    └── montar_video.py
```

## Notas

- A faixa inferior dos slides fica livre (conteúdo até y≈920) para as legendas.
- A barra no topo indica o progresso da apresentação; o contador “n / 14” aparece
  no canto superior direito.
- O encerramento retoma o nome do autor e agradece, além de declarar a voz sintética.
- O relatório técnico de verificação está em `QA.md`.
