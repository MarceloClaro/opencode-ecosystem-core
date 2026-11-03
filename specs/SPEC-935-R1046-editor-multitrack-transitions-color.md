---
spec_id: SPEC-935-R1046
title: Composição multifaixa, transições e cor com evidência técnica delimitada
component: integrations.video_editor_advanced
status: specified
test_file: tests/test_r1046_video_editor_advanced.py
depends_on:
  - SPEC-935-R1042
---

# SPEC-935-R1046

## Objetivo e escopo autorizado

Pesquisar GitHub e ampliar o editor local em CPU: multifaixa, transições e
cor. Renderizar fixtures próprias para verificar execução real. Não prometer
paridade completa com Premiere/DaVinci nem transformar teste em aprovação
estética, linguística ou científica. Não publicar mídia nem fazer push.

## Pesquisa e decisão

Consultar GitHub/API e documentação primária, registrar URLs, licença e
limites. Avaliar FFmpeg, MLT, libopenshot, OpenTimelineIO, Shotcut e Kdenlive.
Reutilizar o executável FFmpeg instalado; sem clone/build/install ou cópia de
código desses projetos. Bibliotecas adicionais permanecem candidatas.

## Contrato

- Preservar schema de projeto R1042 e operações existentes.
- **`multitrack`**: faixas de vídeo em ordem de composição (última por cima),
  intervalos exclusivos [in,out), posição/dimensão/opacidade/raio de canto por
  clipe, lacunas pretas, faixas de áudio explícitas com ganho e atraso em
  amostras. Não duplicar áudio dos clipes de vídeo implicitamente. Sem áudio
  explícito, gerar silêncio. Comprimento inclui todas as faixas; não truncar
  silenciosamente. Fontes com taxa diferente da timeline são conformadas para
  a taxa do projeto com arredondamento para cima e aviso explícito; VFR continua
  bloqueado.
- `transition`: dois clipes, efeito allowlisted (fade/dissolve/wipes/slides),
  sobreposição em frames menor que os dois clipes, imagem via xfade e áudio
  via acrossfade (silêncio quando ausente). Saída = soma menos sobreposição.
  Ordem explícita de IDs; start_frame original não controla esta sequência.
- `color_grade`: clipe selecionado com brilho, contraste, saturação, gamma e
  balanço RGB de sombras/meios-tons/altas luzes; números finitos e faixas
  documentadas, sem expressões arbitrárias, LUT ou HDR nesta etapa.
- `corner_radius` opcional no transform de `multitrack`: máscara alfa `geq`
  limitada a metade da caixa, combinada com opacidade; sem sombra, borda ou
  animação de raio nesta etapa.
- Novas operações: fontes locais regulares sob raiz do projeto, hashes,
  CFR na mesma taxa da timeline, speed=1, saída MP4 local sem sobrescrita.
  Taxa de fonte diferente é convertida para a taxa da timeline por filtro
  `fps`, com duração em frames calculada por razão e aviso no plano; VFR é
  recusado. Preset x264 é allowlisted (`ultrafast`…`veryslow`) e registrado no
  plano/recibo. Recusar campos desconhecidos relevantes, em vez de ignorar
  configurações não suportadas.
- Pré-render avançado: revalidar digest do plano e hashes das fontes, inclusive
  antes de retornar cache. Conferir fontes via probe, frames decodificados,
  geometria, fps, duração e áudio na saída. Preservar gates MCP/Remotion.
- Recibo: `technical_checks_passed` separado de `audiovisual_approved`,
  `translation_accuracy_verified` e `scientific_validity_verified`; estes
  últimos não podem se tornar verdade por render, ASR ou pytest.
- Expor as três operações pelo `plan` CLI/MCP existente; não oferecer shell.

## Testes antes da implementação

1. Planejamento determinístico, duração, z-order, áudio e ausência de mutação.
2. Contraprovas: NaN/inf/bool, injeção, opções não suportadas, symlink/escape,
   VFR/fps divergente, sobreposição indevida e plano/fonte adulterados.
3. Render real pequeno: regiões de cor antes/durante/depois do overlay,
   mistura temporal em fade, mudança de luminância/croma, contagem decodificada,
   áudio antes/depois do atraso e retomada por recibo.
4. Casos sem áudio e taxa racional 30000/1001; mixed-fps conformado; preset
   inválido bloqueado; raio de canto mascarado.
5. Regressão R1042/MCP, R1033–R1045 e guard Remotion.
6. Aceitação opcional com `pilots/r1026-quantum/source.mp4` (1920×1080,
   30000/1001) + cartão 30 fps: 600 frames, conformidade, overlay mascarado,
   áudio e recibo com flags de qualidade em `false`. O vídeo não é versionado.

## Limites e aceite

Sucesso exige testes e renders efetivamente executados, com logs/hashes; não
basta gerar comandos. Fracasso ambiental fica explícito. Os testes de pixels
e áudio comprovam apenas os predicados das fixtures, não qualidade subjetiva.
A aceitação R1026 comprova execução em mídia real e limites das fixtures; não
comprova aprovação editorial do cartão, sincronia labial ou tradução.
Revisão bilíngue, fontes primárias, metodologia e revisão científica são
etapas distintas, não implementadas como certificado automático nesta rodada.
Sem UI NLE, keyframes, multicam, tracking, nodes, LUT, ACES/HDR, VFR automático,
efeitos 3D, legendas animadas ou sincronização labial nesta entrega.
