# SPEC-935-R488 — Audit Chain entre Ciclos (lição Bernstein)

Status: **implementado** (R488)
Data: 2026-09-13
Requer: R462 (âncoras por ciclo), ciclo R487 (análise Bernstein)

## 1. Contexto — Síntese Bernstein

O [bernstein](https://github.com/sipyourdrink-ltd/bernstein) (Apache-2.0, auditado
na R483 e na R487) orquestra 44 agentes CLI com **zero LLM na coordenação** e
protege a execução com:

- **audit chain HMAC-SHA256 (RFC 2104)** — um registro por decisão, tamper-evident;
- **per-artefact lineage** — spine Merkle-chained com identidade de run;
- **always-on replay journal** — não-determinismo vira hash mismatch;

O Core já herda as âncoras **por ciclo** (R462: `merkle_root`, `origin_commit`,
`state_merkle_root`). A liência que este R488 materializa: encadear os ciclos
**entre si** — cada ciclo registra o hash criptográfico do estado do registro
(pós-ciclo anterior), formando uma cadeia contínua. Rearranjar/remover/injetar
ciclos quebra a cadeia.

## 2. Objetivos

- **OF1** — Encadeamento HMAC-SHA256 entre ciclos (RFC 2104) via
  `prev_state_merkle_root` (campo aditivo, retrocompatível).
- **OF2** — `EvolutionRegistry.verify_state_chain()` verifica a cadeia contínua;
  ciclos sem âncora são "nós cegos" tolerados, mas a cadeia inicia a partir do
  primeiro nó âncora e quebras (nó com prev que não bate com o hash do nó
  anterior) são reportadas.
- **OF3** — O ciclo R488 nasce âncora (`state_merkle_root` preenchido, `prev=""`);
  futuros ciclos encadeiam nele.
- **OF4** — 100% stdlib (`hmac`, `hashlib`), sem alterar o comportamento de ciclos
  existentes (imutabilidade).

## 3. Não-objetivos

- Não reescreve o histórico (ciclos passados permanecem sem `prev`).
- Não introduz journal de execução por run (replay journal corporativo — roadmap).
- Não acopla o Core ao Bernstein (referência de padrão, Apache-2.0 respektado).

## 4. Modelo formal

```
chain(prev, state_bytes) = HMAC-SHA256(key=prev, msg=state_bytes)   # RFC 2104
state_merkle_root(n)     = sha256(bytes do cycles.json APÓS inserir o ciclo n)
prev_state_merkle_root(n)= state_merkle_root(n-1)  (se o n-1 estiver ancorado)

verify_state_chain():
    para cada ciclo n EM ORDEM com prev_state_merkle_root preenchido:
        se n == primeiro nó: ok se prev == "" ou prev == state_merkle_root(âncora anterior)
        senão: exige prev == state_merkle_root do último ciclo ancorado
    retorna {ok, size, anchored, broken}
```

## 5. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | `chain_state_merkle(prev, bytes)` produz HMAC-SHA256 determinístico (RFC 2104) |
| CA2 | Campo `prev_state_merkle_root` carregado de ciclos existentes (sem quebrar o filtro allowed) |
| CA3 | `verify_state_chain()` em registro sem âncoras → ok=True, anchored=0 |
| CA4 | Cadeia de 2+ nós âncora contínua → ok=True, size=N |
| CA5 | Alterar estado entre nós (simulado) → ok=False com nó quebrado identificado |
| CA6 | Nó cego no meio (sem prev/state) não quebra a cadeia dos nós ancorados seguintes |
| CA7 | Retrocompatível: `EvolutionRegistry()` carrega cycles.json real sem erro |
| CA8 | Doctor/Core-check passam; suíte existente sem novas falhas |
| CA9 | Documentação do algoritmo no módulo |

## 6. Entregáveis

- `evolution/cycles.py` — campo `prev_state_merkle_root`, `chain_state_merkle()`,
  `verify_state_chain()`
- `tests/test_r488_audit_chain.py`
- Ciclo R488 âncora + lições Bernstein em `evolution/cycles.json`
- spec (este arquivo)

## 7. Prontidão

- `pytest tests/test_r488_audit_chain.py` verde; regressões ciclos/testes anteriores
- `doctor` sem novas falhas