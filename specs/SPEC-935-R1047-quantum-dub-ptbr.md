---
spec_id: SPEC-935-R1047
title: Dublagem PT-BR com voz clonada, slide traduzido e legenda no piloto R1026
component: pilots/r1026-quantum/r1047-dub
status: specified
test_file: tests/test_r1047_quantum_dub.py
depends_on:
  - SPEC-935-R1042
  - SPEC-935-R1046
---

# SPEC-935-R1047

## Objetivo e autorização

Produzir uma versão de 20 s do piloto R1026 com:

1. voz sintética clonada a partir de `presenter-ref.wav`, em CPU e sem serviço
   externo;
2. dublagem PT-BR mais explicativa que a versão anterior;
3. legenda PT-BR sincronizada com a nova locução;
4. slide traduzido com adaptação fluida;
5. **sem cartão** sobre a apresentadora;
6. vídeo full-frame, preservando o original.

O operador declarou autorização da Qiskit e consentimento escrito da voz; o
Core **não verificou** os documentos. Uso pretendido: piloto pessoal/estudo,
não comercial. Nada será publicado nesta rodada.

## Roteiro e conteúdo

A explicação deve cobrir, em PT-BR natural:

- a ampliação do acesso a processadores quânticos de 100+ qubits;
- a desativação dos processadores menores para abrir espaço aos maiores;
- a razão: alguns tamanhos ainda são simuláveis classicamente; os maiores
  alcançam problemas que a simulação não resolve.

O roteiro não precisa repetir as janelas de fala do inglês. A locução pode ser
contínua, com pausas curtas, desde que caiba em 20 s sem aceleração acima de
1,18×. A velocidade do XTTS é limitada a 1,30; o texto final fica em
`narration.pt-BR.json`. A versão final usa **speed 1.0**; a tentativa em 1,3 foi
rejeitada pelo gate de 17 CPS, não por tempo.

## Entregáveis

| Arquivo | Conteúdo |
|---|---|
| `dub-r1047.pt-BR.wav` | 20 s, 48 kHz, estéreo, loudness alvo −16 LUFS |
| `captions-r1047.pt-BR.srt` | legenda com timing da locução |
| `captions-r1047.pt-BR.ass` | legenda para burn-in |
| `slide-patch-r1047.png` + máscara | tradução fluida do slide, camada separada |
| `quantum-ptbr-r1047.mp4` | 1920×1080, 20 s, sem cartão, com legenda |
| `manifest.json` | hashes, duração, loudness, flags e limitações |

## Critérios de aceitação

1. `narration.pt-BR.json` tem 4 segmentos, ids únicos, textos não vazios e
   cobre os três conceitos exigidos.
2. A referência de voz, o modelo e a licença estão declarados; nenhum áudio é
   enviado a serviço externo.
3. O áudio final tem 20 s, 48 kHz, 2 canais; loudness integrado entre −17 e
   −15 LUFS e true peak ≤ −1,5 dBTP, ou a limitação é registrada.
4. SRT e ASS existem, não se sobrepõem e ficam ≤17 CPS; a legenda é
   interpretativa, não verbatim.
5. O patch do slide cobre o texto inglês sem cobrir o rosto; o original e o
   vídeo-fonte permanecem intactos.
6. O vídeo final não contém cartão de apresentadora e mantém 1920×1080,
   20 s, H.264/AAC 48 kHz.
7. O manifesto declara `presenter_card_present=false`,
   `audiovisual_approved=false`, `translation_human_reviewed=false`,
   `scientific_validity_verified=false`, `published=false`.
8. Se a nova locução não for re-sincronizada com Wav2Lip, o manifesto declara
   `lip_sync_resynchronized=false`. Não reutilizar o lip sync antigo como se
   fosse do novo texto.
9. Nenhum arquivo original é sobrescrito; saídas novas usam nomes `r1047`.

## Testes

- Contrato do JSON de narração e presença dos conceitos.
- Cálculo de tempo SRT/ASS e CPS.
- Manifesto, streams, duração, loudness e flags, quando a mídia existir.
- Teste de mídia real opcional com `R1047_REAL_MEDIA=1`.
- Regressão R1042/R1046 e `doctor`.

## Limites

- A voz clonada pode apresentar artefatos; não há escuta humana nem avaliação
  de naturalidade nesta rodada.
- O vídeo base tem lip sync anterior; sem nova passagem do Wav2Lip, a boca não
  corresponde à nova locução.
- A tradução do slide e da fala é interpretativa; revisão bilíngue e editorial
  humanas são obrigatórias antes de publicação.
- XTTS/CPML é não comercial; Wav2Lip, se usado, também é não comercial.
- Testes técnicos não comprovam qualidade estética, emoção, sincronia labial ou
  validade científica.
