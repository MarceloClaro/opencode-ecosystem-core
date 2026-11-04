# SPEC-1055 — Vídeo didático “O que é um qubit?”

- **Status:** implementado e verificado tecnicamente; revisão humana pendente
- **Data:** 2026-11-04
- **Piloto:** `pilots/r1055-qubit/`
- **Entregáveis:** master 16:9 e vertical 9:16, ambos com áudio normalizado

## 1. Contexto

O pedido original era um explicador animado de qubit, no formato do reel de
referência, com referências e teóricos, voz didática, cartão do autor e QR
code. Ao longo do trabalho o pedido evoluiu para:

1. voz natural e expressiva, sem clonar a voz de terceiros;
2. princípios de neuropsicopedagogia para atenção, memória e compreensão;
3. mapa de origem geográfica da teoria, com pontos pulsantes e câmera;
4. efeitos de câmera e esferas de Bloch com sincronia narrativa;
5. versão vertical nativa, sem blur.

## 2. Requisitos

- **R1.** Duração entre 90 e 115 s; 30 fps; 16:9 e 9:16 nativos.
- **R2.** Voz sintética PT-BR, sem clonagem; sem verbalização de pontuação.
- **R3.** Roteiro em sete cenas: pergunta, superposição, medição,
  emaranhamento, interferência/limite, origem/mapa, autor.
- **R4.** Referências reais com DOI verificado; nenhuma citação inventada.
- **R5.** Mapa com base cartográfica de domínio público e marcadores
  pulsantes sincronizados às cinco batidas da cena 06.
- **R6.** Câmera com zoom/pan/foco nas cenas 02–05, ancorada nas legendas.
- **R7.** Esfera de Bloch 3D com fase, brilho, estado misto e projeção.
- **R8.** Legendas por batida, 26 blocos, grafia correta dos nomes.
- **R9.** Cartão final com nome, foto, credenciais, agradecimento, links e QR
  para `https://github.com/MarceloClaro`.
- **R10.** QC técnico: frames, fps, loudness, true peak, silêncio, pretos;
  ASR diagnóstico; nenhuma publicação automática.

## 3. Critérios de aceitação

| ID | Critério | Verificação | Resultado |
|---|---|---|---|
| A1 | 3292 frames nas duas versões | `ffprobe` + `video_qa.py` | pass |
| A2 | 30/1 fps | `video_qa.py` | pass |
| A3 | Loudness −14 ±1 LUFS | `video_qa.py` | −14,49 LUFS |
| A4 | True peak ≤ −1,5 dBTP | `video_qa.py` | −4,42 dBTP |
| A5 | Sem silêncio >4 s | `video_qa.py` | 2,961 s |
| A6 | Sem frames pretos >0,2 s | `video_qa.py` | 0,0 s |
| A7 | Sem “ponto” falado | ASR `faster-whisper-large-v3` | pass |
| A8 | Nomes “Aspect, Clauser, Zeilinger” reconhecidos | ASR | pass |
| A9 | Legendas com “Bell”, “qubit”, “Aspect” | inspeção de `timeline.ts` | pass |
| A10 | Mapa com cinco batidas e pontos pulsantes | inspeção de stills + código | pass |
| A11 | Câmera ancorada nas legendas | inspeção de código/stills | pass |
| A12 | QR do cartão final escaneável | inspeção visual + URL | pass (revisão humana recomendada) |

## 4. Evidência

- `pilots/r1055-qubit/audio/timeline.json` — 26 blocos, 109,72 s.
- `pilots/r1055-qubit/audio/asr.json` — ASR diagnóstico.
- `pilots/r1055-qubit/out/qa-final.json` — QC 16:9.
- `pilots/r1055-qubit/out/vertical-qa-final.json` — QC 9:16.
- `reports/r1055/README.md` — hashes, tempos de render, prosódia e links.
- `docs/CINEMATIC_REMOTION_R1055.md` — pesquisa e módulo de câmera.

## 5. Limites

- O QC técnico não certifica qualidade estética, rigor científico ou aceite
  editorial.
- O mapa é ilustrativo; as cautelas históricas estão em `REFERENCES.md`.
- A voz é sintética; a prosódia foi ajustada, mas não substitui locução
  humana.
- A entrega é para revisão humana; nada foi publicado automaticamente.
