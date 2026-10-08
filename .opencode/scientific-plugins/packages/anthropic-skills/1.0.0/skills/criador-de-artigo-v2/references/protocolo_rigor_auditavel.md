# Protocolo de Rigor Auditavel

## Finalidade
Este arquivo transforma exigencias gerais em um procedimento operacional unico para busca, selecao, leitura, escrita, rastreabilidade e auditoria final. O objetivo e impedir:

- afirmacoes sem lastro documental;
- referencias escolhidas sem criterio explicito;
- citacoes sem localizacao exata;
- saltos logicos entre fonte, interpretacao e conclusao;
- capitulos longos, mas nao verificaveis.

---

## Arquitetura multiagente

Os prompts operacionais de cada funcao estao no diretorio `agents/`. Este protocolo define as regras do sistema; os arquivos em `agents/` definem como cada agente deve operar dentro dessas regras.

Para artigos com codigo, dados, modelos ou simulacoes, este protocolo tambem exige leitura e aplicacao de:

- `references/nucleo_analitico_reprodutivel.md`
- `references/auditoria_codigo_cientifico.md`
- `framework/README.md`
- `datasets/README.md`

### Papel central

O processo deve ser conduzido por um agente-gerente unico, denominado `Editor-Chefe PhD / Gerente de Qualis A1`. Ele e o responsavel final por:

- definir a estrategia geral do artigo;
- distribuir tarefas entre subagentes;
- validar entregas parciais;
- bloquear etapas incompletas;
- arbitrar conflitos entre revisoes;
- decidir se uma saida esta pronta para integrar o manuscrito.

### Subagentes obrigatorios

1. `Agente de Diagnostico`:
- delimita problema, objetivo, hipoteses, escopo e risco metodologico;
- produz o mapa inicial de lacunas e o plano de paginas.

2. `Agente de Busca e Triagem`:
- executa a busca multipla em bases;
- registra logs de busca, triagem e exclusoes;
- confirma texto integral e aderencia.

3. `Agente de Evidencias`:
- constrói a matriz de evidencias;
- relaciona afirmacoes com fontes, paginas e funcao argumentativa;
- aponta limites de uso de cada fonte.

4. `Agente de Redacao`:
- redige os paragrafos com base na matriz aprovada;
- preserva conexao entre definicao, evidencia, analise e transicao;
- nao inventa fonte, dado ou inferencia sem aprovacao previa.

5. `Agente de Estatistica e Metodo`:
- valida desenho, analises, pressupostos e reportes numericos;
- verifica se as escolhas metodologicas estao amparadas por literatura e por logica analitica.

6. `Agente de Qualidade e ABNT`:
- verifica formato, pagina, citações, referencia final, ordem, padrao ABNT e integridade textual;
- acusa divergencia entre texto, rodape e referencia.

7. `Agente de Consistencia Interna`:
- confere se problema, objetivos, hipoteses, resultados e conclusoes fecham entre si;
- detecta repeticiones, saltos logicos e overclaim.

### Regra de independencia funcional

Cada subagente produz uma saida propria, mas nenhuma saida e final ate passar pelo gerente. Nenhum subagente pode aprovar o proprio trabalho. A aprovacao exige sempre revisao por outro agente ou pelo gerente.

---

## Regras inegociaveis

1. Nenhuma referencia entra no texto sem trilha de busca registrada.
2. Nenhuma referencia entra no texto sem leitura do texto integral ou, quando impossivel, justificativa formal de excecao.
3. Nenhuma citacao entra no texto sem pagina, intervalo de paginas, artigo, paragrafo, secao ou identificador equivalente.
4. Nenhum paragrafo deve conter afirmacao factual, normativa, metodologica ou historica sem evidencia explicitamente associada.
5. Toda interpretacao propria deve ser distinguida daquilo que a fonte efetivamente afirma.
6. Todo capitulo deve terminar com um pacote de auditoria completo.
7. Nenhuma etapa pode ser concluida sem gate de handoff assinado pelo gerente.
8. Nenhuma divergencia entre subagentes pode ser ignorada; ela deve ser resolvida, registrada ou bloqueada.
9. Nenhuma saida parcial pode ser consumida como final sem validacao cruzada.
10. Todo artigo com dados, codigo ou simulacao deve ter pacote de reproducibilidade proporcional ao risco metodologico.

---

## Artefatos obrigatorios

| Arquivo | Finalidade | Momento de uso |
|---|---|---|
| `log_busca.md` | Registrar plataformas, strings, filtros, datas, resultados e decisoes | Antes e durante a revisao |
| `triagem_fontes.md` | Registrar inclusoes, exclusoes e criterio de elegibilidade | Logo apos cada rodada de busca |
| `matriz_evidencias.md` | Mapear cada afirmacao relevante a uma evidencia localizavel | Antes de redigir cada secao |
| `mapa_citacoes.md` | Associar referencias a capitulos, paragrafos e funcao argumentativa | Durante a redacao |
| `auditoria_linha_a_linha.md` | Revisar frase a frase, paragrafo a paragrafo | Antes da entrega |
| `pendencias_validacao.md` | Listar lacunas, conflitos, referencias fracas ou duvidas abertas | Sempre que houver incerteza |
| `manifesto_reprodutibilidade.md` | Declarar o escopo real da reproducao e suas restricoes | Sempre que houver dados ou codigo |
| `ambiente_execucao.md` | Congelar linguagens, dependencias, hardware, seeds e ordem de execucao | Antes de validar resultados computacionais |
| `catalogo_datasets.md` | Registrar origem, licenca, versao, split e papel de cada dataset | Antes de modelagem ou analise quantitativa intensiva |
| `codebook_dados.md` | Registrar schema, variaveis, unidades, missing e transformacoes | Antes da analise final |
| `auditoria_codigo.md` | Verificar uso de APIs, bibliotecas e trechos tecnicos contra fontes confiaveis | Antes da liberacao de achados computacionais |
| `auditoria_formulas.md` | Verificar simbolos, derivacoes, suposicoes e estabilidade da modelagem formal | Quando houver equacoes ou modelos matematicos |
| `registro_experimentos.md` | Registrar runs, seeds, hiperparametros, metricas e anomalias | Durante experimentacao ou benchmark |
| `relatorio_benchmark_robustez.md` | Medir baseline, ablation, sensibilidade e estabilidade | Antes do QA final de resultados computacionais |

---

## Fluxo obrigatorio

### 1. Delimitar a pergunta
- Registrar pergunta central, objetivos, hipoteses e variaveis.
- Explicitar quais tipos de evidencia podem responder a cada subquestao.
- Separar o que exige fonte normativa, empirica, teorica, metodologica e estatistica.
- Handoff para `Agente de Busca e Triagem` somente apos aprovacao do `Editor-Chefe PhD / Gerente de Qualis A1`.

### 2. Planejar a busca
- Definir bases obrigatorias por area.
- Redigir strings literais em portugues e ingles.
- Definir periodo temporal, filtros, tipo de documento e criterio de prioridade.
- Definir o que conta como saturacao e o que conta como cobertura minima.
- Handoff para `Agente de Evidencias` somente com log de busca completo.

### 3. Executar e registrar
- Registrar a string exata usada em cada base.
- Registrar filtros aplicados, data, horario e total bruto de resultados.
- Registrar quantos itens foram abertos, quantos lidos integralmente e quantos selecionados.
- Registrar por que os itens rejeitados foram rejeitados.
- O gerente deve revisar o log e bloquear qualquer busca sem criterio de exclusao claro.

### 4. Fazer triagem referencia a referencia
- Confirmar texto integral disponivel.
- Confirmar autoria, veiculo, ano, DOI/URL e integridade do arquivo.
- Confirmar pertinencia direta para o problema do artigo.
- Confirmar em qual papel a fonte sera usada: definicao, suporte empirico, contraste, metodo, norma, dado contextual ou limitacao.
- Handoff para redacao so ocorre apos triagem aprovada pelo gerente e por, no minimo, um subagente de contraste.

### 5. Ler integralmente e localizar
- Ler o texto completo, nao apenas resumo.
- Destacar paginas exatas, tabelas, figuras, artigos de lei ou secoes usadas.
- Registrar o trecho ou dado que realmente sustenta a afirmacao pretendida.
- Registrar tambem o que a fonte nao sustenta, para evitar extrapolacao.
- Toda leitura integral deve ser conferida por uma segunda passagem do `Agente de Evidencias` ou do `Agente de Qualidade e ABNT`.

### 6. Montar a matriz de evidencias
- Antes de escrever, preencher a matriz com as afirmacoes planejadas.
- Toda afirmacao relevante deve nascer com fonte, localizacao e funcao argumentativa.
- Se a afirmacao nao encontrar fonte robusta, ela nao deve entrar no texto como fato.
- O gerente aprova a matriz antes que a redacao comece.

### 7. Redigir com rastreabilidade
- Inserir a citacao o mais proximo possivel da afirmacao que ela sustenta.
- Distinguir no proprio texto: dado reportado, interpretacao dos autores, interpretacao do artigo e implicacao.
- Marcar contrapontos quando houver literatura divergente relevante.
- Cada paragrafo redigido deve voltar ao `Agente de Evidencias` para conferencia de lastro.

### 8. Auditar linha a linha
- Revisar cada frase e classifica-la por funcao.
- Verificar se frases de evidencia e analise estao ancoradas.
- Verificar se ha salto entre o que a fonte diz e o que o texto conclui.
- Verificar se referencias repetidas estao sendo reutilizadas com paginas diferentes e funcao clara.
- O `Agente de Consistencia Interna` valida se a narrativa permanece fechada.

### 9. Fechar o pacote de evidencia
- Conferir coerencia entre `log_busca.md`, `triagem_fontes.md`, `matriz_evidencias.md`, `mapa_citacoes.md` e `auditoria_linha_a_linha.md`.
- Conferir se cada referencia da lista final aparece no mapa de citacoes.
- Conferir se cada citacao no texto tem lastro em uma leitura documentada.
- O pacote final so sobe para o gerente depois da validacao cruzada de pelo menos dois subagentes.

### 10. Fechar o pacote computacional e reprodutivel
- Conferir coerencia entre `manifesto_reprodutibilidade.md`, `ambiente_execucao.md`, `catalogo_datasets.md`, `codebook_dados.md`, `auditoria_codigo.md`, `registro_experimentos.md` e `relatorio_benchmark_robustez.md`.
- Verificar se cada resultado computacional central pode ser rastreado a dado, codigo, configuracao e metrica.
- Verificar se bibliotecas, frameworks e formulas criticas foram auditados contra documentacao ou repositorio oficial.
- Bloquear qualquer resultado computacional sem baseline, sem experimento registrado ou sem limitacao tecnica explicita.

---

## Gates de handoff

### Gate 0 — Inicio

- Entrada: briefing do usuario, tema e tipo de artigo.
- Saida: problema, objetivo, escopo e risco inicial.
- Aprovadores: `Editor-Chefe PhD / Gerente de Qualis A1`.

### Gate 1 — Busca

- Entrada: pergunta delimitada e plano de busca.
- Saida: logs completos, triagem e lista de fontes candidatas.
- Bloqueio: qualquer base sem string literal, data ou criterio de exclusao.

### Gate 2 — Evidencia

- Entrada: fontes candidatas aprovadas.
- Saida: matriz de evidencias com funcao, pagina e limite.
- Bloqueio: qualquer afirmacao sem lastro ou qualquer fonte sem leitura integral.

### Gate 3 — Redacao

- Entrada: matriz de evidencias aprovada.
- Saida: texto por paragrafo com citacao, contraponto e transicao.
- Bloqueio: qualquer paragrafo que introduza inferencia sem ancoragem.

### Gate 4 — Metodo e Estatistica

- Entrada: secao metodologica ou resultado numerico.
- Saida: verificacao de pressupostos, formula, reporte e interpretacao.
- Bloqueio: qualquer metodo sem justificativa ou qualquer estatistica sem transparencia.

### Gate 5 — Qualidade e ABNT

- Entrada: texto consolidado.
- Saida: formato final, referencias, rodapes e consistencia normativa.
- Bloqueio: qualquer divergencia entre corpo, rodape e referencia.

### Gate 6 — Liberacao final

- Entrada: pacote completo validado.
- Saida: aprovacao do gerente para integracao ao manuscrito.
- Bloqueio: qualquer pendencia aberta em `pendencias_validacao.md`.

---

## Criterios de relevancia de busca

Uma busca so e considerada relevante quando cobre, no minimo, estas cinco dimensoes:

1. Relevancia conceitual: responde diretamente ao problema, objetivo ou hipotese.
2. Relevancia metodologica: ajuda a justificar desenho, instrumento, tecnica ou analise.
3. Relevancia empirica: fornece dado, resultado, tendencia ou contraste concreto.
4. Relevancia critica: inclui autores que discordam, limitam ou relativizam a narrativa principal.
5. Relevancia contextual: inclui fontes do contexto geografico, institucional ou normativo pertinente.

---

## Hierarquia minima de fontes

Use a hierarquia mais forte compativel com a pergunta:

- Fonte oficial consolidada para legislacao, regulacao, diretriz e norma.
- Artigo original ou texto fundador para definicoes, conceitos e teoria de base.
- Revisao sistematica ou metanalise para estado da arte empirico consolidado.
- Estudo primario de alta qualidade para dado especifico, local ou recente.
- Artigo metodologico original para tecnica, instrumento, software ou procedimento.
- Fonte critica qualificada para contraponto, limite, controversia ou risco de overclaim.

---

## Template de log de busca

```md
| ID | Pergunta | Base | String literal | Filtros | Data | Resultados brutos | Lidos integralmente | Selecionados | Motivo de selecao/exclusao |
|---|---|---|---|---|---|---|---|---|---|
| B01 | [subquestao] | Scopus | TITLE-ABS-KEY("...") | 2021-2026; article | 2026-03-17 | 124 | 11 | 4 | Selecionados por aderencia ao problema e texto integral disponivel |
```

---

## Template de triagem

```md
| ID | Referencia | Status | Papel no artigo | Texto integral | Localizacao | Criterio de decisao | Risco |
|---|---|---|---|---|---|---|---|
| F01 | AUTOR (2023) | Incluida | Suporte empirico | Sim | PDF | Alta aderencia e metodo compativel | Baixo |
| F02 | AUTOR (2021) | Excluida | - | Sim | HTML | Nao responde a pergunta central | Medio |
```

---

## Template de matriz de evidencias

```md
| ID da afirmacao | Secao/paragrafo | Afirmacao verificavel | Tipo | Fonte principal | Fonte de contraste | Localizacao exata | Funcao da citacao | Limite da evidencia |
|---|---|---|---|---|---|---|---|---|
| A01 | 2.1/P3 | X foi definido como... | Definicao | AUTOR (2019) | AUTOR (2021) | p. 14-16 | Delimitar conceito | Divergencia terminologica |
| A02 | 3.2/P4 | O instrumento Y apresentou alfa > 0,80 | Metodo | AUTOR (2022) | - | p. 55; Tabela 2 | Justificar uso do instrumento | Validado apenas em contexto semelhante |
```

---

## Template de auditoria linha a linha

```md
| Paragrafo | Frase | Funcao | Afirma algo verificavel? | Fonte e localizacao | A fonte sustenta integralmente? | Ajuste necessario |
|---|---|---|---|---|---|---|
| 2.3/P5 | F1 | Definicao | Sim | AUTOR (2018, p. 22) | Sim | Nenhum |
| 2.3/P5 | F3 | Analise | Sim | AUTOR (2018, p. 22); AUTOR (2021, p. 88) | Parcialmente | Explicitar que se trata de inferencia do artigo |
```

### Funcoes padrao de frase
- `D` Definicao
- `E` Evidencia
- `A` Analise
- `C` Contraste
- `L` Limitacao
- `T` Transicao
- `J` Justificativa metodologica

---

## Regras de aceitacao por paragrafo

- Nenhum paragrafo deve terminar sem conexao com o objetivo, argumento ou resultado central.
- Todo paragrafo analitico deve conter pelo menos uma evidencia localizavel.
- Paragrafos de revisao de literatura devem conter, sempre que aplicavel, convergencia e divergencia.
- Paragrafos metodologicos devem indicar escolha, justificativa, suporte e limite.
- Paragrafos de resultados devem apontar tabela, figura, teste, indicador ou saida analitica correspondente.

---

## Regras de rejeicao imediata

- Citar titulo, resumo ou palavras-chave como se fossem prova suficiente.
- Usar referencia sem localizacao exata.
- Usar fonte secundaria quando a primaria esta acessivel.
- Atribuir a um autor uma conclusao que o texto original nao sustenta.
- Tratar inferencia propria como se fosse dado da fonte.
- Fechar a busca sem registrar bases, strings e criterios.
- Omitir literatura contraria quando ela e relevante e conhecida.

---

## Adendo - Nucleo analitico reprodutivel

Quando o manuscrito depender de analise quantitativa intensiva, codigo, dataset, modelo, simulacao ou framework tecnico, a cadeia auditavel passa a exigir:

1. ambiente de execucao minimamente reconstruivel;
2. catalogo de datasets e codebook completos;
3. auditoria de codigo ancorada em documentacao oficial e repositorios oficiais;
4. auditoria de formulas quando houver modelagem formal;
5. registro de experimentos com seeds, configuracoes, metricas e anomalias;
6. benchmark, ablation e robustez antes de declarar ganho, superioridade ou contribuicao tecnica.

### Gate adicional do nucleo analitico

- Entrada: datasets, ambiente, codigo, modelos ou simulacoes relevantes.
- Saida: pacote computacional auditado, com manifesto, ambiente, dados, codigo, experimentos e benchmark.
- Bloqueio: qualquer discrepancia entre codigo, dado e resultado; qualquer snippet sem ancora tecnica; qualquer benchmark sem baseline ou sem registro de runs.

### Criterio de reprovacao imediata adicional

- resultado computacional sem `manifesto_reprodutibilidade.md`;
- dataset sem origem, licenca ou split identificavel;
- codigo critico sem `auditoria_codigo.md`;
- formula central sem simbolos, hipoteses ou limite de aplicacao;
- experimento sem seed, configuracao ou run rastreavel;
- alegacao de ganho tecnico sem baseline ou sem relatorio de robustez.
