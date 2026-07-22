# SPEC-935-R147 — CuttingSheet: Espaçamento Configurável entre Fatias (--gap-cm)

**Versão:** 1.0  
**Data:** 2026-07-17  
**Autor:** marceloclaro (Orquestrador Central)  
**Tipo:** Feature (parâmetro de layout A4)  
**TAG:** `cutting-sheet`, `gap-cm`, `paginacao`

---

## 1. Objetivo

Tornar configurável o **espaçamento entre fatias nas folhas de corte A4** geradas pelo módulo `CuttingSheet`, substituindo as constantes fixas `COL_GAP` e `ROW_GAP` por um valor dinâmico em centímetros, conversível automaticamente para pontos SVG no viewBox A4.

---

## 2. Justificativa

- O valor fixo anterior (`ROW_GAP = 15pt`) correspondia a ~0,42cm, sem relação clara com uma medida física.
- Usuários que imprimem em papel A4 precisam saber exatamente qual a distância entre fatias para planejar o corte e a montagem.
- Diferentes tipos de papel (gramatura, tesouras) podem exigir gaps diferentes — 0,3cm para papel mais fino, 1,0cm para papel mais grosso com margem de segurança.

---

## 3. Critérios de Aceitação (CA)

### CA-01 — Constante `CM_IN_PTS`

```ruby
CuttingSheet::CM_IN_PTS  # => 35.43307086619048 (A4_W / 21.0)
```

O viewBox A4 (744,09 × 1052,36pt) mapeia para 210 × 297mm. Logo 1cm físico = 744,09 / 21,0 ≈ 35,43pt no viewBox.

### CA-02 — Constante `DEFAULT_GAP_CM`

```ruby
CuttingSheet::DEFAULT_GAP_CM  # => 0.5
```

O espaçamento padrão entre fatias é **0,5 cm** (5 mm).

### CA-03 — Parâmetro `gap_cm:` em `CuttingSheet.build`

```ruby
CuttingSheet.build(elevations, lat_steps:, lon_steps:, one_cm_in_pts:, total_length_cm:, gap_cm: 0.5)
```

- `gap_cm:` é opcional (default = `DEFAULT_GAP_CM`).
- O valor é convertido internamente para pontos SVG: `gap_pt = (gap_cm * CM_IN_PTS).round(2)`.
- `gap_pt` substitui o uso de `COL_GAP` e `ROW_GAP` em `layout_pages` e `render_page`.

### CA-04 — Opção `--gap-cm` no CLI

```
ruby 3d-paper-model.rb --place "Cânion do Rio Poti" --gap-cm 0.3
ruby 3d-paper-model.rb --gap-cm 1.0 --paginate parte
```

- Aceita Float, default `CuttingSheet::DEFAULT_GAP_CM` (0,5).
- O valor é propagado para `CuttingSheet.build(gap_cm: gap_cm)`.

### CA-05 — Gap menor → mais fatias por página (menos páginas)

- Com `--gap-cm 0.3` (~10,63pt), cabem mais fatias por coluna → menos folhas A4.
- Com `--gap-cm 1.0` (~35,43pt), cabem menos fatias → mais folhas A4.
- Teste automatizado valida que `gap_cm=0.3` produz ≤ páginas que `gap_cm=1.0`.

### CA-06 — Saída SVG preserva qualidade

- Marcas de registro nos 4 cantos (independentes do gap).
- Cabeçalho com Seção A/B/C/D e numeração de página.
- Polylines renderizadas com coordenadas transladadas corretamente.

### CA-07 — Retrocompatibilidade

- `gap_cm:` não informado → usa `DEFAULT_GAP_CM` (0,5) → **comportamento novo** (antes era 15pt ≈ 0,42cm).
- `--gap-cm` não informado no CLI → default 0,5cm.
- Nenhum teste existente quebra (50 testes, 140 asserções).

---

## 4. Implementação

### 4.1. `lib/cutting_sheet.rb`

**Constantes adicionadas/modificadas:**

```ruby
CM_IN_PTS       = A4_W / 21.0       # 35,43 pt/cm
DEFAULT_GAP_CM  = 0.5
```

**Método `build` alterado:**

```ruby
def build(elevations_in_pixels, lat_steps:, lon_steps:, one_cm_in_pts:,
          total_length_cm:, gap_cm: DEFAULT_GAP_CM)
  gap_pt = (gap_cm * CM_IN_PTS).round(2)
  # ...
  pages = layout_pages(groups, gap_pt)
  pages.each_with_index.map { |page_slices, idx|
    render_page(page_slices, page_num: idx + 1, total_pages: total, gap_pt: gap_pt)
  }
end
```

`COL_GAP` e `ROW_GAP` removidos — substituídos pelo parâmetro `gap_pt` passado para `layout_pages` e `render_page`.

### 4.2. `3d-paper-model.rb`

**Opção adicionada:**

```ruby
opts.on('--gap-cm N', Float, "Espacamento entre fatias nas folhas A4 em cm (default #{CuttingSheet::DEFAULT_GAP_CM})")
```

**Uso:**

```ruby
gap_cm = options[:gap_cm] || CuttingSheet::DEFAULT_GAP_CM
sheets = CuttingSheet.build(pixels, ..., gap_cm: gap_cm)
```

### 4.3. `test/test_cutting_sheet.rb` (novo)

13 testes cobrindo:
- Constantes `DEFAULT_GAP_CM`, `CM_IN_PTS`
- Conversão 0,3 / 0,5 / 1,0 cm → pt
- `build` com gap default e customizado
- Diferentes gaps → diferentes contagens de página
- Validação de saída SVG (tags, seções, marcas)

---

## 5. Exemplos de Uso

```bash
# Gap padrao (0,5cm) — 4 folhas A4 para 24 fatias
ruby 3d-paper-model.rb --place "Cânion do Rio Poti" --paginate poti

# Gap reduzido (0,3cm) — mais fatias por pagina
ruby 3d-paper-model.rb --place "Grand Canyon" --gap-cm 0.3 --paginate canyon

# Gap ampliado (1,0cm) — mais paginas, mais espaco para corte
ruby 3d-paper-model.rb --bbox 48.6,19.3,48.7,19.5 --gap-cm 1.0 --paginate polana
```

---

## 6. Histórico de Revisão

| Versão | Data | Descrição |
|---|---|---|
| 1.0 | 2026-07-17 | Criação — parâmetro `--gap-cm` e `gap_cm:` em CuttingSheet |
