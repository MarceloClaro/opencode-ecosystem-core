# R1070 — Fallback `still-motion` no reel-video

**Status:** implementado e validado localmente. Nenhum vídeo generativo foi
produzido; o fallback é motion determinístico por ffmpeg.

## 1. Instalação

- Clone estável: `~/.local/share/opencode-core/reel-video`
- Licença: MIT
- Commit base: `39a5ea97e81994bbaa0a546fc85fd7668f012890`
- Symlink de compatibilidade:
  `~/.cache/opencode-pilot/external-evals/reel-video`

## 2. Uso

```bash
# Cena: Codex para stills, still-motion para o vídeo
node --import tsx src/cli.ts scene add --name "cena" \
  --provider codex --video-provider still-motion

# Vídeo avulso
node --import tsx src/cli.ts add video --from img-1 \
  --prompt "movimento" --provider still-motion

# Padrão do processo
CANVAS_VIDEO_PROVIDER=still-motion node --import tsx src/cli.ts run
```

O provider `grok` continua disponível; `codex` continua opcional para stills.
O fallback não exige login, conta, rede ou API.

## 3. Comportamento

| Stills | Efeito |
|---|---|
| 1 | zoompan lento (Ken Burns) |
| 2 | crossfade entre first e middle |
| 3 | crossfade first → middle → last |

Saída: H.264, `yuv420p`, 30 fps, 6/10 s, sem áudio, `+faststart`.
Dimensões: 9:16 1080×1920; 1:1 1080×1080; 16:9 1920×1080;
4:3 1440×1080; 3:4 1080×1440.

## 4. Evidência

### Typecheck e testes

```text
npm run typecheck  → OK
npm test           → 22 passed
```

### Render manual

| Caso | Resultado |
|---|---|
| 3 stills, 16:9, 6 s | MP4 6,000 s, 1920×1080, H.264, 61 KB |
| 1 still, 9:16, 6 s | MP4 6,000 s, 1080×1920, H.264, 17 KB |
| runner `runProject` | `vid-1` status `ready`, asset `assets/vid-1.mp4`, `costUsd=0` |

### Hashes dos arquivos alterados

```text
c87995c9...  src/still-motion.ts
d4be834b...  src/types.ts
d4cf9578...  src/project.ts
900ed3da...  src/runner.ts
dee0eda0...  src/cli.ts
5edd2315...  test/still-motion.test.ts
```

## 5. Adaptador no Core

`reel-video` passa a ser `ready` no registro externo:

- dependências: `node`, `ffmpeg`;
- `grok` e `codex` são opcionais;
- safe check: importa `still-motion.ts` e `runner.ts` (rc=0);
- keywords incluem `still-motion`, `motion`, `storyboard`, `keyframes`;
- consentimento continua exigido para o app externo/workspace-write.

## 6. Limites

- Não é vídeo generativo; é motion graphics.
- Não cria stills; ainda precisa de Codex, Grok ou `imagegen`.
- Não adiciona áudio, legendas, TTS ou sincronização.
- Refs além de três são ignoradas; a ordem é first → middle → last.
- Nenhuma validação externa ou publicação.

## 7. Próximo passo

Executar uma cena real com `--provider codex --video-provider still-motion`
para validar a cadeia completa de stills + motion. Isso consome a conta Codex
e deve ser feito com autorização explícita.
