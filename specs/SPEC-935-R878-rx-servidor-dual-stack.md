# SPEC-935-R878 — Servidor dual-stack (IPv4 + IPv6) da reprodução RX

Status: **implemented**
Trilha: RX (reprodução `outputs/core-r853-rx`)
Depende de: SPEC-935-R876 (composição por capacidade), R877 (rebrand)

## Problema

O relatório do operador foi `Failed to fetch` no navegador. Diagnóstico local:
o serviço respondia 200 em todos os endpoints, o JS era válido e o front usa
apenas caminhos relativos — logo, o erro é de camada de rede do cliente.
O host resolve `localhost` para `::1` (IPv6), mas o uvicorn liga **apenas uma
família por processo**:

- `--host 127.0.0.1` → só IPv4 (IPv6 `::1` recusado);
- `--host ::` → **só IPv6** (o uvicorn ≥0.30 força `IPV6_V6ONLY=1`);
- não há bind único do uvicorn que cubra IPv4 **e** IPv6 simultaneamente.

Além disso o operador pediu acesso a partir de **outro dispositivo** (LAN).

## Objetivo

Servir a reprodução, com **uma única instância**, em IPv4 (loopback + LAN) e
IPv6 (loopback), sem duplicar processo nem banco, e sem depender de fallback
happy-eyeballs do navegador.

## Requisitos (critérios de aceitação)

1. Um único processo atende `http://127.0.0.1:8799/`, `http://localhost:8799/`,
   `http://[::1]:8799/` e `http://<IP-LAN>:8799/` → HTTP 200 em `/`.
2. O socket é AF_INET6 em `[::]` com `IPV6_V6ONLY=0` (aceita IPv4 mapeado).
3. O app é carregado de `repro/backend` sem `app_dir` (removido no
   uvicorn ≥0.30/0.51) — via inserção em `sys.path`.
4. Entradas por env: `RX_PORT` (default 8799), `RX_LOGLEVEL` (default warning),
   além de `RX_ENGINE`/`RX_MEDSAM_CKPT` herdadas do backend.
5. Não altera o contrato HTTP nem as evidências congeladas (R853/R876/R877).
6. Sem regressão: a suíte RX permanece verde; `doctor` 22/22.

## Não-objetivos / limites

- **Exposição na LAN é explícita e aceita pelo operador**: as rotas admin da
  reprodução usam credenciais de **demonstração**; não há autenticação forte.
  Não usar com dados reais.
- Não muda bind de produção, TLS, nem adiciona proxy reverso.
- O launcher é um utilitário de execução local; não substitui uvicorn em deploy.

## Implementação

`outputs/core-r853-rx/repro/serve.py`:
- `_dualstack_socket(port)` — cria AF_INET6, `SO_REUSEADDR`, `IPV6_V6ONLY=0`,
  `bind(("::", port))`, `listen(2048)`;
- `main()` — insere `repro/backend` em `sys.path`, monta `uvicorn.Config("app:app", ...)`
  e entrega o socket pronto via `Server.run(sockets=[sock])`.

## Evidência

- `ss -ltn` mostra `*:8799` (dual-stack), não `127.0.0.1:8799`.
- Curl 200 nos quatro endereços (loopback v4/v6, `localhost`, LAN).
- `tests/test_r878_rx_dualstack.py` valida `IPV6_V6ONLY==0` e a aceitação de
  conexões IPv4 **e** IPv6 no mesmo socket.

## Lições

- `uvicorn --host ::` **não** é dual-stack neste uvicorn; exige socket pré-ligado.
- `uvicorn.Config` ≥0.30 não aceita mais `app_dir`.
