# SPEC-935-R1078 — Book Studio Universal

**Status:** proposta; nenhuma implementação iniciada.  
**Data:** 2026-11-05  
**Objetivo:** transformar o Book Studio em um estúdio editorial universal —
diagramador, editor e assistente literário — por contratos e adaptadores,
cobrindo os gaps G1–G15 identificados no Molambudos.

## 1. Não objetivos

- Não publicar, enviar à KDP ou distribuir.
- Não substituir revisão humana, ISBN, ficha catalográfica ou direitos.
- Não declarar qualidade literária, PDF/UA pleno ou aceite editorial.
- Não incorporar código GPL/AGPL como biblioteca.
- Não reescrever a edição canônica nem as variantes R1075/R1076/R1077.

## 2. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| R1 | Contratos versionados | `DocumentIR`, `DesignTokens`, `PrintSpec`, `EditorialReport`, `LiteraryReport`, `A11yReport`, `MetadataRecord`, `ReleaseManifest` com schema e teste |
| R2 | KDP core-native | fórmula de capa/lombada/bleed/trim implementada e testada contra casos conhecidos; sem dependência externa |
| R3 | Gate de licença | GPL/AGPL somente `external_cli` ou `reference`; `library` bloqueada por teste |
| R4 | Sandbox de adaptadores | subprocesso, temp dir, limites, rede desligada por padrão, versão registrada |
| R5 | Produção | PDF 160×230 mm; fontes embutidas; imagens ≥300 DPI; TAC <300%; PDF/A ou PDF/UA quando aplicável |
| R6 | EPUB | EPUBCheck + Ace; alt text, nav e reading order checados |
| R7 | Editorial | LanguageTool/Vale/textstat com relatório pt-BR; nenhuma aprovação automática |
| R8 | Literário | personagens, relações, timeline, POV, motivos e inconsistências com confiança explícita |
| R9 | Metadados | ONIX 3.0 válido; ISBN validado; DOI/Crossref quando aplicável |
| R10 | Tradução | baseline COMET/chrF; glossário; revisão humana obrigatória |
| R11 | Proveniência | SHA-256 de entradas/saídas; `ReleaseManifest`; opcional C2PA/RO-Crate |
| R12 | Anti-overclaim | nenhum relatório declara 10/10, Qualis, publicação ou validação externa |

## 3. Arquitetura

```
core/contracts/      schemas e validadores
core/adapters/       um adaptador por ferramenta externa
core/gates/          licença, sandbox, contraste, DPI, TAC, acessibilidade
core/studio/         jobs, assets, previews, aprovações
core/native/         KDP, spine, design tokens, manifest, checksums
```

Cada adaptador implementa:

```
check() -> capabilities
plan()  -> inputs/outputs/network/time
run()   -> artifact + log + hashes
verify() -> independent gate
report() -> structured JSON
```

## 4. Fase 0 (R1078) — escopo mínimo

1. `book.json` canônico com trim, bleed, páginas, spine, fontes, cores,
   imagens, ISBN e hash.
2. Calculadora KDP de capa/lombada com testes de mesa.
3. `DesignTokens` com paleta HEX/CMYK, contraste e tipografia.
4. `ReleaseManifest` com SHA-256 e checksums.
5. Gate de licença no CI.
6. Teste de schema e cobertura dos 15 gaps.

**Fora da fase 0:** integração real de Typst/Quarto/WeasyPrint, tradução,
áudio/vídeo e UI.

## 5. Critérios de aceitação da fase 0

- `python3 -m pytest tests/test_r1078_book_studio_landscape.py -q` passa.
- `book.json` valida contra schema.
- Calculadora KDP reproduz pelo menos 3 casos de referência.
- Nenhum repositório GPL/AGPL aparece como `library` no manifesto.
- Todos os gaps G1–G15 têm ao menos 3 candidatos mapeados.
- Relatório declara limites e ausência de execução.

## 6. Riscos

| Risco | Mitigação |
|---|---|
| Licença GPL/AGPL contaminar o Core | gate no CI; CLI externo; revisão jurídica |
| Ferramenta externa quebrar | versão fixada; contrato; teste de fumaça |
| PDF/UA incompleto | validador + checklist manual + declaração de limites |
| Capa 300 DPI inexistente | bloquear publicação; não fazer upscale artificial |
| Assistente literário alucinar | confiança explícita; citação de trecho; revisão humana |
| Tradução automática publicada | gate humano obrigatório; COMET/chrF como diagnóstico |

## 7. Definição de pronto

A fase 0 está pronta quando os contratos, a calculadora KDP, o gate de licença e
o manifesto de release estiverem testados e documentados, sem que nenhuma
ferramenta externa tenha sido embutida no Core.
