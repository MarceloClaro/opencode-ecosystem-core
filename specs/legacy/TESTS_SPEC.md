# Estratégia de validação

## Níveis de verificação
- **Sintática**: ABNT, ortografia, formatação (automatizado)
- **Semântica**: coerência argumentativa, aderência ao edital (revisão humana)
- **Legal**: conformidade LGPD, Resolução 39/2025 (checklist)
- **Empírica**: validação com especialistas + grupo focal (Fases 2-3)

## Casos críticos de validação

### CT-001: Anonimato do anteprojeto (valida R3)
- Verificar: zero ocorrências de "Marcelo", "Laranjeira", "OpenCode Ecosystem" como autor
- Ferramenta: grep case-insensitive no PDF extraído
- Falha se: qualquer marca de autoria no corpo do texto

### CT-002: Limite de laudas (valida R3)
- Verificar: PDF tem ≤ 7 páginas (excluindo referências)
- Ferramenta: pdf_count-pdf-pages
- Falha se: > 7 laudas

### CT-003: Margens ABNT (valida R3)
- Verificar: sup/inf = 2,5cm; esq/dir = 3,0cm
- Ferramenta: pdf_analyze-pdf-page
- Falha se: qualquer margem fora do especificado

### CT-004: Arquivo único ≤ 15MB (valida R5)
- Verificar: tamanho do PDF consolidado
- Ferramenta: filesystem_get_file_info
- Falha se: > 15MB

### CT-005: Ordem dos documentos (valida R5)
- Verificar: sequência RG → Diploma → Lattes → Ficha → Anexos → Anteprojeto
- Falha se: qualquer documento fora da ordem do edital

### CT-006: Referências com DOI verificável (valida R1)
- Verificar: cada referência tem DOI e o DOI resolve
- Ferramenta: SEEKER + fetch
- Falha se: DOI não resolve ou referência sem DOI

### CT-007: Zero travessões (valida Q1)
- Verificar: zero ocorrências de "—" (em dash) no texto
- Ferramenta: grep no source .md
- Falha se: qualquer travessão encontrado

### CT-008: Siglas expandidas (valida Q4)
- Verificar: primeira ocorrência de cada sigla tem expansão
- Ex: "LGPD (Lei Geral de Proteção de Dados)"
- Falha se: sigla usada sem expansão prévia

### CT-009: Declaração de IA preenchida (valida E2)
- Verificar: Anexo IV assinado e anexado ao PDF único
- Falha se: Anexo IV ausente ou não assinado

## O que NÃO validar automaticamente
- Qualidade argumentativa (requer julgamento humano)
- Originalidade científica (requer banca)
- Adequação do conteúdo à linha de pesquisa (requer orientador)

## Pipeline de CI
```
1. converter MD → PDF (pandoc)
2. validar CT-001 (anonimato)
3. validar CT-002 (laudas)
4. validar CT-003 (margens)
5. validar CT-004 (tamanho)
6. validar CT-007 (travessões)
7. validar CT-008 (siglas)
8. reportar: APROVADO / REPROVADO com lista de falhas
```
