---
name: edicao-antirrepeticao
description: Audita e reduz repetição em obras longas sem perder lentes, checkpoints, pontes ou sequência didática. Use quando o PDF estiver extenso ou repetitivo; não corte conteúdo por métrica lexical sem revisão humana.
metadata:
  version: "1"
  origem: "R1099 — auditoria das 3000 laudas"
---

# Edição antirrepetição

## Medir

```bash
python3 scripts/auditar_repeticoes.py
```

Ler `livro_pixel/RELATORIO_REPETICOES.md`:
- palavras;
- parágrafos repetidos;
- n-gramas;
- laudar por lente.

## Distinguir

- **Template necessário:** topo, ponte, resultado, rodapé.
- **Repetição pedagógica:** mesma lente em conceitos diferentes.
- **Repetição editorial:** guia, microprática e caveat repetidos sem função.

## Cortar

1. Guia da ponte: uma vez no capítulo da Ponte Sonora.
2. Microprática genérica: remover; manter checkpoint específico.
3. Caveat longo: encurtar sem perder o limite.
4. Remissão em vez de repetir.

## Preservar

- 3000 laudas, 10 lentes, 3 níveis.
- Hanzi, pinyin, tons e microfrase.
- Checkpoint, rigor, resultado, `[Gxxx]` e `[Fxxx]`.

## Critério

Comparar antes/depois e atualizar o relatório. Redução sem perda de objetivo é
a meta; redução por número é risco.
