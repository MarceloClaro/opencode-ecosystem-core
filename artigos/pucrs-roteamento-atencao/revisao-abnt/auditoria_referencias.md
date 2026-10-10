# Auditoria das referências — revisão de 10 de outubro de 2026

A bibliografia contém **51 entradas**. A revisão preservou todas as chaves de citação e as versões de documento citadas originalmente. A apresentação foi normalizada para o sistema autor-data da NBR 10520:2023 e os elementos das referências para a NBR 6023:2025.

Foram obtidos, nesta execução, **41 registros de metadados da API Crossref**, **nove páginas primárias do arXiv** e o registro de **Vaswani et al. (2017) na editora dos anais NeurIPS**. Os 16 retornos HTTP 429 da primeira coleta foram resolvidos por uma nova série de consultas espaçadas. O arquivo `auditoria_referencias.json` registra a fonte, o estado da coleta, os campos bibliográficos e a referência final de cada entrada.

| Tipo de documento | Quantidade |
| --- | ---: |
| Artigo de periódico | 27 |
| Trabalho em evento | 12 |
| Preprint | 9 |
| Livro | 2 |
| Capítulo de livro | 1 |
| Total | 51 |

## Alterações realizadas

- Ordenação alfabética; autores institucionais identificados; chamadas com os três sobrenomes para trabalhos com até três autores e primeiro sobrenome seguido de *et al.* para quatro ou mais autores.
- Retirada das anotações editoriais “Verificada no Crossref”, “Sem DOI verificado” e equivalentes da bibliografia impressa. A classificação de preprint foi mantida como informação bibliográfica.
- Inclusão de “Disponível em” e “Acesso em: 10 out. 2026” nas 51 entradas; DOIs existentes preservados e nove DOIs do arXiv identificados diretamente nas páginas primárias.
- Nome, ano e local dos eventos, título dos anais, local de publicação, editora e páginas completados com metadados primários disponíveis.
- Tratamento de Lean 4 e Z3 como trabalhos em eventos e de Bridle (1990) como capítulo de obra editada, em vez de artigo de periódico.
- Número da conferência NIPS 2017 corrigido para 31; o volume dos anais permanece 30. A fonte oficial confirma os dois elementos separadamente.
- Volume 372 incluído em Page et al. (2021); identificadores de artigo acrescentados em Wilkinson et al. (2016) e Open Science Collaboration (2015).
- Páginas 1–26 incluídas em Efron (1979), confirmadas pelo currículo do próprio autor hospedado pela Stanford University. A página do periódico apresentou bloqueio de conteúdo apesar do retorno HTTP 200.
- Editora do *Handbook of Floating-Point Arithmetic*, segunda edição, ajustada para Birkhäuser, Cham, conforme a ficha da editora; local de Wohlin et al. (2012) especificado como Berlin; Heidelberg.
- Subtítulo de Cumming (2014), “Why and How”, preservado e confirmado em nova consulta ao Crossref.

## Limitações e pendências

A confirmação de identidade e dos campos bibliográficos não constitui validação dos resultados científicos, reprodução computacional ou auditoria da correspondência entre todas as afirmações do texto e seus artigos.

As localidades ausentes nos registros consultados foram indicadas por **[s. l.]** ou **[S. l.]**, sem atribuir uma cidade por suposição. Isso abrange as localidades dos periódicos e as localidades de publicação de Vaswani (2017), Deng (2009) e Wolf (2020). A localização do evento é um campo distinto do local da editora.

As nove entradas originalmente citadas como preprints foram preservadas. A página de Komisarenko e Kull (2024) indica o DOI de uma publicação posterior (`10.3233/FAIA240658`); Bagnara et al. (2019) indica `10.1007/s10601-021-09322-9`. Esses DOIs não substituíram os DOIs dos preprints. A mudança para a versão publicada exigiria conferir novamente as discussões e o ano usado no texto.

PerspectiveGap apresenta revisão v2 e Murray (2026) apresenta revisão v6. Os resultados numéricos eventualmente citados no corpo devem corresponder à versão de preprint efetivamente analisada. As páginas atuais foram consultadas para a identidade bibliográfica; esta revisão não mudou resultados empíricos da dissertação.

Algumas consultas diretas às páginas das editoras receberam páginas de desafio de acesso. Elas foram identificadas no JSON como conteúdo bloqueado, mesmo quando o servidor retornou HTTP 200; o conteúdo útil obtido pela ferramenta de pesquisa e os registros Crossref estão discriminados separadamente.

## Fontes primárias de campos complementares

- [Anais NeurIPS — Attention is all you need](https://proceedings.neurips.cc/paper_files/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html).
- [Conferência NIPS 2017 — local e número](https://nips.cc/Conferences/2017).
- [Springer — Lean 4](https://link.springer.com/chapter/10.1007/978-3-030-79876-5_37).
- [Springer — TACAS 2008](https://link.springer.com/book/10.1007/978-3-540-78800-3).
- [Springer — Bridle](https://link.springer.com/chapter/10.1007/978-3-642-76153-9_28).
- [Birkhäuser — Handbook, segunda edição](https://link.springer.com/book/10.1007/978-3-319-76526-6).
- [Springer — Experimentation in Software Engineering](https://link.springer.com/book/10.1007/978-3-642-29044-2).
- [BMJ — PRISMA 2020, volume 372](https://www.bmj.com/content/372/bmj.n71.long).
- [Stanford — currículo de Bradley Efron](https://cap.stanford.edu/profiles/viewCV?facultyId=6090&name=Bradley_Efron).

Os URLs das 41 consultas Crossref e das nove páginas arXiv constam individualmente do JSON.
