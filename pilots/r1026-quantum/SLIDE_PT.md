# Slide PT-BR — tradução e redesign

## Texto original (EN)

- "What is this course?"
- "What is *practical* quantum computing?"
- "Eagle — 127 qubits"
- "Heron — 133 qubits × p"
- "100+ qubit quantum chips widely available for use"

## Adaptação PT-BR

| Original | Adaptação |
|---|---|
| What is this course? | **Computação quântica na prática** |
| What is practical quantum computing? | **Processadores IBM com mais de 100 qubits** |
| Eagle — 127 qubits | **Eagle — 127 qubits** |
| Heron — 133 qubits × p | **Heron — 133 qubits × p** |
| 100+ qubit chips widely available | **Mais capacidade de 100+ qubits** |

### Callout didático

**Por que a mudança?**

"Alguns números de qubits ainda podem ser simulados classicamente. Os chips
maiores abrem espaço para problemas que a simulação não alcança. É por isso que
os processadores menores saíram de linha."

Essa frase conecta o slide à fala da apresentadora: a IBM desativou
processadores menores para abrir espaço aos chips de 100+ qubits, porque certos
tamanhos ainda são simuláveis classicamente.

## Decisão de composição

- O patch tem **935×864 px** e é aplicado em **(210, 76)** sobre o slide.
- O conteúdo fica à esquerda; a apresentadora ocupa a direita e não é coberta.
- A máscara tem bordas suavizadas para não criar emenda no fundo `#F5F3FF`.
- O slide original é preservado no arquivo-fonte; o patch é uma camada separada.
- O patch não copia o layout original: usa tipografia, cards e ícones próprios,
  inspirados nos conceitos Eagle/Heron.

## Sequência animada

A versão `-anim` substitui o patch estático por uma sequência Remotion
(`SlideSequence`, 934×864, escalada para 935×864, 30 fps, 20 s), composta em
`(210, 76)` com a mesma máscara.

| Cena | Tempo | Conteúdo |
|---|---|---|
| 1 | 0,0–5,47 s | contexto: 100+ qubits amplamente disponíveis |
| 2 | 5,67–12,23 s | mudança: Eagle/Heron e a desativação dos menores |
| 3 | 12,63–20,0 s | por quê: simulação clássica e limite dos chips maiores |

A sequência tem cabeçalho fixo, barra de progresso, indicador `01/03`, entrada
por `spring` e transições nos intervalos de silêncio. Fonte:
`slide-sequence.mp4`. Aplicação: `apply-slide-anim.sh`. Saídas:
`pilot-16x9-lipsync-anim.mp4` e `pilot-9x16-lipsync-anim.mp4`.

O patch estático (`slide-patch.png`) permanece como alternativa e fallback.

## Limites

- É uma **adaptação didática para estudo**, não uma peça oficial da Qiskit.
- A tradução é interpretativa; não é verbatim e deve ser revisada antes de
  publicação.
- O texto do slide é menor na versão 9:16 porque o frame 16:9 é reduzido; nessa
  versão, a legenda carrega a mensagem principal.
- O patch cobre o texto antigo à esquerda; o lado direito do slide permanece
  original, atrás da apresentadora.

## Reprodutibilidade

```bash
python3 make_slide_patch.py       # slide-patch.png + máscara
./apply-slide.sh                 # aplica no master e gera -pt.mp4
```

Arquivos: `slide-patch.png`, `slide-patch-mask.png`, `slide-test.png`,
`slide-test-210.png`.
