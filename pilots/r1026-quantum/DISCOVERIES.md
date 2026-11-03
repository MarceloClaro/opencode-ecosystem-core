# Descobertas — piloto Qiskit (R1026–R1032)

Registro das decisões técnicas e didáticas. Cada item separa evidência,
impacto, decisão e limite.

## 1. Wav2Lip em 1080p estoura a memória

**Evidência:** o primeiro runner em 960×540 atingiu RSS 7.128.024 KB e foi
abortado pelo watchdog de 6 GB antes de concluir o bloco 0. O mesmo modelo em
640×360 consumiu 2,78–3,48 GB por bloco.
**Impacto:** 1080p não é viável neste host sem GPU; a detecção facial em
resolução cheia é o gargalo.
**Decisão:** processar em 640×360 e sobrepor apenas a região do rosto ao vídeo
original 1080p.
**Limite:** a qualidade facial é de estudo, não broadcast; a boca tem menos
detalhe que o resto do quadro.

## 2. O watchdog é o que impede o travamento

**Evidência:** o runner monitora RSS a cada 5 s; abortou o bloco acima de 4,5 GB
em vez de deixar o sistema sem memória. O pico observado no runner estável foi
3,48 GB.
**Impacto:** processar em CPU sem limite de memória pode congelar o desktop.
**Decisão:** watchdog, `nice`, `ionice`, 2 threads, lock e retomada por bloco.
**Limite:** o watchdog não garante integridade do bloco interrompido; o bloco
precisa ser refeito.

## 3. Sobrepor só o rosto preserva o 1080p

**Evidência:** o master composto usa `alphamerge` com máscara elíptica
(`face-mask-1080.png`); slide, fundo e mãos permanecem originais. Frames
`final-16x9-8/15.png` não mostram emenda aparente.
**Impacto:** evita upscalar o frame inteiro do Wav2Lip e perder detalhe fora do
rosto.
**Decisão:** compor a boca sincronizada apenas na região facial.
**Limite:** a máscara é estática; movimentos grandes podem exigir reenquadramento.

## 4. Remotion arredonda a largura para par

**Evidência:** a composição `SlideSequence` foi declarada em 935×864, mas o
render saiu em **934×864**; o `alphamerge` com máscara de 935 falharia.
**Impacto:** um pixel de diferença quebra a composição por máscara.
**Decisão:** `scale=935:864` antes do `alphamerge`.
**Limite:** o ajuste de 1 px é invisível, mas precisa ser documentado.

## 5. O demuxer `concat` desalinhou os segmentos

**Evidência:** no primeiro master de 44 s, o frame em 15 s mostrava a cena 3
quase apagada, embora o arquivo base em 0,5 s mostrasse a cena 1.
**Impacto:** o vídeo parecia correto na duração, mas a ordem dos frames estava
errada.
**Decisão:** trocar o demuxer `concat` pelo filtro `concat`, com
`apad/atrim` para igualar as durações de áudio e vídeo.
**Limite:** a correção exige reencode; não é concatenação sem perdas.

## 6. O 9:16 falhou por SAR diferente

**Evidência:** o filtro recusou a concatenação: `SAR 10240:10239` no intro e
`1:1` no master.
**Impacto:** a versão vertical não era gerada.
**Decisão:** `setsar=1` nos três segmentos antes do `concat`.
**Limite:** normalizar SAR não corrige enquadramento; o layout vertical foi
validado à parte.

## 7. Cenas devem trocar no silêncio

**Evidência:** a fala ocupa 0–5,06 s, 5,86–12,02 s e 12,84–19,56 s; as cenas
foram montadas em 0–5,47, 5,67–12,23 e 12,63–20.
**Impacto:** trocar no meio da frase quebra a leitura.
**Decisão:** usar os intervalos de silêncio para transições.
**Limite:** se a fala for remontada, o timing precisa ser refeito.

## 8. A narração precisa citar todos os itens do roadmap

**Evidência:** a primeira abertura anunciava dois itens, mas exibia três linhas.
A terceira linha aparecia sem narração.
**Impacto:** o espectador lê um item que a voz não apresenta.
**Decisão:** acrescentar “E o limite da simulação.” e atrasar a terceira linha
para 11,5 s.
**Limite:** a frase adicional aumentou a abertura para 14,2 s.

## 9. O ritmo do XTTS varia muito com o texto

**Evidência:** “E o limite da simulação clássica.” gerou 6 s; a versão curta
“E o limite da simulação.” gerou 2,13 s.
**Impacto:** uma frase curta pode dominar a abertura.
**Decisão:** encurtar o texto e medir a duração antes de fixar a composição.
**Limite:** a naturalidade do clone não foi avaliada por escuta humana.

## 10. Palavras-chave destacadas ajudam a leitura

**Evidência:** as legendas com “100 qubits”, “desativados” e “simulados
classicamente” em roxo foram aplicadas em `captions-*-destaque.ass`, mantendo
CPS ≤14,8.
**Impacto:** o destaque fixa o conceito sem aumentar o texto.
**Decisão:** usar no máximo duas palavras-chave por bloco.
**Limite:** cor não substitui contraste; a legenda precisa continuar legível.

## 11. A voz clonada pode narrar a abertura e o encerramento

**Evidência:** XTTS v2 gerou 11,47 s e 9,38 s de narração com a referência de
6 s; os cartões `DidacticIntro16/9` e `DidacticOutro16/9` foram renderizados com
`<Audio>` e concatenados.
**Impacto:** a explicação passa a ter a mesma voz do miolo, sem gravação nova.
**Decisão:** usar a voz clonada também nos cartões, com texto curto.
**Limite:** o consentimento é declarado, não verificado; XTTS/CPML é não
comercial.

## 12. Metadados e frames não provam sincronia

**Evidência:** R1024 retorna `render_metadata_matched` e
`visual_quality_verified: false`; `ffprobe` confirma 44 s, H.264/AAC; os frames
mostram as cenas, mas não o movimento contínuo.
**Impacto:** um vídeo pode passar no gate e ainda ter boca dessincronizada.
**Decisão:** declarar a verificação como estrutural e exigir escuta/revisão.
**Limite:** não houve reprodução contínua com áudio nem aprovação humana.

## 13. Licenças e consentimento delimitam o uso

**Evidência:** XTTS v2/CPML e Wav2Lip são não comerciais; Remotion usa a
Remotion License; o consentimento de voz foi declarado pelo operador.
**Impacto:** o piloto não pode ser tratado como produto comercial nem como voz
oficial da apresentadora.
**Decisão:** registrar `consent-and-licenses.md` e manter o uso como estudo.
**Limite:** o Core não verifica o documento de consentimento.

## 14. A versão didática é mais longa que o clipe

**Evidência:** 14,2 s de abertura + 20 s de miolo + 9,8 s de encerramento =
44,0 s. O clipe original tem 20 s.
**Impacto:** o formato explicador ganha contexto e recapitulação, mas perde
densidade.
**Decisão:** manter o miolo de 20 s e usar os cartões para orientar.
**Limite:** para redes curtas, pode ser necessário cortar a abertura ou reduzir
a narração.

## 15. O cartão branco competia com o slide; o recorte integra a apresentadora

**Evidência:** a primeira versão dos cartões usava `presenter-card.png` dentro
de um retângulo branco. O bloco claro ocupava cerca de um quarto da largura e
dominava a composição. O recorte `presenter-cutout.png` (560×800, alfa>20 em
52,9% da área) sobre o fundo `#2B2145` manteve rosto e corpo sem a caixa branca;
os frames `test-cutout-16.png` e `final-16x9-8.png` mostram a diferença.
**Impacto:** a apresentadora passa a acompanhar abertura e encerramento sem
quebrar a unidade visual com o miolo.
**Decisão:** usar cartão escuro com glow roxo, recorte e zoom lento; manter o
rótulo “APRESENTADORA / VOZ SINTÉTICA”.
**Limite:** a matte usa limiar de luminosidade e morfologia, não um modelo de
segmentação; franjas de cabelo/ombro podem aparecer em tela grande e não houve
revisão humana.

## 16. A linha do tempo vertical preenche o 9:16 e acompanha a narração

**Evidência:** no 9:16, as três linhas compactas terminavam por volta de 900 px
e deixavam quase metade do quadro vazia. A linha do tempo vertical distribui os
passos a cada 340 px e acende cada um nos atrasos 45/135/345 (abertura) e
0/75/150 (encerramento). Frames `final-9x16-8.png` e `final-9x16-40.png`.
**Impacto:** o formato vertical mantém a apresentadora no topo, o roadmap
legível e a ordem da narração.
**Decisão:** usar timeline vertical no 9:16 e linhas compactas no 16:9.
**Limite:** ainda há respiro inferior; a ativação é temporal e não prova
sincronia labial nem compreensão do espectador.

## 17. A apresentadora pode dublar os cartões com lip sync

**Evidência:** o Wav2Lip gerou `presenter-intro-1080.mp4` (14,2 s) e
`presenter-outro-1080.mp4` (9,8 s) a partir das narrações clonadas. O recorte
`presenter-intro-card.mp4` tem 426 frames em 560×700 e mostra a boca aberta em
2 s, 7 s e 12 s (`intro-card4-7.png`, `lipsync-intro16-7.png`). O áudio continua
em `<Audio>` separado e o vídeo do cartão é mudo.
**Impacto:** a apresentadora passa a falar e explicar nos cartões, em vez de
aparecer como retrato estático.
**Decisão:** usar vídeo com lip sync no cartão, recortado em cabeça e ombros,
com o áudio da narração fora do vídeo.
**Limite:** a qualidade do lip sync em CPU não foi avaliada por escuta humana;
frames com boca aberta não provam sincronia contínua.

## 18. Matte suave e enquadramento fechado integram o vídeo ao cartão

**Evidência:** a primeira matte por frame (V>150 e S<55) deixava um halo claro no
cabelo e manchas brancas nas frestas entre mãos e corpo (`matte-a1.png`). A
matte suave `V*(1-S)`, com recorte 560×700 em cabeça e ombros e fade inferior,
removeu as manchas (`matte-closeup-preview.png`, `intro-card4-7.png`). O
GrabCut foi testado e preservou um bloco branco atrás da apresentadora
(`matte-a3.png`), por isso foi descartado.
**Impacto:** o vídeo falante entra no fundo escuro sem caixa branca e sem
competir com a animação.
**Decisão:** matte suave por frame, fundo do cartão assado no vídeo e corte
inferior de 20 px.
**Limite:** a matte continua heurística; franjas de cabelo e gestos rápidos
podem exigir revisão. Não houve validação em tela grande.

## 19. O lip sync em blocos congelava a cada 5 s

**Evidência:** a análise de diferença entre frames do cartão em blocos mostrou
corridas de baixa movimentação em 4,87–4,97 s e 9,87–9,97 s, exatamente nas
emendas dos blocos de 5 s. Depois da passada contínua, a corrida de 10 s
desapareceu; restou apenas uma pausa natural em 5,4–5,47 s e o hold do fim.
**Impacto:** a apresentadora parecia travar a cada cinco segundos.
**Decisão:** usar `render-presenter-card-whole.sh`, com uma única passada do
Wav2Lip e `tpad` no fim; a versão em blocos fica como fallback.
**Limite:** a análise é por diferença de frames, não por reprodução contínua ou
escuta humana.

## 20. O miolo antigo não deve ser concatenado com o cenário novo

**Evidência:** o master anterior usava `pilot-*-didatico-base.mp4` como miolo,
com o slide branco antigo. O novo miolo é `didactic-middle-16/9.mp4`, composto
por `slide-sequence-dark.mp4` e `presenter-middle-card.mp4`; o
`concat-didatico.sh` agora referencia apenas o miolo novo. Frames `r1032-20.png`
e `r1032-30.png` mostram o cenário escuro contínuo.
**Impacto:** a abertura, o miolo e o encerramento passam a ter a mesma
linguagem visual, sem corte para o vídeo antigo.
**Decisão:** não concatenar o miolo antigo; manter o miolo novo no cenário
escuro e o áudio de 20 s.
**Limite:** o cartão do miolo usa o lip sync já existente do áudio de 20 s; não
houve nova avaliação de sincronia por escuta.

## 21. A mancha em “M” era fundo branco na borda esquerda

**Evidência:** o recorte 560×700 ainda incluía um bloco branco puro em
x≈115–145, y≈405–430, ao lado do ombro. A máscara de borda esquerda
(`x<180`, `y 300–540`, `V>0.80`, `S<0.20`), com dilatação, removeu o bloco; o
zoom `whole-left-edge-zoom.png` mostra a borda limpa.
**Impacto:** a mancha em “M” desapareceu do cartão.
**Decisão:** manter a limpeza de borda e a decontaminação de cor na matte.
**Limite:** a limpeza é heurística; gestos muito rápidos podem exigir ajuste.
