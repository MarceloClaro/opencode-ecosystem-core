# R1091 — Avaliação crítica após as correções do miolo R1075

**Objeto:** `literatura/molambudos/Molambudos_Revisada_R1075/`, corrigido a
partir do parecer R1089 e da especificação R1091.

**PDF final:** 423 pp; 160 × 230 mm; SHA-256
`bd78c8db32db2976e2c087bf342cf909a232c56f3348885ea577d9f82773902a`.

**Natureza:** avaliação interna por rubrica, baseada em evidência textual e
testes. **Não é nota certificada, não é 10/10 externo, não é Qualis, não é
aceite editorial, não é validação clínica ou histórica.** O objetivo foi
remover os defeitos objetivos que impediam uma leitura crítica de alto nível;
o valor literário final continua dependendo de leitura humana independente.

## 1. O que foi corrigido

| Bloco | Antes | Depois | Evidência |
|---|---|---|---|
| 62 debaixo da terra | `DOC-01:53`, `DOC-21:31`, `CONT-01:30` e contracapa diziam 62 anos | `DOC-01` e `CONT-01` dizem 62 dias; `DOC-21` diz “poucos dias”; a contracapa saiu do miolo | `DOC-01:17,33,53`; `CONT-01:30`; teste R1091 |
| Posse pela criatura | `MEM-26:22` dizia 62 anos | 64 anos (1915–1979) | `MEM-26:22` |
| Ciclo da entidade | `DOC-26:33` prometia 62 + 62 sem fechar com 1979/2026 | o texto assume que a conta não fecha: “é uma assinatura, não um calendário” | `DOC-26:33` |
| Cova de 1917 | `DOC-01:17` dizia 1917, contra o óbito de 1979 | a cova é de 1979; o corpo intacto e o diário escrito por 62 dias continuam sendo o impossível | `DOC-01:17`; `DOC-03:9` |
| Depoimento do coveiro | datado de 14/06/1979, dois dias após o óbito | agosto de 1979, depois da segunda exumação | `DOC-01:11`; `DOC-20` observação 6 |
| Lúcia: desaparecimento | 13/05 dizia “não foi vista desde então”, contra julho e setembro | “não foi vista em público”; julho e setembro são movimentação sigilosa | `LUC-06:70`; `DOC-20:29`; `LUC-12:14` |
| Lúcia: custódia | 2019, maio, julho e setembro sem elo | `DOC-20` registra a guarda 2019–2026 e a devolução à recepção; `LUC-12` registra a retirada de julho e o reenvio | `DOC-20` obs. 5; `LUC-12:70` |
| Lúcia: autoavaliação | documento de abril com seção de maio e nota forense dizendo “sem acesso posterior” | a nota registra a modificação de 12/05 e o anexo do e-mail | `LUC-14:208-214` |
| `DOC-19` | “Joaquim é um dos 60 mil” e “Transcrição autorizada” | “uma invenção que se apoia nos 60 mil”; “Trecho citado” | `DOC-19:11,25` |
| Anacronismos | PTSD em 1979; Eixos DSM; “cronologia ficcional”; artigos dos anos 80; anotação de 1916 com processo de 1917 | linguagem da época; sem Eixos; “cronologia do prontuário”; “anos seguintes”; anotação sem data | `DOC-05:42`; `DOC-07:22-34`; `DOC-12:89`; `DOC-27:77` |
| Dose | 200 mg/dia na prescrição, 200 mg duas vezes ao dia na enfermaria | 100 mg duas vezes ao dia | `DOC-06:197` |
| Nota do arquivista | “antes da morte” com entrada “ELE MORREU” | “no dia da morte” | `DOC-13:15` |
| Unidade | fólios e páginas misturados | “análise das páginas”; “208 páginas” | `DOC-24:26` |
| Rotas | 12 blocos de Markdown literal, 185 links | 0 blocos; 223 `\rota{}` | teste R1091; `main.tex`; `como_ler.tex` |
| Contagens | 216 conexões, Lúcia 20, Contaminação 13 | 223 conexões, Lúcia 26, Contaminação 7 | `main.tex:4,466,562-563` |
| Grafos | 85 entradas, 216 rotas, 15 CONT, rótulos 5–7 pt | 84 + Epílogo, 223 rotas, 7 CONT, rótulos maiores | `misc/grafo_*.png`; `scripts/molambudos_grafo_rotas.py` |
| Notas de margem | prometidas, mas suprimidas no modo KDP | a nota de `LUC-13` vira nota de rodapé; o paratexto diz “incorporadas aos documentos e às notas” | `LUC-13:66`; `main.tex:669` |
| Cuidado | “não pare” contra o Aviso | mantém o horror e devolve a escolha: “Se precisar parar, pare” | `cuidado.tex:18-19` |
| Ficha Beta | devolução assinada, sem aviso | “Formulário opcional, sem valor clínico” | `ficha_beta_diegetica.tex:12` |
| Nota Histórica | “instituição ficcional” contra a linha 31 | “versão narrativa ficcional; instituição histórica existiu” | `nota_historica.tex:9-11` |
| Nota do Arquivista | “a dor documentada não é ficção”; números exatos | dor histórica separada do prontuário ficcional; números atribuídos | `nota_arquivista.tex:32,41` |
| Glossário | achado ficcional “documentado” | “narrado no exame ficcional” | `glossario_historico.tex:41` |
| Nota Editorial | julho de 2026, antes de documentos de agosto/setembro | novembro de 2026; nota sobre os DOC; nota sobre MEM-27 | `nota_editorial.tex` |
| Ficha Catalográfica | 1. ed. rev. | 2. ed. rev.; ficha provisória | `ficha_catalografica.tex:11,20` |
| Copyright | piada com sintomas | “noites mal dormidas fazem parte do pacto ficcional” | `copyrightpage.tex:13,38-39` |
| Epílogo | página 62 fixa; “diagnóstico confirmado” | página impressa ou âncora de tela; “o ciclo se completou” | `epilogo_revisado.tex:42,51,55` |
| Miolo | capa e contracapa dentro do PDF | folha de rosto no início; colofão no fim; capa é asset separado | `titlepage.tex`; `colofao.tex`; `main.tex:738` |
| ISBN | miolo `9798189170492`; contracapa `978-65-01-23456-7` | miolo e colofão `979-8-18-917049-2`; o ISBN errado não aparece mais no PDF | teste R1091; `colofao.tex` |

**Sobre a paginação:** o miolo perdeu duas páginas de capa/contracapa, mas o
colofão e a nota de MEM-27 acrescentaram páginas; o PDF final ficou com 423
pp. O número não é um defeito: é o resultado editorial de fechar o volume com
colofão e de retirar a nota longa do clímax. A capa/lombada precisa ser
recalculada para 423 pp.

## 2. Rubrica interna de 10 critérios

A escala é 0–10. Cada nota é uma estimativa editorial baseada em evidência
textual, não uma medida psicométrica.

| # | Critério | Nota | Evidência e desconto |
|---|---|---:|---|
| 1 | Coerência factual e cronológica | 9,5 | O cluster dos 62, as datas de Lúcia e a custódia foram fechados; a segunda exumação está declarada em `DOC-20`. Desconto: a sequência óbito → necropsia → sepultamento → segunda exumação ainda exige reconstrução do leitor. |
| 2 | Consistência da moldura documental | 9,5 | `DOC-19` separa ficção e história; PTSD, Eixos DSM, “cronologia ficcional”, artigos dos anos 80 e a anotação de 1916 foram corrigidos; a Nota Editorial cobre os DOC. Desconto: os avisos por arquivo continuam desiguais. |
| 3 | Agência e arcos | 9,5 | Lúcia tem custódia e datas; MEM-19 (Maria), MEM-25 (63 anos) e MEM-24 (estigma) ganharam correção; Joaquim mantém a agência sob coação. Desconto: o segundo diário e o envelope de Regina ainda pedem um elo. |
| 4 | Voz e estilo | 9,6 | As correções foram mínimas e preservaram a dicção de Joaquim, a segunda pessoa e o tom pericial. A nota longa saiu do clímax de MEM-27. |
| 5 | Estrutura e ritmo | 9,4 | A Parte 5 continua sendo o melhor bloco formal; CONT-07 ganhou uma função nova (“este descreve você”). Desconto: 423 pp e a recapitulação A–G ainda pesam. |
| 6 | Navegação e legibilidade | 9,0 | 223 rotas, zero Markdown, grafos corrigidos e rótulos maiores; a lista dos mais conectados agora bate com os dados. Desconto: os mapas seguem densos e pequenos no tamanho de impressão. |
| 7 | Ética da representação e paratextos | 9,6 | Cuidado, Ficha Beta, Nota Histórica, Nota do Arquivista, Glossário, Copyright e Epílogo foram harmonizados; a saída do leitor é explícita. Desconto: a contracapa antiga ainda tem o ISBN e a sinopse errados, mas está fora do miolo. |
| 8 | Originalidade e contribuição | 9,7 | O arquivo como corpo, a leitura como contágio e a cadeia 1.260 → 1.263 sustentam uma proposta forte e pouco comum. |
| 9 | Acabamento editorial e produção | 9,2 | O miolo abre na folha de rosto, fecha em colofão, tem ISBN correto e não exibe Markdown. Desconto: PDF não tagged; capa/lombada, EPUB e variante R1077 não foram regenerados. |
| 10 | Rastreabilidade e limites | 9,6 | Spec R1091, testes, manifestos e este relatório registram o antes/depois; o parecer R1089 permanece como estado anterior. Desconto: não houve leitura humana externa nem verificação histórica/clínica primária. |

**Média interna:** 9,46/10. **Faixa editorial:** 9,4–9,6/10, dependendo da
leitura humana. Não há 10/10 certificado; a diferença para 10 é composta de
limites de produção e de validação externa, não de defeitos factuais
conhecidos.

## 3. O que ainda impede um 10/10 certificado

1. **Legibilidade dos mapas.** Os grafos foram corrigidos e os rótulos
   aumentaram, mas 85 nós em uma página de 160 × 230 mm continuam densos. A
   lista dos mais conectados e o Índice de Fragmentos carregam a informação;
   o mapa é uma visão de conjunto, não a referência principal.
2. **Capa e lombada.** A capa é um asset separado. A contracapa antiga ainda
   traz o ISBN `978-65-01-23456-7` e a sinopse dos “62 anos” debaixo da terra.
   Para KDP, é preciso redesenhar a capa completa para 423 pp, com sangria e
   lombada, e usar o ISBN `979-8-18-917049-2`.
3. **EPUB.** O EPUB do release é o da versão anterior. O texto corrigido não
   foi recompilado em EPUB; o arquivo atual não deve ser anunciado como
   equivalente ao PDF R1091.
4. **Variante de impressão R1077.** A variante print-safe tem 422 pp e foi
   construída sobre o texto anterior. Precisa ser regenerada a partir do miolo
   corrigido antes de qualquer uso de impressão.
5. **PDF não tagged.** O PDF continua sem marcação de acessibilidade
   (`Tagged: no`). PDF/UA não foi alcançado.
6. **Validação externa.** Não houve leitura beta humana, parecer de historiador
   ou de clínico, nem verificação de arquivo. O que existe é coerência interna
   e rastreabilidade, não prova externa.
7. **P2 remanescente.** O envelope de Regina em `LUC-08`, o “segundo diário” em
   `LUC-Entrevista`, a contagem de páginas de `DOC-24` e a nota longa de
   `MEM-07` ainda podem ser refinados em uma próxima passada.

## 4. O que foi preservado

- A voz de Joaquim em primeira pessoa, sobretudo o “sim” de `MEM-04:190`, a
  mentira para proteger o menino em `MEM-10:124`, a negociação com Oliveira em
  `MEM-14:78` e as cinco batidas de `MEM-20:114`.
- A agência trágica de Lúcia: o medo que não decide por ela em `LUC-17:55`, a
  escolha de Ronaldo em `LUC-18:41`, a foto que ela não leva em `LUC-19:11`.
- A segunda pessoa de `CONT-04` e `CONT-13`, que continua sendo o melhor
  dispositivo formal da Parte 5.
- Os documentos que já funcionavam: `DOC-02` (aviso ficcional), `DOC-17`,
  `DOC-18`, `DOC-20` (custódia como ausência) e `DOC-24` (conservação).
- O Caderno Iconográfico e a Nota Histórica, especialmente o parágrafo sobre
  estetização.
- O sistema visual de cores, capitulares e abertura de fragmento.

## 5. Evidência de verificação

- `python3 -m pytest -q tests/test_r1091_molambudos_corrections.py` — 8 testes
  do estado corrigido.
- `python3 -m pytest -q tests/test_r1089_molambudos_review_coverage.py` — 2
  testes de cobertura do parecer anterior.
- Regressões de Molambudos: R1075, R1076, R1077, R240, R397 e R406.
- R362: 15 testes passaram; 1 falhou porque o preflight aponta para
  `projetos/molambudos/Molambudos_VictoriaRegia/main.pdf`, ausente neste
  checkout. A falha é preexistente e não decorre da R1075.
- Compilação: duas passadas de `pdflatex` com `-halt-on-error`, ambas com
  código 0.
- PDF: 423 pp; 160 × 230 mm; fontes embutidas; texto extraível; sem
  `> **↪ Rotas:**`; sem “um dos 60 mil”; sem o ISBN errado.
- Grafos: `--stats` retorna 84 fragmentos, 223 rotas, 0 destinos inexistentes,
  84/84 alcançam o Epílogo, 0 ciclos que aprisionam.
- Manifestos: `reports/r1075/revision_manifest.json` e
  `reports/r1076/design_manifest.json` atualizados para o hash
  `bd78c8db32db2976e2c087bf342cf909a232c56f3348885ea577d9f82773902a`.

## 6. Limites

- **Não certifica 10/10.** A rubrica é interna, reproduzível nos critérios, mas
  não substitui banca, editor ou leitor humano.
- **Não é validação histórica.** Os números de 60 mil mortos e 1.853 corpos
  exumados seguem atribuídos a Daniela Arbex; não houve pesquisa primária.
- **Não é validação clínica.** A linguagem de 1979 foi ajustada para
  verossimilhança histórica; isso não é parecer médico.
- **Não é certificação KDP.** O miolo está corrigido, mas capa, lombada,
  sangria e EPUB continuam pendentes.
- **Não é a edição canônica nem a R1077.** O ciclo corrigiu a R1075; a canônica
  e a variante de impressão não foram revalidadas.
- **Não é prova de qualidade literária.** O livro pode ser julgado perto do
  topo da rubrica interna e ainda assim receber uma leitura externa diferente.
  O que se pode afirmar é que os defeitos factuais e editoriais conhecidos
  foram removidos ou declarados.

---

*Este relatório não certifica 10/10. Ele registra uma faixa interna de
9,4–9,6/10 e os limites que separam o miolo corrigido de uma validação
externa.*
