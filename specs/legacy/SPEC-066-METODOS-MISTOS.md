# SPEC-066: Métodos Mistos — Design Sequencial e Convergente

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Métodos de Investigação
**Dimensão:** metodos
**Palavras-chave:** métodos mistos, sequencial, convergente, QUAN, qual

---

## 1. Problema

Métodos mistos (sequencial e convergente) são fundamentais para o paradigma pragmatista e estão ausentes no ecossistema. Esta SPEC habilita ambas as variações, destravando 2 categorias em `metodos`.

## 2. Definição

- **Misto sequencial (QUAN → qual / qual → QUAN):** Uma fase quantitativa seguida de fase qualitativa (ou vice-versa), com integração na interpretação.
- **Misto convergente:** Coleta simultânea de dados QUAN + qual com triangulação na análise.

## 3. CTs

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SPEC-066 existe com definições de ambos os designs | ✅ |
| CT-02 | Regra co_occurs com paradigmas.Pragmatista registrada | ✅ |
| CT-03 | Skill associada para execução de métodos mistos | ✅ |

## 4. Integração

- `paradigmas.Pragmatista` enables ambos os métodos mistos
- Ambos co_occorrem com `raciocinio.Abdutivo`
- Misto convergente co_occorre com `dados.Dados qualitativos (entrevistas)`
