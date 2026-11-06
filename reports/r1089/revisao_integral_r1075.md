# R1089 — Revisão integral do miolo Molambudos R1075

**Objeto:** `literatura/molambudos/Molambudos_Revisada_R1075/`, na branch
`codex/core-prontidao-rea`, lido a partir de `main_kdp_pt_160x230mm.tex` →
`main.tex`. Revisão editorial e técnica **somente leitura**: nenhum `.tex`,
imagem, PDF ou EPUB desta edição foi alterado.

**Data:** 6 de novembro de 2026.

> **Nota de estado:** este parecer descreve a R1075 **antes** das correções
> R1091. Os localizadores referem-se a esse estado; o estado corrigido está em
> `reports/r1091/avaliacao_critica_pos_correcao.md`.

**Natureza:** parecer crítico de manuscrito. Não é publicação, nova ISBN,
validação clínica, validação histórica, certificação KDP, prêmio ou garantia de
aceite editorial. Não há nota numérica.

## 1. Identificação e extensão real

| Item | Valor observado |
|---|---|
| `main.tex` | SHA-256 `235f7f38e80227c5703cd3367a5cc8fcda6c217043e4c05d9f773f0bb6bdbb68` |
| `main_kdp_pt_160x230mm.tex` | SHA-256 `a4f17ec585fd2aba83df49dd129b9c1c51498b29964ab1f583a845d74f211741` |
| PDF de impressão | 421 pp; 160 × 230 mm; SHA-256 `cc0c5c2110f0a334a9650044191dabaf5da168a701dc194604069c16444991ab` |
| Fragmentos incluídos | **84**: 27 MEM, 27 DOC, 23 LUC, 7 CONT |
| Paratextos chamados por `main.tex` | **16** |
| Epílogo | `fragmentos/epilogo_revisado.tex` |
| CONT arquivados | 6 arquivos em `fragmentos/cont/_removidos/` |
| Apêndice não incluído | `apendice/aparato_de_leitura.tex` |

O hash do PDF confere com `release/SHA256SUMS.txt`. O EPUB declarado no
`release/README.md` tem SHA-256 `0269e8c0c1d26c1f66eb1c7773c732afa2332a58bd1ce5acf2c4fe6b2a4b9c4c`;
não foi revalidado nesta revisão.

A ordem efetiva foi extraída de `main.tex:593-716`: 9 fragmentos no Sertão, 16
na Colônia, 25 no Diário/Laudos, 26 na Investigação Lúcia e 8 na Contaminação
(7 CONT + MEM-27). O epílogo é uma entrada à parte (`EPI-01`), não um 85º
fragmento numerado.

## 2. Método e correções de percurso

A leitura integral foi distribuída em quatro blocos — Sertão/Colônia,
Diário/Laudos, arco de Lúcia e Contaminação/paratextos — e cada achado foi
conferido pelo primário no `.tex` indicado. Três verificações materiais
complementares foram feitas: extração de texto do PDF, rasterização de páginas
escolhidas e OCR das capas.

A conferência **descartou** várias hipóteses dos leitores que não se sustentam
na fonte. Entre elas:

- `MEM-11:14` não contradiz `DOC-02:45`: o “segundo homicídio” é o de junho de
  1922; o de março de 1937 é o terceiro. A mudança para a ala dos silenciados
  em 1923 é compatível.
- `MEM-07:84` não revive Anselmo por erro: a frase diz explicitamente que ele
  “não tinha morrido ainda naquela época”. É uma ressalva retrospectiva.
- `LUC-19:11` não fixa a morte do pai doze anos depois da foto; `LUC-16:83`
  diz que ele morreu doze anos antes de 2026. As duas âncoras são compatíveis.
- `LUC-13:17` não promete transcrever só 4min12s; a nota descreve uma gravação
  de 47min32s com um corte de 23 segundos e restauração parcial, o que o texto
  explica em `LUC-13:38`.
- `DOC-24:26` não opõe “190 páginas” a “208 fólios”; o parecer fala em
  “análise de fólios”, “quantidade de páginas” e “18 páginas a mais”. O
  problema é de unidade, não de números inventados.
- `DOC-25:21` e `DOC-26:37` não são a mesma data: 5 de janeiro é a entrega à
  recepção; 12 de janeiro é a chegada da carta a Oliveira.

Essas correções importam: um parecer que repetisse as seis hipóteses acima
produziria erros novos. O que segue é o que sobreviveu à conferência.

**Limite de método:** o primário não leu palavra por palavra os 84 arquivos
sozinho; a leitura integral foi distribuída e cada linha citada foi conferida
na fonte. A cobertura é a soma das quatro leituras com verificação local, não
uma segunda leitura integral independente.

## 3. Veredito em uma página

A R1075 é uma edição ambiciosa e, em vários pontos, superior à canônica em
ritmo e legibilidade. A voz de Joaquim está mais controlada; o arco de Lúcia
ganhou corpo; os documentos de custódia e conservação são os melhores do
aparato; o Caderno Iconográfico declara com clareza que suas imagens são
reconstituições ficcionais. O livro tem uma tese formal forte: a leitura como
contágio, o arquivo como corpo, a memória como resistência.

O problema central não é a prosa. É a **colisão entre três camadas que o livro
quer manter simultaneamente**: o motivo numérico dos 62, a moldura documental
verossímil e o aparato de navegação. Quando as três se encontram, o texto ora
produz ambiguidade produtiva, ora produz contradição factual. A revisão
separa esses dois casos.

Os seis achados transversais prioritários são:

1. **O número 62 é usado para intervalos incompatíveis.** O livro diz 62 anos
   de internação (correto), 62 dias de sepultamento (correto), 62 anos de
   diário (correto) e, em quatro passagens do miolo e na contracapa, 62 anos
   debaixo da terra (incorreto). A posse pela criatura começa em 1915 e termina
   em 1979: são 64 anos, não 62.
2. **O desaparecimento de Lúcia tem três datas.** 13/05 (`LUC-06:70`), 28/07
   (`DOC-20:29`) e setembro (`DOC-25:64`, `LUC-12:14`). O texto não diz qual é
   a data pública e quais são aparições secretas.
3. **A moldura documental é aplicada de modo desigual.** Alguns DOC declaram
   “reconstituição ficcional” (`DOC-02:11`, `DOC-17:10`, `DOC-18:10`); outros,
   não. Há anacronismos clínicos em `DOC-05:42` e `DOC-07:28`, um vazamento da
   palavra “ficcional” para dentro de um laudo de 1979 e uma passagem que
   insere Joaquim entre os 60 mil mortos (`DOC-19:25`), contra a própria nota
   que a antecede.
4. **O aparato de navegação está desatualizado.** Os três grafos foram gerados
   para uma versão com 85 entradas, 216 rotas e 15 fragmentos de Contaminação;
   o livro tem 84 + epílogo, 185 links `\rota` e 7 CONT. Doze fragmentos
   exibem a rota como Markdown literal, não como link.
5. **Os paratextos éticos se contradizem.** O Aviso garante que o leitor pode
   parar; a página Cuidado manda “não pare”; o epílogo afirma um “diagnóstico
   confirmado” pelo cheiro; a Ficha Beta pede devolução assinada. A intenção
   pode ser deliberada, mas a soma não deixa claro o que é ficção e o que é
   instrução real.
6. **A produção KDP ainda não está fechada.** O PDF de 421 pp inclui capa e
   contracapa como páginas 1 e 421; a contracapa exibe ISBN
   `978-65-01-23456-7`, diferente do ISBN do miolo `9798189170492` e com
   dígito verificador inválido. Para upload como miolo, capa e contracapa
   precisam sair; para capa, falta uma lombada com sangria.

## 4. Achados transversais

### 4.1 O motivo dos 62

| Intervalo | Datas | Duração real | Onde o texto afirma | Situação |
|---|---:|---:|---|---|
| Internação | 1917–1979 | 62 anos | `nota_arquivista.tex:23`, `DOC-03:46`, `DOC-04:24`, `DOC-07:42` | Correto |
| Diário | 1917–1979 | 62 anos | `LUC-06:24`, `LUC-14:222`, `DOC-10:61` | Correto |
| Sepultamento | 12/06/1979 + 62 dias | 62 dias | `MEM-16:122`, `nota_arquivista.tex:23` | Correto |
| Posse pela criatura | 1915–1979 | 64 anos | `MEM-26:22` diz 62 | Desvio de 2 anos |
| “Debaixo da terra” | 12/06/1979 + 62 dias | 62 dias | `DOC-01:33`, `DOC-01:53`, `DOC-21:31`, `CONT-01:30`, contracapa dizem 62 anos | Contradição |
| Ciclo da entidade | 1853–1915–1977 | 62 + 62 alegados | `DOC-26:33` | Não fecha com 1979/2026 |

O epílogo assume o motivo: “62 anos, 62 dias, 62 segundos”
(`fragmentos/epilogo_revisado.tex:44`). Isso poderia transformar a
inconsistência em deliberação. O problema é que a mesma confusão aparece em
documentos que o livro apresenta como registro, não como delírio: o depoimento
do coveiro (`DOC-01`), a carta de Oliveira (`DOC-21`), o protocolo de
contaminação (`CONT-01`) e a contracapa. Se a intenção é que o 62 contamine
todas as camadas, o texto precisa dar ao leitor uma pista de que a contaminação
atinge também os documentos; se não, as quatro passagens estão erradas.

**Ação:** escolher uma das duas soluções e aplicá-la em todo o livro. (a) O
coveiro mente ou lê o mapa errado: a cova é de 1979, e o “62 anos” é delírio
dele. (b) A criatura reescreve os documentos: o “62 anos” é assinatura dela, e
o texto deve marcar a intervenção. A opção (a) é mais simples e preserva a
força de `MEM-16:122`.

### 4.2 O desaparecimento de Lúcia

| Data | Fonte | O que afirma |
|---|---|---|
| 13/05/2026 | `LUC-06:70` | “Dra. Lúcia Mendes não foi vista desde então” |
| 28/07/2026 | `DOC-20:29` | Lúcia retira o objeto do APM e o leva ao cofre |
| 03/09/2026 | `LUC-12:14` | última foto na rodoviária de Barbacena |
| setembro/2026 | `DOC-25:64` | “sete meses depois” de 4 de fevereiro, ela desapareceu |

Além disso, `LUC-12:70` diz que Lúcia enviou o diário de volta “antes de pegar
o ônibus”, enquanto `LUC-06:68` diz que o diário foi encontrado na recepção do
APM em 13 de maio. `LUC-20:55` acrescenta que o diário voltou em 2019. Há, na
prática, quatro elos de custódia sem data única: 2019 (Ronaldo), 13/05 (APM),
28/07 (cofre) e setembro (reenvio). O leitor não consegue dizer se Lúcia
desapareceu em maio e continuou agindo em segredo, ou se o registro de maio é
falso.

**Ação:** criar uma tabela de custódia explícita, como a de `DOC-20`, com
colunas “data, evento, fonte, quem sabia”. Datas diferentes podem ser
mantidas, mas cada uma precisa de uma fonte e de um estado de conhecimento.
A frase “não foi vista desde então” deve virar “não foi vista publicamente” ou
equivalente.

### 4.3 A moldura documental

O livro alterna três regimes:

1. **Documento com aviso explícito:** `DOC-02:11-12`, `DOC-17:10-11`,
   `DOC-18:10-15`, `DOC-19:19` (nota). Funciona.
2. **Documento sem aviso:** `DOC-01`, `DOC-03`, `DOC-04`, `DOC-05`, `DOC-06`,
   `DOC-07`, `DOC-10`, `DOC-20` a `DOC-26`. O leitor não sabe se está diante
   de reconstituição ficcional ou de citação de arquivo.
3. **Documento que se declara real:** `DOC-19:10-11` diz “Trecho do livro
   Holocausto Brasileiro — Daniela Arbex (2013)” e “Transcrição autorizada
   para fins de contexto histórico”. Se não houve autorização editorial, a
   frase é uma alegação falsa; se houve, falta o crédito de permissão.

O caso mais grave é `DOC-19:25`: “O paciente 1.260, Joaquim Antônio Correia, é
um dos 60 mil.” A nota imediatamente anterior (`DOC-19:19`) acabou de dizer
que Joaquim é ficcional e que os 60 mil são históricos. O parágrafo seguinte
desfaz a distinção. É o oposto do que a Nota Histórica promete.

Anacronismos clínicos verificados:

- `DOC-05:42` usa “Transtorno de Estresse Pós-Traumático” em um relatório de
  1979. O PTSD entra no DSM-III em 1980 e na CID-10 em 1992. A linguagem é
  posterior ao documento.
- `DOC-07:22-34` organiza o caso em Eixos I–V, estrutura do DSM-III/IV. Em
  1979, o sistema ainda não estava consolidado no Brasil.
- `DOC-07:28` diz “compatível com a cronologia ficcional”. A palavra
  “ficcional” vaza para dentro de um laudo diegético e quebra a quarta parede
  sem sinalização.
- `DOC-04:32` usa CID-8 295.3. A CID-8 é de 1965; a CID-9 é de 1975. Vale
  confirmar qual versão estava em uso no hospital em 1979.
- `DOC-12:89` é um caderno datado de 20/04/1979 que cita “três artigos
  acadêmicos nos anos 80”. O autor não podia conhecer artigos futuros.
- `DOC-27:77` é uma anotação de 1916 que já cita o “Processo 1.260”, anterior
  à admissão de 1917. Se for a criatura escrevendo fora do tempo, falta o
  sinal; se for erro, a data precisa mudar.

**Ação:** padronizar um cabeçalho ficcional por família DOC, em vez de depender
de avisos arquivo por arquivo. Corrigir os anacronismos clínicos e remover
“cronologia ficcional” do laudo. Resolver `DOC-19` com uma paráfrase creditada
ou com a autorização documentada.

### 4.4 O aparato de navegação

Contagens observadas:

- 84 fragmentos incluídos.
- 185 ocorrências de `\rota{...}` em 72 arquivos; todas viram link.
- 38 alvos de rota em 12 arquivos escritos como Markdown literal
  (`> **↪ Rotas:** ...`), sem `\rota`; não viram link e aparecem como texto
  cru no PDF.
- Total de rotas pretendidas: **223**.
- O livro afirma **216** conexões (`main.tex:4`, `main.tex:466`) e **185**
  rotas (`como_ler.tex:12`). Nenhum dos dois números corresponde ao total
  pretendido.
- O grafo de rotas diz “85 fragmentos, 216 rotas”; o grafo do enredo diz “85
  entradas · 55 rotas atravessam atos”; o grafo linear diz “84 fragmentos +
  Epílogo” e traz “Contaminação (15)”, incluindo CONT-02, CONT-06, CONT-08,
  CONT-10, CONT-11 e CONT-12, que estão em `_removidos` e não integram o miolo.
- `main.tex:562-563` diz “Investigação Lúcia (20)” e “Contaminação (13)”;
  o livro tem 26 LUC e 7 CONT.

Os 12 arquivos com Markdown literal são: `DOC-03`, `DOC-08`, `DOC-26`,
`DOC-27`, `LUC-15`, `LUC-16`, `LUC-17`, `LUC-18`, `LUC-19`, `LUC-20`,
`CONT-07` e `CONT-13`. No PDF, a linha aparece como
`> **↪ Rotas:** **...**` em pelo menos doze páginas. É um defeito visível de
composição, não uma escolha estética.

Os grafos são, além disso, pouco legíveis no tamanho de impressão: a imagem
tem 4400 px de largura e é reduzida a cerca de 0,9 da altura do texto,
rotacionada 90°. Os rótulos dos nós ficam abaixo do limiar de leitura
confortável e não são decifráveis na prévia de 160 × 230 mm. O Mapa 1 promete
“216 conexões” e uma legenda de cores; o que se vê é uma teia densa com rótulos
microscópicos.

As notas de margem prometidas em `main.tex:669` (“As anotações dela estão em
itálico nas margens dos documentos originais”) não existem no PDF de imprensa:
há **uma** chamada de `\margnota` em `LUC-13:66`, e `main.tex:209-216` a
suprime quando `\molambudoskdpprint` está ativo. O modo KDP troca a nota por
vazio para evitar texto fora da margem. A promessa paratextual, portanto, não
se cumpre na edição que o leitor recebe.

**Ação:** substituir os 12 blocos Markdown por `\rota{}`; regerar os três
grafos a partir da lista real de 84 fragmentos; corrigir as contagens para
223 (ou para o número que se decidir contar); trocar “20/13” por “26/7”;
simplificar os grafos para que sejam legíveis ou substituí-los por uma tabela
de rotas; e restaurar as notas de margem dentro da área segura ou reescrever a
nota do arquivista.

### 4.5 Os paratextos éticos

O Aviso ao Leitor (`aviso_ao_leitor.tex:27-43`) é o texto mais cuidadoso do
aparato: separa ficção de realidade, nomeia o CVV e os CAPS, e garante que o
leitor pode interromper. A página Cuidado (`cuidado.tex:18-19`) diz o
contrário: “Se um zumbido surgir durante a leitura, não pare. Já é tarde demais
para parar.” A contradição pode ser um dispositivo de horror, mas ela está em
dois paratextos de segurança, não dentro da ficção. O leitor não tem como saber
qual instrução vale.

O epílogo agrava: manda abrir na página 62, passar a mão na página 126 e diz
que, se o cheiro estiver mais forte, “o diagnóstico está confirmado”
(`epilogo_revisado.tex:42-55`). Isso contradiz o Aviso, que diz que o livro não
diagnostica o leitor. Em formato EPUB, as páginas 62 e 126 nem sequer são
estáveis.

A Ficha Beta (`ficha_beta_diegetica.tex:12`) pede “Devolver devidamente
assinado ao Arquivista” e lista sintomas. Não há endereço, e a ficha vem
depois da Nota Histórica, que deveria ser o fecho ético. Um leitor vulnerável
pode lê-la como instrumento clínico real. A intenção diegética é clara para
quem conhece o gênero, mas o texto não diz “opcional” nem “não é instrumento
clínico”.

A Nota do Arquivista (`nota_arquivista.tex:32`) diz que “a dor documentada
nestas páginas não é ficção”. A Nota Histórica (`nota_historica.tex:9-11`) diz
que Joaquim e a criatura não existiram e que “a instituição narrada como o
Colônia é ficcional” — uma frase que contradiz a linha 31 do mesmo arquivo,
onde o Hospital Colônia de Barbacena “existiu de verdade”. O glossário
(`glossario_historico.tex:41`) chama a icterícia unilateral de “achado pericial
anômalo documentado no exame de Joaquim”, tratando um personagem ficcional como
caso documentado.

**Ação:** manter o horror, mas separar com clareza o que é instrução ficcional
do que é orientação real. Uma linha no Cuidado (“esta página é parte da ficção;
se você precisar parar, pare”) resolve a contradição sem perder o efeito. A
Ficha Beta deve dizer “opcional, sem valor clínico, não enviar a ninguém”. A
Nota Histórica deve corrigir a frase sobre a instituição e qualificar os
números.

### 4.6 Produção e KDP

O PDF tem 421 páginas, todas em 453,543 × 651,968 pt (160 × 230 mm), com fontes
EB Garamond, SFTT1440 e famílias matemáticas embutidas. O texto é extraível. Há
306 links e 16 entradas de marcador (apenas partes e seções maiores). O PDF não
é marcado (`Tagged: no`), o que limita acessibilidade, mas não impede a
impressão.

Problemas materiais:

- **Capa e contracapa dentro do miolo.** A página 1 é a capa e a página 421 é a
  contracapa. Se esse PDF for enviado como miolo KDP, a Amazon imprimirá uma
  capa dentro do livro. O miolo deve começar na folha de rosto; a capa precisa
  de um arquivo separado, com lombada e sangria.
- **ISBN divergente.** O miolo usa `9798189170492` (`main.tex:29`), que tem
  dígito verificador válido. A contracapa exibe `978-65-01-23456-7`, que tem
  dígito verificador inválido (soma 113, resto 3) e não corresponde ao miolo.
- **Ficha catalográfica.** Diz “1. ed. rev.” (`ficha_catalografica.tex:20`),
  enquanto `book.json` diz `"edition": "2 (revista)"`. A CIP não indica a
  agência catalogadora; é uma ficha provisória, não uma CIP validada.
- **Sangria.** As páginas de capa/contracapa são imagens de página inteira, mas
  o PDF não tem BleedBox maior que o TrimBox. Para capa KDP, falta sangria de
  3 mm.
- **Grafos rotacionados.** As páginas 31, 34 e 37 exigem girar o livro; a
  legenda e o texto explicativo ficam em páginas separadas. É usável, mas
  desconfortável.
- **Sobreposição de texto.** O log registra um `Overfull \hbox` de 0,32 pt em
  `DOC-01:61-62`, invisível na impressão. Os muitos `Underfull \vbox` vêm de
  aberturas de parte e páginas em branco; não geram defeito visível.

O `release/README.md` declara EPUBCheck 5.4.0 com 0 erros/0 avisos e Ace 1.4.6
com 26 pass/0 fail. Não reexecutei essas ferramentas; o parecer não as
certifica.

## 5. Matriz dos 84 fragmentos

A matriz segue a ordem de `main.tex`. Cada linha traz uma leitura crítica ou
uma decisão de manutenção, com um localizador conferido. “Manter” significa que
o fragmento cumpre sua função e não exige intervenção obrigatória; “rever”,
“corrigir”, “esclarecer” ou “verificar” indicam ação editorial.

| ID | Leitura crítica ou decisão | Localizador |
|---|---|---|
| MEM-01 | Manter: o olhar para trás inaugura a curiosidade de Joaquim e prepara o incêndio e a vala; é a primeira ruptura com a obediência do pai. | fragmentos/mem/MEM-01.tex:34 |
| MEM-02 | Rever: a parada do pai no juazeiro já encena a despedida que MEM-03 retoma; condensar a repetição ou diferenciar o que cada cena acrescenta. | fragmentos/mem/MEM-02.tex:60 |
| MEM-03 | Manter: a ordem de comer o que não parece comida prepara o pacto; Joaquim deixa o pai vivo ao olhar para trás, o que preserva a culpa não resolvida. | fragmentos/mem/MEM-03.tex:64 |
| MEM-04 | Manter: o “sim” de uma criança faminta é agência sob coação, não consentimento livre; a cena sustenta o pacto sem absolver a criatura. | fragmentos/mem/MEM-04.tex:190 |
| MEM-05 | Manter: o salto para os 72 anos e a assinatura “Último registro” antecipam 1979; a datação da camada de escrita deve ficar implícita, não explicada. | fragmentos/mem/MEM-05.tex:174 |
| MEM-06 | Rever: “as mortes começaram na segunda semana” não acomoda a morte de Anselmo no segundo dia; distinguir a mortandade coletiva do caso individual. | fragmentos/mem/MEM-06.tex:46 |
| MEM-07 | Manter: a partida de Maria é o núcleo afetivo do bloco; a ressalva sobre Anselmo em 84 deve ser conferida para não soar como remendo cronológico. | fragmentos/mem/MEM-07.tex:80 |
| DOC-17 | Manter: a carta do soldado é um testemunho limitado, não uma prova; o menino chegou com a mãe e negou o “bicho”, e essa discrepância deve ser lida como desconhecimento, não erro. | fragmentos/doc/DOC-17.tex:31 |
| DOC-18 | Manter: a reconstituição declara o referente histórico e os limites ficcionais; a voz moralizante do relator é o único ponto a moderar para não competir com o aparato administrativo. | fragmentos/doc/DOC-18.tex:22 |
| MEM-08 | Manter: a lacuna de memória sobre a chegada contrasta com a precisão burocrática de DOC-02; o “mais de cinco mil” em 88 deve ser marcado como saber posterior, não percepção infantil. | fragmentos/mem/MEM-08.tex:14 |
| DOC-02 | Manter: a ficha declara-se reconstituição ficcional e ancora 1907, 1915 e 1917; separar, porém, o exame de admissão dos adendos de 1979 e da custódia pós-necropsia. | fragmentos/doc/DOC-02.tex:11 |
| MEM-09 | Rever: “eu não falava” soa absoluto diante das falas na admissão e em 1922; “quase não falava” ou “não falava com os médicos” preserva a defesa pelo silêncio. | fragmentos/mem/MEM-09.tex:14 |
| MEM-10 | Manter: ao mentir para proteger o menino, Joaquim contraria a criatura e recupera agência; é o contraponto ético ao “sim” de MEM-04. | fragmentos/mem/MEM-10.tex:124 |
| MEM-11 | Manter: a mudança para a ala dos silenciados em 1923 é compatível com o segundo homicídio de 1922 em DOC-02; a contagem de três homicídios precisa permanecer estável. | fragmentos/mem/MEM-11.tex:14 |
| MEM-17 | Manter: as 37 sessões entre 1937 e 1952 são compatíveis com DOC-10; a frase “eu não era refratário” em 117 deve permanecer como experiência subjetiva, não laudo. | fragmentos/mem/MEM-17.tex:79 |
| MEM-18 | Esclarecer: os “15 minutos” são de liberdade sentida, mas o resgate ocorre seis horas depois; explicitar a diferença entre tempo percebido e tempo cronológico. | fragmentos/mem/MEM-18.tex:54 |
| MEM-12 | Manter: a morte de Nonô dá consequência à coruja; reduzir os anúncios repetidos de que o diário precisa ser transmitido em 130 e 163 para não antecipar o desfecho. | fragmentos/mem/MEM-12.tex:89 |
| MEM-21 | Manter: “o jornal mentiu” é a crença de Joaquim, não uma garantia do narrador; a narrativa já mostra que a criatura também escreve o diário, e essa ironia deve ficar visível. | fragmentos/mem/MEM-21.tex:44 |
| MEM-19 | Corrigir ou marcar: o reencontro com Maria em 1950 contradiz “eu nunca mais vi minha mãe” em MEM-07; se for alucinação ou outra Maria, o texto precisa sinalizar antes da revelação. | fragmentos/mem/MEM-19.tex:50 |
| DOC-10 | Verificar: a nota de 2026 cita “Dr. Torres, 2023” e um parecer clínico sem marcar a fonte como ficcional; padronizar o aviso documental para que a citação não pareça bibliografia real. | fragmentos/doc/DOC-10.tex:69 |
| MEM-22 | Manter: o grito por José transforma os “gritos sem sentido” em perda nomeada; é um dos melhores exemplos de como o romance devolve humanidade às vítimas anônimas. | fragmentos/mem/MEM-22.tex:44 |
| MEM-23 | Verificar: o incêndio de 1960 na ala administrativa é narrado como fato; se for ficcional, a Nota Histórica deve dizê-lo, e a admissão da fome em 55 é o verdadeiro centro do fragmento. | fragmentos/mem/MEM-23.tex:14 |
| MEM-20 | Manter: as cinco batidas são uma vitória mínima e “nunca mais fiz amizade” impede que ela pareça definitiva; o fragmento sustenta a tese de que lembrar é uma forma de resistência. | fragmentos/mem/MEM-20.tex:114 |
| MEM-24 | Rever: “pessoas perigosas não escrevem, não pensam” pode ser lida como tese do livro, não como ingenuidade de Isabel; acrescentar uma correção dela ou uma réplica de Joaquim. | fragmentos/mem/MEM-24.tex:36 |
| MEM-25 | Esclarecer: em 1970 Joaquim tem 63 anos e está internado há 53; a pergunta “passei 63 anos aqui?” funciona como confusão, mas precisa de uma correção ou de uma pista de que é a idade, não o cárcere. | fragmentos/mem/MEM-25.tex:46 |
| DOC-01 | Corrigir: “Notas do coveiro Genésio Barbosa” aparece duas vezes em 8 e 10; além disso, a cova de 1917 e o “morto há 62 anos” em 53 contradizem o óbito de 12/06/1979 em DOC-03. | fragmentos/doc/DOC-01.tex:8 |
| DOC-03 | Manter: o laudo fixa óbito em 12/06/1979 e necropsia em 14/06/1979; esses dois marcos devem ser a âncora de toda a cronologia de sepultamento, exumação e custódia. | fragmentos/doc/DOC-03.tex:9 |
| DOC-04 | Verificar: o relatório de 1979 usa CID-8 295.3 e generaliza o discurso de pessoas institucionalizadas; confirmar a versão da CID vigente no Brasil e manter a generalização como perspectiva limitada de Oliveira. | fragmentos/doc/DOC-04.tex:32 |
| DOC-05 | Corrigir: “Transtorno de Estresse Pós-Traumático” em um relatório de 1979 é anacrônico; usar a linguagem disponível na época ou datar o documento como releitura posterior. | fragmentos/doc/DOC-05.tex:42 |
| DOC-06 | Corrigir: a prescrição em 125 indica 200mg/dia, mas a enfermeira informa 200mg duas vezes ao dia em 197; alinhar a dose ou transformar a divergência em erro percebido por Oliveira. | fragmentos/doc/DOC-06.tex:197 |
| DOC-07 | Corrigir: um laudo de 1979 não pode dizer “cronologia ficcional” nem organizar o caso em Eixos I-V do DSM; trocar por linguagem da época e reservar o meta-comentário para a nota editorial. | fragmentos/doc/DOC-07.tex:28 |
| MEM-13 | Manter: a fala sobre fome e remorso é a voz de Joaquim, não uma tese universal; ela explica sem absolver os homicídios e deve continuar ambígua. | fragmentos/mem/MEM-13.tex:80 |
| MEM-14 | Manter: ao exigir que Oliveira pergunte antes de ler, Joaquim recupera agência diante do prontuário; é uma das melhores cenas de negociação entre paciente e instituição. | fragmentos/mem/MEM-14.tex:78 |
| MEM-15 | Rever: a criatura diz que nasceu da vala e comeu os mortos; a imagem é forte, mas transforma vítimas anônimas em matéria monstruosa, e o texto precisa de um contraponto humano explícito. | fragmentos/mem/MEM-15.tex:60 |
| MEM-16 | Manter: “62 dias na terra, um dia para cada ano de prisão” é a formulação correta e deve ser a referência contra as passagens que dizem 62 anos debaixo da terra. | fragmentos/mem/MEM-16.tex:122 |
| MEM-26 | Esclarecer: a “última página” escrita três dias antes da morte não é necessariamente o último registro três dias antes da exumação; separar as duas peças e nomear a que o coveiro encontrou. | fragmentos/mem/MEM-26.tex:18 |
| DOC-11 | Rever: a frase “Você leu. Agora você é meu” repete DOC-06:167 quase literalmente; se a repetição for o mecanismo da criatura, sinalizá-la como ciclo, não como eco involuntário. | fragmentos/doc/DOC-11.tex:103 |
| DOC-12 | Corrigir: o caderno de 20/04/1979 não pode citar artigos dos anos 80; trocar por “nos anos seguintes” ou deslocar a entrada para uma camada posterior. | fragmentos/doc/DOC-12.tex:89 |
| DOC-13 | Corrigir: a nota do arquivista diz “antes da morte do paciente”, mas a entrada começa com “ELE MORREU” e “o paciente morreu hoje”; datar a nota como “no dia da morte”. | fragmentos/doc/DOC-13.tex:15 |
| DOC-14 | Verificar: Oliveira parte para o Ceará em 13/06 às 23h47, mas DOC-20 registra retirada do diário no IML em 16/06; falta um retorno ou uma explicação para a assinatura posterior. | fragmentos/doc/DOC-14.tex:52 |
| DOC-15 | Manter: “centenas, milhares” é fala de uma testemunha ficcional, não contagem aferida; a atribuição deve permanecer explícita para não virar estatística. | fragmentos/doc/DOC-15.tex:31 |
| DOC-16 | Esclarecer: a sequência da mãe coloca Verônica antes de Oliveira, mas DOC-12 situa o desaparecimento dela em 1985; delimitar o alcance temporal dessa voz espectral. | fragmentos/doc/DOC-16.tex:103 |
| DOC-19 | Corrigir: “Joaquim é um dos 60 mil” apaga a distinção que a nota em 19 acabou de estabelecer; dizer que ele é ficcional e que os 60 mil são históricos, sem colocá-lo na contagem. | fragmentos/doc/DOC-19.tex:25 |
| DOC-20 | Verificar: a entrada 3 registra retirada por Oliveira em 16/06, mas ele partiu em 13/06; a lacuna é interessante, mas precisa ser assumida como lacuna, não como prova de transferência sobrenatural. | fragmentos/doc/DOC-20.tex:26 |
| DOC-21 | Corrigir: a carta de junho de 1979 diz que o homem estava morto havia 62 anos, mas Joaquim morreu em 12/06/1979; o luto de Oliveira não justifica a data errada. | fragmentos/doc/DOC-21.tex:31 |
| DOC-22 | Verificar: o memorando diz que o objeto foi retirado do cofre em 02/08, mas DOC-23 o encontra em posição original em 03/08; falta registrar a devolução, a duplicata ou a substituição. | fragmentos/doc/DOC-22.tex:42 |
| DOC-23 | Manter a cena: o registro de 03/08 é eficaz como prova de que algo voltou; o problema é a ausência de nexo com a retirada de 02/08, que deve ser explicitada. | fragmentos/doc/DOC-23.tex:29 |
| DOC-24 | Verificar: o parecer compara a espessura do caderno com “quantidade de páginas” e depois fala em fólios; uniformizar a unidade antes de concluir que há 18 páginas extras. | fragmentos/doc/DOC-24.tex:26 |
| DOC-25 | Corrigir: “sete meses depois” de 4 de fevereiro situa o desaparecimento em setembro, mas LUC-06 diz 13/05; a identificação de Wellington e a última aparição precisam de uma cronologia única. | fragmentos/doc/DOC-25.tex:64 |
| DOC-26 | Esclarecer: a regra “espera 62 anos, encontra um hospedeiro, espera mais 62” não fecha com 1853, 1915, 1979 e 2026; transformar o número em crença da entidade ou ajustar as âncoras. | fragmentos/doc/DOC-26.tex:31 |
| DOC-08 | Rever: o parecer exclui transtorno psicótico compartilhado porque Lúcia nunca conheceu os dois, mas o romance inteiro afirma que o texto transmite; a exclusão precisa considerar a leitura como contato. | fragmentos/doc/DOC-08.tex:41 |
| DOC-09 | Manter como artefato: “validade preditiva de 100%” deve soar como captura da linguagem clínica pela criatura, não como validação do instrumento; uma linha de estranhamento ajudaria. | fragmentos/doc/DOC-09.tex:143 |
| DOC-27 | Verificar: a anotação de 1916 já cita o “Processo 1.260”, anterior à admissão de 1917; se for a criatura escrevendo fora do tempo, sinalizar; se for erro, corrigir a data. | fragmentos/doc/DOC-27.tex:77 |
| LUC-01 | Manter: a elipse entre o pedido de janeiro e o e-mail em “inverno de 2026” funciona como abertura atmosférica; o texto não fixa o mês, e a estação não deve ser lida como data exata. | fragmentos/luc/LUC-01.tex:8 |
| LUC-15 | Manter: o toque breve e o cartão de acesso são uma intimidade contida, não um encontro; a cena funciona porque não resolve o vínculo entre os dois. | fragmentos/luc/LUC-15.tex:65 |
| LUC-02 | Corrigir: a carta diz que foi escrita em 1979 e que o autor passou 47 anos tentando entender; escolher uma ontologia ou marcar a segunda voz como intervenção da criatura. | fragmentos/luc/LUC-02.tex:119 |
| LUC-03 | Verificar: Lúcia atribui a inscrição que a nomeia a 1956 sem demonstrar a datação; fotografar, comparar camadas ou admitir a hipótese como hipótese. | fragmentos/luc/LUC-03.tex:80 |
| LUC-04 | Manter: a fala “troca de mão; a senhora fecha a sua e outra abre” é uma das melhores imagens do ciclo; separar com clareza o destino do objeto do custo de quem o carrega. | fragmentos/luc/LUC-04.tex:179 |
| LUC-05 | Rever: “o ciclo tinha começado” fixa uma causa depois do sonho de abril, mas o cheiro e os despertares já aparecem em janeiro; atribuir a certeza a Lúcia, não ao narrador. | fragmentos/luc/LUC-05.tex:109 |
| LUC-Contraprova | Rever: o mapeamento retiniano normal não explica a mudança de cor da íris; separar o resultado observado da conclusão sobre a descoloração para que a contraprova seja honesta. | fragmentos/luc/LUC-Contraprova.tex:30 |
| LUC-Entrevista | Esclarecer: Antenor chama de “segundo diário” um caderno preto pós-morte, quando Lúcia já encontrara outro caderno preto; perguntar quantos objetos existem e quem guardou cada um. | fragmentos/luc/LUC-Entrevista.tex:74 |
| LUC-16 | Manter: o “eu prometo” à mãe cria uma dívida afetiva que a partida de Lúcia deve cobrar; a cena é mais forte se a promessa não for cumprida e o texto souber disso. | fragmentos/luc/LUC-16.tex:93 |
| LUC-Escolha | Rever: a quarta opção é ler o segundo diário, mas ele aparece aberto sem lembrança dela e ela o fecha e foge; encenar a escolha ou reconhecê-la como adiada. | fragmentos/luc/LUC-Escolha.tex:58 |
| LUC-06 | Corrigir: “não foi vista desde então” em 13/05 contradiz a movimentação no APM em 28/07 e a foto de 03/09; datar cada registro e dizer quem perdeu contato com ela. | fragmentos/luc/LUC-06.tex:70 |
| LUC-07 | Verificar: o caderno de Oliveira é encontrado no Ceará e reaparece em uma caixa do Arquivo Mineiro; mostrar ao menos um elo de transporte e guarda. | fragmentos/luc/LUC-07.tex:20 |
| LUC-08 | Rever: a fala sobre custódia judicial surge depois de Lúcia sair da sessão e “nunca mais” falar com Regina; recolocá-la na conversa preserva o pedido de ajuda e seu custo. | fragmentos/luc/LUC-08.tex:118 |
| LUC-09 | Rever: Lúcia identifica o crânio como Oliveira sem confirmação externa; manter “pode ser” como hipótese permitiria que a exumação abrisse, e não encerrasse, as alternativas. | fragmentos/luc/LUC-09.tex:66 |
| LUC-10 | Esclarecer: o laudo situa em janeiro o contato com o diário, enquanto a autoavaliação data a primeira leitura em abril; distinguir pedido, posse e leitura antes de atribuir sintomas. | fragmentos/luc/LUC-10.tex:27 |
| LUC-11 | Verificar: a digitação de cada página exige explicar como Lúcia recuperou o original após a devolução de maio e a suspensão de cópias de julho. | fragmentos/luc/LUC-11.tex:23 |
| LUC-12 | Corrigir: a última foto é de 03/09/2026, mas LUC-06 diz que ela não foi vista desde 13/05; a foto pode ser a última aparição, mas o texto precisa dizer quem a viu e quando. | fragmentos/luc/LUC-12.tex:14 |
| LUC-17 | Manter: a passagem do medo à fome mostra que a autonomia de Lúcia é real, mas já está sendo minada; é o melhor exemplo da agência trágica do arco. | fragmentos/luc/LUC-17.tex:55 |
| LUC-13 | Manter: a nota do arquivista explica o corte de 23 segundos e a restauração parcial; a transcrição seletiva é coerente com o arquivo, desde que o leitor saiba que não é integral. | fragmentos/luc/LUC-13.tex:17 |
| LUC-18 | Manter: Ronaldo escolhe Lúcia para poupar a filha, e a justificativa não o absolve; a assimetria moral é o ponto, e Lúcia deve reagir a ela sem apagá-la. | fragmentos/luc/LUC-18.tex:41 |
| LUC-14 | Corrigir: o documento datado de 13/04 contém uma seção de maio e um e-mail de 12/05, enquanto a nota forense diz que o arquivo não foi acessado depois de 13/04; separar o anexo ou corrigir a nota. | fragmentos/luc/LUC-14.tex:216 |
| LUC-19 | Manter: a foto de Lúcia aos oito anos com o pai, guardada e não levada, condensa o luto sem explicá-lo; a contenção é mais eficaz que qualquer confissão. | fragmentos/luc/LUC-19.tex:11 |
| LUC-20 | Verificar: Ronaldo diz que o diário voltou em 2019 e que ele o abriu; falta o elo entre essa posse e o achado na recepção do APM em 2026. | fragmentos/luc/LUC-20.tex:55 |
| CONT-01 | Corrigir: “durante 62 anos, o diário cresceu dentro da terra” contradiz os 62 dias de MEM-16 e da Nota do Arquivista; trocar por 62 dias ou assumir a versão impossível do coveiro. | fragmentos/cont/CONT-01.tex:30 |
| CONT-03 | Rever: “passe o dedo nos lábios” é uma instrução tátil que o aviso diz não produzir efeito; manter o horror, mas deixar claro que a ação é simbólica e o leitor pode não executá-la. | fragmentos/cont/CONT-03.tex:48 |
| CONT-04 | Manter: a noite sem susto e a ausência do medo são mais assustadoras que o susto; o fragmento desacelera o terror e transforma a espera em sintoma. | fragmentos/cont/CONT-04.tex:152 |
| CONT-05 | Corrigir: “Joaquim Antônio Correia (ele é real)” contradiz o aviso e a Nota Histórica; o laudo pode afirmar isso como delírio do leitor, mas o texto precisa marcar a afirmação como falsa. | fragmentos/cont/CONT-05.tex:97 |
| CONT-07 | Rever: a segunda enumeração dos critérios A-G retoma extensamente o laudo de CONT-05; dar ao segundo laudo uma função nova, como o diagnóstico final do leitor, em vez de recapitular. | fragmentos/cont/CONT-07.tex:23 |
| CONT-09 | Rever: “a íris está mais clara?” atribui ao leitor uma percepção que ele pode não ter; oferecer uma saída cética ou transformar a pergunta em dúvida, não em confirmação. | fragmentos/cont/CONT-09.tex:18 |
| CONT-13 | Manter: “não há opção limpa” é a tese do ciclo e funciona porque fechar, passar adiante e reler têm custos distintos; a escolha do leitor é real, mas nenhuma é inocente. | fragmentos/cont/CONT-13.tex:19 |
| MEM-27 | Rever: a nota editorial longa em 38 interrompe o retorno de Joaquim no clímax; mover o aparato para o fim do fragmento ou reduzi-lo a uma linha. | fragmentos/mem/MEM-27.tex:38 |

## 6. Paratextos incluídos

Os 16 arquivos chamados por `main.tex` foram lidos e avaliados. A ordem abaixo
segue a ordem de entrada no volume.

1. `frontmatter/titlepage.tex:27` — a folha de rosto e a capa cumprem a função.
   “Coautor: Marcelo Claro” está coerente com a capa (“Coautor e ilustrador”),
   mas o crédito de ilustração não aparece na ficha catalográfica. Alinhar.
2. `frontmatter/aviso_ao_leitor.tex:27` — o melhor paratexto ético do volume:
   nomeia riscos, separa ficção de realidade e oferece CVV e CAPS. A garantia
   de que nenhuma instrução produz efeito físico é correta, mas não resolve a
   contradição com a página Cuidado.
3. `frontmatter/epigrafe.tex:12` — “Ela não é um monstro. Ela é uma
   consequência” sintetiza o livro sem entregar o enredo. Manter.
4. `frontmatter/cuidado.tex:18` — “não pare; já é tarde demais para parar”
   contradiz o direito de interrupção do Aviso. Se a intenção é horror, falta
   uma linha que devolva a escolha ao leitor.
5. `frontmatter/copyrightpage.tex:35` — a piada sobre insônia e olhos amarelos
   enfraquece o registro cuidadoso do Aviso. Uma nota de humor é legítima, mas
   não no mesmo volume que pede cuidado com trauma.
6. `frontmatter/ficha_catalografica.tex:20` — “1. ed. rev.” contra
   `"edition": "2 (revista)"` em `book.json`. A ficha não indica agência
   catalogadora; é provisória. Decidir a edição e padronizar.
7. `frontmatter/nota_arquivista.tex:32` — “a dor documentada nestas páginas não
   é ficção” mistura sofrimento histórico e prontuário ficcional. A linha 41
   dá 60.000 mortos e 1.853 corpos exumados como números exatos, enquanto a
   Nota Histórica diz que os totais não são precisos. Atribuir e qualificar.
8. `frontmatter/como_ler.tex:12` — as quatro rotas são úteis, mas “185 rotas”
   não corresponde às 223 pretendidas; a seção de códigos é repetida na
   Legenda seguinte. Unificar a contagem e remover a repetição.
9. `frontmatter/legenda_codigos.tex:25` — as famílias visuais são claras. Os
   contrastes declarados (6,76; 6,76; 9,23; 7,18) foram medidos sobre #F8F0D7,
   não sobre o fundo real #F2E8CF, que dá 6,32; 6,31; 8,62; 6,71. Todos passam
   o mínimo de 4,5:1, mas o número declarado não é o do papel usado.
10. `frontmatter/tocpage.tex:5` — o sumário funciona e tem links. A paginação
    impressa confere com o PDF; a paginação do EPUB não é a mesma, o que afeta
    as páginas fixas do epílogo.
11. `frontmatter/nota_editorial.tex:44` — assinada “Julho de 2026”, mas o
    volume inclui documentos de 1º, 3 e 4 de agosto e uma foto de 3 de
    setembro. A nota não pode ser anterior aos documentos que descreve.
12. `frontmatter/caderno_iconografico.tex:8` — exemplo positivo: declara que as
    imagens são reconstituições ficcionais, não documentos históricos. As
    legendas repetem “Reconstituição ficcional” em cada prancha. Manter.
13. `frontmatter/glossario_historico.tex:41` — “achado pericial anômalo
    documentado no exame de Joaquim” trata um personagem ficcional como caso
    documentado. Trocar “documentado” por “narrado” ou “ficcional”.
14. `frontmatter/nota_historica.tex:10` — diz que “a instituição narrada como o
    Colônia é ficcional”, mas a linha 31 diz que o Hospital Colônia de
    Barbacena “existiu de verdade”. Corrigir a primeira frase para “a versão
    narrativa do Colônia é ficcional; a instituição histórica existiu”.
15. `frontmatter/ficha_beta_diegetica.tex:12` — pede devolução assinada ao
    Arquivista e lista sintomas. Não diz que é opcional nem que não é
    instrumento clínico. Vem depois da Nota Histórica, que deveria encerrar o
    volume. Mover para antes ou marcar como brinde ficcional.
16. `frontmatter/colofao.tex:1` — o colofão substitui a contracapa no miolo
    corrigido e exibe o ISBN `979-8-18-917049-2`. A antiga
    `frontmatter/backpage.tex:14` permanece como asset de capa, fora do miolo;
    o OCR da imagem antiga mostrava o ISBN `978-65-01-23456-7`, diferente do
    miolo, e a sinopse repetia “62 anos” debaixo da terra.

## 7. Epílogo e arquivos não incluídos

O epílogo (`fragmentos/epilogo_revisado.tex:42-55`) retoma Lúcia como Paciente
1.262, a nota de Ronaldo e a confirmação pelo cheiro. A prosa é eficaz, mas
depende de páginas fixas (“página 62”, “página 126”) que só existem na
paginação impressa. No EPUB, o leitor não tem como cumprir a instrução. A
solução é remover os números ou substituí-los por âncoras textuais (“a página
em que Joaquim encontra a criatura”).

O `apendice/aparato_de_leitura.tex` existe, mas **não é incluído** por
`main.tex`; não faz parte do miolo. Os seis arquivos em
`fragmentos/cont/_removidos/` (CONT-02, 06, 08, 10, 11 e 12) também não são
incluídos. Eles aparecem nos grafos, o que é um dos motivos da desatualização
do aparato visual.

## 8. O que preservar

- **A voz de Joaquim** quando retorna em primeira pessoa, sobretudo em
  `MEM-04:190`, `MEM-10:124`, `MEM-14:78`, `MEM-20:114` e `MEM-27:14`.
- **A agência sob coação**: o “sim” faminto, a mentira para proteger o menino,
  a negociação com Oliveira, as cinco batidas. É a tese moral do livro.
- **O arco de Lúcia**: a passagem do medo à fome (`LUC-17:55`), a escolha de
  Ronaldo (`LUC-18:41`), a foto que ela não leva (`LUC-19:11`).
- **Os melhores documentos**: a ficha com aviso ficcional (`DOC-02:11`), a
  reconstituição administrativa com nota de limites (`DOC-18:10-39`), o termo
  de custódia que assume as lacunas (`DOC-20:42-44`), o parecer de conservação
  (`DOC-24`).
- **O Caderno Iconográfico** e sua declaração de que as imagens não são provas.
- **A Nota Histórica**, especialmente o parágrafo sobre estetização
  (`nota_historica.tex:50-59`), que é o melhor texto ético do volume.
- **O sistema visual** de cores e capitulares, coerente e legível.
- **A recusa de um final limpo** em `CONT-13:19`: fechar, passar adiante e
  reler têm custos distintos. É a melhor ideia formal da Parte 5.

## 9. O que não é erro

Uma revisão justa precisa separar erro de deliberação. Não devem ser
“corrigidos” às cegas:

- **A memória lacunar de Joaquim** (`MEM-08:14`, `MEM-25:46`). A confusão entre
  idade e tempo de cárcere pode ser um sintoma, não uma falha aritmética; o
  que falta é um sinal de que o texto sabe disso.
- **As contradições da criatura**. Ela mente, seduz e reescreve. Se o livro
  assumir que ela é uma narradora não confiável, várias discrepâncias passam a
  ser caracterização.
- **O depoimento impossível do coveiro**. `DOC-01:53` pode ser delírio ou
  contaminação; o problema é que o livro não decide se o leitor deve acreditar
  nele.
- **O motivo dos 62**. “62 anos, 62 dias, 62 segundos” é uma ideia forte; o
  problema não é a repetição, é a aplicação a intervalos que não fecham.
- **As lacunas de custódia** (`DOC-20:42-44`). O termo de custódia é honesto
  ao dizer que é “um documento de ausências”; a lacuna é o assunto, não um
  defeito.
- **A ambiguidade clínica** (`DOC-08:43`, `DOC-09:143`). Um laudo que não
  fecha o diagnóstico é coerente com a tese; o que não pode é usar linguagem
  de certeza científica para uma criatura ficcional.

## 10. Plano de ação priorizado

### P0 — antes de qualquer nova compilação

1. Resolver o cluster dos 62: `DOC-01:33`, `DOC-01:53`, `DOC-21:31`,
   `CONT-01:30` e a contracapa. Escolher entre “62 dias” e “62 anos” e
   aplicar em todas as camadas. Corrigir `MEM-26:22` (64 anos de posse, não
   62).
2. Resolver as datas de Lúcia: `LUC-06:70`, `DOC-20:29`, `DOC-25:64`,
   `LUC-12:14`, `LUC-12:70` e `LUC-20:55`. Criar a tabela de custódia.
3. Corrigir o ISBN da contracapa e decidir se o PDF é miolo ou livro completo.
   Se for miolo, remover capa e contracapa; se for capa, criar o spread com
   lombada e sangria.
4. Corrigir `DOC-19:25` (“Joaquim é um dos 60 mil”) e `DOC-19:11`
   (“Transcrição autorizada”), conforme a autorização real.

### P1 — coerência editorial

5. Padronizar o aviso ficcional dos DOC e corrigir os anacronismos:
   `DOC-05:42`, `DOC-07:22-34`, `DOC-07:28`, `DOC-04:32`, `DOC-12:89`,
   `DOC-27:77`.
6. Corrigir `DOC-06:197` (dose), `DOC-13:15` (nota), `DOC-14:52` e
   `DOC-20:26` (custódia), `DOC-21:31` (62 anos), `DOC-22:42` e `DOC-23:29`
   (retirada/devolução), `DOC-24:26` (fólios/páginas).
7. Corrigir `LUC-02:119` (1979/47 anos), `LUC-14:216` (seção de maio no
   documento de abril), `LUC-06/12/20` (custódia),
   `LUC-03:80` (1956), `LUC-05:109` (começo do ciclo), `LUC-09:66` (crânio),
   `LUC-10:27` (janeiro/abril), `LUC-11:23` (digitação).
8. Substituir os 12 blocos de Markdown por `\rota{}`, regerar os grafos e
   corrigir as contagens. Atualizar `main.tex:562-563` para 26/7.
9. Resolver as notas de margem: restaurar a única `\margnota` ou reescrever
   `main.tex:669`.
10. Harmonizar os paratextos: Cuidado, Aviso, Epílogo, Ficha Beta, Nota
    Histórica, Nota do Arquivista e Glossário.

### P2 — linha editorial

11. `MEM-02:60` (repetição), `MEM-06:46` (mortandade), `MEM-09:14`
    (silêncio), `MEM-19:50` (Maria), `MEM-24:36` (estigma), `MEM-25:46`
    (63 anos), `MEM-27:38` (nota longa).
12. `DOC-01:8` (título duplicado), `DOC-11:103` (eco), `DOC-15:31`
    (atribuição), `DOC-16:103` (Verônica), `DOC-25:64` (sete meses).
13. `CONT-03:48` (instrução tátil), `CONT-05:97` (“ele é real”),
    `CONT-07:23` (recapitulação), `CONT-09:18` (íris).
14. Atualizar a ficha catalográfica para a edição correta e qualificar a CIP
    como provisória.

### Testes propostos para a revisão seguinte

- Um `scripts/check_r1075_consistency.py` com asserções para: (a) todas as
  ocorrências de “62 anos” debaixo da terra; (b) as datas de Lúcia; (c) a dose
  de clorpromazina; (d) o ISBN do miolo e da contracapa; (e) a contagem de
  rotas e a ausência de Markdown literal; (f) a presença de capa/contracapa
  no PDF.
- Um teste de renderização que rasterize as páginas dos grafos e verifique a
  legibilidade mínima dos rótulos.
- Um teste de paratextos que compare as promessas do Aviso, do Cuidado, do
  Epílogo e da Ficha Beta.

## 11. Limites e alegações seguras

- **Não é validação clínica.** O parecer não avalia a correção dos
  diagnósticos, das escalas ou das doses como prática médica; avalia
  verossimilhança histórica e coerência interna.
- **Não é validação histórica.** Os números de 60.000 mortos e 1.853 corpos
  exumados são atribuídos a Daniela Arbex no próprio livro; não os verifiquei
  em fonte primária nesta revisão. A Nota Histórica precisa de fontes para os
  campos do Ceará, não apenas para Barbacena.
- **Não é certificação KDP.** O PDF tem 421 pp e 160 × 230 mm, mas inclui capa
  e contracapa, tem ISBN divergente e não tem sangria de capa. Não é um
  pacote de upload pronto.
- **Não é revisão de arte.** A apreciação das imagens, da capa e dos grafos é
  funcional, não estética.
- **Não é validação do EPUB.** O EPUBCheck e o Ace declarados no release não
  foram reexecutados.
- **Não é leitura beta humana.** A revisão foi feita por leitura distribuída e
  verificação local; não substitui leitores humanos independentes, sobretudo
  para a representação de trauma, violência institucional e saúde mental.
- **Não é a edição canônica nem a R1077.** O parecer vale para a R1075. A
  variante de impressão R1077 e a edição canônica de 435 pp não foram
  avaliadas.
- **Não há nota, Qualis ou garantia de aceite.** Qualquer uso do parecer como
  aprovação editorial seria overclaim.

## 12. Evidência RED/GREEN e rastreabilidade

- **RED:** antes deste parecer, `tests/test_r1089_molambudos_review_coverage.py`
  falhava com `FileNotFoundError` para
  `reports/r1089/revisao_integral_r1075.md`. Os dois testes de cobertura
  estavam vermelhos, como previsto na SPEC-935-R1089.
- **GREEN:** este arquivo cria a matriz com 84 entradas na ordem de `main.tex`,
  cada uma com localizador real; a seção de paratextos cobre os 16 arquivos
  incluídos; o epílogo, o apêndice não incluído e os `_removidos` são
  declarados. A verificação final está registrada na conversa e no teste.
- **Regressões:** a revisão não alterou o manuscrito. Os testes de R1075,
  R1076, R1077, R240 (grafos), R397 (coerência diegética), R406 (coerência
  factual) e R362 (paginação) devem ser rodados como estavam; eventuais falhas
  prévias pertencem ao estado da edição, não a esta revisão.

**Arquivos centrais conferidos:** `main.tex`, `main_kdp_pt_160x230mm.tex`,
`book.json`, `release/README.md`, `release/SHA256SUMS.txt`, os 84 `.tex` de
fragmentos, os 16 `.tex` de `frontmatter/`, `fragmentos/epilogo_revisado.tex`,
o PDF de 421 pp e as três imagens de grafo em `misc/`.

**Contato com o parecer anterior:** `reports/r1075/README.md` foi usado apenas
como cotejo. As contagens de DOC, LUC e CONT foram reconferidas na fonte; o
parecer anterior não substitui esta leitura.

---

*Este parecer é um documento de trabalho. Ele não certifica KDP, não é validação clínica, não é validação histórica e não substitui leitura humana independente.*
