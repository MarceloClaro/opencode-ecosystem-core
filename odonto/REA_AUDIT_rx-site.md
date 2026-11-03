# Auditoria REA — site `rx.engenhariaorofacial.com.br`

- **Data:** 2026-10-15
- **Ferramenta:** REA v6.4.0 (`ecosystem_rea`, operação `analyze`), evidência integral
- **Artefato:** `.opencode/rea/evidence/8b638ccbfaf7ccccce13e448d4facc564b567cbe1665b0e25d43dc565975ae3b.json`
- **Nível de alegação:** inspeção estática de artefato público; **não** é auditoria de
  segurança, nem atestação de funcionamento, nem validação de conteúdo clínico.

## 1. Método

1. Cópia local do site (para análise sem execução remota): `index.html` (104.814 B),
   `navigation.js` (1.581 B), `editor.js` (121.767 B), `navigation.css` (2.549 B)
   → `/tmp/opencode/rx-site/`.
2. `ecosystem_rea` operações `status` → `catalog` → `session` → `analyze(path=/tmp/opencode/rx-site)`.
3. Resultado do `analyze`: 12,3 s, 2 arquivos JS parseados, 21.668 nós AST,
   0 falhas de parse, 0 contradições, 12 findings. `editor.js` truncado por
   orçamento estático (declarado).

## 2. Achados (evidência)

| Categoria | Achado | Leitura |
|---|---|---|
| Identidade | `sha256:d49b4a1157680305f2cc4f45564e0695dd1560fdb236ac03e8d16ae6581768d0` (index.html) + 3 hashes de assets | artefato congelado por digest de conteúdo (`global-exact`) |
| Endpoints de rede | `/admin/api/session`, `/admin/api/logout`, `/feedback`, `/segment/sam` | há camada administrativa, telemetria de feedback e endpoint de **segmentação** (`sam` → provável Segment-Anything) |
| Armazenamento | `session-storage:panoramica-review-notice`, `local-storage` | aviso de revisão ("Panoramica") persistido no cliente |
| Assets | `editor.js`, `navigation.js` | SPA de edição/visualização de imagem |
| Grafo | 20 edges (`jag_edge_*`) + 17 nós de identidade + 75 nós JS-RG | cadeia de custódia completa da análise |

## 3. Interpretação

O alvo é um **visualizador/editor de radiografias panorâmicas** ("Panoramica AI")
com backend de sessão/admin e um endpoint de segmentação (`/segment/sam`).
**Não há indício de pipeline de treino, nem de um "OdontoCA" embarcado**: não
existem módulos de datasets, features, modelos ou autômatos celulares no DOM/JS.
Conclusão operacional: o objetivo de "treinar e prever cárie" **não se resolve
no site auditado**; ele pertence ao projeto OdontoCA em `odonto/`, tratado em
`SPEC-935-R898`.

## 4. Limitações

- Análise puramente estática do cliente; backend não foi exercido.
- `editor.js` truncado; achados podem ser parciais.
- Heurísticas de "electron-renderer" são inferidas, não confirmadas por empacotamento.
- Sem verificação de rede ativa; endpoints foram lidos do código, não chamados.
