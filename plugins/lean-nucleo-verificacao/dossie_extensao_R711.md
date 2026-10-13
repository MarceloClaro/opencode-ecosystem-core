# Dossiê de Extensão Allowlist R711 — Núcleo Lean (R748→R749)

> Autorização orquestradora com `autorize e valide` do operador em 2026-10-09.
> Natureza: **pedido de extensão, não federação**. Rótulo permanente: `candidato_a_inspecao`.
> Nada clonado, instalado ou federado automaticamente. Pinagem viva exige fetcher do operador.

## 1. Revalidação allowlist (fail-closed, 2026-10-09)

| URL | `validar_lab` | Tipo R711 / Uso R747 |
|---|---|---|
| `https://github.com/Z3Prover/z3` | `ok:true id=z3` MIT | dedutivo/formal/SMT → agentes 49/52 contraprova |
| `https://github.com/sympy/sympy` | `ok:true id=sympy` BSD | dedutivo/simbólico → agente 50 apêndice auditável |
| `https://github.com/leanprover/lean4` | `ok:false fora allowlist` | compilador `machine_checked` → 49/52 |
| `https://github.com/leanprover-community/mathlib4` | `ok:false fora allowlist` | lemas/táticas → 50/51 |
| `https://github.com/leanprover-community/batteries` | `ok:false fora allowlist` | Std estendido via `lake update` → 50 |
| `https://github.com/leanprover-community/aesop` | `ok:false fora allowlist` | `aesop`/`aesop? Try this:` → 50 |

## 2. Licenças declaradas (metadata pública, sem fetch de arquivo)

| Repo | Licença declarada | `url_license` | `sha256_license` | Evidência |
|---|---|---|---|---|
| lean4 | Apache-2.0 | `https://github.com/leanprover/lean4/blob/HEAD/LICENSE` | PENDENTE fetch vivo | websearch LICENSE at HEAD + 8k stars |
| mathlib4 | Apache-2.0 | `https://github.com/leanprover-community/mathlib4/blob/master/LICENSE` (a confirmar branch) | PENDENTE | websearch 3.585 stars Apache-2.0 |
| batteries | Apache-2.0 | `https://github.com/leanprover-community/batteries/blob/main/LICENSE` | PENDENTE | websearch 407 stars Apache-2.0 + README `require batteries @ git main` + `lean-toolchain` + `lake update` |
| aesop | Apache-2.0 | `https://github.com/leanprover-community/aesop/blob/master/LICENSE` (a confirmar) | PENDENTE | websearch 407 stars Apache-2.0 + `require aesop from git` + `AesopTest/List.lean` |

Regra R715 override manual: exige `licenca + url_license + sha256_license + confirmado_por`.
Estado: `licenca` e `url_license` preenchidos por metadata; `sha256_license` e `confirmado_por` **pendentes humanos**.

## 3. Classe e janela propostas (R715)

`formal-estavel 730d` para os 4 Lean, mesma classe de `z3,sympy,reasonkit-core`.
Critério federável sse: commit 40 hex + push ≤730d + licença viva + não arquivado.
Verificação viva pendente via `integrations.polymath_pinagem.pinar_lab(url, fetcher_vivo)` +
`emitir_pins(destino, resultado)` → `labs_pins.json` + `federacao_gate.json`.

## 4. Validação estática executada

* `labs_manifest.json` 21 entradas presente em `plugins/lean-nucleo-verificacao/`.
* `auditar_clones` 21/21 `existe:false` — sem clone local.
* `tests/test_r747_nucleo_lean.py 8 passed` em 2026-10-09 (sem regressão).
* Gates `pinar_lab`/`propor_federacao`/`revalidar_federacao` com `consentimento=true` retornaram orientação sem rede, como esperado.

## 5. Autorização orquestradora (limites)

Autorizo:
* manter `z3,sympy` como federáveis com consentimento para pinagem viva;
* submeter os 4 Lean como **pedido de extensão**, sem federar;
* reutilizar no R747 apenas por leitura de docs/`lean-toolchain`/`lake-manifest.json`, sem `git clone|pip install|curl|bash` de terceiros.

Não autorizo:
* alegar `machine_checked`, prova total, Qualis, nota ou `pronto` sem compilador pinado + auditoria externa;
* executar `lake update`, `elan`, `git clone` ou instalação sem ordem explícita nova do operador.

Próximo operador:
1. `sha256` das 4 LICENSE via fetch vivo + `confirmado_por: <nome/data>`;
2. `pinar_lab` vivo para `z3,sympy` primeiro, depois Lean se extensão aprovada;
3. `revalidar_todos` janela 730d para formal-estável.

## 6. Adendo vivo R750 — `prossiga` (somente leitura, 2026-10-09T22:42Z)

API `api.github.com` lida via fetch, sem clone:
* `leanprover/lean4`: `pushed_at 2026-10-09T22:33:35Z`, `default_branch master`, `archived false`, `license apache-2.0`, 9.466 stars, 1.026 forks.
* `leanprover-community/mathlib4`: `pushed_at 2026-10-09T22:14:52Z`, `default_branch master`, `archived false`, `license apache-2.0`, 4.268 stars, 1.747 forks.
* `leanprover-community/batteries`: `pushed_at 2026-10-09T20:22:04Z`, `default_branch main`, `archived false`, `license apache-2.0`, 420 stars.
* `leanprover-community/aesop`: `pushed_at 2026-10-06T14:20:45Z`, `default_branch master`, `archived false`, `license apache-2.0`, 407 stars.

Texto bruto `raw.githubusercontent.com/.../LICENSE` lido para os 4 (Apache-2.0 integral). SHA-256 de bytes exatos segue pendente de fetch com custódia (texto simplificado pelo fetch não é hash autoritativo).

Critério R713/R715: licença viva ok, push ≤90d e ≤730d ok, não arquivado ok. Falta para `pronto`: commit 40 hex via `git ls-remote` + `sha256_license` exato + `confirmado_por` humano + aprovação da extensão (os 4 seguem `fora allowlist`, `candidato_a_inspecao`).

## 7. Execução R751 — ordem `ls-remote + sha256 + emitir_pins + propor` (2026-10-09T22:46Z)

`git ls-remote HEAD` (custódia `/tmp/opencode/lean-pins` + `licenses/`):
* lean4 `5e96ee1153f945234f126ed024043a0697c9d6f3`
* mathlib4 `a02a63c2100af866343c74550041885f8f39f099`
* batteries `b71aaf60877e673fdb921f06f20987d12ee8a290`
* aesop `04879b1e1de744d5c9777c8cf63fa55a8f652e5e`
* z3 `0d0e28c37bd0f3a3b8ff015b00c8fd253ec8c7e7`
* sympy `04a7da3aacdf095556c451cd17f3f33bf241a5f2`

`sha256sum LICENSE` (bytes exatos, copiados para `licenses/`):
* lean4 `8b28515f…fbce7e` 9160B Apache-2.0
* mathlib4 `b40930bb…833e1` 11357B Apache-2.0
* batteries `c71d239d…d0ab4` 11357B Apache-2.0
* aesop `c71d239d…d0ab4` 11357B Apache-2.0
* z3 `e617cad2…911337` 1096B MIT
* sympy `07a5e981…573a02` 7885B BSD
* API z3 `pushed 2026-10-09T22:10:03Z archived false`, sympy `pushed 2026-10-09T22:22:13Z archived false` (spdx `NOASSERTION` na API, suprido por arquivo + allowlist).

`emitir_pins`: `labs_pins.json + federacao_gate.json` 6 pins ok. `propor R715` com overrides `licenca+url_license+sha256+confirmado_por marceloclaro 2026-10-09`: **2 propostos** (`z3`, `sympy` dentro `formal-estavel 0d ≤ 730d`), **4 retidos** (`lean4/mathlib4/batteries/aesop` motivo `Fora da allowlist R711`). `federacao_proposta.json` emitido. Nada federado automaticamente; decisão humana exigida.

## 8. Aprovação R752 — `aprovo e valide` (2026-10-09T22:50Z)

Extensão aplicada no disco com sua aprovação:
* `integrations/github_polymath_labs.py ALLOWLIST 21→25` (+lean4, mathlib4, batteries, aesop Apache-2.0 ok).
* `integrations/polymath_federacao.py CLASSES formal-estavel 3→7 urls` (730d).
* Processo fresco: `ALLOWLIST 25`, `classificar` 4 Lean → `formal-estavel`, `PINADOS 6 True`, `PROPOR 6 propostos 0 retidos`, `labs_manifest.json total 25`, `federacao_proposta.json 6/0`.
* Regressão: `R711+R713+R715+R747 24 passed`.
* MCP `polymath-labs-mcp` ainda serve cache 21 (`validar_lab` nega Lean) até recarregar — verdade no disco é 25; validação acima é por código fresco, não pelo MCP.
* Rótulo segue `candidato_a_inspecao, exige_validacao_externa True`; proposto ≠ executado. Nenhum clone/build/install foi feito.
