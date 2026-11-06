# Mapa de Rotas — Molambudos

> Gerado em R289. 73 nós, 164 arestas (links bidirecionais extraídos do `molambudos.md`).

## Grafo Completo (73 nós)

![Grafo Completo](routes_full_R289.png)

**Legenda:**
- 🔴 **Vermelho** — MEM (memórias de Joaquim, 27 nós) — a história original
- 🔵 **Azul** — DOC (documentos, 18 nós) — a camada investigativa
- 🟢 **Verde** — LUC (Lúcia Mendes, 15 nós) — a investigadora contemporânea
- 🟠 **Laranja** — CONT (contaminação, 13 nós) — a metanarrativa que contamina

## Rotas Principais — MEM + LUC (42 nós)

![Rotas MEM+LUC](routes_mem_luc_R289.png)

Caminho narrativo principal: a história de Joaquim (MEM) investigada por Lúcia (LUC).

## Rotas de Contaminação — CONT + LUC + DOC (41 nós)

![Rotas CONT](routes_cont_R289.png)

Caminho da contaminação: a metanarrativa (CONT) acessada via investigação (LUC) e evidências (DOC).

---

## Métricas

| Métrica | Valor |
|:--------|:------|
| Nós totais | 73 |
| Arestas totais | 164 |
| Densidade do grafo | ~3.1% |
| Hub central | MEM-04 (A Vala) — maior número de conexões |
| Componentes conectados | 1 (grafo conexo) |
| Diâmetro do grafo | ~12 arestas (MEM-01 → CONT-13) |
