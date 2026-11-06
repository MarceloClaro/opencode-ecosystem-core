# SPEC-935-R1080 — Assistente de Romance Psicológico (Linhagem Molambudos)

**Status:** implementado como perfil gerenciado e pacote de estilo; não é
publicação, não é terapia e não é validação literária.
**Data:** 2026-11-05
**Perfil:** `romance-psicologico-molambudos`
**Teste:** `tests/test_r1080_style_catalog.py`

## 1. Objetivo

Disponibilizar ao orquestrador um especialista de escrita e revisão de romance
de terror psicológico, com voz sensorial e sistêmica, técnicas de indução
narrativa e protocolo de tradução PT-BR/EN/ZH.

## 2. Não objetivos

- Não é terapeuta, diagnóstico ou promessa de efeito clínico.
- Não é NLP clínico, hipnose ou mentalismo real.
- Não gera imagens sem modelo/API.
- Não publica, não envia à KDP e não cria ISBN.
- Não substitui leitura crítica, tradução humana ou revisão de sensibilidade.
- Não declara 10/10, Qualis ou aceite editorial.

## 3. Requisitos

| ID | Requisito | Critério |
|---|---|---|
| R1 | Catálogo de estilos | 16 estilos com sintaxe, léxico, sensorialidade, POV, tensão, motivos, riscos e prompt |
| R2 | Tradução | `translation` com `pt-BR`, `en` e `zh` em cada estilo |
| R3 | Protocolo de tradução | princípio, PT-BR, EN, ZH e QA com back-translation e sensibilidade |
| R4 | Ética | ficção, aviso de conteúdo, sem alvo real, sem coerção, sem alegação clínica, sem plágio, documento ficcional marcado |
| R5 | Tag lines | motor com 6 padrões e limite explícito |
| R6 | Gates | 8+ critérios de qualidade, incluindo ética e anti-overclaim |
| R7 | Prompt | system prompt com papel, voz, técnicas, ética, tradução e formato de saída |
| R8 | Perfil gerenciado | `agent_profile_action` cria cartão válido, com capacidade exclusiva e permissões |
| R9 | Teste | `tests/test_r1080_style_catalog.py` passa |
| R10 | Anti-overclaim | nenhuma alegação clínica, nenhum 10/10 |

## 4. Capacidades

- `literary_style`
- `psychological_tension`
- `sensory_writing`
- `narrative_induction`
- `translation_ptbr_en_zh`
- `content_safety`
- `tagline_engineering`
- `manuscript_revision`

## 5. Contrato de saída

Toda entrega deve conter:

- `status`
- `findings`
- `evidence` (arquivo/hash/linhas ou recibo)
- `limitations`

Nenhuma entrega promove confiança por autoavaliação. Sem evidência, devolver
`blocked` ou `partial`.

## 6. Ética

O perfil pode escrever horror psicológico intenso, violência, corpo, doença,
abuso e trauma **como ficção**. Não pode:

- mirar pessoas, famílias ou comunidades reais;
- instruir coerção, autoagressão, fraude ou manipulação de terceiros;
- apresentar documento ficcional como prova histórica;
- prometer cura, diagnóstico ou eficácia clínica;
- copiar voz de autor vivo sem declaração;
- publicar tradução automática sem revisão humana.

## 7. Aceitação

1. `python3 -m pytest tests/test_r1080_style_catalog.py -q` passa.
2. O catálogo tem 16 estilos e 3 línguas por estilo.
3. O perfil é criado com `managed-v1`, capacidade exclusiva e permissões
   compatíveis.
4. O `opencode.json` é regenerado e o cartão aparece no catálogo.
5. O relatório declara limites e ausência de validação externa.

## 8. Arquivos

| Caminho | Conteúdo |
|---|---|
| `reports/r1080/style_catalog.json` | catálogo de estilos |
| `reports/r1080/assistant_prompt.md` | system prompt |
| `reports/r1080/codex_image_workflow.md` | fluxo de imagem com Codex |
| `reports/r1080/repos_analysis.md` | análise dos 23 repositórios |
| `tests/test_r1080_style_catalog.py` | gate do catálogo |
| `agents/catalog/romance-psicologico-molambudos.md` | cartão gerenciado |
