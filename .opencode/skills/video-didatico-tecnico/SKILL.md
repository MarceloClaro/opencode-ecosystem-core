---
name: video-didatico-tecnico
description: Planeje, produza e revise vídeos técnicos didáticos com slides animados, narração, legendas e lip sync, preservando timing, acessibilidade, proveniência e limites. Use para aulas, explicadores, demos e portfólios; não clone voz sem consentimento, não prometa qualidade profissional sem revisão humana e não trate metadados como prova de sincronia.
metadata:
  version: "1"
  origem: "R1029 — destilada do piloto Qiskit (R1026-R1028)"
---

# Vídeo didático técnico

Produza um vídeo que ensine, não apenas que mostre. A unidade é a **ideia por
cena**: uma pergunta, uma evidência e uma consequência. O restante é suporte.

## Princípios didáticos

- Abra com um **roadmap curto**: 3 pontos, não 10.
- Cada cena responde a uma pergunta e prepara a próxima.
- Troque de cena nos **intervalos de silêncio** da fala, não no meio da frase.
- Use **uma hierarquia visual**: sobrancelha, título, corpo; no máximo duas
  linhas de legenda.
- Repita no encerramento as 3 ideias que o espectador deve levar.
- Preserve rosto, slide e legenda em áreas distintas; margens de 5–10%.
- Destaque **palavras-chave** na legenda, mas mantenha ≤17 CPS.
- Narração de abertura/encerramento deve ser curta e mencionar todos os itens
  do roadmap. Se a voz não citar um item, remova o item ou regrave a narração.

Leia [Princípios didáticos](references/principios-didaticos.md).

## Efeitos e motion

Use movimento para **orientar a leitura**:

- entrada por `spring` com deslocamento curto;
- barra de progresso contínua;
- ponto móvel em linha do tempo;
- marcador em escala;
- destaque de palavra-chave na legenda;
- cartões de abertura/encerramento com a mesma tipografia.

Evite efeitos que competem com a fala: zoom contínuo, partículas, contagem que
sugere medição, transições longas e texto sobre o rosto. Cada efeito precisa de
uma função; se não tiver, remova.

## Apresentadora e cartões

Quando houver apresentadora:

- se ela precisar **falar e explicar**, gere um vídeo com **lip sync** (Wav2Lip
  em CPU ou modelo equivalente) e use o vídeo no cartão; retrato estático com
  áudio não mostra a boca falando;
- recorte em **cabeça e ombros** (ex.: 560×700), aplique matte suave por frame e
  componha sobre o fundo do cartão; mantenha o áudio separado e o vídeo mudo;
- mantenha a área da animação livre: texto/roadmap à esquerda no 16:9 e no topo
  no 9:16;
- no 9:16, distribua os três pontos em uma **linha do tempo vertical**; no 16:9,
  use linhas compactas com a mesma ordem;
- rotule “voz sintética” quando a narração for clonada;
- trate a matte como aproximação: limiar e morfologia não são segmentação
  profissional e podem deixar franjas no cabelo;
- sem lip sync disponível, prefira retrato estático e não simule fala.

Leia [Efeitos e motion](references/efeitos-e-motion.md).

## Pipeline

1. **Transcrição** com ASR local; preserve idioma, segmentos e palavras.
2. **Tradução** revisável; legenda não é verbatim por definição.
3. **Voz** com TTS/clone somente se houver consentimento; registre licença.
4. **Lip sync** em CPU em **passada contínua**, com watchdog; blocos de 5 s
   podem congelar nas emendas. Ou GPU.
5. **Slides** em Remotion, com cenas sincronizadas e composição mascarada.
6. **Legendas** em ASS, com CPS e palavras-chave.
7. **Concatenação** pelo filtro `concat`, com `apad/atrim` e `setsar=1`; não
   misture o cenário novo com o miolo antigo.
8. **QC** por `ffprobe`, loudness, frames e escuta humana.

Leia [Pipeline e erros](references/pipeline-e-erros.md).

## Metacognição e registro

Cada descoberta deve virar um registro com **evidência**, **impacto** e
**decisão**. Separe o que foi observado do que foi inferido. Registre no
`DISCOVERIES.md` do projeto e no MetaBus/EvolutionRegistry do Core; não promova
confiança por um sucesso local.

Leia [Registro de descobertas](references/registro-de-descobertas.md) e o
exemplo real em `pilots/r1026-quantum/DISCOVERIES.md`.

## Limites

- Metadados e frames **não provam** sincronia labial, inteligibilidade ou
  qualidade editorial; isso exige reprodução com áudio e revisão humana.
- Clone de voz exige **consentimento** e identificação como sintético; o Core
  não verifica o documento.
- XTTS v2/CPML e Wav2Lip têm uso **não comercial**; Remotion usa a Remotion
  License. Verifique a **licença** antes de publicar.
- A tradução e o slide são adaptação didática, não material oficial da fonte.
- Nada é publicado sem autorização e revisão final.
