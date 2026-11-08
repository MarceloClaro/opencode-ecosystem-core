# Reavaliação comparativa do livro quântico — R1101

**Data:** 2026-11-08
**Obra avaliada:** *3000 Laudas de Física Quântica: do bit ao todo — Bohm, onda piloto e informação quântica do fundamental ao PhD*.
**Versão observada:** PDF de 3553 páginas, 3000 laudas, 100 fichas, 400 notas de cálculo, 3000 códigos únicos.
**Natureza:** avaliação editorial e comparativa. Não é peer review, certificação, estudo de eficácia ou parecer editorial.

> **Escopo:** esta rodada avalia o livro quântico. *Molambudos* é uma obra literária e exige outro conjunto de comparações; não é misturado aqui.

## 1. Método

A avaliação usa seis fontes internas:

- `PROFUNDIDADE_CIENTIFICA.md` — cobertura e limites;
- `LEDGER_AFIRMACOES.md` — status de cada afirmação;
- `RELATORIO_REPETICOES.md` — repetição lexical;
- `PACOTE_PEER_REVIEW.md` — critérios de revisão;
- `AVALIACAO_EFICACIA.md` — protocolo, não resultado;
- `GJQ_RESULTADOS.md` e `docs/gjq-runtime/*.json` — Bell/CHSH e proveniência.

A comparação é **fit-for-purpose**: cada obra responde a um público e a um objetivo diferente. Uma nota única para todas seria enganosa.

## 2. Critérios e pesos

| Dimensão | Peso | Pergunta |
|---|---:|---|
| Fundamentos físicos | 15% | cobre postulados, medida, fase, emaranhamento e interpretação? |
| Informação/computação quântica | 15% | cobre circuitos, algoritmos, complexidade e correção de erro? |
| Bohm e interpretação | 10% | trata a ontologia bohmiana com seriedade e limite? |
| Prática e hardware | 15% | liga ideia, código, counts, simulador e hardware? |
| Didática e autoinstrução | 15% | progressão, lentes, checkpoints, gabarito e leitura autônoma? |
| Exercícios e avaliação | 10% | há prática, solução e instrumento de avaliação? |
| Rigor, citações e provas | 10% | fontes, DOI, ledger, Lean e separação de status? |
| Reprodutibilidade | 5% | código, dados, task IDs, hashes e build? |
| Produção e navegação | 5% | PDF, links, índice, tipografia, acessibilidade e portabilidade? |
| Validação externa | 10% | peer review, adoção, eficácia, ISBN/DOI e tradução? |

**Total:** 100%.

## 3. Matriz de cobertura conceitual

Legenda: **●** cobertura forte/central; **◐** parcial ou limitada; **○** ausente/fora do escopo.

| Obra | Fundamentos | Info/computação | Bohm | Prática | Didática |
|---|---|---|---|---|---|
| **Este livro** | ● | ◐ | ● | ● | ● |
| Nielsen & Chuang | ● | ● | ○ | ◐ | ◐ |
| Preskill (NISQ/notas) | ● | ● | ○ | ◐ | ◐ |
| Bohm & Hiley | ● | ○ | ● | ○ | ◐ |
| Eisberg & Resnick | ● | ○ | ○ | ◐ | ● |
| Qiskit Textbook | ◐ | ● | ○ | ● | ◐ |
| Bernhardt | ● | ◐ | ○ | ○ | ● |
| Hidary | ◐ | ● | ○ | ● | ◐ |
| Feynman (QED/Lectures) | ● | ○ | ○ | ○ | ● |
| Peat | ◐ | ○ | ◐ | ○ | ● |
| Quantum Country | ◐ | ◐ | ○ | ◐ | ● |

## 4. Matriz de rigor, entrega e validação

| Obra | Exercícios/soluções | Rigor/formal | Reprodutibilidade | Produção | Validação externa |
|---|---|---|---|---|---|
| **Este livro** | ◐ | ● | ● | ◐ | ○ |
| Nielsen & Chuang | ● | ● | ◐ | ● | ● |
| Preskill | ◐ | ● | ◐ | ◐ | ● |
| Bohm & Hiley | ○ | ● | ○ | ● | ● |
| Eisberg & Resnick | ● | ● | ○ | ● | ● |
| Qiskit Textbook | ◐ | ◐ | ● | ◐ | ◐ |
| Bernhardt | ◐ | ◐ | ○ | ● | ● |
| Hidary | ◐ | ◐ | ◐ | ● | ● |
| Feynman | ◐ | ● | ○ | ● | ● |
| Peat | ○ | ◐ | ○ | ● | ◐ |
| Quantum Country | ◐ | ◐ | ◐ | ◐ | ◐ |

**Leitura:** “● em validação externa” significa adoção canônica, edição editorial ou circulação ampla — não um experimento de eficácia. Nenhuma obra desta lista passou por um ensaio controlado comparável ao protocolo do livro.

## 5. Forças e limites por obra

| Obra | Força | Limite | Use quando |
|---|---|---|---|
| **Este livro** | integra Bohm, informação quântica, código, hardware, Lean e proveniência em PT-BR; 3000 laudas e 100 fichas | 3553 páginas, repetição de template, sem peer review/eficácia/ISBN/DOI/tradução | ponte didática em português, do bit ao PhD |
| Nielsen & Chuang | referência completa de computação e informação quântica | matemática densa; não cobre Bohm nem operação de hardware real | profundidade em algoritmos, canais e QEC |
| Preskill | panorama NISQ, complexidade e fronteira | notas avançadas, não é curso introdutório | pesquisa e fronteira NISQ |
| Bohm & Hiley | ontologia bohmiana técnica e sistemática | não cobre computação quântica | interpretação e fundamentos |
| Eisberg & Resnick | física quântica geral, histórica e experimental | não cobre informação/computação quântica | base de física quântica |
| Qiskit Textbook | prática de circuitos, algoritmos e hardware | muda rápido; menos fundamentos e interpretação | aprender fazendo com Qiskit |
| Bernhardt | introdução matemática acessível | sem hardware, Bohm ou escala | primeiro curso de computação quântica |
| Hidary | abordagem aplicada e de engenharia | menos fundamentos e filosofia | engenharia e implantação |
| Feynman (QED/Lectures) | clareza e intuição ímpares | não é texto de informação quântica | intuição e ensino conceitual |
| Peat | escrita científica e contexto filosófico | não é livro-texto nem manual | contexto cultural e filosófico |
| Quantum Country | retenção por repetição espaçada | ensaio online, não referência completa | autoestudo com retenção |

## 6. Nota do livro por dimensão

| Dimensão | Peso | Nota | Evidência | Lacuna |
|---|---:|---:|---|---|
| Fundamentos físicos | 15% | 8,5 | postulados, medida, Bell, Bohm, QFT, ruído | menos profundidade matemática que Nielsen/Preskill |
| Info/computação | 15% | 7,0 | circuitos, Deutsch–Jozsa, Grover, Shor, VQC, QEC panorâmico | algoritmos e QEC não são implementação completa |
| Bohm/interpretação | 10% | 8,5 | Bohm como lente, ordem implicada, diálogo, limites | não substitui Bohm & Hiley |
| Prática/hardware | 15% | 9,0 | manual, Python, Qiskit/PennyLane/Cirq, GJQ, counts, task IDs | hardware executado é limitado; grande parte é simulador |
| Didática/autoinstrução | 15% | 8,5 | N0–N2, 10 lentes, checkpoints, 100 fichas, 400 notas | 3553 páginas e repetição dificultam leitura linear |
| Exercícios/avaliação | 10% | 7,0 | fichas, gabarito, checkpoints, protocolo de eficácia | não há estudo de eficácia concluído |
| Rigor/formal | 10% | 8,0 | ledger, Lean, DOI, limites explícitos | Lean cobre identidades específicas, não todo o livro |
| Reprodutibilidade | 5% | 9,0 | JSONs, task IDs, QASM hashes, build script | depende de conta/chave para execução real |
| Produção/navegação | 5% | 7,5 | 3553 pp, 3000 códigos, links internos e PDF versionado | PDF escuro/A5, repetição, sem EPUB/audiobook |
| Validação externa | 10% | 2,5 | pacote de peer review e protocolo | nenhum parecer, nenhum dado de eficácia, sem ISBN/DOI |

### Conta da nota

```text
(8,5×15 + 7,0×15 + 8,5×10 + 9,0×15 + 8,5×15
 + 7,0×10 + 8,0×10 + 9,0×5 + 7,5×5 + 2,5×10) / 100
= 8,375
≈ 8,4/10
```

**Nota anterior:** 8,2/10.
**Variação:** +0,2, puxada pelo apêndice GJQ, pelos resultados explícitos, pela tipografia justificada/hifenizada e pelo PDF versionado com build reproduzível.
**Intervalo subjetivo:** 7,8–8,8. A nota é um julgamento editorial; não é certificação.

## 7. Onde o livro é único

Nenhuma obra comparada faz, ao mesmo tempo:

- sequência N0 → N1 → N2 em português;
- Bohm como lente explícita, sem convertê-lo em prova;
- manual → simulação → hardware → síntese;
- 100 fichas, 400 notas de cálculo e 3000 laudas;
- ledger de afirmações e verificação Lean;
- apêndice GJQ com Bell/CHSH, task IDs, counts e QASM hashes;
- build reproduzível com `pyphen` pt-BR e PDF versionado.

O valor está na **integração didática**, não na substituição de uma referência canônica.

## 8. Onde o livro perde

| Comparação | O livro perde porque |
|---|---|
| Nielsen & Chuang | não cobre álgebra, algoritmos, canais e QEC com a mesma profundidade |
| Preskill | não está na fronteira NISQ nem na análise de complexidade |
| Bohm & Hiley | não desenvolve a ontologia bohmiana com o mesmo detalhe técnico |
| Eisberg & Resnick | não é um curso completo de física quântica geral |
| Qiskit Textbook | não acompanha a velocidade de atualização dos frameworks |
| Bernhardt/Hidary | não é um livro curto, portátil ou de curso semestral |
| Feynman/Peat | não tem a mesma fluência de divulgação ou contexto cultural |
| Quantum Country | não usa repetição espaçada como mecanismo central |

Além disso:

- **Validação externa:** 0 pareceres, 0 dados de eficácia, sem ISBN/DOI, sem edição inglesa.
- **Repetição:** 451.411 palavras, 21.031 parágrafos repetidos; parte é template, parte é candidata a corte.
- **Tamanho:** 3553 páginas em A5 e tema escuro; a edição de curso/print é um projeto separado.
- **Acessibilidade:** sem EPUB, audiobook ou versão de alto contraste para impressão.
- **Inconsistência documental:** `PACOTE_PEER_REVIEW.md`, `EDICAO_ENXUTA.md` e `INTERNATIONAL_EDITION.md` ainda citam 3580 páginas; o PDF atual tem 3553.

## 9. Correções pendentes no livro

| Prioridade | Arquivo | Correção |
|---|---|---|
| P0 | `PACOTE_PEER_REVIEW.md` | 3580 → 3553 páginas |
| P0 | `EDICAO_ENXUTA.md` | 3580 → 3553 páginas |
| P0 | `INTERNATIONAL_EDITION.md` | 3580 → 3553 páginas |
| P0 | `PROFUNDIDADE_CIENTIFICA.md` | acrescentar FAS-GPU `S=2,871094 ± 0,043506` como simulador; separar de Guoji08 `S=2,383` |
| P0 | `LEDGER_AFIRMACOES.md` | adicionar linha do Bell/CHSH GJQ como `measured`/`calculated` no simulador, com task IDs |
| P0 | PDF | recompilar depois das correções e atualizar contagem/tamanho no README |
| P1 | `PACOTE_PEER_REVIEW.md` | executar 3 pareceres externos; hoje a nota de peer review é 3/10 |
| P1 | `AVALIACAO_EFICACIA.md` | aprovar no CEP e executar o estudo; hoje é protocolo |
| P1 | metadados | ISBN/DOI e edição inglesa |
| P2 | `RELATORIO_REPETICOES.md` | revisar os 30 parágrafos mais repetidos e a edição enxuta |
| P2 | produção | EPUB, versão clara para impressão, audiolivro e revisão de acessibilidade |
| P3 | adoção | usar em curso/piloto e medir retenção; publicar também resultados negativos |

## 10. O que levaria a 9/10

Não é “mais páginas”. É evidência externa e edição:

1. três pareceres externos assinados, de instituições diferentes;
2. estudo de eficácia com CEP, grupo de comparação e retenção;
3. ISBN/DOI e ficha catalográfica definitiva;
4. edição inglesa revisada;
5. copyediting e índice remissivo;
6. EPUB e versão print-ready;
7. redução de repetição sem perder a sequência;
8. adoção documentada em curso ou clube de leitura.

Sem esses itens, a nota fica em **8,4/10**; com eles, 9/10 é plausível. 10/10 exigiria, além disso, replicação independente e contribuição reconhecida na área.

## 11. Veredito

**8,4/10 — obra didática singular, não referência canônica.**

| Se você quer… | Use… |
|---|---|
| começar em português, do bit ao PhD | **este livro** |
| profundidade em computação/informação quântica | Nielsen & Chuang; Preskill |
| ontologia bohmiana técnica | Bohm & Hiley |
| física quântica geral | Eisberg & Resnick |
| prática com Qiskit | Qiskit Textbook |
| introdução matemática curta | Bernhardt |
| engenharia aplicada | Hidary |
| intuição e clareza | Feynman |
| contexto filosófico | Peat |
| retenção por repetição espaçada | Quantum Country |

O livro não substitui nenhuma delas. Ele faz uma coisa que nenhuma delas faz sozinha: **conduzir o leitor em português da ideia ao circuito, ao hardware e ao limite, com proveniência explícita**.

## 12. Referências

- NIELSEN, M. A.; CHUANG, I. L. *Quantum Computation and Quantum Information*. 10th Anniversary ed. Cambridge: Cambridge University Press, 2010. DOI: <https://doi.org/10.1017/CBO9780511976667>.
- PRESKILL, J. Quantum Computing in the NISQ era and beyond. *Quantum*, v. 2, p. 79, 2018. DOI: <https://doi.org/10.22331/q-2018-08-06-79>.
- BOHM, D.; HILEY, B. J. *The Undivided Universe: An Ontological Interpretation of Quantum Theory*. London: Routledge, 1993.
- EISBERG, R.; RESNICK, R. *Quantum Physics of Atoms, Molecules, Solids, Nuclei, and Particles*. 2. ed. New York: Wiley, 1985.
- QISKIT. *Qiskit Textbook*. Disponível em: <https://github.com/Qiskit/textbook>. Acesso em: 2026-11-08. Licença Apache-2.0.
- BERNHARDT, C. *Quantum Computing for Everyone*. Cambridge, MA: MIT Press, 2019.
- HIDARY, J. D. *Quantum Computing: An Applied Approach*. 2. ed. Cham: Springer, 2021.
- FEYNMAN, R. P. *QED: The Strange Theory of Light and Matter*. Princeton: Princeton University Press, 1985.
- FEYNMAN, R. P.; LEIGHTON, R. B.; SANDS, M. *The Feynman Lectures on Physics*, v. III. Reading: Addison-Wesley, 1965.
- PEAT, F. D. *From Certainty to Uncertainty: The Story of Science and Ideas in the Twentieth Century*. Washington: Joseph Henry Press, 2002.
- MATUSCHAK, A.; NIELSEN, M. *Quantum Country*. 2019. Disponível em: <https://quantum.country>. Acesso em: 2026-11-08.
