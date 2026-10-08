# SPEC-935-R679 — Livro Core Didático com Enredo, Quadripartição Funcional→Reprodução e Citações com DOI Ativo

**Status:** proposta (orquestrador marceloclaro) — 05 out. 2026
**Escopo:** `livro-core/` (LaTeX A4, tema escuro marinho+ouro+papel)
**Problema:** o `livro-core` existente (19 módulos, 73 `\citref`, `main.pdf` compilável) é técnico-referencial; falta camada didática narrativa que conduza leitor leigo e técnico do uso funcional à estrutura, à teoria e à reprodução independente, com citações reais de DOI ativo justificando cada abordagem e cada cálculo.
**Estado-alvo:** livro didático-científico com enredo contínuo (personagens Ana leiga, Bruno técnico, narrador Orquestrador), quadripartição explícita Funcional→Estrutural→Teórica→Reprodução em cada jornada, cálculos resolvidos passo a passo lastreados em literatura, compilação `pdflatex main.tex` verde e guarda `check.py` verde.

## 1. Critérios de aceitação (gate SDD fail-closed)

1. [CA1] Três novos módulos criados em `livro-core/`: `mod-00a-enredo-prefacio.tex`, `mod-00b-jornada-leitor.tex`, `mod-15-epilogo-reproducao.tex`; `main.tex` os inclui (prólogo no `frontmatter`, epílogo no `backmatter` antes de apêndices).
2. [CA2] Enredo contínuo: Ana (professora leiga, Crateús), Bruno (dev técnico) e narrador MarceloClaro aparecem nos três módulos; cada capítulo alterna parágrafo narrativo (intuição) → vocabulário → mecanismo → evidência → limite, sem pressupor conhecimento prévio.
3. [CA3] Quadripartição explícita: cada módulo-jornada declara as quatro leituras — (F) Funcional: o que entra/sai por fora; (S) Estrutural: quem faz e onde mora no código; (T) Teórica: por que funciona segundo modelo; (R) Reprodução: como refazer e conferir localmente.
4. [CA4] Mínimo 10 novos `\citref` com DOI ativo e verificado externamente (webfetch/doi.org em 05 out. 2026), fora de `tcolorbox` (parágrafo corrido), cada um com {referência ABNT}{DOI}{relevância}{trecho original literal}{tradução livre}{AUTOR, ANO, p.}: Sweller 1988 `10.1207/s15516709cog1202_4` (método didático carga cognitiva); Flavell 1979 `10.1037/0003-066X.34.10.906` (metacognição); Nii 1986 `10.1609/aimag.v7i2.537` (blackboard); Wooldridge & Jennings 1995 `10.1017/S0269888900008122` (agentes); Vaswani et al. 2017 `10.48550/arXiv.1706.03762` + ACM `10.5555/3295222.3295349` (atenção); Ioannidis 2005 `10.1371/journal.pmed.0020124` (PPV/anti-overclaim); Wilkinson et al. 2016 `10.1038/sdata.2016.18` (FAIR); Peng 2011 `10.1126/science.1213847` (reprodutibilidade); Fucci et al. 2017 `10.1109/TSE.2016.2616877` e Rafique & Misic 2013 `10.1109/TSE.2012.28` (TDD granularidade).
5. [CA5] Mínimo 4 cálculos resolvidos passo a passo com hipóteses explícitas: (C1) risco de agregação `P=1-p^N` com N=216, p=0,99 → ~89% e variante p=0,999; (C2) atenção `softmax(QK^T/√d_k)V` com exemplo numérico 2×2; (C3) PPV de Ioannidis `PPV=(1-β)R/((1-β)R+α)` com exemplo R=1:10, α=0,05, poder 0,8; (C4) contagem-inventário reproduzível (`opencode.json`, `specs/`, `mci/`) com comando e interpretação.
6. [CA6] Nenhum DOI de memória: cada DOI listado resolve em `https://doi.org/<doi>`; trechos originais copiados do resumo/texto do editor; traduções rotuladas livres; norma ABNT NBR 6023:2018 (referências) e NBR 10520:2023 (chamada numérica em nota).
7. [CA7] Compilação verde: `python3 livro-core/check.py` exit 0; `pdflatex main.tex` gera `main.pdf` sem erro `!`; sem emoji (U+2600–U+2BFF), sem `\begin{flowch}[..][`, chaves balanceadas, `\elemento` em linha única balanceada.
8. [CA8] Anti-overclaim R110 preservado: nenhum “Qualis A1 / verificado / superhuman” sem validação externa; limites de cada cálculo declarados em caixa `aviso`; números de checkout datados como fotografia.
9. [CA9] Reflexão registrada: ciclo de evolução em `evolution/cycles.json` + memória MetaBus com lições; `doctor` sem novas falhas.

## 2. Roteamento e execução (TDD)

- Perceber: inventário `livro-core/` + `doctor` + MetaBus (feito 05/10/2026).
- Especificar: esta SPEC (gate antes de escrever).
- Delegar/Executar: escrita direta pelo orquestrador (3 arquivos), verificação de DOI por webfetch/search, compilação local.
- Verificar: `check.py` + `pdflatex` + sondagem DOI + revisão anti-overclaim.
- Refletir: registrar ciclo + lições.

## 3. Riscos

- DOI que deixa de resolver → remover antes de compilar (regra R110).
- `\citref` dentro de box quebra nota → usar só em parágrafo corrido.
- Editar `macros.tex`/`mod-11` pode quebrar 19 módulos → não editar; novos arquivos autocontidos.

## 4. Referências desta SPEC (verificadas 05/10/2026)

- SWELLER, J. Cognitive load during problem solving. Cogn. Sci. 12:257-285, 1988. DOI 10.1207/s15516709cog1202_4.
- VASWANI, A. et al. Attention is all you need. NIPS 30, 2017. DOI 10.48550/arXiv.1706.03762.
- IOANNIDIS, J. P. A. Why most published research findings are false. PLoS Med 2:e124, 2005. DOI 10.1371/journal.pmed.0020124.
- WILKINSON, M. D. et al. FAIR Guiding Principles. Sci. Data 3:160018, 2016. DOI 10.1038/sdata.2016.18.
- PENG, R. D. Reproducible research in computational science. Science 334:1226-1227, 2011. DOI 10.1126/science.1213847.
- FUCCI, D. et al. Dissection of TDD process. IEEE TSE 43:597-614, 2017. DOI 10.1109/TSE.2016.2616877.
- RAFIQUE, Y.; MISIC, V. B. Effects of TDD: meta-analysis. IEEE TSE 39:835-856, 2013. DOI 10.1109/TSE.2012.28.
