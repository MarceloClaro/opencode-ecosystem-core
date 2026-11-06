# Molambudos — capa Piranesi/Pencz

**Alternativa de direção visual.** O autor preferiu posteriormente a composição preta com ouro envelhecido, diário e coruja, preservada em `../edicao_2026-11-05/` como capa principal. Este pacote não substitui essa escolha.

Pacote iniciado em 5 de novembro de 2026. Direção visual derivada do contrato R1081 fornecido pelo autor: arquitetura opressiva e escala de Piranesi, figura e gesto de Pencz, papel visual creme, tinta sépia e um detalhe carmim por prancha. Três gravuras originais geradas com a ferramenta de imagem disponível nesta sessão; composição editorial em tríptico: **Memória / Confinamento / Arquivo**.

## Arquivo a usar

`molambudos_capa_completa_422p_print_300dpi.pdf` é a capa aberta principal para o miolo `Molambudos_Print_R1077/main_kdp_print_r1077.pdf`, de **422 páginas**, conferidas diretamente no PDF. Inclui contracapa, lombada e frente em uma única página, com sangria externa e sem guias técnicas impressas.

`molambudos_capa_completa_436p_canonica_300dpi.pdf` é a alternativa para o miolo canônico de **435 páginas**, arredondado para **436 páginas** na impressão KDP. Não misturar as lombadas.

| Parâmetro | Principal | Alternativa canônica |
|---|---:|---:|
| Corte da frente e contracapa | 160 × 230 mm | 160 × 230 mm |
| Páginas para calcular lombada | 422 | 436 |
| Lombada | 25,1570 mm | 25,9916 mm |
| Capa aberta com sangria | 351,5070 × 236,35 mm | 352,3416 × 236,35 mm |
| Sangria externa | 3,175 mm | 3,175 mm |
| PNG da capa aberta, 300 dpi | 4152 × 2792 px | 4162 × 2792 px |

Premissa física: **brochura, cor premium, papel branco, KDP**, herdada do projeto existente. O creme é a cor visual do fundo. Outro papel ou fornecedor exige recalcular a lombada. Fórmula: páginas × 0,002347 polegada × 25,4. [Referência oficial KDP](https://kdp.amazon.com/en_US/help/topic/G201953020).

## Imagens separadas e masters

Em cada pasta de paginação há frente e contracapa de **1890 × 2717 px a 300 dpi**, lombada isolada e capa aberta com sangria. Os painéis separados estão no tamanho de corte, sem sangria. Para impressão da capa inteira usar o PDF ou o PNG `capa_aberta_com_sangria`.

Os masters da frente e da contracapa têm **3780 × 5434 px a 600 dpi**. As ilustrações originais de 1024 × 1536 px são colocadas a **42 × 63 mm**, aproximadamente **619,28 dpi efetivos**, satisfazendo a reserva de resolução de 2× para o tamanho em que foram compostas. Não há upscale nem ampliação artificial. Os PDFs conservam texto e ornamentos vetoriais e as três imagens raster nativas; não são alegados como arte integralmente vetorial.

A reserva do código de barras é branca e vazia, **50,8 × 30,48 mm**, no canto inferior direito da contracapa, afastada 6,35 mm do corte e da lombada. Não foi inserido ISBN: a vinculação da edição revista depende do autor. [Regras de código de barras](https://kdp.amazon.com/en_US/help/topic/G5HDYGP4BXLX4RUW).

## Contrato, provas e execução do perfil

- `contrato/style_pack_original.json` e `README_original.md`: cópias preservadas do contrato R1081, incluindo gramática, seis tipos de prancha e prompts multilíngues. A afirmação de modelo indisponível é o registro histórico daquela execução.
- `provas_deterministicas/`: três provas anteriores e sua folha de contato; arquivos preservados byte a byte e hashes conferidos. São tratamentos de pranchas existentes, não imagens novas.
- `fontes/arte_sertao.png`, `arte_confinamento.png`, `arte_arquivo.png`: as três imagens novas geradas por IA; cada uma possui um único acento carmim visível. Prompts usados em `contrato/prompts_geracao.json`.
- `contrato/perfil_ativacao.json`: ativação do perfil existente pelo MarceloClaro, A2A `task-16e5a510`; revisão editorial externa efetivamente executada pelo subagente do Codex.
- `contrato/perfil_primeira_tentativa.json`: execução da ponte Core com leitura bloqueada; resultado substantivo parcial, embora o avaliador heurístico tenha retornado sucesso.
- `contrato/perfil_execucao_editorial.json`: tarefa real `task-0c4481f8`, perfil `romance-psicologico-molambudos`, executor Codex, retorno 0. Concluiu briefing, confirmação de créditos e sinopse usando os trechos documentais fornecidos pelo primário; não alegou leitura própria dos arquivos.

## Conferência e limites

`preflight_local.json` registra dimensões, paginação, resolução efetiva, fontes embutidas e textos. A aceitação independente está em `tests/test_r1082_molambudos_cover_assets.py`; a especificação está em `specs/SPEC-935-R1082-molambudos-capas-piranesi-pencz.md`. O manifesto contém hashes das saídas e origens. As prévias devem ser examinadas visualmente; o resultado dessa inspeção fica em `REVISAO_VISUAL.md`.

Os swatches vetoriais CMYK de texto/linha têm soma nominal inferior a 210%. As ilustrações permanecem RGB: **não foi medido TAC global após conversão ICC**, nem produzido TIFF de precisão nativa de 16 bits, PDF/X ou prova de cor. PNGs são sem perdas; não se confunde exportação de maior profundidade com informação tonal nova.

Todas as cenas são **reconstituições ficcionais geradas por IA, em homagem visual**, sem copiar uma prancha específica e sem identificar vítimas reais. A capa está montada para revisão editorial; a aprovação humana, o previewer oficial e a prova física de impressão permanecem pendentes. Nenhum upload ou publicação foi realizado. A numeração R1082 não declara validação externa.

Reprodução local: `python3 fontes/produzir.py` com XeLaTeX, EB Garamond, Lato, PyMuPDF e Pillow. Os arquivos do miolo e as capas anteriores são preservados.
