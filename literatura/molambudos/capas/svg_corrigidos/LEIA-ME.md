# Molambudos — SVGs corrigidos

Entrega de 6 de novembro de 2026, a partir dos três PNGs indicados pelo autor.

## Arquivos

- `CAPA.svg`, `CONTRACAPA.svg`, `LOMBADA.svg`: gravuras e letras em curvas. São as versões preferidas para manter a aparência ao abrir em outro computador; não dependem de fontes instaladas.
- `*_EDITAVEL.svg`: os mesmos elementos com textos editáveis e subconjuntos das fontes incorporados em WOFF2. Aplicativos que ignoram fontes incorporadas podem substituir as letras; nesse caso, use as versões em curvas para preservar a aparência.
- `*_PREVIA.png` e `PREVIA_CONJUNTO.png`: prévias dos SVGs em curvas. Os PNGs são apenas prévias e não estão incorporados nos vetores.
- `textos_corrigidos.txt`: transcrição dos textos recompostos.
- `manifesto.json`, `validacao.json` e `*_LIMITES_TEXTO.json`: origem, hashes e verificações locais.
- `produzir.py`, `verificar.py` e `ESPECIFICACAO.md`: produção e critérios registrados.

## Correções

Revisão dos textos em português, inglês e chinês simplificado; padronização de título, créditos e numeração; acentos nas placas de Ceará e Hospital Colônia; recomposição da inscrição do diário e da ficha do paciente; reorganização da contracapa para legibilidade. A sinopse distingue os 62 anos de internação do tempo de sepultamento. Mantém-se o Paciente 1.260 da narrativa e o Paciente 1.263 do aviso ficcional ao leitor.

A história é ficcional. A referência editorial à cronologia veio da nota do arquivista da edição local, não de uma comprovação histórica. A revisão auxiliar foi executada pelo subagente Codex `revisao_textual`, correlacionada à tarefa A2A `task-b8f38e52` do perfil registrado `book-orchestration-editor`.

## Vetorização e limites

As gravuras foram traçadas por contornos Bézier em dez tons de preto e dourado, usando Potrace 1.16. Não há imagens raster incorporadas, imagens vinculadas, scripts ou filtros nos SVGs. A baixa resolução dos PNGs de origem limita os detalhes que podem ser recuperados: aumentar o SVG não cria novos detalhes da gravura. As letras recompostas permanecem nítidas ao ampliar.

As proporções dos PNGs originais foram conservadas: capa 500 × 749, contracapa 533 × 777 e lombada 109 × 772 unidades SVG. Não foram definidas dimensões físicas, sangria nem largura de lombada para uma tiragem específica. Esta entrega é uma arte vetorial local; não é um fechamento de impressão nem aprovação da gráfica.

Os três PNGs originais permanecem inalterados. A inspeção local inclui integridade XML, referências internas, ausência de raster, preservação dos originais, cobertura de caracteres, limites geométricos dos textos e conferência visual das prévias. As versões editáveis e em curvas foram comparadas por renderização; pequenas diferenças de desenho das fontes entre renderizadores são registradas em `validacao.json`.
