# Referência 01 — explicador vertical sobre o Monte Roraima

**ID:** r1059-reference-01 · **Versão da extração:** 1
**Fonte:** vídeo MP4 fornecido pelo usuário, hospedado em CDN do Instagram.
**URL:** omitida por conter parâmetros assinados; hash da URL em
`access-receipt.json` (fora do pacote versionado).
**Arquivo local:** `source.mp4` (não redistribuído neste repositório).
**SHA-256 da mídia:** `9e1a716e9ca4b282fa40759d23acdd725d4ad2b973ec5242ba667c45c342cdbe`
**Inventário:** 82,174708 s · 720×1280 · 30/1 fps · H.264 · AAC 48 kHz estéreo · 13.042.795 bytes.

## 1. Escopo e origem dos tempos

Tempos em segundos desde o início do arquivo acessível. Não há deslocamento
conhecido em relação a uma publicação maior. O vídeo foi obtido por HTTPS,
sem cookies ou autenticação, em 2026-11-05T00:18:14Z.

## 2. Cobertura

| Modalidade | Status | Método | Lacuna |
|---|---|---|---|
| Visual | parcial | 9 folhas de contato a 2 fps (0–82,17 s) + 2 candidatos de corte | Sem reprodução contínua; movimento entre amostras não observado |
| Áudio | parcial | detecção de fala + transcrição automática | Sem escuta humana; música/SFX não classificados |
| Transcrição | parcial | faster-whisper `small`, CPU, 21 segmentos | Nomes/números não conferidos por escuta |

A inspeção de amostras não prova cortes, tracking ou duração de estados entre
elas. Os candidatos de corte (`22,27 s`, `40,50 s`) vêm de `ffmpeg scene > 0,15`
e não foram confirmados quadro a quadro.

## 3. Mapa interpretado

| Unidade | Intervalo | Foco |
|---|---|---|
| U1 | 0–22,3 | mesa de pedra, mapa da América do Sul, três países, ponto triplo |
| U2 | 22,3–40,5 | escala de tempo geológico e comparação com dinossauros/Andes |
| U3 | 40,5–55,0 | tepuis, ilha no céu, fauna endêmica, chuvas, três bacias |
| U4 | 55,0–62,0 | Arthur Conan Doyle e *O Mundo Perdido* (1912) |
| U5 | 62,0–69,5 | trilha de subida pelo lado venezuelano |
| U6 | 69,5–76,5 | estado de Roraima e síntese “ilha no céu” |
| U7 | 76,5–82,17 | encerramento com marca, like e inscrição |

## 4. Fala

Transcrição automática disponível em `transcription-machine.json` (fora do
pacote). Não houve escuta humana; palavras isoladas e números podem divergir.
O texto na tela foi tratado separadamente da fala.

## 5. Achados por dimensão

| Dimensão | Achado | Status | Evidência |
|---|---|---|---|
| Enquadramento | vertical 9:16; mapas em tela cheia; texto no terço inferior | observado | e01 |
| Crop/zoom/tracking | zoom lento sobre mapas; ilustração fixa no centro | observado | e01 |
| Tipografia | título branco condensado em caixa alta; etiquetas amarelas com texto escuro | observado | e01 |
| Cor/luz | base verde-azulada escura; acentos amarelo, ciano e verde; vinheta | observado | e01 |
| Legendas | pílula inferior central; uma linha na maioria dos estados | observado | e01 |
| Inserções | bandeiras, ícones, capa de livro e fotografias com moldura branca | observado | e01 |
| Transições | cortes secos alternados com entradas por escala/opacidade | inferido | e01, e02 |
| Composição/camadas | mapa + ilustração isométrica + texto sobreposto | observado | e01 |
| Alfa/3D | ilustração aparenta volume; método 3D não comprovado | nao_verificavel | — |
| Ritmo/pausas | unidades de ~2–4 s; 7 unidades em 82 s | observado | e01 |
| Áudio/música/SFX | fala presente; trilha e efeitos não classificados | nao_verificavel | e04 |
| Fala/movimento | mudanças de texto próximas das fronteiras da fala | inferido | e01, e04 |

Fonte exata, plugin, preset e técnica de recorte não são verificáveis apenas
pela imagem comprimida.

## 6. Regras adaptáveis

1. **Legenda-pílula:** quando a fala enuncia um fato, manter uma pílula de alto
   contraste no terço inferior, com uma ideia por estado. Testar leitura no
   tamanho final.
2. **Mapa como palco:** usar mapa escurecido com vinheta; zoom lento funciona
   como câmera, não como decoração. Evitar texto sobre áreas claras.
3. **Cartão de capítulo:** trocar assunto com título curto em caixa alta e
   acento de cor; manter no máximo duas linhas.
4. **Objeto-âncora:** repetir a mesma ilustração do tepui como fio condutor,
   mudando escala/posição em vez de criar um desenho novo a cada ideia.
5. **Conectores rotulados:** bandeiras/etiquetas ligadas ao objeto por linhas
   tracejadas; usar somente quando a relação geográfica for o conteúdo.
6. **Inserção documental:** fotografia ou capa com moldura clara e legenda
   curta, entries por escala; não usar como prova de causalidade.

## 7. Aplicação e limites

O piloto R1059 aplica as regras 1–5 em 10 s, com mapa EOX/Natural Earth,
ilustração vetorial original no Motion Canvas e montagem no Remotion. Não
reutiliza marca, voz, textos, bandeiras oficiais, fotografias ou assets do
vídeo de referência. A regra 6 não foi usada.

**Limites:** amostragem visual de 2 fps; sem escuta humana; sem confirmação de
cortes; técnica 3D/alfa não verificável; direitos da referência não transferidos.
