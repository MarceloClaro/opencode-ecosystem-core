# SPEC-935-R484 — Integração do ReverseScanner ao CLI do orquestrador

Status: **implementado** (R484)
Data: 2026-09-13
Requer: R483 (ReverseScanner), R015 (NoologicalScanner), CLI existente

## 1. Contexto

O R483 criou `scanners/reverse_scanner.py` com pipeline completo (grafo → R(F) → Δ → p(g)),
mas expôs apenas API Python. O usuário precisa da capacidade via terminal, no mesmo
padrão de `doctor`, `core-check` e `apm` do `marceloclaro.cli`.

## 2. Objetivos

- **OF1** — Novo comando direto `python3 -m marceloclaro.cli reverse-scan` com
  `--target` (obrigatório), `--file` (lista de artefatos locais), `--domain`
  (default `ecosystem`), `--json` (saída estruturada).
- **OF2** — Sem `--file`, escaneia o diretório `specs/` do próprio Core como corpus
  (hermético, local, sem rede).
- **OF3** — Saída humana em PT-BR formal com `R(F)`, `Δ` e oportunidades priorizadas;
  saída JSON com os campos do `ReverseScanReport`.
- **OF4** — Exit code: 0 sucesso; 1 erro de uso ou falha interna.

## 3. Não-objetivos

- Não altera o menu interativo (opções 1–10) — apenas adiciona comando direto.
- Não altera `ReverseScanner`, `CrossValidationEngine` nem `NoologicalScanner`.
- Não adiciona orquestração multi-alvo remota (futuro).

## 4. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | Sem `--target` → exit 1 + mensagem de uso |
| CA2 | Com `--file` → JSON parseável contendo `target_state`, `reverse_closure`, `evolution_gap`, `opportunities`, `params` |
| CA3 | Com `--json` ausente → saída humana contendo rótulos `R(F)`, `Gap evolutivo` e linhas `tier=` |
| CA4 | Sem `--file` → usa `specs/` e executa com exit 0 |
| CA5 | Saída JSON sem palavras anti-overclaim (`superhuman`, `verificado(s)`, `qualis a1`, `superação`) |
| CA6 | Ajuda (`ajuda`/`--help`) documenta o comando |
| CA7 | `--domain` e `--file` combinados funcionam (ex.: domínio academic) |

## 5. Entregáveis

- `marceloclaro/cli.py`: `_cmd_reverse_scan(args)` + rota no modo comando direto + AJUDA_TEXT
- `tests/test_r484_cli_reverse_scan.py`
- ciclo R484 + reflexão + commit

## 6. Prontidão

- `python3 -m pytest tests/test_r484_cli_reverse_scan.py` verde
- `python3 -m marceloclaro.cli doctor` inalterado; suíte completa sem novas falhas