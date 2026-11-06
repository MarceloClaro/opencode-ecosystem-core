# Molambudos — capa, contracapa e lombada

**Versão principal escolhida pelo autor nesta conversa:** preto e ouro envelhecido, diário e coruja. A alternativa Piranesi/Pencz está preservada em pasta própria.

Produção local de 5 de novembro de 2026. Proposta editorial baseada no texto da edição de impressão R1077, preservando título, autoria e crédito secundário. Artes novas geradas por IA; tipografia e ornamentos vetoriais. Não altera a obra nem substitui as capas anteriores.

## Arquivo principal

`molambudos_capa_completa_422p_print_300dpi.pdf` corresponde ao miolo `Molambudos_Print_R1077/main_kdp_print_r1077.pdf`, conferido com **422 páginas e 160 × 230 mm**.

- Encadernação: brochura.
- Premissa de produção: **cor premium, papel branco, KDP**, herdada do projeto de capa existente. Outro papel ou fornecedor exige recálculo da lombada.
- Lombada: `422 × 0,002347 polegada = 25,1570236 mm`.
- Capa aberta com sangria: **351,5070236 × 236,35 mm**.
- Corte da frente e da contracapa: **160 × 230 mm** cada.
- Sangria externa: **3,175 mm** em cada borda externa.
- Textos afastados do corte; texto de lombada com folga superior a 1,6 mm das dobras.
- Reserva de código de barras: **50,8 × 30,48 mm**, no canto inferior direito da contracapa, com 6,35 mm de afastamento do corte e da lombada. Área vazia, sem ISBN inventado ou código de exemplo.

## Alternativa canônica

`molambudos_capa_completa_436p_canonica_300dpi.pdf` corresponde à impressão do miolo canônico de 435 páginas, **arredondado para 436 páginas** pela regra de página par da KDP. Não usar esta lombada com o miolo de 422 páginas.

## Resolução e formato

As duas ilustrações de origem possuem 1024 × 1536 pixels. Elas são usadas com **86 mm de largura**, correspondendo a aproximadamente **302,4 dpi efetivos**, sem ampliação ou interpolação. O desenho da capa usa uma prancha central, fundos e ornamentos vetoriais, mantendo a nitidez nativa da arte. Título, sinopse e créditos permanecem vetoriais nos PDFs, com fontes embutidas. Os PNGs finais são renderizados a 300 dpi, com dimensões em pixels arredondadas para cima pelo renderizador.

Os PDFs são os arquivos de dimensão física exata para produção. Os PNGs individuais são recortes no tamanho de corte, sem sangria; para impressão da capa inteira usar o PDF ou o PNG identificado `capa_aberta_com_sangria`. Cor RGB de produção KDP, sem alegação de prova de cor ou conversão CMYK perfilada.

## Critérios de aceitação e conferência

O processo reabre cada PDF e verifica: uma página; dimensões; TrimBox/BleedBox; textos e créditos; ausência de ISBN de exemplo; fontes embutidas; duas imagens a pelo menos 300 dpi efetivos; arquivo sem criptografia; ausência de caixas excedentes na compilação; PNGs com metadados de 300 dpi. Resultado em `preflight_local.json`. As prévias precisam ser examinadas visualmente antes da entrega.

Limite: validação local. Ainda requer conferência no previewer oficial da KDP ou no gabarito da gráfica e prova física; não houve envio ou publicação. A vinculação de ISBN da edição revista depende do autor e não foi inferida da edição anterior.

Fontes de produção: `Molambudos_Print_R1077/frontmatter/titlepage_print.tex`, `frontmatter/preface.tex`, `frontmatter/backpage_print.tex`, fragmentos MEM e LUC, `Molambudos_VictoriaRegia/capa_completa_pt_160x230mm.tex`.

Referências oficiais consultadas: [Criar capa de brochura](https://kdp.amazon.com/en_US/help/topic/G201953020), [Requisitos de envio e arredondamento de páginas](https://kdp.amazon.com/en_US/help/topic/G201857950). As fórmulas de espessura e sangria foram conferidas nestas páginas.

Reprodução local: em `fontes/`, executar `python3 produzir.py` em ambiente com XeLaTeX, fontes EB Garamond/Lato, PyMuPDF e Pillow. As artes originais são preservadas.
