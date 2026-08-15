# evo-51 — R420: Apêndice A (glossário) e avaliação da q-estatística

## Objetivo

1. Responder conceitualmente à pergunta do usuário sobre o uso de
   q-exponencial/q-estatística (Tsallis) na análise e no artigo.
2. Implementar o Apêndice A — Glossário de símbolos, códigos e abreviaturas
   no MD canônico e no LaTeX, para facilitar a leitura.

## Avaliação conceitual: q-exponencial e q-estatística

**Conclusão: não implementar na análise central.** Fundamentos:

1. **Sem ganho inferencial**: a inferência do artigo já é robusta à
   não-normalidade por dois caminhos independentes — erros padrão
   clusterizados por país (painel FE) e bootstrap por país não paramétrico
   (R419). A q-estatística não alteraria nenhuma conclusão.
2. **Sem ancoragem teórica**: a estatística não extensiva de Tsallis
   generaliza a entropia para sistemas com interações de longo alcance e
   fortes correlações (motivação física). O desenho aqui é observacional
   associativo; aplicar q-gaussiana exigiria justificativa teórica que o
   estudo não possui.
3. **Diagnóstico empírico realizado** (resíduos da regressão simples,
   n = 4374): curtose excedente +3,27; assimetria −1,11; P(|z|>2) = 3,86%
   (menor que 4,55% da normal); P(|z|>3) = 0,80% (maior que 0,27%).
   A não-normalidade vem principalmente da heterogeneidade entre países
   (absorvida pelos efeitos fixos) e da assimetria, não de um mecanismo de
   caudas que a q-gaussiana modelaria com ancoragem teórica.
4. **Parcimônia e anti-overclaim**: acrescentar q-exponencial seria
   cosmético, aumentaria complexidade e o risco de alegação sem suporte —
   contra as regras do ecossistema.
5. **Alternativa oferecida**: diagnóstico suplementar de caudas (material
   online) se o usuário quiser explorar — sem mudar as conclusões.

## Mudanças (R420)

1. **SPEC-935-R420** criada.
2. **Apêndice A** no MD canônico (após Referências): A.1 símbolos
   estatísticos (ρ, ρ_níveis, ρ_1ªdif, Δ, ln, IC95%, p, n, H0, H1, p.p.,
   D.P., β, WGI_media); A.2 códigos WDI/WGI (NY.GDP.PCAP.KD,
   NY.GDP.PCAP.KD.ZG, SE.TER.ENRR, SE.XPD.TOTL.GD.ZS, GB.XPD.RSDV.GD.ZS,
   NV.IND.MANF.ZS, BX.KLT.DINV.WD.GD.ZS, TX.VAL.TECH.MF.ZS,
   SP.URB.TOTL.IN.ZS, SP.DYN.LE00.IN, SI.POV.GINI, CC.EST, GE.EST, PV.EST,
   RQ.EST, RL.EST, VA.EST); A.3 abreviaturas (WDI, WGI, PIB, P&D, FE,
   LOOCV, RF, ROC, GroupKFold, ML, ISO3, RBEP, IDE, SHA-256, UTC).
3. **Espelho LaTeX** com `\appendix`, tabelas com `\resizebox{\textwidth}`
   (0 Overfull/Underfull), sem `\caption*` (bug de numeração), com nota de
   fonte após `\end{tabular}` (regra R411) e títulos em negrito.
4. **Testes R420** (15): existência, subseções, símbolos/códigos/siglas no
   MD e TeX, anti-overclaim no texto inteiro, PDF presente, log sem
   Overfull/Underfull.
5. **Correção de regressões**: teste R410 `test_referencias_ordem_alfabetica`
   agora ignora o bloco "## Apêndice" ao extrair a lista de referências.

## Verificação

- Suíte R408–R420: **323 testes passed** (R420: 15).
- LaTeX: 19 páginas; 0 Overfull; 0 Underfull.
- Doctor após registro do ciclo: 10/12 pass, 0 failed (warns pré-existentes).

## Lições

- Qualquer conteúdo pós-referências (apêndice) exige ajustar os testes que
  extraem a lista de referências pelo marcador "Referências".
- `\caption*` é proibido no projeto (bug de numeração R411) — usar título em
  `\noindent\textbf{}` + nota de fonte após `\end{tabular}`.
- "P&D" no TeX é `P\&D`; testes de conteúdo do TeX devem usar a variante
  escapada.
