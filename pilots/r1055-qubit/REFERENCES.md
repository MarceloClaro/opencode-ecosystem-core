# Referências e créditos — R1055

Vídeo: **O que é um qubit?** — explicador animado, 16:9 e 9:16, 109,73 s.
Data de fechamento: 2026-11-04.

Este arquivo separa **referências verificadas**, **origens geográficas**,
**créditos de mídia** e **limites**. Nenhum DOI, dado ou resultado foi
inventado. Os identificadores abaixo foram consultados no Crossref em
2026-11-04; a resolução de cada DOI foi confirmada com status HTTP 200.

## 1. Referências teóricas

| Autor(es) | Título | Veículo | Ano | DOI | Uso no vídeo |
|---|---|---|---|---|---|
| Nielsen, M. A.; Chuang, I. L. | *Quantum Computation and Quantum Information* | Cambridge University Press | 2000 | `10.1017/CBO9780511976667` | Base para qubit, portas, medição e correção de erro. O registro Crossref da edição on-line é de 2012; a obra é de 2000. |
| Schumacher, B. | Quantum coding | *Physical Review A* 51, 2738–2747 | 1995 | `10.1103/PhysRevA.51.2738` | Origem do termo *qubit* e da codificação quântica. |
| DiVincenzo, D. P. | The Physical Implementation of Quantum Computation | *Fortschritte der Physik* 48, 771–783 | 2000 | `10.1002/1521-3978(200009)48:9/11<771::AID-PROP771>3.0.CO;2-E` | Critérios de implementação física e correção de erro. |
| Feynman, R. P. | Simulating physics with computers | *International Journal of Theoretical Physics* 21, 467–488 | 1982 | `10.1007/BF02650179` | Proposta de usar física quântica para computar; cena do mapa (Caltech). |
| Schrödinger, E. | Die gegenwärtige Situation in der Quantenmechanik | *Die Naturwissenschaften* 23, 807–812 | 1935 | `10.1007/BF01491891` | Contexto histórico da superposição e do gato de Schrödinger. |
| Clauser, J. F.; Horne, M. A.; Shimony, A.; Holt, R. A. | Proposed Experiment to Test Local Hidden-Variable Theories | *Physical Review Letters* 23, 880–884 | 1969 | `10.1103/PhysRevLett.23.880` | Teste de Bell; cena do mapa (Berkeley/Clauser). |
| Aspect, A.; Dalibard, J.; Roger, G. | Experimental Test of Bell's Inequalities Using Time-Varying Analyzers | *Physical Review Letters* 49, 1804–1807 | 1982 | `10.1103/PhysRevLett.49.1804` | Teste de Bell com fótons; cena do mapa (Orsay/Paris). |
| Zeilinger, A. | Experiment and the foundations of quantum physics | *Reviews of Modern Physics* 71, S288–S297 | 1999 | `10.1103/RevModPhys.71.S288` | Emaranhamento e fundamentos; cena do mapa (Viena). |
| Preskill, J. | Quantum Computing in the NISQ era and beyond | *Quantum* 2, 79 | 2018 | `10.22331/q-2018-08-06-79` | Limites atuais, decoerência e era NISQ. |
| Bennett, C. H.; DiVincenzo, D. P. | Quantum information and computation | *Nature* 404, 247–255 | 2000 | `10.1038/35005001` | Panorama de informação quântica. |
| Nobel Prize Outreach | The Nobel Prize in Physics 2022 | nobelprize.org | 2022 | — | Aspect, Clauser e Zeilinger; URL oficial: <https://www.nobelprize.org/prizes/physics/2022/summary/> |

## 2. Origens geográficas do mapa

O mapa é **ilustrativo** e marca cidades associadas aos autores e às
instituições, não a localização exata de cada descoberta. A narração e os
rótulos foram redigidos para não sugerir que a teoria nasceu em um só lugar.

| Cidade | Personagem | Vínculo representado | Fonte | Cautela |
|---|---|---|---|---|
| Copenhague, Dinamarca | Niels Bohr | Instituto de Física Teórica; complementaridade; centro da mecânica quântica nos anos 1920 | Nobel 1922: <https://www.nobelprize.org/prizes/physics/1922/bohr/facts/> | O mapa não afirma que toda a teoria nasceu em Copenhague. |
| Viena, Áustria | Erwin Schrödinger; Anton Zeilinger | Schrödinger nasceu em Viena; Zeilinger é da Universidade de Viena e recebeu o Nobel de 2022 | Nobel 1933: <https://www.nobelprize.org/prizes/physics/1933/schrodinger/facts/>; Nobel 2022 | A equação de onda foi formulada em Zurique, em 1926; Viena marca o nascimento de Schrödinger e o Nobel de Zeilinger. |
| Leipzig, Alemanha | Werner Heisenberg | Mecânica matricial, 1925; período em Leipzig | Nobel 1932: <https://www.nobelprize.org/prizes/physics/1932/heisenberg/facts/> | O mapa marca o período institucional, não toda a obra. |
| Pasadena, Califórnia, EUA | Richard Feynman | Caltech; artigo de 1982 sobre simular física com computadores | DOI `10.1007/BF02650179`; afiliação no artigo | O artigo é de 1982; a palestra que o originou é de 1981. |
| Gambier/Ohio, EUA | Benjamin Schumacher | Kenyon College; artigo de 1995 que usa o termo *qubit* | DOI `10.1103/PhysRevA.51.2738`; afiliação no artigo | O mapa usa “Ohio” como rótulo curto. |
| Paris/Orsay, França | Alain Aspect | Institut d'Optique, Orsay; experimento de 1982 | DOI `10.1103/PhysRevLett.49.1804`; afiliação no artigo | “Paris” é uma simplificação; Orsay fica na região metropolitana. |
| Berkeley, Califórnia, EUA | John Clauser | Lawrence Berkeley Laboratory/UC Berkeley; proposta de 1969 e experimento de 1972 | DOI `10.1103/PhysRevLett.23.880`; registros institucionais | O mapa marca Berkeley como sede do experimento, não como único local da obra. |

## 3. Base cartográfica

- **Natural Earth** — vetores culturais 1:110m, domínio público.
  <https://www.naturalearthdata.com/>
- **world-atlas@2** — TopoJSON derivado do Natural Earth, usado para
  renderizar o mapa escuro em 4096×1354.
  <https://github.com/topojson/world-atlas>
- Render próprio: `pilots/r1055-qubit/render_world_map.py` (matplotlib/Pillow).
- A base **NASA Blue Marble** foi tentada, mas o host
  `eoimages.gsfc.nasa.gov` não respondeu dentro do tempo limite. A escolha
  pela Natural Earth é profissional, offline e de domínio público, conforme
  a autorização do pedido (“NASA ou um profissional”).

## 4. Voz

- Voz sintética **Microsoft Edge Neural** `pt-BR-FranciscaNeural`, gerada com
  o cliente `edge-tts` (LGPLv3; um arquivo do pacote é MIT).
- **Não há clonagem** de voz humana nem uso da voz do vídeo de referência.
- O áudio foi gerado em 24 kHz mono, com ritmo por batida (0,98–1,08) e pausas
  de 0,20–0,60 s; o master foi normalizado a −14,49 LUFS e pico −4,42 dBTP.
- O áudio XTTS anterior (voz Sofia Hellen) foi preservado em `audio-xtts/`
  apenas para proveniência; **não** integra a entrega final.
- Antes de publicar, confira os termos de uso do serviço de voz neural e a
  política da plataforma de destino.

## 5. Imagens, QR e fontes

- Foto do autor: avatar público do GitHub de MarceloClaro
  (`https://avatars.githubusercontent.com/u/58664974`), usado pelo próprio
  autor no cartão final.
- QR code: gerado localmente com `qrcode` (BSD), apontando para
  <https://github.com/MarceloClaro>. O QR não coleta dados.
- Fontes: DejaVu Sans (licença Bitstream Vera, livre).
- Nenhuma imagem, voz ou trilha do vídeo de referência do Instagram foi
  copiada.

## 6. Software e licenças

| Ferramenta | Uso | Licença/observação |
|---|---|---|
| Remotion 4.0.540 | Composição e render | Núcleo MIT; renderer com licença própria da Remotion. Ver `docs/REMOTION_AUDITAVEL_R1025.md`. |
| FFmpeg | Mux, normalização, QC | LGPL/GPL conforme a build; usado como executável. |
| Python 3.14 + Pillow/NumPy/matplotlib | Mapa, contatos, métricas | PSF/BSD/BSD |
| librosa | Prosódia | ISC |
| faster-whisper | ASR diagnóstico | MIT |
| edge-tts | Voz neural | LGPLv3 (um arquivo MIT) |
| qrcode | QR | BSD |
| Natural Earth | Mapa | Domínio público |

### Pesquisa de motion graphics

Padrões de câmera, Ken Burns, parallax, stagger e “render → inspecionar →
corrigir” foram estudados em:

- **Claude Remotion Skill** (haidrrrry), MIT —
  <https://github.com/haidrrrry/claude-remotion-skill>. Usamos as regras de
  ofício (easing em toda interpolação, entradas com 2–3 propriedades, stagger,
  respiração, camadas e verificação por frames), **sem copiar código**.
- **Remotion Docs** — <https://www.remotion.dev/docs/>.
- **Motion Canvas**, MIT — <https://github.com/motion-canvas/motion-canvas>.
- **Manim Community**, MIT — <https://github.com/ManimCommunity/manim>.
- **Theatre.js**, Apache-2.0 — <https://github.com/theatre-js/theatre>.
- **GSAP** — licença padrão (não é open source); citado apenas como referência
  de timeline, não usado.
- **OpenTimelineIO**, Apache-2.0 — <https://github.com/AcademySoftwareFoundation/OpenTimelineIO>.
- **Blender**, GPL — referência de câmera 3D, não usado no render.

A implementação própria está em
`editor-workspace/remotion-smoke/src/r1055-qubit/cinematic.tsx` e no
`BlochSphere` de `QubitExplainer.tsx`.

## 7. Limites

- O vídeo é uma **síntese didática**, não um curso completo nem uma revisão
  sistemática.
- O mapa simplifica afiliações e deslocamentos; as cautelas da seção 2 valem.
- A voz é sintética; a prosódia foi ajustada, mas não substitui locução humana.
- O ASR foi usado como **diagnóstico**, não como aprovação perceptual.
- O QC técnico (`video_qa.py`) verifica frames, fps, loudness, pico, silêncio e
  pretos; não certifica qualidade estética, rigor científico ou aceitação
  editorial.
- Nada foi publicado automaticamente. A entrega é para revisão humana.
