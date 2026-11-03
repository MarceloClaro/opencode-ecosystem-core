# Dublagem PT-BR R1047 — piloto R1026

Esta pasta gera uma versão de **20 s** do piloto Qiskit com voz clonada,
legenda PT-BR, slide traduzido e **sem cartão**. O vídeo original e os arquivos
anteriores não são sobrescritos.

## Arquivos

| Arquivo | Função |
|---|---|
| `narration.pt-BR.json` | roteiro em 4 blocos, velocidade, referência e consentimento declarado |
| `build_dub.py` | XTTS local, mix 20 s, SRT/ASS, composição e manifesto |
| `make_slide_patch.py` | recria o patch 935×864 e a máscara |
| `slide-patch-r1047.png` | tradução fluida do slide |
| `slide-patch-r1047-mask.png` | máscara suave do patch |
| `out/` | mídia e manifesto gerados (ignorados pelo Git) |

## Comandos

```bash
cd pilots/r1026-quantum/r1047-dub
~/.cache/opencode-pilot/venvs/xtts/bin/python build_dub.py
```

O script usa `OPENCODE_PILOT_BASE` se definido; por padrão,
`~/.cache/opencode-pilot`. Ele exige:

- `refs/presenter-ref.wav` (referência de 6 s);
- modelo XTTS v2 em `tts/`;
- `../presenter-middle-1080.mp4` (vídeo full-frame sem cartão);
- patch e máscara nesta pasta.

Para regerar o slide:

```bash
python3 make_slide_patch.py
```

## O que o roteiro melhora

A versão anterior dizia apenas que os menores foram desativados. A nova
locução explica a relação:

1. a IBM ampliou o acesso a processadores de 100+ qubits;
2. os menores saíram de linha para abrir espaço aos maiores;
3. alguns tamanhos ainda são simuláveis classicamente;
4. os maiores alcançam problemas que a simulação não resolve.

O slide repete a explicação em linguagem visual, com o callout **“O que
mudou?”**.

## Limites

- A voz é sintética (XTTS/CPML, não comercial). O operador declarou
  consentimento escrito; o Core não verificou o documento.
- O vídeo base tem lip sync anterior. **Esta rodada não re-sincroniza a boca**
  com a nova locução; o manifesto registra `lip_sync_resynchronized=false`.
- A tradução é interpretativa. Revisão bilíngue, editorial e de naturalidade
  continua humana.
- Não há publicação, upload ou envio de voz a serviço externo.
- Testes técnicos não aprovam estética, emoção, sincronia labial ou validade
  científica.
