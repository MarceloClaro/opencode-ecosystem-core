# SPEC-935-R1058 — Vídeo do plano de ação Airam Veras

## Objetivo

Produzir um vídeo didático, em português brasileiro, sobre o plano de ação
pedagógica SPAECE de novembro de 2026 da Escola de Cidadania Airam Veras
(Crateús/CE), 5º ano A e B, Língua Portuguesa e Matemática. O vídeo deve
explicar, em sequência lógica, o diagnóstico, as habilidades prioritárias, o
cronograma de intervenções das professoras, exemplos de conteúdos e questões,
o porquê dessas questões, as metas e o monitoramento.

## Insumos

- `Plano_Acao_SPAECE_Novembro_2026_5Ano_A_B_Airam_Veras.pdf` (34 páginas).
- `Dossie_Unico_5Ano_A_B_Airam_Veras_2026_Com_Matematica_CORRIGIDO.pdf`
  (3.226 páginas; consolidado CAEd/UFJF, data-base 11/08/2026).
- Logo da escola extraída da capa do dossiê institucional.
- Limites estaduais/municipais do IBGE e mapa de ruas OpenStreetMap.

## Requisitos

1. Vídeo 1440×810, 30 fps, narração institucional PT-BR sintética; agradecimento final com voz clonada do próprio autor, autorizada e aplicada em uma frase curta.
2. Logo da escola na abertura e no fechamento.
3. Mapa dinâmico Ceará → Crateús → Maratoan, com zoom de câmera e ponto
   pulsante na escola; atribuição OSM/IBGE visível.
4. Diagnóstico agregado: LP, Matemática, fluência e escrita, com a ressalva de
   que é linha de base de agosto, não resultado de novembro.
5. Habilidades prioritárias e marcadores de menor acerto, deixando claro que
   H01–H20 são marcadores do arquivo CAEd e não descritores oficiais.
6. Cronograma de 03 a 30/11, cinco semanas, avaliações e rotina semanal fixa (segunda a sexta), com prova em 01/12/2026.
7. Exemplos de LP e Matemática, com pergunta, resposta esperada e explicação
   do porquê de cada questão.
8. Responsáveis, grupos C1–C4, metas propostas e monitoramento.
9. Não expor nomes, resultados individuais ou rankings de estudantes.
10. Não declarar resultado novo, eficácia, aceite ou publicação.

## Critérios de aceitação

| ID | Critério | Verificação |
|---|---|---|
| A1 | 13.749 frames, 30/1 fps, 1440×810 | `ffprobe` + `video_qa.py` |
| A2 | Duração 458,3 s ±1,0 s | `ffprobe` |
| A3 | Loudness −14 ±1 LUFS; true peak ≤ −1,5 dBTP | `video_qa.py` |
| A4 | Logo e mapa presentes nos frames de controle | stills + inspeção |
| A5 | Ponto pulsante na escola e zoom Ceará→Crateús→ruas | stills + código |
| A6 | Nenhum nome de estudante no vídeo | inspeção de texto/ASR |
| A7 | Dados agregados conferem com o plano/dossiê | checklist |
| A8 | Exemplos e porquês aparecem com resposta esperada | inspeção |
| A9 | Sem silêncio >4 s e sem frame preto >0,2 s | `video_qa.py` |
| A10 | Nada publicado automaticamente | declaração no relatório |

## Fora de escopo

- Atualizar resultados de novembro ou prever o SPAECE.
- Substituir o plano oficial, o calendário escolar ou a matriz do SPAECE.
- Expor dados nominais do dossiê.
- Publicar em redes sociais ou repositório remoto sem autorização.
