# Editor de vídeo universal — R1042

Este núcleo transforma o trabalho do piloto em uma base reutilizável para
**qualquer vídeo**. Ele não é um fork de editor comercial nem promete todos os
recursos de um Premiere/DaVinci; é um editor local, auditável e extensível, com
FFmpeg, Remotion e adaptadores explícitos.

## O que já funciona

| Operação | Backend | Estado |
|---|---|---|
| `probe` | ffprobe | implementado |
| `trim` | FFmpeg | corte frame-exato, reencode |
| `concat` | FFmpeg | cortes duros, frame a frame |
| `scale`, `pad`, `crop` | FFmpeg | dimensões pares e validação de enquadramento |
| `extract_audio`, `replace_audio`, `mix_audio` | FFmpeg | WAV/AAC, sem ducking automático |
| `subtitles` | FFmpeg | burn-in ou faixa `mov_text` |
| `remotion` | Remotion CLI | composição React, com licença e aprovação |
| `dub` | adaptador | bloqueia sem adaptador; não inventa voz |

Ainda **não** implementados: transições, keyframes, color grading, composição
multi-faixa de vídeo, legendas animadas nativas, normalização de VFR, lip sync
e correção automática de enquadramento. O modelo de timeline já prevê faixas e
clipes; novas operações entram por plugin.

## Modelo de projeto

Um projeto é JSON com:

- `fps` racional (`25/1`, `30000/1001`), `width`, `height`, `sample_rate`;
- `sources` com caminho, SHA-256 opcional, frames e duração;
- `tracks` (`video`, `audio`, `subtitle`) e clipes com `in_frame`,
  `out_frame`, `start_frame`, `speed`, `volume`;
- `root` para confinar arquivos locais;
- `schema_version` e `version`.

O núcleo valida cobertura, sobreposição na mesma faixa, clipe fora da fonte,
ID duplicado, dimensões ímpares e caminhos com `..`/symlink.

## Fluxo

1. **Abrir** (MCP `editor_open`): faz probe local e grava
   `editor-projects/<id>.json`. Não edita nem renderiza.
2. **Planejar** (`editor_plan`): escolhe operação e parâmetros; grava
   `editor-plans/<plan_id>.json` com args, frames esperados, avisos e
   limitações. Nenhum FFmpeg é executado.
3. **Prévia** (`editor_render` com `dry_run=true`): mostra o comando.
4. **Aprovar**: o operador cria `editor-approvals/<plan_id>.json` com
   `approved: true`, `reviewer` e o `plan_sha256` exato. O modelo não cria
   essa aprovação.
5. **Renderizar**: `editor_render` com `dry_run=false` usa arquivo temporário,
   confere frames, grava recibo e só então promove a saída. Nada sobrescreve
   saída existente; retomada só reutiliza recibo cujo hash confere.

## Remotion

O backend Remotion exige:

- projeto local com `package.json`, entrada e composição descoberta;
- `license_ack: true` (Remotion License, não OSI);
- `render_approved: true` no plano;
- comando `npx --no-install remotion render ...`, sem instalação implícita;
- política do `remotion_guard`, que bloqueia render/instalação sem aprovação.

Exemplo de parâmetros:

```json
{
  "project_path": "remotion",
  "composition_id": "Demo",
  "entry_point": "src/index.ts",
  "props": {"title": "Olá"},
  "output": "renders/demo.mp4",
  "license_ack": true,
  "render_approved": true
}
```

O scan do projeto usa regex e **não compila TypeScript**. Uma composição
encontrada não prova que o projeto compila; o render prova apenas que o
comando terminou e os frames conferiram. Qualidade visual, sincronia e
enquadramento continuam exigindo prévia e revisão humana.

O CLI **Remotion 4.0.540** foi instalado em `editor-workspace/remotion-smoke`
com `--ignore-scripts`. `remotion compositions` foi executado com sucesso e
listou a composição `Smoke` (50 frames, 25 fps, 1280×720). Isso valida bundle
e inicialização do navegador, **não** render, still, áudio ou qualidade.
Recibo: `reports/r1043/remotion-install-receipt.json`. Render continua exigindo
`REMOTION_RENDER_APPROVED=1` e aprovação do operador.

## MCP `editor-local`

Ferramentas (5, superfície pequena):

- `editor_open(media_path, project_id)`;
- `editor_list_projects()`;
- `editor_plan(project_id, operation, params)`;
- `editor_render(plan_id, dry_run=True)`;
- `editor_status()`.

Raiz configurada por `EDITOR_PROJECT_ROOT`; caminhos do cliente são relativos e
confinados. Não há shell, URL, upload ou comando arbitrário. Respostas são
resumidas; detalhes ficam nos arquivos locais com hash.

## Outros motores

Entram como adaptadores/plugins, nunca como dependência implícita:

- **Demucs** para stems e música;
- **XTTS** para voz clonada, com referência e consentimento;
- **faster-whisper** para ASR;
- **Nemotron 3 Diarization** (não gated) para “quem falou quando”;
- **Tesseract** para OCR de legendas queimadas;
- **Rubberband** para tempo/pitch;
- **Qiskit/Remotion** e outros renderizadores.

## Skills e catálogo

- `video-editor-universal` orquestra as 10 skills `cp-*`/`meia-*` extraídas do
  pacote **Caixa Preta IA** e o método dos dois livros de Tiago Lemos.
- `docs/VIDEO_EDITOR_TOOLCHAIN_R1043.md` e `reports/r1043/toolchain.json`
  registram 46 ferramentas/modelos GitHub/Hugging Face, licença, papel e
  status. O catálogo não instala nem executa nada.

`register_operation(name, validate, plan)` adiciona operações;
`register_backend(name, preflight)` adiciona backend de render. Sem plugin, a
operação é recusada — não há fallback silencioso.

## CLI

```bash
python3 -m integrations.video_editor probe media.mp4 --out probe.json
python3 -m integrations.video_editor plan projeto.json trim params.json --out plan.json
python3 -m integrations.video_editor render plan.json --dry-run
```

`render` real usa o mesmo gate de recibo do MCP; para Remotion, o plano precisa
das duas declarações e o comando passa pela política de licença.

## Limites atuais

- FFmpeg cobre os formatos que a instalação local decodifica; não há garantia
  universal de codecs/containers.
- VFR é **sinalizado**, não convertido automaticamente.
- O modelo de timeline tem faixas, mas a composição multi-faixa de vídeo ainda
  não foi implementada; `concat` é corte duro.
- Não há aprovação perceptual automática: frames e loudness não provam
  inteligibilidade, emoção, lip sync ou qualidade editorial.
- Remotion License e direitos de mídia/fontes/marcas são responsabilidade do
  operador; o Core não dá parecer jurídico.
- CPU é o alvo; GPU não é presumida.
