# SPEC-935-R146 — Modo Polana: Renderização de Fatias com Base de Encaixe

**Versão:** 1.1  
**Data:** 2026-07-17  
**Autor:** marceloclaro (Orquestrador Central)  
**Tipo:** Feature (modo alternativo de renderização)  
**TAG:** `polana-mode`, `relevo-papel`, `render-mode`

---

## 1. Objetivo

Adicionar ao motor `RelevoPapel` um **segundo modo de renderização** — `'polana'` — que
reproduz fielmente a estrutura e o estilo visual do projeto original
`3d-paper-terrain-model/reference/polana/` (SVGs `part-a.svg` a `part-d.svg`). O modo
`'classic'` existente permanece inalterado.

---

## 2. Critérios de Aceitação (CA)

### CA-01 — Constantes de modo exportadas

```js
RelevoPapel.MODE_CLASSIC === 'classic'
RelevoPapel.MODE_POLANA   === 'polana'
```

### CA-02 — Parâmetro `mode` no pipeline

`generateModel({ ..., mode: 'polana' })` → `buildCrossSlicesPages(..., { mode })` →
`renderPage(..., { mode })`.  
Todas as funções do pipeline aceitam `mode` e o propagam.  
`options.mode` default é `'classic'` para backward compatibility.

### CA-03 — Parâmetro `polanaOpts` no pipeline

`generateModel({ ..., mode: 'polana', polanaOpts: { hillshading, alignMarks, contours, notches } })`.

- `polanaOpts.notches`: boolean (default `true`) — gera os encaixes em V na base de cada fatia
- `polanaOpts.hillshading`: boolean (default `false`) — overlay de declividade
- `polanaOpts.alignMarks`: boolean (default `false`) — marcas laterais de alinhamento
- `polanaOpts.contours`: boolean (default `false`) — linhas de contorno

### CA-04 — Fatias em modo polana (estilo visual)

Quando `mode === 'polana'`, cada fatia V e H deve ser renderizada como:

- **Polyline reta** (não Bezier suave) — pontos ligados por segmentos retos
- **fill="#ffffff"** (branco sólido, sem gradiente de elevação)
- **stroke="#ff0000" stroke-width="4"** (traço vermelho 4px, como no polana)
- sem slots (V-de-cima / H-de-baixo)
- sem `profileFillColor` nem `profileStrokeColor` — cor fixa

### CA-05 — Encaixes em V (notches) nas fatias

Quando `polanaOpts.notches === true`, cada fatia recebe **7 encaixes em V**
proporcionais à largura da fatia, reproduzindo o padrão do `part-a.svg`:

- **Largura do encaixe**: ~12px na base
- **Profundidade**: ~33px abaixo da linha de dobra
- **Espaçamento**: ~40px no slice de referência (316px), escalado proporcionalmente
- **Margens**: ~14.6% à esquerda, ~9.5% à direita (proporcional à largura total)
- **Formato**: polyline fechada: `pos,baseY  pos-5,baseY+6  pos-5,baseY+33  pos-7,baseY+33  pos-7,baseY+6  pos-12,baseY`
- **Estilo**: `fill="#ffffff" stroke="#ff0000" stroke-width="4"` (idêntico à fatia)

### CA-06 — buildPolanaBasePiece (SVG separado)

`buildPolanaBasePiece(options)` retorna string SVG standalone (sem template) com:

- **3 tracks horizontais** (retângulos longos com borda):
  - Track V (superior, olive `#808000`): 24 entalhes em V espaçados ~21.3px
  - Track H (médio, blue `#0000ff`): 24 entalhes em V, alternando cores (vermelho/azul)
  - Track V2 (inferior, olive): mesmo padrão da superior
- **Cada entalhe:** `m X,baseY -5,6 0,27 -2,0 0,-27 -5,-6` com `fill="#ffffff" stroke="#808000" stroke-width="4"`
- **Labels**: identificação V/H, informações de elevação
- **Marcas de registro** (crop marks)
- **Parâmetros**:
  ```js
  {
    nVSlices: 24,          // número de fatias V
    nHSlices: 80,          // número de fatias H
    eleMin: 0,
    eleMax: 1000,
    label: 'Polana Terrain'
  }
  ```

### CA-07 — Modo clássico preservado

Quando `mode` não é especificado ou é `'classic'`, o comportamento é **exatamente o mesmo**
de antes: gradiente de cor, slots V/H cruzados, Bezier suave, hillshading, contornos,
marcas de alinhamento. Nenhuma alteração no modo classic.

### CA-08 — Extras opcionais no modo polana

Em modo polana, os extras são controlados por `polanaOpts`:

| Extra | Default | Descrição |
|-------|---------|-----------|
| `notches` | `true` | Encaixes em V na base |
| `hillshading` | `false` | Overlay semi-transparente de declividade |
| `alignMarks` | `false` | Marcas laterais de alinhamento |
| `contours` | `false` | Linhas de contorno de elevação |

### CA-09 — buildPolanaBasePiece exportada

```js
assert.ok(typeof RelevoPapel.buildPolanaBasePiece === 'function');
const svg = RelevoPapel.buildPolanaBasePiece({ nVSlices: 24, nHSlices: 80 });
assert.ok(svg.includes('<svg'));
assert.ok(svg.includes('track-v'));
assert.ok(svg.includes('track-h'));
```

### CA-10 — Numeração cumulativa das fatias (#1..#N)

Em modo `polana`, cada fatia recebe um **número cumulativo sequencial** que ajuda na
ordenação durante a montagem:

- **Fatias V**: número = índice V (1-based) → `#1 V-1 (500m)`, `#2 V-2 (400m)`…
- **Fatias H**: número = `lonSteps + índice H (1-based)` → `#11 H-1 (300m)` (se houver 10 V)  

Este número aparece como prefixo no label da fatia, no formato `#N V-k (ele m)`.

### CA-11 — Label de seção no cabeçalho das páginas

Em modo `polana`, o cabeçalho de cada página inclui a **Seção** baseada no número da página:

- Página 1 → `Relevo em Papel 3D — Seção A — Página 1 de N`
- Página 2 → `Relevo em Papel 3D — Seção B — Página 2 de N`
- Página 3 → `Relevo em Papel 3D — Seção C — Página 3 de N`
- … seguindo o alfabeto (A–Z)

Isto reproduz a organização por seções (A, B, C, D) do `all-parts-togerther.svg` de referência.

### CA-12 — Testes smoke estendidos

O smoke test existente (`tests/smoke.mjs`) deve continuar passando sem alterações.
Novos testes para modo polana:

1. `renderPage` com `mode: 'polana'` gera `<polyline` e não `<path` (bézier)
2. Saída contém `fill="#ffffff"` e `stroke="#ff0000"`
3. Saída não contém `class="slot-v"` nem `class="slot-h"` (sem slots)
4. Saída contém encaixes em V quando `polanaOpts.notches === true`
5. `buildPolanaBasePiece` gera SVG válido com tracks

---

## 3. Arquivos Afetados

| Arquivo | Tipo | Mudança |
|---------|------|---------|
| `assets/relevo-papel.js` | engine | Adicionar `MODE_CLASSIC`, `MODE_POLANA`, `generatePolanaSlice`, `buildPolanaBasePiece`; modificar `renderPage`, `buildCrossSlicesPages`, `generateModel` |
| `assets/relevo-papel/template-cut.svg` | template | Adicionar classe `.polana-slice` (opcional) |
| `tests/smoke.mjs` | teste | Adicionar testes CA-04 a CA-10 |

---

## 4. Risco e Mitigação

| Risco | Mitigação |
|-------|-----------|
| Quebrar modo classic | Parâmetro `mode` com default `'classic'`; testes existentes inalterados |
| PolanaBasePiece muito grande | Gerar uma única vez como SVG separado (não no loop de páginas) |
| Notches mal proporcionados | Usar proporções relativas à largura da fatia (não valores absolutos) |

---

## 5. Histórico

| Rev | Data | Autor | Descrição |
|-----|------|-------|-----------|
| 1.0 | 2026-07-17 | marceloclaro | Criação inicial |
| 1.1 | 2026-07-17 | marceloclaro | CA-10 (numeração cumulativa #1..#N), CA-11 (seção A/B/C no cabeçalho) |
