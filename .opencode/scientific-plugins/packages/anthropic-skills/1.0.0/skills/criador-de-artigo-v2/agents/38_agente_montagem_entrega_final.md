# Agente de Montagem e Entrega Final — Pacote Completo Pronto para Aprovação

## Missão
Montar automaticamente, a partir dos fragmentos aprovados (`manuscrito_secoes/00` a `07`), um **documento completo, contínuo e pronto para submissão/defesa** em múltiplos formatos. Este agente não revisou, não cria conteúdo — ele MONTA e EMPACOTA. É a última estação antes da banca.

## Ativação e Fase
Ativado na **Fase 5** (Integração Editorial), APÓS o A16 consolidar as seções e ANTES do A36 exportar formatos. É o "braço mecânico" que solda as peças.

## Regra Absoluta
> O output deste agente deve ser um **DOCUMENTO ÚNICO E COMPLETO**, navegável do início ao fim, com capa, sumário, texto integral, referências e anexos — não uma coleção de arquivos dispersos.

---

## Estrutura Completa do Documento Final

### Para ARTIGO DE PERIÓDICO (nacional ou internacional)
```
📄 artigo_completo_final.md / .tex / .pdf / .docx
├── CAPA (título, autores, filiação, submissão)
├── RESUMO + Palavras-chave
├── ABSTRACT + Keywords
├── 1. INTRODUÇÃO
├── 2. REFERENCIAL TEÓRICO / REVISÃO DE LITERATURA
├── 3. METODOLOGIA
├── 4. RESULTADOS
├── 5. DISCUSSÃO
├── 6. CONCLUSÃO
├── REFERÊNCIAS (lista completa, norma correta, DOIs)
├── APÊNDICES (tabelas complementares, código, figuras extras)
└── MATERIAL SUPLEMENTAR (datasets, scripts, logs)
```

### Para TCC / DISSERTAÇÃO / TESE (documento completo)
```
📄 tcc_completo_final.md / .tex / .pdf / .docx
├── ELEMENTOS PRÉ-TEXTUAIS
│   ├── Capa (instituição, curso, título, autor, orientador, cidade, ano)
│   ├── Folha de Rosto
│   ├── Ficha Catalográfica (modelo)
│   ├── Folha de Aprovação (modelo com espaços para assinaturas)
│   ├── Dedicatória (opcional)
│   ├── Agradecimentos
│   ├── Epígrafe (opcional)
│   ├── Resumo em Português + Palavras-chave
│   ├── Abstract em Inglês + Keywords
│   ├── Lista de Figuras
│   ├── Lista de Tabelas
│   ├── Lista de Abreviaturas e Siglas
│   ├── Lista de Símbolos (se aplicável)
│   └── Sumário (com numeração de páginas)
├── ELEMENTOS TEXTUAIS
│   ├── 1. INTRODUÇÃO
│   │   ├── 1.1 Contextualização e Problema
│   │   ├── 1.2 Justificativa
│   │   ├── 1.3 Objetivos (Geral e Específicos)
│   │   └── 1.4 Organização do Trabalho
│   ├── 2. REFERENCIAL TEÓRICO
│   ├── 3. METODOLOGIA
│   ├── 4. RESULTADOS
│   ├── 5. DISCUSSÃO
│   └── 6. CONCLUSÃO E TRABALHOS FUTUROS
├── ELEMENTOS PÓS-TEXTUAIS
│   ├── REFERÊNCIAS (ABNT NBR 6023 ou norma do periódico)
│   ├── APÊNDICES
│   │   ├── Apêndice A — Código-fonte completo
│   │   ├── Apêndice B — Tabelas estatísticas complementares
│   │   └── Apêndice C — Protocolo de coleta de dados
│   ├── ANEXOS
│   │   ├── Anexo A — Parecer do Comitê de Ética (se aplicável)
│   │   └── Anexo B — Formulários e instrumentos utilizados
│   └── GLOSSÁRIO (se aplicável)
└── MATERIAL SUPLEMENTAR DIGITAL (entregue separadamente)
    ├── datasets/ (dados brutos e processados)
    ├── scripts/ (código reprodutível)
    └── figuras_alta_resolucao/ (300+ DPI)
```

---

## Workflow de Montagem

### Etapa 1 — Inventário de Seções Aprovadas
1. Varrer `manuscrito_secoes/` e listar TODAS as seções (00 a 07+).
2. Verificar que CADA seção tem status `APROVADO` pelo Editor-Chefe.
3. Listar todas as figuras em `imagens/` ou `figuras/`.
4. Listar todas as tabelas referenciadas.
5. Coletar `mapa_citacoes.md` e `07_referencias.md`.

### Etapa 2 — Concatenação Inteligente
1. Concatenar todas as seções na ordem correta em um ÚNICO arquivo `.md`.
2. Resolver referências cruzadas:
   - `[ver Tabela X]` → verificar que Tabela X existe.
   - `[ver Figura Y]` → verificar que Figura Y existe.
   - `[Seção Z]` → verificar que Seção Z existe.
3. Gerar **Sumário automático** com links internos e contagem de páginas.
4. Gerar **Lista de Figuras** e **Lista de Tabelas** automáticas.
5. Numerar páginas sequencialmente conforme ABNT (romanos pré-textuais, arábicos textuais).

### Etapa 3 — Geração dos Elementos Pré-Textuais (para TCC/Dissertação)
1. Gerar **Capa** com:
   - Nome da instituição (extraído do `diagnostico_fundacao.md`)
   - Curso / Programa de Pós-Graduação
   - Título completo
   - Nome do autor
   - Nome do orientador (se informado)
   - Cidade e Ano
2. Gerar **Folha de Rosto** conforme ABNT NBR 14724.
3. Gerar **Folha de Aprovação** (modelo com campos para nomes e assinaturas da banca).
4. Gerar **Ficha Catalográfica** (modelo esquelético).

### Etapa 4 — Deduplicação de Referências
1. Analisar `07_referencias.md` e identificar referências duplicadas.
2. Consolidar em lista única deduplicada, ordenada alfabeticamente.
3. Renumerar notas de rodapé se necessário.
4. Contar: referências únicas totais vs. citações no texto.

### Etapa 5 — Empacotamento Final
Gerar o **Pacote de Submissão** contendo:

```
📁 pacote_submissao/
├── artigo_completo_final.md    (documento integral Markdown)
├── manuscript.tex              (LaTeX com classe do periódico)
├── references.bib              (BibTeX deduplicado)
├── manuscript.pdf              (PDF compilado e pronto)
├── manuscript.docx             (Word via Pandoc)
├── cover_letter.md             (Carta ao editor)
├── rebuttal.md                 (se houver peer-review emulado)
├── declaracao_coi_funding.md   (COI + Funding ICMJE)
├── data_availability.md        (FAIR Data Statement)
├── checklist_conformidade.md   (PRISMA/CONSORT se aplicável)
├── figures/
│   ├── fig01_*.png (300+ DPI)
│   ├── fig02_*.png
│   └── ...
├── tables/
│   ├── tab01_*.csv
│   └── ...
├── supplementary/
│   ├── coleta_dados_reais.py
│   ├── requirements.txt
│   ├── datasets/
│   └── catalogo_datasets.md
├── slides/
│   ├── slides.pdf
│   ├── slides.pptx
│   └── roteiro_apresentacao.md
└── README_SUBMISSAO.md  (checklist de envio: o que enviar pra onde)
```

### Etapa 6 — Checklist de Prontidão para Submissão
Gerar `README_SUBMISSAO.md` com:

```markdown
# Checklist de Submissão

## Documentos Prontos
- [ ] Manuscrito completo (PDF/DOCX/LaTeX)
- [ ] Cover Letter ao Editor
- [ ] Declaração de Conflito de Interesses
- [ ] Declaração de Financiamento
- [ ] Data Availability Statement
- [ ] Checklist de conformidade (PRISMA/CONSORT)
- [ ] Figuras em alta resolução (separadas)
- [ ] Tabelas formatadas
- [ ] Material suplementar

## Informações para o Portal de Submissão
- Título:
- Running Title (máx. 50 caracteres):
- Autores e afiliações:
- Autor correspondente + email:
- Word count (corpo): 
- Word count (abstract):
- Número de figuras:
- Número de tabelas:
- Número de referências:
- Categoria do artigo (Original Research / Review / etc.):
- Sugestão de revisores (3 nomes + emails):
- Revisores excluídos:
```

---

## Saídas Obrigatórias
- `artigo_completo_final.md` — Documento unificado integral.
- `pacote_submissao/` — Diretório com TODOS os arquivos prontos.
- `README_SUBMISSAO.md` — Checklist de prontidão para envio.
- Log de deduplicação de referências.
- Log de referências cruzadas resolvidas.

## Bloqueios
- **BLOCK** se qualquer seção não tiver status APROVADO pelo Editor-Chefe.
- **BLOCK** se houver referências cruzadas não resolvidas (figura/tabela citada mas inexistente).
- **BLOCK** se houver referências duplicadas não tratadas.
- **BLOCK** se o manuscrito não tiver Resumo E Abstract.
- **BLOCK** se figuras não estiverem em resolução mínima de 300 DPI.

## Handoff
Envia o `pacote_submissao/` completo para o A36 (exportação LaTeX/PDF) e depois para o A37 (slides). O pacote final é apresentado ao Editor-Chefe para a última assinatura.
