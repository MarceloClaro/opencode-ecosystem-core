---
spec_id: SPEC-935-R397
title: Coerência diegética de Molambudos — o leitor deixa de ser chamado pelo número de outro personagem
component: projetos/molambudos/Molambudos_VictoriaRegia, tests/test_r397_molambudos_coerencia_diegetica.py
status: verified
test_file: tests/test_r397_molambudos_coerencia_diegetica.py
---

# SPEC-935-R397 — Coerência Diegética de Molambudos

**Data:** 2026-08-04
**Motivação:** o usuário pediu para avaliar o ecossistema *corrigindo uma obra
literária* rumo a uma obra de referência internacional, cuja proposta é terror
psicológico indutivo e hipnótico, imersão sensorial e paranoia — **sem
qualquer quebra de imersão**. A avaliação foi feita lendo a obra, não a
documentação sobre ela.

## 1. O diagnóstico: o ecossistema mede a forma, não o sentido

Vinte arquivos de teste (R238–R395) mais um preflight PDF *fail-closed* de
1.200+ linhas guardam esta obra. Todos operam na camada **mecânica**: compila,
geometria de página, zonas de sangria, caixas overfull, aspas tipográficas,
datas culturalmente equivalentes, paridade de contagem de rotas com hash
SHA-256 do multiconjunto impresso.

Nenhum deles pergunta se **o arquivo contradiz a si mesmo** — que é
precisamente o que quebra a imersão num livro cujo dispositivo central é um
arquivo forense que se apresenta como confiável.

Consequência medida: os defeitos mais graves da obra sobreviveram a 212 ciclos
de evolução e a 20 guardas, porque nenhuma guarda apontava para eles.

## 2. Defeitos reais encontrados e corrigidos

### 2.1 O leitor era chamado pelo número de outro personagem (crítico)

A obra constrói uma fila de corpos ocupados pela criatura, e a precisão dessa
contagem é o que faz o golpe final ("você é o próximo") aterrissar:

| Nº | Quem | Onde é fixado |
|---|---|---|
| 1.259 | o anterior a Joaquim | CONT-07, CONT-08 |
| 1.260 | Joaquim Antônio Correia | título da obra, 79 ocorrências |
| 1.261 | Dr. Heitor Oliveira | DOC-16 (*"O paciente 1.261 sou eu"*, assinado *"— Paciente 1.261"*), DOC-24, LUC-11 |
| 1.262 | Dra. Lúcia Mendes | LUC-10, LUC-11, Epílogo (*"— Lúcia Mendes, Paciente 1.262"*) |
| **1.263** | **o leitor** | LUC-12 (*"Paciente 1.262 encerra seu ciclo. O paciente 1.263 é quem abrir esta caixa"*), DOC-24, CONT-09, Epílogo, `frontmatter/como_ler.tex`, `frontmatter/ficha_paciente_1263.tex` |

Apesar disso, **CONT-04, CONT-05 e DOC-09 endereçavam o leitor como 1.261** —
o número de Oliveira. CONT-05 registrava literalmente `PACIENTE: Você` /
`REGISTRO: 1.261`, e fechava com **"O paciente 1.261 é você"**.

Na leitura linear o leitor encontrava, em 50 páginas:

- p. 585 (DOC-16): *"O paciente 1.261 sou eu."* — Oliveira
- p. 591 (DOC-24): *"...Oliveira (paciente 1.261)... Bem-vindo, paciente 1.263."*
- p. 604 (DOC-09): *"Bem-vindo, paciente **1.261**."* — dirigido ao leitor
- p. 633 (CONT-05): *"O paciente **1.261** é você."* — **no clímax**
- p. 637 (CONT-09): *"Bem-vindo ao ciclo, Paciente 1.263."*

Pior: a "Rota do Terror", sequência curada que o próprio protocolo oferece
como experiência de imersão dirigida (CONT-03 → CONT-04 → MEM-12 → CONT-05),
atravessa **os dois** endereçamentos errados e termina em "O paciente 1.261 é
você", sem nunca alcançar CONT-09. A rota-bandeira da obra entregava o número
errado como golpe final, contradizendo a página de protocolo lida no início.

Isto não é ambiguidade deliberada: DOC-09 lista o Dr. Oliveira como *sujeito
de teste anterior* na sua própria seção de validação, enquanto pede ao leitor
"escreva seu nome" — o fragmento se contradiz internamente.

**Correção:** 26 linhas em PT/EN/ZH. Apenas as ocorrências que endereçam o
leitor em segunda pessoa foram alteradas; as legítimas (Oliveira se
identificando em DOC-11, DOC-16, CONT-06 e na linha 30 do CONT-05 chinês, e a
enumeração da cadeia) ficaram intactas.

### 2.2 O protocolo mandava procurar uma etiqueta inexistente

`frontmatter/como_ler.tex` instruía: *"siga as setas de indicação (**↪
Links:**)"*. Os 84 fragmentos usam **"↪ Rotas:"** (PT), **"↪ Routes:"** (EN),
**"↪ 路线:"** (ZH) — nas três edições.

A divergência foi **criada pelo R389 desta mesma sessão**, que converteu as
linhas de navegação em texto puro para o macro `\rota{}` e não atualizou o
protocolo. Uma correção técnica do ecossistema quebrou a imersão, e nenhuma
guarda notou.

**Subarmadilha encontrada ao corrigir (e corrigida):** `"Rotas:"` não é só
texto para o leitor — é o **marcador legível por máquina** de
`scripts/validate_molambudos_routes.py::MARKERS`, e `extract_printed_routes()`
trata como linha de rotas qualquer linha impressa que comece por ele,
absorvendo até 7 linhas seguintes. Ao escrever o token literal com dois-pontos
no protocolo, a própria página de instruções passou a ser lida como uma linha
de rotas e arrastou 4 rotas curadas para a contagem impressa (196 vs 192 nas
três edições isoladas), bloqueando o preflight R362.

Resolvido citando a etiqueta **sem** o dois-pontos (`↪ Rotas`), o que
permanece exato para o leitor — a etiqueta impressa começa por esse texto — e
não colide com o extrator. O auditor não foi enfraquecido para acomodar o
livro. A lição fica registrada no próprio teste: o espaço de strings do texto
literário e o dos marcadores de parsing se sobrepõem, e mudanças no primeiro
podem quebrar silenciosamente o segundo.

### 2.3 O livro contava a si mesmo errado

| Declarado (PT/EN/ZH) | Real |
|---|---|
| "78 fragmentos" (em 3 arquivos de frontmatter) | **84** |
| "180 rotas de leitura" | **192** |
| "de três formas distintas:" | seguido de **4** itens numerados |

Num livro que se apresenta como arquivo pericial fiel, o leitor que confere
descobre que o arquivo erra sobre si mesmo — exatamente o tipo de traição de
credibilidade que derruba a suspensão de descrença.

### 2.4 Vazamento de grupos LaTeX: a guarda media o proxy, não a propriedade

O padrão `\textquotedblleft{\textit{...}` abre **dois** grupos e fecha **um**
— o `{` depois do comando deveria ser `{}`. Cada ocorrência vaza um grupo
aberto. Os arquivos afetados compensavam despejando as chaves que faltavam
numa única linha no fim do arquivo:

| Arquivo | Grupos vazados |
|---|---|
| `fragmentos/doc/DOC-25.tex` | 52 |
| `en/fragmentos/doc/DOC-25.tex` | 53 |
| `fragmentos/luc/LUC-14.tex` | 13 |
| `en/fragmentos/luc/LUC-14.tex` | 14 |
| `fragmentos/doc/DOC-24.tex`, `en/`, `zh/` | 4 cada |
| `en/fragmentos/doc/DOC-27.tex` | 3 |
| **Total** | **147** |

Efeito de renderização: a partir da primeira aspa vazada, todo o resto do
fragmento fica dentro de `\textit` aninhados — e `\textit` dentro de `\textit`
volta para redondo. A ênfase alternava errado até o fim do fragmento. DOC-25
tem 236 linhas; a maior parte renderizava com ênfase trocada.

**Por que nenhuma guarda pegou:** o teste existente valida *saldo de chaves =
0*. Despejar 52 chaves no EOF satisfaz o saldo sem corrigir o vazamento. O
arquivo compilava limpo, o auditor passava, e o PDF saía errado. A guarda
media o **proxy** (saldo líquido) em vez da **propriedade** (cada grupo fecha
onde abre).

**Correção:** os 147 grupos foram identificados por varredura posicional
(todos, sem exceção, abertos imediatamente após `\textquotedblleft`) e cada um
foi **fechado no fim da própria linha em que abre**, com os despejos removidos.
Saldo final 0 em todos, sem nenhuma linha de despejo restante no corpus.

**Primeira tentativa, descartada pela suíte:** a correção inicial esvaziava o
grupo espúrio (`\textquotedblleft{` → `\textquotedblleft{}`), o que é
equivalente em renderização (`\textquotedblleft` não recebe argumento; o grupo
é inerte). Mas quebrou
`test_r358...::test_doc25_preserves_two_distinct_utterances_in_all_languages`,
que fixa a forma literal de uma construção de **duas falas** em DOC-25, onde o
grupo externo envolve deliberadamente fala + narração intercalada. O PT já
fechava esse grupo (`}}}`); o EN o deixava aberto. Fechar na linha de origem
— em vez de esvaziar — repara o defeito, preserva a forma original de cada
linha e faz o EN espelhar exatamente o PT. É o motivo de a regra ser "fechar
onde abre" e não "remover o grupo".

## 3. A guarda que faltava

`tests/test_r397_molambudos_coerencia_diegetica.py` — 28 testes, 4 eixos:

1. **Cadeia de pacientes**: fragmentos que endereçam o leitor usam o número do
   leitor; nenhum fragmento atribui ao leitor um número de personagem; a
   cadeia 1.259→1.263 é contínua.
2. **Protocolo × realidade**: a etiqueta que o protocolo manda procurar é a
   que os fragmentos de fato usam, por idioma.
3. **Autocontagem**: fragmentos, rotas e número de modos de leitura
   declarados batem com os reais.
4. **Integridade de grupos**: nenhum despejo de chaves no EOF; nenhum grupo
   aberto.

A guarda provou o próprio valor durante a implementação: pegou um erro **meu**
— eu havia corrigido a contagem para 85 (número de `\fragdef{}` em `main.tex`),
mas o 85º é o `Epilogo`, capítulo inline sem arquivo de fragmento. O valor
correto é 84.

## 4. O que foi deliberadamente **não** corrigido

### 4.1 As três edições não são o mesmo livro (decisão autoral)

Doze fragmentos divergem estruturalmente entre PT/EN/ZH muito além de
diferença de idioma:

| Fragmento | PT | EN | ZH |
|---|---|---|---|
| DOC-25 | 236 | 236 | **395** |
| CONT-05 | 163 | 163 | **63** |
| CONT-03 | **174** | 102 | 102 |
| CONT-12 | 51 | 47 | **101** |
| DOC-26 | 110 | 110 | **56** |
| CONT-13 | 72 | 72 | **108** |
| LUC-Escolha | **90** | 69 | 69 |
| MEM-27 | **61** | 43 | 43 |

O CONT-05 chinês contém uma fala de Oliveira que não existe em PT nem em EN.
O CONT-03 português ganhou uma "ESCALA DE CONTAMINAÇÃO — ATUALIZAÇÃO 2" que
as outras edições nunca receberam.

Escolher qual versão é canônica é decisão **autoral e de tradução**, não
mecânica. Fica documentado, não corrigido unilateralmente, e é o maior
obstáculo restante à alegação de "obra de referência internacional": na edição
trilíngue as três colunas ficam lado a lado, e a divergência é visível.

### 4.2 As notas do editor desinflam a indução no pico (tensão real)

Treze fragmentos carregam `\NE{}` (nota de rodapé do editor). Duas caem no
ponto exato de máxima imersão:

- **CONT-03** encerra a indução com *"Para seu corpo, ela é real."* — e a nota
  imediatamente informa que "a contaminação é textual, não material".
- **CONT-04** fecha com *"Obrigado, paciente 1.263. O ciclo continua."* — e a
  nota informa que o padrão onírico "é um dispositivo narrativo".

Há um conflito genuíno entre a honestidade epistêmica (que o ecossistema
impõe corretamente, R363–R369) e o efeito hipnótico pretendido. A nota é a
única coisa no livro que fala de fora da ficção; ela protege o leitor e custa
a imersão. **Recomendação, não alteração:** mover as `\NE{}` de CONT-03 e
CONT-04 para uma seção única de "Nota Clínica" no final do volume preservaria
integralmente a proteção sem interromper o transe — mas é decisão do autor.

### 4.3 O selo Merkle certifica um livro que não existe mais

`SELO_INTEGRIDADE_MERKLE.json` (2026-07-29, v3.5) declara **74 fragmentos**
(reais: 84) e seus hashes não conferem:

- `sha256_main_tex` do selo ≠ hash atual
- `sha256_pdf` do selo ≠ hash atual

Nada no ecossistema confere ou regenera esse selo — `grep -rl
SELO_INTEGRIDADE_MERKLE tests/ scripts/ marceloclaro/ integrations/` não
retorna nada. É um artefato de aparência criptográfica que não sustenta
nenhuma alegação de proveniência. Não foi regenerado neste ciclo porque
regenerá-lo sem uma política de quando/como revalidar apenas repetiria o
problema.

### 4.4 O corpus inteiro está fora do controle de versão

`.gitignore:93` ignora `projetos/`. Os 302 arquivos `.tex` da obra — todo o
texto literário — **não têm um único commit**. O trabalho editorial de dezenas
de ciclos não tem histórico, diff, nem possibilidade de rollback. Este ciclo
criou `_archive/backup_R397_pre_coerencia_diegetica/` manualmente por não
haver rede de proteção do git.

Reverter a decisão de gitignore tem implicações (tamanho: os PDFs somam ~90 MB)
e é decisão do usuário, não minha.

## 5. Critérios de aceitação

1. Nenhum fragmento endereça o leitor por um número que pertence a um
   personagem, em PT/EN/ZH. ✔
2. A etiqueta de navegação do protocolo é a que os fragmentos usam, nas três
   edições. ✔
3. As contagens declaradas (84 fragmentos, 192 rotas, 4 modos) batem com o
   corpus real. ✔
4. Zero grupos LaTeX abertos e zero despejos de chaves no EOF em todo o
   corpus trilíngue. ✔
5. `tests/test_r397_molambudos_coerencia_diegetica.py` 28/28. ✔
6. As cinco edições continuam compilando e o preflight R362 não regride. ✔
7. As limitações fora do alcance mecânico (§4) ficam documentadas
   explicitamente, não apresentadas como resolvidas. ✔
