# SPEC-935-R882 — Empacotamento de deploy (container) da reprodução RX

Status: **implemented**
Trilha: RX (reprodução `outputs/core-r853-rx`)
Depende de: SPEC-935-R853 (reprodução), R874 (admin/persistência), R876 (composição
por capacidade), R878 (serve.py dual-stack)

## Problema

O operador quer publicar a reprodução "como site". O **GitHub Pages é estático**
(não executa Python), então a app completa (`/predict`, `/admin/api/*`,
`/segment/sam`, SQLite) não roda lá — o front sozinho daria "Failed to fetch".
É preciso um **host Python** (PaaS/container). Falta o pacote: imagem, deps
mínimas, bind compatível com provedor, healthcheck e passo a passo.

## Objetivo

Entregar um **pacote de deploy pronto e testado** para a app real, executável num
PaaS por Docker, sem pesos e sem dependências pesadas no caminho padrão.

## Requisitos (critérios de aceitação)

1. `serve.py` resolve o bind: local `("::", 8799)` (dual-stack R878) por padrão;
   em nuvem, `RX_HOST` define a interface e **`PORT` tem precedência sobre
   `RX_PORT`**.
2. `backend/requirements.txt` contém **apenas** runtime mínimo (`fastapi`,
   `uvicorn`, `pillow`, `python-multipart`) — **sem** torch/opencv/ultralytics/
   segment-anything.
3. `Dockerfile` (contexto `repro/`) instala os requisitos, copia
   `serve.py`/`backend/`/`frontend/`, expõe `8799`, tem `HEALTHCHECK` em
   `/health` e `CMD ["python","serve.py"]`.
4. `.dockerignore` exclui `__pycache__`, pesos (`*.pth/*.pt`), bancos locais e
   `training/`.
5. Blueprint `render.yaml` com runtime docker e healthcheck `/health`.
6. **Prova de container mínimo**: a app serve `/health`, `/`, `/opcoes.json`,
   login admin e `/predict` **com torch/cv2/numpy/segment_anything bloqueados**.
7. Sem regressão: R878 (dual-stack) e demais testes RX verdes; `doctor` 22/22.
8. **Rastreabilidade p/ deploy from GitHub** (correção R883): o `.gitignore`
   precisa re-incluir TODO o runtime da reprodução (`serve.py`, `Dockerfile`,
   `.dockerignore`, `render.yaml`, `DEPLOY.md`, `engines.py`, `store.py`,
   `requirements.txt`) — antes, `engines.py`/`store.py` e os artefatos de deploy
   estavam ignorados e o clone do GitHub ficaria **incompleto** (`app.py` falha
   ao importar `engines`/`store`). Coberto por teste de contrato (`git check-ignore`).

## Não-objetivos / limites

- **Não** executa o deploy (o agente não tem a conta do provedor). Entrega
  pacote + instruções; a publicação é ato do operador, verificada por HTTP.
- **Não** empacota os motores reais (`weights`/`open_base`): exigem torch +
  checkpoints (build separado, disco, custo).
- Sem disco persistente, o SQLite é efêmero (dados de demonstração).

## Implementação

- `repro/serve.py`: `_resolve_bind(env)` + ramo de nuvem (`uvicorn.run` em
  `RX_HOST:PORT`); default dual-stack preservado.
- `repro/backend/requirements.txt`, `repro/Dockerfile`, `repro/.dockerignore`,
  `repro/render.yaml`.
- `outputs/core-r853-rx/DEPLOY.md`: Render (principal) + Railway/Fly/Cloud Run/
  Hugging Face Spaces, env vars, persistência, verificação anti-overclaim.

## Evidência

- `tests/test_r882_rx_deploy.py` (8 testes) — bind (3), artefatos (4), prova de
  container mínimo (1, subprocesso com import bloqueado) → **verde**.
- `tests/test_r878_rx_dualstack.py` continua verde (sem regressão).
- Suíte RX completa verde; `doctor` 22/22.

## Lições

- Deps pesadas já são lazy em `app.py`/`engines.py`/`store.py` → o engine `stub`
  cabe em imagem `python:3.12-slim` com 4 pacotes.
- Provedores exigem bind em `0.0.0.0` e injetam `PORT`; `RX_HOST`/`PORT` cobrem
  isso sem quebrar o dual-stack local.
- Teste de contrato de `requirements.txt` deve ignorar comentários (evita falso
  negativo por menção textual a "torch").
