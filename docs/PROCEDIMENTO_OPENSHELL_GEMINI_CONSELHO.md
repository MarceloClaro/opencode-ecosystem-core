# Procedimento de reprodução — conselho no sandbox OpenShell via executor Gemini

Este documento registra o procedimento completo e reproduzível para executar o
**conselho de 13 cientistas (R989)** DENTRO do sandbox **OpenShell**, usando o
executor **Gemini** (`gemini-client` + `GEMINI_API_KEY`) em vez do `agy` (que
exige OAuth de conta + keyring).

Data de referência: 2026-10-31. Ambiente: WSL2, glibc 2.43, sudo passwordless,
Podman 5.7.0 rootless, `dpkg`/`apt`. OpenShell 0.1.6.

---

## 1. Instalar o OpenShell (uma vez)

```bash
# 1a. Baixar e inspecionar o instalador oficial (Apache-2.0)
curl -fsSL https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh -o /tmp/install.sh
sh /tmp/install.sh          # instala openshell 0.1.6-1 (deb) e registra o gateway

# 1b. Ativar o socket da API do Podman (rootless) — o gateway precisa dele
systemctl --user enable --now podman.socket

# 1c. Fixar o compute driver (a detecção automática falha sem Docker)
mkdir -p ~/.config/systemd/user/openshell-gateway.service.d
cat > ~/.config/systemd/user/openshell-gateway.service.d/override.conf <<'EOF'
[Service]
Environment=OPENSHELL_COMPUTE_DRIVER=podman
Environment=OPENSHELL_TELEMETRY_ENABLED=false
EOF
systemctl --user daemon-reload && systemctl --user restart openshell-gateway

openshell --version   # 0.1.6
openshell status      # Connected (mTLS), endpoint https://127.0.0.1:17670
```

> **Telemetria**: o endpoint é `events.telemetry.data.nvidia.com/v1.1/events/json`
> (`OPENSHELL_TELEMETRY_ENDPOINT`) + OTLP (`OPENSHELL_OTLP_ENDPOINT`). O opt-out
> `OPENSHELL_TELEMETRY_ENABLED=false` desativa ambos. Captura de pacotes (R998)
> confirmou zero tráfego de telemetria e zero SYN de egress do sandbox.

## 2. Compilar o executor Gemini

```bash
cd integrations/gemini_client
cargo build --release
# binário: target/release/gemini-client (~5 MB, ligado a libc — presente no Ubuntu)
```

O cliente lê o prompt de `stdin`, chama
`generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}`
e imprime o texto. Usa skip-verify TLS (necessário: o proxy OpenShell faz MITM).

## 3. Criar o sandbox e carregar o executor + chave

```bash
openshell sandbox create --name council-sbx

# subir o binário e a chave (a chave fica em arquivo com permissão 600)
openshell sandbox upload council-sbx target/release/gemini-client /tmp/gemini-client
printf '%s' "$GEMINI_API_KEY" > /tmp/key.txt
openshell sandbox upload council-sbx /tmp/key.txt /tmp/gemini-key && rm /tmp/key.txt
printf 'gemini-3.5-flash' > /tmp/model.txt
openshell sandbox upload council-sbx /tmp/model.txt /tmp/gemini-model && rm /tmp/model.txt

openshell sandbox exec council-sbx -- sh -c \
  'chmod +x /tmp/gemini-client; chmod 600 /tmp/gemini-key; echo READY'
```

> **Gotcha 1 — integridade do binário**: o proxy registra o hash do executável na
> primeira conexão e nega se o arquivo mudar (`binary integrity violation`).
> Se trocar o binário, **recrie o sandbox** (delete + create).

## 4. Política de egress (mínima)

```bash
# protocolo rest: terminação TLS + inspeção HTTP; read-write permite POST
openshell policy update council-sbx \
  --add-endpoint "*.googleapis.com:443:read-write:rest:enforce" \
  --binary /tmp/gemini-client
```

> **Gotcha 2 — protocolo**: `rest` (HTTP) faz MITM TLS e o cliente precisa
> skip-verify. `tcp` (relay sem inspeção) deu `transparent_tcp_policy_denied`
> para o `generativelanguage.googleapis.com`. `full`/`rest` com `enforce` foi o
> que funcionou para este cliente HTTPS.

Teste de fumaça dentro do sandbox:

```bash
printf 'Responda somente: OK' | openshell sandbox exec council-sbx --timeout 60 -- \
  sh -c 'export GEMINI_API_KEY=$(cat /tmp/gemini-key); export GEMINI_MODEL=$(cat /tmp/gemini-model); /tmp/gemini-client'
# esperado: OK
```

## 5. Executar o conselho R989 dentro do sandbox

```python
import subprocess, json, time
from scientific_lab import council as C
from marceloclaro.orchestrator import MarceloClaroOrchestrator

class GeminiSandboxCoordinator:
    SBX = "council-sbx"
    def __init__(self, o): self.orchestrator = o
    def run(self, task, required_capabilities, **kw):
        aid = required_capabilities[0].replace("profile_", "").replace("_", "-")
        for _ in range(3):  # retry para 503/429 transitório
            r = subprocess.run(["openshell", "sandbox", "exec", self.SBX, "--timeout", "90", "--",
                "sh", "-c", "export GEMINI_API_KEY=$(cat /tmp/gemini-key); "
                            "export GEMINI_MODEL=$(cat /tmp/gemini-model); /tmp/gemini-client"],
                input=task, capture_output=True, text=True, timeout=120)
            out = r.stdout.strip()
            if r.returncode == 0 and out and not out.startswith(("GEMINI_ERROR", "CLI error", "Error:")):
                return {"status": "completed", "success": True, "agent_id": aid, "steps": 1,
                        "output": out, "attempts": [{"success": True, "output": out}],
                        "ecosystem": "gemini-in-sandbox"}
        return {"status": "failed", "success": False, "error": (r.stderr or r.stdout or "empty")[:200], "attempts": []}

primary = MarceloClaroOrchestrator(auto_load_agents=False)
coord = GeminiSandboxCoordinator(primary)
result = C.run_council(
    "Como caracterizar a adoção de IA em organizações, benefícios e riscos?",
    [{"id": "obs1", "text": "Estudo observacional com 120 organizações mediu a adoção de inteligência artificial entre 2020 e 2024. A automação de tarefas repetitivas cresceu 40 por cento. Sistemas de decisão assistida por IA foram adotados por 35 por cento. Riscos de viés não mitigado em 18 por cento dos sistemas auditados. Não houve ensaio randomizado nem grupo de controle.",
      "provenance": "fixture sintética"}],
    confirm=True, executor="antigravity", coordinator=coord, max_agents=13, timeout=560)
```

Cada cientista produz JSON `status/findings/evidence/limitations/feynman`;
`validate_report` confere citação literal contra a fonte e a completude Feynman.

## 6. Limpeza (obrigatória — credencial no sandbox)

```bash
openshell sandbox delete council-sbx
podman ps -a   # deve estar vazio
```

## Limites observados (honestos)

- **Quota Gemini**: a chave gratuita esgota (HTTP 429); os runs pararam em 7, 5
  e 3 cientistas conforme a cota drenou. Rotacione a chave para o run completo.
- **agy vs Gemini**: `agy` (OAuth/keyring) rodou 12/13 no host e 3/13 no sandbox
  (token expira). O Gemini (chave portátil) é a alternativa estável ao OAuth.
- **Skip-verify TLS** é válido apenas dentro do sandbox (MITM do proxy); fora,
  use TLS verificado.
- **Provider do OpenShell** não foi necessário: injeção manual da chave + egress
  `rest` resolveu o executor. Para produção, o provider injeta/renova credencial
  de forma governada.

## Evidência

Recibos em `docs/evidence/`: `R992_OPENSHELL_REAL.json` (instalação/isolamento),
`R994_COUNCIL_REAL.json` (conselho host 12/13), `R999_COUNCIL_IN_SANDBOX.json`
(agy no sandbox 3/13), `R1000_COUNCIL_13_IN_SANDBOX.json` (Gemini no sandbox),
`R996`/`R998` (capturas de pacotes). Ciclos R985–R1000 em `evolution/cycles.json`.
