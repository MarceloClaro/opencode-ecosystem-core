# R1058 — Vídeo do plano de ação Airam Veras

- **Status:** renderizado e aprovado no QC técnico; revisão humana pendente
- **Data:** 2026-11-04
- **Spec:** `specs/SPEC-935-R1058-video-airam.md`
- **Piloto:** `pilots/r1058-airam-veras/`
- **Roteiro:** `pilots/r1058-airam-veras/SCRIPT.md`
- **Referências:** `pilots/r1058-airam-veras/REFERENCES.md`

## 1. Entregável

| Arquivo | Formato | Duração | Frames | Tamanho | SHA-256 |
|---|---|---|---|---|---|
| `pilots/r1058-airam-veras/out/airam-plano-acao.mp4` | 1440×810, 30 fps | 458,30 s | 13.749 | 52.397.060 | `91762270ac4693fee4f5238b96c7b7ca45c7c7be78f8180ab2bf925adba387cf` |

Áudio: narração institucional Edge TTS `pt-BR-FranciscaNeural` e agradecimento
final com voz clonada XTTS do próprio autor, autorizada, em uma frase curta;
AAC 48 kHz estéreo; loudness −14,64 LUFS; true peak −4,14 dBTP.

## 2. Conteúdo

1. Abertura com logo, escola, 5º A/B, LP e Matemática.
2. Mapa **mundo → Brasil → Ceará → Crateús → Maratoan**, com zoom e ponto pulsante.
3. Diagnóstico agregado de agosto/2026, com ressalva de linha de base.
4. Cronograma corrigido: **SPAECE em 01/12/2026, terça-feira**; preparação até 30/11; cinco semanas.
5. Visão de LP por turma: 5º A e 5º B, com marcadores e conteúdos.
6. Seis habilidades de LP exemplificadas: inferência, assunto global, sentido, pontuação, conflito e coesão.
7. Visão de Matemática por turma: 5º A e 5º B.
8. Cinco habilidades de Matemática exemplificadas: multiplicação/divisão, frações, geometria/área, medidas e gráficos.
9. Rotina semanal fixa: segunda/quarta leitura e produção; terça Matemática; quinta simulados e revisão; sexta vídeos, Torta na Cara, Tabuada Divertida e Bingo.
10. Intervenções, grupos C1–C4, metas 80/75 e monitoramento.
11. Agradecimento com foto, perfil, ORCID/Instagram/links e QR do GitHub; voz clonada autorizada na frase final, voz institucional no restante.

## 3. QC técnico

```json
{
  "frame_count": {
    "ok": true,
    "expected": 13749,
    "actual": 13749
  },
  "fps": {
    "ok": true,
    "expected": "30/1",
    "actual": "30/1"
  },
  "loudness": {
    "ok": true,
    "target": -14.0,
    "tolerance": 1.0,
    "actual": -14.64
  },
  "true_peak": {
    "ok": true,
    "max": -1.5,
    "actual": -4.14
  },
  "silence": {
    "ok": true,
    "max_allowed": 4.0,
    "longest": 1.481
  },
  "black": {
    "ok": true,
    "max_allowed": 0.2,
    "longest": 0.0
  },
  "contact_sheet": {
    "ok": true,
    "path": "pilots/r1058-airam-veras/out/contact-final.png"
  }
}
```

## 4. Verificação de conteúdo

- [x] Nenhum nome, nota individual ou ranking de estudante no vídeo.
- [x] Dados agregados conferem com o plano/dossiê.
- [x] Linha de base identificada como agosto/2026, não novembro.
- [x] H01–H20 identificados como marcadores, não descritores oficiais.
- [x] Metas identificadas como propostas, não garantias.
- [x] Logo, mapa e atribuições OSM/IBGE presentes.
- [x] Exemplos e porquês conferidos em stills e no contato de frames.
- [x] QR do GitHub decodificado para `https://github.com/MarceloClaro`.
- [x] Nada publicado automaticamente.

## 5. Render

- Composição Remotion `AiramVerasVideo`, 13.749 frames, 30 fps.
- Render direto: `--scale=0.75 --concurrency=6 --crf=18`.
- Saída visual: `out/airam-visual-1440.mp4` (intermediário local).
- Tempo: **2.375,12 s** (39min35s); RSS máximo 558.072 KB.
- Log local de render: `out/direct-render.log` (ignorado pelo Git).
- Mux: FFmpeg, vídeo copy, AAC 192k, 48 kHz estéreo, `loudnorm I=-14:TP=-1.5:LRA=11`.
- Recibo: `out/render-receipt.json`; QC: `out/qa-final.json`; contato: `out/contact-final.png`.

## 6. Voz, pronúncia e mapa

- **Véras**: o TTS usa “Véras” para a sílaba tônica; a tela mantém “Veras”.
- **SPAECE**: o TTS usa “Espaéce” para evitar leitura letra a letra.
- **Matemática**: a locução escreve números por extenso (“quatro”, “doze”,
  “dois vírgula cinco”, “dez mil”) e usa pausas; os cards mantêm a notação.
- **Clonagem**: referência local de 25 s do próprio autor, autorizada; XTTS v2
  em CPU. Aplicada ao agradecimento final; o restante usa voz institucional.
  A inferência completa levaria horas, então não se declara clonagem total.
- **Mapa**: OSM retorna Ipase no endereço do equipamento; a indicação local
  adotada é Maratoan. A diferença está documentada em `REFERENCES.md`.

## 7. Limites

- O vídeo é síntese pedagógica; não substitui os PDFs, o plano oficial, a
  matriz do SPAECE ou a decisão da equipe escolar.
- A linha de base é de 11/08/2026; não é resultado de novembro.
- Metas são propostas; não há garantia de resultado.
- H01–H20 não são descritores oficiais sem dicionário de equivalência.
- O mapa é ilustrativo e pedagógico; não é mapa de resultados nem limite
  oficial de bairro.
- Não há validação externa, aceite editorial ou publicação.
