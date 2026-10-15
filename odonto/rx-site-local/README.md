# Panoramica AI — cópia local funcional (backend simulado)

Cópia estática da página `rx.engenhariaorofacial.com.br` (auditoria REA, ver
`../REA_AUDIT_rx-site.md`) **mais um servidor local que substitui a API**.

## Por que isto existe

O front-end chama `fetch(...).then(r => r.json())`. Servido por um
`python3 -m http.server` comum, cada endpoint devolvia a página **404 em HTML** e o
console do navegador quebrava com:

```
Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

Evidência da falha original (artefato `.opencode/browser/evidence/6850e1d3…json`):
`Total messages: 9 (Errors: 9)` — `/health`, `/reviewer-ranking`,
`/reviewer-profiles`, `/administrator-statistics`, `/training-progress`,
`/admin/api/session`, `/og-image.png`, `/favicon.ico`, `/training-video.mp4`.

## Resultado (execução real no navegador)

Após `serve.py` (artefato `.opencode/browser/evidence/9de7aeed…json`):

```
Total messages: 1 (Errors: 1)
[ERROR] 404 @ /training-video.mp4
```

**9 → 1 erros.** O único restante é `training-video.mp4`, arquivo que não está
entre os arquivos capturados na auditoria; o próprio front tem fallback para
vídeo ausente. Navegação clicável verificada: clique em *Revisão* → `/review`
renderiza a página explicativa (artefato `ff27ac01…json`, `success: true`).

## Como rodar

```bash
cd odonto/rx-site-local
python3 serve.py --port 8791              # sem detecções (padrão honesto)
python3 serve.py --port 8791 --simulate 5 # caixas DEMO para exercitar a UI
```

Avisar: `http://127.0.0.1:8791/`

Testes (toda a pasta): `python3 -m pytest odonto/rx-site-local/tests/ -q` → **25 passed**
(10 do servidor MOCK + 15 da API real dos laboratórios). Ver também
`tests/test_r581_deploy_guards.py` (4 testes da guarda de smoke DOM).

## Laboratórios reais (SPEC-935-R900)

As rotas de laboratório **não** são explicativas: consomem endpoints `/api/*`
executados pelo `serve.py` sobre `backend/` e o pacote `odonto/local/odontoca`.

| Rota | Conteúdo | Endpoints usados |
|---|---|---|
| `/cadastro` | inventário de datasets, amostra real, treino em thread | `/api/datasets`, `/api/datasets/sample`, `/api/train`, `/api/train/status` |
| `/review` | simulador de autômato celular H→C + modelos reais | `/api/ca/demo`, `/api/ca/simulate`, `/api/models` |
| `/validacao` | gate de coorte travada, nível honesto, validação externa | `/api/validation` |
| `/docs` | catálogo dos endpoints (botão *testar*) | todos os acima |

Nível de alegação exibido em cada página (anti-overclaim):

- Autômato celular → `descritivo_nao_causal` (heurística declarada ou regra ajustada
  nas transições H→C reais do `Table_S1.xlsx`).
- Treino → `comparacao_empirica` (CV agrupada com OOF; **não** é desempenho clínico
  validado nem generalização externa).
- Validação externa → `bloqueado` (`../external_validation_protocol.md` exige
  coorte prospectiva com CEP/pré-registro).
- Gate de coorte fail-closed: `rows/events/children = 996/83/81` conferidos contra
  o SHA-256 do `../manuscript_assets/robust_audit/Table_S1.xlsx`
  (`b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa`).
- Nenhum número é inventado: as métricas vêm de `../local/outputs/*/report.json`.

Guarda de smoke: `write`/`edit` de `.html` rodam
`.opencode/hooks/js_smoke_dom.sh` (stub de DOM em Node) e bloqueiam a classe de
bug R580 (`querySelector('num')` sem ponto). O stub é ESM desde a correção
R900; o plugin `.opencode/plugins/deploy-guards.ts` valida agora o **conteúdo
prospectivo** (`write` novo deixou de ser negado com ENOENT) — efetivo após o
reinício do OpenCode.

## O que é simulado (anti-overclaim)

| Aspecto | Comportamento |
|---|---|
| Inferência de IA | **Não existe.** `X-*`-Counts refletem apenas o que o mock escreveu. |
| Detecções | **Zero por padrão.** `--simulate N` gera caixas rotuladas `DEMO-FDI`, com `mock: true` no JSON. |
| Marca d'água | Toda imagem enviada volta com selo `MOCK`. |
| Revisões / exportação | `POST /feedback` devolve `{revision:1}`; export é um ZIP de instrução, sem dados. |
| Usuário | Sessão `demo-local`, não autenticada de verdade. |

Este servidor **não substitui** o serviço hospedado nem valida qualquer resultado
clínico. `report.age_classification.label` é sempre `uncertain`.

## Contrato implementado

| Rota | Resposta |
|---|---|
| `GET /health` | `{status, mock, additional_model:{status:"ready"}}` |
| `GET /admin/api/session` | `{username, csrf, is_admin, mock}` |
| `GET /training-progress` | `{completed, target, remaining, percentage, mock}` |
| `GET /reviewer-ranking` | `{counts:[0×8], mock}` |
| `GET /reviewer-profiles` | `{profiles:[], mock}` |
| `GET /administrator-statistics` | `{adult:0, child:0, mock}` |
| `POST /predict/images?…` | **ZIP STORED** com `panoramica-anotada.png`, `panoramica-anatomia.png`, `panoramica-dentes.png`, `panoramica-impressao.json` + headers `X-Teeth-Count`, `X-Findings-Count`, `X-Additional-Status`, `X-Additional-Count`, `X-Anatomy-Count`, `X-Model-Scope` |
| `POST /segment/sam` | `{polygon_xy, bbox_xyxy, model:"mock"}` |
| `POST /feedback` | `{revision, reviewer, mock}` |
| `POST /admin/api/wishes`, `/admin/api/logout`, `*/edit-lock` | JSON de confirmação |
| `/review`, `/validacao`, `/cadastro`, `/docs` | **página de laboratório real** (SPEC-935-R900; consome `/api/*`) |
| `/desejos` | página explicativa (a rota original não foi capturada na auditoria) |
| `favicon.ico`, `og-image.png`, `colaboradores/*` | PNG 1×1 transparente |

Restrições do `readImageBundle` respeitadas: ZIP sem data descriptor
(`flags == 0`), `compression == 0`, e `panoramica-dentes.png` com exatamente
`layout.width × layout.height`.

## Limitações

- Rotas `/review`, `/validacao`, `/cadastro`, `/docs` não fazem parte da cópia
  capturada: foram escritas neste repositório (SPEC-935-R900) e consomem dados
  **locais reais**, não o serviço hospedado — não reproduzem o produto original.
- `/desejos` permanece página explicativa (`POST /desejos` não é exponível aqui).
- `/admin/api/images/*` responde `404 JSON` (revisão administrativa exige backend real).
- `training-video.mp4` continua 404 (arquivo não capturado).
- `editor.js` truncado na análise estática da REA; a edição no navegador não foi exercitada.

## Proveniência dos arquivos

| Arquivo | Origem |
|---|---|
| `index.html`, `editor.js`, `navigation.js`, `navigation.css` | cópia local de `rx.engenhariaorofacial.com.br` (auditoria REA, SPEC-935-R898) |
| `serve.py`, `tests/test_serve.py` | escrito neste repositório (SPEC-935-R899) |
| `backend/{paths,datasets,labs,jobs,ca_lab,api}.py`, `pages/{cadastro,review,validacao,docs}.html`, `tests/test_real_api.py` | escrito neste repositório (SPEC-935-R900) |
| `.opencode/hooks/smoke_dom_stub.js` (ESM) + `tests/test_r581_deploy_guards.py` | correção de guarda do ciclo R900 (CommonJS → ESM) |
| aviso `#mock-notice` | injetado pelo servidor no rodapé do HTML, com `pointer-events:none` para não interceptar cliques |
