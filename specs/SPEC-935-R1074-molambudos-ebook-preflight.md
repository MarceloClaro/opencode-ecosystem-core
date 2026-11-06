# SPEC-935-R1074 — EPUB, preflight KDP e acessibilidade do Molambudos

**Status:** EPUB implementado e validado localmente; preflight executado com
falhas documentadas; PDF tagged bloqueado pelo toolchain.  
**Objetivo:** produzir uma edição EPUB de leitura a partir da canônica, medir a
prontidão KDP do miolo/capa e registrar o estado real da acessibilidade PDF.

## 1. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| R1 | EPUB derivado da canônica | Fonte `main.tex` + 84 fragmentos + epílogo; nenhum texto de v2/Diário |
| R2 | Estrutura completa | 5 partes, 84 seções de fragmento, epílogo e backmatter |
| R3 | Metadados e capa | Title, dois autores, `pt-BR`, ISBN, publisher, capa |
| R4 | Navegação | TOC com 5 partes, 84 links de fragmento; 0 links quebrados |
| R5 | Higiene técnica | 0 LaTeX cru, 0 imagens ausentes, 0 referências não resolvidas |
| R6 | Validação | ZIP/OPF/nav/spine válidos; 84 seções com corpo; razão de palavras 0,9–1,1 |
| R7 | Preflight KDP | Medir trim, páginas, margens, fontes, imagens, capa, lombada, sangria, ISBN e barras |
| R8 | Não overclaim | EPUB sem EPUBCheck; preflight local não substitui previewer KDP; PDF tagged não declarado |
| R9 | Release | EPUB, fonte, manifesto e preflight dentro de `release/2026-11-05/` |
| R10 | Gate | `tests/test_r1074_molambudos_epub.py` valida manifestos e release local |

## 2. Entregáveis

| Caminho | Papel |
|---|---|
| `scripts/build_molambudos_epub.py` | gerador reprodutível do EPUB |
| `scripts/preflight_molambudos_kdp.py` | verificador local de KDP |
| `reports/r1074/epub_manifest.json` | hash, contagens e validação do EPUB |
| `reports/r1074/preflight_kdp.json` | 13 passes, 5 avisos, 3 falhas |
| `reports/r1074/tagged_pdf_status.json` | bloqueio e evidências do PDF tagged |
| `reports/r1074/README.md` | parecer consolidado |
| `reports/r1074/evidence/*.log` | logs das tentativas de tagging |
| `literatura/molambudos/release/2026-11-05/epub/` | EPUB, fonte, CSS e manifesto |
| `literatura/molambudos/release/2026-11-05/preflight/` | relatório de KDP |
| `tests/test_r1074_molambudos_epub.py` | gate |

## 3. Falhas de KDP registradas

1. Capa a ~163 DPI; mínimo KDP de 300 DPI.
2. Reserva de barras 2,15×0,95 in; requisito 2,0×1,2 in.
3. Reserva no canto inferior esquerdo; LTR pede o canto inferior direito.

Avisos: código fictício na arte, sangria do miolo, imagens <300 DPI, PDF não
tagged e página 435 branca.

## 4. Fora de escopo

- Corrigir a arte da capa sem os originais em alta resolução.
- Publicar, enviar à KDP ou distribuir.
- Declarar conformidade EPUB 3, PDF/UA, WCAG ou Qualis.
- Substituir leitura humana, prova digital/física ou validação externa.

## 5. Limites

O preflight mede arquivos; não aprova o livro. O EPUB é uma edição de leitura
derivada; o PDF canônico segue como referência de impressão. O PDF tagged não
foi produzido.
