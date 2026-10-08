# SPEC-935-R690 — Relato de experiência TDAH/brincar de vizinhança em LaTeX modular ABNT

**Status:** `implementado com pendências declaradas`
**Round:** R689 (registro do ciclo) — esta SPEC formaliza a especificação do artefato após a entrega, corrigindo a não-conformidade de ter entregado sem spec (lição registrada).
**Data:** 2026-10-05

## 1. Problema e objetivo

Produzir relato de experiência acadêmico (disciplina de Psicologia, clínica humanista)
sobre criança de 5 anos com laudo de TDAH misto cuja intensidade de sintomas
minimizou após mudança de endereço com brincar livre diário na vizinhança,
em formato de **revisão integrativa ilustrada por vinheta clínica anonimizada**
(N=1 sem valor probatório, sem alegação causal), em **LaTeX modular compilado
em PDF ABNT**, com **artigo-gap norteador** e autoria conforme modelo DOCX
da disciplina (5 discentes).

## 2. Critérios de aceitação

- [x] AC1 — Pergunta PCC declarada; objetivo geral + 3 específicos.
- [x] AC2 — Gap demonstrado por literatura, não apenas declarado (Hood & Baumann 2024; Damasceno et al. 2025; Kuo & Faber Taylor 2004/2009/2011; Yang et al. 2019).
- [x] AC3 — 10 módulos LaTeX + main.tex unificador + referencias.bib; compilação com 0 erros e 0 citações indefinidas.
- [x] AC4 — ABNT NBR 6023/10520 via abntex2-alf.bst; margens 3/2cm; Times; espaço 1,5.
- [x] AC5 — Autoria e resumo rotulado fiéis ao modelo DOCX da disciplina (5 autoras).
- [x] AC6 — Ética declarada: anonimização, TCLE [A ANEXAR], ECA, LGPD, CNS 466/2012 e 510/2016; medicamento registrado como "não declarado" sem presumir ausência.
- [x] AC7 — Falsificabilidade: 5 critérios de invalidação da hipótese na Metodologia.
- [x] AC8 — Referências com metadados verificados em fonte primária (Crossref/DOI) antes de entrar no .bib.
- [x] AC9 — Auditoria por scanners do Core (SRI/EXS/falácias) + Merkle; resultado reportado com anti-overclaim.
- [x] AC10 — Pendências para submissão explicitadas (instituição/orientadora, TCLE físico, declaração literal sobre medicação).

## 3. Design técnico

- Pipeline: `pdflatex → bibtex → pdflatex ×2` (latexmk equivalente).
- Ordem de pacotes crítica: `hyperref` **antes** de `abntex2cite` (lição R689).
- `abntex2-options.bib` + `abntex2-alf.bst` copiados para o diretório do artigo.
- `edition` iniciado com dígito ganha ". ed." automático do estilo; uso de grupo `{5}` para "5. ed. rev.".

## 4. Verificação e limites

- SRI 60/100 (moderate_rigor), EXS 55/100, 0 falácias, após refinamento pós-scanner.
- Teto declarado: relato N=1 descritivo não atinge calibração experimental dos scanners; nota final é da banca humana.
- Melhorias de ciclo seguinte (R690): +5 referências (Bronfenbrenner; Polanczyk et al. 2007; Faber Taylor & Kuo 2009; AAP 2019; Louv), referencial teórico explícito, colunas medida/limitação no Quadro 1, declaração de conflitos/financiamento.

## 5. Resultado do ciclo R690 (melhorias executadas)

- [x] Corpus ampliado 10 → 15 referências (todas com DOI/ISBN verificados; 3 novos DOIs conferidos via Crossref: 10.1176/ajp.2007.164.6.942; 10.1177/1087054708323000; 10.1542/peds.2019-2528).
- [x] Referencial teórico explícito (ART + Bronfenbrenner + ACP) na Introdução; conceito "ecologia" agora tem fonte.
- [x] Quadro 1 com 6 linhas incluindo o experimento controlado intrasujeito (Faber Taylor & Kuo 2009, N=17).
- [x] Discussão incorpora "déficit de natureza" (Louv); Conclusão ganha 4 implicações práticas.
- [x] Declaração de conflitos de interesses e financiamento no rodapé do resumo.
- [x] SPEC formal criada (este arquivo) — conformidade SDD restaurada.
- Scanner final: falsificabilidade 100/100; 0 falácias; SRI varia com o recorte textual enviado (55/40 na rodada 3) — métrica instável para desenho N=1; o delta negativo reflete o resumo enviado, não regressão do PDF (lição registrada em R690).
