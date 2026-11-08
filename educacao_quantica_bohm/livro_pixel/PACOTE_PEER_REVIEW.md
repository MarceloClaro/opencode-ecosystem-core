# Pacote de peer review {#peer-review}

> **Status:** este capítulo é um **convite e um formulário de revisão**, não um
> parecer. Nenhum revisor externo avaliou esta edição até a data de fechamento.
> A nota de peer review permanece **3/10** até que revisores independentes
> assinem pareceres.

## 1. Por que um pacote de revisão

Um livro de 3580 páginas não deve ser avaliado por um leitor solitário. A
revisão por pares exige:

- critérios explícitos;
- revisores com especialidades diferentes;
- declaração de conflitos;
- confidencialidade;
- prazo;
- resposta do autor;
- registro público do parecer.

Este pacote organiza esse processo. Ele não substitui uma editora, uma banca ou
um conselho científico.

## 2. Perfis de revisor

| Perfil | O que avalia | Formação sugerida |
|---|---|---|
| **R1 — Ensino de física** | progressão, analogias, erros conceituais, adequação ao público | mestrado/doutorado em ensino de física |
| **R2 — Computação quântica** | circuitos, Qiskit/PennyLane/Cirq, hardware, ruído | doutorado em computação quântica ou área afim |
| **R3 — Bohm e filosofia da física** | interpretação, ordem implicada, diálogo, limites | doutorado em filosofia da física ou história da ciência |
| **R4 — Método e estatística** | desenho, amostra, análise, reprodutibilidade | estatístico ou pesquisador com publicação em método |
| **R5 — Educação inclusiva** | acessibilidade, neurodivergência, linguagem, equidade | pesquisador ou profissional com experiência inclusiva |

O mínimo para um parecer completo é **três revisores**: R1, R2 e R4. R3 e R5
são recomendados para a dimensão Bohm e acessibilidade.

## 3. Conflitos de interesse

O revisor deve declarar:

- vínculo com o autor, a instituição ou a plataforma Tiangong/CIQuanta;
- participação em projeto concorrente;
- relação comercial com o livro;
- qualquer interesse que possa afetar o julgamento.

Conflito não impede o parecer, mas deve ser declarado e considerado pelo editor.

## 4. Confidencialidade

- O manuscrito é confidencial até a publicação.
- O revisor não deve compartilhar o texto, os dados ou os pareceres.
- O revisor não deve usar o material para projeto próprio.
- O parecer pode ser publicado de forma anônima ou assinada, conforme política.

## 5. Formulário de avaliação

Cada dimensão recebe nota **0–10** e um comentário com **evidência** (página,
lauda, experimento, tabela). Nota sem evidência não conta.

| Dimensão | 0–10 | Evidência | Comentário |
|---|---:|---|---|
| **Contribuição didática em PT-BR** |  |  |  |
| **Contribuição científica original** |  |  |  |
| **Integração Bohm + computação + hardware** |  |  |  |
| **Rigor e reprodutibilidade** |  |  |  |
| **Avaliação independente / peer review** |  |  |  |
| **Contribuição global ponderada** |  |  |  |
| **Potencial de impacto na educação brasileira** |  |  |  |
| **Como livro-texto internacional de referência** |  |  |  |
| **Profundidade científica** |  |  |  |
| **Repetição e extensão** |  |  |  |
| **Lean 4 e limites da prova formal** |  |  |  |

### 5.1 Critérios de nota

| Nota | Significado |
|---:|---|
| 0–2 | ausente, incorreto ou não verificável |
| 3–4 | presente, mas frágil; lacunas importantes |
| 5–6 | adequado, com limitações claras |
| 7–8 | forte, com pequenas lacunas |
| 9 | excelente, referência na categoria |
| 10 | excepcional, sem lacuna relevante e com evidência independente |

## 6. Perguntas obrigatórias

1. O livro **substitui** alguma obra de referência? Em quê?
2. O livro **complementa** Nielsen & Chuang, Preskill, Bohm & Hiley ou Eisberg
   & Resnick? Onde?
3. As trilhas são **coerentes** com os níveis N0, N1 e N2?
4. Os experimentos são **executáveis** por um leitor com o PDF?
5. Os cálculos são **reproduzíveis** à mão?
6. As afirmações de hardware têm **task ID, data e limite**?
7. O Lean 4 prova o que o texto diz que ele prova?
8. O livro **exagera** alguma conclusão? Onde?
9. A linguagem é **acessível** sem infantilizar?
10. A repetição é **pedagógica** ou **editorial**?

## 7. Parecer estruturado

O revisor deve entregar:

```text
1. Resumo do manuscrito (5–8 linhas)
2. Pontos fortes (3–5, com evidência)
3. Pontos fracos (3–5, com evidência)
4. Erros conceituais ou factuais (com página/lauda)
5. Problemas de método ou estatística
6. Problemas de acessibilidade ou ética
7. Nota por dimensão (tabela acima)
8. Recomendação: aceitar / aceitar com correções / revisar / rejeitar
9. Correções obrigatórias (numeradas)
10. Correções opcionais
```

## 8. Resposta do autor

O autor deve responder item por item:

| Comentário | Resposta | Alteração | Onde |
|---|---|---|---|
|  |  |  |  |

Regra: **não responder “discordo” sem argumento e evidência**. Se não for
corrigir, explicar por quê e registrar o limite.

## 9. Prazo e fluxo

| Etapa | Prazo |
|---|---|
| Convite e confirmação | 7 dias |
| Leitura e parecer | 30 dias |
| Resposta do autor | 21 dias |
| Réplica do revisor | 14 dias |
| Decisão editorial | 14 dias |

## 10. O que este pacote não faz

- Não cria revisores.
- Não garante aceite.
- Não substitui uma editora.
- Não transforma o livro em publicação peer-reviewed.
- Não autoriza usar o nome de instituições ou plataformas como endosso.

> **Regra:** um parecer honesto pode dizer “não é 10/10”. O objetivo do pacote
> não é obter nota alta; é obter **evidência independente** para que a nota seja
> merecida.

## 11. Modelo de convite

```text
Prezado(a) [nome],

Convido você a avaliar o manuscrito “Do Bit ao Todo — 3000 Laudas de Física Quântica”, de
Marcelo Claro Laranjeira. O livro tem 3580 páginas, 3000 laudas, 100 fichas,
18 experimentos e verificação formal em Lean 4.

Sua função é avaliar [dimensão] com base no formulário anexo. O prazo é de 30
dias. O manuscrito é confidencial. Declare conflitos de interesse.

O parecer pode ser assinado ou anônimo. Não há remuneração nesta edição; o
resultado será publicado com o livro e com os pareceres.

Atenciosamente,
[editor]
```

## 12. Critério de 10/10 em peer review

Para que a dimensão “avaliação independente / peer review” chegue a 10/10, são
necessários:

- pelo menos três pareceres externos;
- revisores de instituições diferentes;
- declaração de conflitos;
- correções implementadas e registradas;
- parecer final publicado;
- dados e código disponíveis para os revisores;
- resposta pública aos pontos principais.

Sem isso, a nota continua 3/10 — e dizer o contrário seria overclaim.
