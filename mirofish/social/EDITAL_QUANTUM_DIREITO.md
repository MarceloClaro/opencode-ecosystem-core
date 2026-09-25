# Perfis Editoriais — Computação Quântica e Direito (R-976.19)

Síntese dos **12 novos perfis editoriais** adicionados em 2026-09-24 ao
`mirofish/social/editorial_profiles.py` (6 de computação quântica + 6 de direito),
no mesmo padrão do R-976.17 (health/IA) e R-976.18 (educação original).

> **ANTI-OVERCLAIM (R110):** estes são **rótulos de simulação** para calibração de
> perfis de banca. Traduzem critérios públicos em pesos de avaliação; não
> representam parecer real, afiliação, promessa editorial nem reproduzem conteúdo
> protegido das revistas. Ver `CORRIGENDUM.md`.

## Computação Quântica (6)

| Perfil (chave) | Periódico | Decisões editoriais mais marcantes (fonte oficial) |
|---|---|---|
| `npj Quantum Information` | npj Quantum Information (Nature Portfolio) | OA CC BY; 1ª decisão mediana ~5 dias; cover letter + reporting summary/checklists na submissão; deduplicação vs arXiv; políticas Nature Portfolio |
| `Quantum` | Quantum — The open journal for quantum science | Overlay journal: submissão via **arXiv (quant-ph)**; **sem taxas** (APC zero); **sem limite de formato/comprimento** (explícito); revisão com pareceristas nomeados; critérios: correção técnica, significância, clareza/reprodutibilidade, reivindicações honestas, escopo; contributions + disclosure LLM |
| `Quantum Science and Technology` | QST (IOP Publishing) | **Altamente seletivo**: "essential reading" + interesse da comunidade ampla + **impacto duradouro**; Letters (justification statement, prioridade), Papers (avanço significativo), Topical reviews convidadas, Roadmaps (2–3 pp/seção); **single anonymous** |
| `IEEE Transactions on Quantum Engineering` | IEEE TQE | **Gold open access**; **sem page limit** (all-electronic); APC **USD 1.995** (descontos IEEE 5% / Society 20%, não combináveis); regular/review/tutorial; escopo: engenharia de fenômenos quânticos + supercondutividade, magnética, micro-ondas, fotônica, processamento de sinais |
| `ACM Transactions on Quantum Computing` | ACM TQC | Submissões via **Manuscript Central** (desde 01/01/2026); transição **100% OA** (APC com waivers/discounts); revisão minor em **30 dias**; revisão hierárquica EIC → seção → Senior Associate Editors; **ORCID obrigatório**; conferências estendidas declaram substancial novidade |
| `Quantum Information Processing` | QIP (Springer) | **Single-blind**; abstract **150–250** palavras; fonte editável + PDF obrigatórios; template LaTeX recomendado |

## Direito (6)

| Perfil (chave) | Periódico | Decisões editoriais mais marcantes (fonte oficial) |
|---|---|---|
| `Revista Direito GV` | Revista Direito GV (FGV Direito SP) | Desk review (ineditismo, adequação temático-metodológica, requisitos formais); **duplo-cego → simples-cego quando há preprint** (revisor conhece autoria); **5 palavras-chave em PT/EN/ES**; desidentificação; resenhas **≤2.000 palavras (incl. referências)**; ScholarOne; sem taxas; software de similaridade |
| `Revista Direito e Práxis` | Revista Direito e Práxis (UERJ) | Trilíngue (PT/EN/ES); desk review (resposta em até **30 dias** se fora do escopo) + **duplo-cega com 2 avaliadores ad hoc** (stricto sensu); **3º avaliador se divergência**; declaração rigorosa de conflito de interesses; preprints permitidos (SciELO/arXiv/bioRxiv/medRxiv); sem APC |
| `Revista de Direito Administrativo` | RDA (FGV Direito Rio) | Desde **1945**; desk review ≤15 dias; **2–3 pareceristas doutores** por área; titulação mínima **doutor**; **máximo 2 autores (1 doutor)**; sem inclusão de autor após submissão; ABNT; **CC BY-NC-ND 4.0** |
| `Seqüência (UFSC)` | Seqüência — Estudos Jurídicos e Políticos (UFSC) | Avaliação **duplo-cega**; **iThenticate** antiplágio; **CC BY 4.0**; sem taxas; ABNT; fluxo contínuo |
| `Revista de Estudos Empíricos em Direito` | REED | Foco em **pesquisa empírica jurídica** (dados e evidências); duplo-cega com **exogenia de pareceristas ≥75%**; **nomes de avaliadores publicados** (ciência aberta); ORCID; formatos .doc/.docx/.odt; avaliação média ~6 meses (parecerista ~1 mês) |
| `Suprema (STF)` | Suprema — Revista de Estudos Constitucionais (STF) | **Semestral**; duplo-cega com **≥2 pareceristas externos**; **3º parecerista se impasse**; **até 3 coautores** (titulação de doutor primordial); PT/EN/ES/FR/IT; fluxo contínuo; sem taxas |

## Fontes oficiais consultadas (2026-09-24)

- https://www.nature.com/npjqi/for-authors-and-referees + https://www.nature.com/npjqi/content-types
- https://quantum-journal.org/authors/
- https://publishingsupport.iopscience.iop.org/journals/quantum-science-technology/about-quantum-science-technology
- https://tqe.ieee.org/submission-process
- https://dl.acm.org/journal/tqc/author-guidelines
- https://link.springer.com/journal/11128/submission-guidelines
- https://periodicos.fgv.br/revdireitogv/politicaeditorial
- https://www.e-publicacoes.uerj.br/revistaceaju/about/submissions
- https://periodicos.fgv.br/rda/about/submissions
- https://periodicos.ufsc.br/index.php/sequencia/about/submissions
- https://revistareas.unifesp.br/index.php/reed/about
- https://suprema.stf.jus.br/index.php/suprema/about/submissions

## Notas de atualidade e cuidado

- **Quantum** não cobra nem impõe formato — é o perfil mais "leve" em
  `length_limit`; a seletividade está na exigência de correção técnica e
  significância, refletida em pesos altos de originalidade/teoria/metodologia.
- **QIP (Springer)** e **QST (IOP)** usam modelos distintos: single-blind vs
  single anonymous. O perfil QST reflete "essential reading + impacto duradouro",
  o QIP é mais aberto a contribuições incrementais.
- **Direito GV**: o diferencial mais forte é o **deslocamento duplo-cego →
  simples-cego na presença de preprint** — raro entre periódicos Qualis A1 de
  direito e capturado no `special_gates`.
- **RDA** tem **restrições de autoria e titulação** (máx. 2 autores, ≥1 doutor)
  que apareceram em poucos outros perfis do catálogo — destaque para o gate.
- **Suprema/STF** e **Seqüência/UFSC** representam o polo institucional público
  (STF e universidade federal), complementares ao polo privado (FGV) e
  universitário (UERJ).
- Pesos: periódicos quânticos privilegiam originalidade/teoria/metodologia/
  reprodutibilidade; periódicos de direito privilegiam teoria/originalidade/
  clareza e (REED) metodologia/evidências/estatística.