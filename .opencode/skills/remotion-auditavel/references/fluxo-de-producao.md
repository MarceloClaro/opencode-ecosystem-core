# Fluxo de produção auditável

## 1. Licença

```bash
python3 - <<'PY'
from integrations.remotion_guard import license_scope
print(license_scope("for_profit", employees=3))
PY
```

Substitua `entity_type` e `employees` pelos dados reais. `company_license_required`
significa que a licença comercial deve ser resolvida antes do uso.

## 2. Inspeção

```bash
python3 - <<'PY'
from integrations.remotion_guard import scan_project
print(scan_project("caminho/do/projeto"))
PY
```

Confira `remotion_dependencies`, `pinned`, `license.remotion_license_detected`,
`config_files`, `compositions` e `warnings`. O scanner não compila o projeto.

## 3. Prévia

```bash
npx remotion studio --no-open
```

Abra a URL local e confira a composição. O plugin permite esse comando.

## 4. Plano e pré-render

```bash
python3 -m integrations.video_edit_plan validate plano.json
python3 -m integrations.video_edit_plan compile plano.json
```

`render_preflight` combina o plano R1024 com a composição e o caminho de saída:

```bash
python3 - <<'PY'
import json
from integrations.remotion_guard import render_preflight
plan = json.load(open("plano.json"))
print(render_preflight(plan, composition_id="Intro", project_path="."))
PY
```

## 5. Render explícito

```bash
REMOTION_RENDER_APPROVED=1 npx remotion render Intro out/video.mp4
```

Sem a variável, o plugin bloqueia. A aprovação não valida licença nem direitos.

## 6. QC

```bash
python3 -m integrations.video_edit_plan verify plano.json relatorio.json
```

O resultado confirma metadados; assista à prévia e confira o trecho crítico.
Qualidade visual e sincronização continuam não verificadas pelo validador.
