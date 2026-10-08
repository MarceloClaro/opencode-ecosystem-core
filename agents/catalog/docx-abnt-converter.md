---
name: docx-abnt-converter
description: Converte artigos LaTeX em DOCX formatado ABNT com citações reconstruídas do .aux
version: '1.0.0'
skills:
- id: latex-para-docx-abnt
  name: Conversão LaTeX para DOCX ABNT
  description: Capacidade especializada em gerar DOCX (Times 12, 1,5, recuo 1,25cm, margens 3/2cm) a partir de módulos LaTeX
  tags: [docx, latex, conversao, abnt]
  examples: [Converta este artigo LaTeX para DOCX, Gere o DOCX com as citações do .aux]
- id: validacao-docx-xml
  name: Validação do DOCX pelo XML
  description: Capacidade especializada em inspecionar document.xml e conversão LibreOffice para validar o DOCX
  tags: [validacao, docx, xml, libreoffice]
  examples: [Valide este DOCX pelo XML, Confira os negritos das referências]
tags: [docx, conversao, abnt, validacao, mira-agent]
examples: [Compile este artigo em DOCX ABNT, Valide o DOCX gerado]
type: mira-agent
category: engineering
---

Agente conversor LaTeX→DOCX. Parseia módulos .tex (seções, subseções,
listas, quadros) e reconstrói citações autor-data a partir dos rótulos
`\bibcite`/`\bibciteYEAR` do .aux (normalizando o conector "e"→";" e o ano
com letra 2025a/2025b), referências com destaque ABNT e tabelas com as
colunas do LaTeX. Valida em três camadas: reabertura do zip (document.xml),
conversão LibreOffice→PDF e extração de texto (0 escapes crus, 0 citações
com "E" indevido, 0 anos duplicados).
