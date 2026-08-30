# Recibo local de validação — SPEC-935-R457

## Escopo

Implementação da **proposta pós-Recamán** documentada no manual técnico RAG
(SPEC-935-R456): um conjunto de artefatos que diversificam de forma
**determinística** e **estruturada** o ranking pós-ranqueado da arquitetura RAG,
fechando a lacuna de métrica de diversidade do painel `EnhancedRAG.metrics()`.

A implementação é **aditiva, de baixo acoplamento e não-invasiva**: cria o módulo
`rag/recaman.py` e acrescenta um campo novo (`diversity`) ao dicionário de
métricas, sem alterar o contrato dos campos existentes nem o comportamento dos
ranqueadores atuais.

## Artefatos implementados (GREEN)

| Artefato | Descrição |
|---|---|
| `rag/recaman.py` | Novo módulo 100% stdlib, determinístico. |
| `recaman_sequence(n)` | Gera os `n` primeiros termos de A005132 (oráculo OEIS). |
| `ArtifactType` | Enum de classificação semântica (paper/regulation/judicial/clinical/generic). |
| `AnchorResolver` | Deduplica por âncora canônica (identidade de fonte/âmago). |
| `RecamanDiversifier` | Diversifica ranking via offsets `(1 + a_m) mod N` (Tabela 1 do manual). |
| `CanonicalContextPacker` | Posiciona âncoras distintas de forma determinística (mitiga "lost in the middle"). |
| `diversity(items)` | Métrica Div(S) ∈ [0,1] sobre âncoras canônicas (Eq. 6.1 do manual). |
| `EnhancedRAG.metrics()` | Integração ADITIVA: novo campo `diversity`, sem remover/renomear os 4 existentes. |

## Evidência observada

```text
25 passed in 0.34s   # tests/test_r457_recaman_diversifier.py (25 contratos GREEN)
48 passed in 0.81s   # R457 + R456 + R455
47 passed in 6.49s   # regressão R436 (enhanced_search_rag) + R99 (rag_evolved)
```

## Fidelidade matemática ao manual

- **Oráculo OEIS A005132**: `[0,1,3,6,2,7,13,...]` — confirmado por teste.
- **Tabela 1 (N=8)**: índices `(1 + a_m) mod 8 = [1,2,4,7,3,0]` — confirmado por teste.
- **Seção 5.1**: relevância primária (top-1) nunca perdida — confirmado por teste
  para vários `k`.
- **Seção 6.1**: Div(S) ≈ 0 para itens idênticos; ≈ 1 para itens disjuntos —
  confirmado por teste.
- **Custo O(N)/O(M)**: implementação iterativa com conjunto visitado; sem
  recursão, termina sempre — confirmado por teste para N até 512.

## Distinção escopo (anti-overclaim)

- A implementação **torna a capacidade e a métrica disponíveis**, mas **NÃO
  promove o diversificador ao pipeline padrão**: a flag `_DIVERSIFIER_ENABLED`
  permanece `False` e o fluxo principal fica configurável/desligado.
- **NÃO** alega ganhos empíricos de qualidade (isso exige experimento de coorte
  futuro, fora desta spec).
- **NÃO** altera ranqueamento primário (BM25/denso) nem roteamento adaptativo.

## Comandos executados

```bash
cd /home/marceloclaro/opencode-ecosystem-core
python3 -m pytest tests/test_r457_recaman_diversifier.py -q
python3 -m pytest tests/test_r457_recaman_diversifier.py tests/test_r456_manual_tecnico_rag.py tests/test_r455_readme_historico_operacional.py -q
python3 -m pytest tests/test_r436_enhanced_search_rag.py tests/test_r99_rag_evolved.py -q
python3 -m marceloclaro.cli doctor
```

## Limites conhecidos

- O `diversity` é computado sobre âncoras canônicas (source/doc_id/title), que é
  uma aproximação determinística de "âmago" sem embeddings — suficiente para a
  métrica, que pode ser refinada em ciclo futuro.
- Para `N` pequenos, offsets de Recamán repetem posições; o `diversify` pula
  posições já usadas e completa por relevância, garantindo unicidade.
- A sequência de Recamán legitimanmente revisita valores (A005132 não é injetora
  para `n` grande) — os testes refletem a definição real, não uma premissa falsa
  de termos todos distintos.
