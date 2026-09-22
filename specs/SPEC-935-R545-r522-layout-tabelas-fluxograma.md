# SPEC-935-R545 — Correção de layout das tabelas e do fluxograma R522

**Status:** SDD executável  
**Data:** 2026-09-19  
**Escopo:** Manuscrito `manuscrito_porescrito799_R522` — versão v30 observada e versão de leitura/revisor.

## 1. Problema

O usuário reportou que as tabelas e o fluxograma do manuscrito R522 apresentam sobreposição textual e/ou extrapolam as margens. Isso compromete legibilidade, aderência editorial e leitura do PDF.

## 2. Objetivo

Reenquadrar o fluxograma PRISMA-ScR e as Tabelas 1–2 dentro da largura útil do documento, removendo sobreposição textual e preservando os dados consolidados do ciclo R544 (corpus final n=21).

## 3. Critérios de aceitação

- **CA1 — Fluxograma:** a Figura 1 deve ser substituída por versão compacta, sem texto sobreposto, com blocos legíveis e largura adequada à página.
- **CA2 — Imagem no DOCX:** a imagem embutida deve ter largura máxima igual ou inferior à largura útil da página A4 após margens.
- **CA3 — Tabelas:** as Tabelas 1 e 2 devem usar autofit/colunas fixas compatíveis com a largura útil, fonte reduzida e quebra de linha controlada.
- **CA4 — Dados preservados:** nenhum valor de n, percentual ou ID da matriz pode ser alterado.
- **CA5 — PDF:** o PDF final deve ser gerado e permanecer dentro do limite editorial de 15–20 páginas, sem resíduos autorais ou internos.
- **CA6 — Rastreabilidade:** atualizar README e registrar R545 no EvolutionRegistry com hashes finais.

## 4. Estratégia técnica

1. Recriar o fluxograma com matplotlib em formato vertical compacto e caixas largas o suficiente para reduzir quebras internas.
2. Inserir imagem com largura controlada no DOCX por `python-docx`.
3. Definir largura de página e margens A4; aplicar largura fixa nas tabelas e fonte 7–8 pt, principalmente na coluna de IDs.
4. Converter DOCX para PDF via LibreOffice.
5. Auditar páginas, resíduos e hashes.
