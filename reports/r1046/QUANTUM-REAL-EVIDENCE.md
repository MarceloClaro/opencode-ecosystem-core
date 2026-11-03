# Aceitação real R1026 no editor R1046

Data: 2026-11-03. Este documento registra **execução real** com mídia do piloto
`pilots/r1026-quantum`, não apenas fixtures sintéticas. Os derivados ficaram em
`/tmp/opencode/r1046-quantum/work` e **não** foram versionados; o original não
foi alterado. Recibo legível por máquina:
[`quantum-real-evidence.json`](quantum-real-evidence.json).

## Fonte e sobreposição

| Item | Valor observado |
|---|---|
| Fonte | `pilots/r1026-quantum/source.mp4` |
| SHA-256 | `10da024a9da037483ddcaa6821701c66495f03750399be196e6b0b2d37bcb674` |
| Vídeo | 1920×1080, H.264, 30000/1001 fps, 600 frames, 20,02 s |
| Áudio | AAC 48 kHz, estéreo, 20,0 s |
| Overlay | `presenter-middle-card.mp4` |
| SHA-256 do overlay | `e27067a6c0b8b5800b67c131c82138d64ce8e98ae7273ef8f5c20c07df180ac9` |
| Overlay | 560×700, 30/1 fps, 600 frames, sem áudio |

A diferença **30 fps → 29,97 fps** foi o caso real que motivou a conformidade
explícita de fps. O plano registra `conformed_to_timeline: true` e aviso; não há
conversão silenciosa, e VFR continua bloqueado.

## Resultados

| Arquivo | Composição | Preset | Frames | Duração | SHA-256 | Técnico |
|---|---|---|---:|---:|---|---|
| `quantum-multitrack.mp4` | cartão grande sobre o rosto | medium | 600 | 20,02 s | `9eef79e5…d83d5` | passou |
| `quantum-multitrack-v2.mp4` | cartão no canto inferior direito | veryfast | 600 | 20,02 s | `658ee372…aa1bb` | passou |
| `quantum-multitrack-v3.mp4` | v2 + raio de canto 24 | medium | 600 | 20,02 s | `adc97df3…66f178` | passou |
| `quantum-transition.mp4` | duas metades da fonte, fade de 30 frames | veryfast | 570 | 19,019 s | `b8b75366…0adb5` | passou |

Todos os recibos mantêm:

```json
{
  "technical_checks_passed": true,
  "audiovisual_approved": false,
  "translation_accuracy_verified": false,
  "scientific_validity_verified": false
}
```

## Tempo de CPU observado

| Render | Tempo | RSS máximo |
|---|---:|---:|
| Multifaixa 1080p, medium, 20 s | 119,19 s | 726 MB |
| Multifaixa 1080p, veryfast, 20 s | 112,57 s | 513 MB |
| Multifaixa 1080p, medium + raio de canto | 158,02 s | 739 MB |
| Transição 1080p, veryfast, 19 s | 86,43 s | 576 MB |
| Aceite 640×360, veryfast | 32,80 s | 240 MB |

O preset `veryfast` teve ganho pequeno no multifaixa 1080p porque o custo
dominante foi decodificação, escala, overlay e máscara, não o encoder. O número
é medição local, não promessa de desempenho em outra máquina.

## O que o teste real encontrou

1. **FPS misto bloqueava o projeto.** A fonte está em 29,97 fps e o cartão em
   30 fps. O editor passou a conformar por `fps` com duração em frames calculada
   por razão e arredondamento para cima, registrando aviso.
2. **Áudio do clipe precisava ser convertido pela taxa da fonte.** O corte de
   amostras agora usa a taxa da fonte e o comprimento da timeline; não usa mais
   os frames da fonte como se fossem frames do projeto.
3. **O primeiro cartão cobria o rosto.** A posição foi corrigida para o canto
   inferior direito. Isso é decisão editorial, não um bug do render.
4. **O cartão tinha canto reto.** Foi adicionado `corner_radius` com máscara
   alfa `geq`, limitado a metade da caixa e combinado com opacidade.
5. **O preset não era explícito.** Agora é allowlisted, registrado no plano e no
   recibo; `medium` permanece o padrão.

## Verificação visual

Foram extraídos contatos de 4 frames e um recorte do cartão. A inspeção humana
do orquestrador observou:

- o cartão menor preserva o rosto da apresentadora;
- o raio de canto é visível e não recorta o conteúdo central;
- a transição de 30 frames mostra a mistura esperada entre as duas metades;
- não foi observado frame preto, áudio mudo ou duração truncada nas amostras.

Essa inspeção **não** é aprovação editorial, estética, de lip sync ou de
tradução. O cartão ainda tem borda visual e o matte do vídeo de origem pode
apresentar artefatos; uma versão final exige revisão humana e, se necessário,
outro tratamento de máscara.

## Reprodução

```bash
# 1. Regressão local (não renderiza mídia real)
python3 -m pytest -q tests/test_r1046_video_editor_advanced.py \
  tests/test_r1046_video_editor_integrity.py \
  tests/test_r1046_video_editor_render.py \
  tests/test_r1042_video_editor.py tests/test_r1042_video_editor_mcp.py

# 2. Aceite opcional com o vídeo real; grava somente em tmp_path do pytest
R1046_REAL_MEDIA=1 python3 -m pytest -q -s tests/test_r1046_quantum_real.py

# 3. Render manual 1080p: recrie o projeto/plano com os dois arquivos
python3 -m integrations.video_editor plan projeto.json multitrack params.json --out plan.json
python3 -m integrations.video_editor render plan.json
```

O teste opcional exige `pilots/r1026-quantum/source.mp4` e
`presenter-middle-card.mp4`; sem os arquivos, é pulado. Ele não publica, não
envia mídia e não converte o original.

## Pesquisa GitHub registrada

`reports/r1046/github-research.json` consultou a API do GitHub em 2026-11-03:
FFmpeg (LGPL/GPL conforme build), MLT (LGPL-2.1), libopenshot (LGPL-3.0),
OpenTimelineIO (Apache-2.0), Shotcut e Kdenlive (GPL-3.0). Nenhum clone, build ou
instalação de terceiro foi executado; a implementação usa o FFmpeg já instalado.
Licença é triagem, não parecer jurídico. O binário FFmpeg local inclui libx264
(GPL); distribuir o binário ou o projeto tem implicações próprias, distintas de
distribuir o vídeo renderizado.

## Limites

- CPU, SDR 8-bit; sem HDR, ACES, LUT calibrada ou perfil de câmera.
- Sem UI NLE, keyframes, multicam, tracking, nodes ou composição 3D.
- Sem aprovação automática de estética, inteligibilidade, emoção, lip sync,
  tradução ou validade científica.
- O recibo técnico não é certificado de qualidade e não autoriza publicação.
- Nada foi publicado; nenhum push foi feito nesta rodada.
