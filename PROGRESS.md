# PROGRESS — Checkpoint de trabalho resumível

> Arquivo vivo (R129). Serve para **retomar o trabalho de onde parou** se
> uma sessão terminar no meio. Atualize-o e commite a cada passo concluído.

## Estado atual

- **Branch:** `main` · última entrega: **R404 — notas do editor saem do clímax de contaminação** (2026-08-07)
- **R404 (2026-08-07) — "remova a nota do editor que está quebrando o clímax…
  corrija para imergir um desconforto e sensações já propostas":** o R397
  identificou e recomendou; o R398 implementou e **reverteu** por quebrar
  proveniência. Desta vez os fragmentos rastreados foram levantados **antes** de
  agir (MEM-02/04/06/12/26, DOC-02/05/08/15/17/18, LUC-01/10) e confirmou-se que
  **CONT não está entre eles** — caminho livre sem tocar em registro selado.
  **As notas não eram todas a mesma coisa**: (a) *explicam a técnica* — CONT-02,
  CONT-10, CONT-13, crítica literária dentro da ficção desmontando o efeito no
  instante em que ocorre (CONT-02 dizia que "o uso da segunda pessoa é um
  dispositivo formal de contaminação") → removidas, esse material já está no
  dossiê do R403; (b) *ressalvas de proteção* — CONT-03/04/07 → migradas ao
  aviso; (c) *híbrida com desescalada* — CONT-01 mandava "feche o livro por 60
  segundos" no auge sensorial → removida; (d) **diegética** — CONT-11, o
  arquivista relatando um lápis de marca inexistente em 1979 → **mantida**,
  aprofunda o horror em vez de explicá-lo. 17 removidas (PT 13→9, EN 17→10,
  ZH 16→10). A substância protetiva migrou para `aviso_ao_leitor.tex` nos 3
  idiomas — paratexto antes da ficção, custo de imersão zero — com duas
  cláusulas novas: sonhos/sono/sintomas, e códigos clínicos, esta com **"este
  livro não diagnostica o leitor"** (importa porque DOC-09 formata um item de
  suicidalidade num instrumento com escore). **Efeito**: CONT-03 encerra em
  *"Para seu corpo, ela é real."* e a página segue; CONT-04 em *"Obrigado,
  paciente 1.263. O ciclo continua."* e vai direto às rotas. `test_r384`
  reescrito (fixava a **presença** da nota) para travar a política nova. ZH de
  impressão 397→399 págs, capa atualizada (23,79mm). Preflight
  **`overall_internal_spec_passed=True`, 648/648, zero violações**; suíte
  **2730, 0 falhas**. Ver `specs/SPEC-935-R404-molambudos-notas-fora-do-climax.md`.
- **R403 (2026-08-05) — "faça uma ficha dossiê sobre o projeto Molambudos em 3
  línguas… a nível acadêmico rigoroso":** criados `dossie/dossie_{pt,en,zh}.tex`
  (6, 6 e 7 páginas A4) como **aparato crítico separado** — não parte da ficção,
  para não quebrar o quadro diegético. Seções: ficha técnica medida, projeto
  literário, arquitetura formal, linhagem literária, técnicas narrativas,
  fundamentos teóricos, base histórica e postura ética, análise crítica,
  limitações verificadas, estado de validação, agenda de pesquisa. **Todos os
  números medidos** sobre os fontes (84 fragmentos: MEM 27/DOC 27/LUC 17/CONT
  13; 43.730 palavras PT, 44.978 EN, 70.750 caracteres ZH; 27 dos 84 com segunda
  pessoa sustentada). **Disciplina epistêmica**: a seção de linhagem declara que
  identifica afinidades formais verificáveis e **não** afirma que o autor leu as
  obras citadas — parentesco de procedimento, não genealogia de leitura. A seção
  *Estado de validação* separa o verificado tecnicamente do **não realizado**
  (revisão por pares, revisão editorial externa, verificação historiográfica,
  revisão nativa das traduções) e declara recepção crítica **inexistente** e
  impacto **não mensurável**. A análise crítica registra os dois lados; ponto
  mais sério levantado: a metáfora sobrenatural pode aliviar o horror histórico
  ao deslocar responsabilidade política para uma entidade.
- **R402 (2026-08-05) — "corrigir main_kdp_pt_160x230mm… não esqueça de
  atualizar as paginações":** existiam **quatro** wrappers com o mesmo basename
  `main_kdp_print_160x230mm.tex` (raiz, `en/`, `zh/`, `tri/`); como todos usam
  caminhos relativos à raiz, são compilados de lá e o LaTeX nomeia a saída pelo
  basename — **os quatro produziam o mesmo PDF**, e compilar dois sobrescrevia o
  outro sem erro. Era a explicação de o PDF da raiz conter texto chinês quando
  inspecionado no R399. Agora um wrapper por edição com jobname próprio
  (`main_kdp_{pt,en,zh,tri}_160x230mm.tex`), trim medido 160,0×230,0mm nas
  quatro: PT 435, EN 427, ZH 397, tri 1115 páginas. O miolo PT foi de 433 para
  435 (índice +11, mapas ampliados) e o teste da capa falhou de imediato —
  geradas as capas de EN e ZH, já que cada paginação exige lombada própria
  (25,93 / 25,46 / 23,67 mm). O selo passou a conferir **oito** paginações.
  **Defeito no próprio selo**: gerado durante um build, `_paginas()` leu
  `main.pdf` em reescrita, o PDF abriu sem erro reportando **zero** páginas e o
  selo gravou o zero — pior que campo ausente, porque é a paginação que
  dimensiona a lombada; agora devolve `None`, com teste. Testes R239/R240
  fixavam a fração `0.85\textheight` e quebraram ao ampliar para `0.90` sem nada
  real ter quebrado — reescritos para exigir a **propriedade** (escala relativa
  e restrição em **ambas** as dimensões, que é o que impede o estouro do R401).
  Ver `specs/SPEC-935-R402-molambudos-quatro-edicoes-de-impressao.md`.
- **R401 (2026-08-05) — "faça o mesmo com os mapas de grafos 2 e 3":**
  `molambudos_grafo_rotas.py` ganhou `--mapa {rotas,enredo,linear,todos}` e passou
  a derivar a estrutura de partes do próprio `main.tex`, não de lista mantida à
  mão — que foi como as legendas acabaram dizendo "78 fragmentos" muito depois de
  o corpus passar de 78. **Mapa 2**: atos agrupando as 5 partes (Trauma 9,
  Institucionalização 41, O Ciclo 35), faixas com altura **proporcional ao
  conteúdo** (faixas iguais dariam ao Ato 1 o mesmo peso do Ato 2, sugerindo
  equilíbrio que a obra não tem) e as **55 rotas que atravessam atos** em
  vermelho. **Mapa 3**: 85 entradas em serpentina, coloridas por parte,
  transições em vermelho, Epílogo em preto. **Achado maior que os mapas**: o
  **Índice de Fragmentos estava incompleto** — declarava 26 e 21 nas Partes 3 e 4
  mas listava 18 e 17; faltavam **11 fragmentos** (DOC-20 a DOC-27, LUC-13,
  LUC-14, MEM-27), quase os mesmos que o R400 achou sem rota de entrada. Aquele
  conteúdo entrou na obra e **não foi ligado a nenhum dos dois sistemas de
  navegação** — existia só para quem folheasse página a página. Os 11 inseridos
  com títulos reais lidos dos arquivos; índice agora **84/84**. O livro dizia
  **três números diferentes sobre si mesmo**, nenhum correto ("78 fragmentos" em
  7 lugares, "180 rotas" em 4, "71 FRAGMENTOS" num comentário): 15 ocorrências
  corrigidas nos 4 `main*.tex`. **Erro meu pego pelo preflight**: o Mapa 2 saiu
  em paisagem 2:1 e as inclusões só limitavam `height=` — `keepaspectratio` só
  funciona como esperado com **as duas** dimensões, então a largura cresceu livre
  e estourou a página xxvii (4 violações por edição). `tri/main_tri.tex` já usava
  o padrão certo no Mapa 1; as outras 11 inclusões não — as 12 foram alinhadas.
  Preflight: **`overall_internal_spec_passed=True`, 648/648 rotas, zero violações
  nas 5 edições**. Suíte **2726, 0 falhas**. Ver
  `specs/SPEC-935-R401-molambudos-mapas-e-indice.md`.
- **R400 (2026-08-04) — "todas as rotas levam para o epílogo" + "sem loops
  infinitos" + "não quero nenhum aberto":** o Epílogo era **inalcançável** —
  tinha âncora (`\fragdef{Epilogo}`, última entrada da ordem linear) mas
  **nenhuma rota apontava para ele** em nenhum idioma; o grafo tinha um
  sorvedouro de 48 fragmentos onde o leitor circulava sem nunca chegar ao fim.
  **Escolha levada ao autor**: grafo acíclico estrito custaria 85 das 192 rotas
  (−44%), justamente as remissões documento→memória, e contradiria a tese do
  livro ("O ciclo recomeça") — o autor optou por **garantir saída sempre**,
  preservando os ciclos. Epílogo recebeu o ID **`EPI-01`** (casa com o padrão do
  validador, então passa a ser auditado), com `\rota{EPI-01}` em 10 fragmentos
  terminais. **Armadilha**: renomear nos 3 `main*.tex` de idioma não bastou —
  `tri/main_tri.tex` ficou para trás, e como a trilíngue ancora cada fragmento
  sob 3 prefixos (`frag:`/`fragen:`/`fragzh:`), as rotas EN e ZH não resolviam:
  preflight acusou **618/648**, exatamente 30 faltantes. Foi o preflight que
  pegou, não a revisão manual. Depois, os **14 fragmentos sem rota de entrada**
  (DOC-17, DOC-20 a DOC-27, LUC-13, LUC-14, MEM-18, MEM-21, MEM-27 — o bloco
  DOC-20→DOC-26 órfão inteiro) receberam enlaces escolhidos por **motivação
  narrativa**: a cadeia do dossiê de 2026 em sequência (carta de Oliveira →
  memorando → ocorrência → conservação → identificação → mecanismo → a origem de
  1853), a espiral final de Lúcia (desaparecimento → gravação da noite →
  autoavaliação), *A Fila* → *A Última Página*. **Estado final**: 0 órfãos
  (eram 14), **84/84 alcançam o Epílogo** (eram 0), Epílogo sorvedouro (10
  entradas, 0 saídas), 6 ciclos preservados (maior: 58) com **0 aprisionantes**, 216 rotas,
  0 quebradas. Protocolo declara 216 rotas nos 3 idiomas com a promessa escrita.
  4 testes novos travam as propriedades. Preflight: **`overall_internal_spec_passed=True`,
  648/648 rotas, zero violações nas 5 edições**. Ver
  `specs/SPEC-935-R400-molambudos-convergencia-das-rotas.md`.
- **R399 (2026-08-04) — "já está pronto para publicação" → "prossiga em
  sequência" + "atualize o mapa de grafo das rotas":** o diagnóstico foi **não**,
  com 3 bloqueios. **(1) A capa não podia ser impressa com nenhum miolo**:
  painéis de 157,4×234,6mm contra miolo de 160×230mm, e lombada de 1,404in
  dimensionada para ~623 páginas contra miolos de 415 e 1115 — o template
  arquivado (`CASE_LAMINATE_6.000x9.000_471_PREMIUM_WHITE`) mostra que foi feita
  para capa dura 6×9in com 471 páginas. Pior: `capa_completa.pdf` **nunca
  renderizou** — `overlay` sem ancorar em `current page.south west` empurrava
  todo o conteúdo para fora da página; sobrava um retângulo escuro com uma tira
  no topo, desde julho, sem guarda nenhuma. Também descoberto que
  `main_kdp_print_160x230mm.tex` (raiz, PT) e `tri/main_kdp_print_160x230mm.tex`
  **colidem no mesmo basename** — o PDF na raiz era o build trilíngue. Criado
  `main_kdp_pt_160x230mm.tex` (jobname próprio): **433 páginas, trim medido
  160,0×230,0mm**. Nova `capa_completa_pt_160x230mm.tex` em **brochura** (a KDP
  não oferece 160×230mm em capa dura), geometria inteiramente derivada de 5
  parâmetros, lombada 25,81mm pela constante de impressão **em cor** —
  verificado que todas as páginas têm preenchimento sépia `#F2E8CF`. A arte tem
  proporção 0,6955 e o painel 160×230mm tem 0,6957: o formato pedido é o certo;
  o painel de capa dura (0,6710) é que a distorcia. **Não corrigido** (exige
  regeneração externa): arte a 163 DPI onde a KDP pede 300, e **código de barras
  fictício embutido** no `contracapa.png` com ISBN `978-65-01-23456-7` ≠ ISBN
  real — a reserva branca foi dimensionada para cobri-lo. **(2) O selo não
  provava nada**: declarava 74 fragmentos (reais 84), 359 páginas, hashes que não
  conferiam, e ninguém o gerava ou conferia. Novo `scripts/molambudos_selo.py`
  (`gerar`/`verificar`), algoritmo `merkle-sha256-v1` documentado no próprio JSON
  e campo `escopo` declarando o que ele **não** atesta. **Guarda provado**:
  alterar `MEM-01.tex` fez `verificar` sair 1 e o teste falhar; restaurado,
  voltou ao verde. **(3) O grafo de rotas** era PNG estático de 30/jul sem script
  de origem. Novo `scripts/molambudos_grafo_rotas.py` lê as `\rota{}` reais e
  regenera `grafo_narrativo.png`. Revelou: **1 componente conexo, 0 rotas
  quebradas, 0 becos**, hub DOC-01 com 20 entradas — mas **14 fragmentos sem
  rota de entrada**, inalcançáveis pela "Rota Hipertextual" do protocolo;
  verificado contra o backup pré-R397 que a condição é **anterior** a esta
  sessão. Registrada, não corrigida (arquitetura narrativa). **Bloqueio que
  permanece**: 10 fragmentos ainda divergem estruturalmente entre PT/EN/ZH.
  Testes: `test_r399` 8/8, conjunto Molambudos 57/57. Ver
  `specs/SPEC-935-R399-molambudos-preparacao-de-impressao.md`.
- **R398 (2026-08-04) — "polimento, 160×230mm, incoerências/redundâncias/loops"
  + "remova redundância e repetições" + "psiquiatra forense":** a redundância
  **não era autoral** — DOC-24/DOC-25/DOC-27 carregavam, colados após seu fim
  natural, cópias de cenas da Parte 4 (LUC-11; LUC-03+04+05; LUC-08+09). Prova
  de acidente: o trecho colado no DOC-24 abre com `úcia sabia que...`, o "L"
  comido no corte (mesmo padrão em LUC-08: `la marcou uma sessão`). Em ordem
  linear DOC-25 vem **16 fragmentos antes** de LUC-03, e LUC-03 era 94%
  idêntico ao já lido, LUC-05 89%, LUC-04 67% — a Parte 4, que é a aceleração
  da obra, virava reprise. **Descoberta que inverteu o plano**: a cauda colada
  era a versão *melhor* (as edições de prosa do R386 chegaram ao DOC-25 e nunca
  aos LUC: *"a **fome** não quer que eu conte"*, *"apodrece com ele por
  dentro"*, *"não respirava: era respirada"*). Migrada a versão polida para os
  LUC e truncados os documentos no fim real → **70 → 0 frases duplicadas**,
  perda zero verificada parágrafo a parágrafo nos 9 casos documento×idioma.
  **Erro cometido e corrigido**: o primeiro corte do DOC-27 varreu junto o
  registro clínico de julho (tem `itemize`), espalhando `\item` soltos e
  quebrando o build; restaurado e refeito. **Coerência factual**: Lúcia tinha
  **4 registros profissionais** diferentes e profissão oscilante — levado ao
  autor, que decidiu *psiquiatra forense*; 43 ocorrências alinhadas em PT/EN/ZH
  com `CRM-MG 28.391`, preservando as referências à Dra. Regina, que é
  psicóloga de fato. "Três meses depois" → "Sete meses depois" (Lúcia assina
  documento em 28/jul, é fotografada em 3/set e tem carta em 15/out). CRM de
  Oliveira alinhado entre edições. Cronologia central (1907→1917→62 anos→†1979
  aos 72→Colônia fecha 1980) **verificada íntegra e não alterada**. Árvore
  canônica `projetos/molambudos/fragmentos` sincronizada (34→0/84; 5
  divergências eram pré-existentes e ela era a cópia *mais velha*).
  **Consolidação das notas `\NE` implementada e REVERTIDA**: MEM-06/MEM-26
  estão sob cadeia de proveniência SHA-256 num artefato **selado** do R362
  (`external_validation`, `human_review_required`); fazê-la passar exigiria
  reescrever um `new_sha256` de outro ciclo — falsificar auditoria, o mesmo
  defeito que o R397 apontou no selo Merkle. Fica como ciclo próprio de
  re-baseline. `aviso_ao_leitor.tex` **mantida** (paratexto antes da ficção,
  custo zero de imersão; sustenta a distinção da ficção com Barbacena e a linha
  do CVV). Suíte **2706, 0 falhas**; preflight `overall_internal_spec_passed=True`,
  rotas 576/576. Paginação: PT 415, EN 411, ZH 387, tri 1061, KDP 160×230mm 1115.
  Ver `specs/SPEC-935-R398-molambudos-deduplicacao-e-coerencia-factual.md`.
- **R397 (2026-08-04) — "avalie o ecossistema corrigindo a obra literária":**
  avaliação feita **lendo a obra**, não a documentação sobre ela. Diagnóstico
  central: as 20 guardas existentes validam a camada *mecânica* (compila,
  geometria, aspas, datas, paridade de rotas) e **nenhuma** valida se o
  arquivo contradiz a si mesmo — que é o que quebra imersão num livro cujo
  dispositivo é um arquivo forense confiável. **4 defeitos reais corrigidos**:
  (1) **crítico** — CONT-04/CONT-05/DOC-09 chamavam o leitor de "paciente
  1.261", número que DOC-16 já dera ao Dr. Oliveira; na leitura linear o
  leitor via "O paciente 1.261 é você" (clímax, p.633) 42 páginas depois de
  "O paciente 1.261 sou eu" (p.585), e a "Rota do Terror" curada terminava
  no número errado. Cânone (LUC-12, DOC-24, CONT-09, Epílogo, `como_ler`,
  `ficha_paciente_1263`): leitor = **1.263**. 26 linhas corrigidas em PT/EN/ZH,
  preservando os 1.261 legítimos (Oliveira se identificando). (2) o protocolo
  mandava procurar "↪ Links:" mas os 84 fragmentos usam "↪ Rotas:/Routes:/路线:"
  — **divergência criada pelo próprio R389** desta sessão. (3) o livro contava
  a si mesmo errado: "78 fragmentos" (reais 84), "180 rotas" (reais 192), "três
  formas distintas" seguido de 4 itens. (4) **147 grupos LaTeX vazados** em 8
  arquivos (`\textquotedblleft{` que devia ser `{}`), compensados despejando
  até 52 chaves numa linha no EOF: o saldo dava 0, o auditor passava, e o PDF
  renderizava com ênfase alternando errado até o fim do fragmento — a guarda
  media o **proxy** (saldo líquido) em vez da **propriedade** (cada grupo fecha
  onde abre). **Guarda nova**: `tests/test_r397_molambudos_coerencia_diegetica.py`,
  28 testes em 4 eixos (cadeia de pacientes, protocolo×realidade, autocontagem,
  integridade de grupos) — pegou um erro meu durante a implementação (85 vs 84:
  o 85º `\fragdef` é o `Epilogo`, capítulo inline). **Documentado e NÃO
  corrigido** (decisão autoral, não mecânica): as 3 edições divergem
  estruturalmente em 12 fragmentos (DOC-25 ZH tem 395 linhas vs 236 PT/EN;
  CONT-05 ZH tem 63 vs 163) — maior obstáculo restante à alegação de "obra de
  referência internacional"; as `\NE{}` de CONT-03/CONT-04 desinflam a indução
  no pico (sugerida realocação para "Nota Clínica" ao final); o selo
  `SELO_INTEGRIDADE_MERKLE.json` declara 74 fragmentos e hashes que não
  conferem, e **nada no ecossistema o confere ou regenera**; e o corpus inteiro
  (302 `.tex`) está sob `.gitignore` — zero commits, sem histórico nem rollback
  (por isso o backup manual em `_archive/backup_R397_pre_coerencia_diegetica/`).
  Ver `specs/SPEC-935-R397-molambudos-coerencia-diegetica.md`.
- **R396 (2026-08-04) — "faça e atualize o readme,md e suas arquiteturas":**
  documentação pura, sem mudança de código. `README.md`: badges (versão
  3.7.0→3.8.0, testes 2695→2750, ciclos 199→212, specs 223→237), novo
  "Act VIII" narrativo (R382–R395), nova seção técnica "16. Auditoria Real
  dos Três CLIs Externos e do Daemon Local (R391–R395)", contagem de
  placeholders corrigida (57→56) e bloco de estatísticas do rodapé
  atualizado. `ARCHITECTURE.md`: cabeçalho/intro atualizados para v3.8 e
  nova seção final com 2 diagramas mermaid (cabeça `load` do
  AttentionRouter; ciclo de vida do spawn do supervisor LiteRT-LM) e
  tabelas das correções reais nas pontes de CLI (Antigravity bridge,
  cli_ecosystem_bridge, scanners/pipeline, /pypi) e specs do bloco
  R391–R395. Tabela histórica "Métricas de Maturidade" (v3.0.0 vs v3.2.0)
  deliberadamente não reescrita — snapshot congelado de um marco anterior,
  fora de escopo. Ver ciclo de evolução R396 em `evolution/cycles.json`.
- **R395 (2026-08-03) — "corrija" (as 2 limitações do R394):** investigação
  real revelou que o LiteRT-LM, documentado como "offline" há vários
  ciclos, tinha na verdade um processo **vivo desde 24 de julho** (11+
  dias) — travado, não offline: aceitava conexão TCP e nunca respondia
  na camada HTTP. O supervisor detectava corretamente a não-resposta e
  acumulava `failure_count` (chegou a 41), mas nunca encerrava o zumbi.
  **Ação imediata**: processo encerrado, daemon novo e saudável
  confirmado com inferência real (chat completion coerente em
  português) e `doctor` mudando de `warn` para `pass`. **Bug real de
  diagnóstico corrigido**: `_spawn_locked()` descartava `stdout`/`stderr`
  do processo filho (`DEVNULL`) — quando o `litert-lm` morre logo após o
  spawn (ex.: `Address already in use`, reproduzido ao vivo), essa
  mensagem real era perdida, forçando reprodução manual fora do
  supervisor para diagnosticar. Corrigido: novo `SupervisorConfig.
  log_path`, spawn redireciona para arquivo real; `litert-lm-start.sh
  --log` agora mostra esse log quando não há unidade systemd. TDD
  (RED→GREEN), 19/19 no arquivo do supervisor. **Limitação restante
  documentada, não escondida**: cold-start do modelo padrão (2.4GB) ainda
  excede 120s neste hardware sem GPU — não é mais travamento permanente,
  mas continua lento; trocar o modelo padrão é decisão editorial, fora
  de escopo. Subagentes continuam não invocáveis via `opencode run
  --agent <nome>` — comportamento do binário externo, não controlável
  por este código. Suíte completa: **2694 aprovados (+1), 0 falhas**. Ver
  `specs/SPEC-935-R395-litert-lm-zombie-daemon-and-diagnostics.md`.
- **R394 (2026-08-03) — "revise o opencode cli":** testado com o binário
  real (`opencode` v1.18.11), não só lendo código, no mesmo espírito da
  auditoria do R393. **Confirmado funcional**: `agent list` carrega 216
  agentes reais; `mcp list` conecta 6/6 servers; `providers list` mostra
  5 credenciais reais; `run --agent X --model opencode/claude-sonnet-5`
  retornou um erro real e específico (`Insufficient balance`) em vez de
  travar — prova que a integração é genuína até a fronteira da chamada de
  API. **2 bugs reais achados e corrigidos**: (1) `scanners/pipeline.py`
  usava `ReversaScanner` sem importá-lo — mesma classe de bug do
  `EpistemicPrioritizer` (R391) — todo `/diagnose` real reportava um
  `NameError` disfarçado de resultado de scanner; (2) o template do
  `/pypi` chamava `search('*', limit=5)` como fallback de argumento
  vazio, mas a busca não trata `'*'` como coringa — `/pypi` sem argumento
  (a invocação mais simples) sempre retornava zero resultados, sem erro
  nem aviso. Corrigido para imprimir instrução de uso em vez de rodar
  busca que sabidamente não retorna nada. **Limitações operacionais reais
  documentadas, não escondidas**: modelo padrão do `opencode.json` aponta
  para o daemon LiteRT-LM offline (qualquer `opencode run` sem `--model`
  explícito trava neste ambiente); subagentes do catálogo não são
  invocáveis diretamente via `opencode run --agent <nome>` — o binário
  real cai de volta para o agente primário `build` (comportamento do
  próprio CLI externo). Novo teste genérico que executa o comando shell
  real de cada uma das 9 entradas do `opencode.json` — teria pego os 2
  bugs automaticamente. Suíte completa: **2693 aprovados (+11), 0
  falhas**. Ver `specs/SPEC-935-R394-opencode-cli-real-audit.md`.
- **R393 (2026-08-03) — "todos estão funcional nos cli (opencode,
  antigravity, claude)?":** testados os 3 binários reais instalados
  (`opencode` v1.18.11, `agy` v1.1.8, `claude`). **OpenCode CLI: funciona
  de verdade** — carrega 216 agentes reais, inclusive a correção de
  permissão do `contextscout` (R391) propagada corretamente. **Antigravity:
  2 bugs reais achados e corrigidos.** `AntigravityBridge.delegate()`
  montava `agy run --agent X --prompt Y` — o binário real não tem
  subcomando `run` nem essa flag; a sintaxe real é `--agent`/`--print`/
  `--output-format`. Pior: o erro resultante (`bubbletea: error opening
  TTY`) saía com `returncode == 0`, e `delegate()` só checava o código de
  saída — **toda delegação, sempre, reportava sucesso mesmo não tendo
  feito nada**. Corrigido: sintaxe real + detecção de prefixos de erro
  conhecidos mesmo com `returncode == 0`. Também corrigido
  `cli_ecosystem_bridge.py`: `antigravity_cli.active` checava a
  existência de `AGENTS.md` (que é documentação do *OpenCode* CLI, não
  tem relação com Antigravity) — trocado por `shutil.which("agy")`; e
  `get_unified_status()` retornava `"fully_synchronized"` como **string
  fixa**, independente de qualquer verificação — agora é computado de
  verdade. Verificação end-to-end real (não só mock): delegação via `agy`
  completou com resposta real de modelo. **Lacuna documentada, não
  escondida**: `agy agents` continua sem nenhum dos 205+ agentes do
  catálogo — corrigir a sintaxe não resolveu essa integração mais
  profunda; Claude Code CLI também segue sem `.claude/agents/`. Suíte
  completa: **2682 aprovados (+8), 0 falhas**. Ver
  `specs/SPEC-935-R393-antigravity-bridge-real-cli-syntax.md`.
- **R392 (2026-08-03) — "funciona com uma rede transformer sem ser uma
  cascata vazia?" → "tem como implementa?":** investigação ao vivo
  (`AttentionRouter.explain()` sobre os 210 agentes reais do Blackboard)
  confirmou 3 das 4 cabeças com sinal real e diferenciado (`confidence` com
  20 valores distintos reais, `semantic` escolhendo corretamente o agente
  certo para uma tarefa KDP de teste) — mas a cabeça `load` (10% do peso)
  retornava **1.0 para os 210 agentes, sempre, sem exceção**. Causa raiz:
  `AgentCard.to_dict()` nunca publicava a chave `load`; o default silencioso
  de `_head_load()` mascarava a ausência. **Descartei a correção óbvia**
  (usar status busy/available) porque o `AttentionRouter` já exclui
  agentes ocupados nos hard gates *antes* da pontuação — um sinal binário
  não diferenciaria nada entre os candidatos elegíveis (todos já
  disponíveis por construção). Implementado `_live_load()`: carga real
  contada a partir de tarefas de fato atribuídas no Blackboard, normalizada
  em `[0, 1]`. TDD (RED→GREEN), verificado também com o orquestrador real
  (atribuí 4 tarefas reais a um agente ao vivo — `load` foi de `1.0`
  idêntico para todos a `0.8` vs `0.0`, diferenciando de verdade). Suíte
  completa: **2674 aprovados (+2), 0 falhas** — zero regressão. Ver
  `specs/SPEC-935-R392-attention-router-real-load-head.md`.
- **R391 (2026-08-03) — "liste as 31 falhas e corrija":** cada falha
  investigada individualmente antes de corrigir (bug real vs. teste
  desatualizado por evolução legítima vs. overclaim histórico já
  documentado — nunca uma heurística única para as 31). **Bug real mais
  sério encontrado**: `marceloclaro/catalog_loader.py` sempre derivava
  `agent_id` de `name:` (frequentemente Title Case, ex. "KDP Orchestrator
  PhD"), **ignorando** um `agent_id:` explícito no frontmatter — afetava
  qualquer card cujo `name:` não fosse já um slug, em produção, não só em
  teste. Também real: `contextscout.md` tinha dois blocos de frontmatter
  empilhados (um placeholder cobrindo o card real com `permission:
  write/edit: deny` — a negação real nunca chegava ao `opencode.json`);
  `scanners/pipeline.py` usava `EpistemicPrioritizer` sem import
  (`NameError` em runtime); 7 agentes `kdp-*-phd.md` sem `model:`/`tools:`
  exigidos pela SPEC-935-R262; 8 `literary-*-phd.md` sem menção a SDD
  exigida pela R268; Molambudos `DOC-08.tex` sem o diagnóstico
  diferencial de Pelagra/CID-11 6D50 pedido pela R238 (perdido numa
  reescrita); `capa_frontal.tex/.pdf` (R242) nunca criado. **Testes
  corrigidos por evolução legítima** (não os fatos): nota do Arquivista em
  `CONT-01` sobre fragmentos "destruídos" que hoje existem de verdade
  (R376/R377); valores tipográficos específicos da R239/R240 superados
  por recalibração posterior já verificada funcional (R389/R390).
  **Overclaim histórico respeitado, não desfeito**: `ficha_estudo_critico.
  tex/.pdf` (R266/R267) já documentado como nunca implementado em
  `test_r265_r279_spec_deliverables.py` — alinhei os 2 testes ao mesmo
  padrão de skip honesto em vez de fabricar um estudo crítico às pressas.
  **Erro cometido e corrigido, com transparência**: um `find` falhou por
  indisponibilidade temporária do classificador de segurança do Bash; eu
  prossegui sem confirmar o resultado e sobrescrevi
  `literary-image-sepia.md` (que já existia, mais rico) — pego pela
  própria suíte completa (regressão em `test_r380`), revertido via `git
  checkout`. Resultado: **0 falhas, 2672 aprovados, 56 pulados** (era 31
  falhas / 2644 aprovados / 53 pulados). Ver
  `specs/SPEC-935-R391-pre-existing-suite-failures-triage.md`.
- **R390 (2026-08-03) — "os scanners fizeram as análises?" → "quero o
  livro inteiro" → "corrija para deixar 100/100":** medir o livro
  inteiro como um blob único (via `pdftotext` do `main.pdf`) satura o
  scanner literário em 100/100 em quase todas as dimensões — artefato
  de escala, não sinal real (mesmo padrão já presente no relatório
  R270, anterior a esta sessão). Corrigido escaneando os 84 fragmentos
  individualmente e agregando — sinal real e diferenciado. Pedido do
  usuário de "otimizar até 100/100" **recusado como objetivo literal**
  (Goodhart's law + registro apropriado varia por tipo de fragmento);
  ofereci e o usuário aceitou via `AskUserQuestion` a alternativa:
  edição editorial nos fragmentos genuinamente fracos. De 27 candidatos
  estatisticamente fracos, só **12 receberam edição real** após leitura
  humana individual — os outros 15 foram deixados intocados de
  propósito (11 já eram excelentes, falso negativo do scanner; `DOC-18`
  por razão ética, genérico de propósito sobre um campo de concentração
  histórico real; `DOC-17`/`MEM-26` por trava de proveniência). Média
  do livro: excelência literária 44.63→45.34, imersão psicológica
  31.53→32.55 — movimento pequeno e honesto (nunca 100/100), com 2
  quedas pequenas mantidas sem forçar correção. Recompilação completa
  após o pass: `overall_internal_spec_passed: true`, rotas
  PT=EN=ZH=192, zero violação de layout, zero regressão na suíte
  completa (31 falhas pré-existentes, mesmo conjunto do R389). Ver
  `specs/SPEC-935-R390-molambudos-scanner-guided-editorial-pass.md`.
- **R389 (2026-08-03) — "prepare a obra trilíngue pronta para publicação
  literária, prossiga":** primeira vez que o pipeline `scripts/audit_r362_
  pdf_layout.py --build` rodou de fim a fim desde as edições de prosa dos
  ciclos R386/R387/R388 — nenhum dos 5 PDFs publicados refletia o texto
  atual até este ciclo. Revelou **3 bugs reais de compilação nunca antes
  detectados**: (1) glifo Unicode `╳` (U+2573) em `MEM-27.tex` travava
  pdfLaTeX com erro fatal (PT) e desaparecia silenciosamente sob XeLaTeX
  (edição `tri`) — corrigido para `$\times$` no fragmento e no gerador
  `build_miolo.py`; (2) 5 tabelas de 2 colunas sem quebra de linha
  (`CONT-03`, `LUC-Escolha`, `CONT-07` PT/EN/ZH) estouravam a página —
  novo ambiente `moltabletwo` criado seguindo o precedente já
  estabelecido (`moltablethree/four/five/six`); (3) **12 fragmentos PT**
  (`CONT-03/05/06/07/08/09/10/11/12/13`, `MEM-27`, `LUC-Escolha`) usavam
  links de navegação em texto puro em vez do macro `\rota{}` — o leitor
  de PT perdia hyperlink clicável + número de página nessas 12 passagens
  (EN/ZH já corretos), e o pipeline de auditoria as contava como
  inexistentes (PT=167 rotas vs EN=ZH=192). Corrigido preservando os
  alvos de rota já existentes em cada arquivo PT (não copiados do EN).
  **Incidente transparente durante a correção**: uma primeira tentativa
  via `re.sub()` com `\n`/`\t`/`\r` literais na substituição corrompeu os
  12 arquivos (bug clássico do Python) — detectado imediatamente pelo
  mesmo verificador de balanceamento de chaves do R358, corrigido antes
  de prosseguir. Mesmo padrão de número mágico do R358 (contagem de
  fragmentos) reapareceu na contagem de rotas — trocado por invariante
  de paridade entre idiomas. Duplicidade de build
  `main_kdp_print_160x230mm.pdf` (raiz vs `tri/`, órfão de ciclo
  anterior) resolvida via recompilação completa + limpeza do artefato
  órfão. Resultado: **`overall_internal_spec_passed: true`** no
  preflight R362 (5 edições, 2 passadas, 0 erros, 0 violações de
  layout); `test_r362` 16/16, `test_r384` 9/9; suíte completa sem nova
  regressão. `release_gate` continua `"blocked"` por design — prontidão
  **técnica**, não editorial/histórica/de publicação. Ver
  `specs/SPEC-935-R389-molambudos-trilingual-build-readiness.md`.
- **R388 (2026-08-03) — "corrija e limpe para não ter dualidades":**
  levantamento completo (74 fragmentos, não amostra) mostrou 31 com
  divergência de conteúdo real entre `molambudos.md` (fonte nominal
  desde o R376) e o `.tex` publicado. **Achado que mudou o plano**: não
  era "notas a mais no `.tex`" — era reescrita real de cena (CONT-04:
  "Noite 3" inteira reestruturada; MEM-02: morte do pai reescrita para
  ficar mais ambígua), correção geográfica dos ciclos R374/R375 nunca
  propagada (MEM-04/02: "sertão de Quixeramobim" → "rota de Senador
  Pompeu a Fortaleza"), cenas inteiras novas só no `.tex` (MEM-05: a
  coruja; MEM-10: o enfermeiro e o menino), e **3 correções
  anti-overclaim reais** (DOC-02/17/07/18: o `.tex` já havia trocado
  alegações que soavam como documento histórico genuíno por linguagem
  que deixa claro ser reconstituição ficcional — nunca propagado ao
  `.md`). Perguntei ao usuário a direção da correção antes de agir
  (`.tex`→`.md`, direção oposta ao esperado, dado que o `.tex` está mais
  maduro); escolheu transcrever tudo. 26 fragmentos sincronizados,
  verificados individualmente por regeneração+comparação de palavras
  (zero divergência real restante). Nenhum `.tex` tocado — proveniência
  R360/R361/R362 inteiramente não afetada (verificado). Exceções
  estruturais (fotos/figuras em LUC-02/04/12, DOC-03/09) documentadas,
  não ignoradas. Zero regressão (34 falhas, idêntico ao baseline
  pós-R386). Ver `specs/SPEC-935-R388-molambudos-md-tex-content-sync.md`.
- **R387 (2026-08-03) — continuação do R386 ("prossiga"):** mesmas 3
  técnicas aplicadas a mais 3 fragmentos curtos com baixa densidade
  sensorial (CONT-10, CONT-11, CONT-13), mesma disciplina de verificação
  prévia de proveniência + backup manual. Melhoria mensurável em todos
  (ex.: `sensory_immersion` 7.96→50.22 em CONT-11). **Achado
  metodológico transparente**: `molambudos.md` (fonte) e o corpus `.tex`
  real divergem (edições de prosa vão direto no `.tex`, seguindo
  precedente do R384) — não fabriquei um número único de "livro inteiro
  antes/depois" porque os dois corpora não são comparáveis diretamente;
  o comparativo confiável é por fragmento, mesmo tipo de arquivo.
  Zero regressão (18/18 `test_r385`, proveniência limpa). Ver
  `specs/SPEC-935-R387-prose-enhancement-batch-2.md`.
- **R386 (2026-08-03) — as duas pendências do R385 resolvidas em
  sequência, a pedido do usuário:** (b) infraestrutura: 6 testes
  (R270,271,273,274,275,276) corrigidos para apontar para
  `_archive/relatorios/` (arquivamento em lote deliberado de 2026-07-30,
  respeitado, não desfeito); 9 cards `agents/catalog/literary-*.md`
  restaurados (`name:` para slug exato, `temperature:`, seção "Contrato
  de Saída Obrigatório" + "Guarda Anti-Overclaim" referenciando os
  scanners Python reais); `opencode.json` regenerado, corrigindo 2
  falhas pré-existentes não relacionadas como efeito colateral honesto.
  Resultado: **30/30 testes das 7 suítes R270-R276 passam** (eram 27
  falhas). (a) prosa: verificado programaticamente que nenhum fragmento
  `CONT-*` está travado por hash de proveniência (só DOC-17/LUC-01/
  MEM-06/MEM-12/MEM-26, já tratado); backup manual criado; edições
  cirúrgicas em CONT-01 e CONT-02 (cruzamento sensorial + comandos
  diretos de 2ª pessoa), medidas antes/depois com os scanners
  (`sensory_immersion` sobe 25.56→61.06 em CONT-01). **Bug real
  encontrado na própria validação** (não escondido): o scanner de
  manipulação psicológica não detectava imperativo no início de
  parágrafo (parágrafos LaTeX começam com `\noindent`, não pontuação) —
  bug sistemático, corrigido com teste de regressão; recontagem real no
  livro inteiro sobe de 22 para 28 ocorrências. Suíte completa: **34
  falhas (era 64), zero regressão nova, 30 corrigidas**. Ver
  `specs/SPEC-935-R386-literary-agents-contract-restore-and-prose-enhancement.md`.
- **R385 (2026-08-03) — diagnóstico literário de Molambudos + ferramentas
  novas:** pedido do usuário para revisar a obra com scanners e avaliar se
  é "hipnótica, terror psicológico visceral e frenético, imersiva,
  sensorial" com "mentalismo e indução". Reconhecimento (agente Explore)
  confirmou: os 8 scanners existentes (`scanners/literary_scanners.py`)
  não medem indução, dinâmica de ritmo, densidade sensorial detalhada ou
  manipulação narrativa — o único artefato que promete isso
  (`literary-neurolinguistic-engineering-phd.md`) é só prompt de LLM, sem
  código. Usuário pediu para melhorar os scanners e criar novos. Feito:
  novo módulo `scanners/psychological_immersion_scanners.py` (4 scanners:
  indução hipnótica, ritmo frenético dinâmico, imersão sensorial,
  manipulação psicológica narrativa); correção metodológica em
  `StyleVoiceScanner.riqueza_lexical` (TTR global → MSTTR, corrigindo
  penalização injusta de textos longos — `molambudos.md` subiu de 30.27
  "frágil" para 100.0); achado e correção de recall (`dupla_vinculacao`
  dava 0 apesar de texto real com dupla vinculação inequívoca — regex
  complementar corrigiu). 17 testes TDD novos, zero regressão (64 falhas
  / 2610 aprovados / 53 pulados, idêntico ao baseline). Ver
  `specs/SPEC-935-R385-psychological-immersion-scanners.md`.
- **Diagnóstico rodado sobre `molambudos.md` (244.801 caracteres, ~40k
  palavras):** suíte literária 99.38/100 "excelente"; suíte de imersão
  psicológica (nova) 59.81/100 "consistente" (indução hipnótica 81.32
  "forte", ritmo frenético 66.78 "consistente", imersão sensorial 47.67
  "emergente", manipulação psicológica 43.48 "emergente"). Revisão
  qualitativa completa entregue ao usuário na conversa (não persistida
  como arquivo — refazer chamando as 3 funções de scanner se precisar
  reproduzir).
- **Achado de infraestrutura do R385, resolvido no R386 (ver acima):**
  relatórios R270-R276 movidos + 9 cards `literary-*.md` com contrato
  perdido — ambos corrigidos.
- **R384 (2026-08-03) — o achado "fora de escopo" do R383, resolvido a
  pedido do usuário ("prossiga"):** antes de regenerar, verifiquei em
  memória e descobri que a divergência era **maior** do que eu tinha
  comunicado — não era só o epílogo cortado, era um `.tex` publicado
  desatualizado em relação a uma revisão bem mais extensa do
  `molambudos.md` (`CONT-03` ganhou 65 palavras novas; `MEM-27` foi de
  43→61 linhas; `LUC-Escolha` de 69→86). Reportei o achado maior ao
  usuário antes de agir. Achado adicional, na direção oposta: o `.tex`
  publicado tinha **2 notas editoriais** (`\NE{...}` em `CONT-03` e
  `MEM-27`) e **1 parágrafo narrativo inteiro** em `LUC-Escolha` ("havia
  uma quarta opção...") que **nunca existiram no `.md`** — confirmado
  via `grep`. Perguntei ao usuário como proceder (3 opções); escolheu
  regenerar preservando esse conteúdo. Feito: backup manual, regeneração
  dos 3, reinserção manual das notas/parágrafo na posição exata (com
  âncora de texto verificada, não offset fixo), zero palavras reais
  perdidas (só artefatos cosméticos de macro LaTeX). 9 testes TDD. As 3
  cadeias de proveniência (R360/R361/R362) reverificadas
  programaticamente: zero problemas. Suíte completa: 64 falhas / 2593
  aprovados / 53 pulados — idêntica ao baseline, zero regressão nova. Ver
  `specs/SPEC-935-R384-molambudos-extend-regen-cont03-mem27-luc-escolha.md`.
  **Pendência Molambudos agora fechada** — os 3 arquivos originais
  (`CORRIGENDUM.md`, `clean_headers_and_lettrines.py`,
  `regenerate_vic_cont_r376.py`) e os 3 fragmentos com gap de conteúdo
  estão todos resolvidos e commitados.
- **R383 (2026-08-03) — os 3 arquivos pendentes da frente Molambudos
  (`CORRIGENDUM.md`, `scripts/clean_headers_and_lettrines.py`,
  `scripts/regenerate_vic_cont_r376.py`) finalmente resolvidos, a pedido
  explícito do usuário:** antes de executar qualquer coisa, verifiquei o
  regenerador comparando sua saída em memória (sem sobrescrever nada)
  contra os fragmentos já commitados — achei que minha primeira hipótese
  ("alguém editou manualmente depois da geração") **estava errada**: o
  parser real `scripts/build_miolo.py::extract_fragment_content()` corta
  todo o conteúdo na primeira linha `"↪ Links:"`, um bug real que já
  apagava silenciosamente o epílogo de **4 fragmentos** (`CONT-03`,
  `CONT-07`, `MEM-27`, `LUC-Escolha`) — 3 deles **já estavam sem esse
  conteúdo no `.tex` publicado**, há tempos (achado à parte, fora de
  escopo, ver abaixo). Corrigido `extract_fragment_content()` (preserva
  conteúdo pós-Links quando ele existe de verdade), com 6 testes TDD.
  Após o usuário confirmar explicitamente que queria "rodar os dois
  scripts e commitar tudo" mesmo sabendo do risco, executei de verdade:
  regenerador (`CONT-05..13`, 8/9 idênticos, `CONT-07` recupera o
  epílogo) e `clean_headers_and_lettrines.py` (84 fragmentos, zero
  palavras perdidas, verificado por comparação contra backup manual —
  `projetos/` está inteiramente no `.gitignore`, sem rede de segurança
  do git, então criei um backup manual real antes de escrever).
  **Regressão real encontrada e corrigida durante a validação**: 5
  arquivos (`DOC-17.tex`, `MEM-06.tex` — manifesto R362; `MEM-12.tex`,
  `LUC-01.tex`, `MEM-26.tex` — dossiê R360, sem entrada em nenhum
  manifesto de drift) quebravam cadeias de proveniência imutáveis de
  ciclos já fechados; restaurados do backup. As 3 cadeias
  (R360→R361→R362) verificadas programaticamente: zero problemas.
  Conjunto de falhas Molambudos idêntico ao baseline do R382. Ver
  `specs/SPEC-935-R383-molambudos-build-miolo-links-epilogue-fix.md`.
- **R382 (2026-08-03) — causa raiz achada e corrigida (não era o daemon, era o código):** o achado colateral do R381 (`TestIntegration` travando) foi investigado a fundo por bissecção: `QualityChecker` **nunca soube de `dry_run`** e sempre tentava reescrever via rede real (`LiteRTMClient.chat`, até 3 tentativas × 120s) quando o conteúdo simulado do dry-run reprovava nos critérios semânticos — o que acontece quase sempre. Sem o daemon LiteRT-LM respondendo, cada bloco travava até o timeout de conexão; com 30 blocos, a suíte travava por dezenas de minutos. Corrigido: `QualityChecker(dry_run=...)` propagado de `NanoOrchestrator`, `rewrite_block()` retorna `None` imediatamente em dry-run sem nunca abrir socket. Também corrigido `tests/test_r237_diagrams_repair.py` (esperava `"v3.6.0"` no README, que já fora atualizado para `v3.7.0` num commit anterior a esta sessão — teste desatualizado, não o README). **Resultado medido:** `test_nano_orchestration.py` 76/76 em 1.27s (antes: nunca terminava); suíte completa **343s, 64 falhas / 2578 aprovados / 53 pulados, zero `--deselect`** (antes: precisava excluir 3 testes manualmente ou não terminava dentro de 1500s). Ver `specs/SPEC-935-R382-nano-orchestration-dry-run-hang-fix.md`.
- **Pós-R381 (2026-08-03) — nomenclatura + documentação:** durante a
  atualização do README, achei que a chave de estágio `r106_rigor` colidia
  com `specs/SPEC-935-R106.md` (CI/CD Pipeline + Quality Gates, spec real
  não relacionado). Renomeada para `r381` em código/teste/spec/PROGRESS/
  evolution (17/17 testes verdes após o rename). Em seguida, README.md
  ganhou o Ato VII (R370-R381) e a Seção 15 (integração R381), diagrama
  de arquitetura atualizado com a aresta real `Composer -> EP7
  (ProductionScaffolds)` — antes ausente até no próprio diagrama —, e
  todos os números obsoletos corrigidos para o estado medido agora (198
  ciclos, 2.695 testes, 222 specs, 129/205 episteme). CHANGELOG.md ganhou
  a entrada [2.5.0] cobrindo R370-R381 (nunca haviam sido registrados lá).
  4 diagramas Mermaid validados via `mmdc` real. Pushed: commits `71c4ec3`
  (R381), `0c64cd0` (rename), `713c918` (docs).
- **R381 (2026-08-02) — unificação real, não apenas testes isolados:** ao
  investigar se as camadas R363-R373 estão de fato conectadas ao orquestrador
  principal (pedido do usuário: "unifique... sendo um ecossistema metacognitivo
  superior"), confirmei que a Camada Epistêmica (R363) já está viva via
  `AttentionRouter.semantic_matcher`, mas `scientific_discovery_pipeline()`
  **nunca chamava** `audit_scientific_manuscript()` (R369) apesar do R105 já
  produzir `sections: Dict[str,str]` real no formato exato esperado pelo
  auditor. Corrigido: novo estágio `r381`, consultivo (não bloqueia,
  como R104d/R105), com calibração de confiança + traço metacognitivo no
  mesmo padrão dos demais estágios, e novo campo de conveniência
  `result["manuscript_rigor_gate"]`. **Fora de escopo, documentado, não
  fabricado:** R370 (estatística), R371 (triangulação) e R372 (pré-registro)
  continuam opt-in via `OrchestratorReviewer` — exigem dados brutos que só o
  chamador tem; candidatos a R382+ se houver caso de uso real. Ver
  `specs/SPEC-935-R381-manuscript-rigor-gate-integration.md` (7 critérios de
  aceitação) e `tests/test_r381_manuscript_rigor_gate_integration.py` (7
  testes, TDD real, GREEN). Zero regressão: `test_r108` 10/10, `doctor`
  12/12 sem falha nova.
- **Achado colateral do R381, resolvido no R382:** `tests/
  test_nano_orchestration.py::TestIntegration` travava indefinidamente
  (documentado como "não é regressão, precisa de triagem futura" no R381).
  Causa raiz achada e corrigida no R382 (ver acima) — não era o daemon
  LiteRT-LM em si, era `QualityChecker` chamando rede real sem checar
  `dry_run`.
- **⚠️ Concorrência real detectada (2026-08-02):** durante o R380, encontrei
  `evolution/cycles.json` já contendo ciclos R374–R379 de uma **frente
  concorrente trabalhando ao vivo no mesmo checkout** (Molambudos:
  `projetos/molambudos`, `scripts/clean_headers_and_lettrines.py`,
  `scripts/regenerate_vic_cont_r376.py`, `CORRIGENDUM.md` — todos
  modificados/criados, não commitados). Meu primeiro append como "R374"
  foi perdido (sobrescrito pelo `save()` completo da outra sessão).
  Renomeei meu ciclo para **R380** (spec, teste, provenance notes) e
  **não toquei nos arquivos da frente Molambudos** (deixados como
  encontrados — trabalho em andamento de outra sessão). Se você estiver
  coordenando as duas frentes: os arquivos do Molambudos seguem
  pendentes de commit por aquela sessão, não pela desta.
- **R380 (2026-08-02):** 46 agentes MASWOS (00–53) enriquecidos —
  description placeholder + corpo apontando para caminho externo
  inexistente, substituídos por conteúdo real (missão, entradas, saídas,
  workflow) portado de `~/OpenCode_Ecosystem-main/OpenCode_Ecosystem-main/
  criador-artigo/agents/` (repositório-fonte confirmado, nunca fabricado).
  187 testes de regressão verdes. README Seção 6.1 atualizada: 103→57
  registros com placeholder restante (família `reversa-*` com fonte já
  localizada mas não portada, `auxjuris_*`, ferramental genérico, médicos
  — candidatos a R381+).
- **Suíte completa pós-sync (2026-08-02, 5h05m):** 61 falhas, 2387 aprovados, 53
  pulados. **Zero regressão dos ciclos R363-R373** (206 testes próprios rodados
  isolados = 100% verde). As 61 falhas são pré-existentes, expostas pela
  primeira vez porque esta foi a 1ª suíte completa desde o commit `47821bb`
  (sync de 309 arquivos de outras frentes: literária, KDP, Molambudos).
  Diagnosticadas 4 amostras para confirmar o padrão antes de concluir:
  `test_r213_notebook.py` (notebook com célula sem import, de R219, não-meu),
  `test_auxjuris_integration.py` (mesmo bug já isolado por bisseção no R363),
  `test_r262_kdp_agents.py` (cards KDP do sync, nunca testados),
  `test_deep_diagnose.py` (`NameError: EpistemicPrioritizer` num scanner).
  Lista completa dos 28 arquivos afetados no log de
  `/tmp/.../tasks/bfh1lg1hd.output` (efêmero — recapturar rodando a suíte de
  novo se precisar). **Pendência para quem pegar a frente literária/KDP/
  Molambudos**: essas ~61 falhas precisam de triagem própria; não são bloqueio
  para o trabalho de infraestrutura (R363-R373) que está fechado e testado.
- **Diagramas Mermaid (2026-08-02):** paleta de 7 cores real (classDef/class)
  nos diagramas 1/2/4, blocos `rect` RED/GREEN no diagrama 3 (sequência),
  validados renderizando de verdade com `@mermaid-js/mermaid-cli` (zero erro
  de sintaxe). Números obsoletos corrigidos (33→66+ SPECs, 65→190+ ciclos).
- **Auditoria de referências (2026-08-02):** manuscrito reformatado para ABNT
  NBR 6023:2018/10520 (citação autor-data no corpo, lista alfabética). As 53
  referências verificadas individualmente via WebFetch/busca: 19 ativas
  sem alteração, 20 corrigidas (link morto/redirecionado/genérico demais),
  12 não verificáveis por bloqueio anti-bot (IBGE/Gartner/IMF/ONU — não
  necessariamente mortas), 2 monografias sem URL. **Erros factuais reais
  corrigidos**: DOI errado (Gakidou), 2 anos de publicação errados (Banco
  Mundial "Um Ajuste Justo" 2021→2017; Veloso FGV/IBRE 2020→2013), 1
  referência trocada por ser genérica demais (Nature Index → arXiv
  2404.01268). Relatório completo:
  `validacao_externa/manuscrito_armadilha_renda_media/relatorio_validacao_pipeline.md`
  (seção 6). DOCX/PDF recompilados (14 páginas). Nota honesta preservada:
  "Qualis A1" é classificação do periódico, não do manuscrito — não
  certificável por software.
  **Achado residual não corrigido no código**: o léxico de novidade do R369
  (`_NOVELTY_PRIORITY_PHRASES`) ainda tem ambiguidade em "a primeira a"
  (ordinal vs. alegação de prioridade) — candidato a refinamento futuro
  (exigir verbo logo após a frase).
- **R373 (2026-08-02):** validação real (não sintética) dos gates R369-R372 sobre
  manuscrito USP construído a partir de dossiê existente (53 refs, 7 correlações
  reais) — `academic/papers/manuscrito_educacao_armadilha_renda_media_usp.md`.
  Achados e correções:
  - BUG REAL: R369 tinha falso positivo ("primeiro/primeira" bruto disparava em
    "primeiras diferenças", termo econométrico) — corrigido para exigir fraseado
    de prioridade autoral explícito.
  - GAP REAL: R370 exige dados brutos, manuscritos publicados só têm r/p/n — 
    fechado com `pearson_naive_significance()` (t-Student em Python puro,
    validado contra scipy a 1e-15) + `crosscheck_reported_correlation()`
    (ASSIMÉTRICA: só sinaliza p reportado mais forte que o ingênuo, nunca mais
    conservador — evita falso positivo contra correções legítimas de cointegração).
  - R371 e R372 funcionaram corretamente de primeira sobre o caso real.
  - Achado sem correção (fidelidade à fonte): 2/7 correlações do artigo-fonte não
    declaram `n` na Tabela 2 apesar da legenda definir n — documentado como
    recomendação no relatório de validação, não alterado no manuscrito.
  Relatório completo: `validacao_externa/manuscrito_armadilha_renda_media/relatorio_validacao_pipeline.md`.
  50 testes TDD novos; 194 regressão verdes; 2501 testes coletados sem erro.
- **R372 (2026-08-02):** BUG REAL CORRIGIDO em `mci/experiment_designer.py`:
  `"pre_registered": context.get("pre_registered", True)` dava o selo de graça
  sem verificação alguma — confirmado reproduzindo o bug antes de corrigir.
  `mci/preregistration_protocol.py` novo: `register_protocol`/`verify_protocol`
  (comparação textual exata, protege contra HARKing). `pre_registered` agora
  `False` por padrão; só `True` com protocolo registrado E honrado. Gate real
  no R103 (`verify_preregistered_claim`, mesmo padrão de R370/R371). 17 testes
  TDD verdes; 193 testes de regressão verdes; 2473 testes coletados sem erro
  em toda a suíte (checagem rápida de import-time em todo o repo).
  **Com R370+R371+R372, a trinca "estatística severa + validação cruzada +
  contraprovas + multidisciplinar + pré-registro" está completa na camada de
  infraestrutura/gate.** Doctor: 9/12 pass, 3 warn (ambiente: loop_specs vazio,
  scihub-cli ausente, litert-lm daemon parado — nenhum é bug de código).
- **R371 (2026-08-02):** `mci/multidisciplinary_triangulation.py` — segunda metade
  do pedido "estatística severa + cruzar informações multidisciplinares" fechado.
  `triangulated=True` só com >=2 domínios independentes concordantes E zero
  contestadores; contestação de qualquer domínio bloqueia (nunca maioria de
  votos). Design aditivo — não toca EvidenceGraph (R102) nem DataKnowledgeHub
  (R52/R55). Gate real no R103: `verify_multidisciplinary_claim()`, mesmo padrão
  do `verify_statistical_claim` do R370. 16 testes TDD verdes; zero regressão
  (115 testes combinados R102+R103+R370 verdes).
  **Com R370+R371, o pedido do usuário ("estatística severa, validação cruzada,
  contraprovas, cruzar informações multidisciplinares") está coberto no nível
  de infraestrutura de gate — falta ainda: uso real em produção (rodar o
  pipeline R101-R105 fim-a-fim com esses gates ativos num caso real) e o
  pré-registro de protocolo (opção descartada no brainstorming do R370, fica
  como R372+ se o usuário quiser).
- **R370 (2026-08-02):** `mci/rigorous_validation.py` — estatística COMPUTADA de dados
  brutos (não só validação de números já dados): contraprova por permutação
  (centrada pela própria distribuição nula — corrige viés para estatísticas
  assimétricas como Mann-Whitney U), Welch-t + Mann-Whitney + Cohen's d com IC
  bootstrap, k-fold CV genérico (partição exaustiva/disjunta, guarda contra
  denominador ~zero), `convergent_validity_report` (reaproveita
  `validate_statistics()` existente). Gate real no R103:
  `OrchestratorReviewer.verify_statistical_claim()` só verifica claim quando
  convergente. 23 testes TDD verdes; zero regressão (R103: 51 verdes,
  scientific_superhuman: 45 verdes). Bug real pego em TDD e documentado na
  spec: comparar `|observado|` vs `|permutado|` direto assume distribuição
  nula centrada em zero — falso para U de Mann-Whitney.
  Triangulação multidisciplinar (então pendente) foi feita no ciclo R371,
  logo acima.
- **R369 (2026-08-02):** `reasoning/production_scaffolds.py` — ponte entre os motores de
  raciocínio (SPEC-917/ARCHE) e a produção editorial: 8 movimentos científicos auditáveis
  com engine_hints; auditoria de novidade (`UNSUPPORTED_NOVELTY_CLAIM` quando "inédito/
  inovador" não tem citação/comparação na mesma frase); plano literário contratual
  (voz/conflito/símbolos/estranhamento); relatório medido de distintividade (léxico de
  22 clichês pt); `select_scaffold` via episteme da tarefa. 21 testes TDD verdes.
- **R368 (2026-08-02):** cobertura epistêmica do catálogo 32%→**65%** (léxico pt/en em 2
  rodadas curadas; invariante de sinais disjuntos; `catalog_episteme_coverage()`;
  12º check do doctor `episteme_coverage` com números medidos). Higiene SDD: 6 specs
  (R264–R279) apontavam para validações fantasmas → testes de regressão reais criados,
  `test_sdd_tdd` 12/12; 15 dirs `mci_test_state_*` removidos/ignorados.
  **Pendência documentada (frente literária):** falhas R272–R276 (~17) existem também
  no HEAD (verificado com stash do catálogo) — cards `literary-*` fora de contrato
  (ex.: `literary-ethics-trauma-phd` sem termo obrigatório "limites") e relatório R276
  ausente; corrigir na frente literária, não misturar aqui.
- **R364–R367 (2026-08-02):** implementados os três agentes que eram só interface no R359 +
  benchmark medido: TerminologyGraphAgent (`translation/terminology_graph.py`),
  AuthorVoiceGuardian (`translation/author_voice.py`), BackTranslationVerifier
  (`translation/back_translation.py`) — todos fail-closed, com gate humano, agent cards
  com `episteme:` explícita — e benchmark cultural medido
  (`scripts/benchmark_r367_cultural.py`: precisão micro 1.00, recall 0.86 em corpus
  interno de 18 casos; substitui o "98%" não medido do plano). 62 testes novos verdes.
  Pendências honestas: API/white label segue inexistente (só CLI local); validação
  externa do agente cultural continua não feita; opencode.json regenerado mas não
  commitado (mistura pendências de outra frente).
- **R363 (2026-08-02):** SPEC-935-R363 verified; `transformer/episteme.py` (6 regimes,
  inferência determinística), peso brando ±10% no `SkillHandbook.match` (fail-open),
  frontmatter opcional `episteme:` no catalog_loader; 27 testes TDD verdes.
  Suíte completa: 2200 pass / 58 falhas **pré-existentes de outras frentes**
  (literárias R272-R276, sépia R351, SPEC-R264 no test_sdd_tdd) — ver §6 da spec.
- **Working tree:** ⚠️ ainda há muito trabalho pendente de outras frentes
  (agents/catalog/*.md, Molambudos, etc.) — não misturar em commits do R363.
- **Trabalho avulso (sem ciclo):** capa trilíngue Molambudos corrigida
  (PT/EN/ZH recompostos em fonte vetorial sobre a arte, 4x upscale) —
  entregue em `~/Downloads/Molambudos_capa_trilingue_4x_TEXTO_CORRIGIDO.png`;
  script reprodutível no scratchpad da sessão (`recompose.py`).
- **Últimos commits (6):**

| Commit | Descrição |
|---|---|
| `d6fd391` | .gitignore: padrão *:Zone.Identifier |
| `6c5c39d` | .gitignore: scripts/cloud/ (pendente revisão) |
| `ee12dfa` | tests: ciclos R51-R53, R143-R145 |
| `4e1602d` | .gitignore + deploy/, publishing/templates/, geradores |
| `f0f0410` | **R229**: Catálogo, CLI, opencode.json, Academic Pipeline |
| `456821f` | **R223-R227**: Core Infra — Scanners, MCP, Trust, Transformer |
| `3938216` | **R210-R214**: LiteRT-LM supervisor + provider + plugin TS |
| `19c697e` | **R220-R222**: LLM Reduction Layer — engines, agent cards |
| `64544e1` | **R228**: Colibri + OLMoE — runtime MoE on-device |

## Ciclos completos (R47 → R229)

| Ciclo | O quê | Score |
|---|---|---|
| **R228** | Colibri + OLMoE: bridge, MCP, provider, doctor, agente | 0.95 |
| **R229** | Catálogo 187 agentes, CLI, opencode.json, Academic Pipeline | — |
| **R223-R227** | Core Infra: scanners, MCP, trust, transformer, observabilidade | — |
| **R220-R222** | LLM Reduction, DataKnowledgeHub, Observabilidade (3 gaps) | 0.94 |
| **R210-R214** | LiteRT-LM supervisor, provider, plugin TS, MCP reconciliation | 0.88 |
| **R208** | Médico Virtual Supremo + MetaBus + Scanner CLI | — |
| **R143** | Reconciliação de overlay stale | — |
| **R142** | Honest Evaluation Engine antioverclaim | — |
| **R141** | OCR-Vision para documentos antigos (SPEC-1001) | — |
| **R139** | pdf2latex multi-engine (SPEC-1000) | — |
| **R138** | OpenCode Go + Zen + Model Router | — |
| **R129** | Fluxo resumível (checkpoints) | — |
| **R128** | Encanamento seguro de chaves LLM (OpenAI + Ollama) | — |
| **R127** | Documentação minuciosa da arquitetura | — |
| **R126** | Agente-executor MIRA delegável | — |
| **R125** | MIRA como cidadão de primeira classe | — |
| **R124** | Capa/contracapa TikZ de livros | — |
| **R123** | Pipeline MIRA de apresentações | — |
| **R120** | CLI de pesquisa + fallback Sci-Hub | — |
| **R117** | Mapa 3D interativo da arquitetura | — |
| **R116** | Instalação multiplataforma + manual/helpdesk | — |
| **R53** | Nano-Orquestração LiteRT-LM (500 laudas) | 10.0 |
| **R52** | LiteRT-LM Skill + Provider OpenAI-compatível | — |
| **R51** | Jinja2 Templates engine | — |
| **R50** | DataKnowledgeHub | — |
| **R49** | GameTheoryLocal | — |
| **R48** | LLM Reduction Layer | — |

## Saúde do ecossistema

```json
{
  "checks_passed": 8,
  "checks_warned": 3,
  "checks_failed": 0,
  "warnings": [
    "CLI externa faltando: scihub-cli (pip install scihub-cli)",
    "LiteRT-LM daemon sem readiness (cold-start)",
    "Pendente revisão: scripts/cloud/ (324 scripts externos)"
  ],
  "agent_count": 187,
  "last_suite": "pendente de execução"
}
```

## Pendências conhecidas

1. **scripts/cloud/** — 324 scripts cloud externos. Pendente revisão de licença antes de versionar.
2. **LiteRT-LM daemon** — sem readiness (warm start pendente). Não afeta o funcionamento do ecossistema (fallback para Ollama + OpenAI).
3. **Colibri/OLMoE** — bridge e MCP implementados. Runtime C nativo precisa ser compilado (`make -C colibri/c olmoe`). Não versionado como submodule (embedded git repo).
4. **PROGRESS.md** — manter atualizado conforme novos ciclos.

## Próximos passos

1. **Triagem das ~31 falhas pré-existentes da suíte** (não relacionadas ao Molambudos, expostas desde o sync do R363/R380) — em andamento.
2. **Molambudos — limite de páginas KDP:** a edição impressa trilíngue (`kdp_tri`) tem 1.143 páginas contra um limite assumido de 828 na Amazon KDP (não validado externamente); precisa de decisão editorial (reduzir corpo, dividir em volumes, ou confirmar limite real no painel KDP) antes de qualquer tentativa de publicação física.
3. **Molambudos — validações humanas que não podem ser fabricadas:** revisão beta real, revisão de sensibilidade, revisão profissional de tradução nativa (EN/ZH), confirmação do ISBN numa conta KDP real, prova física impressa.
4. **Push pendente:** commits locais à frente de `origin/main` — enviar quando o usuário autorizar.

## Como retomar

1. `git log --oneline -5` — ver onde parou
2. `git status --short` — confirmar working tree limpa
3. `python3 -m marceloclaro.cli doctor` — saúde do ecossistema
4. `python3 -m pytest tests/ -q` — suíte de testes
5. Ler as pendências acima e seguir o próximo item

## Disciplina de checkpoint

Trabalho longo é quebrado em **passos pequenos, cada um commitável e verificável**.
Se a sessão acabar, a próxima retoma sem re-derivar contexto — a perda máxima é o passo em andamento, não o trabalho inteiro.
