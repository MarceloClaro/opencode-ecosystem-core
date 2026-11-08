# Protocolo de avaliação de eficácia {#avaliacao-eficacia}

> **Status:** este capítulo é um **protocolo de pesquisa**, não um estudo
> concluído. Nenhum dado de estudante foi coletado para esta edição. A nota de
> eficácia do livro permanece **não medida** até que o protocolo seja aprovado
> por um Comitê de Ética em Pesquisa (CEP), executado e analisado por uma equipe
> independente.
>
> **Versão 1.1 — ajustada após o piloto sintético R920.** O ensaio sintético
> (21 casos, 42 rounds, 84 ações, 196 perguntas) gerou 8 objeções de método.
> Elas estão respondidas na seção 14 e no apêndice **Piloto sintético**. O
> piloto não mediu aprendizagem; apenas testou a clareza e a factibilidade do
> protocolo.

## 1. Pergunta e hipóteses

**Pergunta:** um curso baseado nas trilhas deste livro aumenta a compreensão
conceitual, a capacidade de crítica científica e a retenção de curto prazo em
estudantes do ensino fundamental e médio, em comparação com um ensino
expositivo tradicional?

**H1 (compreensão):** o grupo que usa as trilhas terá ganho maior no teste
conceitual pós-intervenção, controlando o pré-teste.

**H2 (crítica):** o grupo que usa as trilhas terá maior desempenho em tarefas
de crítica científica — identificar amostra, incerteza, limite e explicação
alternativa.

**H3 (retenção):** o ganho se mantém em 3 e 6 meses após o fim da intervenção.

**H4 (equidade):** o ganho não será menor para estudantes com menor desempenho
inicial, neurodivergentes ou sem computador em casa.

**H0:** não há diferença entre os grupos em nenhum dos desfechos principais.

## 2. Desenho

Ensaio controlado randomizado por **cluster** (turma ou escola), com pré-teste,
pós-teste e seguimento. A randomização por cluster reduz contaminação entre
grupos da mesma turma.

| Elemento | Decisão |
|---|---|
| Unidade de randomização | turma ou escola |
| Braços | (A) trilhas do livro; (B) ensino expositivo tradicional |
| Medidas | pré-teste, pós-teste imediato, 3 meses, 6 meses |
| Duração da intervenção | 12 semanas (Trilha A) ou 20 semanas (Trilha B) |
| Professores | mesmos critérios de formação; treinamento padronizado |
| Cegamento | impossível para professores e alunos; avaliadores do teste cegos |
| Análise | intenção de tratar; ANCOVA com pré-teste; erros cluster-robustos |

## 3. População e amostra

### 3.1 População

- **Trilha A:** estudantes de 12 a 14 anos, ensino fundamental.
- **Trilha B:** estudantes de 15 a 17 anos, ensino médio.
- **Trilha P:** professores em formação continuada.

Critérios de inclusão: turma regular, professor disposto, consentimento dos
responsáveis e assentimento do estudante. Critérios de exclusão: participação
em outro curso de computação quântica no mesmo período; ausência de dados no
pré-teste sem possibilidade de reposição.

### 3.2 Tamanho de amostra

Para detectar `d=0,40` com poder de 80% e alfa de 5%, são necessários cerca de
**98 estudantes por grupo** em um desenho individual. Com clusters de 25
estudantes e ICC=0,05, o efeito de desenho é:

```text
DE = 1 + (m − 1) × ICC = 1 + (25 − 1) × 0,05 = 2,2
n_por_grupo ≈ 98 × 2,2 ≈ 216
n_total ≈ 432
```

Para `d=0,50`, o total cai para cerca de **276 estudantes**. O protocolo adota
`d=0,40` como alvo conservador e prevê **440 estudantes** (22 turmas de 20,
11 por braço), com margem para perda de 20%.

### 3.3 Seleção de escolas e turmas

| Critério | Inclusão | Exclusão | Registro |
|---|---|---|---|
| Escola | rede pública ou privada, com ensino fundamental/médio | escola em greve ou sem autorização | carta de anuência |
| Turma | turma regular, professor titular | turma multisseriada sem apoio | lista de turmas |
| Professor | disposto a seguir o protocolo | outro curso quântico no período | termo de compromisso |
| Estudante | assentimento + consentimento | ausência total no pré-teste | formulário |
| Infraestrutura | sala, internet para demonstração | sem energia/Internet e sem plano B | checklist |

A seleção deve ser **pública e replicável**: lista de escolas convidadas, ordem
de resposta, critérios de recusa e mapa de substituição. Nada de “escolhemos as
melhores turmas” sem registro.

## 4. Instrumentos

| Instrumento | O que mede | Formato | Confiabilidade |
|---|---|---|---|
| Teste conceitual | bit, qubit, medição, fase, emaranhamento, circuito | 20 itens de múltipla escolha | alfa de Cronbach ≥ 0,70 |
| Teste de transferência | aplicar a ideia a um caso novo | 5 questões abertas | rubrica de 0–4 |
| Tarefa de crítica | amostra, incerteza, limite, alternativa | 3 casos com counts | rubrica de 0–4 |
| Escala de atitude | interesse, autoeficácia, ansiedade | 15 itens Likert | alfa ≥ 0,75 |
| Caderno de bordo | previsão, resultado, limite | análise documental | rubrica |
| Observação de aula | fidelidade ao protocolo | checklist | dois observadores |
| Retenção | teste conceitual reduzido | 10 itens | alfa ≥ 0,70 |

Os instrumentos devem ser pilotados com 30 estudantes fora da amostra, com
análise de dificuldade, discriminação e tempo de resposta. A versão final deve
ser pré-registrada antes da coleta.

### 4.1 Definições operacionais

| Conceito | Definição operacional | Como medir |
|---|---|---|
| **Compreensão conceitual** | explicar, prever e aplicar bit, qubit, medição, fase e emaranhamento | teste de 20 itens + transferência |
| **Crítica científica** | identificar amostra, incerteza, limite e explicação alternativa | rubrica de 0–4 em 3 casos |
| **Retenção** | manter o ganho após 3 e 6 meses | teste reduzido de 10 itens |
| **Atitude** | interesse, autoeficácia e ansiedade | escala Likert de 15 itens |
| **Fidelidade** | adesão ao checklist de 10 itens por sessão | observação + registro |
| **Equidade** | ausência de diferença > 0,20 entre subgrupos | análise moderada por subgrupo |

Essas definições existem para impedir que “compreensão” vire “vocabulário” e que
“crítica” vire “opinião”. Se um instrumento não mede a definição, ele não entra.

## 5. Intervenção

### 5.1 Braço A — trilhas do livro

- Trilha A: 12 semanas, 3 sessões de 30–40 min por semana.
- Trilha B: 20 semanas, 2 sessões de 60 min por semana.
- Sequência: manual → simulação → hardware → síntese.
- Professor usa o livro, o caderno e os scripts; hardware é demonstrativo e
  supervisionado.
- Fidelidade: checklist de 10 itens por sessão; 80% de adesão mínima.

### 5.2 Braço B — ensino expositivo tradicional

- Mesmo conteúdo conceitual, sem a sequência manual-first e sem os experimentos
  de hardware.
- Aulas expositivas, lista de exercícios e demonstração pelo professor.
- Mesmo tempo total de instrução.

### 5.3 Contaminação

- Turmas do mesmo professor em braços diferentes devem ser evitadas.
- Se ocorrer, registrar e analisar como variável de sensibilidade.
- Não impedir que o braço B use o livro fora da aula; registrar o uso.

## 6. Ética e proteção de dados

1. Submissão ao **CEP** via Plataforma Brasil, com projeto detalhado.
2. **Consentimento informado** dos responsáveis e **assentimento** dos estudantes.
3. Dados anonimizados; nenhum nome, chave de API ou dado pessoal no corpus.
4. Nenhuma conta de plataforma quântica criada por menor sem responsável.
5. Direito de retirada a qualquer momento, sem prejuízo acadêmico.
6. Dados armazenados em repositório institucional com controle de acesso.
7. Plano de comunicação de resultados aos participantes e à escola.

> **Regra:** sem aprovação do CEP, o protocolo não deve ser executado. O livro
> não autoriza coleta de dados em sala sem esse passo.

## 7. Análise

### 7.1 Desfecho principal

Ganho no teste conceitual, medido por:

```text
ganho = pós − pré
```

Modelo ANCOVA:

```text
pós_ij = β0 + β1·grupo_j + β2·pré_ij + u_j + e_ij
```

em que `u_j` é o efeito aleatório de turma e `e_ij` o erro individual. Erros
padrão cluster-robustos. Efeito padronizado:

```text
g = (média_A − média_B) / desvio_padrão_pooled
```

### 7.2 Desfechos secundários

- crítica científica (rubrica 0–4);
- atitude e autoeficácia;
- retenção em 3 e 6 meses;
- equidade por desempenho inicial, neurodivergência e acesso a computador.

### 7.3 Dados faltantes

- Análise de intenção de tratar.
- Imputação múltipla (20 imputações) como sensibilidade.
- Relatar taxa de atrito por braço e motivo.

### 7.4 Multiplicidade

- Desfecho principal único; secundários com correção de Holm.
- Relatar todos os desfechos, inclusive os não significativos.

## 8. Critérios de sucesso

| Critério | Limiar | O que significa |
|---|---|---|
| Ganho conceitual | `g ≥ 0,40` | efeito educacional moderado |
| Crítica científica | `g ≥ 0,50` | melhora em amostra, incerteza e limite |
| Retenção 3 meses | ≥ 70% do ganho | não é só novidade |
| Retenção 6 meses | ≥ 50% do ganho | mudança durável |
| Equidade | sem diferença > 0,20 entre subgrupos | não amplia desigualdade |
| Fidelidade | ≥ 80% do checklist | intervenção foi aplicada |

Se o efeito for menor que 0,20, o protocolo deve ser revisto antes de nova
coleta. Se for maior que 0,60, replicar com outra equipe antes de celebrar.

## 9. Ameaças à validade

- **Novidade:** o entusiasmo inicial pode inflar o pós-teste; a retenção mede.
- **Efeito do professor:** treinamento e observação reduzem, mas não eliminam.
- **Contaminação:** alunos do braço B podem usar o livro; registrar.
- **Autosseleção:** escolas que aceitam podem ser diferentes; relatar.
- **Cegamento:** avaliadores cegos, mas professores e alunos não.
- **Validade de construto:** o teste conceitual pode medir vocabulário, não
  compreensão; usar transferência e crítica.
- **Poder:** 440 alunos detectam `d=0,40`; efeitos menores exigem mais.

### 9.1 Interpretações rivais

| Resultado observado | Explicação preferida | Rival plausível | Como distinguir |
|---|---|---|---|
| ganho no pós-teste | o livro ensina | novidade e atenção do pesquisador | retenção em 3/6 meses; grupo ativo de comparação |
| melhora na crítica | a rubrica ensina | treino de vocabulário | transferência para caso novo |
| diferença entre turmas | intervenção | efeito do professor | observação de fidelidade e modelo multinível |
| queda no seguimento | esquecimento | mudança de escola ou perda seletiva | análise de atrito e imputação |
| ausência de diferença | o livro não funciona | implementação fraca | checar fidelidade ≥ 80% antes de concluir |

O protocolo deve registrar **explicações rivais antes da coleta**, não depois de
ver o resultado. É a diferença entre testar e torcer.

## 10. Pré-registro e transparência

- Registrar o protocolo no **OSF Registries** antes da coleta.
- Publicar instrumentos, plano de análise e critérios de exclusão.
- Depositar dados anonimizados e código de análise em repositório com DOI.
- Relatar desvios do protocolo e análises exploratórias separadamente.

## 11. Cronograma e orçamento ilustrativo

| Fase | Duração | Produto |
|---|---|---|
| Aprovação CEP | 2–3 meses | parecer consubstanciado |
| Piloto | 1 mês | instrumentos calibrados |
| Coleta | 3–5 meses | pré, pós, seguimento |
| Análise | 3 meses | relatório e artigo |
| Divulgação | 2 meses | devolutiva às escolas |

Orçamento ilustrativo: bolsas, impressão, deslocamento, software, revisão e
publicação. Valores devem ser calculados pela instituição; este protocolo não
fixa cifras.

### 11.1 Cronograma com dependências

| Etapa | Depende de | Entrega | Atraso aceitável |
|---|---|---|---|
| CEP | projeto completo | parecer | 0 (bloqueante) |
| Cartas de anuência | escola e Secretaria | documento assinado | 2 semanas |
| Piloto | CEP + anuência | instrumentos calibrados | 2 semanas |
| Coleta | piloto + treinamento | base anonimizada | 4 semanas |
| Análise | coleta encerrada | relatório | 4 semanas |
| Devolutiva | análise | apresentação às escolas | 4 semanas |

### 11.2 Recursos mínimos

| Recurso | Uso | Se faltar |
|---|---|---|
| 1 coordenador | ética, logística, análise | o estudo não começa |
| 2 assistentes | aplicação, digitação, observação | reduzir turmas |
| 1 estatístico | plano e análise | contratar ou parceria |
| computadores | Python/simulação | usar resultados documentados |
| internet | hardware demonstrativo | usar dados registrados |
| impressão | cadernos e instrumentos | versão digital |

### 11.3 Plano de contingência

| Risco | Sinal | Resposta |
|---|---|---|
| greve/closure | escola fechada | adiar coleta; registrar |
| professor ausente | substituição | sessão de reposição |
| hardware indisponível | fila/erro | usar simulação + dados documentados |
| baixa adesão | < 70% | reforço, não exclusão |
| perda de dados | falha de backup | backup diário + hash |
| contaminação | braço B usa o livro | registrar e analisar sensibilidade |
| atrito diferencial | mais perda em um braço | imputação + relatório |

### 11.4 Governança e cartas de anuência

- Carta da escola com assinatura do diretor.
- Carta da Secretaria, quando exigida.
- Termo de compromisso do professor.
- Contato do CEP e do pesquisador responsável.
- Canal para dúvidas e retirada.
- Registro de versões do protocolo e dos instrumentos.

### 11.5 Plano de dados e fontes

- Dados brutos anonimizados, com hash SHA-256.
- Dicionário de variáveis e código de análise.
- Backup em dois locais; acesso restrito.
- Retenção por 5 anos, depois destruição.
- Publicação de dados agregados; nunca de respostas individuais.
- Se uma fonte externa ficar indisponível, registrar a data e usar a última
  versão com hash; não substituir evidência negativa por conveniência.

## 12. O que este protocolo não é

- Não é um resultado.
- Não é uma prova de que o livro funciona.
- Não é um parecer de ética.
- Não é um peer review.
- Não é uma licença para coletar dados sem consentimento.

É um **plano verificável**. Se executado, permitirá substituir “acreditamos que
funciona” por “medimos que funciona — ou não”.

## 13. Resposta ao piloto sintético

O protocolo foi submetido ao **piloto sintético R920** (motor acadêmico local,
sem LLM, sem OASIS, sem dados humanos). Resultado operacional:

| Métrica | Valor |
|---|---:|
| Casos | 21 |
| Rounds | 42 |
| Ações | 84 |
| Perguntas geradas | 196 |
| Objeções não resolvidas | 8 |
| Status | completed |
| Review status | needs_revision |
| Trajetória SHA-256 | `0fbaaed5de26ac45de5f828799beef7fbf72502b86442174938c9a9a736a645f` |

As 8 objeções e as respostas no protocolo:

| Objeção do piloto | Resposta nesta versão |
|---|---|
| Perguntas ou interpretações alternativas | Seção 9.1 — interpretações rivais |
| Genealogia e limites dos conceitos | Seção 4.1 — definições operacionais |
| Análise de interpretações rivais | Seção 9.1 — tabela de explicações alternativas |
| Critérios de seleção | Seção 3.3 — seleção de escolas e turmas |
| Precedências e prazos | Seção 11.1 — cronograma com dependências |
| Disponibilidade de recursos | Seção 11.2 — recursos mínimos |
| Contingências | Seção 11.3 — plano de contingência |
| Aderência institucional | Seção 11.4 — governança e cartas |
| Fonte indisponível | Seção 11.5 — plano de dados e fontes |

O piloto **não** mediu aprendizagem, não gerou effect size e não substitui o
CEP. Ele apenas mostrou que o protocolo precisava explicitar melhor as
alternativas, os critérios, os recursos e as contingências. A versão 1.1
incorpora essas respostas.

## 14. Referências {#avaliacao-referencias}

FREEMAN, S. et al. Active learning increases student performance in science,
engineering, and mathematics. *PNAS*, v. 111, n. 23, p. 8410–8415, 2014.
DOI: <https://doi.org/10.1073/pnas.1319030111>.

DESLAURIERS, L. et al. Measuring actual learning versus feeling of learning in
response to being actively engaged in the classroom. *PNAS*, v. 116, n. 39,
p. 19251–19257, 2019. DOI: <https://doi.org/10.1073/pnas.1821936116>.

HATTIE, J.; TIMPERLEY, H. The Power of Feedback. *Review of Educational
Research*, v. 77, n. 1, p. 81–112, 2007.
DOI: <https://doi.org/10.3102/003465430298487>.

ROEDIGER, H. L.; KARPICKE, J. D. Test-Enhanced Learning. *Psychological
Science*, v. 17, n. 3, p. 249–255, 2006.
DOI: <https://doi.org/10.1111/j.1467-9280.2006.01693.x>.

CEPEDA, N. J. et al. Distributed practice in verbal recall tasks: A review and
quantitative synthesis. *Psychological Bulletin*, v. 132, n. 3, p. 354–380,
2006. DOI: <https://doi.org/10.1037/0033-2909.132.3.354>.

KRIJTENBURG, H. K. E.; DEPREZ, E. van den B.; VAN DER VEEN, J. T. Insights into
teaching quantum mechanics in secondary and lower undergraduate education.
*Physical Review Physics Education Research*, v. 13, p. 010109, 2017.
DOI: <https://doi.org/10.1103/PhysRevPhysEducRes.13.010109>.

OPEN SCIENCE COLLABORATION. Estimating the reproducibility of psychological
science. *Science*, v. 349, n. 6251, aac4716, 2015.
DOI: <https://doi.org/10.1126/science.aac4716>.

WASSERSTEIN, R. L.; LAZAR, N. A. The ASA Statement on p-Values: Context,
Process, and Purpose. *The American Statistician*, v. 70, n. 2, p. 129–133,
2016. DOI: <https://doi.org/10.1080/00031305.2016.1154108>.
