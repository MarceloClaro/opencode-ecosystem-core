# Edição de vídeo auditável — R1024

## O que mudou

O Core ganhou um validador de **plano de edição**: um JSON que descreve
origens, cortes, faixas, legendas e saída antes de qualquer render. Ele pega
erros que costumam aparecer só depois de horas de processamento — corte fora da
origem, clipes sobrepostos, legenda rápida demais, crop inválido, codec
incompatível, destino que sobrescreve o original e direitos não resolvidos.

O validador não abre mídia, não executa `ffprobe`, não acessa a rede e não
renderiza. Ele lê o plano e, opcionalmente, compara um relatório de metadados
que o usuário produziu com o plano.

## Formato mínimo

```json
{
  "schema_version": "1.0",
  "project": {
    "id": "demo", "title": "Demonstração",
    "fps": 30, "width": 1920, "height": 1080, "sample_rate": 48000
  },
  "sources": [
    {
      "id": "cam", "path": "input/cam.mp4",
      "sha256": "…64 hex opcional…",
      "duration_frames": 900, "width": 1920, "height": 1080,
      "rights": "authorized"
    }
  ],
  "video": [
    {
      "id": "v1", "source": "cam",
      "in_frame": 0, "out_frame": 300,
      "timeline_start": 0, "lane": 0,
      "crop": [0, 0, 1920, 1080],
      "scale": [1920, 1080]
    }
  ],
  "audio": [
    {
      "id": "a1", "source": "cam",
      "in_frame": 0, "out_frame": 300,
      "timeline_start": 0, "lane": 0,
      "gain_db": 0, "fade_in_frames": 0, "fade_out_frames": 0
    }
  ],
  "captions": [
    {
      "id": "c1", "start_frame": 0, "end_frame": 90,
      "text": "Uma frase curta de teste.", "lane": 0, "max_cps": 17
    }
  ],
  "output": {
    "path": "out/final.mp4", "container": "mp4",
    "video_codec": "h264", "audio_codec": "aac",
    "loudness_lufs": -16
  }
}
```

Frames são inteiros. A duração em segundos é derivada de `frames / fps`, sem
arredondamento silencioso. O padrão de leitura de legenda é **17 CPS**
(caracteres não vazios por segundo), ajustável por legenda.

## Comandos

```bash
# Validar e ver erros/avisos
python3 -m integrations.video_edit_plan validate plano.json

# Validar e imprimir a forma canônica + digest
python3 -m integrations.video_edit_plan compile plano.json

# Comparar metadados de render com o plano
python3 -m integrations.video_edit_plan verify plano.json relatorio.json
```

O relatório de render é produzido pelo usuário, por exemplo a partir de
`ffprobe -show_format -show_streams -of json`, e reduzido a:

```json
{
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "duration_seconds": 20.0,
  "video_codec": "h264",
  "audio_codec": "aac",
  "container": "mp4",
  "loudness_lufs": -16
}
```

`verify` aceita aliases de codec (`avc1`→`h264`, `mp4a`→`aac`, `av01`→`av1`).
Duração tem tolerância de 1,5 frame; fps, 0,01. Loudness tem tolerância de
±2 LU. Ausência de loudness gera aviso, não erro.

## Regras que bloqueiam

| Código | Situação |
|---|---|
| `unknown_field` | campo não reconhecido, provável erro de digitação |
| `duplicate_id` | ID repetido entre projeto, origens, clipes, áudio ou legendas |
| `source_not_found` | clipe referencia origem inexistente |
| `source_bounds` | corte fora da duração da origem |
| `timeline_overlap` | dois clipes na mesma faixa ao mesmo tempo |
| `caption_too_fast` | CPS acima do limite declarado |
| `caption_overlap` | duas legendas na mesma faixa ao mesmo tempo |
| `caption_beyond_timeline` | legenda depois do fim do vídeo |
| `crop_outside_source` | crop maior que a origem |
| `output_overwrites_source` | destino igual a uma origem |
| `container_extension_mismatch` | extensão não corresponde ao contêiner |
| `codec_container_incompatible` | codec não suportado pelo contêiner |
| `rights_unresolved` | direitos da origem ausentes ou `unknown` |
| `hash_invalid` | SHA-256 malformado |
| `loudness_out_of_range` | alvo fora de −24 a −9 LUFS |
| `unsafe_path` | caminho absoluto, com `..` ou barra invertida |

Lacunas na faixa principal são **avisos** (`timeline_gap`): pausa pode ser
intencional. Proporção de crop diferente da saída também é aviso
(`aspect_mismatch`), não correção automática.

## O que foi aproveitado do GitHub

O manifesto `federation/video-editing-sources-r1024.json` registra 11 projetos
com commit, licença e limite. Nenhum foi clonado, instalado ou executado.

| Projeto | Contribuição conceitual |
|---|---|
| OpenTimelineIO | linha de tempo com trilhas, clipes e intervalos |
| auto-editor | primeiro passe de silêncio; lacuna como decisão |
| PySceneDetect | limite de cena por frame (trabalho futuro) |
| WhisperX | timestamp por palavra para CPS e alinhamento |
| stable-ts | timestamps estáveis, não estimados |
| ffsubsync | sincronização de legenda exige medição |
| VMAF | qualidade perceptual não se prova por metadado |
| FFmpeg/ffprobe | campos do relatório de render |
| Remotion | prévia antes de render; render só por pedido |
| OpenCut | linha de tempo interativa e modo headless |
| Diffusion Studio Core | separação entre prévia e render final |

Licenças relevantes: Remotion usa a **Remotion License**, não uma licença OSI,
e pode exigir licença comercial; VMAF é BSD-2-Clause-Patent; FFmpeg é
LGPL-2.1+ com partes GPL opcionais.

## O que não foi feito

- Nenhum vídeo foi aberto, cortado, renderizado ou medido.
- Nenhum `ffprobe`, VMAF, detecção de cena, ASR ou sincronização foi executado.
- O validador não prova qualidade visual, sincronização real da fala, segurança
  do crop sobre o rosto ou loudness medido.
- O digest identifica o plano canônico, não o render.

A conferência visual, a escuta, a revisão humana e a autorização de uso
continuam obrigatórias.
