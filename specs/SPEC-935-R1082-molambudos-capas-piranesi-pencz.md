# SPEC-935-R1082 — Capas Molambudos em gravura Piranesi/Pencz

Data: 2026-11-05. Escopo: artefatos gráficos locais; não altera o miolo, o perfil ou o contrato R1081.

Escolha posterior do autor: a composição preta com ouro envelhecido, diário e coruja passa a ser a capa principal. O conjunto Piranesi/Pencz fica como alternativa visual. A capa principal é aceita com arte nativa >=300 dpi efetivos; a reserva de 2x permanece específica às pranchas Piranesi/Pencz.

Esclarecimento final do autor: conservar a composição preta/ouro e aplicar o traço de Piranesi/Pencz aos elementos brasileiros do romance. A entrega principal é `literatura/molambudos/capas/molambudos_final/`: sertão, caatinga, Rasga Mortalha, diário e arquitetura institucional brasileira, sem cenografia europeia como assunto. O tríptico creme permanece estudo complementar.

Último refinamento: usar a arte fornecida pelo autor (`capas/Sem nome (3012 x 4425 px) (37 x 26 cm).png`, tamanho observado 2000 x 1405 px) e limpar a parte textual. Remover texto multilíngue incorporado, avisos, inscrições e branding da imagem; conservar os elementos ilustrados e reaplicar texto vetorial essencial em português. Guardar as duas artes sem texto e os prompts de limpeza.

## Objetivo

Entregar capa frontal, contracapa, lombada e capa aberta para brochura 160 × 230 mm, com direção Piranesi/Pencz do R1081 e execução editorial real correlacionada ao perfil existente. Capa principal para 422 páginas; alternativa canônica para 436 páginas (435 arredondadas para par). Premissa explícita: cor premium, papel branco, fórmula KDP de 0,002347 polegada/página.

## Aceitação

- Dois PDFs de página única, dimensões físicas derivadas, 3,175 mm de sangria externa, TrimBox e BleedBox.
- Frente e contracapa isoladas de 160 × 230 mm, PNG a 300 dpi, mais masters a 600 dpi.
- Três pranchas originais geradas por IA em tríptico, impressas a 42 mm de largura, com resolução efetiva mínima de 600 dpi; nenhum upscale.
- Papel creme, tinta sépia, um acento carmim por prancha; arquitetura/escala de Piranesi e figura/gesto de Pencz. Legendas externas e identificação de ficção.
- Fontes embutidas, créditos canônicos, nenhum ISBN de exemplo; reserva branca de 50,8 × 30,48 mm no canto inferior direito da contracapa.
- Contrato R1081 e provas determinísticas anteriores preservados, com hashes; imagens novas identificadas como IA, provas anteriores como tratamento determinístico.
- Manifesto, prompts efetivamente enviados, recibos de execução e ficha técnica. Testes em `tests/test_r1082_molambudos_cover_assets.py`.
- Swatches de texto/linha CMYK com soma nominal ≤210%; sem alegar TAC global das imagens RGB, perfil ICC, PDF/X, prova física ou aprovação externa.

## Pranchas de prova (6)

Além das capas, foram montadas 6 pranchas de prova a partir das artes existentes
e de `placa_00`: `carceri-colonia`, `paisagem-erodida`, `arquivo-doente`,
`retrato-emblematico`, `tabela-alegorica` e `anatomia-contaminacao`.

- 300 DPI no tamanho final de 86 mm; 316–345 DPI observados.
- A 2× (172 mm), as fontes caem para 158–173 DPI; não há 2× a 300 DPI sem nova
  arte ou upscale, que foi recusado.
- Caderno de provas de 8 páginas, 160 × 230 mm, com preflight local: fontes
  embutidas, 6 imagens ≥317 DPI, TAC máximo 117,9%.
- O caderno canônico do livro não foi alterado.

## Limites

Homagem visual e reconstituição ficcional; não é documento histórico. Não substituirá revisão humana, previewer da gráfica/KDP ou prova física. A execução externa pela equipe do Codex será distinguida de ativação/registro do perfil e de eventual execução pela ponte Core. Não publicar ou enviar à KDP.
